"""
GPM CFTV Studio - Formulário de Câmera
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QPushButton, QLabel, QGroupBox, QMessageBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, QSize

from studio.models.camera import Camera, RTSP_PROFILES


class CameraFormDialog(QDialog):
    """
    Diálogo para adicionar/editar câmera.
    """
    
    def __init__(self, camera: Camera = None, parent=None):
        super().__init__(parent)
        self.camera = camera
        self.setup_ui()
        
        if camera:
            self.load_camera_data(camera)
            self.setWindowTitle("✏️ Editar Câmera")
        else:
            self.setWindowTitle("📷 Adicionar Nova Câmera")
    
    def setup_ui(self):
        """Configura a interface do formulário."""
        # Permitir redimensionamento
        self.setMinimumSize(550, 650)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setModal(True)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("Configuração da Câmera IP")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            padding: 10px;
            color: #cdd6f4;
        """)
        layout.addWidget(title)
        
        # Grupo: Rede
        network_group = QGroupBox("🌐 Configurações de Rede")
        network_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #89b4fa;
                border: 2px solid #45475a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px 15px 15px 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
            }
        """)
        network_layout = QFormLayout(network_group)
        network_layout.setSpacing(12)
        network_layout.setContentsMargins(10, 10, 10, 10)
        network_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        network_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # IP
        lbl_ip = QLabel("Endereço IP:")
        lbl_ip.setMinimumWidth(100)
        lbl_ip.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.txt_ip = QLineEdit()
        self.txt_ip.setPlaceholderText("Ex: 192.168.1.100")
        self.txt_ip.setMinimumHeight(35)
        network_layout.addRow(lbl_ip, self.txt_ip)
        
        # Porta
        lbl_port = QLabel("Porta RTSP:")
        lbl_port.setMinimumWidth(100)
        lbl_port.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)
        self.spin_port.setValue(554)
        self.spin_port.setMinimumHeight(35)
        self.spin_port.setMinimumWidth(120)
        network_layout.addRow(lbl_port, self.spin_port)
        
        layout.addWidget(network_group)
        
        # Grupo: Autenticação
        auth_group = QGroupBox("🔐 Autenticação")
        auth_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #f9e2af;
                border: 2px solid #45475a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px 15px 15px 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
            }
        """)
        auth_layout = QFormLayout(auth_group)
        auth_layout.setSpacing(12)
        auth_layout.setContentsMargins(10, 10, 10, 10)
        auth_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        auth_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Usuário
        lbl_user = QLabel("Usuário:")
        lbl_user.setMinimumWidth(100)
        lbl_user.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Ex: admin")
        self.txt_username.setText("admin")
        self.txt_username.setMinimumHeight(35)
        auth_layout.addRow(lbl_user, self.txt_username)
        
        # Senha
        lbl_pass = QLabel("Senha:")
        lbl_pass.setMinimumWidth(100)
        lbl_pass.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Senha da câmera")
        self.txt_password.setMinimumHeight(35)
        auth_layout.addRow(lbl_pass, self.txt_password)
        
        layout.addWidget(auth_group)
        
        # Grupo: RTSP
        rtsp_group = QGroupBox("📡 Configurações RTSP")
        rtsp_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #a6e3a1;
                border: 2px solid #45475a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px 15px 15px 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
            }
        """)
        rtsp_layout = QVBoxLayout(rtsp_group)
        rtsp_layout.setSpacing(10)
        rtsp_layout.setContentsMargins(10, 10, 10, 10)
        
        # Fabricante
        lbl_manufacturer = QLabel("Fabricante:")
        lbl_manufacturer.setStyleSheet("font-weight: bold; margin-top: 5px;")
        rtsp_layout.addWidget(lbl_manufacturer)
        
        self.combo_manufacturer = QComboBox()
        self.combo_manufacturer.setMinimumHeight(35)
        self.combo_manufacturer.addItem("Selecione o fabricante...")
        self.combo_manufacturer.addItems(RTSP_PROFILES.keys())
        self.combo_manufacturer.currentTextChanged.connect(self.on_manufacturer_changed)
        rtsp_layout.addWidget(self.combo_manufacturer)
        
        # Perfil
        lbl_profile = QLabel("Perfil RTSP:")
        lbl_profile.setStyleSheet("font-weight: bold; margin-top: 5px;")
        rtsp_layout.addWidget(lbl_profile)
        
        self.combo_profile = QComboBox()
        self.combo_profile.setMinimumHeight(35)
        self.combo_profile.addItem("Selecione o perfil...")
        self.combo_profile.currentIndexChanged.connect(self.on_profile_selected)
        rtsp_layout.addWidget(self.combo_profile)
        
        # Caminho manual
        lbl_path = QLabel("Caminho RTSP:")
        lbl_path.setStyleSheet("font-weight: bold; margin-top: 5px;")
        rtsp_layout.addWidget(lbl_path)
        
        self.txt_rtsp_path = QLineEdit()
        self.txt_rtsp_path.setMinimumHeight(35)
        self.txt_rtsp_path.setPlaceholderText("Ou digite o caminho manualmente...")
        rtsp_layout.addWidget(self.txt_rtsp_path)
        
        # URL preview
        self.lbl_url = QLabel("Preencha os campos para gerar a URL...")
        self.lbl_url.setStyleSheet("""
            color: #89b4fa; 
            font-style: italic; 
            padding: 8px;
            background-color: #1e1e2e;
            border-radius: 5px;
        """)
        self.lbl_url.setWordWrap(True)
        self.lbl_url.setMinimumHeight(40)
        rtsp_layout.addWidget(self.lbl_url)
        
        layout.addWidget(rtsp_group)
        
        # Checkbox ativo
        self.chk_enabled = QCheckBox("✅ Câmera ativa")
        self.chk_enabled.setChecked(True)
        self.chk_enabled.setStyleSheet("""
            font-size: 13px;
            font-weight: bold;
            padding: 5px;
        """)
        layout.addWidget(self.chk_enabled)
        
        # Conectar eventos para preview
        self.txt_ip.textChanged.connect(self.update_url_preview)
        self.txt_username.textChanged.connect(self.update_url_preview)
        self.txt_rtsp_path.textChanged.connect(self.update_url_preview)
        self.spin_port.valueChanged.connect(self.update_url_preview)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.btn_test = QPushButton("🔍 Testar Conexão")
        self.btn_test.setMinimumHeight(40)
        self.btn_test.clicked.connect(self.on_test_connection)
        buttons_layout.addWidget(self.btn_test)
        
        buttons_layout.addStretch()
        
        self.btn_save = QPushButton("💾 Salvar")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.setMinimumWidth(120)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #94e2d5;
            }
        """)
        buttons_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("❌ Cancelar")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.setMinimumWidth(120)
        self.btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(buttons_layout)
    
    def on_manufacturer_changed(self, manufacturer: str):
        """Atualiza perfis quando fabricante muda."""
        self.combo_profile.clear()
        self.combo_profile.addItem("Selecione o perfil...")
        
        if manufacturer in RTSP_PROFILES:
            profiles = RTSP_PROFILES[manufacturer]
            for profile_name, path in profiles.items():
                self.combo_profile.addItem(f"{profile_name} → {path}", path)
    
    def on_profile_selected(self, index: int):
        """Preenche caminho RTSP quando perfil selecionado."""
        if index > 0:
            path = self.combo_profile.currentData()
            if path:
                self.txt_rtsp_path.setText(path)
    
    def update_url_preview(self):
        """Atualiza preview da URL RTSP."""
        ip = self.txt_ip.text().strip()
        port = self.spin_port.value()
        username = self.txt_username.text().strip()
        path = self.txt_rtsp_path.text().strip()
        
        if ip and path:
            url = f"rtsp://{username}:****@{ip}:{port}{path}"
            self.lbl_url.setText(f"🔗 URL: {url}")
        else:
            self.lbl_url.setText("⚠️ Preencha IP, usuário e caminho RTSP para gerar a URL...")
    
    def load_camera_data(self, camera: Camera):
        """Carrega dados da câmera no formulário."""
        self.txt_ip.setText(camera.ip)
        self.spin_port.setValue(camera.port)
        self.txt_username.setText(camera.username)
        self.txt_password.setText(camera.password)
        self.txt_rtsp_path.setText(camera.rtsp_path)
        self.chk_enabled.setChecked(camera.enabled)
    
    def get_camera_data(self) -> Camera:
        """Obtém dados do formulário como Camera."""
        return Camera(
            ip=self.txt_ip.text().strip(),
            port=self.spin_port.value(),
            username=self.txt_username.text().strip(),
            password=self.txt_password.text(),
            rtsp_path=self.txt_rtsp_path.text().strip(),
            enabled=self.chk_enabled.isChecked()
        )
    
    def on_test_connection(self):
        """Testa conexão com a câmera."""
        camera = self.get_camera_data()
        valid, msg = camera.validate()
        
        if not valid:
            QMessageBox.warning(self, "Validação", msg)
            return
        
        QMessageBox.information(
            self,
            "Teste de Conexão",
            f"Funcionalidade em desenvolvimento!\n\n"
            f"URL a ser testada:\n{camera.get_rtsp_url()}"
        )
    
    def on_save(self):
        """Salva a câmera."""
        camera = self.get_camera_data()
        valid, msg = camera.validate()
        
        if not valid:
            QMessageBox.warning(self, "Erro de Validação", msg)
            return
        
        self.accept()
    
    def accept(self):
        """Sobrescreve accept para validar antes de fechar."""
        camera = self.get_camera_data()
        valid, msg = camera.validate()
        
        if not valid:
            QMessageBox.warning(self, "Erro de Validação", msg)
            return
        
        super().accept()