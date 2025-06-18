"""
ENVIRONMENT GENERATOR MODULE
Specialized module for generating environmental assets
Handles terrain features, paths, water bodies, and atmospheric elements
"""

from typing import Dict, List, Any
from pathlib import Path
import logging
import random

class EnvironmentGenerator:
    """
    Specialized environment generation module
    Handles terrain features, paths, water, and atmospheric elements
    """
    
    def __init__(self, output_dir: Path, ai_core):
        self.output_dir = output_dir
        self.ai_core = ai_core
        self.logger = logging.getLogger(__name__)
        
        # Environment-specific directories
        self.scripts_dir = output_dir / "blender_scripts"
        self.environment_dir = output_dir / "environment"
        self.scripts_dir.mkdir(exist_ok=True)
        self.environment_dir.mkdir(exist_ok=True)
    
    async def generate_ai_creative_environment(self, world_spec: Dict[str, Any], theme: str) -> List[Dict]:
        """Generate AI-creative environment assets"""
        environment_assets = []
        
        # Extract world information
        size = world_spec.get('size', (40, 40))
        terrain_map = world_spec.get('terrain_map', [])
        buildings = world_spec.get('buildings', [])
        
        # Generate paths connecting buildings
        paths = await self._generate_path_network(buildings, size, theme)
        environment_assets.extend(paths)
        
        # Generate terrain features
        terrain_features = await self._generate_terrain_features(terrain_map, theme)
        environment_assets.extend(terrain_features)
        
        # Generate water features if appropriate
        water_features = await self._generate_water_features(world_spec, theme)
        environment_assets.extend(water_features)
        
        # Generate atmospheric elements
        atmospheric = await self._generate_atmospheric_elements(theme, size)
        environment_assets.extend(atmospheric)
        
        # Generate ambient props
        ambient_props = await self._generate_ambient_props(world_spec, theme)
        environment_assets.extend(ambient_props)
        
        return environment_assets
    
    async def _generate_path_network(self, buildings: List[Dict], size: tuple, theme: str) -> List[Dict]:
        """Generate intelligent path network connecting buildings"""
        paths = []
        
        if len(buildings) < 2:
            return paths
        
        # Find central hub (usually largest building or tavern)
        hub_building = None
        for building in buildings:
            if building.get('type') in ['tavern', 'church', 'market']:
                hub_building = building
                break
        
        if not hub_building:
            hub_building = buildings[0]  # Use first building as hub
        
        hub_pos = hub_building.get('position', {'x': 0, 'y': 0})
        
        # Generate main paths from hub to other buildings
        for i, building in enumerate(buildings):
            if building == hub_building:
                continue
                
            building_pos = building.get('position', {'x': 0, 'y': 0})
            
            # Create path description
            path_description = await self._generate_path_description(
                hub_pos, building_pos, theme, building.get('type', 'building')
            )
            
            # Generate path geometry
            path_points = self._calculate_path_points(hub_pos, building_pos)
            
            path_asset = {
                'id': f"path_hub_to_{building.get('type', 'building')}_{i}",
                'type': 'path',
                'description': path_description,
                'start_position': hub_pos,
                'end_position': building_pos,
                'path_points': path_points,
                'path_style': await self._generate_path_style(theme),
                'script_path': self._create_path_script(path_points, theme, i)
            }
            
            paths.append(path_asset)
        
        # Generate secondary connecting paths
        secondary_paths = await self._generate_secondary_paths(buildings, theme)
        paths.extend(secondary_paths)
        
        return paths
    
    async def _generate_path_description(self, start_pos: Dict, end_pos: Dict, theme: str, destination_type: str) -> str:
        """Generate AI description for path"""
        if not self.ai_core.ai_available:
            return f"A {theme} path leading to the {destination_type}"
        
        distance = ((end_pos['x'] - start_pos['x'])**2 + (end_pos['y'] - start_pos['y'])**2)**0.5
        distance_desc = "short" if distance < 15 else "long" if distance > 30 else "winding"
        
        prompt = f"""Describe a {distance_desc} path in a {theme} world leading to a {destination_type}.
        Include details about:
        - Path material and construction
        - Surrounding vegetation or landmarks
        - Condition and maintenance level
        - Any unique features
        
        Keep it to 1-2 sentences."""
        
        response = await self.ai_core.call_gemini(prompt)
        return response if response else f"A {distance_desc} {theme} path leading to the {destination_type}"
    
    def _calculate_path_points(self, start_pos: Dict, end_pos: Dict) -> List[Dict]:
        """Calculate path waypoints with natural curves"""
        points = [start_pos]
        
        # Add intermediate points for longer paths
        distance = ((end_pos['x'] - start_pos['x'])**2 + (end_pos['y'] - start_pos['y'])**2)**0.5
        
        if distance > 20:
            # Add 1-2 intermediate points with slight curves
            num_points = 2 if distance > 35 else 1
            
            for i in range(1, num_points + 1):
                ratio = i / (num_points + 1)
                
                # Linear interpolation with random offset for natural curves
                mid_x = start_pos['x'] + (end_pos['x'] - start_pos['x']) * ratio
                mid_y = start_pos['y'] + (end_pos['y'] - start_pos['y']) * ratio
                
                # Add slight curve offset
                curve_offset = random.uniform(-3, 3)
                perpendicular_angle = 1.5708  # 90 degrees in radians
                
                mid_x += curve_offset * (-1 if i % 2 else 1)
                mid_y += curve_offset * (-1 if i % 2 else 1)
                
                points.append({'x': mid_x, 'y': mid_y, 'z': 0})
        
        points.append(end_pos)
        return points
    
    async def _generate_path_style(self, theme: str) -> Dict[str, Any]:
        """Generate path styling parameters"""
        base_styles = {
            'medieval': {
                'material': random.choice(['cobblestone', 'dirt', 'gravel', 'flagstone']),
                'width': random.uniform(1.5, 3.0),
                'edge_treatment': random.choice(['grass', 'stones', 'wild_flowers']),
                'condition': random.choice(['well_maintained', 'worn', 'overgrown'])
            },
            'fantasy': {
                'material': random.choice(['enchanted_stone', 'crystal_path', 'moss_covered', 'glowing_stones']),
                'width': random.uniform(1.8, 3.5),
                'edge_treatment': random.choice(['magical_flowers', 'glowing_moss', 'crystal_formations']),
                'condition': random.choice(['pristine', 'mystical', 'ancient'])
            },
            'spooky': {
                'material': random.choice(['cracked_stone', 'dark_earth', 'bone_fragments', 'rotting_wood']),
                'width': random.uniform(1.0, 2.5),
                'edge_treatment': random.choice(['dead_grass', 'thorny_vines', 'mushrooms', 'fog']),
                'condition': random.choice(['decrepit', 'abandoned', 'treacherous'])
            },
            'desert': {
                'material': random.choice(['sandstone', 'packed_sand', 'adobe_bricks', 'sun_dried_clay']),
                'width': random.uniform(2.0, 4.0),
                'edge_treatment': random.choice(['sand_dunes', 'desert_plants', 'stone_markers']),
                'condition': random.choice(['sand_swept', 'sun_bleached', 'well_traveled'])
            }
        }
        
        return base_styles.get(theme, base_styles['medieval'])
    
    def _create_path_script(self, path_points: List[Dict], theme: str, index) -> str:
        """Create path generation script"""
        # Ensure index is properly converted to string in all uses
        index_str = str(index)
        
        script_content = f'''
import bpy
import bmesh
from mathutils import Vector

# AI-GENERATED PATH
# Path {index_str} in {theme} theme
# Points: {len(path_points)}

def create_ai_path():
    """Create AI-designed path"""
    path_objects = []
    
    # Path parameters
    path_width = 2.0
    path_segments = {len(path_points) - 1}
    
    # Create path curve
    curve_data = bpy.data.curves.new(name=f"AI_Path_{index_str}", type='CURVE')
    curve_data.dimensions = '3D'
    
    # Create spline
    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(path_segments)
    
    # Set path points
    points = {path_points}
    for i, point in enumerate(points):
        bezier_point = spline.bezier_points[i]
        bezier_point.co = (point['x'], point['y'], point.get('z', 0))
        bezier_point.handle_left_type = 'AUTO'
        bezier_point.handle_right_type = 'AUTO'
    
    # Create curve object
    curve_obj = bpy.data.objects.new(f"AI_Path_Curve_{index_str}", curve_data)
    bpy.context.collection.objects.link(curve_obj)
    
    # Convert to mesh and extrude for path width
    bpy.context.view_layer.objects.active = curve_obj
    bpy.ops.object.convert(target='MESH')
    
    path_mesh = bpy.context.active_object
    path_mesh.name = f"AI_Path_{index_str}"
    
    return [path_mesh]

# Execute path creation
try:
    created_path = create_ai_path()
    print(f"✅ Created AI path with {{len(created_path)}} components")
except Exception as e:
    print(f"❌ Error creating path: {{e}}")

print("🛤️ AI Path Generation Complete!")
'''
        
        script_path = self.scripts_dir / f"ai_path_{index_str}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return str(script_path)
    
    async def _generate_secondary_paths(self, buildings: List[Dict], theme: str) -> List[Dict]:
        """Generate secondary connecting paths between buildings"""
        secondary_paths = []
        
        # Connect buildings that are close to each other
        for i, building1 in enumerate(buildings):
            for j, building2 in enumerate(buildings[i+1:], i+1):
                pos1 = building1.get('position', {'x': 0, 'y': 0})
                pos2 = building2.get('position', {'x': 0, 'y': 0})
                
                distance = ((pos2['x'] - pos1['x'])**2 + (pos2['y'] - pos1['y'])**2)**0.5
                
                # Create secondary path if buildings are reasonably close
                if distance < 25 and random.random() < 0.3:  # 30% chance for nearby buildings
                    path_points = self._calculate_path_points(pos1, pos2)
                    
                    # Create safe index for file naming
                    path_index = f"sec_{i}_{j}"
                    
                    secondary_path = {
                        'id': f"secondary_path_{i}_{j}",
                        'type': 'secondary_path',
                        'description': f"A secondary {theme} path connecting nearby buildings",
                        'start_position': pos1,
                        'end_position': pos2,
                        'path_points': path_points,
                        'path_style': await self._generate_path_style(theme),
                        'script_path': self._create_path_script(path_points, theme, path_index)
                    }
                    
                    secondary_paths.append(secondary_path)
        
        return secondary_paths
    
    async def _generate_terrain_features(self, terrain_map: List[List[str]], theme: str) -> List[Dict]:
        """Generate terrain features based on terrain map"""
        terrain_features = []
        
        if not terrain_map:
            return terrain_features
        
        # Analyze terrain for feature placement
        height = len(terrain_map)
        width = len(terrain_map[0]) if height > 0 else 0
        
        # Find terrain clusters for feature placement
        terrain_clusters = self._find_terrain_clusters(terrain_map)
        
        for cluster_type, positions in terrain_clusters.items():
            if len(positions) > 3:  # Only create features for significant clusters
                feature = await self._create_terrain_feature(cluster_type, positions, theme)
                if feature:
                    terrain_features.append(feature)
        
        return terrain_features
    
    def _find_terrain_clusters(self, terrain_map: List[List[str]]) -> Dict[str, List[tuple]]:
        """Find clusters of similar terrain types"""
        clusters = {}
        height = len(terrain_map)
        width = len(terrain_map[0]) if height > 0 else 0
        
        for y in range(height):
            for x in range(width):
                terrain_type = terrain_map[y][x]
                if terrain_type not in clusters:
                    clusters[terrain_type] = []
                clusters[terrain_type].append((x, y))
        
        return clusters
    
    async def _create_terrain_feature(self, terrain_type: str, positions: List[tuple], theme: str) -> Dict[str, Any]:
        """Create a terrain feature for a cluster of terrain"""
        # Calculate center of cluster
        center_x = sum(pos[0] for pos in positions) / len(positions)
        center_y = sum(pos[1] for pos in positions) / len(positions)
        
        # Generate feature based on terrain type
        feature_types = {
            'forest': ['clearing', 'dense_grove', 'ancient_tree'],
            'mountain': ['peak', 'rocky_outcrop', 'cave_entrance'],
            'water': ['pond', 'stream', 'waterfall'],
            'grass': ['flower_field', 'hill', 'stone_circle'],
            'desert': ['oasis', 'sand_dune', 'rock_formation']
        }
        
        available_features = feature_types.get(terrain_type, ['natural_formation'])
        feature_type = random.choice(available_features)
        
        # Generate feature description
        description = await self._generate_terrain_feature_description(feature_type, terrain_type, theme)
        
        return {
            'id': f"terrain_{terrain_type}_{feature_type}",
            'type': 'terrain_feature',
            'feature_type': feature_type,
            'terrain_type': terrain_type,
            'position': {'x': center_x, 'y': center_y, 'z': 0},
            'description': description,
            'affected_area': len(positions),
            'script_path': self._create_terrain_feature_script(feature_type, center_x, center_y, theme)
        }
    
    async def _generate_terrain_feature_description(self, feature_type: str, terrain_type: str, theme: str) -> str:
        """Generate description for terrain feature"""
        if not self.ai_core.ai_available:
            return f"A {theme} {feature_type} in {terrain_type} terrain"
        
        prompt = f"""Describe a {feature_type} located in {terrain_type} terrain within a {theme} world.
        Include details about:
        - Visual appearance and scale
        - Natural elements and vegetation
        - Atmospheric qualities
        - Any unique characteristics
        
        Keep it to 1-2 sentences."""
        
        response = await self.ai_core.call_gemini(prompt)
        return response if response else f"A {theme} {feature_type} nestled in the {terrain_type}"
    
    def _create_terrain_feature_script(self, feature_type: str, x: float, y: float, theme: str) -> str:
        """Create terrain feature generation script"""
        # Convert coordinates to strings for safe concatenation
        x_str = str(int(x))
        y_str = str(int(y))
        
        script_content = f'''
import bpy
import random
import math

# AI-GENERATED TERRAIN FEATURE
# Feature: {feature_type}
# Theme: {theme}
# Position: ({x:.1f}, {y:.1f})

def create_terrain_feature():
    """Create {feature_type} terrain feature"""
    feature_objects = []
    
    if "{feature_type}" == "clearing":
        # Create a natural clearing
        clearing = create_clearing()
        feature_objects.extend(clearing)
    elif "{feature_type}" == "rocky_outcrop":
        # Create rocky formation
        rocks = create_rocky_outcrop()
        feature_objects.extend(rocks)
    elif "{feature_type}" == "flower_field":
        # Create flower field
        flowers = create_flower_field()
        feature_objects.extend(flowers)
    else:
        # Generic natural formation
        formation = create_generic_formation()
        feature_objects.extend(formation)
    
    return feature_objects

def create_clearing():
    """Create a natural clearing"""
    clearing_objects = []
    
    # Create clearing ground
    bpy.ops.mesh.primitive_cylinder_add(
        radius=8,
        depth=0.1,
        location=({x}, {y}, 0.05)
    )
    ground = bpy.context.active_object
    ground.name = "AI_clearing_ground"
    clearing_objects.append(ground)
    
    # Add scattered logs or stones around edge
    for i in range(random.randint(3, 6)):
        angle = i * (2 * math.pi / 6) + random.uniform(-0.5, 0.5)
        radius = random.uniform(6, 9)
        log_x = {x} + math.cos(angle) * radius
        log_y = {y} + math.sin(angle) * radius
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.3,
            depth=2,
            location=(log_x, log_y, 0.15)
        )
        log = bpy.context.active_object
        log.rotation_euler[1] = math.radians(90)  # Lay log horizontally
        log.rotation_euler[2] = angle
        log.name = f"AI_clearing_log_{{i}}"
        clearing_objects.append(log)
    
    return clearing_objects

def create_rocky_outcrop():
    """Create rocky outcrop formation"""
    rock_objects = []
    
    # Create main rock formation
    for i in range(random.randint(3, 7)):
        rock_size = random.uniform(1, 3)
        offset_x = random.uniform(-4, 4)
        offset_y = random.uniform(-4, 4)
        height = random.uniform(0.5, 2.5)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=rock_size,
            location=({x} + offset_x, {y} + offset_y, height)
        )
        rock = bpy.context.active_object
        rock.scale = (1, 1, random.uniform(0.6, 1.4))  # Vary height
        bpy.ops.object.transform_apply(scale=True)
        rock.name = f"AI_outcrop_rock_{{i}}"
        rock_objects.append(rock)
    
    return rock_objects

def create_flower_field():
    """Create a field of flowers"""
    flower_objects = []
    
    # Create flower clusters
    for i in range(random.randint(15, 25)):
        cluster_x = {x} + random.uniform(-10, 10)
        cluster_y = {y} + random.uniform(-10, 10)
        
        # Create flower cluster as small spheres
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=0.2,
            location=(cluster_x, cluster_y, 0.3)
        )
        flower = bpy.context.active_object
        
        # Random flower colors
        if random.random() < 0.5:
            flower.color = (random.uniform(0.8, 1), random.uniform(0.6, 0.9), random.uniform(0.6, 0.9), 1)
        else:
            flower.color = (random.uniform(0.9, 1), random.uniform(0.8, 1), random.uniform(0.4, 0.7), 1)
        
        flower.name = f"AI_flower_{{i}}"
        flower_objects.append(flower)
    
    return flower_objects

def create_generic_formation():
    """Create generic natural formation"""
    formation_objects = []
    
    # Create central feature
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=2,
        location=({x}, {y}, 1)
    )
    center = bpy.context.active_object
    center.name = "AI_formation_center"
    formation_objects.append(center)
    
    return formation_objects

# Execute terrain feature creation
try:
    created_feature = create_terrain_feature()
    print(f"✅ Created terrain feature {{'{feature_type}'}} with {{len(created_feature)}} components")
except Exception as e:
    print(f"❌ Error creating terrain feature: {{e}}")

print("🌍 AI Terrain Feature Generation Complete!")
'''
        
        script_path = self.scripts_dir / f"ai_terrain_{feature_type}_{x_str}_{y_str}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return str(script_path)
    
    async def _generate_water_features(self, world_spec: Dict[str, Any], theme: str) -> List[Dict]:
        """Generate water features like ponds, streams, fountains"""
        water_features = []
        
        size = world_spec.get('size', (40, 40))
        terrain_map = world_spec.get('terrain_map', [])
        
        # Check if world has water terrain
        has_water_terrain = False
        if terrain_map:
            for row in terrain_map:
                if 'water' in row:
                    has_water_terrain = True
                    break
        
        # Generate water features based on theme and terrain
        if has_water_terrain or random.random() < 0.4:  # 40% chance even without water terrain
            water_types = ['pond', 'fountain', 'stream']
            if theme == 'desert':
                water_types = ['oasis', 'well']
            elif theme == 'fantasy':
                water_types.extend(['magical_spring', 'crystal_pool'])
            
            num_features = random.randint(1, 3)
            for i in range(num_features):
                water_type = random.choice(water_types)
                
                # Random position away from buildings
                x = random.uniform(5, size[0] - 5)
                y = random.uniform(5, size[1] - 5)
                
                description = await self._generate_water_feature_description(water_type, theme)
                
                water_feature = {
                    'id': f"water_{water_type}_{i}",
                    'type': 'water_feature',
                    'water_type': water_type,
                    'position': {'x': x, 'y': y, 'z': 0},
                    'description': description,
                    'script_path': self._create_water_feature_script(water_type, x, y, theme, i)
                }
                
                water_features.append(water_feature)
        
        return water_features
    
    async def _generate_water_feature_description(self, water_type: str, theme: str) -> str:
        """Generate description for water feature"""
        if not self.ai_core.ai_available:
            return f"A {theme} {water_type} with clear, refreshing water"
        
        prompt = f"""Describe a {water_type} in a {theme} world.
        Include details about:
        - Water clarity and movement
        - Surrounding environment
        - Size and depth
        - Any special properties or features
        
        Keep it to 1-2 sentences."""
        
        response = await self.ai_core.call_gemini(prompt)
        return response if response else f"A beautiful {theme} {water_type} with pristine water"
    
    def _create_water_feature_script(self, water_type: str, x: float, y: float, theme: str, index: int) -> str:
        """Create water feature generation script"""
        script_content = f'''
import bpy
import random
import math

# AI-GENERATED WATER FEATURE
# Type: {water_type}
# Theme: {theme}
# Position: ({x:.1f}, {y:.1f})

def create_water_feature():
    """Create {water_type} water feature"""
    water_objects = []
    
    if "{water_type}" == "pond":
        water_objects = create_pond()
    elif "{water_type}" == "fountain":
        water_objects = create_fountain()
    elif "{water_type}" == "stream":
        water_objects = create_stream()
    elif "{water_type}" == "oasis":
        water_objects = create_oasis()
    else:
        water_objects = create_generic_water()
    
    return water_objects

def create_pond():
    """Create a natural pond"""
    pond_objects = []
    
    # Main water body
    bpy.ops.mesh.primitive_cylinder_add(
        radius=4,
        depth=0.5,
        location=({x}, {y}, -0.25)
    )
    water = bpy.context.active_object
    water.name = f"AI_pond_water_{index}"
    pond_objects.append(water)
    
    # Pond edge/rim
    bpy.ops.mesh.primitive_torus_add(
        major_radius=4.2,
        minor_radius=0.3,
        location=({x}, {y}, 0)
    )
    rim = bpy.context.active_object
    rim.name = f"AI_pond_rim_{index}"
    pond_objects.append(rim)
    
    return pond_objects

def create_fountain():
    """Create an ornamental fountain"""
    fountain_objects = []
    
    # Fountain base
    bpy.ops.mesh.primitive_cylinder_add(
        radius=2,
        depth=0.5,
        location=({x}, {y}, 0.25)
    )
    base = bpy.context.active_object
    base.name = f"AI_fountain_base_{index}"
    fountain_objects.append(base)
    
    # Water basin
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.8,
        depth=0.3,
        location=({x}, {y}, 0.4)
    )
    basin = bpy.context.active_object
    basin.name = f"AI_fountain_basin_{index}"
    fountain_objects.append(basin)
    
    # Central spout
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.1,
        depth=2,
        location=({x}, {y}, 1.5)
    )
    spout = bpy.context.active_object
    spout.name = f"AI_fountain_spout_{index}"
    fountain_objects.append(spout)
    
    return fountain_objects

def create_stream():
    """Create a flowing stream"""
    stream_objects = []
    
    # Create stream bed as curved path
    stream_length = 15
    segments = 8
    
    for i in range(segments):
        segment_x = {x} + (i - segments/2) * 2
        segment_y = {y} + math.sin(i * 0.5) * 2  # Curved path
        
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(segment_x, segment_y, -0.1)
        )
        segment = bpy.context.active_object
        segment.scale = (1.5, 0.8, 0.2)
        bpy.ops.object.transform_apply(scale=True)
        segment.name = f"AI_stream_segment_{{i}}_{index}"
        stream_objects.append(segment)
    
    return stream_objects

def create_oasis():
    """Create a desert oasis"""
    oasis_objects = []
    
    # Central water pool
    bpy.ops.mesh.primitive_cylinder_add(
        radius=3,
        depth=0.4,
        location=({x}, {y}, -0.2)
    )
    water = bpy.context.active_object
    water.name = f"AI_oasis_water_{index}"
    oasis_objects.append(water)
    
    # Surrounding vegetation (palm trees)
    for i in range(random.randint(3, 6)):
        angle = i * (2 * math.pi / 6)
        palm_x = {x} + math.cos(angle) * 5
        palm_y = {y} + math.sin(angle) * 5
        
        # Palm trunk
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.2,
            depth=4,
            location=(palm_x, palm_y, 2)
        )
        trunk = bpy.context.active_object
        trunk.name = f"AI_palm_trunk_{{i}}_{index}"
        oasis_objects.append(trunk)
        
        # Palm fronds
        for j in range(6):
            frond_angle = j * (2 * math.pi / 6)
            frond_x = palm_x + math.cos(frond_angle) * 2
            frond_y = palm_y + math.sin(frond_angle) * 2
            
            bpy.ops.mesh.primitive_cube_add(
                size=1,
                location=(frond_x, frond_y, 4.5)
            )
            frond = bpy.context.active_object
            frond.scale = (0.2, 2, 0.1)
            bpy.ops.object.transform_apply(scale=True)
            frond.rotation_euler[2] = frond_angle
            frond.name = f"AI_palm_frond_{{i}}_{{j}}_{index}"
            oasis_objects.append(frond)
    
    return oasis_objects

def create_generic_water():
    """Create generic water feature"""
    water_objects = []
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=2,
        depth=0.3,
        location=({x}, {y}, -0.15)
    )
    water = bpy.context.active_object
    water.name = f"AI_water_generic_{index}"
    water_objects.append(water)
    
    return water_objects

# Execute water feature creation
try:
    created_water = create_water_feature()
    print(f"✅ Created water feature {{'{water_type}'}} with {{len(created_water)}} components")
except Exception as e:
    print(f"❌ Error creating water feature: {{e}}")

print("💧 AI Water Feature Generation Complete!")
'''
        
        script_path = self.scripts_dir / f"ai_water_{water_type}_{index}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        return str(script_path)
    
    async def _generate_atmospheric_elements(self, theme: str, size: tuple) -> List[Dict]:
        """Generate atmospheric elements like lighting, fog, particle effects"""
        atmospheric_elements = []
        
        # Generate lighting setup
        lighting = await self._generate_lighting_setup(theme)
        atmospheric_elements.append(lighting)
        
        # Generate weather/atmosphere effects
        if random.random() < 0.6:  # 60% chance of atmospheric effects
            atmosphere = await self._generate_atmosphere_effects(theme)
            atmospheric_elements.append(atmosphere)
        
        # Generate ambient sounds (metadata only)
        sounds = await self._generate_ambient_sounds(theme)
        atmospheric_elements.append(sounds)
        
        return atmospheric_elements
    
    async def _generate_lighting_setup(self, theme: str) -> Dict[str, Any]:
        """Generate theme-appropriate lighting"""
        lighting_setups = {
            'medieval': {
                'sun_intensity': random.uniform(3, 5),
                'sun_angle': random.uniform(30, 60),
                'ambient_color': [0.4, 0.4, 0.5],
                'sun_color': [1.0, 0.95, 0.8]
            },
            'fantasy': {
                'sun_intensity': random.uniform(2, 4),
                'sun_angle': random.uniform(20, 50),
                'ambient_color': [0.3, 0.4, 0.6],
                'sun_color': [0.9, 0.95, 1.0],
                'magical_lights': True
            },
            'spooky': {
                'sun_intensity': random.uniform(1, 2),
                'sun_angle': random.uniform(10, 30),
                'ambient_color': [0.2, 0.25, 0.3],
                'sun_color': [0.7, 0.7, 0.8],
                'fog_density': 0.3
            },
            'desert': {
                'sun_intensity': random.uniform(4, 6),
                'sun_angle': random.uniform(40, 80),
                'ambient_color': [0.6, 0.5, 0.4],
                'sun_color': [1.0, 0.9, 0.7],
                'heat_shimmer': True
            }
        }
        
        setup = lighting_setups.get(theme, lighting_setups['medieval'])
        
        return {
            'id': f"lighting_{theme}",
            'type': 'lighting_setup',
            'theme': theme,
            'settings': setup,
            'description': f"Atmospheric lighting setup for {theme} environment"
        }
    
    async def _generate_atmosphere_effects(self, theme: str) -> Dict[str, Any]:
        """Generate atmospheric effects"""
        effects = {
            'medieval': ['light_fog', 'dust_motes', 'wind'],
            'fantasy': ['magical_sparkles', 'floating_particles', 'aurora'],
            'spooky': ['heavy_fog', 'mist', 'shadows', 'eerie_glow'],
            'desert': ['heat_waves', 'sand_particles', 'mirages']
        }
        
        available_effects = effects.get(theme, ['light_fog'])
        selected_effect = random.choice(available_effects)
        
        return {
            'id': f"atmosphere_{theme}_{selected_effect}",
            'type': 'atmospheric_effect',
            'effect_type': selected_effect,
            'theme': theme,
            'intensity': random.uniform(0.3, 0.8),
            'description': f"{selected_effect.replace('_', ' ').title()} effect for {theme} atmosphere"
        }
    
    async def _generate_ambient_sounds(self, theme: str) -> Dict[str, Any]:
        """Generate ambient sound profile"""
        sound_profiles = {
            'medieval': ['birds_chirping', 'wind_through_trees', 'distant_bells'],
            'fantasy': ['magical_chimes', 'mystical_whispers', 'ethereal_music'],
            'spooky': ['owls_hooting', 'creaking_wood', 'distant_howls', 'eerie_silence'],
            'desert': ['wind_through_sand', 'distant_drums', 'camel_bells']
        }
        
        sounds = sound_profiles.get(theme, ['nature_ambience'])
        
        return {
            'id': f"ambient_sounds_{theme}",
            'type': 'ambient_sounds',
            'sound_list': sounds,
            'theme': theme,
            'volume': random.uniform(0.2, 0.6),
            'description': f"Ambient soundscape for {theme} environment"
        }
    
    async def _generate_ambient_props(self, world_spec: Dict[str, Any], theme: str) -> List[Dict]:
        """Generate small ambient props scattered throughout the world"""
        ambient_props = []
        
        size = world_spec.get('size', (40, 40))
        
        # Generate scattered small props
        prop_types = {
            'medieval': ['barrel', 'cart', 'fence_post', 'milestone', 'campfire'],
            'fantasy': ['crystal_formation', 'rune_stone', 'magical_circle', 'fairy_ring'],
            'spooky': ['gravestone', 'dead_branch', 'cauldron', 'skull', 'thorny_vine'],
            'desert': ['cactus', 'sun_dial', 'nomad_tent', 'bone', 'sand_dune']
        }
        
        available_props = prop_types.get(theme, ['generic_prop'])
        num_props = random.randint(3, 8)
        
        for i in range(num_props):
            prop_type = random.choice(available_props)
            
            # Random position
            x = random.uniform(2, size[0] - 2)
            y = random.uniform(2, size[1] - 2)
            
            ambient_prop = {
                'id': f"ambient_{prop_type}_{i}",
                'type': 'ambient_prop',
                'prop_type': prop_type,
                'position': {'x': x, 'y': y, 'z': 0},
                'description': f"A {theme} {prop_type} adding atmosphere to the environment",
                'scale': random.uniform(0.8, 1.2)
            }
            
            ambient_props.append(ambient_prop)
        
        return ambient_props