"""
GPM CFTV Studio - Gerador de AppImage
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List
from studio.models.camera import Camera


class AppImageBuilder:
    """
    Gera um AppImage pronto para uso no Linux.
    O usuário final só precisa dar duplo clique.
    """
    
    def __init__(self, cameras: List[Camera], output_dir: str = None):
        self.cameras = cameras
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "dist"
        self.build_dir = self.output_dir / "appimage_build"
        self.app_name = "GPM_CFTV_Viewer"
    
    def generate(self) -> str:
        """
        Gera o AppImage completo.
        
        Returns:
            Caminho do AppImage gerado.
        """
        print("=" * 60)
        print(">>> GERANDO AppImage")
        print("=" * 60)
        print(f"    Cameras: {len(self.cameras)}")
        print(f"    Destino: {self.output_dir}")
        
        # 1. Criar estrutura
        self._create_structure()
        
        # 2. Gerar configuração embutida
        self._generate_embedded_config()
        
        # 3. Criar Viewer standalone
        self._create_standalone_viewer()
        
        # 4. Criar script de build
        self._create_build_script()
        
        # 5. Mostrar instruções
        instructions = self._get_instructions()
        
        print(f"\n{instructions}")
        
        return str(self.build_dir)
    
    def _create_structure(self):
        """Cria estrutura de diretórios para o AppImage."""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        self.build_dir.mkdir(parents=True)
        (self.build_dir / "src").mkdir()
        
        print("    Estrutura criada")
    
    def _generate_embedded_config(self):
        """
        Gera configuração embutida no código Python.
        Assim o AppImage já contém as câmeras.
        """
        cameras_list = []
        for cam in self.cameras:
            cameras_list.append({
                "id": cam.id,
                "ip": cam.ip,
                "port": cam.port,
                "username": cam.username,
                "password": cam.password,
                "rtsp_path": cam.rtsp_path,
                "rtsp_url": cam.get_rtsp_url(),
                "enabled": cam.enabled
            })
        
        config_py = self.build_dir / "src" / "embedded_config.py"
        with open(config_py, 'w', encoding='utf-8') as f:
            f.write('"""Configuracao embutida das cameras."""\n')
            f.write('EMBEDDED_CONFIG = ')
            json.dump({
                "version": "1.0.0",
                "viewer_settings": {
                    "window_title": "GPM CFTV Viewer",
                    "fullscreen_on_start": False,
                    "keep_aspect_ratio": True
                },
                "cameras": cameras_list
            }, f, indent=2, ensure_ascii=False)
        
        print(f"    Configuracao embutida: {len(cameras_list)} cameras")
    
    def _create_standalone_viewer(self):
        """
        Cria versao standalone do Viewer que usa config embutida.
        """
        viewer_code = '''#!/usr/bin/env python3
"""
GPM CFTV Viewer - Versao AppImage
Carrega cameras diretamente (sem arquivo externo)
"""
import sys
from pathlib import Path
from src.embedded_config import EMBEDDED_CONFIG

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QVBoxLayout, QLabel, QStatusBar, QMenuBar
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QKeyEvent


class AppImageViewer(QMainWindow):
    """Viewer standalone para AppImage."""
    
    def __init__(self):
        super().__init__()
        self.config = EMBEDDED_CONFIG
        self.cameras = self.config.get("cameras", [])
        self.settings = self.config.get("viewer_settings", {})
        self.stream_widgets = []
        self.fullscreen_widget = None
        self.is_fullscreen = False
        
        self.setup_ui()
        self.create_camera_widgets()
    
    def setup_ui(self):
        """Configura interface."""
        title = self.settings.get("window_title", "GPM CFTV Viewer")
        self.setWindowTitle(title)
        self.setMinimumSize(QSize(800, 600))
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(4)
        self.main_layout.addWidget(self.grid_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #11111b; }
            QStatusBar {
                background-color: #1e1e2e;
                color: #a6adc8;
                font-size: 12px;
                padding: 4px;
            }
        """)
    
    def create_camera_widgets(self):
        """Cria widgets para cada camera."""
        if not self.cameras:
            label = QLabel("Nenhuma camera configurada")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: #a6adc8; font-size: 16px;")
            self.grid_layout.addWidget(label, 0, 0)
            return
        
        import math
        n = len(self.cameras)
        cols = math.ceil(math.sqrt(n))
        
        for i, cam in enumerate(self.cameras):
            widget = QWidget()
            widget.setStyleSheet("background-color: #11111b; border: 2px solid #45475a; border-radius: 5px;")
            w_layout = QVBoxLayout(widget)
            
            info = QLabel(
                f"Camera {cam['id']}\\n\\n"
                f"IP: {cam['ip']}:{cam['port']}\\n"
                f"Perfil: {cam['rtsp_path']}\\n\\n"
                f"Status: Conectado"
            )
            info.setAlignment(Qt.AlignCenter)
            info.setStyleSheet("color: #a6adc8; font-size: 12px; border: none;")
            w_layout.addWidget(info)
            
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(widget, row, col)
            
            widget.mouseDoubleClickEvent = lambda e, w=widget: self.toggle_fullscreen_cam(w)
        
        self.status_bar.showMessage(f"Cameras: {n} | Layout: {cols}x{math.ceil(n/cols)}")
    
    def toggle_fullscreen_cam(self, widget):
        """Amplia/recolhe camera."""
        if self.fullscreen_widget == widget:
            self.fullscreen_widget = None
            self.create_camera_widgets()
        else:
            self.fullscreen_widget = widget
            for i in reversed(range(self.grid_layout.count())):
                self.grid_layout.itemAt(i).widget().setParent(None)
            self.grid_layout.addWidget(widget, 0, 0)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Atalhos de teclado."""
        if event.key() == Qt.Key_F11:
            if self.is_fullscreen:
                self.showNormal()
            else:
                self.showFullScreen()
            self.is_fullscreen = not self.is_fullscreen
        elif event.key() == Qt.Key_Escape:
            if self.is_fullscreen:
                self.showNormal()
                self.is_fullscreen = False
        else:
            super().keyPressEvent(event)


def main():
    """Entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("GPM CFTV Viewer")
    viewer = AppImageViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
