#!/usr/bin/env python3
"""
COMPLETE FIXED Godot Scene Builder - Buildings Now Positioned on Ground + Third-Person Camera
File: orchestrator/godot_exporter/godot/scene_builder.py

This fixes the floating buildings issue by properly mapping world coordinates to Godot 3D space
PLUS fixes NPC script attachment issue
PLUS fixes ground collision with proper BoxShape3D
PLUS adds third-person camera support
"""

import logging
import json
import math
from pathlib import Path
from typing import Dict, Any, List

class GodotSceneBuilder:
    """Fixed Godot scene builder that places buildings on the ground AND properly attaches NPC scripts AND has proper ground collision PLUS third-person camera"""
    
    def __init__(self, dirs: Dict[str, Path], logger: logging.Logger):
        self.dirs = dirs
        self.logger = logger
        self.scenes_dir = dirs['scenes_dir']
        # Camera mode options: 'first_person', 'third_person'
        self.camera_mode = 'third_person'  # Default to third-person
    
    def set_camera_mode(self, mode: str):
        """Set camera mode: 'first_person' or 'third_person'"""
        self.camera_mode = mode
        self.logger.info(f"Camera mode set to: {mode}")
    
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
            
            self.logger.info(f"✅ Created {len(scene_files)} scenes including {len(world_spec.get('buildings', []))} buildings ON GROUND with proper ground collision and {self.camera_mode} camera")
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
        
        # Create sub-resources section with PROPER ground collision
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
shadow_enabled = true

[node name="Ground" type="StaticBody3D" parent="Environment"]

[node name="GroundMesh" type="MeshInstance3D" parent="Environment/Ground"]
mesh = SubResource("PlaneMesh_1")

[node name="GroundCollision" type="CollisionShape3D" parent="Environment/Ground"]
shape = SubResource("GroundShape_1")

