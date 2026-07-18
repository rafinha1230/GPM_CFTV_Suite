"""
GPM CFTV Viewer - Modelo de Configuração
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class CameraConfig:
    """
    Configuração de uma câmera carregada pelo Viewer.
    Dados vêm do JSON gerado pelo Studio.
    """
    id: str = ""
    ip: str = ""
    port: int = 554
    username: str = "admin"
    password: str = ""
    rtsp_path: str = ""
    rtsp_url: str = ""
    enabled: bool = True
    
    def get_rtsp_url(self) -> str:
        """Retorna a URL RTSP completa."""
        if self.rtsp_url:
            return self.rtsp_url
        
        if all([self.ip, self.username, self.password, self.rtsp_path]):
            return (
                f"rtsp://{self.username}:{self.password}"
                f"@{self.ip}:{self.port}"
                f"{self.rtsp_path}"
            )
        return ""


@dataclass
class ViewerConfig:
    """
    Configuração completa do Viewer.
    """
    version: str = "1.0.0"
    window_title: str = "GPM CFTV Viewer"
    fullscreen_on_start: bool = False
    keep_aspect_ratio: bool = True
    cameras: List[CameraConfig] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ViewerConfig':
        """Carrega configuração de um dicionário."""
        config = cls()
        config.version = data.get("version", "1.0.0")
        
        viewer_settings = data.get("viewer_settings", {})
        config.window_title = viewer_settings.get("window_title", "GPM CFTV Viewer")
        config.fullscreen_on_start = viewer_settings.get("fullscreen_on_start", False)
        config.keep_aspect_ratio = viewer_settings.get("keep_aspect_ratio", True)
        
        cameras_data = data.get("cameras", [])
        for cam_data in cameras_data:
            if cam_data.get("enabled", True):
                camera = CameraConfig(
                    id=cam_data.get("id", ""),
                    ip=cam_data.get("ip", ""),
                    port=cam_data.get("port", 554),
                    username=cam_data.get("username", "admin"),
                    password=cam_data.get("password", ""),
                    rtsp_path=cam_data.get("rtsp_path", ""),
                    rtsp_url=cam_data.get("rtsp_url", ""),
                )
                config.cameras.append(camera)
        
        return config