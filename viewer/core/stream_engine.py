"""
GPM CFTV Viewer - Motor de Streaming com Reconexão Automática
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from viewer.models.camera_config import CameraConfig


class StreamWidget(QWidget):
    """
    Widget que exibe o stream de uma câmera.
    Com sistema de reconexão automática.
    """
    
    # Estados da câmera
    STATE_DISCONNECTED = "disconnected"
    STATE_CONNECTING = "connecting"
    STATE_CONNECTED = "connected"
    STATE_ERROR = "error"
    
    # Configuração de reconexão (exponential backoff)
    RECONNECT_DELAYS = [1, 2, 4, 8, 16, 30]  # segundos
    
    def __init__(self, camera: CameraConfig, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.state = self.STATE_DISCONNECTED
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = len(self.RECONNECT_DELAYS)
        
        self.setup_ui()
        
        # Timer de reconexão
        self.reconnect_timer = QTimer()
        self.reconnect_timer.setSingleShot(True)
        self.reconnect_timer.timeout.connect(self.try_reconnect)
        
        # Iniciar conexão
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
        
        # Status da câmera
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                padding: 2px;
            }
        """)
        layout.addWidget(self.status_label, 0)
        
        # Label central com informações
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Segoe UI", 12))
        self.info_label.setStyleSheet("""
            QLabel {
                color: #a6adc8;
                background: transparent;
                border: none;
                padding: 10px;
            }
        """)
        layout.addWidget(self.info_label, 1)
        
        # Label de tentativas
        self.attempts_label = QLabel()
        self.attempts_label.setAlignment(Qt.AlignCenter)
        self.attempts_label.setFont(QFont("Segoe UI", 8))
        self.attempts_label.setStyleSheet("""
            QLabel {
                color: #6c7086;
                background: transparent;
                border: none;
                padding: 2px;
            }
        """)
        self.attempts_label.hide()
        layout.addWidget(self.attempts_label, 0)
        
        self.update_display()
    
    def update_display(self):
        """Atualiza informações exibidas baseado no estado."""
        colors = {
            self.STATE_DISCONNECTED: "#6c7086",
            self.STATE_CONNECTING: "#f9e2af",
            self.STATE_CONNECTED: "#a6e3a1",
            self.STATE_ERROR: "#f38ba8",
        }
        
        icons = {
            self.STATE_DISCONNECTED: "⚫",
            self.STATE_CONNECTING: "🟡",
            self.STATE_CONNECTED: "🟢",
            self.STATE_ERROR: "🔴",
        }
        
        color = colors.get(self.state, "#6c7086")
        icon = icons.get(self.state, "⚫")
        
        # Status superior
        status_text = {
            self.STATE_DISCONNECTED: "Desconectado",
            self.STATE_CONNECTING: "Conectando...",
            self.STATE_CONNECTED: "Conectado",
            self.STATE_ERROR: "Erro de Conexão",
        }
        
        self.status_label.setText(
            f"<span style='color:{color};'>{icon} {status_text.get(self.state, '')}</span>"
        )
        
        # Informação principal
        self.info_label.setText(
            f"📷 Câmera {self.camera.id}\n\n"
            f"IP: {self.camera.ip}:{self.camera.port}\n"
            f"Perfil: {self.camera.rtsp_path}"
        )
        
        # Tentativas
        if self.reconnect_attempts > 0 and self.state in [self.STATE_CONNECTING, self.STATE_ERROR]:
            self.attempts_label.setText(
                f"Tentativa {self.reconnect_attempts} de {self.max_reconnect_attempts}"
            )
            self.attempts_label.show()
        else:
            self.attempts_label.hide()
    
    def start_stream(self):
        """
        Inicia o stream da câmera.
        Versão simulada - será substituída por GStreamer.
        """
        self.state = self.STATE_CONNECTING
        self.reconnect_attempts = 0
        self.update_display()
        
        # Simula conexão bem-sucedida após 1 segundo
        QTimer.singleShot(1000, self._on_connected)
        
        print(f"🔗 Conectando: {self.camera.ip}")
    
    def _on_connected(self):
        """Callback de conexão bem-sucedida."""
        self.state = self.STATE_CONNECTED
        self.reconnect_attempts = 0
        self.update_display()
        print(f"✅ Conectado: {self.camera.ip}")
    
    def stop_stream(self):
        """Para o stream da câmera."""
        self.reconnect_timer.stop()
        self.state = self.STATE_DISCONNECTED
        self.update_display()
        print(f"⏹️ Parado: {self.camera.ip}")
    
    def simulate_disconnect(self):
        """
        Simula queda de conexão (para teste).
        Remove na versão final.
        """
        if self.state == self.STATE_CONNECTED:
            self.state = self.STATE_ERROR
            self.update_display()
            self.schedule_reconnect()
            print(f"❌ Simulando queda: {self.camera.ip}")
    
    def schedule_reconnect(self):
        """
        Agenda tentativa de reconexão com exponential backoff.
        """
        if self.reconnect_attempts < self.max_reconnect_attempts:
            delay = self.RECONNECT_DELAYS[self.reconnect_attempts]
            self.reconnect_attempts += 1
            self.state = self.STATE_CONNECTING
            self.update_display()
            
            print(f"🔄 Reconexão em {delay}s (tentativa {self.reconnect_attempts})")
            self.reconnect_timer.start(delay * 1000)
        else:
            # Máximo de tentativas atingido
            self.state = self.STATE_ERROR
            self.update_display()
            print(f"❌ Máximo de tentativas atingido: {self.camera.ip}")
    
    def try_reconnect(self):
        """
        Tenta reconectar ao stream.
        """
        self.state = self.STATE_CONNECTING
        self.update_display()
        
        # Simula reconexão (50% de chance de sucesso para teste)
        import random
        if random.random() > 0.3:  # 70% de sucesso
            delay = random.randint(500, 2000)
            QTimer.singleShot(delay, self._on_reconnected)
        else:
            QTimer.singleShot(1000, self._on_reconnect_failed)
        
        print(f"🔗 Tentando reconectar: {self.camera.ip}")
    
    def _on_reconnected(self):
        """Callback de reconexão bem-sucedida."""
        self.state = self.STATE_CONNECTED
        self.reconnect_attempts = 0
        self.update_display()
        print(f"✅ Reconectado: {self.camera.ip}")
    
    def _on_reconnect_failed(self):
        """Callback de falha na reconexão."""
        self.schedule_reconnect()
        print(f"❌ Falha na reconexão: {self.camera.ip}")