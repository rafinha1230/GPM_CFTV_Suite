"""
GPM CFTV Studio - Criador do Instalador Linux
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import os
from pathlib import Path
from datetime import datetime


class InstallerCreator:
    """
    Cria um script instalador que:
    1. Instala dependências automaticamente (pede senha 1 vez)
    2. Copia o Viewer para o Desktop
    3. Cria atalho no menu
    """
    
    @staticmethod
    def create_installer_script(output_dir: str) -> str:
        """
        Cria o script instalador para Linux.
        
        Args:
            output_dir: Diretório de saída.
            
        Returns:
            Caminho do script gerado.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        script = """#!/bin/bash
# ================================================
# INSTALADOR - GPM CFTV Viewer
# Armazem Paraiba - GPM Manutencao
# ================================================
# Este script instala TUDO automaticamente.
# So pede a senha UMA vez.
# ================================================

echo ""
echo "========================================="
echo "  GPM CFTV Viewer - Instalador"
echo "  Armazem Paraiba"
echo "========================================="
echo ""

# Verificar se esta rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "[1/4] Precisamos de permissoes de administrador..."
    echo "      Digite a senha do computador:"
    sudo "$0"
    exit $?
fi

echo "[1/4] Instalando dependencias..."
apt-get update -qq
apt-get install -y -qq libxcb-cursor0 python3 python3-pip 2>/dev/null

echo "[2/4] Instalando bibliotecas Python..."
pip3 install --quiet PySide6 2>/dev/null

echo "[3/4] Instalando GPM CFTV Viewer..."
# Copiar para /opt (pasta de programas)
mkdir -p /opt/gpm-cftv-viewer
cp "$(dirname "$0")/GPM_CFTV_Viewer" /opt/gpm-cftv-viewer/
chmod +x /opt/gpm-cftv-viewer/GPM_CFTV_Viewer

# Criar atalho no Desktop do usuario
for user_home in /home/*; do
    if [ -d "$user_home" ]; then
        desktop_dir="$user_home/Desktop"
        if [ ! -d "$desktop_dir" ]; then
            desktop_dir="$user_home/Área de Trabalho"
        fi
        
        if [ -d "$desktop_dir" ]; then
            cp /opt/gpm-cftv-viewer/GPM_CFTV_Viewer "$desktop_dir/"
            chmod +x "$desktop_dir/GPM_CFTV_Viewer"
            chown $(stat -c '%U' "$user_home"):$(stat -c '%G' "$user_home") "$desktop_dir/GPM_CFTV_Viewer"
        fi
    fi
done

echo "[4/4] Criando atalho no menu..."
# Criar arquivo .desktop
cat > /usr/share/applications/gpm-cftv-viewer.desktop << 'DESKTOP'
[Desktop Entry]
Name=GPM CFTV Viewer
Comment=Sistema de Monitoramento CFTV
Comment[pt_BR]=Sistema de Monitoramento CFTV
Exec=/opt/gpm-cftv-viewer/GPM_CFTV_Viewer
Icon=video-display
Terminal=false
Type=Application
Categories=System;Video;
StartupNotify=true
DESKTOP

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

# Tentar abrir o Viewer automaticamente
echo "Abrindo o Viewer..."
sudo -u $(logname) /opt/gpm-cftv-viewer/GPM_CFTV_Viewer &
"""
        
        script_path = output_path / "instalar.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script)
        os.chmod(script_path, 0o755)
        
        return str(script_path)
    
    @staticmethod
    def create_readme_instrucoes(output_dir: str, num_cameras: int) -> str:
        """
        Cria arquivo com instruções para o Rafael.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        readme = """========================================
GPM CFTV Viewer - INSTRUCOES DE INSTALACAO
========================================

PARA INSTALAR NO COMPUTADOR DO USUARIO:

[OPCAO 1 - INSTALADOR AUTOMATICO] (Recomendado)

1. Copie a pasta inteira para o computador Linux
2. Abra o terminal na pasta
3. Execute:
   chmod +x instalar.sh
   ./instalar.sh
4. Digite a senha do computador (1 vez)
5. Pronto! O Viewer abre automaticamente!


[OPCAO 2 - MANUAL]

Se o instalador falhar, execute manualmente:

1. Instalar dependencias (1 vez):
   sudo apt update
   sudo apt install -y libxcb-cursor0 python3 python3-pip
   pip3 install PySide6

2. Copiar o Viewer:
   cp GPM_CFTV_Viewer ~/Desktop/

3. Executar:
   Duplo clique no Desktop


[OPCAO 3 - PORTATIL]

Basta copiar o arquivo GPM_CFTV_Viewer
para o Desktop do usuario e executar.

(Se nao abrir, execute a Opcao 2 primeiro)


========================================
GERADO POR: GPM CFTV Studio
DATA: {data}
CAMERAS CONFIGURADAS: {cameras}
========================================
""".format(
            data=datetime.now().strftime('%d/%m/%Y %H:%M'),
            cameras=num_cameras
        )
        
        readme_path = output_path / "LEIA_ANTES_DE_INSTALAR.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        
        return str(readme_path)