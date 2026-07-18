"""
GPM CFTV Studio - Gerador de AppImage
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import os
import json
import shutil
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List
from studio.models.camera import Camera


class AppImageBuilder:
    """
    Gera um AppImage pronto para uso no Linux.
    Inclui instalador automático.
    """
    
    def __init__(self, cameras: List[Camera], output_dir: str = None):
        self.cameras = cameras
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "dist"
        self.build_dir = self.output_dir / "appimage_build"
        self.app_name = "GPM_CFTV_Viewer"
    
    def generate(self) -> str:
        """
        Gera o pacote completo com instalador.
        
        Returns:
            Caminho do diretório de build.
        """
        print("=" * 60)
        print(">>> GERANDO PACOTE DE INSTALACAO")
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
        
        # 5. Criar instalador automático
        self._create_installer_script()
        
        # 6. Criar instruções
        self._create_instructions()
        
        # 7. Exportar ZIP
        zip_path = self._export_zip()
        
        print(f"\n{'='*60}")
        print(f"PACOTE GERADO COM SUCESSO!")
        print(f"{'='*60}")
        print(f"Arquivo: {zip_path}")
        print(f"")
        print(f"PROXIMOS PASSOS (no Linux):")
        print(f"1. Extraia o ZIP no computador Linux")
        print(f"2. Execute: chmod +x build_appimage.sh")
        print(f"3. Execute: ./build_appimage.sh")
        print(f"4. Execute: ./instalar.sh")
        print(f"")
        print(f"O usuario so precisa do arquivo final!")
        
        return str(self.build_dir)
    
    def _create_structure(self):
        """Cria estrutura de diretórios."""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        self.build_dir.mkdir(parents=True)
        (self.build_dir / "src").mkdir()
        
        print("    Estrutura criada")
    
    def _generate_embedded_config(self):
        """
        Gera configuração embutida no código Python.
        Usa formato Python (True/False/None) em vez de JSON.
        """
        config = {
            "version": "1.0.0",
            "viewer_settings": {
                "window_title": "GPM CFTV Viewer",
                "fullscreen_on_start": False,
                "keep_aspect_ratio": True
            },
            "cameras": []
        }
        
        for cam in self.cameras:
            config["cameras"].append({
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
            f.write('# Formato Python (True/False/None)\n')
            f.write('EMBEDDED_CONFIG = ')
            # Usar repr() para garantir formato Python
            f.write(repr(config))
        
        print(f"    Configuracao embutida: {len(self.cameras)} cameras")
    
    def _create_standalone_viewer(self):
        """
        Cria versao standalone do Viewer com config embutida.
        """
        viewer_code = '''#!/usr/bin/env python3
"""
GPM CFTV Viewer - Versao Final
Carrega cameras diretamente (sem arquivo externo)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from src.embedded_config import EMBEDDED_CONFIG

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout,
    QVBoxLayout, QLabel, QStatusBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QKeyEvent


