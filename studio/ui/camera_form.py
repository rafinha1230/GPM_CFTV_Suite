"""
GPM CFTV Studio - Formulário de Câmera Super Automático
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba

Só digita IP, Usuário, Senha e clica em Salvar.
O programa detecta todo o resto sozinho!
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
        self.progress.emit("Procurando câmera na rede...")
        result = RTSPTester.auto_detect(self.ip, self.username, self.password)
        if result:
            self.finished.emit(result)
        else:
            self.error.emit("Câmera não encontrada. Configure manualmente.")


class CameraFormDialog(QDialog):
    """Diálogo super automático - só IP, Usuário e Senha."""
    
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
        self.setMinimumSize(450, 320)
        self.resize(480, 350)
        self.setMaximumSize(600, 500)
        self.setModal(True)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("Nova Câmera IP")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px; color: #cdd6f4;")
        main_layout.addWidget(title)
        
        subtitle = QLabel("Digite apenas IP, Usuário e Senha.\nO resto é automático!")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #a6adc8; font-size: 11px; padding: 0px;")
        main_layout.addWidget(subtitle)
        
        # ============ CAMPOS PRINCIPAIS ============
        fields_group = QGroupBox("📋 Dados de Acesso")
        fields_group.setStyleSheet(self._group_style("#89b4fa"))
        fields_layout = QFormLayout(fields_group)
        fields_layout.setSpacing(10)
        fields_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # IP
        self.txt_ip = QLineEdit()
        self.txt_ip.setPlaceholderText("Ex: 192.168.1.100")
        self.txt_ip.setMinimumHeight(36)
        lbl_ip = QLabel("Endereço IP:")
        lbl_ip.setFixedWidth(85)
        lbl_ip.setStyleSheet("font-weight: bold;")
        fields_layout.addRow(lbl_ip, self.txt_ip)
        
        # Usuário
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Ex: admin")
        self.txt_username.setText("admin")
        self.txt_username.setMinimumHeight(36)
        lbl_user = QLabel("Usuário:")
        lbl_user.setFixedWidth(85)
        lbl_user.setStyleSheet("font-weight: bold;")
        fields_layout.addRow(lbl_user, self.txt_username)
        
        # Senha
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Senha da câmera")
        self.txt_password.setMinimumHeight(36)
        lbl_pass = QLabel("Senha:")
        lbl_pass.setFixedWidth(85)
        lbl_pass.setStyleSheet("font-weight: bold;")
        fields_layout.addRow(lbl_pass, self.txt_password)
        
        main_layout.addWidget(fields_group)
        
        # Status da detecção
        self.lbl_status = QLabel("Preencha os campos e clique em Salvar")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet("color: #a6adc8; font-style: italic; padding: 8px;")
        self.lbl_status.setWordWrap(True)
        main_layout.addWidget(self.lbl_status)
        
        # Campos ocultos (preenchidos automaticamente)
        self.txt_rtsp_path = QLineEdit()
        self.txt_rtsp_path.setVisible(False)
        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)
        self.spin_port.setValue(554)
        self.spin_port.setVisible(False)
        
        main_layout.addStretch()
        
        # ============ BOTÕES ============
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.btn_save = QPushButton("💾 Salvar (Auto-Detectar)")
        self.btn_save.setMinimumHeight(42)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
                font-weight: bold;
                font-size: 13px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #94e2d5;
            }
        """)
        buttons_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setMinimumHeight(42)
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
                padding: 20px 15px 15px 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
            }}
        """
    
    def on_save(self):
        """Salva com auto-detecção automática."""
        ip = self.txt_ip.text().strip()
        username = self.txt_username.text().strip()
        password = self.txt_password.text()
        
        # Validar campos
        if not ip:
            QMessageBox.warning(self, "Aviso", "Digite o endereço IP!")
            self.txt_ip.setFocus()
            return
        
        if not username:
            QMessageBox.warning(self, "Aviso", "Digite o nome de usuário!")
            self.txt_username.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "Aviso", "Digite a senha!")
            self.txt_password.setFocus()
            return
        
        # Se já tem configuração detectada, salva direto
        if self.detected_config:
            self.accept()
            return
        
        # Se já tem caminho RTSP manual (edição), salva direto
        if self.camera and self.txt_rtsp_path.text().strip():
            self.accept()
            return
        
        # Auto-detectar
        self.btn_save.setEnabled(False)
        self.btn_save.setText("⏳ Detectando câmera...")
        self.lbl_status.setText("Procurando câmera na rede...")
        self.lbl_status.setStyleSheet("color: #f9e2af; font-weight: bold; padding: 8px;")
        
        self.worker = AutoDetectWorker(ip, username, password)
        self.worker.finished.connect(self._on_detected)
        self.worker.error.connect(self._on_not_detected)
        self.worker.progress.connect(self.lbl_status.setText)
        self.worker.start()
    
    def _on_detected(self, result: dict):
        """Câmera detectada - salva automaticamente."""
        self.detected_config = result
        
        # Preencher campos ocultos
        self.txt_rtsp_path.setText(result.get('rtsp_path', ''))
        self.spin_port.setValue(result.get('port', 554))
        
        self.lbl_status.setText(
            f"✅ Detectada: {result.get('manufacturer', '')} | "
            f"Porta {result.get('port', 554)} | "
            f"{result.get('profile', 'main')}"
        )
        self.lbl_status.setStyleSheet("color: #a6e3a1; font-weight: bold; padding: 8px;")
        
        self.btn_save.setEnabled(True)
        self.btn_save.setText("💾 Salvar")
        
        # Salvar automaticamente
        self.accept()
    
    def _on_not_detected(self, error_msg: str):
        """Câmera não detectada - mostra manual."""
        self.btn_save.setEnabled(True)
        self.btn_save.setText("💾 Salvar")
        
        self.lbl_status.setText(f"❌ {error_msg}")
        self.lbl_status.setStyleSheet("color: #f38ba8; font-weight: bold; padding: 8px;")
        
        # Mostrar diálogo para configurar manualmente
        reply = QMessageBox.question(
            self,
            "Câmera não detectada",
            f"{error_msg}\n\n"
            f"Deseja configurar manualmente?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self._show_manual_config()
    
    def _show_manual_config(self):
        """Mostra diálogo de configuração manual."""
        dialog = ManualConfigDialog(self)
        if dialog.exec():
            self.txt_rtsp_path.setText(dialog.txt_path.text().strip())
            self.spin_port.setValue(dialog.spin_port.value())
            self.accept()
    
    def load_camera_data(self, camera: Camera):
        """Carrega dados da câmera no formulário."""
        self.txt_ip.setText(camera.ip)
        self.txt_username.setText(camera.username)
        self.txt_password.setText(camera.password)
        self.txt_rtsp_path.setText(camera.rtsp_path)
        self.spin_port.setValue(camera.port)
    
    def get_camera_data(self) -> Camera:
        """Obtém dados do formulário como Camera."""
        if self.detected_config:
            port = self.detected_config.get('port', 554)
            rtsp_path = self.detected_config.get('rtsp_path', '')
        else:
            port = self.spin_port.value()
            rtsp_path = self.txt_rtsp_path.text().strip()
        
        return Camera(
            ip=self.txt_ip.text().strip(),
            port=port,
            username=self.txt_username.text().strip(),
            password=self.txt_password.text(),
            rtsp_path=rtsp_path
        )
    
    def accept(self):
        """Valida antes de fechar."""
        camera = self.get_camera_data()
        valid, msg = camera.validate()
        
        if not valid:
            QMessageBox.warning(self, "Erro de Validação", msg)
            return
        
        super().accept()


class ManualConfigDialog(QDialog):
    """Diálogo simples para configuração manual."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Configuração Manual")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Configure os parâmetros RTSP manualmente")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-weight: bold; color: #cdd6f4;")
        layout.addWidget(title)
        
        form = QFormLayout()
        form.setSpacing(8)
        
        # Porta
        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)
        self.spin_port.setValue(554)
        self.spin_port.setMinimumHeight(32)
        form.addRow("Porta RTSP:", self.spin_port)
        
        # Fabricante
        self.combo_manufacturer = QComboBox()
        self.combo_manufacturer.addItem("Selecione o fabricante...")
        self.combo_manufacturer.addItems(RTSP_PROFILES.keys())
        self.combo_manufacturer.currentTextChanged.connect(self._on_manufacturer_changed)
        form.addRow("Fabricante:", self.combo_manufacturer)
        
        # Caminho
        self.txt_path = QLineEdit()
        self.txt_path.setPlaceholderText("Ex: /Streaming/Channels/101")
        self.txt_path.setMinimumHeight(32)
        form.addRow("Caminho RTSP:", self.txt_path)
        
        layout.addLayout(form)
        layout.addStretch()
        
        # Botões
        buttons = QHBoxLayout()
        btn_ok = QPushButton("✅ OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        buttons.addWidget(btn_ok)
        buttons.addWidget(btn_cancel)
        layout.addLayout(buttons)
    
    def _on_manufacturer_changed(self, manufacturer: str):
        """Preenche caminho ao selecionar fabricante."""
        if manufacturer in RTSP_PROFILES:
            profiles = RTSP_PROFILES[manufacturer]
            first_path = list(profiles.values())[0]
            self.txt_path.setText(first_path)