"""
GPM CFTV Studio - Testador de Conexão RTSP com Auto-Detecção
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import socket
import subprocess
import platform
from typing import Tuple, Optional
from studio.models.camera import Camera, RTSP_PROFILES


class RTSPTester:
    """
    Testa conectividade com câmeras IP via RTSP.
    Detecta automaticamente porta e caminho RTSP.
    """
    
    # Portas comuns para testar
    COMMON_PORTS = [554, 80, 8554, 10554]
    
    @staticmethod
    def auto_detect(ip: str, username: str, password: str, timeout: int = 3) -> Optional[dict]:
        """
        Detecta automaticamente as configurações da câmera.
        Testa várias combinações de porta + caminho RTSP.
        
        Args:
            ip: Endereço IP
            username: Usuário
            password: Senha
            timeout: Timeout por teste
            
        Returns:
            Dicionário com configurações encontradas ou None.
            Ex: {"port": 554, "rtsp_path": "/Streaming/Channels/101", "manufacturer": "Hikvision"}
        """
        print(f"\n🔍 Auto-detectando câmera em {ip}...")
        print("-" * 50)
        
        # 1. Testar ping primeiro
        if not RTSPTester._ping(ip, timeout):
            print(f"❌ IP {ip} não responde a ping")
            return None
        
        print(f"✅ IP {ip} responde a ping")
        
        # 2. Descobrir porta aberta
        port = RTSPTester._find_open_port(ip, timeout)
        if not port:
            print(f"❌ Nenhuma porta RTSP encontrada em {ip}")
            return None
        
        print(f"✅ Porta {port} aberta")
        
        # 3. Testar caminhos RTSP
        result = RTSPTester._find_rtsp_path(ip, port, username, password, timeout)
        if result:
            print(f"✅ Câmera detectada: {result['manufacturer']} - {result['profile']}")
            return {
                "port": port,
                "rtsp_path": result["path"],
                "manufacturer": result["manufacturer"],
                "profile": result["profile"]
            }
        
        print(f"⚠️ Porta aberta mas não foi possível detectar o caminho RTSP")
        return None
    
    @staticmethod
    def _find_open_port(ip: str, timeout: int = 2) -> Optional[int]:
        """
        Encontra a primeira porta RTSP aberta.
        Testa as portas mais comuns.
        """
        for port in RTSPTester.COMMON_PORTS:
            if RTSPTester._check_port(ip, port, timeout):
                return port
        
        # Se nenhuma porta comum, testar range 554-558
        for port in range(554, 559):
            if RTSPTester._check_port(ip, port, timeout):
                return port
        
        return None
    
    @staticmethod
    def _find_rtsp_path(ip: str, port: int, username: str, password: str, timeout: int = 3) -> Optional[dict]:
        """
        Testa vários caminhos RTSP para encontrar o correto.
        """
        # Lista de caminhos para testar (ordenados por popularidade)
        paths_to_test = []
        
        # Hikvision (mais comum)
        paths_to_test.append({"path": "/Streaming/Channels/101", "manufacturer": "Hikvision", "profile": "main"})
        paths_to_test.append({"path": "/Streaming/Channels/102", "manufacturer": "Hikvision", "profile": "sub"})
        
        # Dahua / Intelbras
        paths_to_test.append({"path": "/cam/realmonitor?channel=1&subtype=0", "manufacturer": "Dahua/Intelbras", "profile": "main"})
        paths_to_test.append({"path": "/cam/realmonitor?channel=1&subtype=1", "manufacturer": "Dahua/Intelbras", "profile": "sub"})
        
        # ONVIF
        paths_to_test.append({"path": "/onvif1", "manufacturer": "ONVIF", "profile": "main"})
        
        # Giga / Genérico
        paths_to_test.append({"path": "/profile1", "manufacturer": "Generico", "profile": "main"})
        paths_to_test.append({"path": "/profile2", "manufacturer": "Generico", "profile": "sub"})
        
        # Outros caminhos comuns
        paths_to_test.append({"path": "/live/main", "manufacturer": "Generico", "profile": "main"})
        paths_to_test.append({"path": "/live/sub", "manufacturer": "Generico", "profile": "sub"})
        paths_to_test.append({"path": "/h264", "manufacturer": "Generico", "profile": "main"})
        paths_to_test.append({"path": "/video1", "manufacturer": "Generico", "profile": "main"})
        paths_to_test.append({"path": "/media/video1", "manufacturer": "Generico", "profile": "main"})
        
        # Adicionar caminhos dos perfis
        for manufacturer, profiles in RTSP_PROFILES.items():
            for profile, path in profiles.items():
                paths_to_test.append({
                    "path": path,
                    "manufacturer": manufacturer,
                    "profile": profile
                })
        
        # Remover duplicados
        seen = set()
        unique_paths = []
        for p in paths_to_test:
            if p["path"] not in seen:
                seen.add(p["path"])
                unique_paths.append(p)
        
        print(f"  Testando {len(unique_paths)} caminhos RTSP...")
        
        # Testar cada caminho
        for i, test in enumerate(unique_paths):
            path = test["path"]
            rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}{path}"
            
            # Mostrar progresso
            manufacturer = test["manufacturer"]
            print(f"  [{i+1}/{len(unique_paths)}] {manufacturer}: {path}...", end=" ")
            
            if RTSPTester._test_rtsp_stream(rtsp_url, timeout):
                print("✅ OK")
                return test
            else:
                print("❌")
        
        return None
    
    @staticmethod
    def quick_test(ip: str, port: int = 554, timeout: int = 2) -> Tuple[bool, str]:
        """
        Teste rápido: apenas ping + porta.
        
        Args:
            ip: Endereço IP
            port: Porta RTSP
            timeout: Timeout em segundos
            
        Returns:
            Tupla (status, mensagem)
        """
        if not RTSPTester._ping(ip, timeout):
            return False, "Offline"
        
        if not RTSPTester._check_port(ip, port, timeout):
            return False, "Porta fechada"
        
        return True, "Online"
    
    @staticmethod
    def test_camera(camera: Camera, timeout: int = 3) -> Tuple[bool, str]:
        """
        Testa conexão com uma câmera já configurada.
        """
        if not RTSPTester._ping(camera.ip, timeout):
            return False, f"IP {camera.ip} não responde"
        
        if not RTSPTester._check_port(camera.ip, camera.port, timeout):
            return False, f"Porta {camera.port} fechada"
        
        rtsp_url = camera.get_rtsp_url()
        if rtsp_url:
            if RTSPTester._test_rtsp_stream(rtsp_url, timeout):
                return True, "Online - Stream OK"
            else:
                return False, "Stream RTSP não disponível"
        
        return True, "Online - IP e porta OK"
    
    @staticmethod
    def _ping(ip: str, timeout: int = 2) -> bool:
        """Testa se IP responde a ping."""
        try:
            if platform.system() == "Windows":
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip]
            else:
                cmd = ["ping", "-c", "1", "-W", str(timeout), ip]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout + 1
            )
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def _check_port(ip: str, port: int, timeout: int = 3) -> bool:
        """Testa se porta TCP está aberta."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    @staticmethod
    def _test_rtsp_stream(rtsp_url: str, timeout: int = 3) -> bool:
        """Testa se stream RTSP está acessível via ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-rtsp_transport", "tcp",
                "-timeout", str(timeout * 1000000),
                rtsp_url
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=timeout + 2
            )
            return result.returncode == 0
        except:
            return False