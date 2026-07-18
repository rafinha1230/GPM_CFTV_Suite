#!/usr/bin/env python3
"""
GPM CFTV Viewer - Visualizador de Câmeras IP
Versão: 1.0.0
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QGridLayout, QVBoxLayout, QLabel,
    QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QKeyEvent

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
        """)
    
    def create_camera_widgets(self):
        """Cria widgets para cada câmera."""
        # Limpar widgets existentes
        for w in self.stream_widgets:
            w.setParent(None)
        self.stream_widgets.clear()
        
        if not self.config or not self.config.cameras:
            # Mostrar mensagem se não houver câmeras
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
        
        # Criar stream widget para cada câmera
        for camera in self.config.cameras:
            widget = StreamWidget(camera)
            widget.setMouseTracking(True)
            widget.mouseDoubleClickEvent = lambda e, w=widget: self.on_camera_double_click(w)
            self.stream_widgets.append(widget)
        
        self.update_layout()
        self.update_status()
    
    def update_layout(self):
        """Atualiza o layout do grid."""
        num_cameras = len(self.stream_widgets)
        
        if num_cameras == 0:
            return
        
        cols, rows = LayoutManager.calculate_grid(num_cameras)
        
        # Limpar grid
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
        
        # Adicionar widgets ao grid
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
            self.status_bar.showMessage(
                f"📷 {num} câmera(s) | 📐 Layout: {layout} | "
                f"F11: Tela Cheia | Duplo Clique: Ampliar"
            )
    
    def on_camera_double_click(self, widget: StreamWidget):
        """Expande/recolhe câmera com duplo clique."""
        if self.fullscreen_widget == widget:
            # Voltar ao grid
            self.fullscreen_widget = None
            self.update_layout()
            self.status_bar.showMessage("📐 Modo Grid")
        else:
            # Expandir câmera
            self.fullscreen_widget = widget
            
            # Limpar grid
            for i in reversed(range(self.grid_layout.count())):
                item = self.grid_layout.itemAt(i)
                if item.widget():
                    item.widget().setParent(None)
            
            # Mostrar apenas esta câmera
            self.grid_layout.addWidget(widget, 0, 0)
            self.status_bar.showMessage(f"🔍 Câmera {widget.camera.id} ampliada")
    
    def setup_shortcuts(self):
        """Configura atalhos de teclado."""
        # F11 - Tela cheia será tratado no keyPressEvent
    
    def keyPressEvent(self, event: QKeyEvent):
        """Gerencia eventos de teclado."""
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape:
            if self.is_fullscreen:
                self.toggle_fullscreen()
            elif self.fullscreen_widget:
                self.fullscreen_widget = None
                self.update_layout()
                self.status_bar.showMessage("📐 Modo Grid")
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
            self.status_bar.showMessage("🖥️ Tela Cheia")
    
    def resizeEvent(self, event):
        """Redimensiona e atualiza layout."""
        super().resizeEvent(event)
        self.resize_timer.start(300)  # Debounce 300ms
    
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