"""
BUILDING GENERATOR MODULE
Specialized module for generating architectural assets
Handles houses, taverns, churches, shops, and other building types
"""

import random
import hashlib
from typing import Dict, List, Any
from pathlib import Path
import logging

class BuildingGenerator:
    """
    Specialized building generation module
    Handles all architectural assets and building creation
    """
    
    def __init__(self, output_dir: Path, ai_core):
        self.output_dir = output_dir
        self.ai_core = ai_core
        self.logger = logging.getLogger(__name__)
        
        # Building-specific directories
        self.scripts_dir = output_dir / "blender_scripts"
        self.models_dir = output_dir / "models"
        self.scripts_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
    
    async def generate_ai_creative_buildings(self, buildings: List[Dict], theme: str) -> List[Dict]:
        """Generate AI-creative buildings with unique architectural designs"""
        creative_buildings = []
        
        for i, building in enumerate(buildings):
            building_type = building.get('type', 'house')
            position = building.get('position', {'x': 0, 'y': 0, 'z': 0})
            
            # Generate AI creative description
            ai_description = await self.ai_core.generate_building_description(building_type, theme, i)
            
            # Generate creative variations
            variations = await self.ai_core.generate_building_variations(building_type, theme)
            
            # Generate unique architectural style parameters
            style_params = await self._generate_building_style(building_type, theme)
            
            # Generate AI textures for building
            building_textures = await self._generate_building_textures(building_type, theme, ai_description, i)
            
            # Generate geometry parameters
            geometry_params = await self.ai_core.generate_geometry_parameters(building_type, ai_description)
            
            # Generate architectural details
            architectural_details = await self._generate_architectural_details(building_type, theme, style_params)
            
            # Create building script
            script_content = self._create_building_script(
                building, theme, ai_description, variations, style_params,
                building_textures, geometry_params, architectural_details, i
            )
            
            building_id = f"{building_type}_{i}_{position['x']}_{position['y']}"
            script_path = self.scripts_dir / f"ai_building_{building_id}.py"
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            creative_buildings.append({
                'id': building_id,
                'type': building_type,
                'position': position,
                'ai_description': ai_description,
                'creative_variations': variations,
                'style_parameters': style_params,
                'geometry_parameters': geometry_params,
                'architectural_details': architectural_details,
                'unique_textures': building_textures,
                'script_path': str(script_path),
                'creativity_score': len(variations) + len(building_textures) + len(architectural_details),
                'uniqueness_id': hashlib.md5(f"{ai_description}{style_params}".encode()).hexdigest()[:8]
            })
        
        return creative_buildings
    
    async def _generate_building_style(self, building_type: str, theme: str) -> Dict[str, Any]:
        """Generate unique architectural style parameters"""
        # Base architectural styles with theme variations
        base_styles = {
            'house': {
                'roof_type': random.choice(['gabled', 'hipped', 'flat', 'shed', 'gambrel']),
                'wall_material': random.choice(['wood', 'stone', 'brick', 'timber_frame']),
                'foundation': random.choice(['stone', 'brick', 'concrete', 'raised']),
                'window_style': random.choice(['casement', 'double_hung', 'bay', 'dormer']),
                'door_style': random.choice(['single', 'double', 'arched', 'reinforced']),
                'chimney': random.choice(['none', 'single', 'double', 'ornate']),
                'stories': random.choice([1, 1, 2, 2, 3]),  # Weighted toward 1-2 stories
                'architectural_style': random.choice(['cottage', 'farmhouse', 'tudor', 'colonial'])
            },
            'tavern': {
                'roof_type': random.choice(['gabled', 'hipped', 'gambrel']),
                'wall_material': random.choice(['timber_frame', 'stone', 'brick']),
                'foundation': random.choice(['stone', 'brick']),
                'window_style': random.choice(['casement', 'bay', 'leaded_glass']),
                'door_style': random.choice(['double', 'arched', 'heavy_wood']),
                'chimney': random.choice(['single', 'double', 'ornate']),
                'stories': random.choice([2, 2, 3]),  # Usually multi-story
                'special_features': random.choice(['balcony', 'porch', 'sign_post', 'outdoor_seating']),
                'architectural_style': random.choice(['inn', 'public_house', 'roadhouse'])
            },
            'church': {
                'roof_type': random.choice(['gabled', 'vaulted', 'spired']),
                'wall_material': random.choice(['stone', 'brick', 'marble']),
                'foundation': 'stone',  # Churches typically have stone foundations
                'window_style': random.choice(['gothic', 'rose', 'stained_glass', 'arched']),
                'door_style': random.choice(['arched', 'ornate', 'double_arched']),
                'tower': random.choice(['bell_tower', 'spire', 'dome', 'none']),
                'stories': random.choice([1, 2]),
                'special_features': random.choice(['flying_buttresses', 'rose_window', 'bell', 'cross']),
                'architectural_style': random.choice(['gothic', 'romanesque', 'byzantine', 'chapel'])
            },
            'shop': {
                'roof_type': random.choice(['gabled', 'flat', 'shed']),
                'wall_material': random.choice(['wood', 'brick', 'stone']),
                'foundation': random.choice(['stone', 'brick', 'raised']),
                'window_style': random.choice(['storefront', 'display', 'large_pane']),
                'door_style': random.choice(['single', 'double', 'sliding']),
                'chimney': random.choice(['none', 'single']),
                'stories': random.choice([1, 1, 2]),  # Usually 1-2 stories
                'special_features': random.choice(['awning', 'display_window', 'hanging_sign', 'workshop']),
                'architectural_style': random.choice(['merchant', 'craftsman', 'market_stall'])
            }
        }
        
        # Get base style or use house as default
        style_params = base_styles.get(building_type, base_styles['house']).copy()
        
        # Apply theme-specific modifications
        if theme in ['spooky', 'halloween']:
            style_params['condition'] = random.choice(['weathered', 'decrepit', 'haunted', 'abandoned'])
            style_params['special_features'] = random.choice(['boarded_windows', 'cracked_walls', 'overgrown', 'mysterious'])
        elif theme == 'fantasy':
            style_params['magical_elements'] = random.choice(['glowing_windows', 'crystal_accents', 'floating_stones', 'enchanted'])
            style_params['special_features'] = random.choice(['tower_addition', 'mystical_symbols', 'garden', 'workshop'])
        elif theme == 'desert':
            style_params['wall_material'] = random.choice(['adobe', 'sandstone', 'mud_brick'])
            style_params['roof_type'] = random.choice(['flat', 'low_pitched'])
            style_params['special_features'] = random.choice(['courtyard', 'shade_structure', 'water_feature'])
        elif theme == 'medieval':
            style_params['defensive_features'] = random.choice(['none', 'reinforced_door', 'small_windows', 'fortified'])
            
        return style_params
    
    async def _generate_building_textures(self, building_type: str, theme: str, description: str, index: int) -> Dict[str, str]:
        """Generate AI-unique textures for buildings"""
        textures = {}
        
        # Standard building textures
        textures['walls'] = await self._generate_building_texture(f"{description} walls", 'stone', theme, index)
        textures['roof'] = await self._generate_building_texture(f"{description} roof", 'wood', theme, index)
        textures['foundation'] = await self._generate_building_texture(f"{description} foundation", 'stone', theme, index)
        
        # Building-type specific textures
        if building_type == 'tavern':
            textures['sign'] = await self._generate_building_texture(f"{description} tavern sign", 'wood', theme, index)
            textures['door'] = await self._generate_building_texture(f"{description} heavy door", 'wood', theme, index)
        elif building_type == 'church':
            textures['stained_glass'] = await self._generate_building_texture(f"{description} stained glass", 'glass', theme, index)
            textures['altar'] = await self._generate_building_texture(f"{description} altar", 'stone', theme, index)
        elif building_type == 'shop':
            textures['counter'] = await self._generate_building_texture(f"{description} shop counter", 'wood', theme, index)
            textures['shelving'] = await self._generate_building_texture(f"{description} shelving", 'wood', theme, index)
        
        return {k: v for k, v in textures.items() if v}
    
    async def _generate_building_texture(self, description: str, texture_type: str, theme: str, index: int) -> str:
        """Generate building-specific texture"""
        # This would integrate with the texture generator module
        # For now, return a placeholder path
        texture_id = hashlib.md5(f"{description}_{texture_type}_{theme}_{index}".encode()).hexdigest()[:8]
        return f"textures/buildings/{texture_type}_{theme}_{texture_id}.png"
    
    async def _generate_architectural_details(self, building_type: str, theme: str, style_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed architectural elements"""
        details = {}
        
        # Standard architectural details
        details['dimensions'] = {
            'width': random.uniform(8, 20),
            'length': random.uniform(10, 25),
            'height': random.uniform(8, 15) * style_params.get('stories', 1)
        }
        
        details['structural_elements'] = {
            'support_beams': style_params.get('wall_material') == 'timber_frame',
            'load_bearing_walls': True,
            'foundation_depth': random.uniform(2, 4)
        }
        
        # Roof details
        roof_type = style_params.get('roof_type', 'gabled')
        details['roof_details'] = {
            'type': roof_type,
            'pitch': random.uniform(30, 45) if roof_type in ['gabled', 'hipped'] else 0,
            'material': random.choice(['thatch', 'slate', 'wood_shingle', 'tile']),
            'overhang': random.uniform(0.5, 2.0)
        }
        
        # Window and door details
        details['openings'] = {
            'window_count': random.randint(2, 8),
            'door_count': 1 if building_type != 'tavern' else random.randint(1, 2),
            'window_size': random.choice(['small', 'medium', 'large']),
            'door_width': random.uniform(0.8, 1.2),
            'window_placement': random.choice(['regular', 'asymmetric', 'grouped'])
        }
        
        # Building-specific details
        if building_type == 'church':
            details['religious_elements'] = {
                'altar_position': 'east',
                'nave_length': details['dimensions']['length'] * 0.7,
                'sanctuary_area': True,
                'bell_tower_height': random.uniform(20, 40) if style_params.get('tower') == 'bell_tower' else 0
            }
        elif building_type == 'tavern':
            details['commercial_elements'] = {
                'common_room_size': details['dimensions']['width'] * details['dimensions']['length'] * 0.6,
                'kitchen_area': True,
                'guest_rooms': random.randint(2, 6),
                'storage_area': True
            }
        elif building_type == 'shop':
            details['commercial_elements'] = {
                'shop_floor_area': details['dimensions']['width'] * details['dimensions']['length'] * 0.7,
                'storage_area': True,
                'workshop_area': random.choice([True, False]),
                'display_area': True
            }
        
        # Theme-specific details
        if theme == 'fantasy':
            details['magical_elements'] = {
                'enchanted_features': random.choice(['glowing_runes', 'floating_objects', 'magical_lights']),
                'crystal_accents': random.choice([True, False]),
                'mystical_garden': random.choice([True, False])
            }
        elif theme in ['spooky', 'halloween']:
            details['atmospheric_elements'] = {
                'weathering': random.choice(['severe', 'moderate', 'light']),
                'overgrowth': random.choice([True, False]),
                'mysterious_features': random.choice(['strange_sounds', 'moving_shadows', 'cold_spots'])
            }
        
        return details
    
    def _create_building_script(self, building: Dict, theme: str, ai_description: str,
                               variations: List[str], style_params: Dict[str, Any],
                               textures: Dict[str, str], geometry_params: Dict[str, Any],
                               architectural_details: Dict[str, Any], index: int) -> str:
        """Create comprehensive building generation script"""
        building_type = building.get('type', 'house')
        position = building.get('position', {'x': 0, 'y': 0, 'z': 0})
        
        # Create texture assignments
        texture_assignments = []
        for key, path in textures.items():
            texture_assignments.append(f'"{key}": "{path}"')
        texture_dict = "{" + ", ".join(texture_assignments) + "}"
        
        # Extract parameters
        dimensions = architectural_details.get('dimensions', {'width': 10, 'length': 12, 'height': 8})
        roof_details = architectural_details.get('roof_details', {'type': 'gabled', 'pitch': 35})
        openings = architectural_details.get('openings', {'window_count': 4, 'door_count': 1})
        
        # Style parameters
        roof_type = style_params.get('roof_type', 'gabled')
        wall_material = style_params.get('wall_material', 'stone')
        stories = style_params.get('stories', 1)
        
        return f'''
import bpy
import bmesh
import random
import math
from mathutils import Vector

# AI-GENERATED CREATIVE BUILDING
# Building #{index + 1}: {building_type}
# AI Description: {ai_description}
# Style Parameters: {style_params}
# Architectural Details: {architectural_details}

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# AI Texture paths
ai_textures = {texture_dict}

# Building Parameters
BUILDING_WIDTH = {dimensions['width']}
BUILDING_LENGTH = {dimensions['length']}
BUILDING_HEIGHT = {dimensions['height']}
STORIES = {stories}
ROOF_TYPE = "{roof_type}"
WALL_MATERIAL = "{wall_material}"

# Position
POS_X = {position['x']}
POS_Y = {position['y']}
POS_Z = {position['z']}

print(f"🏗️ Creating AI-Designed {building_type}:")
print(f"   📐 Dimensions: {{BUILDING_WIDTH:.1f}} x {{BUILDING_LENGTH:.1f}} x {{BUILDING_HEIGHT:.1f}}")
print(f"   🏠 Stories: {{STORIES}}")
print(f"   🏠 Roof: {{ROOF_TYPE}}")
print(f"   🧱 Material: {{WALL_MATERIAL}}")

def create_ai_building():
    """Create complete AI-designed building"""
    building_objects = []
    
    # Create foundation
    foundation = create_foundation()
    if foundation:
        building_objects.append(foundation)
    
    # Create walls for each story
    for story in range(STORIES):
        story_height = BUILDING_HEIGHT / STORIES
        story_walls = create_story_walls(story, story_height)
        building_objects.extend(story_walls)
    
    # Create roof
    roof = create_roof()
    if roof:
        building_objects.append(roof)
    
    # Add architectural details
    details = create_architectural_details()
    building_objects.extend(details)
    
    # Join all building components
    if len(building_objects) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in building_objects:
            if obj and obj.name in bpy.data.objects:
                obj.select_set(True)
        
        if building_objects:
            bpy.context.view_layer.objects.active = building_objects[0]
            bpy.ops.object.join()
            
            final_building = bpy.context.active_object
            final_building.name = f"AI_{building_type}_{index}"
            final_building.location = (POS_X, POS_Y, POS_Z)
            
            print(f"✅ Created AI {building_type} with {{len(building_objects)}} components")
    
    return building_objects

def create_foundation():
    """Create building foundation"""
    foundation_height = 0.5
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, foundation_height/2)
    )
    foundation = bpy.context.active_object
    foundation.scale = (BUILDING_WIDTH, BUILDING_LENGTH, foundation_height)
    bpy.ops.object.transform_apply(scale=True)
    foundation.name = f"AI_foundation_{index}"
    
    return foundation

def create_story_walls(story_number: int, story_height: float):
    """Create walls for a specific story"""
    story_objects = []
    base_z = 0.5 + (story_number * story_height)  # Account for foundation
    
    # Wall thickness
    wall_thickness = 0.3
    
    # Create four walls
    walls_data = [
        {{'name': 'front', 'size': (BUILDING_WIDTH, wall_thickness, story_height), 
          'pos': (0, -BUILDING_LENGTH/2 + wall_thickness/2, base_z + story_height/2)}},
        {{'name': 'back', 'size': (BUILDING_WIDTH, wall_thickness, story_height),
          'pos': (0, BUILDING_LENGTH/2 - wall_thickness/2, base_z + story_height/2)}},
        {{'name': 'left', 'size': (wall_thickness, BUILDING_LENGTH - wall_thickness, story_height),
          'pos': (-BUILDING_WIDTH/2 + wall_thickness/2, 0, base_z + story_height/2)}},
        {{'name': 'right', 'size': (wall_thickness, BUILDING_LENGTH - wall_thickness, story_height),
          'pos': (BUILDING_WIDTH/2 - wall_thickness/2, 0, base_z + story_height/2)}}
    ]
    
    for wall_data in walls_data:
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=wall_data['pos']
        )
        wall = bpy.context.active_object
        wall.scale = wall_data['size']
        bpy.ops.object.transform_apply(scale=True)
        wall.name = f"AI_wall_{{wall_data['name']}}_story{{story_number}}_{index}"
        story_objects.append(wall)
    
    # Add windows and doors for ground floor
    if story_number == 0:
        openings = create_openings(base_z, story_height)
        story_objects.extend(openings)
    
    return story_objects

def create_roof():
    """Create building roof based on roof type"""
    roof_base_z = 0.5 + (STORIES * (BUILDING_HEIGHT / STORIES))
    
    if ROOF_TYPE == "gabled":
        return create_gabled_roof(roof_base_z)
    elif ROOF_TYPE == "hipped":
        return create_hipped_roof(roof_base_z)
    elif ROOF_TYPE == "flat":
        return create_flat_roof(roof_base_z)
    else:
        return create_gabled_roof(roof_base_z)  # Default

def create_gabled_roof(base_z: float):
    """Create a gabled roof"""
    roof_height = {roof_details.get('pitch', 35) * 0.1}  # Convert pitch to height factor
    roof_peak_height = roof_height * (BUILDING_WIDTH / 2)
    
    # Create roof as a triangular prism
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, base_z + roof_peak_height/2)
    )
    roof = bpy.context.active_object
    roof.scale = (BUILDING_WIDTH + 1, BUILDING_LENGTH + 1, roof_peak_height)
    bpy.ops.object.transform_apply(scale=True)
    
    # Convert to mesh and create gabled shape
    bpy.context.view_layer.objects.active = roof
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select top face and extrude to create peak
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
    bpy.ops.mesh.inset_faces(thickness=BUILDING_WIDTH/4)
    bpy.ops.mesh.extrude_region_move(
        TRANSFORM_OT_translate={{"value": (0, 0, roof_peak_height/2)}}
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
    roof.name = f"AI_gabled_roof_{index}"
    
    return roof

def create_hipped_roof(base_z: float):
    """Create a hipped roof"""
    roof_height = {roof_details.get('pitch', 35) * 0.08}
    roof_peak_height = roof_height * min(BUILDING_WIDTH, BUILDING_LENGTH) / 2
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, base_z + roof_peak_height/2)
    )
    roof = bpy.context.active_object
    roof.scale = (BUILDING_WIDTH + 1, BUILDING_LENGTH + 1, roof_peak_height)
    bpy.ops.object.transform_apply(scale=True)
    roof.name = f"AI_hipped_roof_{index}"
    
    return roof

def create_flat_roof(base_z: float):
    """Create a flat roof"""
    roof_thickness = 0.3
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, base_z + roof_thickness/2)
    )
    roof = bpy.context.active_object
    roof.scale = (BUILDING_WIDTH + 0.5, BUILDING_LENGTH + 0.5, roof_thickness)
    bpy.ops.object.transform_apply(scale=True)
    roof.name = f"AI_flat_roof_{index}"
    
    return roof

def create_openings(base_z: float, story_height: float):
    """Create windows and doors"""
    openings = []
    
    # Create main door
    door_width = 1.0
    door_height = 2.0
    door_depth = 0.1
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, -BUILDING_LENGTH/2 - door_depth/2, base_z + door_height/2)
    )
    door = bpy.context.active_object
    door.scale = (door_width, door_depth, door_height)
    bpy.ops.object.transform_apply(scale=True)
    door.name = f"AI_door_{index}"
    openings.append(door)
    
    # Create windows
    window_count = {openings.get('window_count', 4)}
    window_size = 0.8
    window_height = 1.2
    window_depth = 0.05
    
    for i in range(window_count):
        # Distribute windows around the building
        if i < 2:  # Front wall windows
            x_pos = (-BUILDING_WIDTH/3) + (i * (2*BUILDING_WIDTH/3))
            y_pos = -BUILDING_LENGTH/2 - window_depth/2
        else:  # Side wall windows
            side = i - 2
            x_pos = (-BUILDING_WIDTH/2 - window_depth/2) if side == 0 else (BUILDING_WIDTH/2 + window_depth/2)
            y_pos = (-BUILDING_LENGTH/4) + (side * (BUILDING_LENGTH/2))
        
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(x_pos, y_pos, base_z + story_height * 0.6)
        )
        window = bpy.context.active_object
        window.scale = (window_size, window_depth, window_height)
        bpy.ops.object.transform_apply(scale=True)
        window.name = f"AI_window_{{i}}_{index}"
        openings.append(window)
    
    return openings

def create_architectural_details():
    """Create building-specific architectural details"""
    details = []
    
    # Add chimney if specified
    chimney_type = "{style_params.get('chimney', 'none')}"
    if chimney_type != "none":
        chimney = create_chimney()
        if chimney:
            details.append(chimney)
    
    # Add building-type specific details
    if "{building_type}" == "tavern":
        # Add tavern sign
        sign = create_tavern_sign()
        if sign:
            details.append(sign)
    elif "{building_type}" == "church":
        # Add cross or religious symbol
        symbol = create_religious_symbol()
        if symbol:
            details.append(symbol)
    elif "{building_type}" == "shop":
        # Add shop awning
        awning = create_shop_awning()
        if awning:
            details.append(awning)
    
    return details

def create_chimney():
    """Create a chimney"""
    chimney_width = 0.8
    chimney_height = 2.5
    roof_top_z = 0.5 + (STORIES * (BUILDING_HEIGHT / STORIES)) + 1.0  # Approximate roof height
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(BUILDING_WIDTH/3, BUILDING_LENGTH/3, roof_top_z + chimney_height/2)
    )
    chimney = bpy.context.active_object
    chimney.scale = (chimney_width, chimney_width, chimney_height)
    bpy.ops.object.transform_apply(scale=True)
    chimney.name = f"AI_chimney_{index}"
    
    return chimney

def create_tavern_sign():
    """Create a tavern sign"""
    sign_post_height = 3.0
    sign_width = 1.5
    sign_height = 0.8
    
    # Sign post
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.05,
        depth=sign_post_height,
        location=(BUILDING_WIDTH/2 + 1, -BUILDING_LENGTH/2 - 0.5, sign_post_height/2)
    )
    post = bpy.context.active_object
    post.name = f"AI_sign_post_{index}"
    
    # Sign board
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(BUILDING_WIDTH/2 + 1, -BUILDING_LENGTH/2 - 0.5, sign_post_height * 0.7)
    )
    sign = bpy.context.active_object
    sign.scale = (sign_width, 0.1, sign_height)
    bpy.ops.object.transform_apply(scale=True)
    sign.name = f"AI_sign_board_{index}"
    
    return post  # Return one object, they'll be joined later

def create_religious_symbol():
    """Create a religious symbol for church"""
    symbol_height = 1.5
    roof_top_z = 0.5 + (STORIES * (BUILDING_HEIGHT / STORIES)) + 1.5
    
    # Simple cross
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, roof_top_z + symbol_height/2)
    )
    cross_vertical = bpy.context.active_object
    cross_vertical.scale = (0.1, 0.1, symbol_height)
    bpy.ops.object.transform_apply(scale=True)
    cross_vertical.name = f"AI_cross_vertical_{index}"
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, roof_top_z + symbol_height * 0.7)
    )
    cross_horizontal = bpy.context.active_object
    cross_horizontal.scale = (0.6, 0.1, 0.1)
    bpy.ops.object.transform_apply(scale=True)
    cross_horizontal.name = f"AI_cross_horizontal_{index}"
    
    return cross_vertical

def create_shop_awning():
    """Create a shop awning"""
    awning_width = BUILDING_WIDTH * 0.8
    awning_depth = 1.0
    awning_height = 0.1
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, -BUILDING_LENGTH/2 - awning_depth/2, (BUILDING_HEIGHT / STORIES) * 0.8)
    )
    awning = bpy.context.active_object
    awning.scale = (awning_width, awning_depth, awning_height)
    bpy.ops.object.transform_apply(scale=True)
    awning.name = f"AI_awning_{index}"
    
    return awning

# Execute the building creation
try:
    created_objects = create_ai_building()
    print(f"✅ Successfully created AI {building_type} with {{len(created_objects)}} components")
    print(f"🏗️ Architectural Style: {style_params}")
    print(f"📐 Dimensions: {{BUILDING_WIDTH}} x {{BUILDING_LENGTH}} x {{BUILDING_HEIGHT}}")
    print(f"🎯 Variations: {len(variations)}")
except Exception as e:
    print(f"❌ Error creating AI {building_type}: {{e}}")
    import traceback
    traceback.print_exc()

print("🏗️ AI-Creative Building Generation Script Complete!")
'''