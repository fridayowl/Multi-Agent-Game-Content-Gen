#!/usr/bin/env python3
"""
Asset system exporter
Handles copying and organizing 3D models, textures, and materials
"""

from typing import Dict, List, Any
from pathlib import Path
import logging
import shutil

from ..core.data_types import UnityGameObject, UnityComponent

class AssetExporter:
    """Handles asset system export to Unity"""
    
    def __init__(self, models_dir: Path, textures_dir: Path, materials_dir: Path, logger: logging.Logger):
        self.models_dir = models_dir
        self.textures_dir = textures_dir
        self.materials_dir = materials_dir
        self.logger = logger
        self.exported_assets = []
    
    async def export_asset_system(self, assets: Dict[str, Any]) -> List[UnityGameObject]:
        """Export asset system"""
        self.logger.info("🎨 Exporting asset system...")
        
        asset_objects = []
        
        # Copy asset files if they exist
        if assets and assets.get('output_directory'):
            await self._copy_asset_files(assets)
        
        # Create asset manager
        asset_manager = UnityGameObject(
            name="AssetManager",
            transform={
                "position": [0, 0, 0],
                "rotation": [0, 0, 0, 1],
                "scale": [1, 1, 1]
            },
            components=[
                UnityComponent(
                    component_type="AssetManager",
                    properties={
                        "assetCount": assets.get('generation_summary', {}).get('total_creative_assets', 0) if assets else 0
                    }
                )
            ],
            children=[]
        )
        asset_objects.append(asset_manager)
        
        self.logger.info(f"   ✅ Exported asset system")
        return asset_objects
    
    async def _copy_asset_files(self, assets: Dict[str, Any]):
        """Copy asset files to Unity project"""
        self.logger.info("📁 Copying asset files...")
        
        asset_dir = Path(assets.get('output_directory', ''))
        if not asset_dir.exists():
            self.logger.warning(f"Asset directory not found: {asset_dir}")
            return
        
        # Copy models
        models_src = asset_dir / "models"
        if models_src.exists():
            for model_file in models_src.glob("*.obj"):
                dest_file = self.models_dir / model_file.name
                shutil.copy2(model_file, dest_file)
                self.exported_assets.append(f"Models/{model_file.name}")
        
        # Copy textures  
        textures_src = asset_dir / "ai_textures"
        if textures_src.exists():
            for texture_file in textures_src.glob("*.png"):
                dest_file = self.textures_dir / texture_file.name
                shutil.copy2(texture_file, dest_file)
                self.exported_assets.append(f"Textures/{texture_file.name}")
        
        self.logger.info(f"   ✅ Copied {len(self.exported_assets)} asset files")
    
    def get_exported_assets(self) -> List[str]:
        """Get list of exported asset files"""
        return self.exported_assets.copy()