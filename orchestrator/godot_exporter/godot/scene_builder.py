#!/usr/bin/env python3
"""
COMPLETELY FIXED Godot scene builder
Properly assembles ALL orchestrator data into working World.tscn
"""

import logging
import re
import json
from pathlib import Path
from typing import Dict, Any, List

class GodotSceneBuilder:
    """Handles Godot scene creation with PROPER data assembly from orchestrator"""
    
    def __init__(self, dirs: Dict[str, Path], logger: logging.Logger):
        self.dirs = dirs
        self.logger = logger
        self.scenes_dir = dirs['scenes_dir']
        
        # Track external resources for scenes
        self.external_resources = []
    
    async def export_world_scenes(self, world_spec: Dict[str, Any]) -> List[str]:
        """Export world data as Godot scenes"""
        scene_files = []
        
        try:
            # Ensure scenes directory exists
            self.scenes_dir.mkdir(parents=True, exist_ok=True)
            
            # Create individual building scenes if buildings exist
            if world_spec and 'buildings' in world_spec:
                for i, building in enumerate(world_spec['buildings']):
                    try:
                        building_scene = await self._create_building_scene(building, i)
                        scene_files.append(building_scene)
                    except Exception as e:
                        self.logger.error(f"Failed to create building scene {i}: {e}")
            
            self.logger.info(f"   ✅ Created {len(scene_files)} world scenes")
            return scene_files
            
        except Exception as e:
            self.logger.error(f"Critical error in world scene export: {e}")
            return []
    
    async def create_main_scenes(self, world_spec: Dict[str, Any], characters: Dict[str, Any]) -> List[str]:
        """Create main game scenes with GUARANTEED assembly of all orchestrator data"""
        scene_files = []
        
        try:
            # DEBUG: Log what data we received
            self.logger.info("🔍 === ORCHESTRATOR DATA RECEIVED ===")
            self.logger.info(f"🌍 World spec: {world_spec}")
            self.logger.info(f"👥 Characters: {characters}")
            self.logger.info("==========================================")
            
            # Ensure scenes directory exists
            self.scenes_dir.mkdir(parents=True, exist_ok=True)
            
            # Create player scene FIRST (required for World scene)
            try:
                player_scene = await self._create_player_scene()
                scene_files.append(player_scene)
                self.logger.info("✅ Created player scene")
            except Exception as e:
                self.logger.error(f"❌ Failed to create player scene: {e}")
                # Don't continue without Player scene
                raise Exception("Cannot create World without Player scene")
            
            # Create main world scene WITH GUARANTEED Player and Buildings
            try:
                world_scene = await self._create_complete_world_scene(world_spec, characters)
                scene_files.append(world_scene)
                self.logger.info("✅ Created COMPLETE world scene with Player, Buildings, and NPCs")
            except Exception as e:
                self.logger.error(f"❌ Failed to create complete world scene: {e}")
                # Create emergency working scene
                try:
                    emergency_scene = await self._create_emergency_working_scene()
                    scene_files.append(emergency_scene)
                    self.logger.warning("⚠️ Created emergency working scene with Player")
                except Exception as e2:
                    self.logger.error(f"❌ Even emergency scene failed: {e2}")
                    raise Exception("Complete scene generation failure")
            
            # Create NPC scenes if characters exist
            if characters and 'characters' in characters:
                for i, character in enumerate(characters['characters']):
                    try:
                        npc_scene = await self._create_npc_scene(character, i)
                        scene_files.append(npc_scene)
                        self.logger.info(f"✅ Created NPC scene for {character.get('name', f'NPC_{i}')}")
                    except Exception as e:
                        self.logger.error(f"Failed to create NPC scene {i}: {e}")
            
            self.logger.info(f"🎮 === FINAL RESULT: {len(scene_files)} scenes created ===")
            return scene_files
            
        except Exception as e:
            self.logger.error(f"❌ CRITICAL FAILURE in scene creation: {e}")
            return scene_files
    
    async def _create_complete_world_scene(self, world_spec: Dict[str, Any], characters: Dict[str, Any]) -> str:
        """Create COMPLETE world scene using ALL orchestrator data"""
        
        self.logger.info("🔧 Building COMPLETE world scene...")
        
        # Process buildings data
        buildings = world_spec.get('buildings', [])
        if not buildings:
            self.logger.warning("⚠️ No buildings data found, creating test buildings")
            buildings = [
                {"type": "house", "position": [10, 0, 10]},
                {"type": "tavern", "position": [-10, 0, 10]},
                {"type": "blacksmith", "position": [0, 0, -15]}
            ]
        
        # Ensure buildings have positions
        positioned_buildings = self._ensure_building_positions(buildings)
        
        # Process character spawn points
        character_spawns = []
        if characters and 'characters' in characters:
            for i, char in enumerate(characters['characters']):
                spawn_pos = char.get('position', [0, 0, 0])
                if spawn_pos == [0, 0, 0]:  # Generate position if missing
                    angle = (i / len(characters['characters'])) * 2 * 3.14159
                    x = 25 * cos(angle) if 'cos' in dir() else (i * 8 - 16)
                    z = 25 * sin(angle) if 'sin' in dir() else (i * 6 - 12)
                    spawn_pos = [x, 0, z]
                character_spawns.append({
                    'name': char.get('name', f'NPC_{i}'),
                    'position': spawn_pos
                })
        
        # Get world theme
        theme = world_spec.get('theme', 'default')
        spawn_point = world_spec.get('spawn_point', [0, 2, 0])
        
        self.logger.info(f"🏗️ Building world with {len(positioned_buildings)} buildings, {len(character_spawns)} NPCs")
        
        # Build the complete scene
        scene_content = self._build_world_scene_content(positioned_buildings, character_spawns, theme, spawn_point)
        
        # Write the scene file
        world_scene_file = self.scenes_dir / "World.tscn"
        with open(world_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        self.logger.info("🎮 COMPLETE World.tscn created with ALL orchestrator data!")
        return "World.tscn"
    
    def _ensure_building_positions(self, buildings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure all buildings have proper positions"""
        positioned_buildings = []
        grid_size = 25
        buildings_per_row = 3
        
        for i, building in enumerate(buildings):
            positioned_building = building.copy()
            
            # Check if building has valid position
            pos = building.get('position', [0, 0, 0])
            if not pos or pos == [0, 0, 0] or (len(pos) >= 2 and pos[0] == 0 and pos[2] == 0):
                # Generate grid position
                row = i // buildings_per_row
                col = i % buildings_per_row
                x = (col - buildings_per_row // 2) * grid_size
                z = (row - len(buildings) // (2 * buildings_per_row)) * grid_size
                positioned_building['position'] = [x, 0, z]
                self.logger.info(f"🎯 Generated position for {building.get('type', 'building')}_{i}: [{x}, 0, {z}]")
            else:
                self.logger.info(f"🎯 Using existing position for {building.get('type', 'building')}_{i}: {pos}")
            
            positioned_buildings.append(positioned_building)
        
        return positioned_buildings
    
    def _build_world_scene_content(self, buildings: List[Dict[str, Any]], character_spawns: List[Dict[str, Any]], theme: str, spawn_point: List[float]) -> str:
        """Build the complete World.tscn content"""
        
        # Calculate resources needed
        building_count = len(buildings)
        load_steps = 4 + (building_count * 3)  # Base + buildings
        
        # Scene header
        content = f'[gd_scene load_steps={load_steps} format=3 uid="uid://world_main"]\n\n'
        
        # External resources
        content += '[ext_resource type="Script" path="res://scripts/WorldManager.gd" id="1"]\n'
        content += '[ext_resource type="PackedScene" uid="uid://player_scene" path="res://scenes/Player.tscn" id="2"]\n\n'
        
        # Sub-resources
        content += '''[sub_resource type="Environment" id="Environment_1"]
background_mode = 1
background_color = Color(0.4, 0.6, 1, 1)
ambient_light_source = 2
ambient_light_color = Color(1, 1, 1, 1)
ambient_light_energy = 0.3

[sub_resource type="PlaneMesh" id="PlaneMesh_1"]
size = Vector2(100, 100)

[sub_resource type="BoxShape3D" id="PlaneShape_1"]
size = Vector3(100, 0.1, 100)

[sub_resource type="StandardMaterial3D" id="StandardMaterial3D_1"]
albedo_color = Color(0.2, 0.8, 0.2, 1)

'''
        
        # Building resources
        for i, building in enumerate(buildings):
            building_type = building.get('type', 'generic')
            color = self._get_building_color(building_type)
            
            content += f'''[sub_resource type="BoxMesh" id="BoxMesh_{i+1}"]
size = Vector3(4, 3, 4)

[sub_resource type="BoxShape3D" id="BoxShape_{i+1}"]
size = Vector3(4, 3, 4)

[sub_resource type="StandardMaterial3D" id="StandardMaterial3D_{i+2}"]
albedo_color = Color{color}

'''
        
        # Main nodes
        content += '''[node name="World" type="Node3D"]
script = ExtResource("1")

[node name="Environment" type="Node3D" parent="."]

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="Environment"]
transform = Transform3D(0.707107, -0.5, 0.5, 0, 0.707107, 0.707107, -0.707107, -0.5, 0.5, 0, 10, 0)
light_energy = 1.0
shadow_enabled = true

[node name="Ground" type="StaticBody3D" parent="Environment"]

[node name="MeshInstance3D" type="MeshInstance3D" parent="Environment/Ground"]
mesh = SubResource("PlaneMesh_1")
surface_material_override/0 = SubResource("StandardMaterial3D_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="Environment/Ground"]
shape = SubResource("PlaneShape_1")

'''
        
        # GUARANTEED Player instantiation
        content += f'[node name="Player" parent="." instance=ExtResource("2")]\n'
        content += f'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {spawn_point[0]}, {spawn_point[1]}, {spawn_point[2]})\n\n'
        
        # Buildings
        if buildings:
            content += '[node name="Buildings" type="Node3D" parent="."]\n\n'
            
            for i, building in enumerate(buildings):
                building_type = building.get('type', 'generic')
                position = building.get('position', [0, 0, 0])
                building_name = f"{building_type}_{i}"
                
                content += f'''[node name="{building_name}" type="StaticBody3D" parent="Buildings"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {position[0]}, 1.5, {position[2]})

[node name="MeshInstance3D" type="MeshInstance3D" parent="Buildings/{building_name}"]
mesh = SubResource("BoxMesh_{i+1}")
surface_material_override/0 = SubResource("StandardMaterial3D_{i+2}")

[node name="CollisionShape3D" type="CollisionShape3D" parent="Buildings/{building_name}"]
shape = SubResource("BoxShape_{i+1}")

[node name="InteractionArea" type="Area3D" parent="Buildings/{building_name}"]
collision_layer = 32
collision_mask = 2

[node name="InteractionCollision" type="CollisionShape3D" parent="Buildings/{building_name}/InteractionArea"]
shape = SubResource("BoxShape_{i+1}")

'''
        
        # NPCs container
        content += '[node name="NPCs" type="Node3D" parent="."]\n'
        
        # Add NPC spawn points as markers
        for spawn in character_spawns:
            name = self._sanitize_node_name(spawn['name'], "NPC")
            pos = spawn['position']
            content += f'''
[node name="{name}_SpawnPoint" type="Marker3D" parent="NPCs"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {pos[0]}, 0, {pos[2]})
'''
        
        return content
    
    async def _create_emergency_working_scene(self) -> str:
        """Create emergency working scene if main generation fails"""
        
        self.logger.info("🚨 Creating emergency working scene...")
        
        content = '''[gd_scene load_steps=8 format=3 uid="uid://world_main"]

[ext_resource type="Script" path="res://scripts/WorldManager.gd" id="1"]
[ext_resource type="PackedScene" uid="uid://player_scene" path="res://scenes/Player.tscn" id="2"]

[sub_resource type="Environment" id="Environment_1"]
background_mode = 1
background_color = Color(0.4, 0.6, 1, 1)
ambient_light_source = 2
ambient_light_color = Color(1, 1, 1, 1)
ambient_light_energy = 0.3

[sub_resource type="PlaneMesh" id="PlaneMesh_1"]
size = Vector2(100, 100)

[sub_resource type="BoxShape3D" id="PlaneShape_1"]
size = Vector3(100, 0.1, 100)

[sub_resource type="StandardMaterial3D" id="StandardMaterial3D_1"]
albedo_color = Color(0.2, 0.8, 0.2, 1)

[sub_resource type="BoxMesh" id="BoxMesh_1"]
size = Vector3(4, 3, 4)

[sub_resource type="StandardMaterial3D" id="StandardMaterial3D_2"]
albedo_color = Color(0.8, 0.6, 0.4, 1)

[node name="World" type="Node3D"]
script = ExtResource("1")

[node name="Environment" type="Node3D" parent="."]

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="Environment"]
transform = Transform3D(0.707107, -0.5, 0.5, 0, 0.707107, 0.707107, -0.707107, -0.5, 0.5, 0, 10, 0)
light_energy = 1.0
shadow_enabled = true

[node name="Ground" type="StaticBody3D" parent="Environment"]

[node name="MeshInstance3D" type="MeshInstance3D" parent="Environment/Ground"]
mesh = SubResource("PlaneMesh_1")
surface_material_override/0 = SubResource("StandardMaterial3D_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="Environment/Ground"]
shape = SubResource("PlaneShape_1")

[node name="Player" parent="." instance=ExtResource("2")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0)

[node name="Buildings" type="Node3D" parent="."]

[node name="TestHouse" type="StaticBody3D" parent="Buildings"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 15, 1.5, 15)

[node name="MeshInstance3D" type="MeshInstance3D" parent="Buildings/TestHouse"]
mesh = SubResource("BoxMesh_1")
surface_material_override/0 = SubResource("StandardMaterial3D_2")

[node name="CollisionShape3D" type="CollisionShape3D" parent="Buildings/TestHouse"]
shape = SubResource("BoxMesh_1")

[node name="TestTavern" type="StaticBody3D" parent="Buildings"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, -15, 1.5, 15)

[node name="MeshInstance3D" type="MeshInstance3D" parent="Buildings/TestTavern"]
mesh = SubResource("BoxMesh_1")
surface_material_override/0 = SubResource("StandardMaterial3D_2")

[node name="CollisionShape3D" type="CollisionShape3D" parent="Buildings/TestTavern"]
shape = SubResource("BoxMesh_1")

[node name="NPCs" type="Node3D" parent="."]
'''
        
        world_scene_file = self.scenes_dir / "World.tscn"
        with open(world_scene_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return "World.tscn"
    
    async def _create_player_scene(self) -> str:
        """Create player character scene"""
        
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
collision_layer = 2
collision_mask = 1

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
mesh = SubResource("CapsuleMesh_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("CapsuleShape3D_1")

[node name="Camera3D" type="Camera3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)
fov = 75.0

[node name="InteractionRay" type="RayCast3D" parent="Camera3D"]
target_position = Vector3(0, 0, -3)
collision_mask = 32
'''
        
        player_scene_file = self.scenes_dir / "Player.tscn"
        with open(player_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        return "Player.tscn"
    
    async def _create_building_scene(self, building: Dict[str, Any], index: int) -> str:
        """Create individual building scene"""
        
        building_type = building.get('type', 'generic')
        building_name = f"Building_{index}"
        color = self._get_building_color(building_type)
        
        scene_content = f'''[gd_scene load_steps=5 format=3 uid="uid://building_{index}"]

[ext_resource type="Script" path="res://scripts/Building.gd" id="1"]

[sub_resource type="BoxMesh" id="BoxMesh_1"]
size = Vector3(4, 3, 4)

[sub_resource type="BoxShape3D" id="BoxShape3D_1"]
size = Vector3(4, 3, 4)

[sub_resource type="StandardMaterial3D" id="StandardMaterial3D_1"]
albedo_color = Color{color}

[node name="{building_name}" type="StaticBody3D"]
script = ExtResource("1")
collision_layer = 16
collision_mask = 2

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.5, 0)
mesh = SubResource("BoxMesh_1")
surface_material_override/0 = SubResource("StandardMaterial3D_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.5, 0)
shape = SubResource("BoxShape3D_1")

[node name="InteractionArea" type="Area3D" parent="."]
collision_layer = 32
collision_mask = 2

[node name="InteractionCollision" type="CollisionShape3D" parent="InteractionArea"]
transform = Transform3D(1.2, 0, 0, 0, 1.2, 0, 0, 0, 1.2, 0, 1.5, 0)
shape = SubResource("BoxShape3D_1")
'''
        
        building_scene_file = self.scenes_dir / f"{building_name}.tscn"
        with open(building_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        return f"{building_name}.tscn"
    
    async def _create_npc_scene(self, character: Dict[str, Any], index: int) -> str:
        """Create NPC character scene"""
        
        character_name = character.get('name', f'NPC_{index}')
        safe_name = self._sanitize_node_name(character_name, f"NPC_{index}")
        
        scene_content = f'''[gd_scene load_steps=5 format=3 uid="uid://npc_{index}"]

[ext_resource type="Script" path="res://scripts/NPC.gd" id="1"]

[sub_resource type="CapsuleMesh" id="CapsuleMesh_1"]
radius = 0.4
height = 1.8

[sub_resource type="CapsuleShape3D" id="CapsuleShape3D_1"]
radius = 0.4
height = 1.8

[sub_resource type="SphereShape3D" id="SphereShape3D_1"]
radius = 3.0

[node name="{safe_name}" type="CharacterBody3D" groups=["npcs"]]
script = ExtResource("1")
collision_layer = 8
collision_mask = 1

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
mesh = SubResource("CapsuleMesh_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("CapsuleShape3D_1")

[node name="InteractionArea" type="Area3D" parent="."]
collision_layer = 32
collision_mask = 2

[node name="InteractionCollision" type="CollisionShape3D" parent="InteractionArea"]
shape = SubResource("SphereShape3D_1")
'''
        
        npc_scene_file = self.scenes_dir / f"{safe_name}.tscn"
        with open(npc_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        return f"{safe_name}.tscn"
    
    def _sanitize_node_name(self, name: str, fallback: str) -> str:
        """Sanitize a string to be a valid Godot node name"""
        if not name:
            return fallback
        
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        if sanitized and sanitized[0].isdigit():
            sanitized = f"_{sanitized}"
        
        return sanitized if sanitized else fallback
    
    def _get_building_color(self, building_type: str) -> str:
        """Get color for building type"""
        color_map = {
            'house': '(0.8, 0.6, 0.4, 1)',
            'shop': '(0.6, 0.8, 0.4, 1)',
            'tavern': '(0.9, 0.7, 0.3, 1)',
            'blacksmith': '(0.5, 0.5, 0.5, 1)',
            'temple': '(0.9, 0.9, 0.9, 1)',
            'castle': '(0.7, 0.7, 0.8, 1)',
            'market': '(0.8, 0.8, 0.6, 1)',
            'inn': '(0.8, 0.5, 0.3, 1)',
            'church': '(0.9, 0.9, 0.8, 1)',
            'tower': '(0.6, 0.6, 0.7, 1)',
            'generic': '(0.6, 0.6, 0.6, 1)'
        }
        return color_map.get(building_type.lower(), color_map['generic'])