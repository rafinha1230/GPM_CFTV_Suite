"""
GPM CFTV Studio - Formulário de Câmera
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QPushButton, QLabel, QGroupBox, QMessageBox,
    QScrollArea, QWidget
)
from PySide6.QtCore import Qt, QSize

from studio.models.camera import Camera, RTSP_PROFILES


class CameraFormDialog(QDialog):
    """Diálogo para adicionar/editar câmera."""
    
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
        # Tamanho fixo adequado para notebooks
        self.setMinimumSize(480, 580)
        self.resize(520, 620)
        self.setMaximumSize(700, 800)
        self.setModal(True)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title = QLabel("Configuração da Câmera IP")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px; color: #cdd6f4;")
        main_layout.addWidget(title)
        
        # Área com scroll (garante que tudo fique visível)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        
        # ============ GRUPO REDE ============
        network_group = QGroupBox("🌐 Configurações de Rede")
        network_group.setStyleSheet(self._group_style("#89b4fa"))
        network_layout = QFormLayout(network_group)
        network_layout.setSpacing(8)
        network_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.txt_ip = QLineEdit()
        self.txt_ip.setPlaceholderText("Ex: 192.168.1.100")
        self.txt_ip.setMinimumHeight(32)
        lbl_ip = QLabel("Endereço IP:")
        lbl_ip.setFixedWidth(90)
        network_layout.addRow(lbl_ip, self.txt_ip)
        
        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)
        self.spin_port.setValue(554)
        self.spin_port.setMinimumHeight(32)
        self.spin_port.setFixedWidth(100)
        lbl_port = QLabel("Porta RTSP:")
        lbl_port.setFixedWidth(90)
        network_layout.addRow(lbl_port, self.spin_port)
        
        scroll_layout.addWidget(network_group)
        
        # ============ GRUPO AUTENTICAÇÃO ============
        auth_group = QGroupBox("🔐 Autenticação")
        auth_group.setStyleSheet(self._group_style("#f9e2af"))
        auth_layout = QFormLayout(auth_group)
        auth_layout.setSpacing(8)
        auth_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Ex: admin")
        self.txt_username.setText("admin")
        self.txt_username.setMinimumHeight(32)
        lbl_user = QLabel("Usuário:")
        lbl_user.setFixedWidth(90)
        auth_layout.addRow(lbl_user, self.txt_username)
        
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Senha da câmera")
        self.txt_password.setMinimumHeight(32)
        lbl_pass = QLabel("Senha:")
        lbl_pass.setFixedWidth(90)
        auth_layout.addRow(lbl_pass, self.txt_password)
        
        scroll_layout.addWidget(auth_group)
        
        # ============ GRUPO RTSP ============
        rtsp_group = QGroupBox("📡 Configurações RTSP")
        rtsp_group.setStyleSheet(self._group_style("#a6e3a1"))
        rtsp_layout = QVBoxLayout(rtsp_group)
        rtsp_layout.setSpacing(6)
        
        lbl_manufacturer = QLabel("Fabricante:")
        lbl_manufacturer.setStyleSheet("font-weight: bold;")
        rtsp_layout.addWidget(lbl_manufacturer)
        
        self.combo_manufacturer = QComboBox()
        self.combo_manufacturer.setMinimumHeight(32)
        self.combo_manufacturer.addItem("Selecione o fabricante...")
        self.combo_manufacturer.addItems(RTSP_PROFILES.keys())
        self.combo_manufacturer.currentTextChanged.connect(self.on_manufacturer_changed)
        rtsp_layout.addWidget(self.combo_manufacturer)
        
        lbl_profile = QLabel("Perfil RTSP:")
        lbl_profile.setStyleSheet("font-weight: bold;")
        rtsp_layout.addWidget(lbl_profile)
        
        self.combo_profile = QComboBox()
        self.combo_profile.setMinimumHeight(32)
        self.combo_profile.addItem("Selecione o perfil...")
        self.combo_profile.currentIndexChanged.connect(self.on_profile_selected)
        rtsp_layout.addWidget(self.combo_profile)
        
        lbl_path = QLabel("Caminho RTSP:")
        lbl_path.setStyleSheet("font-weight: bold;")
        rtsp_layout.addWidget(lbl_path)
        
        self.txt_rtsp_path = QLineEdit()
        self.txt_rtsp_path.setMinimumHeight(32)
        self.txt_rtsp_path.setPlaceholderText("Ou digite o caminho manualmente...")
        rtsp_layout.addWidget(self.txt_rtsp_path)
        
        self.lbl_url = QLabel("Preencha os campos para gerar a URL...")
        self.lbl_url.setStyleSheet("color: #89b4fa; font-style: italic; padding: 6px; background-color: #1e1e2e; border-radius: 4px;")
        self.lbl_url.setWordWrap(True)
        self.lbl_url.setMinimumHeight(36)
        rtsp_layout.addWidget(self.lbl_url)
        
        scroll_layout.addWidget(rtsp_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll, 1)
        
        # Eventos de preview
        self.txt_ip.textChanged.connect(self.update_url_preview)
        self.txt_username.textChanged.connect(self.update_url_preview)
        self.txt_rtsp_path.textChanged.connect(self.update_url_preview)
        self.spin_port.valueChanged.connect(self.update_url_preview)
        
        # ============ BOTÕES (SEMPRE VISÍVEIS) ============
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.btn_test = QPushButton("🔍 Testar")
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
            self.lbl_url.setText(f"🔗 {url}")
        else:
            self.lbl_url.setText("⚠️ Preencha IP e caminho RTSP...")
    
    def load_camera_data(self, camera: Camera):
        """Carrega dados da câmera no formulário."""
        self.txt_ip.setText(camera.ip)
        self.spin_port.setValue(camera.port)
        self.txt_username.setText(camera.username)
        self.txt_password.setText(camera.password)
        self.txt_rtsp_path.setText(camera.rtsp_path)
    
    def get_camera_data(self) -> Camera:
        """Obtém dados do formulário como Camera."""
        return Camera(
            ip=self.txt_ip.text().strip(),
            port=self.spin_port.value(),
            username=self.txt_username.text().strip(),
            password=self.txt_password.text(),
            rtsp_path=self.txt_rtsp_path.text().strip()
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
            f"URL: {camera.get_rtsp_url()}"
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
        """Valida antes de fechar."""
        camera = self.get_camera_data()
        valid, msg = camera.validate()
        
        if not valid:
            QMessageBox.warning(self, "Erro de Validação", msg)
            return
        
        super().accept()