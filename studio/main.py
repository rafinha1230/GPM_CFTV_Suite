#!/usr/bin/env python3
"""
GPM CFTV Studio - Ferramenta de Configuração de Câmeras
Versão: 1.0.0
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QPushButton, QFrame, QStatusBar, QListWidget,
    QListWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon

from studio.core.camera_manager import CameraManager
from studio.ui.camera_form import CameraFormDialog


class MainWindow(QMainWindow):
    """Janela Principal do GPM CFTV Studio."""
    
    def __init__(self):
        super().__init__()
        self.camera_manager = CameraManager()
        print(f"🔧 Inicializando GPM CFTV Studio...")
        print(f"📷 Câmeras carregadas: {self.camera_manager.count()}")
        self.setup_ui()
        self.apply_styles()
        self.refresh_camera_list()
        print("✅ Interface carregada com sucesso!")
    
    def setup_ui(self):
        """Configura a interface do usuário."""
        self.setWindowTitle("GPM CFTV Studio v1.0.0")
        self.setMinimumSize(QSize(900, 650))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Cabeçalho
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QVBoxLayout(header_frame)
        
        title = QLabel("🎥 GPM CFTV Studio")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        header_layout.addWidget(title)
        
        subtitle = QLabel("Configuração de Câmeras IP - Armazém Paraíba")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 14))
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header_frame)
        
        # Área de conteúdo
        content_layout = QHBoxLayout()
        
        # Lista de câmeras
        list_frame = QFrame()
        list_frame.setFrameStyle(QFrame.StyledPanel)
        list_layout = QVBoxLayout(list_frame)
        
        list_title = QLabel("📋 Câmeras Cadastradas")
        list_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        list_layout.addWidget(list_title)
        
        self.camera_list = QListWidget()
        self.camera_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.camera_list.itemDoubleClicked.connect(self.on_edit_camera)
        list_layout.addWidget(self.camera_list)
        
        self.lbl_count = QLabel("Nenhuma câmera cadastrada")
        self.lbl_count.setAlignment(Qt.AlignCenter)
        list_layout.addWidget(self.lbl_count)
        
        content_layout.addWidget(list_frame, 2)
        
        # Painel de ações
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.StyledPanel)
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setSpacing(10)
        
        actions_title = QLabel("⚡ Ações")
        actions_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        actions_layout.addWidget(actions_title)
        
        self.btn_add = QPushButton("📷 Adicionar Câmera")
        self.btn_add.setMinimumHeight(45)
        self.btn_add.clicked.connect(self.on_add_camera)
        actions_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("✏️ Editar Câmera")
        self.btn_edit.setMinimumHeight(45)
        self.btn_edit.clicked.connect(self.on_edit_camera)
        actions_layout.addWidget(self.btn_edit)
        
        self.btn_remove = QPushButton("🗑️ Remover Câmera")
        self.btn_remove.setMinimumHeight(45)
        self.btn_remove.clicked.connect(self.on_remove_camera)
        actions_layout.addWidget(self.btn_remove)
        
        actions_layout.addStretch()
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        actions_layout.addWidget(separator)
        
        self.btn_generate = QPushButton("🚀 Gerar Viewer")
        self.btn_generate.setMinimumHeight(50)
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4d0fb;
            }
        """)
        self.btn_generate.clicked.connect(self.on_generate_viewer)
        actions_layout.addWidget(self.btn_generate)
        
        content_layout.addWidget(actions_frame, 1)
        main_layout.addLayout(content_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"✅ Pronto | {self.camera_manager.count()} câmera(s)")
    
    def apply_styles(self):
        """Aplica estilos CSS."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QFrame {
                background-color: #313244;
                border: 2px solid #45475a;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
            QLabel {
                color: #cdd6f4;
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: 2px solid #585b70;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #585b70;
                border-color: #89b4fa;
            }
            QPushButton:pressed {
                background-color: #313244;
            }
            QListWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 2px solid #45475a;
                border-radius: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #45475a;
            }
            QListWidget::item:selected {
                background-color: #45475a;
                color: #89b4fa;
            }
            QListWidget::item:hover {
                background-color: #313244;
            }
            QStatusBar {
                background-color: #313244;
                color: #a6adc8;
                border-top: 2px solid #45475a;
            }
        """)
    
    def refresh_camera_list(self):
        """Atualiza a lista de câmeras na interface."""
        self.camera_list.clear()
        cameras = self.camera_manager.get_all()
        
        for camera in cameras:
            status_icon = "🟢" if camera.enabled else "🔴"
            item_text = f"{status_icon} {camera.ip}:{camera.port} - {camera.rtsp_path}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, camera.id)
            self.camera_list.addItem(item)
        
        count = self.camera_manager.count()
        self.lbl_count.setText(f"{count} câmera(s) cadastrada(s)")
        self.status_bar.showMessage(f"✅ Pronto | {count} câmera(s)")
    
    def on_add_camera(self):
        """Abre formulário para adicionar câmera."""
        dialog = CameraFormDialog(parent=self)
        if dialog.exec():
            camera = dialog.get_camera_data()
            if self.camera_manager.add(camera):
                self.refresh_camera_list()
                self.status_bar.showMessage("✅ Câmera adicionada com sucesso!")
    
    def on_edit_camera(self):
        """Abre formulário para editar câmera selecionada."""
        current_item = self.camera_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Aviso", "Selecione uma câmera para editar!")
            return
        
        camera_id = current_item.data(Qt.UserRole)
        camera = self.camera_manager.get(camera_id)
        
        if camera:
            dialog = CameraFormDialog(camera, parent=self)
            if dialog.exec():
                updated_camera = dialog.get_camera_data()
                if self.camera_manager.update(camera_id, updated_camera):
                    self.refresh_camera_list()
                    self.status_bar.showMessage("✅ Câmera atualizada com sucesso!")
    
    def on_remove_camera(self):
        """Remove a câmera selecionada."""
        current_item = self.camera_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Aviso", "Selecione uma câmera para remover!")
            return
        
        camera_id = current_item.data(Qt.UserRole)
        camera = self.camera_manager.get(camera_id)
        
        reply = QMessageBox.question(
            self,
            "Confirmar Remoção",
            f"Deseja realmente remover a câmera?\n\n"
            f"IP: {camera.ip}:{camera.port}\n"
            f"Caminho: {camera.rtsp_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.camera_manager.remove(camera_id)
            self.refresh_camera_list()
            self.status_bar.showMessage("🗑️ Câmera removida")
    
    def on_generate_viewer(self):
        """Gera o pacote do Viewer."""
        enabled = self.camera_manager.get_enabled()
        if not enabled:
            QMessageBox.warning(self, "Aviso", "Nenhuma câmera ativa para gerar o Viewer!")
            return
        
        QMessageBox.information(
            self,
            "🚀 Gerar Viewer",
            f"Funcionalidade em desenvolvimento!\n\n"
            f"Câmeras ativas: {len(enabled)}\n"
            f"O Viewer será gerado como AppImage para Linux."
        )
    
    def closeEvent(self, event):
        """Confirmação ao fechar."""
        reply = QMessageBox.question(
            self,
            'Confirmar Saída',
            'Deseja realmente sair do GPM CFTV Studio?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
            print("👋 GPM CFTV Studio encerrado.")
        else:
            event.ignore()


def main():
    """Função principal."""
    print("=" * 60)
    print("🎥 GPM CFTV Studio v1.0.0")
    print("📅 Iniciando aplicação...")
    print("💻 Desenvolvimento: code-server")
    print("=" * 60)
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("GPM CFTV Studio")
        app.setOrganizationName("GPM Manutenção")
        app.setOrganizationDomain("armazemparaiba.com.br")
        
        window = MainWindow()
        window.show()
        
        print("✅ Aplicação iniciada com sucesso!")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()