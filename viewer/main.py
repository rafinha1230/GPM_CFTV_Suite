#!/usr/bin/env python3
"""
GPM CFTV Viewer - Visualizador de Câmeras IP
Versão: 1.0.0
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import sys
from pathlib import Path
import random

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QVBoxLayout, QLabel,
    QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QKeyEvent, QAction

from viewer.core.config_loader import ConfigLoader
from viewer.core.layout_manager import LayoutManager
from viewer.core.stream_engine import StreamWidget
from viewer.models.camera_config import ViewerConfig


class ViewerWindow(QMainWindow):
    """Janela Principal do GPM CFTV Viewer."""
    
    def __init__(self):
        super().__init__()
        self.config: ViewerConfig = None
        self.stream_widgets = []
        self.fullscreen_widget = None
        self.is_fullscreen = False
        self.load_config()
        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()
    
    def load_config(self):
        """Carrega configuração das câmeras."""
        print("=" * 60)
        print("🎥 GPM CFTV Viewer v1.0.0")
        print("📅 Iniciando...")
        print("=" * 60)
        
        self.config = ConfigLoader.load()
        
        if not self.config.cameras:
            print("⚠️ Nenhuma câmera configurada!")
    
    def setup_ui(self):
        """Configura a interface."""
        self.setWindowTitle(self.config.window_title if self.config else "GPM CFTV Viewer")
        self.setMinimumSize(QSize(800, 600))
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Área do grid
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.grid_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Criar widgets para cada câmera
        self.create_camera_widgets()
        
        # Timer para atualizar layout (redimensionamento)
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.update_layout)
        
        self.apply_styles()
    
    def apply_styles(self):
        """Aplica tema escuro."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #11111b;
            }
            QStatusBar {
                background-color: #1e1e2e;
                color: #a6adc8;
                border-top: 2px solid #313244;
                font-size: 12px;
                padding: 4px;
            }
            QMenuBar {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border-bottom: 1px solid #313244;
                padding: 2px;
            }
            QMenuBar::item {
                padding: 4px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #45475a;
            }
            QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 30px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #45475a;
            }
        """)
    
    def setup_menu(self):
        """Configura menu superior."""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("📁 &Arquivo")
        
        reload_action = QAction("🔄 &Recarregar Configuração", self)
        reload_action.triggered.connect(self.reload_config)
        file_menu.addAction(reload_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("❌ &Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Visualizar
        view_menu = menubar.addMenu("👁️ &Visualizar")
        
        fullscreen_action = QAction("🖥️ &Tela Cheia (F11)", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        view_menu.addSeparator()
        
        reset_action = QAction("📐 &Voltar ao Grid", self)
        reset_action.setShortcut("Esc")
        reset_action.triggered.connect(self.reset_to_grid)
        view_menu.addAction(reset_action)
        
        # Menu Teste (remover na versão final)
        test_menu = menubar.addMenu("🧪 &Teste")
        
        disconnect_action = QAction("❌ Simular Queda (Aleatório)", self)
        disconnect_action.triggered.connect(self.simulate_random_disconnect)
        test_menu.addAction(disconnect_action)
        
        disconnect_all_action = QAction("❌ Simular Queda (Todas)", self)
        disconnect_all_action.triggered.connect(self.simulate_all_disconnect)
        test_menu.addAction(disconnect_all_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("❓ &Ajuda")
        
        about_action = QAction("ℹ️ &Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_shortcuts(self):
        """Configura atalhos de teclado."""
        pass  # F11 e Esc tratados no keyPressEvent
    
    def create_camera_widgets(self):
        """Cria widgets para cada câmera."""
        for w in self.stream_widgets:
            w.stop_stream()
            w.setParent(None)
        self.stream_widgets.clear()
        
        if not self.config or not self.config.cameras:
            no_cameras = QLabel(
                "📷 Nenhuma câmera configurada\n\n"
                "Use o GPM CFTV Studio para configurar as câmeras\n"
                "e gerar o arquivo cameras.json"
            )
            no_cameras.setAlignment(Qt.AlignCenter)
            no_cameras.setFont(QFont("Segoe UI", 14))
            no_cameras.setStyleSheet("color: #a6adc8; background: transparent;")
            self.grid_layout.addWidget(no_cameras, 0, 0)
            self.status_bar.showMessage("⚠️ Nenhuma câmera")
            return
        
        for camera in self.config.cameras:
            widget = StreamWidget(camera)
            widget.setMouseTracking(True)
            widget.mouseDoubleClickEvent = lambda e, w=widget: self.on_camera_double_click(w)
            self.stream_widgets.append(widget)
        
        self.update_layout()
        self.update_status()
    
    def reload_config(self):
        """Recarrega arquivo de configuração."""
        self.config = ConfigLoader.load()
        self.setWindowTitle(self.config.window_title)
        self.create_camera_widgets()
        self.status_bar.showMessage("✅ Configuração recarregada")
    
    def update_layout(self):
        """Atualiza o layout do grid."""
        if self.fullscreen_widget:
            return
        
        num_cameras = len(self.stream_widgets)
        
        if num_cameras == 0:
            return
        
        cols, rows = LayoutManager.calculate_grid(num_cameras)
        
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        
        for i, widget in enumerate(self.stream_widgets):
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(widget, row, col)
        
        layout_name = LayoutManager.get_layout_name(num_cameras)
        print(f"📐 Layout: {layout_name} ({num_cameras} câmeras)")
    
    def update_status(self):
        """Atualiza barra de status."""
        if self.config:
            num = len(self.config.cameras)
            layout = LayoutManager.get_layout_name(num)
            
            # Contar status
            connected = sum(1 for w in self.stream_widgets if w.state == StreamWidget.STATE_CONNECTED)
            
            self.status_bar.showMessage(
                f"📷 {num} câmera(s) | 🟢 {connected} online | "
                f"📐 Layout: {layout} | "
                f"F11: Tela Cheia | Duplo Clique: Ampliar"
            )
            
            # Atualizar status a cada 2 segundos
            QTimer.singleShot(2000, self.update_status)
    
    def on_camera_double_click(self, widget: StreamWidget):
        """Expande/recolhe câmera com duplo clique."""
        if self.fullscreen_widget == widget:
            self.reset_to_grid()
        else:
            self.fullscreen_widget = widget
            
            for i in reversed(range(self.grid_layout.count())):
                item = self.grid_layout.itemAt(i)
                if item.widget():
                    item.widget().setParent(None)
            
            self.grid_layout.addWidget(widget, 0, 0)
            self.status_bar.showMessage(f"🔍 Câmera {widget.camera.id} ampliada | ESC para voltar")
    
    def reset_to_grid(self):
        """Volta ao layout de grid."""
        if self.fullscreen_widget:
            self.fullscreen_widget = None
            self.update_layout()
            self.status_bar.showMessage("📐 Modo Grid")
    
    def keyPressEvent(self, event: QKeyEvent):
        """Gerencia eventos de teclado."""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape:
            if self.is_fullscreen:
                self.toggle_fullscreen()
            elif self.fullscreen_widget:
                self.reset_to_grid()
        else:
            super().keyPressEvent(event)
    
    def toggle_fullscreen(self):
        """Alterna tela cheia."""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
            self.status_bar.showMessage("📐 Modo Normal")
        else:
            self.showFullScreen()
            self.is_fullscreen = True
            self.status_bar.showMessage("🖥️ Tela Cheia | F11 para sair")
    
    def simulate_random_disconnect(self):
        """Simula queda em câmera aleatória (para teste)."""
        if self.stream_widgets:
            widget = random.choice(self.stream_widgets)
            widget.simulate_disconnect()
            self.status_bar.showMessage(f"🧪 Simulando queda: {widget.camera.ip}")
    
    def simulate_all_disconnect(self):
        """Simula queda em todas as câmeras (para teste)."""
        for widget in self.stream_widgets:
            widget.simulate_disconnect()
        self.status_bar.showMessage("🧪 Simulando queda em todas as câmeras")
    
    def show_about(self):
        """Mostra diálogo Sobre."""
        QMessageBox.about(
            self,
            "Sobre - GPM CFTV Viewer",
            "<h2>🎥 GPM CFTV Viewer v1.0.0</h2>"
            "<p><b>Sistema de Monitoramento CFTV</b></p>"
            "<p>Desenvolvido por: <b>Rafael</b></p>"
            "<p>Equipe: <b>GPM Manutenção</b></p>"
            "<p>Empresa: <b>Armazém Paraíba</b></p>"
            "<hr>"
            "<p>✅ Reconexão automática</p>"
            "<p>📐 Layout automático</p>"
            "<p>🖥️ Tela cheia (F11)</p>"
            "<p>🔍 Ampliar câmera (Duplo clique)</p>"
        )
    
    def resizeEvent(self, event):
        """Redimensiona e atualiza layout."""
        super().resizeEvent(event)
        self.resize_timer.start(300)
    
    def closeEvent(self, event):
        """Para streams ao fechar."""
        print("🛑 Parando streams...")
        for widget in self.stream_widgets:
            widget.stop_stream()
        print("👋 GPM CFTV Viewer encerrado.")
        event.accept()


def main():
    """Função principal."""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("GPM CFTV Viewer")
        app.setOrganizationName("GPM Manutenção")
        
        window = ViewerWindow()
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()