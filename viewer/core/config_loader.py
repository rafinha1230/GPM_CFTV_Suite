"""
GPM CFTV Viewer - Carregador de Configuração
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import json
import os
import sys
from pathlib import Path
from viewer.models.camera_config import ViewerConfig


class ConfigLoader:
    """
    Carrega a configuração do Viewer.
    Busca o arquivo cameras.json em vários locais.
    """
    
    CONFIG_FILE = "cameras.json"
    
    @staticmethod
    def load() -> ViewerConfig:
        """
        Carrega a configuração das câmeras.
        
        Procura o arquivo nesta ordem:
        1. Mesma pasta do executável
        2. Pasta home do usuário
        3. Caminho passado como argumento
        
        Returns:
            ViewerConfig com as câmeras carregadas.
        """
        config_path = ConfigLoader._find_config()
        
        if not config_path:
            print("❌ Arquivo de configuração não encontrado!")
            print("   Coloque o cameras.json na mesma pasta do programa.")
            return ViewerConfig()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = ViewerConfig.from_dict(data)
            print(f"✅ Configuração carregada: {config_path}")
            print(f"📷 Câmeras encontradas: {len(config.cameras)}")
            
            return config
            
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {e}")
            return ViewerConfig()
    
    @staticmethod
    def _find_config() -> str:
        """
        Procura o arquivo de configuração.
        
        Returns:
            Caminho do arquivo ou None se não encontrado.
        """
        # 1. Argumento de linha de comando
        if len(sys.argv) > 1:
            arg_path = sys.argv[1]
            if os.path.exists(arg_path):
                return arg_path
        
        # 2. Mesma pasta do executável
        exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path.cwd()
        exe_config = exe_dir / ConfigLoader.CONFIG_FILE
        if exe_config.exists():
            return str(exe_config)
        
        # 3. Pasta home
        home_config = Path.home() / ConfigLoader.CONFIG_FILE
        if home_config.exists():
            return str(home_config)
        
        return None