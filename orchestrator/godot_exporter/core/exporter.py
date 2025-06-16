#!/usr/bin/env python3
"""
Godot Code Exporter - Main coordination class
Handles the complete export pipeline from multi-agent content to Godot project
"""

import os
import json
import logging
import zipfile
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Import Godot-specific modules
from ..godot.project_builder import GodotProjectBuilder
from ..godot.scene_builder import GodotSceneBuilder  
from ..godot.script_generator import GodotScriptGenerator
from ..godot.resource_exporter import GodotResourceExporter
from .data_types import GodotExportResult, GodotExportManifest

class GodotCodeExporter:
    """Main Godot export coordination class"""
    
    def __init__(self, output_dir: str = "godot_export"):
        self.output_dir = Path(output_dir)
        self.logger = self._setup_logger()
        
        # Initialize directory structure
        self.dirs = {}
        
        # Initialize export modules (will be set up in export_complete_package)
        self.project_builder = None
        self.scene_builder = None
        self.script_generator = None
        self.resource_exporter = None
        
        # Export tracking
        self.exported_scripts = []
        self.exported_scenes = []
        self.exported_resources = []
        self.exported_assets = []
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the exporter"""
        logger = logging.getLogger('GodotExporter')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def export_complete_package(self, world_spec: Dict[str, Any], 
                                    assets: Dict[str, Any], 
                                    characters: Dict[str, Any], 
                                    quests: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export complete Godot package from all pipeline components
        """
        self.logger.info("🚀 Starting Godot project export...")
        
        project_name = f"GeneratedGame_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Step 1: Create Godot project structure
            await self._initialize_export_modules()
            await self.project_builder.create_project_structure(project_name)
            
            # Step 2: Export world system
            world_scenes = await self.scene_builder.export_world_scenes(world_spec)
            self.exported_scenes.extend(world_scenes)
            
            # Step 3: Export character system
            if characters:
                character_scripts = await self.script_generator.export_character_scripts(characters)
                self.exported_scripts.extend(character_scripts)
            
            # Step 4: Export quest system
            if quests:
                quest_scripts = await self.script_generator.export_quest_scripts(quests)
                self.exported_scripts.extend(quest_scripts)
            
            # Step 5: Export game management scripts
            game_scripts = await self.script_generator.export_game_management_scripts()
            self.exported_scripts.extend(game_scripts)
            
            # Step 6: Export resources and data
            resource_files = await self.resource_exporter.export_data_resources(
                world_spec, assets, characters, quests
            )
            self.exported_resources.extend(resource_files)
            
            # Step 7: Export assets if available
            if assets:
                asset_files = await self.resource_exporter.export_asset_files(assets)
                self.exported_assets.extend(asset_files)
            
            # Step 8: Create main scenes
            main_scenes = await self.scene_builder.create_main_scenes(world_spec, characters)
            self.exported_scenes.extend(main_scenes)
            
            # Step 9: Generate project configuration
            await self.project_builder.create_project_configuration(project_name)
            
            # Step 10: Create export manifest
            manifest = await self._create_export_manifest(
                project_name, world_spec, characters, quests, assets
            )
            
            # Step 11: Create documentation
            await self._create_documentation(manifest)
            
            result = GodotExportResult(
                status="success",
                project_name=project_name,
                project_path=str(self.dirs['project_dir']),
                manifest=manifest,
                output_directory=str(self.output_dir),
                godot_project_path=str(self.dirs['project_dir']),
                import_ready=True,
                file_counts={
                    'scripts': len(self.exported_scripts),
                    'scenes': len(self.exported_scenes),
                    'resources': len(self.exported_resources),
                    'assets': len(self.exported_assets)
                }
            )
            
            self.logger.info("✅ Godot project export completed successfully!")
            return result.__dict__
            
        except Exception as e:
            self.logger.error(f"❌ Export failed: {str(e)}")
            
            error_result = GodotExportResult(
                status="error",
                project_name=project_name,
                project_path="",
                manifest=None,
                output_directory=str(self.output_dir),
                godot_project_path="",
                import_ready=False,
                file_counts={},
                error=str(e)
            )
            
            return error_result.__dict__
    
    async def _initialize_export_modules(self):
        """Initialize all export modules with proper directory structure"""
        
        # Create main project directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_dir = self.output_dir / f"GodotProject_{timestamp}"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up directory structure
        self.dirs = {
            'project_dir': project_dir,
            'scenes_dir': project_dir / 'scenes',
            'scripts_dir': project_dir / 'scripts',
            'resources_dir': project_dir / 'resources',
            'data_dir': project_dir / 'data',
            'assets_dir': project_dir / 'assets',
            'models_dir': project_dir / 'assets' / 'models',
            'textures_dir': project_dir / 'assets' / 'textures',
            'materials_dir': project_dir / 'assets' / 'materials'
        }
        
        # Create directories
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize export modules
        self.project_builder = GodotProjectBuilder(self.dirs, self.logger)
        self.scene_builder = GodotSceneBuilder(self.dirs, self.logger)
        self.script_generator = GodotScriptGenerator(self.dirs, self.logger)
        self.resource_exporter = GodotResourceExporter(self.dirs, self.logger)
    
    async def _create_export_manifest(self, project_name: str, world_spec: Dict[str, Any], 
                                    characters: Dict[str, Any], quests: Dict[str, Any], 
                                    assets: Dict[str, Any]) -> GodotExportManifest:
        """Create export manifest"""
        
        return GodotExportManifest(
            project_name=project_name,
            godot_version="4.3",
            export_timestamp=datetime.now().isoformat(),
            content_summary=self._create_content_summary(world_spec, characters, quests, assets),
            file_structure=self._create_file_structure_map(),
            import_instructions=self._create_import_instructions(),
            scene_files=self.exported_scenes,
            script_files=self.exported_scripts,
            resource_files=self.exported_resources,
            asset_files=self.exported_assets
        )
    
    def _create_content_summary(self, world_spec: Dict[str, Any], 
                               characters: Dict[str, Any], 
                               quests: Dict[str, Any], 
                               assets: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of exported content"""
        
        summary = {
            'world_components': len(world_spec.get('buildings', [])) if world_spec else 0,
            'character_count': len(characters.get('characters', [])) if characters else 0,
            'quest_count': len(quests.get('quests', [])) if quests else 0,
            'asset_count': assets.get('total_count', 0) if assets else 0,
            'export_features': [
                'Player controller with first-person movement',
                'Interactive NPC system with dialogue',
                'Quest management system',
                'World building placement',
                'JSON-based data loading system'
            ]
        }
        
        return summary
    
    def _create_file_structure_map(self) -> Dict[str, str]:
        """Create file structure description"""
        
        return {
            'project.godot': 'Main Godot project file',
            'scenes/': 'Game scenes (.tscn files)',
            'scenes/World.tscn': 'Main world scene',
            'scenes/Player.tscn': 'Player character scene',
            'scripts/': 'GDScript files (.gd)',
            'scripts/WorldManager.gd': 'Main world management',
            'scripts/Player.gd': 'Player controller',
            'scripts/NPC.gd': 'NPC system',
            'scripts/QuestManager.gd': 'Quest management',
            'resources/': 'Godot resource files',
            'data/': 'JSON data files',
            'assets/': 'Game assets (models, textures, materials)'
        }
    
    def _create_import_instructions(self) -> List[str]:
        """Create import instructions for users"""
        
        return [
            "1. Download and install Godot 4.3+ from godotengine.org",
            "2. Open Godot and click 'Import'",
            "3. Navigate to the exported project directory",
            "4. Select 'project.godot' file",
            "5. Click 'Import & Edit'",
            "6. Press F5 to run the game",
            "7. Use WASD to move, mouse to look around, E to interact"
        ]
    
    async def _create_documentation(self, manifest: GodotExportManifest):
        """Create documentation files"""
        
        # Create README
        readme_content = f"""# {manifest.project_name}

Generated by Multi-Agent Game Content Pipeline
Export Date: {manifest.export_timestamp}

## Content Summary
- World Components: {manifest.content_summary['world_components']}
- Characters: {manifest.content_summary['character_count']}
- Quests: {manifest.content_summary['quest_count']}
- Assets: {manifest.content_summary['asset_count']}

## Import Instructions
{chr(10).join([f"{i}. {instruction}" for i, instruction in enumerate(manifest.import_instructions, 1)])}

## Controls
- WASD: Move
- Mouse: Look around
- E: Interact with NPCs and objects
- ESC: Release mouse cursor

## File Structure
{chr(10).join([f"- {path}: {desc}" for path, desc in manifest.file_structure.items()])}

## Features
{chr(10).join([f"- {feature}" for feature in manifest.content_summary['export_features']])}
"""
        
        readme_file = self.dirs['project_dir'] / 'README.md'
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        # Save manifest as JSON
        manifest_file = self.dirs['project_dir'] / 'export_manifest.json'
        with open(manifest_file, 'w') as f:
            json.dump(manifest.__dict__, f, indent=2, default=str)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get exporter status"""
        return {
            'status': 'ready',
            'output_dir': str(self.output_dir),
            'exported_projects': len(list(self.output_dir.glob('GodotProject_*'))) if self.output_dir.exists() else 0
        }