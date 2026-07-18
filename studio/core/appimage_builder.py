"""
GPM CFTV Studio - Gerador de AppImage
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List
from studio.models.camera import Camera


class AppImageBuilder:
    """
    Gera o pacote completo do Viewer com instalador automático.
    """
    
    def __init__(self, cameras: List[Camera], output_dir: str = None):
        self.cameras = cameras
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "dist"
        self.build_dir = self.output_dir / "appimage_build"
        self.app_name = "GPM_CFTV_Viewer"
    
    def generate(self) -> str:
        """
        Gera o pacote completo com instalador.
        """
        print("=" * 60)
        print(">>> GERANDO PACOTE DE INSTALACAO")
        print("=" * 60)
        print(f"    Cameras: {len(self.cameras)}")
        print(f"    Destino: {self.output_dir}")
        
        self._create_structure()
        self._generate_embedded_config()
        self._create_standalone_viewer()
        self._create_build_script()
        self._create_installer_script()
        self._create_instructions()
        zip_path = self._export_zip()
        
        print(f"\n{'='*60}")
        print(f"PACOTE GERADO COM SUCESSO!")
        print(f"{'='*60}")
        print(f"Arquivo: {zip_path}")
        print(f"")
        print(f"PROXIMOS PASSOS (no Linux):")
        print(f"1. Extraia o ZIP no computador Linux")
        print(f"2. Execute: ./instalar.sh")
        print(f"3. Digite a senha 1 vez")
        print(f"4. Pronto! Icone na Area de Trabalho!")
        
        return str(self.build_dir)
    
    def _create_structure(self):
        """Cria estrutura de diretórios."""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        self.build_dir.mkdir(parents=True)
        (self.build_dir / "src").mkdir()
        print("    Estrutura criada")
    
    def _generate_embedded_config(self):
        """Gera config no formato Python (True/False/None)."""
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
            f.write('EMBEDDED_CONFIG = ')
            f.write(repr(config))
        
        print(f"    Configuracao embutida: {len(self.cameras)} cameras")
    
    def _create_standalone_viewer(self):
        """Cria Viewer standalone com config embutida."""
        viewer_code = '''#!/usr/bin/env python3
"""
GPM CFTV Viewer - Versao Final
Empresa: Armazem Paraiba
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
        """Cria script de build para Linux."""
        script = '''#!/bin/bash
# ==========================================
# BUILD - GPM CFTV Viewer
# ==========================================

echo "=================================="
echo "GPM CFTV Viewer - Gerando executavel"
echo "=================================="

if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python3 nao encontrado"
    echo "Instale: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[1/3] Instalando dependencias..."
sudo apt update -qq
sudo apt install -y -qq libxcb-cursor0 python3-pip
pip3 install --quiet PySide6 pyinstaller

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
    src/viewer_app.py 2>&1 | grep -E "(complete|ERRO)"

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
        Cria script instalador automatico que:
        1. Gera o executavel se necessario
        2. Instala em todos os usuarios
        3. Funciona com Desktop ou Area de Trabalho
        """
        script = '''#!/bin/bash
# ================================================
# INSTALADOR COMPLETO - GPM CFTV Viewer
# Armazem Paraiba - GPM Manutencao
# Faz TUDO automaticamente!
# ================================================

clear
echo ""
echo "========================================="
echo "  GPM CFTV Viewer - Instalador Completo"
echo "  Armazem Paraiba"
echo "========================================="
echo ""

# Obter a pasta onde este script esta
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ==========================================
# ETAPA 1: Gerar executavel
# ==========================================
echo "[ETAPA 1/3] Gerando executavel..."

if [ ! -f "dist/GPM_CFTV_Viewer" ]; then
    echo "  Executavel nao encontrado. Gerando..."
    
    # Verificar Python
    if ! command -v python3 &> /dev/null; then
        echo "  Instalando Python..."
        sudo apt-get update -qq
        sudo apt-get install -y -qq python3 python3-pip
    fi
    
    # Instalar PyInstaller
    echo "  Instalando PyInstaller..."
    pip3 install --quiet pyinstaller PySide6 2>/dev/null
    
    # Corrigir formato do script se necessario
    sed -i 's/\\r$//' build_appimage.sh 2>/dev/null
    
    # Gerar executavel
    echo "  Compilando... (pode demorar 2-3 minutos)"
    python3 -m PyInstaller \\
        --onefile \\
        --windowed \\
        --name="GPM_CFTV_Viewer" \\
        --add-data="src/embedded_config.py:src" \\
        --hidden-import=PySide6 \\
        --collect-all PySide6 \\
        --clean \\
        --noconfirm \\
        src/viewer_app.py 2>&1 | grep -E "(INFO|ERROR|complete)"
    
    if [ ! -f "dist/GPM_CFTV_Viewer" ]; then
        echo ""
        echo "[ERRO] Falha ao gerar executavel!"
        echo "Tente executar manualmente: ./build_appimage.sh"
        exit 1
    fi
    
    echo "  Executavel gerado com sucesso!"
