"""
GPM CFTV Studio - Gerador do Viewer
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import json
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List

from studio.models.camera import Camera


class ViewerGenerator:
    """
    Gera o pacote do GPM CFTV Viewer pronto para distribuição.
    """
    
    def __init__(self, cameras: List[Camera], output_dir: str = None):
        """
        Inicializa o gerador.
        
        Args:
            cameras: Lista de câmeras configuradas.
            output_dir: Diretório de saída (padrão: pasta dist/).
        """
        self.cameras = cameras
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "dist"
        self.build_dir = self.output_dir / "viewer_build"
    
    def generate(self) -> str:
        """
        Gera o pacote completo do Viewer.
        
        Returns:
            Caminho do arquivo gerado.
        """
        print(">>> Iniciando geracao do Viewer...")
        print(f"    Cameras configuradas: {len(self.cameras)}")
        
        # 1. Criar diretórios
        self._create_directories()
        
        # 2. Gerar cameras.json
        self._generate_config()
        
        # 3. Copiar arquivos do Viewer
        self._copy_viewer_files()
        
        # 4. Criar script de inicialização
        self._create_launcher()
        
        # 5. Criar README
        self._create_readme()
        
        # 6. Empacotar
        package_path = self._create_package()
        
        print(f">>> Viewer gerado com sucesso!")
        print(f"    Arquivo: {package_path}")
        
        return str(package_path)
    
    def _create_directories(self):
        """Cria estrutura de diretórios."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Limpar build anterior
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        self.build_dir.mkdir(parents=True)
        (self.build_dir / "viewer").mkdir()
        (self.build_dir / "config").mkdir()
        
        print(f"    Diretorios criados: {self.build_dir}")
    
    def _generate_config(self) -> Path:
        """
        Gera o arquivo cameras.json.
        
        Returns:
            Caminho do arquivo gerado.
        """
        config = {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "generated_by": "GPM CFTV Studio",
            "total_cameras": len(self.cameras),
            "viewer_settings": {
                "window_title": "GPM CFTV Viewer",
                "fullscreen_on_start": False,
                "keep_aspect_ratio": True,
                "auto_reconnect": True,
                "reconnect_interval": 5
            },
            "cameras": []
        }
        
        for camera in self.cameras:
            config["cameras"].append({
                "id": camera.id,
                "ip": camera.ip,
                "port": camera.port,
                "username": camera.username,
                "password": camera.password,
                "rtsp_profile": camera.rtsp_profile,
                "rtsp_path": camera.rtsp_path,
                "rtsp_url": camera.get_rtsp_url(),
                "enabled": camera.enabled
            })
        
        # Salvar no build
        config_path = self.build_dir / "config" / "cameras.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        # Também salvar na raiz do build
        root_config = self.build_dir / "cameras.json"
        with open(root_config, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"    Configuracao gerada: {config_path}")
        
        return config_path
    
    def _copy_viewer_files(self):
        """
        Copia arquivos do Viewer para o build.
        """
        project_root = Path(__file__).parent.parent.parent
        viewer_source = project_root / "viewer"
        
        if viewer_source.exists():
            viewer_dest = self.build_dir / "viewer"
            
            # Copiar apenas arquivos Python
            for py_file in viewer_source.rglob("*.py"):
                rel_path = py_file.relative_to(viewer_source)
                dest_file = viewer_dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(py_file, dest_file)
            
            print("    Arquivos do Viewer copiados")
        else:
            print("    [AVISO] Pasta viewer/ nao encontrada - usando modo standalone")
            self._create_standalone_viewer()
    
    def _create_standalone_viewer(self):
        """
        Cria versão standalone mínima do Viewer.
        """
        viewer_code = '#!/usr/bin/env python3\n'
        viewer_code += '"""GPM CFTV Viewer - Standalone"""\n'
        viewer_code += 'import json, sys\n'
        viewer_code += 'from pathlib import Path\n\n'
        viewer_code += 'def load_config():\n'
        viewer_code += '    config_path = Path(__file__).parent.parent / "cameras.json"\n'
        viewer_code += '    if not config_path.exists():\n'
        viewer_code += '        config_path = Path.cwd() / "cameras.json"\n'
        viewer_code += '    with open(config_path, "r") as f:\n'
        viewer_code += '        return json.load(f)\n\n'
        viewer_code += 'if __name__ == "__main__":\n'
        viewer_code += '    config = load_config()\n'
        viewer_code += '    print("=" * 50)\n'
        viewer_code += '    print("GPM CFTV Viewer")\n'
        viewer_code += '    print("Cameras: " + str(len(config.get("cameras", []))))\n'
        viewer_code += '    print("=" * 50)\n'
        viewer_code += '    for cam in config.get("cameras", []):\n'
        viewer_code += '        print("  " + cam["ip"] + ":" + str(cam["port"]) + " - " + cam["rtsp_path"])\n'
        
        viewer_file = self.build_dir / "viewer" / "main.py"
        viewer_file.parent.mkdir(parents=True, exist_ok=True)
        with open(viewer_file, 'w') as f:
            f.write(viewer_code)
        
        print("    Viewer standalone criado")
    
    def _create_launcher(self):
        """
        Cria script de inicialização para Linux e Windows.
        """
        # Script Linux
        launcher_linux = '#!/bin/bash\n'
        launcher_linux += '# GPM CFTV Viewer - Script de Inicializacao\n'
        launcher_linux += '# Gerado pelo GPM CFTV Studio\n\n'
        launcher_linux += 'echo "Iniciando GPM CFTV Viewer..."\n'
        launcher_linux += 'echo "=================================="\n\n'
        launcher_linux += '# Verificar Python\n'
        launcher_linux += 'if ! command -v python3 &> /dev/null; then\n'
        launcher_linux += '    echo "[ERRO] Python 3 nao encontrado!"\n'
        launcher_linux += '    echo "   Instale: sudo apt install python3 python3-pip"\n'
        launcher_linux += '    exit 1\n'
        launcher_linux += 'fi\n\n'
        launcher_linux += '# Verificar dependencias\n'
        launcher_linux += 'echo "Verificando dependencias..."\n'
        launcher_linux += 'python3 -c "from PySide6.QtWidgets import QApplication" 2>/dev/null\n'
        launcher_linux += 'if [ $? -ne 0 ]; then\n'
        launcher_linux += '    echo "[AVISO] PySide6 nao encontrado. Instalando..."\n'
        launcher_linux += '    pip3 install PySide6\n'
        launcher_linux += 'fi\n\n'
        launcher_linux += '# Executar Viewer\n'
        launcher_linux += 'cd "$(dirname "$0")"\n'
        launcher_linux += 'python3 viewer/main.py\n\n'
        launcher_linux += 'echo "Viewer encerrado."\n'
        
        launcher_path = self.build_dir / "start_viewer.sh"
        with open(launcher_path, 'w') as f:
            f.write(launcher_linux)
        os.chmod(launcher_path, 0o755)
        
        # Script Windows
        bat_launcher = '@echo off\n'
        bat_launcher += 'echo Iniciando GPM CFTV Viewer...\n'
        bat_launcher += 'echo ==================================\n'
        bat_launcher += 'python viewer/main.py\n'
        bat_launcher += 'pause\n'
        
        bat_path = self.build_dir / "start_viewer.bat"
        with open(bat_path, 'w') as f:
            f.write(bat_launcher)
        
        print("    Scripts de inicializacao criados")
    
    def _create_readme(self):
        """
        Cria arquivo README com instruções.
        """
        generated_date = datetime.now().strftime('%d/%m/%Y %H:%M')
        num_cameras = len(self.cameras)
        
        readme = "=" * 60 + "\n"
        readme += "GPM CFTV Viewer\n"
        readme += "Sistema de Monitoramento CFTV - Armazem Paraiba\n"
        readme += "=" * 60 + "\n\n"
        
        readme += "INFORMACOES DO PACOTE\n"
        readme += "-" * 30 + "\n"
        readme += f"Gerado em: {generated_date}\n"
        readme += f"Gerado por: GPM CFTV Studio v1.0.0\n"
        readme += f"Cameras configuradas: {num_cameras}\n\n"
        
        readme += "COMO EXECUTAR\n"
        readme += "-" * 30 + "\n"
        readme += "Linux (Zorin OS):\n"
        readme += "  chmod +x start_viewer.sh\n"
        readme += "  ./start_viewer.sh\n\n"
        readme += "Windows:\n"
        readme += "  start_viewer.bat\n\n"
        readme += "Manual:\n"
        readme += "  python3 viewer/main.py\n\n"
        
        readme += "CAMERAS CONFIGURADAS\n"
        readme += "-" * 30 + "\n"
        for cam in self.cameras:
            readme += f"  {cam.id} | {cam.ip}:{cam.port} | {cam.rtsp_path}\n"
        
        readme += "\nATALHOS\n"
        readme += "-" * 30 + "\n"
        readme += "  F11         - Tela cheia\n"
        readme += "  ESC         - Voltar ao grid\n"
        readme += "  Duplo clique - Ampliar camera\n"
        readme += "  Ctrl+Q      - Sair\n\n"
        
        readme += "SUPORTE\n"
        readme += "-" * 30 + "\n"
        readme += "GPM Manutencao - Armazem Paraiba\n"
        
        readme_path = self.build_dir / "LEIA-ME.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        
        print("    README criado")
    
    def _create_package(self) -> Path:
        """
        Cria arquivo ZIP do pacote.
        
        Returns:
            Caminho do ZIP gerado.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_name = f"GPM_CFTV_Viewer_{timestamp}.zip"
        zip_path = self.output_dir / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.build_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.build_dir)
                    zf.write(file_path, arcname)
        
        print(f"    Pacote criado: {zip_path}")
        print(f"    Tamanho: {zip_path.stat().st_size / 1024:.1f} KB")
        
        return zip_path