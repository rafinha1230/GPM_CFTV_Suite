"""
GPM CFTV Studio - Formulário de Câmera Simplificado
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox,
    QPushButton, QLabel, QGroupBox, QMessageBox,
    QScrollArea, QWidget, QProgressDialog
)
from PySide6.QtCore import Qt, QThread, Signal

from studio.models.camera import Camera, RTSP_PROFILES
from studio.core.rtsp_tester import RTSPTester


class AutoDetectWorker(QThread):
    """Thread para auto-detecção sem travar a interface."""
    finished = Signal(dict)
    progress = Signal(str)
    error = Signal(str)
    
    def __init__(self, ip, username, password):
        super().__init__()
        self.ip = ip
        self.username = username
        self.password = password
    
    def run(self):
        self.progress.emit("Testando conexão com a câmera...")
        result = RTSPTester.auto_detect(self.ip, self.username, self.password)
        if result:
            self.finished.emit(result)
        else:
            self.error.emit("Não foi possível detectar a câmera automaticamente.")


class CameraFormDialog(QDialog):
    """Diálogo simplificado para adicionar/editar câmera."""
    
    def __init__(self, camera: Camera = None, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.detected_config = None
        self.setup_ui()
        
        if camera:
            self.load_camera_data(camera)
            self.setWindowTitle("✏️ Editar Câmera")
        else:
            self.setWindowTitle("📷 Adicionar Nova Câmera")
    
    def setup_ui(self):
        """Configura a interface simplificada."""
        self.setMinimumSize(450, 400)
        self.resize(480, 450)
        self.setMaximumSize(600, 600)
        self.setModal(True)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title = QLabel("Configuração da Câmera IP")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px; color: #cdd6f4;")
        main_layout.addWidget(title)
        
        # Área com scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        
        # ============ DADOS BÁSICOS ============
        basic_group = QGroupBox("📋 Dados da Câmera")
        basic_group.setStyleSheet(self._group_style("#89b4fa"))
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(8)
        basic_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # IP
        self.txt_ip = QLineEdit()
        self.txt_ip.setPlaceholderText("Ex: 192.168.1.100")
        self.txt_ip.setMinimumHeight(32)
        lbl_ip = QLabel("Endereço IP:")
        lbl_ip.setFixedWidth(90)
        basic_layout.addRow(lbl_ip, self.txt_ip)
        
        # Usuário
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Ex: admin")
        self.txt_username.setText("admin")
        self.txt_username.setMinimumHeight(32)
        lbl_user = QLabel("Usuário:")
        lbl_user.setFixedWidth(90)
        basic_layout.addRow(lbl_user, self.txt_username)
        
        # Senha
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Senha da câmera")
        self.txt_password.setMinimumHeight(32)
        lbl_pass = QLabel("Senha:")
        lbl_pass.setFixedWidth(90)
        basic_layout.addRow(lbl_pass, self.txt_password)
        
        scroll_layout.addWidget(basic_group)
        
        # ============ BOTÃO AUTO-DETECTAR ============
        detect_layout = QHBoxLayout()
        
        self.btn_detect = QPushButton("🔍 Auto-Detectar Câmera")
        self.btn_detect.setMinimumHeight(42)
        self.btn_detect.clicked.connect(self.on_auto_detect)
        self.btn_detect.setStyleSheet("""
            QPushButton {
                background-color: #f9e2af;
                color: #1e1e2e;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f5c2e7;
            }
        """)
        detect_layout.addWidget(self.btn_detect)
        
        scroll_layout.addLayout(detect_layout)
        
        # Status da detecção
        self.lbl_detect_status = QLabel("")
        self.lbl_detect_status.setAlignment(Qt.AlignCenter)
        self.lbl_detect_status.setStyleSheet("color: #a6adc8; font-style: italic; padding: 5px;")
        self.lbl_detect_status.setWordWrap(True)
        scroll_layout.addWidget(self.lbl_detect_status)
        
        # ============ CONFIGURAÇÕES DETECTADAS ============
        detected_group = QGroupBox("📡 Configurações Detectadas (Automático)")
        detected_group.setStyleSheet(self._group_style("#a6e3a1"))
        detected_layout = QFormLayout(detected_group)
        detected_layout.setSpacing(8)
        
        self.lbl_manufacturer = QLabel("--")
        self.lbl_manufacturer.setStyleSheet("font-weight: bold; color: #a6e3a1;")
        detected_layout.addRow("Fabricante:", self.lbl_manufacturer)
        
        self.lbl_port = QLabel("--")
        detected_layout.addRow("Porta:", self.lbl_port)
        
        self.lbl_profile = QLabel("--")
        detected_layout.addRow("Perfil:", self.lbl_profile)
        
        self.lbl_path = QLabel("--")
        self.lbl_path.setWordWrap(True)
        detected_layout.addRow("Caminho RTSP:", self.lbl_path)
        
        # Campos ocultos (preenchidos automaticamente)
        self.txt_rtsp_path = QLineEdit()
        self.txt_rtsp_path.setVisible(False)
        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)
        self.spin_port.setValue(554)
        self.spin_port.setVisible(False)
        
        scroll_layout.addWidget(detected_group)
        
        # ============ CONFIGURAÇÃO MANUAL (opcional) ============
        manual_group = QGroupBox("⚙️ Configuração Manual (Opcional)")
        manual_group.setStyleSheet(self._group_style("#6c7086"))
        manual_layout = QFormLayout(manual_group)
        manual_layout.setSpacing(8)
        
        # Porta manual
        manual_port_layout = QHBoxLayout()
        self.spin_port_manual = QSpinBox()
        self.spin_port_manual.setRange(1, 65535)
        self.spin_port_manual.setValue(554)
        self.spin_port_manual.setMinimumHeight(32)
        self.spin_port_manual.setFixedWidth(100)
        manual_port_layout.addWidget(self.spin_port_manual)
        manual_port_layout.addStretch()
        manual_layout.addRow("Porta RTSP:", manual_port_layout)
        
        # Caminho manual
        self.txt_rtsp_path_manual = QLineEdit()
        self.txt_rtsp_path_manual.setPlaceholderText("Ex: /Streaming/Channels/101")
        self.txt_rtsp_path_manual.setMinimumHeight(32)
        manual_layout.addRow("Caminho RTSP:", self.txt_rtsp_path_manual)
        
        # Fabricante
        self.combo_manufacturer = QComboBox()
        self.combo_manufacturer.setMinimumHeight(32)
        self.combo_manufacturer.addItem("Selecione o fabricante...")
        self.combo_manufacturer.addItems(RTSP_PROFILES.keys())
        self.combo_manufacturer.currentTextChanged.connect(self.on_manufacturer_changed)
        manual_layout.addRow("Fabricante:", self.combo_manufacturer)
        
        scroll_layout.addWidget(manual_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1)
        
        # ============ BOTÕES ============
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.btn_test = QPushButton("🔍 Testar Conexão")
        self.btn_test.setMinimumHeight(38)
        self.btn_test.clicked.connect(self.on_test_connection)
        buttons_layout.addWidget(self.btn_test)
        
        buttons_layout.addStretch()
        
        self.btn_save = QPushButton("💾 Salvar")
        self.btn_save.setMinimumHeight(38)
        self.btn_save.setFixedWidth(110)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #94e2d5;
            }
        """)
        buttons_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setMinimumHeight(38)
        self.btn_cancel.setFixedWidth(110)
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)
        
        main_layout.addLayout(buttons_layout)
    
    def _group_style(self, color: str) -> str:
        """Retorna estilo para GroupBox."""
        return f"""
            QGroupBox {{
                font-size: 13px;
                font-weight: bold;
                color: {color};
                border: 2px solid #45475a;
                border-radius: 8px;
                margin-top: 8px;
                padding: 18px 12px 10px 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
        """
    
    def on_manufacturer_changed(self, manufacturer: str):
        """Preenche caminho RTSP ao selecionar fabricante."""
        if manufacturer in RTSP_PROFILES:
            profiles = RTSP_PROFILES[manufacturer]
            first_profile = list(profiles.keys())[0]
            first_path = profiles[first_profile]
            self.txt_rtsp_path_manual.setText(first_path)
            self.txt_rtsp_path_manual.setStyleSheet("background-color: #313244; color: #a6e3a1;")
    
    def on_auto_detect(self):
        """Auto-detecta configurações da câmera."""
        ip = self.txt_ip.text().strip()
        username = self.txt_username.text().strip()
        password = self.txt_password.text()
        
        if not ip:
            QMessageBox.warning(self, "Aviso", "Digite o endereço IP primeiro!")
            return
        
        if not username:
            QMessageBox.warning(self, "Aviso", "Digite o nome de usuário!")
            return
        
        # Desabilitar botão durante detecção
        self.btn_detect.setEnabled(False)
        self.btn_detect.setText("⏳ Detectando...")
        self.lbl_detect_status.setText("Procurando câmera...")
        
        # Criar worker thread
        self.worker = AutoDetectWorker(ip, username, password)
        self.worker.finished.connect(self.on_detect_success)
        self.worker.error.connect(self.on_detect_error)
        self.worker.progress.connect(self.lbl_detect_status.setText)
        self.worker.start()
    
    def on_detect_success(self, result: dict):
        """Callback de detecção bem-sucedida."""
        self.btn_detect.setEnabled(True)
        self.btn_detect.setText("🔍 Auto-Detectar Câmera")
        
        self.detected_config = result
        
        # Preencher campos
        self.lbl_manufacturer.setText(f"✅ {result.get('manufacturer', 'Detectado')}")
        self.lbl_port.setText(f"✅ {result.get('port', 554)}")
        self.lbl_profile.setText(f"✅ {result.get('profile', 'main')}")
        self.lbl_path.setText(f"✅ {result.get('rtsp_path', '')}")
        
        # Preencher campos ocultos
        self.txt_rtsp_path.setText(result.get('rtsp_path', ''))
        self.spin_port.setValue(result.get('port', 554))
        
        self.lbl_detect_status.setText("✅ Câmera detectada com sucesso!")
        self.lbl_detect_status.setStyleSheet("color: #a6e3a1; font-weight: bold; padding: 5px;")
    
    def on_detect_error(self, error_msg: str):
        """Callback de erro na detecção."""
        self.btn_detect.setEnabled(True)
        self.btn_detect.setText("🔍 Auto-Detectar Câmera")
        
        self.lbl_manufacturer.setText("❌ Não detectado")
        self.lbl_port.setText("❌")
        self.lbl_profile.setText("❌")
        self.lbl_path.setText("❌")
        
        self.lbl_detect_status.setText(f"❌ {error_msg}\nUse a configuração manual abaixo.")
        self.lbl_detect_status.setStyleSheet("color: #f38ba8; font-weight: bold; padding: 5px;")
        
        QMessageBox.warning(
            self,
            "Câmera não detectada",
            f"{error_msg}\n\n"
            f"Você pode configurar manualmente\n"
            f"os parâmetros na seção 'Configuração Manual'."
        )
    
    def load_camera_data(self, camera: Camera):
        """Carrega dados da câmera no formulário."""
        self.txt_ip.setText(camera.ip)
        self.txt_username.setText(camera.username)
        self.txt_password.setText(camera.password)
        self.txt_rtsp_path.setText(camera.rtsp_path)
        self.spin_port.setValue(camera.port)
        self.spin_port_manual.setValue(camera.port)
        self.txt_rtsp_path_manual.setText(camera.rtsp_path)
        
        if camera.rtsp_path:
            self.lbl_path.setText(f"✅ {camera.rtsp_path}")
            self.lbl_port.setText(f"✅ {camera.port}")
    
    def get_camera_data(self) -> Camera:
        """Obtém dados do formulário como Camera."""
        # Se detectou automaticamente, usa os valores detectados
        if self.detected_config:
            port = self.detected_config.get('port', 554)
            rtsp_path = self.detected_config.get('rtsp_path', '')
        else:
            # Usa valores manuais
            port = self.spin_port_manual.value()
            rtsp_path = self.txt_rtsp_path_manual.text().strip()
        
        return Camera(
            ip=self.txt_ip.text().strip(),
            port=port,
            username=self.txt_username.text().strip(),
            password=self.txt_password.text(),
            rtsp_path=rtsp_path
        )
    
    def on_test_connection(self):
        """Testa conexão com a câmera."""
        camera = self.get_camera_data()
        valid, msg = camera.validate()
        
        if not valid:
            QMessageBox.warning(self, "Validação", msg)
            return
        
        status, msg = RTSPTester.test_camera(camera)
        
        if status:
            QMessageBox.information(self, "✅ Conexão OK", f"Câmera conectada!\n\n{msg}")
        else:
            QMessageBox.warning(self, "❌ Falha", f"Erro na conexão:\n{msg}")
    
    def on_save(self):
        """Salva a câmera."""
        self.accept()
    
    def accept(self):
        """Valida antes de fechar."""
        camera = self.get_camera_data()
        valid, msg = camera.validate()
        
        # Se o erro for caminho RTSP vazio, tenta pegar do campo manual
        if not valid and "Caminho RTSP" in msg:
            if self.txt_rtsp_path_manual.text().strip():
                camera.rtsp_path = self.txt_rtsp_path_manual.text().strip()
                valid, msg = camera.validate()
        
        if not valid:
            QMessageBox.warning(self, "Erro de Validação", msg)
            return
        
        super().accept()