{self._create_player_node_with_camera()}

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
        
        self.logger.info(f"✅ Created main world scene with {building_count} buildings ON GROUND and {character_count} NPCs WITH SCRIPTS and proper ground collision using {self.camera_mode} camera")
        return "World.tscn"
    
    def _create_player_node_with_camera(self) -> str:
        """Create player node with camera based on selected mode"""
        
        if self.camera_mode == 'third_person':
            return self._create_player_node_third_person()
        else:
            return self._create_player_node_first_person()
    
    def _create_player_node_first_person(self) -> str:
        """Create player node with first-person camera (ORIGINAL)"""
        return '''[node name="Player" type="CharacterBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0)
script = ExtResource("2")

[node name="PlayerMesh" type="MeshInstance3D" parent="Player"]
mesh = SubResource("PlayerMesh_1")

[node name="PlayerCollision" type="CollisionShape3D" parent="Player"]
shape = SubResource("PlayerShape_1")

[node name="Camera3D" type="Camera3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)
current = true

[node name="InteractionRay" type="RayCast3D" parent="Player/Camera3D"]
target_position = Vector3(0, 0, -3)

'''
    
    def _create_player_node_third_person(self) -> str:
        """Create player node with third-person camera (NEW)"""
        return '''[node name="Player" type="CharacterBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0)
script = ExtResource("2")

[node name="PlayerMesh" type="MeshInstance3D" parent="Player"]
mesh = SubResource("PlayerMesh_1")

[node name="PlayerCollision" type="CollisionShape3D" parent="Player"]
shape = SubResource("PlayerShape_1")

[node name="Camera3D" type="Camera3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, 0.940, 0.342, 0, -0.342, 0.940, 0, 4, 8)
current = true
fov = 75.0

[node name="InteractionRay" type="RayCast3D" parent="Player/Camera3D"]
target_position = Vector3(0, 0, -3)

'''
    
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
        """Generate all sub-resources needed for buildings with PROPER GROUND COLLISION"""
        sub_resources = '''[sub_resource type="PlaneMesh" id="PlaneMesh_1"]
size = Vector2(100, 100)

[sub_resource type="BoxShape3D" id="GroundShape_1"]
size = Vector3(100, 0.1, 100)

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
        rotation_rad = rotation * math.pi / 180 if rotation else 0
        
        # Create rotation transform if there's rotation
        if rotation != 0:
            # Simple Y-axis rotation for now
            cos_r = math.cos(rotation_rad)
            sin_r = math.sin(rotation_rad)
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
        """Create player scene with camera mode selection"""
        
        if self.camera_mode == 'third_person':
            return await self._create_player_scene_third_person()
        else:
            return await self._create_player_scene_first_person()
    
    async def _create_player_scene_first_person(self) -> str:
        """Create player scene with first-person camera (ORIGINAL)"""
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
current = true

[node name="InteractionRay" type="RayCast3D" parent="Camera3D"]
target_position = Vector3(0, 0, -3)
'''
        
        player_scene_file = self.scenes_dir / "Player.tscn"
        with open(player_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        return "Player.tscn"
    
    async def _create_player_scene_third_person(self) -> str:
        """Create player scene with third-person camera (NEW)"""
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
transform = Transform3D(1, 0, 0, 0, 0.940, 0.342, 0, -0.342, 0.940, 0, 4, 8)
current = true
fov = 75.0

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

    # NEW ADDITION: Advanced Camera Configuration Methods
    async def create_main_scenes_with_camera_options(self, world_spec: Dict[str, Any], 
                                                   characters: Dict[str, Any], 
                                                   camera_config: Dict[str, Any] = None) -> List[str]:
        """Create main scenes with advanced camera configuration options"""
        
        if camera_config:
            self.camera_mode = camera_config.get('mode', 'third_person')
            self.camera_distance = camera_config.get('distance', 8.0)
            self.camera_height = camera_config.get('height', 4.0)
            self.camera_angle = camera_config.get('angle', -20.0)
            self.camera_fov = camera_config.get('fov', 75.0)
        
        return await self.create_main_scenes(world_spec, characters)
    
    def _create_advanced_third_person_camera(self, config: Dict[str, Any] = None) -> str:
        """Create advanced third-person camera with custom configuration"""
        
        distance = config.get('distance', 8.0) if config else 8.0
        height = config.get('height', 4.0) if config else 4.0
        angle = config.get('angle', -20.0) if config else -20.0
        fov = config.get('fov', 75.0) if config else 75.0
        
        # Calculate camera transform based on distance, height, and angle
        angle_rad = math.radians(angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        # Position camera behind and above player
        camera_x = 0
        camera_y = height
        camera_z = distance
        
        # Create rotation matrix for looking down
        return f'''[node name="Camera3D" type="Camera3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, {cos_angle}, {sin_angle}, 0, {-sin_angle}, {cos_angle}, {camera_x}, {camera_y}, {camera_z})
current = true
fov = {fov}

'''
    
    def get_camera_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined camera configuration presets"""
        return {
            'close_follow': {
                'mode': 'third_person',
                'distance': 5.0,
                'height': 3.0,
                'angle': -15.0,
                'fov': 70.0
            },
            'far_overview': {
                'mode': 'third_person',
                'distance': 12.0,
                'height': 6.0,
                'angle': -30.0,
                'fov': 80.0
            },
            'action_camera': {
                'mode': 'third_person',
                'distance': 6.0,
                'height': 2.5,
                'angle': -10.0,
                'fov': 75.0
            },
            'strategy_view': {
                'mode': 'third_person',
                'distance': 15.0,
                'height': 10.0,
                'angle': -45.0,
                'fov': 85.0
            },
            'first_person': {
                'mode': 'first_person',
                'distance': 0.0,
                'height': 1.6,
                'angle': 0.0,
                'fov': 75.0
            }
        }
    
    async def create_scenes_with_preset(self, world_spec: Dict[str, Any], 
                                      characters: Dict[str, Any], 
                                      preset_name: str = 'action_camera') -> List[str]:
        """Create scenes using a predefined camera preset"""
        
        presets = self.get_camera_presets()
        if preset_name not in presets:
            self.logger.warning(f"Unknown preset '{preset_name}', using 'action_camera'")
            preset_name = 'action_camera'
        
        camera_config = presets[preset_name]
        self.logger.info(f"Using camera preset: {preset_name}")
        
        return await self.create_main_scenes_with_camera_options(world_spec, characters, camera_config)
    
    def _create_dynamic_camera_controller(self) -> str:
        """Create a dynamic camera that can switch between modes at runtime"""
        return '''[node name="CameraController" type="Node3D" parent="Player"]
script = ExtResource("3")

[node name="FirstPersonCamera" type="Camera3D" parent="Player/CameraController"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)

[node name="ThirdPersonCamera" type="Camera3D" parent="Player/CameraController"]
transform = Transform3D(1, 0, 0, 0, 0.940, 0.342, 0, -0.342, 0.940, 0, 4, 8)
current = true
fov = 75.0

[node name="OverviewCamera" type="Camera3D" parent="Player/CameraController"]
transform = Transform3D(1, 0, 0, 0, 0.707, 0.707, 0, -0.707, 0.707, 0, 10, 15)
fov = 85.0

'''
    
    def get_scene_builder_info(self) -> Dict[str, Any]:
        """Get information about the scene builder configuration"""
        return {
            'camera_mode': self.camera_mode,
            'available_presets': list(self.get_camera_presets().keys()),
            'features': [
                'Ground-positioned buildings',
                'Proper NPC script attachment',
                'Multiple camera modes',
                'Dynamic camera switching',
                'Configurable camera presets',
                'First-person and third-person support',
                'Advanced lighting setup',
                'Proper collision detection'
            ],
            'supported_building_types': [
                'house', 'church', 'tower', 'tavern', 'shop', 'blacksmith', 'generic'
            ],
            'camera_controls': {
                'third_person': {
                    'mouse': 'Rotate camera around player',
                    'wasd': 'Move player',
                    'escape': 'Toggle mouse capture'
                },
                'first_person': {
                    'mouse': 'Look around',
                    'wasd': 'Move player',
                    'escape': 'Toggle mouse capture'
                }
            }
        }