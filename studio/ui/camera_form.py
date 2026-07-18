"""
GPM CFTV Studio - Formulário de Câmera
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QPushButton, QLabel, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt

from studio.models.camera import Camera, RTSP_PROFILES


class CameraFormDialog(QDialog):
    """
    Diálogo para adicionar/editar câmera.
    """
    
    def __init__(self, camera: Camera = None, parent=None):
        """
        Inicializa o formulário.
        
        Args:
            camera: Câmera para edição (None = nova câmera).
            parent: Widget pai.
        """
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
        self.setMinimumWidth(500)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Configuração da Câmera IP")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Grupo: Rede
        network_group = QGroupBox("🌐 Configurações de Rede")
        network_layout = QFormLayout(network_group)
        
        self.txt_ip = QLineEdit()
        self.txt_ip.setPlaceholderText("Ex: 192.168.1.100")
        network_layout.addRow("Endereço IP:", self.txt_ip)
        
        self.spin_port = QSpinBox()
        self.spin_port.setRange(1, 65535)
        self.spin_port.setValue(554)
        network_layout.addRow("Porta RTSP:", self.spin_port)
        
        layout.addWidget(network_group)
        
        # Grupo: Autenticação
        auth_group = QGroupBox("🔐 Autenticação")
        auth_layout = QFormLayout(auth_group)
        
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Ex: admin")
        self.txt_username.setText("admin")
        auth_layout.addRow("Usuário:", self.txt_username)
        
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Senha da câmera")
        auth_layout.addRow("Senha:", self.txt_password)
        
        layout.addWidget(auth_group)
        
        # Grupo: RTSP
        rtsp_group = QGroupBox("📡 Configurações RTSP")
        rtsp_layout = QVBoxLayout(rtsp_group)
        
        # Combo de fabricante
        self.combo_manufacturer = QComboBox()
        self.combo_manufacturer.addItem("Selecione o fabricante...")
        self.combo_manufacturer.addItems(RTSP_PROFILES.keys())
        self.combo_manufacturer.currentTextChanged.connect(self.on_manufacturer_changed)
        rtsp_layout.addWidget(QLabel("Fabricante:"))
        rtsp_layout.addWidget(self.combo_manufacturer)
        
        # Combo de perfil
        self.combo_profile = QComboBox()
        self.combo_profile.addItem("Selecione o perfil...")
        rtsp_layout.addWidget(QLabel("Perfil RTSP:"))
        rtsp_layout.addWidget(self.combo_profile)
        
        # Caminho RTSP manual
        self.txt_rtsp_path = QLineEdit()
        self.txt_rtsp_path.setPlaceholderText("Ou digite o caminho manualmente...")
        rtsp_layout.addWidget(QLabel("Caminho RTSP:"))
        rtsp_layout.addWidget(self.txt_rtsp_path)
        
        # URL completa (apenas leitura)
        self.lbl_url = QLabel("URL será gerada automaticamente...")
        self.lbl_url.setStyleSheet("color: #89b4fa; font-style: italic; padding: 5px;")
        self.lbl_url.setWordWrap(True)
        rtsp_layout.addWidget(self.lbl_url)
        
        layout.addWidget(rtsp_group)
        
        # Opções
        self.chk_enabled = QCheckBox("Câmera ativa")
        self.chk_enabled.setChecked(True)
        layout.addWidget(self.chk_enabled)
        
        # Preview da URL
        self.txt_ip.textChanged.connect(self.update_url_preview)
        self.txt_rtsp_path.textChanged.connect(self.update_url_preview)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.btn_test = QPushButton("🔍 Testar Conexão")
        self.btn_test.clicked.connect(self.on_test_connection)
        buttons_layout.addWidget(self.btn_test)
        
        buttons_layout.addStretch()
        
        self.btn_save = QPushButton("💾 Salvar")
        self.btn_save.clicked.connect(self.on_save)
        buttons_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("❌ Cancelar")
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
                self.combo_profile.addItem(f"{profile_name} - {path}", path)
    
    def on_profile_selected(self, index: int):
        """Preenche caminho RTSP quando perfil selecionado."""
        if index > 0:
            path = self.combo_profile.currentData()
            if path:
                self.txt_rtsp_path.setText(path)
    
    def update_url_preview(self):
        """Atualiza preview da URL RTSP."""
        ip = self.txt_ip.text().strip()
        path = self.txt_rtsp_path.text().strip()
        
        if ip and path:
            url = f"rtsp://{self.txt_username.text()}:****@{ip}:{self.spin_port.value()}{path}"
            self.lbl_url.setText(f"URL: {url}")
        else:
            self.lbl_url.setText("Preencha IP e caminho RTSP...")
    
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