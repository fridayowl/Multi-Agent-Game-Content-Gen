#!/usr/bin/env python3
"""
FIXED Godot Scene Builder with Proper SubResource ID Management
This fixes the SubResource ID mismatch errors by ensuring all IDs are unique and sequential
"""

import logging
import json
import math
from pathlib import Path
from typing import Dict, Any, List

class GodotSceneBuilder:
    """Fixed Godot scene builder with proper SubResource ID management"""
    
    def __init__(self, dirs: Dict[str, Path], logger: logging.Logger):
        self.dirs = dirs
        self.logger = logger
        self.scenes_dir = dirs['scenes_dir']
        self.camera_mode = 'third_person'
        # Track SubResource IDs to avoid conflicts
        self.subresource_counter = 1
        self.subresource_map = {}
    
    def _get_next_subresource_id(self, resource_type: str) -> str:
        """Get next unique SubResource ID"""
        resource_id = f"{resource_type}_{self.subresource_counter}"
        self.subresource_counter += 1
        return resource_id
    
    def _reset_subresource_counter(self):
        """Reset SubResource counter for new scene"""
        self.subresource_counter = 1
        self.subresource_map = {}
    
    def set_camera_mode(self, mode: str):
        """Set camera mode: 'first_person' or 'third_person'"""
        self.camera_mode = mode
        self.logger.info(f"Camera mode set to: {mode}")
    
    async def create_main_scenes(self, world_spec: Dict[str, Any], characters: Dict[str, Any]) -> List[str]:
        """Create main game scenes with proper SubResource ID management"""
        scene_files = []
        
        try:
            self.scenes_dir.mkdir(parents=True, exist_ok=True)
            
            # Create main world scene
            world_scene = await self._create_world_scene_with_all_buildings(world_spec, characters)
            scene_files.append(world_scene)
            
            # Create player scene
            player_scene = await self._create_player_scene()
            scene_files.append(player_scene)
            
            # Create individual building scenes
            if world_spec and 'buildings' in world_spec:
                for i, building in enumerate(world_spec['buildings']):
                    building_scene = await self._create_building_scene(building, i)
                    scene_files.append(building_scene)
            
            # Create NPC scenes
            if characters and 'characters' in characters:
                for i, character in enumerate(characters['characters']):
                    npc_scene = await self._create_npc_scene(character, i)
                    scene_files.append(npc_scene)
            
            feature_count = len(world_spec.get('natural_features', []))
            self.logger.info(f"✅ Created {len(scene_files)} scenes with {feature_count} environmental features")
            return scene_files
            
        except Exception as e:
            self.logger.error(f"Critical error in scene creation: {e}")
            return []
    
    async def _create_world_scene_with_all_buildings(self, world_spec: Dict[str, Any], characters: Dict[str, Any]) -> str:
        """Create the main world scene with proper SubResource ID management"""
        
        # Reset SubResource counter for new scene
        self._reset_subresource_counter()
        
        buildings = world_spec.get('buildings', [])
        characters_list = characters.get('characters', []) if characters else []
        natural_features = world_spec.get('natural_features', [])
        
        building_count = len(buildings)
        character_count = len(characters_list)
        feature_count = len(natural_features)
        
        # Calculate ExtResources
        base_ext_resources = 2  # WorldManager.gd + Player.gd
        npc_ext_resources = character_count
        total_ext_resources = base_ext_resources + npc_ext_resources
        
        # Generate all SubResources with proper IDs
        sub_resources_data = self._generate_all_subresources(buildings, natural_features)
        total_subresources = len(sub_resources_data['ids'])
        total_load_steps = total_ext_resources + total_subresources
        
        # Generate ExtResource headers
        ext_resources = self._generate_npc_ext_resources(characters_list)
        
        # Create scene content
        scene_content = f'''[gd_scene load_steps={total_load_steps} format=3 uid="uid://world_main"]

[ext_resource type="Script" path="res://scripts/WorldManager.gd" id="1"]
[ext_resource type="Script" path="res://scripts/Player.gd" id="2"]
{ext_resources}

{sub_resources_data['content']}

[node name="World" type="Node3D"]
script = ExtResource("1")

[node name="Environment" type="Node3D" parent="."]

[node name="DirectionalLight3D" type="DirectionalLight3D" parent="Environment"]
transform = Transform3D(0.707107, -0.5, 0.5, 0, 0.707107, 0.707107, -0.707107, -0.5, 0.5, 0, 10, 0)
light_energy = 1.0
shadow_enabled = true

[node name="Ground" type="StaticBody3D" parent="Environment"]

[node name="GroundMesh" type="MeshInstance3D" parent="Environment/Ground"]
mesh = SubResource("{sub_resources_data['ground_mesh_id']}")

[node name="GroundCollision" type="CollisionShape3D" parent="Environment/Ground"]
shape = SubResource("{sub_resources_data['ground_shape_id']}")

{self._create_player_node_with_camera(sub_resources_data)}

[node name="Buildings" type="Node3D" parent="."]

'''
        
        # Add buildings
        for i, building in enumerate(buildings):
            building_node = self._create_building_node_on_ground(building, i, sub_resources_data)
            scene_content += building_node
        
        # Add environmental props
        environmental_props_section = self._create_environmental_props_section(natural_features, sub_resources_data)
        scene_content += environmental_props_section
        
        # Add NPCs
        scene_content += '[node name="NPCs" type="Node3D" parent="."]\n\n'
        
        for i, character in enumerate(characters_list):
            npc_node = self._create_npc_node_on_ground_with_script(character, i, sub_resources_data)
            scene_content += npc_node
        
        # Write scene file
        world_scene_file = self.scenes_dir / "World.tscn"
        with open(world_scene_file, 'w', encoding='utf-8') as f:
            f.write(scene_content)
        
        self.logger.info(f"✅ Created world scene with {building_count} buildings, {feature_count} environmental features, {character_count} NPCs")
        return "World.tscn"
    
    def _generate_all_subresources(self, buildings: List[Dict], natural_features: List[Dict]) -> Dict[str, Any]:
        """Generate all SubResources with proper unique IDs"""
        
        subresources_content = ""
        subresource_ids = []
        
        # Ground resources
        ground_mesh_id = self._get_next_subresource_id("PlaneMesh")
        ground_shape_id = self._get_next_subresource_id("BoxShape3D")
        subresource_ids.extend([ground_mesh_id, ground_shape_id])
        
        subresources_content += f'''[sub_resource type="PlaneMesh" id="{ground_mesh_id}"]
size = Vector2(100, 100)

[sub_resource type="BoxShape3D" id="{ground_shape_id}"]
size = Vector3(100, 0.1, 100)

'''
        
        # Player resources
        player_mesh_id = self._get_next_subresource_id("CapsuleMesh")
        player_shape_id = self._get_next_subresource_id("CapsuleShape3D")
        subresource_ids.extend([player_mesh_id, player_shape_id])
        
        subresources_content += f'''[sub_resource type="CapsuleMesh" id="{player_mesh_id}"]
radius = 0.5
height = 2.0

[sub_resource type="CapsuleShape3D" id="{player_shape_id}"]
radius = 0.5
height = 2.0

'''
        
        # Building resources
        building_resources = {}
        for i, building in enumerate(buildings):
            building_type = building.get('type', 'generic')
            scale = building.get('scale', 1.0)
            color = self._get_building_color(building_type)
            
            mesh_id = self._get_next_subresource_id("BoxMesh")
            shape_id = self._get_next_subresource_id("BoxShape3D")
            material_id = self._get_next_subresource_id("StandardMaterial3D")
            
            subresource_ids.extend([mesh_id, shape_id, material_id])
            building_resources[i] = {
                'mesh_id': mesh_id,
                'shape_id': shape_id,
                'material_id': material_id
            }
            
            mesh_size = f"Vector3({4 * scale}, {3 * scale}, {4 * scale})"
            
            subresources_content += f'''[sub_resource type="BoxMesh" id="{mesh_id}"]
size = {mesh_size}

[sub_resource type="BoxShape3D" id="{shape_id}"]
size = {mesh_size}

[sub_resource type="StandardMaterial3D" id="{material_id}"]
albedo_color = Color{color}
roughness = 0.7
metallic = 0.1

'''
        
        # Environmental props resources
        environmental_resources = {}
        for i, feature in enumerate(natural_features):
            feature_type = feature.get('type', 'rock')
            scale = feature.get('scale', 1.0)
            
            if feature_type in ['oak_tree', 'tree']:
                trunk_mesh_id = self._get_next_subresource_id("CylinderMesh")
                leaves_mesh_id = self._get_next_subresource_id("SphereMesh")
                trunk_shape_id = self._get_next_subresource_id("CylinderShape3D")
                trunk_material_id = self._get_next_subresource_id("StandardMaterial3D")
                leaves_material_id = self._get_next_subresource_id("StandardMaterial3D")
                
                subresource_ids.extend([trunk_mesh_id, leaves_mesh_id, trunk_shape_id, trunk_material_id, leaves_material_id])
                environmental_resources[i] = {
                    'type': 'tree',
                    'trunk_mesh_id': trunk_mesh_id,
                    'leaves_mesh_id': leaves_mesh_id,
                    'trunk_shape_id': trunk_shape_id,
                    'trunk_material_id': trunk_material_id,
                    'leaves_material_id': leaves_material_id
                }
                
                subresources_content += f'''[sub_resource type="CylinderMesh" id="{trunk_mesh_id}"]
top_radius = {0.2 * scale}
bottom_radius = {0.3 * scale}
height = {3.0 * scale}

[sub_resource type="SphereMesh" id="{leaves_mesh_id}"]
radius = {1.5 * scale}
height = {3.0 * scale}

[sub_resource type="CylinderShape3D" id="{trunk_shape_id}"]
top_radius = {0.2 * scale}
bottom_radius = {0.3 * scale}
height = {3.0 * scale}

[sub_resource type="StandardMaterial3D" id="{trunk_material_id}"]
albedo_color = Color(0.4, 0.2, 0.1, 1)
roughness = 0.9
metallic = 0.0

[sub_resource type="StandardMaterial3D" id="{leaves_material_id}"]
albedo_color = Color(0.2, 0.8, 0.2, 1)
roughness = 1.0
metallic = 0.0

'''
            
            elif feature_type in ['bush', 'flower_patch']:
                mesh_id = self._get_next_subresource_id("SphereMesh")
                shape_id = self._get_next_subresource_id("SphereShape3D")
                material_id = self._get_next_subresource_id("StandardMaterial3D")
                
                subresource_ids.extend([mesh_id, shape_id, material_id])
                environmental_resources[i] = {
                    'type': 'bush',
                    'mesh_id': mesh_id,
                    'shape_id': shape_id,
                    'material_id': material_id
                }
                
                subresources_content += f'''[sub_resource type="SphereMesh" id="{mesh_id}"]
radius = {0.8 * scale}
height = {1.6 * scale}

[sub_resource type="SphereShape3D" id="{shape_id}"]
radius = {0.8 * scale}

[sub_resource type="StandardMaterial3D" id="{material_id}"]
albedo_color = Color(0.3, 0.7, 0.3, 1)
roughness = 1.0
metallic = 0.0

'''
            
            elif feature_type == 'rock':
                mesh_id = self._get_next_subresource_id("SphereMesh")
                shape_id = self._get_next_subresource_id("SphereShape3D")
                material_id = self._get_next_subresource_id("StandardMaterial3D")
                
                subresource_ids.extend([mesh_id, shape_id, material_id])
                environmental_resources[i] = {
                    'type': 'rock',
                    'mesh_id': mesh_id,
                    'shape_id': shape_id,
                    'material_id': material_id
                }
                
                subresources_content += f'''[sub_resource type="SphereMesh" id="{mesh_id}"]
radius = {0.5 * scale}
height = {1.0 * scale}

[sub_resource type="SphereShape3D" id="{shape_id}"]
radius = {0.5 * scale}

[sub_resource type="StandardMaterial3D" id="{material_id}"]
albedo_color = Color(0.6, 0.6, 0.6, 1)
roughness = 0.8
metallic = 0.0

'''
            
            elif feature_type == 'well':
                mesh_id = self._get_next_subresource_id("CylinderMesh")
                shape_id = self._get_next_subresource_id("CylinderShape3D")
                material_id = self._get_next_subresource_id("StandardMaterial3D")
                
                subresource_ids.extend([mesh_id, shape_id, material_id])
                environmental_resources[i] = {
                    'type': 'well',
                    'mesh_id': mesh_id,
                    'shape_id': shape_id,
                    'material_id': material_id
                }
                
                subresources_content += f'''[sub_resource type="CylinderMesh" id="{mesh_id}"]
top_radius = {0.6 * scale}
bottom_radius = {0.6 * scale}
height = {1.0 * scale}

[sub_resource type="CylinderShape3D" id="{shape_id}"]
top_radius = {0.6 * scale}
bottom_radius = {0.6 * scale}
height = {1.0 * scale}

[sub_resource type="StandardMaterial3D" id="{material_id}"]
albedo_color = Color(0.5, 0.5, 0.5, 1)
roughness = 0.7
metallic = 0.0

'''
        
        return {
            'content': subresources_content,
            'ids': subresource_ids,
            'ground_mesh_id': ground_mesh_id,
            'ground_shape_id': ground_shape_id,
            'player_mesh_id': player_mesh_id,
            'player_shape_id': player_shape_id,
            'building_resources': building_resources,
            'environmental_resources': environmental_resources
        }
    
    def _create_environmental_props_section(self, natural_features: List[Dict], sub_resources_data: Dict) -> str:
        """Create environmental props section with proper SubResource references"""
        if not natural_features:
            return ""
        
        section = '[node name="EnvironmentalProps" type="Node3D" parent="."]\n\n'
        
        for i, feature in enumerate(natural_features):
            if i in sub_resources_data['environmental_resources']:
                feature_node = self._create_environmental_prop_node(feature, i, sub_resources_data['environmental_resources'][i])
                section += feature_node
        
        return section
    
    def _create_environmental_prop_node(self, feature: Dict[str, Any], index: int, resource_data: Dict) -> str:
        """Create individual environmental prop node with proper SubResource references"""
        feature_id = feature.get('id', f'feature_{index}')
        feature_type = feature.get('type', 'rock')
        position = feature.get('position', {'x': 0, 'y': 0, 'z': 0})
        rotation = feature.get('rotation', 0)
        scale = feature.get('scale', 1.0)
        
        # Handle position
        if isinstance(position, dict):
            world_x, world_y, world_z = position.get('x', 0), position.get('y', 0), position.get('z', 0)
        else:
            world_x, world_y, world_z = 0, 0, 0
        
        # Map coordinates
        godot_x = world_x
        godot_z = world_y
        
        # Set height based on feature type
        if feature_type in ['oak_tree', 'tree']:
            godot_y = 1.5 * scale
        elif feature_type in ['bush', 'flower_patch']:
            godot_y = 0.8 * scale
        elif feature_type == 'rock':
            godot_y = 0.5 * scale
        elif feature_type == 'well':
            godot_y = 0.5 * scale
        else:
            godot_y = 0.5 * scale
        
        # Calculate rotation
        rotation_rad = rotation * math.pi / 180 if rotation else 0
        cos_r = math.cos(rotation_rad)
        sin_r = math.sin(rotation_rad)
        
        # Sanitize name
        safe_name = self._sanitize_node_name(feature_id, f"Feature_{index}")
        
        if resource_data['type'] == 'tree':
            node_content = f'''[node name="{safe_name}" type="StaticBody3D" parent="EnvironmentalProps"]
transform = Transform3D({cos_r * scale}, 0, {sin_r * scale}, 0, {scale}, 0, {-sin_r * scale}, 0, {cos_r * scale}, {godot_x}, {godot_y}, {godot_z})

[node name="TreeTrunk" type="MeshInstance3D" parent="EnvironmentalProps/{safe_name}"]
mesh = SubResource("{resource_data['trunk_mesh_id']}")
surface_material_override/0 = SubResource("{resource_data['trunk_material_id']}")

[node name="TreeLeaves" type="MeshInstance3D" parent="EnvironmentalProps/{safe_name}"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0)
mesh = SubResource("{resource_data['leaves_mesh_id']}")
surface_material_override/0 = SubResource("{resource_data['leaves_material_id']}")

[node name="TreeCollision" type="CollisionShape3D" parent="EnvironmentalProps/{safe_name}"]
shape = SubResource("{resource_data['trunk_shape_id']}")

'''
        
        elif resource_data['type'] == 'bush':
            node_content = f'''[node name="{safe_name}" type="StaticBody3D" parent="EnvironmentalProps"]
transform = Transform3D({cos_r * scale}, 0, {sin_r * scale}, 0, {scale}, 0, {-sin_r * scale}, 0, {cos_r * scale}, {godot_x}, {godot_y}, {godot_z})

[node name="BushMesh" type="MeshInstance3D" parent="EnvironmentalProps/{safe_name}"]
mesh = SubResource("{resource_data['mesh_id']}")
surface_material_override/0 = SubResource("{resource_data['material_id']}")

[node name="BushCollision" type="CollisionShape3D" parent="EnvironmentalProps/{safe_name}"]
shape = SubResource("{resource_data['shape_id']}")

'''
        
        elif resource_data['type'] == 'rock':
            node_content = f'''[node name="{safe_name}" type="StaticBody3D" parent="EnvironmentalProps"]
transform = Transform3D({cos_r * scale}, 0, {sin_r * scale}, 0, {scale}, 0, {-sin_r * scale}, 0, {cos_r * scale}, {godot_x}, {godot_y}, {godot_z})

[node name="RockMesh" type="MeshInstance3D" parent="EnvironmentalProps/{safe_name}"]
mesh = SubResource("{resource_data['mesh_id']}")
surface_material_override/0 = SubResource("{resource_data['material_id']}")

[node name="RockCollision" type="CollisionShape3D" parent="EnvironmentalProps/{safe_name}"]
shape = SubResource("{resource_data['shape_id']}")

'''
        
        elif resource_data['type'] == 'well':
            node_content = f'''[node name="{safe_name}" type="StaticBody3D" parent="EnvironmentalProps"]
transform = Transform3D({cos_r * scale}, 0, {sin_r * scale}, 0, {scale}, 0, {-sin_r * scale}, 0, {cos_r * scale}, {godot_x}, {godot_y}, {godot_z})

[node name="WellMesh" type="MeshInstance3D" parent="EnvironmentalProps/{safe_name}"]
mesh = SubResource("{resource_data['mesh_id']}")
surface_material_override/0 = SubResource("{resource_data['material_id']}")

[node name="WellCollision" type="CollisionShape3D" parent="EnvironmentalProps/{safe_name}"]
shape = SubResource("{resource_data['shape_id']}")

'''
        
        return node_content
    
    def _create_player_node_with_camera(self, sub_resources_data: Dict) -> str:
        """Create player node with proper SubResource references"""
        
        player_mesh_id = sub_resources_data['player_mesh_id']
        player_shape_id = sub_resources_data['player_shape_id']
        
        if self.camera_mode == 'third_person':
            return f'''[node name="Player" type="CharacterBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0)
script = ExtResource("2")

[node name="PlayerMesh" type="MeshInstance3D" parent="Player"]
mesh = SubResource("{player_mesh_id}")

[node name="PlayerCollision" type="CollisionShape3D" parent="Player"]
shape = SubResource("{player_shape_id}")

[node name="Camera3D" type="Camera3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, 0.940, 0.342, 0, -0.342, 0.940, 0, 4, 8)
current = true
fov = 75.0

[node name="InteractionRay" type="RayCast3D" parent="Player/Camera3D"]
target_position = Vector3(0, 0, -3)

'''
        else:
            return f'''[node name="Player" type="CharacterBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0)
script = ExtResource("2")

[node name="PlayerMesh" type="MeshInstance3D" parent="Player"]
mesh = SubResource("{player_mesh_id}")

[node name="PlayerCollision" type="CollisionShape3D" parent="Player"]
shape = SubResource("{player_shape_id}")

[node name="Camera3D" type="Camera3D" parent="Player"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.6, 0)
current = true

[node name="InteractionRay" type="RayCast3D" parent="Player/Camera3D"]
target_position = Vector3(0, 0, -3)

'''
    
    def _create_building_node_on_ground(self, building: Dict[str, Any], index: int, sub_resources_data: Dict) -> str:
        """Create building node with proper SubResource references"""
        
        building_id = building.get('id', f'building_{index}')
        position = building.get('position', {'x': 0, 'y': 0, 'z': 0})
        rotation = building.get('rotation', 0)
        scale = building.get('scale', 1.0)
        
        # Handle position
        if isinstance(position, dict):
            world_x, world_y, world_z = position.get('x', 0), position.get('y', 0), position.get('z', 0)
        elif isinstance(position, list) and len(position) >= 2:
            world_x, world_y = position[0], position[1]
            world_z = position[2] if len(position) > 2 else 0
        else:
            world_x, world_y, world_z = 0, 0, 0
        
        godot_x = world_x
        godot_y = 1.5 * scale
        godot_z = world_y
        
        # Calculate rotation
        rotation_rad = rotation * math.pi / 180 if rotation else 0
        
        if rotation != 0:
            cos_r = math.cos(rotation_rad)
            sin_r = math.sin(rotation_rad)
            rotation_matrix = f"{cos_r * scale}, 0, {sin_r * scale}, 0, {scale}, 0, {-sin_r * scale}, 0, {cos_r * scale}"
        else:
            rotation_matrix = f"{scale}, 0, 0, 0, {scale}, 0, 0, 0, {scale}"
        
        safe_name = self._sanitize_node_name(building_id, f"Building_{index}")
        
        # Get SubResource IDs for this building
        building_resources = sub_resources_data['building_resources'][index]
        
        building_node = f'''[node name="{safe_name}" type="StaticBody3D" parent="Buildings"]
transform = Transform3D({rotation_matrix}, {godot_x}, {godot_y}, {godot_z})

[node name="BuildingMesh" type="MeshInstance3D" parent="Buildings/{safe_name}"]
mesh = SubResource("{building_resources['mesh_id']}")
surface_material_override/0 = SubResource("{building_resources['material_id']}")

[node name="BuildingCollision" type="CollisionShape3D" parent="Buildings/{safe_name}"]
shape = SubResource("{building_resources['shape_id']}")

[node name="InteractionArea" type="Area3D" parent="Buildings/{safe_name}"]

[node name="InteractionShape" type="CollisionShape3D" parent="Buildings/{safe_name}/InteractionArea"]
transform = Transform3D(1.2, 0, 0, 0, 1.2, 0, 0, 0, 1.2, 0, 0, 0)
shape = SubResource("{building_resources['shape_id']}")

'''
        
        return building_node
    
    def _create_npc_node_on_ground_with_script(self, character: Dict[str, Any], index: int, sub_resources_data: Dict) -> str:
        """Create NPC node with proper SubResource references"""
        
        character_name = character.get('name', f'NPC_{index}')
        location = character.get('location', 'house')
        safe_name = self._sanitize_node_name(character_name, f"NPC_{index}")
        
        script_ext_resource_id = index + 3
        
        spawn_positions = {
            'house': (10, 1, 10),
            'church': (14, 1, 30),
            'tower': (14, 1, 10),
            'tavern': (20, 1, 20),
            'shop': (25, 1, 15)
        }
        
        x, y, z = spawn_positions.get(location, (5 + index * 3, 1, 5))
        
        player_mesh_id = sub_resources_data['player_mesh_id']
        player_shape_id = sub_resources_data['player_shape_id']
        
        npc_node = f'''[node name="{safe_name}" type="CharacterBody3D" parent="NPCs"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {x}, {y}, {z})
script = ExtResource("{script_ext_resource_id}")

[node name="NPCMesh" type="MeshInstance3D" parent="NPCs/{safe_name}"]
mesh = SubResource("{player_mesh_id}")

[node name="NPCCollision" type="CollisionShape3D" parent="NPCs/{safe_name}"]
shape = SubResource("{player_shape_id}")

'''
        
        return npc_node
    
    def _generate_npc_ext_resources(self, characters_list: List[Dict[str, Any]]) -> str:
        """Generate ExtResource entries for all NPC scripts"""
        ext_resources = ""
        
        for i, character in enumerate(characters_list):
            character_name = character.get('name', f'NPC_{i}')
            safe_name = self._sanitize_node_name(character_name, f"NPC_{i}")
            ext_resource_id = i + 3  # Start from 3 (1=WorldManager, 2=Player)
            
            ext_resources += f'[ext_resource type="Script" path="res://scripts/{safe_name}.gd" id="{ext_resource_id}"]\n'
        
        return ext_resources
    
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
        
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
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
        """Create player scene with first-person camera"""
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
        """Create player scene with third-person camera"""
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
    
    # Debugging methods
    def debug_world_spec_structure(self, world_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Debug the world specification structure to identify issues"""
        debug_info = {
            'world_spec_keys': list(world_spec.keys()) if world_spec else [],
            'buildings_count': len(world_spec.get('buildings', [])) if world_spec else 0,
            'natural_features_count': len(world_spec.get('natural_features', [])) if world_spec else 0,
            'features_count': len(world_spec.get('features', [])) if world_spec else 0,
            'natural_features_sample': None,
            'issues': []
        }
        
        if not world_spec:
            debug_info['issues'].append("world_spec is None or empty")
            return debug_info
        
        natural_features = world_spec.get('natural_features', [])
        if natural_features:
            debug_info['natural_features_sample'] = natural_features[0] if len(natural_features) > 0 else None
            debug_info['natural_features_types'] = list(set(f.get('type', 'unknown') for f in natural_features[:10]))
        else:
            debug_info['issues'].append("No 'natural_features' field found in world_spec")
            
        features = world_spec.get('features', [])
        if features:
            debug_info['issues'].append("Found 'features' field - should be 'natural_features'")
            
        return debug_info
    
    def quick_fix_test(self, world_spec: Dict[str, Any]) -> str:
        """Quick test to see if environmental props will be generated"""
        debug = self.debug_world_spec_structure(world_spec)
        
        test_results = []
        test_results.append("🔍 ENVIRONMENTAL PROPS DEBUG TEST")
        test_results.append("="*50)
        
        test_results.append(f"📊 World spec keys: {debug['world_spec_keys']}")
        test_results.append(f"🏠 Buildings found: {debug['buildings_count']}")
        test_results.append(f"🌳 Natural features found: {debug['natural_features_count']}")
        
        if debug['natural_features_count'] > 0:
            test_results.append("✅ Natural features detected!")
            test_results.append(f"📝 Sample feature: {debug['natural_features_sample']}")
            test_results.append(f"🎯 Feature types: {debug.get('natural_features_types', [])}")
            test_results.append("✅ Environmental props SHOULD appear in Godot!")
            test_results.append("✅ SubResource IDs will be properly managed!")
        else:
            test_results.append("❌ NO natural features found!")
            test_results.append("❌ Environmental props will NOT appear in Godot!")
            
        if debug['issues']:
            test_results.append("\n⚠️  Issues found:")
            for issue in debug['issues']:
                test_results.append(f"   - {issue}")
                
        return "\n".join(test_results)
    
    def get_environmental_props_summary(self, world_spec: Dict[str, Any]) -> str:
        """Get a human-readable summary of environmental props"""
        natural_features = world_spec.get('natural_features', [])
        
        if not natural_features:
            return "❌ No environmental props found. Trees, bushes, and rocks will not appear in Godot."
        
        # Count feature types
        feature_types = {}
        for feature in natural_features:
            feature_type = feature.get('type', 'unknown')
            feature_types[feature_type] = feature_types.get(feature_type, 0) + 1
        
        summary_lines = [
            f"✅ Found {len(natural_features)} environmental features:",
        ]
        
        for feature_type, count in feature_types.items():
            emoji = {
                'oak_tree': '🌳', 'tree': '🌳',
                'bush': '🌿', 'flower_patch': '🌸',
                'rock': '🪨', 'well': '🪣'
            }.get(feature_type, '❓')
            summary_lines.append(f"  {emoji} {feature_type}: {count}")
        
        summary_lines.append("✅ SubResource IDs will be properly managed to avoid conflicts!")
        
        return "\n".join(summary_lines)