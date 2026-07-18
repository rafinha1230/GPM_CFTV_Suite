"""
GPM CFTV Viewer - Motor de Streaming
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba

Nota: Esta é uma versão simulada para desenvolvimento.
A versão final usará GStreamer para streaming real.
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from viewer.models.camera_config import CameraConfig


class StreamWidget(QWidget):
    """
    Widget que exibe o stream de uma câmera.
    Versão simulada - será substituída por GStreamer.
    """
    
    def __init__(self, camera: CameraConfig, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.is_connected = False
        self.reconnect_attempts = 0
        self.setup_ui()
        self.start_stream()
    
    def setup_ui(self):
        """Configura a interface do widget."""
        self.setStyleSheet("""
            QWidget {
                background-color: #11111b;
                border: 2px solid #45475a;
                border-radius: 5px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label central com informações
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Segoe UI", 11))
        self.info_label.setStyleSheet("""
            QLabel {
                color: #a6adc8;
                background: transparent;
                border: none;
                padding: 10px;
            }
        """)
        layout.addWidget(self.info_label)
        
        self.update_info()
    
    def update_info(self):
        """Atualiza informações exibidas."""
        status_color = "#a6e3a1" if self.is_connected else "#f38ba8"
        
        self.info_label.setText(
            f"📷 Câmera {self.camera.id}\n\n"
            f"IP: {self.camera.ip}:{self.camera.port}\n"
            f"Perfil: {self.camera.rtsp_path}\n\n"
            f"<span style='color:{status_color};'>"
            f"{'🟢 Conectado' if self.is_connected else '🔴 Desconectado'}"
            f"</span>"
        )
    
    def start_stream(self):
        """
        Inicia o stream da câmera.
        Versão simulada - será substituída por GStreamer.
        """
        self.is_connected = True
        self.update_info()
        print(f"✅ Stream iniciado: {self.camera.ip}")
    
    def stop_stream(self):
        """Para o stream da câmera."""
        self.is_connected = False
        self.update_info()
        print(f"⏹️ Stream parado: {self.camera.ip}")
    
    def reconnect(self):
        """Tenta reconectar ao stream."""
        self.reconnect_attempts += 1
        print(f"🔄 Tentativa {self.reconnect_attempts}: {self.camera.ip}")
        self.start_stream()