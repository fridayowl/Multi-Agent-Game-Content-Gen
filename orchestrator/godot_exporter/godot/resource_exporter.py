#!/usr/bin/env python3
"""
Godot resource exporter
Handles export of data files, assets, and Godot resources
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List

class GodotResourceExporter:
    """Handles Godot resource and data export"""
    
    def __init__(self, dirs: Dict[str, Path], logger: logging.Logger):
        self.dirs = dirs
        self.logger = logger
        self.data_dir = dirs['data_dir']
        self.resources_dir = dirs['resources_dir']
        self.assets_dir = dirs['assets_dir']
    
    async def export_data_resources(self, world_spec: Dict[str, Any], 
                                   assets: Dict[str, Any], 
                                   characters: Dict[str, Any], 
                                   quests: Dict[str, Any]) -> List[str]:
        """Export JSON data files for Godot to load"""
        resource_files = []
        
        # Export world specification
        if world_spec:
            world_file = await self._export_world_data(world_spec)
            resource_files.append(world_file)
        
        # Export character data
        if characters:
            characters_file = await self._export_characters_data(characters)
            resource_files.append(characters_file)
        
        # Export quest data
        if quests:
            quests_file = await self._export_quests_data(quests)
            resource_files.append(quests_file)
        
        # Export game configuration
        config_file = await self._export_game_config()
        resource_files.append(config_file)
        
        self.logger.info(f"   ✅ Created {len(resource_files)} data files")
        return resource_files
    
    async def export_asset_files(self, assets: Dict[str, Any]) -> List[str]:
        """Export asset files and create Godot resources"""
        asset_files = []
        
        # Create basic mesh resources
        mesh_files = await self._create_basic_meshes()
        asset_files.extend(mesh_files)
        
        # Create material resources
        material_files = await self._create_basic_materials()
        asset_files.extend(material_files)
        
        # Copy asset files if they exist
        if assets and 'assets' in assets:
            copied_files = await self._copy_pipeline_assets(assets)
            asset_files.extend(copied_files)
        
        self.logger.info(f"   ✅ Created {len(asset_files)} asset files")
        return asset_files
    
    async def _export_world_data(self, world_spec: Dict[str, Any]) -> str:
        """Export world specification to JSON"""
        
        world_file = self.data_dir / "world_spec.json"
        with open(world_file, 'w') as f:
            json.dump(world_spec, f, indent=2)
        
        return "world_spec.json"
    
    async def _export_characters_data(self, characters: Dict[str, Any]) -> str:
        """Export character data to JSON"""
        
        characters_file = self.data_dir / "characters.json"
        with open(characters_file, 'w') as f:
            json.dump(characters, f, indent=2)
        
        return "characters.json"
    
    async def _export_quests_data(self, quests: Dict[str, Any]) -> str:
        """Export quest data to JSON"""
        
        quests_file = self.data_dir / "quests.json"
        with open(quests_file, 'w') as f:
            json.dump(quests, f, indent=2)
        
        return "quests.json"
    
    async def _export_game_config(self) -> str:
        """Export game configuration"""
        
        config = {
            "game_settings": {
                "title": "Generated Game World",
                "version": "1.0.0",
                "player_start_position": [0, 2, 0],
                "world_bounds": [-50, 50, -50, 50],
                "gravity": 9.8
            },
            "ui_settings": {
                "show_debug_info": False,
                "enable_minimap": True,
                "dialogue_speed": 50
            },
            "gameplay_settings": {
                "player_speed": 5.0,
                "interaction_distance": 3.0,
                "auto_save_interval": 300
            }
        }
        
        config_file = self.data_dir / "game_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return "game_config.json"
    
    async def _create_basic_meshes(self) -> List[str]:
        """Create basic mesh resources for buildings and objects"""
        mesh_files = []
        
        # Building cube mesh
        building_mesh = '''[gd_resource type="BoxMesh" format=3]

[resource]
size = Vector3(4, 3, 4)
'''
        
        building_mesh_file = self.dirs['models_dir'] / "building_cube.tres"
        with open(building_mesh_file, 'w') as f:
            f.write(building_mesh)
        mesh_files.append("building_cube.tres")
        
        # Building collision shape
        building_collision = '''[gd_resource type="BoxShape3D" format=3]

[resource]
size = Vector3(4, 3, 4)
'''
        
        building_collision_file = self.dirs['models_dir'] / "building_collision.tres"
        with open(building_collision_file, 'w') as f:
            f.write(building_collision)
        mesh_files.append("building_collision.tres")
        
        # Tree mesh (cylinder + sphere)
        tree_mesh = '''[gd_resource type="CylinderMesh" format=3]

[resource]
top_radius = 0.2
bottom_radius = 0.3
height = 3.0
'''
        
        tree_mesh_file = self.dirs['models_dir'] / "tree_trunk.tres"
        with open(tree_mesh_file, 'w') as f:
            f.write(tree_mesh)
        mesh_files.append("tree_trunk.tres")
        
        # Tree leaves
        tree_leaves = '''[gd_resource type="SphereMesh" format=3]

[resource]
radius = 1.5
height = 3.0
'''
        
        tree_leaves_file = self.dirs['models_dir'] / "tree_leaves.tres"
        with open(tree_leaves_file, 'w') as f:
            f.write(tree_leaves)
        mesh_files.append("tree_leaves.tres")
        
        return mesh_files
    
    async def _create_basic_materials(self) -> List[str]:
        """Create basic material resources"""
        material_files = []
        
        # Stone material for buildings
        stone_material = '''[gd_resource type="StandardMaterial3D" format=3]

[resource]
albedo_color = Color(0.6, 0.6, 0.6, 1)
roughness = 0.8
metallic = 0.0
'''
        
        stone_material_file = self.dirs['materials_dir'] / "stone_material.tres"
        with open(stone_material_file, 'w') as f:
            f.write(stone_material)
        material_files.append("stone_material.tres")
        
        # Wood material for doors/trim
        wood_material = '''[gd_resource type="StandardMaterial3D" format=3]

[resource]
albedo_color = Color(0.4, 0.2, 0.1, 1)
roughness = 0.9
metallic = 0.0
'''
        
        wood_material_file = self.dirs['materials_dir'] / "wood_material.tres"
        with open(wood_material_file, 'w') as f:
            f.write(wood_material)
        material_files.append("wood_material.tres")
        
        # Grass material
        grass_material = '''[gd_resource type="StandardMaterial3D" format=3]

[resource]
albedo_color = Color(0.2, 0.8, 0.2, 1)
roughness = 1.0
metallic = 0.0
'''
        
        grass_material_file = self.dirs['materials_dir'] / "grass_material.tres"
        with open(grass_material_file, 'w') as f:
            f.write(grass_material)
        material_files.append("grass_material.tres")
        
        # Water material
        water_material = '''[gd_resource type="StandardMaterial3D" format=3]

[resource]
albedo_color = Color(0.2, 0.4, 0.8, 0.7)
transparency = 1
roughness = 0.1
metallic = 0.0
'''
        
        water_material_file = self.dirs['materials_dir'] / "water_material.tres"
        with open(water_material_file, 'w') as f:
            f.write(water_material)
        material_files.append("water_material.tres")
        
        return material_files
    
    async def _copy_pipeline_assets(self, assets: Dict[str, Any]) -> List[str]:
        """Copy assets from the pipeline output"""
        copied_files = []
        
        # This would copy actual 3D models, textures, etc. from the pipeline
        # For now, create placeholder information
        
        asset_info = {
            "pipeline_assets": assets,
            "note": "3D models and textures from the multi-agent pipeline would be copied here",
            "supported_formats": [".obj", ".fbx", ".gltf", ".png", ".jpg"],
            "conversion_needed": "Some formats may need conversion to Godot-compatible formats"
        }
        
        asset_info_file = self.assets_dir / "pipeline_assets_info.json"
        with open(asset_info_file, 'w') as f:
            json.dump(asset_info, f, indent=2)
        
        copied_files.append("pipeline_assets_info.json")
        
        # TODO: Implement actual asset copying and conversion
        # This would involve:
        # 1. Converting .obj files to .tres mesh resources
        # 2. Converting textures to Godot-compatible formats
        # 3. Creating material resources that reference the textures
        # 4. Setting up proper import settings
        
        return copied_files
    
    async def _create_character_resources(self, characters: Dict[str, Any]) -> List[str]:
        """Create character-specific resources"""
        resource_files = []
        
        if 'characters' in characters:
            for i, character in enumerate(characters['characters']):
                char_resource = await self._create_character_resource(character, i)
                if char_resource:
                    resource_files.append(char_resource)
        
        return resource_files
    
    async def _create_character_resource(self, character: Dict[str, Any], index: int) -> str:
        """Create a character resource file"""
        
        character_name = character.get('name', f'Character_{index}')
        safe_name = character_name.replace(' ', '_').replace("'", "")
        
        # Create character resource
        char_resource = f'''[gd_resource type="Resource" format=3]

[resource]
script = preload("res://scripts/CharacterData.gd")
character_name = "{character_name}"
personality = {character.get("personality", {})}
dialogue_lines = {character.get("dialogue", [])}
relationships = {character.get("relationships", {})}
'''
        
        char_resource_file = self.resources_dir / f"{safe_name}_data.tres"
        with open(char_resource_file, 'w') as f:
            f.write(char_resource)
        
        return f"{safe_name}_data.tres"
    
    async def create_autoload_configuration(self) -> str:
        """Create autoload script for global game data"""
        
        autoload_content = '''extends Node

# Global game data autoload

var world_data: Dictionary = {}
var character_data: Dictionary = {}
var quest_data: Dictionary = {}
var game_config: Dictionary = {}

func _ready():
    load_all_data()

func load_all_data():
    world_data = load_json_file("res://data/world_spec.json")
    character_data = load_json_file("res://data/characters.json")
    quest_data = load_json_file("res://data/quests.json")
    game_config = load_json_file("res://data/game_config.json")
    
    print("Global data loaded successfully")

func load_json_file(file_path: String) -> Dictionary:
    var file = FileAccess.open(file_path, FileAccess.READ)
    if file:
        var json_string = file.get_as_text()
        file.close()
        
        var json = JSON.new()
        var parse_result = json.parse(json_string)
        if parse_result == OK:
            return json.data
        else:
            print("Error parsing JSON file: ", file_path)
    else:
        print("Could not open file: ", file_path)
    
    return {}

func get_character_by_name(name: String) -> Dictionary:
    if character_data.has("characters"):
        for character in character_data["characters"]:
            if character.get("name") == name:
                return character
    return {}

func get_quest_by_id(quest_id: String) -> Dictionary:
    if quest_data.has("quests"):
        for quest in quest_data["quests"]:
            if quest.get("id") == quest_id:
                return quest
    return {}
'''
        
        autoload_file = self.dirs['scripts_dir'] / "GlobalData.gd"
        with open(autoload_file, 'w') as f:
            f.write(autoload_content)
        
        return "GlobalData.gd"