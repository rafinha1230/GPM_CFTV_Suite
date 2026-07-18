"""
GPM CFTV Studio - Gerenciador de Câmeras
Autor: Rafael - GPM Manutenção
Empresa: Armazém Paraíba
"""

import json
import os
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from studio.models.camera import Camera


class CameraManager:
    """
    Gerencia o CRUD de câmeras e persistência em JSON.
    """
    
    def __init__(self, config_file: str = "cameras_config.json"):
        """
        Inicializa o gerenciador.
        
        Args:
            config_file: Nome do arquivo de configuração.
        """
        self.config_file = Path(config_file)
        self.cameras: List[Camera] = []
        self.load()
    
    def add(self, camera: Camera) -> bool:
        """
        Adiciona uma nova câmera.
        
        Args:
            camera: Instância de Camera a ser adicionada.
            
        Returns:
            True se adicionou com sucesso, False se falhou.
        """
        # Validar câmera
        valid, msg = camera.validate()
        if not valid:
            print(f"❌ Erro ao adicionar: {msg}")
            return False
        
        # Verificar IP duplicado
        for existing in self.cameras:
            if existing.ip == camera.ip and existing.rtsp_path == camera.rtsp_path:
                print(f"❌ Câmera com IP {camera.ip} e caminho {camera.rtsp_path} já existe!")
                return False
        
        camera.created_at = datetime.now().isoformat()
        camera.updated_at = datetime.now().isoformat()
        
        self.cameras.append(camera)
        self.save()
        
        print(f"✅ Câmera {camera.id} adicionada com sucesso!")
        return True
    
    def remove(self, camera_id: str) -> bool:
        """
        Remove uma câmera pelo ID.
        
        Args:
            camera_id: ID da câmera a remover.
            
        Returns:
            True se removeu, False se não encontrou.
        """
        for i, camera in enumerate(self.cameras):
            if camera.id == camera_id:
                removed = self.cameras.pop(i)
                self.save()
                print(f"🗑️ Câmera {removed.id} removida!")
                return True
        
        print(f"❌ Câmera {camera_id} não encontrada!")
        return False
    
    def update(self, camera_id: str, updated_camera: Camera) -> bool:
        """
        Atualiza uma câmera existente.
        
        Args:
            camera_id: ID da câmera a atualizar.
            updated_camera: Nova instância com dados atualizados.
            
        Returns:
            True se atualizou, False se não encontrou.
        """
        for i, camera in enumerate(self.cameras):
            if camera.id == camera_id:
                updated_camera.id = camera_id
                updated_camera.created_at = camera.created_at
                updated_camera.updated_at = datetime.now().isoformat()
                
                valid, msg = updated_camera.validate()
                if not valid:
                    print(f"❌ Erro ao atualizar: {msg}")
                    return False
                
                self.cameras[i] = updated_camera
                self.save()
                print(f"✅ Câmera {camera_id} atualizada!")
                return True
        
        print(f"❌ Câmera {camera_id} não encontrada!")
        return False
    
    def get(self, camera_id: str) -> Optional[Camera]:
        """
        Busca uma câmera pelo ID.
        
        Args:
            camera_id: ID da câmera.
            
        Returns:
            Camera se encontrada, None caso contrário.
        """
        for camera in self.cameras:
            if camera.id == camera_id:
                return camera
        return None
    
    def get_all(self) -> List[Camera]:
        """
        Retorna todas as câmeras cadastradas.
        
        Returns:
            Lista de Camera.
        """
        return self.cameras
    
    def get_enabled(self) -> List[Camera]:
        """
        Retorna apenas câmeras ativas.
        
        Returns:
            Lista de Camera habilitadas.
        """
        return [c for c in self.cameras if c.enabled]
    
    def count(self) -> int:
        """
        Retorna o número total de câmeras.
        
        Returns:
            Quantidade de câmeras.
        """
        return len(self.cameras)
    
    def clear(self):
        """Remove todas as câmeras."""
        self.cameras.clear()
        self.save()
        print("🗑️ Todas as câmeras foram removidas!")
    
    def save(self):
        """Salva as câmeras no arquivo JSON."""
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "cameras": [camera.to_dict() for camera in self.cameras]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Configuração salva: {self.config_file}")
    
    def load(self):
        """Carrega as câmeras do arquivo JSON."""
        if not self.config_file.exists():
            print(f"📄 Arquivo de configuração não encontrado. Criando novo: {self.config_file}")
            self.cameras = []
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.cameras = []
            for camera_data in data.get("cameras", []):
                camera = Camera.from_dict(camera_data)
                self.cameras.append(camera)
            
            print(f"📂 Carregadas {len(self.cameras)} câmeras de {self.config_file}")
            
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {e}")
            self.cameras = []
    
    def export_for_viewer(self, output_file: str = "viewer_config.json"):
        """
        Exporta configuração para o Viewer (apenas câmeras ativas).
        
        Args:
            output_file: Caminho do arquivo de saída.
        """
        enabled_cameras = self.get_enabled()
        
        data = {
            "version": "1.0.0",
            "viewer_settings": {
                "window_title": "GPM CFTV Viewer",
                "fullscreen_on_start": False,
                "keep_aspect_ratio": True
            },
            "cameras": [camera.to_dict() for camera in enabled_cameras]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"📦 Configuração do Viewer exportada: {output_file}")
        return output_file