"""
GPM CFTV Viewer - Gerenciador de Layout Automático
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import math
from typing import Tuple


class LayoutManager:
    """
    Calcula o layout de grid baseado no número de câmeras.
    """
    
    @staticmethod
    def calculate_grid(num_cameras: int) -> Tuple[int, int]:
        """
        Calcula o grid ideal (colunas, linhas).
        
        Args:
            num_cameras: Número de câmeras.
            
        Returns:
            Tupla (colunas, linhas).
        """
        if num_cameras <= 0:
            return 0, 0
        
        if num_cameras == 1:
            return 1, 1
        
        if num_cameras == 2:
            return 2, 1
        
        # Para outras quantidades: grid mais próximo de um quadrado
        cols = math.ceil(math.sqrt(num_cameras))
        rows = math.ceil(num_cameras / cols)
        
        return cols, rows
    
    @staticmethod
    def get_layout_name(num_cameras: int) -> str:
        """
        Retorna nome descritivo do layout.
        
        Args:
            num_cameras: Número de câmeras.
            
        Returns:
            Nome do layout (ex: "2x2", "3x3").
        """
        cols, rows = LayoutManager.calculate_grid(num_cameras)
        return f"{cols}x{rows}"
    
    @staticmethod
    def print_layout_table():
        """Imprime tabela de layouts para debug."""
        print("\n📐 Tabela de Layouts:")
        print("-" * 25)
        for n in range(1, 17):
            cols, rows = LayoutManager.calculate_grid(n)
            print(f"  {n:2d} câmera(s) → {cols}x{rows}")