#!/usr/bin/env python3
"""
Godot scene builder
Handles creation of Godot scene files (.tscn)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from ..core.data_types import GodotScene, GodotNode, GODOT_NODE_TEMPLATES

class GodotSceneBuilder:
    """Handles Godot scene creation"""
    
    def __init__(self, dirs: Dict[str, Path], logger: logging.Logger):
        self.dirs = dirs
        self.logger = logger
        self.scenes_dir = dirs['scenes_dir']
        
        # Track external resources for scenes
        self.external_resources = []
    
    async def export_world_scenes(self, world_spec: Dict[str, Any]) -> List[str]:
        """Export world data as Godot scenes"""
        scene_files = []
        
        # Create individual building scenes if buildings exist
        if world_spec and 'buildings' in world_spec:
            for i, building in enumerate(world_spec['buildings']):
                building_scene = await self._create_building_scene(building, i)
                scene_files.append(building_scene)
        
        self.logger.info(f"   ✅ Created {len(scene_files)} world scenes")
        return scene_files
    
    async def create_main_scenes(self, world_spec: Dict[str, Any], characters: Dict[str, Any]) -> List[str]:
        """Create main game scenes"""
        scene_files = []
        
        # Create main world scene
        world_scene = await self._create_main_world_scene(world_spec)
        scene_files.append(world_scene)
        
        # Create player scene
        player_scene = await self._create_player_scene()
        scene_files.append(player_scene)
        
        # Create NPC scenes if characters exist
        if characters and 'characters' in characters:
            for i, character in enumerate(characters['characters']):
                npc_scene = await self._create_npc_scene(character, i)
                scene_files.append(npc_scene)
        
        self.logger.info(f"   ✅ Created {len(scene_files)} main scenes")
        return scene_files
    
    async def _create_main_world_scene(self, world_spec: Dict[str, Any]) -> str:
        """Create the main world scene"""
        
        # Start building the scene content
        scene_content = '[gd_scene load_steps=5 format=3]\n\n'
        
        # External resources
        scene_content += '[ext_resource type="Script" path="res://scripts/WorldManager.gd" id="1"]\n'
        scene_content += '[ext_resource type="PackedScene" path="res://scenes/Player.tscn" id="2"]\n'
        
        # Sub-resources for environment
        scene_content += '''
[sub_resource type="Environment" id="Environment_1"]
background_mode = 1
background_color = Color(0.4, 0.6, 1, 1)
ambient_light_source = 2
ambient_light_color = Color(1, 1, 1, 1)
ambient_light_energy = 0.3

[sub_resource type="PlaneMesh" id="PlaneMesh_1"]
size = Vector2(100, 100)

[sub_resource type="StandardMaterial3D" id="StandardMaterial3D_1"]
albedo_color = Color(0.2, 0.8, 0.2, 1)

'''
        
        # Main world node
        scene_content += '[node name="World" type="Node3D"]\n'
        scene_content += 'script = ExtResource("1")\n\n'
        
        # Environment setup
        scene_content += '[node name="Environment" type="Node3D" parent="."]\n\n'
        
        scene_content += '[node name="DirectionalLight3D" type="DirectionalLight3D" parent="Environment"]\n'
        scene_content += 'transform = Transform3D(0.707107, -0.5, 0.5, 0, 0.707107, 0.707107, -0.707107, -0.5, 0.5, 0, 10, 0)\n'
        scene_content += 'light_energy = 1.0\n'
        scene_content += 'shadow_enabled = true\n\n'
        
        # Ground plane
        scene_content += '[node name="Ground" type="MeshInstance3D" parent="Environment"]\n'
        scene_content += 'mesh = SubResource("PlaneMesh_1")\n'
        scene_content += 'surface_material_override/0 = SubResource("StandardMaterial3D_1")\n\n'
        
        # Player
        scene_content += '[node name="Player" parent="." instance=ExtResource("2")]\n'
        scene_content += 'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0)\n\n'
        
        # Buildings container
        scene_content += '[node name="Buildings" type="Node3D" parent="."]\n\n'
        
        # Add buildings if they exist
        if world_spec and 'buildings' in world_spec:
            for i, building in enumerate(world_spec['buildings']):
                position = building.get('position', [0, 0])
                building_type = building.get('type', 'generic')
                
                scene_content += f'[node name="Building_{i}" type="StaticBody3D" parent="Buildings"]\n'
                scene_content += f'transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {position[0]}, 0, {position[1]})\n'
                scene_content += f'metadata/building_type = "{building_type}"\n'
                scene_content += f'metadata/building_data = {building}\n\n'
                
                # Add a simple cube mesh for buildings
                scene_content += f'[node name="MeshInstance3D" type="MeshInstance3D" parent="Buildings/Building_{i}"]\n'
                scene_content += 'mesh = preload("res://assets/models/building_cube.tres")\n\n'
                
                scene_content += f'[node name="CollisionShape3D" type="CollisionShape3D" parent="Buildings/Building_{i}"]\n'
                scene_content += 'shape = preload("res://assets/models/building_collision.tres")\n\n'
        
        # NPCs container
        scene_content += '[node name="NPCs" type="Node3D" parent="."]\n\n'
        
        # Write the scene file
        world_scene_file = self.scenes_dir / "World.tscn"
        with open(world_scene_file, 'w') as f:
            f.write(scene_content)
        
        return "World.tscn"
    
    async def _create_player_scene(self) -> str:
        """Create player character scene"""
        
        scene_content = '''[gd_scene load_steps=4 format=3]

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
collision_mask = 28
'''
        
        player_scene_file = self.scenes_dir / "Player.tscn"
        with open(player_scene_file, 'w') as f:
            f.write(scene_content)
        
        return "Player.tscn"
    
    async def _create_building_scene(self, building: Dict[str, Any], index: int) -> str:
        """Create individual building scene"""
        
        building_type = building.get('type', 'generic')
        building_name = f"Building_{index}"
        
        scene_content = f'''[gd_scene load_steps=4 format=3]

[ext_resource type="Script" path="res://scripts/Building.gd" id="1"]

[sub_resource type="BoxMesh" id="BoxMesh_1"]
size = Vector3(4, 3, 4)

[sub_resource type="BoxShape3D" id="BoxShape3D_1"]
size = Vector3(4, 3, 4)

[node name="{building_name}" type="StaticBody3D"]
script = ExtResource("1")
building_type = "{building_type}"
building_data = {building}

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.5, 0)
mesh = SubResource("BoxMesh_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.5, 0)
shape = SubResource("BoxShape3D_1")
'''
        
        building_scene_file = self.scenes_dir / f"{building_name}.tscn"
        with open(building_scene_file, 'w') as f:
            f.write(scene_content)
        
        return f"{building_name}.tscn"
    
    async def _create_npc_scene(self, character: Dict[str, Any], index: int) -> str:
        """Create NPC character scene"""
        
        character_name = character.get('name', f'NPC_{index}')
        safe_name = character_name.replace(' ', '_').replace("'", "")
        
        scene_content = f'''[gd_scene load_steps=4 format=3]

[ext_resource type="Script" path="res://scripts/NPC.gd" id="1"]

[sub_resource type="CapsuleMesh" id="CapsuleMesh_1"]
radius = 0.4
height = 1.8

[sub_resource type="CapsuleShape3D" id="CapsuleShape3D_1"]
radius = 0.4
height = 1.8

[node name="{safe_name}" type="CharacterBody3D" groups=["npcs"]]
script = ExtResource("1")
character_name = "{character_name}"
character_data = {character}

[node name="MeshInstance3D" type="MeshInstance3D" parent="."]
mesh = SubResource("CapsuleMesh_1")

[node name="CollisionShape3D" type="CollisionShape3D" parent="."]
shape = SubResource("CapsuleShape3D_1")

[node name="InteractionArea" type="Area3D" parent="."]

[node name="InteractionCollision" type="CollisionShape3D" parent="InteractionArea"]
shape = SubResource("CapsuleShape3D_1")
'''
        
        npc_scene_file = self.scenes_dir / f"{safe_name}.tscn"
        with open(npc_scene_file, 'w') as f:
            f.write(scene_content)
        
        return f"{safe_name}.tscn"
    
    def _format_transform(self, position: List[float] = None, rotation: List[float] = None, scale: List[float] = None) -> str:
        """Format transform for Godot scene"""
        
        if position is None:
            position = [0, 0, 0]
        if rotation is None:
            rotation = [0, 0, 0]  # Will be converted to basis
        if scale is None:
            scale = [1, 1, 1]
        
        # For simplicity, just use identity rotation with translation
        return f"Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {position[0]}, {position[1]}, {position[2]})"