"""
GPM CFTV Studio - Modelo de Dados da Câmera
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class Camera:
    """
    Representa uma câmera IP no sistema.
    
    Atributos:
        id: Identificador único da câmera
        ip: Endereço IP da câmera
        port: Porta RTSP (padrão: 554)
        username: Nome de usuário para autenticação
        password: Senha para autenticação
        rtsp_profile: Perfil RTSP (main, sub, etc.)
        rtsp_path: Caminho do stream RTSP
        enabled: Se a câmera está ativa
        created_at: Data de criação do registro
        updated_at: Data da última modificação
    """
    
    # Identificação
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # Configurações de rede
    ip: str = ""
    port: int = 554
    
    # Autenticação
    username: str = "admin"
    password: str = ""
    
    # Configurações RTSP
    rtsp_profile: str = "main"
    rtsp_path: str = ""
    
    # Status
    enabled: bool = True
    
    # Metadados
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def get_rtsp_url(self) -> str:
        """
        Gera a URL RTSP completa da câmera.
        
        Returns:
            String com a URL RTSP formatada.
            
        Exemplo:
            rtsp://admin:12345@192.168.1.100:554/Streaming/Channels/101
        """
        if not all([self.ip, self.username, self.password, self.rtsp_path]):
            return ""
        
        return (
            f"rtsp://{self.username}:{self.password}"
            f"@{self.ip}:{self.port}"
            f"{self.rtsp_path}"
        )
    
    def validate(self) -> tuple[bool, str]:
        """
        Valida se os campos obrigatórios estão preenchidos.
        
        Returns:
            Tupla (válido, mensagem_de_erro).
        """
        if not self.ip:
            return False, "❌ Endereço IP é obrigatório"
        
        if not self.username:
            return False, "❌ Nome de usuário é obrigatório"
        
        if not self.password:
            return False, "❌ Senha é obrigatória"
        
        if not self.rtsp_path:
            return False, "❌ Caminho RTSP é obrigatório"
        
        # Validar formato do IP (básico)
        parts = self.ip.split(".")
        if len(parts) != 4:
            return False, "❌ Formato de IP inválido"
        
        try:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False, "❌ IP fora do intervalo válido (0-255)"
        except ValueError:
            return False, "❌ IP contém caracteres inválidos"
        
        # Validar porta
        if self.port < 1 or self.port > 65535:
            return False, "❌ Porta fora do intervalo válido (1-65535)"
        
        return True, "✅ Câmera válida"
    
    def to_dict(self) -> dict:
        """
        Converte a câmera para dicionário (para serialização JSON).
        
        Returns:
            Dicionário com os dados da câmera.
        """
        data = asdict(self)
        # Adiciona a URL completa
        data['rtsp_url'] = self.get_rtsp_url()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Camera':
        """
        Cria uma câmera a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados da câmera.
            
        Returns:
            Instância de Camera.
        """
        # Remove campos que não são do modelo
        valid_fields = {
            'id', 'ip', 'port', 'username', 'password',
            'rtsp_profile', 'rtsp_path', 'enabled',
            'created_at', 'updated_at'
        }
        
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def __str__(self) -> str:
        """Representação amigável da câmera."""
        return (
            f"📷 Câmera {self.id}\n"
            f"   IP: {self.ip}:{self.port}\n"
            f"   Perfil: {self.rtsp_profile}\n"
            f"   Status: {'✅ Ativa' if self.enabled else '❌ Inativa'}"
        )


# Lista de caminhos RTSP comuns para auto-detecção
RTSP_PROFILES = {
    "Hikvision": {
        "main": "/Streaming/Channels/101",
        "sub": "/Streaming/Channels/102",
        "third": "/Streaming/Channels/103",
    },
    "Dahua": {
        "main": "/cam/realmonitor?channel=1&subtype=0",
        "sub": "/cam/realmonitor?channel=1&subtype=1",
    },
    "Intelbras": {
        "main": "/cam/realmonitor?channel=1&subtype=0",
        "sub": "/cam/realmonitor?channel=1&subtype=1",
    },
    "Giga": {
        "main": "/profile1",
        "sub": "/profile2",
    },
    "Genérico": {
        "main": "/live/main",
        "sub": "/live/sub",
    },
    "ONVIF": {
        "main": "/onvif1",
        "sub": "/onvif2",
    },
}


def get_all_rtsp_paths() -> list[dict]:
    """
    Retorna todos os caminhos RTSP para teste automático.
    
    Returns:
        Lista de dicionários com fabricante, perfil e caminho.
    """
    paths = []
    for manufacturer, profiles in RTSP_PROFILES.items():
        for profile, path in profiles.items():
            paths.append({
                "manufacturer": manufacturer,
                "profile": profile,
                "path": path,
            })
    return paths