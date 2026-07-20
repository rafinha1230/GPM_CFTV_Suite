"""
GPM CFTV Studio - Escritor de Scripts Linux
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba

Garante que scripts .sh sejam gerados com formato Unix (LF).
"""

import os
from pathlib import Path


class ScriptWriter:
    """
    Escreve scripts shell com formato Unix (LF),
    independente do sistema operacional.
    """
    
    @staticmethod
    def write_script(filepath: str, content: str, executable: bool = True):
        """
        Escreve um arquivo de script garantindo:
        - Quebras de linha Unix (LF)
        - Permissão de execução (no Linux)
        - Encoding UTF-8 sem BOM
        
        Args:
            filepath: Caminho do arquivo
            content: Conteúdo do script
            executable: Se deve marcar como executável
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Substituir CRLF por LF (remove o ^M)
        content = content.replace('\r\n', '\n')
        content = content.replace('\r', '\n')
        
        # Garantir que termina com um LF
        if not content.endswith('\n'):
            content += '\n'
        
        # Escrever arquivo
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        # Tornar executável (funciona no Linux)
        if executable:
            try:
                os.chmod(filepath, 0o755)
            except (OSError, PermissionError):
                pass  # Windows não suporta chmod
        
        print(f"    Script escrito: {filepath.name}")