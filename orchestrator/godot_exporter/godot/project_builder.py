#!/usr/bin/env python3
"""
Godot project builder
Handles creation of Godot project structure and settings
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any
from ..core.data_types import GodotProjectSettings

class GodotProjectBuilder:
    """Handles Godot project structure creation"""
    
    def __init__(self, dirs: Dict[str, Path], logger: logging.Logger):
        self.dirs = dirs
        self.logger = logger
        self.project_dir = dirs['project_dir']
    
    async def create_project_structure(self, project_name: str):
        """Create Godot project structure"""
        self.logger.info("📁 Creating Godot project structure...")
        
        # Ensure all directories exist
        for dir_name, dir_path in self.dirs.items():
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"   📂 Created {dir_name}: {dir_path.name}")
        
        self.logger.info("   ✅ Project structure created")
    
    async def create_project_configuration(self, project_name: str):
        """Create Godot project.godot file and other configuration"""
        
        # Create project settings
        project_settings = GodotProjectSettings(
            name=project_name,
            main_scene="res://scenes/World.tscn",
            features=["4.3"]
        )
        
        # Generate project.godot content
        project_content = self._generate_project_godot_content(project_settings)
        
        # Write project.godot file
        project_file = self.project_dir / "project.godot"
        with open(project_file, 'w') as f:
            f.write(project_content)
        
        self.logger.info(f"   ✅ Created project.godot for {project_name}")
        
        # Create input map configuration
        await self._create_input_map()
        
        # Create addon configuration if needed
        await self._create_addon_configuration()
    
    def _generate_project_godot_content(self, settings: GodotProjectSettings) -> str:
        """Generate the content for project.godot file"""
        
        content = f'''[application]

config/name="{settings.name}"
run/main_scene="{settings.main_scene}"
config/features=PackedStringArray({self._format_string_array(settings.features)})

[input]

interact={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":69,"key_label":0,"unicode":101,"echo":false,"script":null)
]
}}

move_left={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":65,"key_label":0,"unicode":97,"echo":false,"script":null)
]
}}

move_right={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":68,"key_label":0,"unicode":100,"echo":false,"script":null)
]
}}

move_forward={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":87,"key_label":0,"unicode":119,"echo":false,"script":null)
]
}}

move_backward={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":83,"key_label":0,"unicode":115,"echo":false,"script":null)
]
}}

jump={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":32,"key_label":0,"unicode":32,"echo":false,"script":null)
]
}}

[rendering]

renderer/rendering_method="{settings.rendering_method}"
renderer/rendering_method.mobile="{settings.rendering_method}"

[layer_names]

3d_physics/layer_1="World"
3d_physics/layer_2="Player"
3d_physics/layer_3="NPCs"
3d_physics/layer_4="Buildings"
3d_physics/layer_5="Interactables"
'''
        
        return content
    
    def _format_string_array(self, arr: list) -> str:
        """Format Python list as Godot PackedStringArray format"""
        formatted_items = [f'"{item}"' for item in arr]
        return "[" + ", ".join(formatted_items) + "]"
    
    async def _create_input_map(self):
        """Create input map configuration"""
        # Input map is included in project.godot file above
        self.logger.info("   ✅ Created input map configuration")
    
    async def _create_addon_configuration(self):
        """Create addon configuration if needed"""
        
        # Create addons directory for future use
        addons_dir = self.project_dir / "addons"
        addons_dir.mkdir(exist_ok=True)
        
        # Create a simple plugin configuration for the game content
        plugin_dir = addons_dir / "game_content"
        plugin_dir.mkdir(exist_ok=True)
        
        plugin_cfg = {
            "plugin": {
                "name": "Generated Game Content",
                "description": "Auto-generated game content from multi-agent pipeline",
                "author": "Multi-Agent Game Pipeline",
                "version": "1.0",
                "script": "plugin.gd"
            }
        }
        
        # Write plugin.cfg
        plugin_cfg_file = plugin_dir / "plugin.cfg"
        with open(plugin_cfg_file, 'w') as f:
            f.write("[plugin]\n\n")
            for key, value in plugin_cfg["plugin"].items():
                f.write(f'{key}="{value}"\n')
        
        # Create simple plugin.gd
        plugin_gd_content = '''@tool
extends EditorPlugin

func _enter_tree():
    print("Generated Game Content plugin loaded")

func _exit_tree():
    print("Generated Game Content plugin unloaded")
'''
        
        plugin_gd_file = plugin_dir / "plugin.gd"
        with open(plugin_gd_file, 'w') as f:
            f.write(plugin_gd_content)
        
        self.logger.info("   ✅ Created addon configuration")
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information"""
        return {
            'project_dir': str(self.project_dir),
            'directories': {name: str(path) for name, path in self.dirs.items()},
            'project_file': str(self.project_dir / "project.godot")
        }