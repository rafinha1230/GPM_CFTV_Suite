"""
GPM CFTV Studio - Testador de Conexão RTSP
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import socket
import subprocess
import platform
from typing import Tuple
from studio.models.camera import Camera


class RTSPTester:
    """
    Testa conectividade com câmeras IP via RTSP.
    """
    
    @staticmethod
    def test_camera(camera: Camera, timeout: int = 3) -> Tuple[bool, str]:
        """
        Testa conexão com uma câmera.
        
        Args:
            camera: Instância da câmera a testar
            timeout: Tempo máximo de espera em segundos
            
        Returns:
            Tupla (status, mensagem)
        """
        # 1. Testar se IP responde (ping)
        if not RTSPTester._ping(camera.ip, timeout):
            return False, f"IP {camera.ip} não responde"
        
        # 2. Testar se porta está aberta
        if not RTSPTester._check_port(camera.ip, camera.port, timeout):
            return False, f"Porta {camera.port} fechada"
        
        # 3. Testar stream RTSP com ffprobe (se disponível)
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
            # Windows: ping -n 1 -w 2000
            # Linux: ping -c 1 -W 2
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
            # Tenta usar ffprobe (parte do FFmpeg)
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-rtsp_transport", "tcp",
                "-timeout", str(timeout * 1000000),  # microssegundos
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