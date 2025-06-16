#!/usr/bin/env python3
"""
Main Unity Code Exporter
Coordinates all export modules to create complete Unity packages
"""

import asyncio
import json
import os
import zipfile
from typing import Dict, List, Any
from pathlib import Path
from dataclasses import asdict
import logging
from datetime import datetime

from .data_types import ExportManifest, ExportResult
from ..exporters.world_exporter import WorldExporter
from ..exporters.character_exporter import CharacterExporter
from ..exporters.quest_exporter import QuestExporter
from ..exporters.asset_exporter import AssetExporter
from ..unity.project_builder import ProjectBuilder
from ..unity.scene_builder import SceneBuilder
from ..scripts.game_scripts import GameScriptsGenerator
from ..utils.documentation import DocumentationGenerator

class UnityCodeExporter:
    """
    COMPLETE UNITY CODE EXPORTER AGENT
    - Converts multi-agent pipeline output to Unity packages
    - Generates C# scripts for NPCs, quests, and world systems
    - Creates prefabs, scenes, and import-ready packages
    - Provides complete Unity project setup
    """
    
    def __init__(self, output_dir: str = "unity_export"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize project builder
        self.project_builder = ProjectBuilder(self.output_dir, self.logger)
        
        # Get directory references
        self.dirs = self.project_builder.get_directories()
        
        # Initialize all export modules
        self.world_exporter = WorldExporter(self.dirs['scripts_dir'], self.logger)
        self.character_exporter = CharacterExporter(self.dirs['scripts_dir'], self.logger)
        self.quest_exporter = QuestExporter(self.dirs['scripts_dir'], self.logger)
        self.asset_exporter = AssetExporter(
            self.dirs['models_dir'], 
            self.dirs['textures_dir'], 
            self.dirs['materials_dir'], 
            self.logger
        )
        self.scene_builder = SceneBuilder(self.dirs['scenes_dir'], self.logger)
        self.game_scripts = GameScriptsGenerator(self.dirs['scripts_dir'], self.logger)
        self.doc_generator = DocumentationGenerator(self.output_dir, self.logger)
        
        # Export tracking
        self.exported_scripts = []
        self.exported_prefabs = []
        self.exported_scenes = []
        self.exported_assets = []
    
    async def export_complete_package(self, world_spec: Dict[str, Any], 
                                    assets: Dict[str, Any], 
                                    characters: Dict[str, Any], 
                                    quests: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export complete Unity package from all pipeline components
        """
        self.logger.info("🚀 Starting Unity package export...")
        
        project_name = f"GeneratedGame_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Step 1: Create Unity project structure
            await self.project_builder.create_project_structure(project_name)
            
            # Step 2: Export world system
            world_objects = await self.world_exporter.export_world_system(world_spec)
            
            # Step 3: Export character system
            character_objects = await self.character_exporter.export_character_system(characters)
            
            # Step 4: Export quest system
            quest_objects = await self.quest_exporter.export_quest_system(quests, characters)
            
            # Step 5: Export assets
            asset_objects = await self.asset_exporter.export_asset_system(assets)
            
            # Step 6: Create main scene
            main_scene = await self.scene_builder.create_main_scene(
                world_objects, character_objects, quest_objects, asset_objects
            )
            
            # Step 7: Generate management scripts
            management_scripts = await self.game_scripts.generate_management_scripts(
                world_spec, characters, quests
            )
            
            # Step 8: Collect all exported files
            await self._collect_exported_files()
            
            # Step 9: Create Unity package
            package_path = await self._create_unity_package(project_name)
            
            # Step 10: Generate documentation
            docs_path = await self.doc_generator.generate_documentation(
                project_name, world_spec, characters, quests, assets
            )
            
            # Step 11: Create export manifest
            export_manifest = await self._create_export_manifest(project_name, world_spec, characters, quests, assets)
            
            # Step 12: Save manifest
            manifest_path = self.output_dir / "export_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(asdict(export_manifest), f, indent=2)
            
            self.logger.info(f"✅ Unity package export complete!")
            self.logger.info(f"   📦 Package: {package_path}")
            self.logger.info(f"   📄 Scripts: {len(self.exported_scripts)}")
            self.logger.info(f"   🎮 Prefabs: {len(self.exported_prefabs)}")
            self.logger.info(f"   🌍 Scenes: {len(self.exported_scenes)}")
            
            return {
                'status': 'success',
                'project_name': project_name,
                'package_path': str(package_path),
                'manifest': asdict(export_manifest),
                'output_directory': str(self.output_dir),
                'unity_project_path': str(self.dirs['unity_project_dir']),
                'import_ready': True,
                'file_counts': {
                    'scripts': len(self.exported_scripts),
                    'prefabs': len(self.exported_prefabs),
                    'scenes': len(self.exported_scenes),
                    'assets': len(self.exported_assets)
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Unity export failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'error': str(e),
                'partial_export': True,
                'output_directory': str(self.output_dir)
            }
    
    async def _collect_exported_files(self):
        """Collect all exported files from different modules"""
        # Collect scripts from all exporters
        self.exported_scripts.extend(self.game_scripts.get_exported_scripts())
        
        # Collect scenes
        self.exported_scenes.extend(self.scene_builder.get_exported_scenes())
        
        # Collect assets
        self.exported_assets.extend(self.asset_exporter.get_exported_assets())
    
    async def _create_unity_package(self, project_name: str) -> Path:
        """Create Unity package file"""
        
        self.logger.info("📦 Creating Unity package...")
        
        package_path = self.output_dir / f"{project_name}.unitypackage"
        
        # Create a zip file with Unity package structure
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as package_zip:
            
            # Add all files from the Unity project
            for root, dirs, files in os.walk(self.dirs['unity_project_dir']):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(self.dirs['unity_project_dir'])
                    package_zip.write(file_path, arc_path)
        
        self.logger.info(f"   ✅ Package created: {package_path.name}")
        return package_path
    
    async def _create_export_manifest(self, project_name: str, world_spec: Dict[str, Any], 
                                    characters: Dict[str, Any], quests: Dict[str, Any], 
                                    assets: Dict[str, Any]) -> ExportManifest:
        """Create export manifest"""
        
        return ExportManifest(
            project_name=project_name,
            unity_version="2022.3 LTS",
            export_timestamp=datetime.now().isoformat(),
            content_summary=self._create_content_summary(world_spec, characters, quests, assets),
            file_structure=self._create_file_structure_map(),
            import_instructions=self._create_import_instructions(),
            scene_files=self.exported_scenes,
            script_files=self.exported_scripts,
            prefab_files=self.exported_prefabs,
            asset_files=self.exported_assets
        )
    
    def _create_content_summary(self, world_spec: Dict[str, Any], 
                               characters: Dict[str, Any], 
                               quests: Dict[str, Any], 
                               assets: Dict[str, Any]) -> Dict[str, Any]:
        """Create content summary for manifest"""
        
        return {
            "world": {
                "theme": world_spec.get('theme', 'Unknown'),
                "buildings": len(world_spec.get('buildings', [])),
                "natural_features": len(world_spec.get('natural_features', []))
            },
            "characters": {
                "total_npcs": len(characters.get('characters', [])),
                "unique_personalities": len(characters.get('characters', [])),
                "relationships": characters.get('generation_summary', {}).get('total_relationships', 0)
            },
            "quests": {
                "total_quests": len(quests.get('quests', [])),
                "main_quests": len([q for q in quests.get('quests', []) if q.get('quest_type') == 'main']),
                "side_quests": len([q for q in quests.get('quests', []) if q.get('quest_type') == 'side'])
            },
            "assets": {
                "total_assets": assets.get('generation_summary', {}).get('total_creative_assets', 0),
                "ai_generated": assets.get('ai_generated', False)
            }
        }
    
    def _create_file_structure_map(self) -> Dict[str, str]:
        """Create file structure mapping"""
        
        return {
            "Scripts/": "C# scripts for game logic and systems",
            "Scenes/": "Unity scene files ready to play",
            "Models/": "3D model files (.obj, .fbx)",
            "Textures/": "AI-generated texture files (.png)",
            "Materials/": "Unity material definitions",
            "Prefabs/": "Reusable Unity prefabs",
            "ProjectSettings/": "Unity project configuration",
            "Packages/": "Unity package dependencies"
        }
    
    def _create_import_instructions(self) -> List[str]:
        """Create import instructions"""
        
        return [
            "1. Open Unity 2022.3 LTS or newer",
            "2. Create new 3D project or open existing project",
            "3. Go to Assets > Import Package > Custom Package",
            "4. Select the .unitypackage file from this export",
            "5. Import all assets when prompted",
            "6. Open Assets/Scenes/GeneratedGameScene.unity",
            "7. Press Play to start exploring the generated world",
            "8. Use WASD to move, E to interact, Q for quest log",
            "9. Interact with NPCs to start conversations and quests",
            "10. Customize scripts and assets as needed for your project"
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get code exporter status"""
        
        return {
            'status': 'ready',
            'unity_version_target': '2022.3 LTS',
            'output_directory': str(self.output_dir),
            'exported_counts': {
                'scripts': len(self.exported_scripts),
                'prefabs': len(self.exported_prefabs),
                'scenes': len(self.exported_scenes),
                'assets': len(self.exported_assets)
            },
            'capabilities': [
                'unity_package_generation',
                'csharp_script_creation',
                'scene_file_generation',
                'prefab_creation',
                'project_structure_setup',
                'documentation_generation',
                'asset_integration',
                'system_coordination'
            ],
            'supported_formats': [
                'Unity 2022.3+ packages',
                'C# scripts',
                'Unity scenes (.unity)',
                'Unity prefabs (.prefab)',
                'OBJ 3D models',
                'PNG textures',
                'Unity materials'
            ],
            'export_features': [
                'Complete game systems',
                'NPC interaction systems',
                'Quest management',
                'Save/load functionality',
                'UI management',
                'Player controller',
                'World management',
                'Dialogue systems'
            ]
        }