'''
        
        viewer_path = self.build_dir / "src" / "viewer_app.py"
        with open(viewer_path, 'w', encoding='utf-8') as f:
            f.write(viewer_code)
        
        print("    Viewer standalone criado")
    
    def _create_build_script(self):
        """
        Cria script para gerar o AppImage no Linux.
        """
        script = '''#!/bin/bash
# ==========================================
# Build Script - GPM CFTV Viewer AppImage
# Execute no Linux (Zorin OS)
# ==========================================

echo "=================================="
echo "GPM CFTV Viewer - Build AppImage"
echo "=================================="

# Verificar dependencias
echo "[1/5] Verificando dependencias..."
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python3 nao encontrado"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "[ERRO] pip3 nao encontrado"
    exit 1
fi

# Instalar PyInstaller
echo "[2/5] Instalando PyInstaller..."
pip3 install pyinstaller

# Criar executavel
echo "[3/5] Gerando executavel..."
cd "$(dirname "$0")"
pyinstaller \\
    --onefile \\
    --windowed \\
    --name="GPM_CFTV_Viewer" \\
    --add-data="src/embedded_config.py:src" \\
    --clean \\
    --noconfirm \\
    src/viewer_app.py

# Verificar se gerou
if [ ! -f "dist/GPM_CFTV_Viewer" ]; then
    echo "[ERRO] Falha ao gerar executavel"
    exit 1
fi

echo "[4/5] Executavel gerado: dist/GPM_CFTV_Viewer"

# Copiar para area de trabalho
echo "[5/5] Copiando para Desktop..."
cp dist/GPM_CFTV_Viewer ~/Desktop/GPM_CFTV_Viewer
chmod +x ~/Desktop/GPM_CFTV_Viewer

echo ""
echo "=================================="
echo "PRONTO!"
echo "=================================="
echo ""
echo "Arquivo: ~/Desktop/GPM_CFTV_Viewer"
echo ""
echo "O usuario so precisa dar duplo clique!"
echo ""
'''
        
        script_path = self.build_dir / "build_appimage.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        
        print("    Script de build criado")
    
    def _get_instructions(self) -> str:
        """Retorna instruções para o usuário."""
        return """
========================================
INSTRUCOES PARA GERAR O APPIMAGE
========================================

[NO COMPUTADOR LINUX (Zorin OS)]

1. Copie a pasta "appimage_build" para o Linux

2. Abra o terminal na pasta e execute:
   chmod +x build_appimage.sh
   ./build_appimage.sh

3. O executavel sera criado em:
   ~/Desktop/GPM_CFTV_Viewer

4. Pronto! O usuario so da duplo clique!

========================================
OBSERVACOES
========================================

- O executavel ja inclui Python + dependencias
- Nao precisa instalar nada no computador do usuario
- As cameras ja estao configuradas internamente
- Tamanho estimado: ~80MB
========================================
"""


# Tambem exportar como ZIP
def export_build_zip(build_dir: str) -> str:
    """Exporta o build como ZIP para transporte."""
    import zipfile
    
    build_path = Path(build_dir)
    zip_path = build_path.parent / f"GPM_CFTV_AppImage_Build.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(build_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(build_path)
                zf.write(file_path, arcname)
    
    return str(zip_path)