else
    echo "  Executavel ja existe. Pulando geracao."
fi

# ==========================================
# ETAPA 2: Instalar no sistema
# ==========================================
echo ""
echo "[ETAPA 2/3] Instalando no sistema..."

# Pedir senha uma unica vez
if [ "$EUID" -ne 0 ]; then
    echo "  Precisamos de permissoes de administrador."
    echo "  Digite a senha do computador:"
    echo ""
    exec sudo "$0"
fi

# Instalar biblioteca grafica
echo "  Instalando dependencias..."
apt-get update -qq 2>/dev/null
apt-get install -y -qq libxcb-cursor0 2>/dev/null

# Copiar para pasta do sistema
echo "  Instalando programa..."
mkdir -p /opt/gpm-cftv-viewer
cp "$SCRIPT_DIR/dist/GPM_CFTV_Viewer" /opt/gpm-cftv-viewer/
chmod +x /opt/gpm-cftv-viewer/GPM_CFTV_Viewer

# ==========================================
# ETAPA 3: Criar atalhos
# ==========================================
echo ""
echo "[ETAPA 3/3] Criando atalhos..."

# Para cada usuario no sistema
for user_home in /home/*; do
    if [ -d "$user_home" ]; then
        username=$(basename "$user_home")
        
        # Detectar pasta Desktop (portugues ou ingles)
        desktop=""
        [ -d "$user_home/Desktop" ] && desktop="$user_home/Desktop"
        [ -d "$user_home/Área de Trabalho" ] && desktop="$user_home/Área de Trabalho"
        [ -d "$user_home/Área de trabalho" ] && desktop="$user_home/Área de trabalho"
        
        if [ -n "$desktop" ]; then
            cp /opt/gpm-cftv-viewer/GPM_CFTV_Viewer "$desktop/"
            chmod +x "$desktop/GPM_CFTV_Viewer"
            chown "$username:$username" "$desktop/GPM_CFTV_Viewer" 2>/dev/null
            echo "  Icone criado em: $desktop"
        fi
    fi
done

# Criar atalho no menu do sistema
cat > /usr/share/applications/gpm-cftv-viewer.desktop << 'EOF'
[Desktop Entry]
Name=GPM CFTV Viewer
Name[pt_BR]=GPM CFTV Viewer
Comment=Sistema de Monitoramento CFTV
Comment[pt_BR]=Sistema de Monitoramento CFTV - Armazem Paraiba
Exec=/opt/gpm-cftv-viewer/GPM_CFTV_Viewer
Icon=video-display
Terminal=false
Type=Application
Categories=System;Video;
StartupNotify=true
EOF

echo "  Atalho no menu criado!"

# ==========================================
# CONCLUSAO
# ==========================================
echo ""
echo "========================================="
echo "  INSTALACAO CONCLUIDA COM SUCESSO!"
echo "========================================="
echo ""
echo "O GPM CFTV Viewer esta pronto para usar!"
echo ""
echo "COMO ABRIR:"
echo "  - Duplo clique no icone da Area de Trabalho"
echo "  - Ou procure no menu: GPM CFTV Viewer"
echo ""
echo "ATALHOS:"
echo "  F11         - Tela cheia"
echo "  Duplo clique - Ampliar camera"
echo "  ESC         - Voltar ao normal"
echo ""
echo "========================================="
echo ""

# Perguntar se quer abrir agora
read -p "Deseja abrir o Viewer agora? (s/N): " resposta
if [ "$resposta" = "s" ] || [ "$resposta" = "S" ]; then
    echo "Abrindo..."
    /opt/gpm-cftv-viewer/GPM_CFTV_Viewer &
fi
'''
        
        script_path = self.build_dir / "instalar.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        
        print("    Script instalador completo criado")
    
    def _create_instructions(self):
        """Cria arquivo de instrucoes."""
        data_atual = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        instrucoes = f"""========================================
GPM CFTV Viewer - INSTRUCOES
========================================

GERADO EM: {data_atual}
CAMERAS CONFIGURADAS: {len(self.cameras)}

----------------------------------------
PARA INSTALAR (FAZ TUDO SOZINHO)
----------------------------------------

1. Abra o terminal na pasta extraida
2. Execute:
   chmod +x instalar.sh
   ./instalar.sh
3. Digite a senha do computador (1 vez)
4. Pronto! Icone na Area de Trabalho!

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
        """Exporta tudo como ZIP."""
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