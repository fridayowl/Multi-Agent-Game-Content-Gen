#!/usr/bin/env python3
"""
Godot project builder - FIXED VERSION
Handles creation of Godot project structure and settings with proper syntax
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Define GodotProjectSettings if not imported
class GodotProjectSettings:
    def __init__(self, name: str, main_scene: str, features: list):
        self.name = name
        self.main_scene = main_scene
        self.features = features

class GodotProjectBuilder:
    """Handles Godot project structure creation with proper syntax"""
    
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
        
        # Create .godot directory for Godot internal files
        godot_internal_dir = self.project_dir / ".godot"
        godot_internal_dir.mkdir(exist_ok=True)
        
        # Create .gitignore for the project
        await self._create_gitignore()
        
        self.logger.info("   ✅ Project structure created")
    
    async def create_project_configuration(self, project_name: str):
        """Create Godot project.godot file and other configuration"""
        
        # Create project settings
        project_settings = GodotProjectSettings(
            name=project_name,
            main_scene="res://scenes/World.tscn",
            features=["4.4", "Forward Plus"]
        )
        
        # Generate project.godot content
        project_content = self._generate_project_godot_content(project_settings)
        
        # Write project.godot file
        project_file = self.project_dir / "project.godot"
        with open(project_file, 'w', encoding='utf-8') as f:
            f.write(project_content)
        
        self.logger.info(f"   ✅ Created project.godot for {project_name}")
        
        # Create input map configuration
        await self._create_input_map()
        
        # Create addon configuration if needed
        await self._create_addon_configuration()
        
        # Create autoload configuration
        await self._create_autoload_configuration()
    
    def _generate_project_godot_content(self, settings: GodotProjectSettings) -> str:
        """Generate the content for project.godot file - FIXED VERSION"""
        
        # FIXED: Proper Godot project file format with correct header and config_version
        content = f'''; Engine configuration file.
; It's best edited using the editor UI and not directly,
; since the parameters that go here are not all obvious.
;
; Format:
;   [section] ; section goes between []
;   param=value ; assign values to parameters

config_version=5

[application]

config/name="{settings.name}"
run/main_scene="{settings.main_scene}"
config/features=PackedStringArray({self._format_string_array_fixed(settings.features)})
config/icon="res://icon.svg"

[autoload]

GlobalData="*res://scripts/GlobalData.gd"

[input]

interact={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":69,"key_label":0,"unicode":101,"echo":false,"script":null)]
}}

move_left={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":65,"key_label":0,"unicode":97,"echo":false,"script":null)]
}}

move_right={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":68,"key_label":0,"unicode":100,"echo":false,"script":null)]
}}

move_forward={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":87,"key_label":0,"unicode":119,"echo":false,"script":null)]
}}

move_backward={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":83,"key_label":0,"unicode":115,"echo":false,"script":null)]
}}

jump={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":32,"key_label":0,"unicode":32,"echo":false,"script":null)]
}}

ui_accept={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":32,"key_label":0,"unicode":32,"echo":false,"script":null), Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194309,"key_label":0,"unicode":0,"echo":false,"script":null)]
}}

ui_cancel={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194305,"key_label":0,"unicode":0,"echo":false,"script":null)]
}}

pause={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":-1,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194305,"key_label":0,"unicode":0,"echo":false,"script":null)]
}}

[rendering]

renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
environment/defaults/default_environment="res://default_env.tres"

[physics]

common/enable_pause_aware_picking=true

[layer_names]

3d_physics/layer_1="World"
3d_physics/layer_2="Player"
3d_physics/layer_3="NPCs"
3d_physics/layer_4="Buildings"
3d_physics/layer_5="Interactables"
3d_physics/layer_6="Items"
3d_physics/layer_7="Projectiles"

[debug]

gdscript/warnings/enable=true
gdscript/warnings/treat_warnings_as_errors=false
gdscript/warnings/exclude_addons=true
'''
        
        return content
    
    def _format_string_array_fixed(self, arr: list) -> str:
        """Format Python list as Godot PackedStringArray format - FIXED VERSION"""
        # FIXED: Proper PackedStringArray format without extra brackets
        formatted_items = [f'"{item}"' for item in arr]
        return ", ".join(formatted_items)
    
    async def _create_input_map(self):
        """Create input map configuration"""
        # Input map is included in project.godot file
        self.logger.info("   ✅ Created input map configuration")
    
    async def _create_autoload_configuration(self):
        """Create autoload configuration"""
        # Autoload configuration is included in project.godot file
        self.logger.info("   ✅ Created autoload configuration")
    
    async def _create_addon_configuration(self):
        """Create addon configuration if needed"""
        
        # Create addons directory for future use
        addons_dir = self.project_dir / "addons"
        addons_dir.mkdir(exist_ok=True)
        
        # Create a simple plugin configuration for the game content
        plugin_dir = addons_dir / "game_content"
        plugin_dir.mkdir(exist_ok=True)
        
        # Write plugin.cfg - FIXED FORMAT
        plugin_cfg_content = '''[plugin]

name="Generated Game Content"
description="Auto-generated game content from multi-agent pipeline"
author="Multi-Agent Game Pipeline"
version="1.0"
script="plugin.gd"
'''
        
        plugin_cfg_file = plugin_dir / "plugin.cfg"
        with open(plugin_cfg_file, 'w', encoding='utf-8') as f:
            f.write(plugin_cfg_content)
        
        # Create plugin.gd - FIXED VERSION
        plugin_gd_content = '''@tool
extends EditorPlugin

func _enter_tree():
    print("Generated Game Content plugin loaded")
    # Add custom dock or tools here if needed

func _exit_tree():
    print("Generated Game Content plugin unloaded")
    # Clean up custom additions here

func get_plugin_name():
    return "Generated Game Content"
'''
        
        plugin_gd_file = plugin_dir / "plugin.gd"
        with open(plugin_gd_file, 'w', encoding='utf-8') as f:
            f.write(plugin_gd_content)
        
        self.logger.info("   ✅ Created addon configuration")
    
    async def _create_gitignore(self):
        """Create .gitignore file for Godot project"""
        
        gitignore_content = '''# Godot 4+ specific ignores
.godot/

# Godot-specific ignores
.import/
export.cfg
export_presets.cfg

# Imported translations (automatically generated from CSV files)
*.translation

# Mono-specific ignores
.mono/
data_*/
mono_crash.*.json

# System/tool-specific ignores
.DS_Store
*.tmp
*~

# IDE specific ignores
.vscode/
.idea/
*.swp
*.swo

# Build results
builds/
exports/
'''
        
        gitignore_file = self.project_dir / ".gitignore"
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        self.logger.info("   ✅ Created .gitignore")
    
    async def create_default_environment(self):
        """Create default environment resource"""
        
        env_content = '''[gd_resource type="Environment" format=3]

[resource]
background_mode = 1
background_color = Color(0.4, 0.6, 1, 1)
ambient_light_source = 2
ambient_light_color = Color(1, 1, 1, 1)
ambient_light_energy = 0.3
fog_enabled = true
fog_light_color = Color(0.6, 0.7, 0.9, 1)
fog_sun_scatter = 0.1
'''
        
        env_file = self.project_dir / "default_env.tres"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        self.logger.info("   ✅ Created default environment")
    
    async def create_default_icon(self):
        """Create default icon.svg file"""
        
        # Simple SVG icon for the project
        icon_content = '''<svg height="128" width="128" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="124" height="124" rx="14" ry="14" fill="#363d52" stroke="#212532" stroke-width="4"/>
  <g transform="scale(.101) translate(122 122)">
    <g fill="#fff">
      <path d="m464 428c0 66.25-53.75 120-120 120s-120-53.75-120-120 53.75-120 120-120 120 53.75 120 120z"/>
      <path d="m464 108c0 66.25-53.75 120-120 120s-120-53.75-120-120 53.75-120 120-120 120 53.75 120 120z"/>
      <path d="m144 268c0 66.25-53.75 120-120 120s-120-53.75-120-120 53.75-120 120-120 120 53.75 120 120z"/>
    </g>
  </g>
</svg>'''
        
        icon_file = self.project_dir / "icon.svg"
        with open(icon_file, 'w', encoding='utf-8') as f:
            f.write(icon_content)
        
        self.logger.info("   ✅ Created default icon")
    
    async def create_export_presets(self):
        """Create export presets for the project"""
        
        export_presets_content = '''[preset.0]

name="Windows Desktop"
platform="Windows Desktop"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="builds/windows/game.exe"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.0.options]

custom_template/debug=""
custom_template/release=""
debug/export_console_wrapper=1
binary_format/embed_pck=false
texture_format/bptc=true
texture_format/s3tc=true
texture_format/etc=false
texture_format/etc2=false
binary_format/architecture="x86_64"
codesign/enable=false
application/modify_resources=true
application/icon=""
application/console_wrapper_icon=""
application/icon_interpolation=4
application/file_version=""
application/product_version=""
application/company_name=""
application/product_name=""
application/file_description=""
application/copyright=""
application/trademarks=""
application/export_angle=0
ssh_remote_deploy/enabled=false
ssh_remote_deploy/host="user@host_ip"
ssh_remote_deploy/port="22"
ssh_remote_deploy/extra_args_ssh=""
ssh_remote_deploy/extra_args_scp=""
ssh_remote_deploy/run_script_path=""
ssh_remote_deploy/cleanup_script_path=""

[preset.1]

name="Linux/X11"
platform="Linux/X11"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="builds/linux/game.x86_64"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.1.options]

custom_template/debug=""
custom_template/release=""
debug/export_console_wrapper=1
binary_format/embed_pck=false
texture_format/bptc=true
texture_format/s3tc=true
texture_format/etc=false
texture_format/etc2=false
binary_format/architecture="x86_64"
ssh_remote_deploy/enabled=false
ssh_remote_deploy/host="user@host_ip"
ssh_remote_deploy/port="22"
ssh_remote_deploy/extra_args_ssh=""
ssh_remote_deploy/extra_args_scp=""
ssh_remote_deploy/run_script_path=""
ssh_remote_deploy/cleanup_script_path=""

[preset.2]

name="Web"
platform="Web"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter=""
export_path="builds/web/index.html"
encryption_include_filters=""
encryption_exclude_filters=""
encrypt_pck=false
encrypt_directory=false

[preset.2.options]

custom_template/debug=""
custom_template/release=""
variant/extensions_support=false
vram_texture_compression/for_desktop=true
vram_texture_compression/for_mobile=false
html/export_icon=true
html/custom_html_shell=""
html/head_include=""
html/canvas_resize_policy=2
html/focus_canvas_on_start=true
html/experimental_virtual_keyboard=false
progressive_web_app/enabled=false
progressive_web_app/offline_page=""
progressive_web_app/display=1
progressive_web_app/orientation=0
progressive_web_app/icon_144x144=""
progressive_web_app/icon_180x180=""
progressive_web_app/icon_512x512=""
progressive_web_app/background_color=Color(0, 0, 0, 1)
'''
        
        export_presets_file = self.project_dir / "export_presets.cfg"
        with open(export_presets_file, 'w', encoding='utf-8') as f:
            f.write(export_presets_content)
        
        self.logger.info("   ✅ Created export presets")
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information"""
        return {
            'project_dir': str(self.project_dir),
            'directories': {name: str(path) for name, path in self.dirs.items()},
            'project_file': str(self.project_dir / "project.godot"),
            'main_scene': "res://scenes/World.tscn",
            'autoload_scripts': ["GlobalData"],
            'input_actions': [
                "interact", "move_left", "move_right", "move_forward", 
                "move_backward", "jump", "ui_accept", "ui_cancel", "pause"
            ],
            'physics_layers': [
                "World", "Player", "NPCs", "Buildings", 
                "Interactables", "Items", "Projectiles"
            ]
        }