class AppImageViewer(QMainWindow):
    """Viewer standalone final."""
    
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
            widget.setStyleSheet(
                "background-color: #11111b; "
                "border: 2px solid #45475a; "
                "border-radius: 5px;"
            )
            w_layout = QVBoxLayout(widget)
            
            info = QLabel(
                f"Camera {cam['id']}\\n\\n"
                f"IP: {cam['ip']}:{cam['port']}\\n"
                f"Perfil: {cam['rtsp_path']}\\n\\n"
                f"[CONECTADO]"
            )
            info.setAlignment(Qt.AlignCenter)
            info.setStyleSheet(
                "color: #a6adc8; "
                "font-size: 12px; "
                "border: none;"
            )
            w_layout.addWidget(info)
            
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(widget, row, col)
        
        self.status_bar.showMessage(
            f"Cameras: {n} | Layout: {cols}x{math.ceil(n/cols)} | "
            f"F11: Tela Cheia | Duplo Clique: Ampliar"
        )
    
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
        Cria script para gerar o executavel no Linux.
        """
        script = '''#!/bin/bash
# ==========================================
# BUILD - GPM CFTV Viewer
# Gera o executavel final
# ==========================================

echo "=================================="
echo "GPM CFTV Viewer - Gerando executavel"
echo "=================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python3 nao encontrado"
    echo "Instale: sudo apt install python3 python3-pip"
    exit 1
fi

# Instalar dependencias
echo "[1/3] Instalando dependencias..."
sudo apt update -qq
sudo apt install -y -qq libxcb-cursor0 python3-pip
pip3 install --quiet PySide6 pyinstaller

# Gerar executavel
echo "[2/3] Gerando executavel..."
cd "$(dirname "$0")"
python3 -m PyInstaller \\
    --onefile \\
    --windowed \\
    --name="GPM_CFTV_Viewer" \\
    --add-data="src/embedded_config.py:src" \\
    --hidden-import=PySide6 \\
    --collect-all PySide6 \\
    --clean \\
    --noconfirm \\
    src/viewer_app.py

if [ ! -f "dist/GPM_CFTV_Viewer" ]; then
    echo "[ERRO] Falha ao gerar executavel"
    exit 1
fi

echo "[3/3] Executavel gerado com sucesso!"
echo ""
echo "Arquivo: $(pwd)/dist/GPM_CFTV_Viewer"
echo ""
echo "Agora execute: ./instalar.sh"
'''
        
        script_path = self.build_dir / "build_appimage.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        
        print("    Script de build criado")
    
    def _create_installer_script(self):
        """
        Cria script instalador automatico.
        """
        script = '''#!/bin/bash
# ================================================
# INSTALADOR - GPM CFTV Viewer
# Armazem Paraiba - GPM Manutencao
# ================================================

echo ""
echo "========================================="
echo "  GPM CFTV Viewer - Instalador"
echo "  Armazem Paraiba"
echo "========================================="
echo ""

# Verificar se esta rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "Precisamos de permissoes de administrador."
    echo "Digite a senha do computador:"
    echo ""
    sudo "$0"
    exit $?
fi

echo "[1/3] Instalando dependencias do sistema..."
apt-get update -qq
apt-get install -y -qq libxcb-cursor0 python3 2>/dev/null

echo "[2/3] Instalando GPM CFTV Viewer..."
mkdir -p /opt/gpm-cftv-viewer
cp "$(dirname "$0")/dist/GPM_CFTV_Viewer" /opt/gpm-cftv-viewer/ 2>/dev/null
chmod +x /opt/gpm-cftv-viewer/GPM_CFTV_Viewer 2>/dev/null

# Copiar para Desktop de todos os usuarios
for user_home in /home/*; do
    if [ -d "$user_home" ]; then
        username=$(basename "$user_home")
        
        # Desktop
        desktop="$user_home/Desktop"
        [ ! -d "$desktop" ] && desktop="$user_home/Área de Trabalho"
        
        if [ -d "$desktop" ]; then
            cp /opt/gpm-cftv-viewer/GPM_CFTV_Viewer "$desktop/" 2>/dev/null
            chmod +x "$desktop/GPM_CFTV_Viewer" 2>/dev/null
            chown "$username:$username" "$desktop/GPM_CFTV_Viewer" 2>/dev/null
            echo "  Instalado para usuario: $username"
        fi
    fi
done

# Criar atalho no menu
echo "[3/3] Criando atalho no menu..."
cat > /usr/share/applications/gpm-cftv-viewer.desktop << 'EOF'
[Desktop Entry]
Name=GPM CFTV Viewer
Name[pt_BR]=GPM CFTV Viewer
Comment=Sistema de Monitoramento CFTV
Comment[pt_BR]=Sistema de Monitoramento CFTV
Exec=/opt/gpm-cftv-viewer/GPM_CFTV_Viewer
Icon=video-display
Terminal=false
Type=Application
Categories=System;Video;
StartupNotify=true
EOF

echo ""
echo "========================================="
echo "  INSTALACAO CONCLUIDA!"
echo "========================================="
echo ""
echo "O GPM CFTV Viewer esta instalado!"
echo ""
echo "Para abrir:"
echo "  - Duplo clique no icone do Desktop"
echo "  - Ou procure no menu: GPM CFTV Viewer"
echo ""
echo "========================================="
'''
        
        script_path = self.build_dir / "instalar.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        
        print("    Script instalador criado")
    
    def _create_instructions(self):
        """
        Cria arquivo de instrucoes.
        """
        data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        instrucoes = f"""========================================
GPM CFTV Viewer - INSTRUCOES
========================================

GERADO EM: {data_atual}
CAMERAS CONFIGURADAS: {len(self.cameras)}

----------------------------------------
PARA INSTALAR NO COMPUTADOR DO USUARIO
----------------------------------------

[PASSO 1] Gerar o executavel (1 vez)
  chmod +x build_appimage.sh
  ./build_appimage.sh

[PASSO 2] Instalar no sistema (1 vez)
  chmod +x instalar.sh
  ./instalar.sh
  (Digite a senha do computador quando pedir)

[PASSO 3] Usar
  Duplo clique no icone do Desktop
  OU procure no menu: GPM CFTV Viewer

----------------------------------------
ATALHOS DO VIEWER
----------------------------------------
  F11         - Tela cheia
  ESC         - Sair da tela cheia
  Duplo clique - Ampliar camera
  Ctrl+Q      - Fechar

----------------------------------------
SUPORTE
----------------------------------------
GPM Manutencao - Armazem Paraiba
"""
        
        readme_path = self.build_dir / "LEIA_ANTES_DE_INSTALAR.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(instrucoes)
        
        print("    Instrucoes criadas")
    
    def _export_zip(self) -> str:
        """
        Exporta tudo como ZIP.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_name = f"GPM_CFTV_Viewer_Instalador_{timestamp}.zip"
        zip_path = self.output_dir / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.build_dir):
                for file in files:
                    if file.endswith(('.sh', '.txt', '.py')):
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(self.build_dir)
                        zf.write(file_path, arcname)
        
        print(f"    ZIP exportado: {zip_path}")
        return str(zip_path)


def export_build_zip(build_dir: str) -> str:
    """Exporta o build como ZIP."""
    build_path = Path(build_dir)
    zip_path = build_path.parent / f"GPM_CFTV_AppImage_Build.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(build_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(build_path)
                zf.write(file_path, arcname)
    
    return str(zip_path)