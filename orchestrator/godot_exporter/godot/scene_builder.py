#!/usr/bin/env python3
"""
COMPLETE FIXED Godot Scene Builder - Buildings Now Positioned on Ground
File: orchestrator/godot_exporter/godot/scene_builder.py

This fixes the floating buildings issue by properly mapping world coordinates to Godot 3D space
PLUS fixes NPC script attachment issue
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List

class GodotSceneBuilder:
    """Fixed Godot scene builder that places buildings on the ground AND properly attaches NPC scripts"""
    
    def __init__(self, dirs: Dict[str, Path], logger: logging.Logger):
        self.dirs = dirs
        self.logger = logger
        self.scenes_dir = dirs['scenes_dir']
    
    async def create_main_scenes(self, world_spec: Dict[str, Any], characters: Dict[str, Any]) -> List[str]:
        """Create main game scenes with ALL buildings properly positioned on ground"""
        scene_files = []
        
        try:
            # Ensure scenes directory exists
            self.scenes_dir.mkdir(parents=True, exist_ok=True)
            
            # Create main world scene with ALL buildings on ground
            world_scene = await self._create_world_scene_with_all_buildings(world_spec, characters)
            scene_files.append(world_scene)
            
            # Create player scene
            player_scene = await self._create_player_scene()
            scene_files.append(player_scene)
            
            # Create individual building scenes for each building
            if world_spec and 'buildings' in world_spec:
                for i, building in enumerate(world_spec['buildings']):
                    building_scene = await self._create_building_scene(building, i)
                    scene_files.append(building_scene)
            
            # Create NPC scenes
            if characters and 'characters' in characters:
                for i, character in enumerate(characters['characters']):
                    npc_scene = await self._create_npc_scene(character, i)
                    scene_files.append(npc_scene)
            
            self.logger.info(f"✅ Created {len(scene_files)} scenes including {len(world_spec.get('buildings', []))} buildings ON GROUND")
            return scene_files
            
        except Exception as e:
            self.logger.error(f"Critical error in scene creation: {e}")
            return []
    
    async def _create_world_scene_with_all_buildings(self, world_spec: Dict[str, Any], characters: Dict[str, Any]) -> str:
        """Create the main world scene with ALL buildings properly positioned ON THE GROUND"""
        
        buildings = world_spec.get('buildings', [])
        characters_list = characters.get('characters', []) if characters else []
        
        # Calculate how many sub-resources and ExtResources we need
        building_count = len(buildings)
        character_count = len(characters_list)
        
        # FIXED: Calculate proper load_steps including NPC scripts
        # Base: 2 (WorldManager + Player scripts) + characters scripts + subresources
        base_ext_resources = 2  # WorldManager.gd + Player.gd
        npc_ext_resources = character_count  # One script per NPC
        total_ext_resources = base_ext_resources + npc_ext_resources
        
        # SubResources: 2 (ground) + 2 (player) + (buildings * 3: mesh, shape, material)
        total_subresources = 4 + (building_count * 3)
        total_load_steps = total_ext_resources + total_subresources
        
        # FIXED: Generate ExtResource headers for ALL NPC scripts
        ext_resources = self._generate_npc_ext_resources(characters_list)
        
        # Create sub-resources section
        sub_resources = self._generate_building_subresources(buildings)
        
        # Create the scene header with FIXED ExtResource references
        scene_content = f'''[gd_scene load_steps={total_load_steps} format=3 uid="uid://world_main"]

[ext_resource type="Script" path="res://scripts/WorldManager.gd" id="1"]
[ext_resource type="Script" path="res://scripts/Player.gd" id="2"]
{ext_resources}

{sub_resources}

[node name="World" type="Node3D"]
script = ExtResource("1")

[node name="Environment" type="Node3D" parent="."]

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="Environment"]
transform = Transform3D(0.707107, -0.5, 0.5, 0, 0.707107, 0.707107, -0.707107, -0.5, 0.5, 0, 10, 0)
light_energy = 1.0

[node name="Ground" type="StaticBody3D" parent="Environment"]

[node name="GroundMesh" type="MeshInstance3D" parent="Environment/Ground"]
mesh = SubResource("PlaneMesh_1")

[node name="GroundCollision" type="CollisionShape3D" parent="Environment/Ground"]
shape = SubResource("PlaneShape_1")

[node name="Player" type="CharacterBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0)
script = ExtResource("2")

[node name="PlayerMesh" type="MeshInstance3D" parent="Player"]
mesh = SubResource("PlayerMesh_1")

[node name="PlayerCollision" type="CollisionShape3D" parent="Player"]
shape = SubResource("PlayerShape_1")

[node name="Camera3D" type="Camera3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)

[node name="InteractionRay" type="RayCast3D" parent="Player/Camera3D"]
target_position = Vector3(0, 0, -3)

[node name="Buildings" type="Node3D" parent="."]

'''
        
        # Add ALL buildings to the scene - NOW WITH GROUND POSITIONING
        for i, building in enumerate(buildings):
            building_node = self._create_building_node_on_ground(building, i)
            scene_content += building_node
        
        # Add NPCs section
        scene_content += '[node name="NPCs" type="Node3D" parent="."]\n\n'
        
        # Add ALL NPCs to the scene - FIXED: WITH PROPER SCRIPT REFERENCES
        for i, character in enumerate(characters_list):
            npc_node = self._create_npc_node_on_ground_with_script(character, i)
            scene_content += npc_node
        
        # Write the complete scene file
        world_scene_file = self.scenes_dir / "World.tscn"
        with open(world_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        self.logger.info(f"✅ Created main world scene with {building_count} buildings ON GROUND and {character_count} NPCs WITH SCRIPTS")
        return "World.tscn"
    
    def _generate_npc_ext_resources(self, characters_list: List[Dict[str, Any]]) -> str:
        """FIXED: Generate ExtResource entries for all NPC scripts"""
        ext_resources = ""
        
        for i, character in enumerate(characters_list):
            character_name = character.get('name', f'NPC_{i}')
            safe_name = self._sanitize_node_name(character_name, f"NPC_{i}")
            ext_resource_id = i + 3  # Start from 3 (1=WorldManager, 2=Player)
            
            ext_resources += f'[ext_resource type="Script" path="res://scripts/{safe_name}.gd" id="{ext_resource_id}"]\n'
        
        return ext_resources
    
    def _generate_building_subresources(self, buildings: List[Dict[str, Any]]) -> str:
        """Generate all sub-resources needed for buildings"""
        sub_resources = '''[sub_resource type="PlaneMesh" id="PlaneMesh_1"]
size = Vector2(100, 100)

[sub_resource type="PlaneShape3D" id="PlaneShape_1"]

[sub_resource type="CapsuleMesh" id="PlayerMesh_1"]
radius = 0.5
height = 2.0

[sub_resource type="CapsuleShape3D" id="PlayerShape_1"]
radius = 0.5
height = 2.0

'''
        
        # Generate mesh and material for each building
        for i, building in enumerate(buildings):
            building_type = building.get('type', 'generic')
            color = self._get_building_color(building_type)
            scale = building.get('scale', 1.0)
            
            # Create unique mesh for each building with proper size
            mesh_size = f"Vector3({4 * scale}, {3 * scale}, {4 * scale})"
            
            sub_resources += f'''[sub_resource type="BoxMesh" id="BuildingMesh_{i}"]
size = {mesh_size}

[sub_resource type="BoxShape3D" id="BuildingShape_{i}"]
size = {mesh_size}

[sub_resource type="StandardMaterial3D" id="BuildingMaterial_{i}"]
albedo_color = Color{color}
roughness = 0.7
metallic = 0.1

'''
        
        return sub_resources
    
    def _create_building_node_on_ground(self, building: Dict[str, Any], index: int) -> str:
        """Create a building node positioned ON THE GROUND - FIXED VERSION"""
        
        # Get building properties
        building_id = building.get('id', f'building_{index}')
        building_type = building.get('type', 'generic')
        position = building.get('position', {'x': 0, 'y': 0, 'z': 0})
        rotation = building.get('rotation', 0)
        scale = building.get('scale', 1.0)
        
        # Handle different position formats from world_spec
        if isinstance(position, dict):
            world_x, world_y, world_z = position.get('x', 0), position.get('y', 0), position.get('z', 0)
        elif isinstance(position, list) and len(position) >= 2:
            world_x, world_y = position[0], position[1]
            world_z = position[2] if len(position) > 2 else 0
        else:
            world_x, world_y, world_z = 0, 0, 0
        
        # CRITICAL FIX: Proper coordinate mapping for ground placement
        # In your world_spec: position.x and position.y are 2D map coordinates
        # In Godot 3D: X = left/right, Y = up/down (height), Z = forward/back (depth)
        
        godot_x = world_x           # World X maps to Godot X (left/right)
        godot_y = 1.5 * scale       # Always place on ground (building center at half-height)
        godot_z = world_y           # World Y maps to Godot Z (forward/back depth)
        
        # Convert rotation to radians if needed
        rotation_rad = rotation * 3.14159 / 180 if rotation else 0
        
        # Create rotation transform if there's rotation
        if rotation != 0:
            # Simple Y-axis rotation for now
            cos_r = cos(rotation_rad) if 'cos' in dir() else 1
            sin_r = sin(rotation_rad) if 'sin' in dir() else 0
            rotation_matrix = f"{cos_r * scale}, 0, {sin_r * scale}, 0, {scale}, 0, {-sin_r * scale}, 0, {cos_r * scale}"
        else:
            rotation_matrix = f"{scale}, 0, 0, 0, {scale}, 0, 0, 0, {scale}"
        
        # Sanitize building name for Godot
        safe_name = self._sanitize_node_name(building_id, f"Building_{index}")
        
        building_node = f'''[node name="{safe_name}" type="StaticBody3D" parent="Buildings"]
transform = Transform3D({rotation_matrix}, {godot_x}, {godot_y}, {godot_z})

[node name="BuildingMesh" type="MeshInstance3D" parent="Buildings/{safe_name}"]
mesh = SubResource("BuildingMesh_{index}")
surface_material_override/0 = SubResource("BuildingMaterial_{index}")

[node name="BuildingCollision" type="CollisionShape3D" parent="Buildings/{safe_name}"]
shape = SubResource("BuildingShape_{index}")

[node name="InteractionArea" type="Area3D" parent="Buildings/{safe_name}"]

[node name="InteractionShape" type="CollisionShape3D" parent="Buildings/{safe_name}/InteractionArea"]
transform = Transform3D(1.2, 0, 0, 0, 1.2, 0, 0, 0, 1.2, 0, 0, 0)
shape = SubResource("BuildingShape_{index}")

'''
        
        return building_node
    
    def _create_npc_node_on_ground_with_script(self, character: Dict[str, Any], index: int) -> str:
        """FIXED: Create an NPC node positioned on the ground WITH proper script reference"""
        
        character_name = character.get('name', f'NPC_{index}')
        location = character.get('location', 'house')
        safe_name = self._sanitize_node_name(character_name, f"NPC_{index}")
        
        # FIXED: Calculate correct ExtResource ID (3+ because 1=WorldManager, 2=Player)
        script_ext_resource_id = index + 3
        
        # Place NPCs at reasonable ground positions
        spawn_positions = {
            'house': (10, 1, 10),
            'church': (14, 1, 30),
            'tower': (14, 1, 10),
            'tavern': (20, 1, 20),
            'shop': (25, 1, 15)
        }
        
        x, y, z = spawn_positions.get(location, (5 + index * 3, 1, 5))
        
        # FIXED: Include script reference in the node definition
        npc_node = f'''[node name="{safe_name}" type="CharacterBody3D" parent="NPCs"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})
script = ExtResource("{script_ext_resource_id}")

[node name="NPCMesh" type="MeshInstance3D" parent="NPCs/{safe_name}"]
mesh = SubResource("PlayerMesh_1")

[node name="NPCCollision" type="CollisionShape3D" parent="NPCs/{safe_name}"]
shape = SubResource("PlayerShape_1")

'''
        
        return npc_node
    
    def _create_npc_node_on_ground(self, character: Dict[str, Any], index: int) -> str:
        """Create an NPC node positioned on the ground - ORIGINAL METHOD KEPT FOR COMPATIBILITY"""
        
        character_name = character.get('name', f'NPC_{index}')
        location = character.get('location', 'house')
        
        # Place NPCs at reasonable ground positions
        spawn_positions = {
            'house': (10, 1, 10),
            'church': (14, 1, 30),
            'tower': (14, 1, 10),
            'tavern': (20, 1, 20),
            'shop': (25, 1, 15)
        }
        
        x, y, z = spawn_positions.get(location, (5 + index * 3, 1, 5))
        safe_name = self._sanitize_node_name(character_name, f"NPC_{index}")
        
        npc_node = f'''[node name="{safe_name}" type="CharacterBody3D" parent="NPCs"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})

[node name="NPCMesh" type="MeshInstance3D" parent="NPCs/{safe_name}"]
mesh = SubResource("PlayerMesh_1")

[node name="NPCCollision" type="CollisionShape3D" parent="NPCs/{safe_name}"]
shape = SubResource("PlayerShape_1")

'''
        
        return npc_node
    
    def _get_building_color(self, building_type: str) -> str:
        """Get color for building type"""
        colors = {
            'house': '(0.8, 0.6, 0.4, 1)',      # Brown
            'church': '(0.9, 0.9, 0.9, 1)',     # White
            'tower': '(0.5, 0.5, 0.5, 1)',      # Gray
            'tavern': '(0.6, 0.4, 0.2, 1)',     # Dark brown
            'shop': '(0.4, 0.6, 0.8, 1)',       # Blue
            'blacksmith': '(0.3, 0.3, 0.3, 1)', # Dark gray
            'generic': '(0.7, 0.7, 0.7, 1)'     # Light gray
        }
        return colors.get(building_type, colors['generic'])
    
    def _sanitize_node_name(self, name: str, fallback: str) -> str:
        """Sanitize node names for Godot"""
        if not name or not isinstance(name, str):
            return fallback
        
        # Remove special characters and spaces
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
        
        return sanitized if sanitized else fallback
    
    async def _create_player_scene(self) -> str:
        """Create player scene"""
        scene_content = '''[gd_scene load_steps=4 format=3 uid="uid://player_scene"]

[ext_resource type="Script" path="res://scripts/Player.gd" id="1"]

[sub_resource type="CapsuleMesh" id="CapsuleMesh_1"]
radius = 0.5
height = 2.0

[sub_resource type="CapsuleShape3D" id="CapsuleShape3D_1"]
radius = 0.5
height = 2.0

[node name="Player" type="CharacterBody3D"]
script = ExtResource("1")

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
mesh = SubResource("CapsuleMesh_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("CapsuleShape3D_1")

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)

[node name="InteractionRay" type="RayCast3D" parent="Camera3D"]
target_position = Vector3(0, 0, -3)
'''
        
        player_scene_file = self.scenes_dir / "Player.tscn"
        with open(player_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        return "Player.tscn"
    
    async def _create_building_scene(self, building: Dict[str, Any], index: int) -> str:
        """Create individual building scene"""
        building_type = building.get('type', 'generic')
        building_name = f"Building_{building_type}_{index}"
        color = self._get_building_color(building_type)
        
        scene_content = f'''[gd_scene load_steps=4 format=3 uid="uid://building_{index}"]

[sub_resource type="BoxMesh" id="BoxMesh_1"]
size = Vector3(4, 3, 4)

[sub_resource type="BoxShape3D" id="BoxShape3D_1"]
size = Vector3(4, 3, 4)

[sub_resource type="StandardMaterial3D" id="StandardMaterial3D_1"]
albedo_color = Color{color}

[node name="{building_name}" type="StaticBody3D"]

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.5, 0)
mesh = SubResource("BoxMesh_1")
surface_material_override/0 = SubResource("StandardMaterial3D_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.5, 0)
shape = SubResource("BoxShape3D_1")
'''
        
        building_scene_file = self.scenes_dir / f"{building_name}.tscn"
        with open(building_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        return f"{building_name}.tscn"
    
    async def _create_npc_scene(self, character: Dict[str, Any], index: int) -> str:
        """Create NPC scene"""
        character_name = character.get('name', f'NPC_{index}')
        safe_name = self._sanitize_node_name(character_name, f"NPC_{index}")
        
        scene_content = f'''[gd_scene load_steps=3 format=3 uid="uid://npc_{index}"]

[sub_resource type="CapsuleMesh" id="CapsuleMesh_1"]
radius = 0.4
height = 1.8

[sub_resource type="CapsuleShape3D" id="CapsuleShape3D_1"]
radius = 0.4
height = 1.8

[node name="{safe_name}" type="CharacterBody3D" groups=["npcs"]]

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
mesh = SubResource("CapsuleMesh_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("CapsuleShape3D_1")
'''
        
        npc_scene_file = self.scenes_dir / f"{safe_name}.tscn"
        with open(npc_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        return f"{safe_name}.tscn"
    
    async def export_world_scenes(self, world_spec: Dict[str, Any]) -> List[str]:
        """Export world data as individual scenes"""
        scene_files = []
        
        if world_spec and 'buildings' in world_spec:
            for i, building in enumerate(world_spec['buildings']):
                building_scene = await self._create_building_scene(building, i)
                scene_files.append(building_scene)
        
        return scene_files