"""
PROP GENERATOR MODULE
Specialized module for generating natural features and props
Handles trees, rocks, bushes, wells, and other environmental objects
"""

import random
import hashlib
import math
from typing import Dict, List, Any
from pathlib import Path
import logging

class PropGenerator:
    """
    Specialized prop generation module
    Handles all natural features and environmental props
    """
    
    def __init__(self, output_dir: Path, ai_core):
        self.output_dir = output_dir
        self.ai_core = ai_core
        self.logger = logging.getLogger(__name__)
        
        # Prop-specific directories
        self.scripts_dir = output_dir / "blender_scripts"
        self.scripts_dir.mkdir(exist_ok=True)
        
        # Shared with texture generator
        self.texture_cache = {}
    
    async def generate_ai_creative_props(self, props: List[Dict], theme: str) -> List[Dict]:
        """Generate AI-creative props with unique designs"""
        creative_props = []
        
        for i, prop in enumerate(props):
            prop_type = prop.get('type', 'tree')
            position = prop.get('position', {'x': 0, 'y': 0, 'z': 0})
            
            # Generate AI creative description
            ai_description = await self.ai_core.generate_prop_description(prop_type, theme, i)
            
            # Generate creative variations
            variations = await self.ai_core.generate_prop_variations(prop_type, theme)
            
            # Generate unique style parameters (FIXED with all defaults)
            style_params = await self._generate_ai_prop_style(prop_type, theme)
            
            # Generate AI textures
            prop_textures = await self._generate_ai_prop_textures(prop_type, theme, ai_description, i)
            
            # Generate geometry parameters
            geometry_params = await self.ai_core.generate_geometry_parameters(prop_type, ai_description)
            
            # Create creative script
            script_content = self._create_ai_creative_prop_script(
                prop, theme, ai_description, variations, style_params, 
                prop_textures, geometry_params, i
            )
            
            prop_id = f"{prop_type}_{i}_{position['x']}_{position['y']}"
            script_path = self.scripts_dir / f"ai_prop_{prop_id}.py"
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            creative_props.append({
                'id': prop_id,
                'type': prop_type,
                'position': position,
                'ai_description': ai_description,
                'creative_variations': variations,
                'style_parameters': style_params,
                'geometry_parameters': geometry_params,
                'unique_textures': prop_textures,
                'script_path': str(script_path),
                'creativity_score': len(variations) + len(prop_textures),
                'uniqueness_id': hashlib.md5(f"{ai_description}{style_params}".encode()).hexdigest()[:8]
            })
        
        return creative_props

    async def _generate_ai_prop_style(self, prop_type: str, theme: str) -> Dict[str, Any]:
        """FIXED: Generate unique style parameters for props with all required defaults"""
        # Base style templates with ALL required parameters
        base_styles = {
            'tree': {
                'trunk_style': random.choice(['straight', 'twisted', 'gnarled', 'split']),
                'canopy_shape': random.choice(['round', 'oval', 'irregular', 'sparse']),
                'branch_density': random.choice(['sparse', 'medium', 'dense']),
                'leaf_type': random.choice(['broad', 'needle', 'palm', 'none']),
                'seasonal_state': random.choice(['spring', 'summer', 'autumn', 'winter']),
                'bark_texture': random.choice(['smooth', 'rough', 'scarred', 'mossy']),
                'height_variation': random.choice(['dwarf', 'normal', 'tall', 'giant'])
            },
            'oak_tree': {
                'trunk_style': random.choice(['straight', 'twisted', 'gnarled', 'split']),
                'canopy_shape': random.choice(['round', 'oval', 'irregular', 'sparse']),
                'branch_density': random.choice(['sparse', 'medium', 'dense']),
                'leaf_type': 'broad',  # Oak trees have broad leaves
                'seasonal_state': random.choice(['spring', 'summer', 'autumn', 'winter']),
                'bark_texture': random.choice(['rough', 'deeply_furrowed', 'scarred']),
                'height_variation': random.choice(['normal', 'tall', 'ancient'])
            },
            'rock': {
                'shape': random.choice(['rounded', 'angular', 'flat', 'crystalline']),
                'surface': random.choice(['smooth', 'rough', 'cracked', 'mossy']),
                'size_category': random.choice(['small', 'medium', 'large', 'boulder']),
                'formation': random.choice(['single', 'cluster', 'outcrop', 'pile']),
                'weathering': random.choice(['fresh', 'weathered', 'ancient', 'eroded']),
                'mineral_type': random.choice(['granite', 'limestone', 'sandstone', 'basalt'])
            },
            'bush': {
                'shape': random.choice(['round', 'oval', 'spreading', 'upright']),
                'density': random.choice(['sparse', 'medium', 'thick', 'overgrown']),
                'leaf_size': random.choice(['small', 'medium', 'large']),
                'flowering': random.choice(['none', 'spring', 'summer', 'year_round']),
                'berry_type': random.choice(['none', 'red', 'blue', 'purple', 'black']),
                'thorns': random.choice(['none', 'light', 'heavy'])
            },
            'well': {
                'construction': random.choice(['stone', 'brick', 'wood', 'metal']),
                'roof_style': random.choice(['none', 'wooden', 'tiled', 'thatched']),
                'bucket_system': random.choice(['rope', 'chain', 'pulley', 'crank']),
                'water_level': random.choice(['high', 'medium', 'low', 'dry']),
                'decoration': random.choice(['plain', 'carved', 'painted', 'ivy_covered']),
                'age': random.choice(['new', 'weathered', 'ancient', 'crumbling'])
            }
        }
        
        # Get base style or create generic one
        if prop_type in base_styles:
            style_params = base_styles[prop_type].copy()
        elif prop_type in ['tree', 'oak_tree', 'dead_tree', 'palm_tree']:
            style_params = base_styles['tree'].copy()
            # Adjust for specific tree types
            if prop_type == 'dead_tree':
                style_params['leaf_type'] = 'none'
                style_params['seasonal_state'] = 'dead'
                style_params['bark_texture'] = 'cracked'
            elif prop_type == 'palm_tree':
                style_params['canopy_shape'] = 'palm_fronds'
                style_params['leaf_type'] = 'palm'
                style_params['trunk_style'] = 'curved'
        else:
            # Generic style for unknown prop types
            style_params = {
                'shape': random.choice(['round', 'angular', 'organic', 'geometric']),
                'size': random.choice(['small', 'medium', 'large']),
                'texture': random.choice(['smooth', 'rough', 'detailed', 'weathered']),
                'color_scheme': random.choice(['natural', 'vibrant', 'muted', 'monochrome']),
                'complexity': random.choice(['simple', 'moderate', 'complex', 'intricate'])
            }
        
        # Theme-specific modifications
        if theme in ['spooky', 'halloween']:
            if 'seasonal_state' in style_params:
                style_params['seasonal_state'] = random.choice(['autumn', 'dead', 'withered'])
            if 'surface' in style_params:
                style_params['surface'] = random.choice(['cracked', 'mossy', 'weathered'])
        elif theme == 'desert':
            if 'weathering' in style_params:
                style_params['weathering'] = random.choice(['sandblasted', 'sun_bleached', 'eroded'])
        
        return style_params

    async def _generate_ai_prop_textures(self, prop_type: str, theme: str, description: str, index: int) -> Dict[str, str]:
        """Generate AI-unique textures for props"""
        textures = {}
        
        # Tree textures
        if prop_type in ['tree', 'oak_tree', 'dead_tree', 'palm_tree']:
            textures['bark'] = await self._generate_unique_ai_texture(f"{description} bark", 'wood', theme, index)
            if prop_type != 'dead_tree':
                textures['leaves'] = await self._generate_unique_ai_texture(f"{description} leaves", 'foliage', theme, index)
        
        # Rock textures
        elif prop_type in ['rock', 'stone', 'boulder']:
            textures['surface'] = await self._generate_unique_ai_texture(f"{description} stone", 'stone', theme, index)
        
        # Bush textures
        elif prop_type in ['bush', 'shrub', 'plant']:
            textures['foliage'] = await self._generate_unique_ai_texture(f"{description} foliage", 'foliage', theme, index)
        
        # Well textures
        elif prop_type == 'well':
            textures['stone'] = await self._generate_unique_ai_texture(f"{description} well stone", 'stone', theme, index)
            if 'wood' in description.lower():
                textures['wood'] = await self._generate_unique_ai_texture(f"{description} well wood", 'wood', theme, index)
        else:
            textures['surface'] = await self._generate_unique_ai_texture(f"{description} surface", 'generic', theme, index)
        
        return {k: v for k, v in textures.items() if v}

    async def _generate_unique_ai_texture(self, description: str, texture_type: str, theme: str, index: int) -> str:
        """Generate a unique AI texture"""
        # Create unique texture identifier
        texture_id = hashlib.md5(f"{description}_{texture_type}_{theme}_{index}".encode()).hexdigest()[:8]
        texture_filename = f"{texture_type}_{theme}_{texture_id}.png"
        texture_path = self.output_dir / "ai_textures" / texture_filename
        
        # Check cache first
        cache_key = f"{texture_type}_{theme}_{index}"
        if cache_key in self.texture_cache:
            return str(self.texture_cache[cache_key])
        
        # Generate procedural texture (placeholder - would integrate with texture generator)
        try:
            # This would call the texture generator module
            from PIL import Image
            
            # Simple placeholder texture
            size = (256, 256)
            color = (128, 128, 128)  # Gray placeholder
            image = Image.new('RGB', size, color)
            
            # Ensure directory exists
            texture_path.parent.mkdir(exist_ok=True)
            image.save(texture_path)
            
            # Cache the result
            self.texture_cache[cache_key] = texture_path
            
            return str(texture_path)
            
        except Exception as e:
            self.logger.warning(f"Texture generation failed: {e}")
            return self._create_fallback_texture(texture_type, theme, texture_path)

    def _create_fallback_texture(self, texture_type: str, theme: str, texture_path: Path) -> str:
        """Create simple fallback texture"""
        try:
            from PIL import Image
            size = (64, 64)
            color = (128, 128, 128)  # Gray fallback
            
            image = Image.new('RGB', size, color)
            texture_path.parent.mkdir(exist_ok=True)
            image.save(texture_path)
            return str(texture_path)
        except Exception:
            return "textures/fallback.png"

    def _create_ai_creative_prop_script(self, prop: Dict, theme: str, ai_description: str, 
                                      variations: List[str], style_params: Dict[str, Any], 
                                      textures: Dict[str, str], geometry_params: Dict[str, Any], 
                                      index: int) -> str:
        """FIXED: Create AI-creative prop script with proper variable substitution"""
        prop_type = prop.get('type', 'tree')
        position = prop.get('position', {'x': 0, 'y': 0, 'z': 0})
        
        # Create texture assignments with proper escaping
        texture_assignments = []
        for key, path in textures.items():
            texture_assignments.append(f'"{key}": "{path}"')
        texture_dict = "{" + ", ".join(texture_assignments) + "}"
        
        # Extract geometry parameters with defaults
        height_mult = geometry_params.get('height_multiplier', 1.0)
        width_mult = geometry_params.get('width_multiplier', 1.0)  
        complexity = geometry_params.get('complexity', 'medium')
        detail_count = geometry_params.get('detail_count', 3)
        asymmetry = geometry_params.get('asymmetry_factor', 0.2)
        
        # FIXED: Ensure all style parameters have defaults
        canopy_shape = style_params.get('canopy_shape', 'round')
        trunk_style = style_params.get('trunk_style', 'straight')
        rock_shape = style_params.get('shape', 'rounded')
        bush_shape = style_params.get('shape', 'round')
        
        return f'''
import bpy
import bmesh
import random
import math
from mathutils import Vector

# AI-GENERATED CREATIVE PROP
# Prop #{index + 1}: {prop_type}
# AI Description: {ai_description}
# Style Parameters: {style_params}
# Creative Variations: {len(variations)}

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# AI Texture paths
ai_textures = {texture_dict}

# AI-Generated Geometry Parameters
HEIGHT_MULT = {height_mult}
WIDTH_MULT = {width_mult}
COMPLEXITY = "{complexity}"
DETAIL_COUNT = {detail_count}
ASYMMETRY = {asymmetry}

print(f"🎨 Creating AI-Designed {prop_type}:")
print(f"   📐 Height: {{HEIGHT_MULT:.2f}}x, Width: {{WIDTH_MULT:.2f}}x")
print(f"   🔧 Complexity: {{COMPLEXITY}}")
print(f"   ✨ Details: {{DETAIL_COUNT}}")
print(f"   🎭 Asymmetry: {{ASYMMETRY:.2f}}")

def create_ai_unique_{prop_type.replace(' ', '_')}():
    """Create {prop_type} with AI-determined unique characteristics"""
    
    prop_objects = []
    
    if "{prop_type}" in ["tree", "oak_tree", "dead_tree", "palm_tree"]:
        # Create AI-designed tree
        prop_objects = create_ai_tree()
        
    elif "{prop_type}" in ["rock", "stone", "boulder"]:
        # Create AI-designed rock
        prop_objects = create_ai_rock()
        
    elif "{prop_type}" in ["bush", "shrub", "plant"]:
        # Create AI-designed bush
        prop_objects = create_ai_bush()
        
    elif "{prop_type}" == "well":
        # Create AI-designed well
        prop_objects = create_ai_well()
        
    else:
        # Create generic AI prop
        prop_objects = create_ai_generic_prop()
    
    # Join all components
    if len(prop_objects) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in prop_objects:
            if obj and obj.name in bpy.data.objects:
                obj.select_set(True)
        
        if prop_objects:
            bpy.context.view_layer.objects.active = prop_objects[0]
            bpy.ops.object.join()
            
            final_prop = bpy.context.active_object
            final_prop.name = f"AI_{prop_type}_{index}"
            
            print(f"✅ Created AI {prop_type} with {{len(prop_objects)}} components")
    
    return prop_objects

def create_ai_tree():
    """Create AI-designed tree with unique characteristics"""
    tree_parts = []
    
    # Trunk parameters
    trunk_radius = 0.3 * WIDTH_MULT
    trunk_height = 3.0 * HEIGHT_MULT
    trunk_style = "{trunk_style}"
    
    if trunk_style == "twisted":
        # Create twisted trunk with multiple segments
        for i in range(max(2, DETAIL_COUNT // 2)):
            segment_height = trunk_height / max(2, DETAIL_COUNT // 2)
            twist_angle = i * (360 / max(2, DETAIL_COUNT // 2)) * ASYMMETRY
            
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=6,
                radius=trunk_radius * (1.0 - i * 0.1),
                depth=segment_height,
                location=({position['x']}, {position['y']}, i * segment_height + segment_height/2)
            )
            segment = bpy.context.active_object
            segment.name = f"AI_twisted_segment_{{i}}_{index}"
            segment.rotation_euler[2] = math.radians(twist_angle)
            tree_parts.append(segment)
            
    elif trunk_style == "gnarled":
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=trunk_radius * 1.2,
            depth=trunk_height * 0.8,
            location=({position['x']}, {position['y']}, trunk_height * 0.4)
        )
        trunk = bpy.context.active_object
        trunk.name = f"AI_gnarled_trunk_{index}"
        
        # Add gnarls (bumps)
        for i in range(DETAIL_COUNT):
            bump_radius = trunk_radius * 0.3
            angle = i * (2 * math.pi / DETAIL_COUNT)
            bump_x = {position['x']} + math.cos(angle) * trunk_radius * 0.8
            bump_y = {position['y']} + math.sin(angle) * trunk_radius * 0.8
            bump_z = random.uniform(0.5, trunk_height * 0.7)
            
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=1,
                radius=bump_radius,
                location=(bump_x, bump_y, bump_z)
            )
            bump = bpy.context.active_object
            bump.name = f"AI_gnarl_{{i}}_{index}"
            tree_parts.append(bump)
    
    elif trunk_style == "split":
        # Main trunk
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=trunk_radius,
            depth=trunk_height * 0.6,
            location=({position['x']}, {position['y']}, trunk_height * 0.3)
        )
        trunk = bpy.context.active_object
        trunk.name = f"AI_split_main_{index}"
        tree_parts.append(trunk)
        
        # Split branches
        for i in range(2):
            offset_x = (-1 if i == 0 else 1) * trunk_radius * 0.5
            offset_y = random.uniform(-trunk_radius, trunk_radius) * 0.3
            
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=6,
                radius=trunk_radius * 0.7,
                depth=trunk_height * 0.5,
                location=({position['x']} + offset_x, {position['y']} + offset_y, trunk_height * 0.75)
            )
            branch = bpy.context.active_object
            branch.name = f"AI_split_branch_{{i}}_{index}"
            branch.rotation_euler[0] = math.radians(30 + ASYMMETRY * 20)
            tree_parts.append(branch)
            
    else:  # straight
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=trunk_radius,
            depth=trunk_height,
            location=({position['x']}, {position['y']}, trunk_height/2)
        )
        trunk = bpy.context.active_object
        trunk.name = f"AI_straight_trunk_{index}"
        tree_parts.append(trunk)
    
    # Create AI-determined canopy
    canopy_shape = "{canopy_shape}"
    canopy_size = 2.5 * WIDTH_MULT
    canopy_height = trunk_height + canopy_size * 0.5
    
    if canopy_shape == "round":
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=canopy_size,
            location=({position['x']}, {position['y']}, canopy_height)
        )
        canopy = bpy.context.active_object
        canopy.name = f"AI_round_canopy_{index}"
        tree_parts.append(canopy)
        
    elif canopy_shape == "oval":
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=canopy_size,
            location=({position['x']}, {position['y']}, canopy_height)
        )
        canopy = bpy.context.active_object
        canopy.scale = (1.0, 0.7, 1.3)  # Oval shape
        bpy.ops.object.transform_apply(scale=True)
        canopy.name = f"AI_oval_canopy_{index}"
        tree_parts.append(canopy)
        
    elif canopy_shape == "irregular":
        # Create multiple overlapping spheres for irregular shape
        for i in range(DETAIL_COUNT):
            offset_x = random.uniform(-1, 1) * ASYMMETRY
            offset_y = random.uniform(-1, 1) * ASYMMETRY
            offset_z = random.uniform(-0.5, 0.5) * ASYMMETRY
            size = canopy_size * random.uniform(0.6, 1.2)
            
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=1,
                radius=size,
                location=({position['x']} + offset_x, {position['y']} + offset_y, canopy_height + offset_z)
            )
            sphere = bpy.context.active_object
            sphere.name = f"AI_irregular_canopy_{{i}}_{index}"
            tree_parts.append(sphere)
    
    elif canopy_shape == "sparse":
        # Create few separate leaf clusters
        cluster_count = max(2, DETAIL_COUNT // 2)
        for i in range(cluster_count):
            angle = (i * 2 * math.pi / cluster_count) + (ASYMMETRY * random.uniform(-0.5, 0.5))
            radius = canopy_size * 0.7
            
            cluster_x = {position['x']} + math.cos(angle) * radius
            cluster_y = {position['y']} + math.sin(angle) * radius
            cluster_z = canopy_height + random.uniform(-0.5, 0.5)
            
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=1,
                radius=canopy_size * 0.4,
                location=(cluster_x, cluster_y, cluster_z)
            )
            cluster = bpy.context.active_object
            cluster.name = f"AI_sparse_cluster_{{i}}_{index}"
            tree_parts.append(cluster)
    
    elif canopy_shape == "palm_fronds":
        # Create palm fronds
        frond_count = max(6, DETAIL_COUNT)
        for i in range(frond_count):
            angle = i * (2 * math.pi / frond_count)
            frond_length = canopy_size * 1.5
            
            frond_x = {position['x']} + math.cos(angle) * frond_length * 0.7
            frond_y = {position['y']} + math.sin(angle) * frond_length * 0.7
            frond_z = canopy_height + random.uniform(-0.2, 0.2)
            
            bpy.ops.mesh.primitive_cube_add(
                size=0.2,
                location=(frond_x, frond_y, frond_z)
            )
            frond = bpy.context.active_object
            frond.scale = (0.3, frond_length, 0.1)
            bpy.ops.object.transform_apply(scale=True)
            frond.rotation_euler[2] = angle + math.radians(90)
            frond.name = f"AI_palm_frond_{{i}}_{index}"
            tree_parts.append(frond)
    
    else:  # Default round canopy
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=canopy_size,
            location=({position['x']}, {position['y']}, canopy_height)
        )
        canopy = bpy.context.active_object
        canopy.name = f"AI_default_canopy_{index}"
        tree_parts.append(canopy)
    
    return tree_parts

def create_ai_rock():
    """Create AI-designed rock with unique characteristics"""
    rock_parts = []
    
    # Base rock
    rock_shape = "{rock_shape}"
    base_size = 1.0 * WIDTH_MULT
    rock_height = 0.8 * HEIGHT_MULT
    
    if rock_shape == "angular":
        bpy.ops.mesh.primitive_cube_add(
            size=base_size,
            location=({position['x']}, {position['y']}, rock_height/2)
        )
        rock = bpy.context.active_object
        rock.scale = (1.0, 0.8, rock_height)
        
        # Add random rotation for natural look
        rock.rotation_euler = (
            random.uniform(-0.2, 0.2) * ASYMMETRY,
            random.uniform(-0.2, 0.2) * ASYMMETRY,
            random.uniform(0, 2*math.pi) * ASYMMETRY
        )
        
    elif rock_shape == "crystalline":
        # Create crystal-like rock
        bpy.ops.mesh.primitive_cone_add(
            vertices=6,
            radius1=base_size,
            radius2=0.2,
            depth=rock_height * 1.5,
            location=({position['x']}, {position['y']}, rock_height * 0.75)
        )
        rock = bpy.context.active_object
        
        # Add smaller crystals
        for i in range(DETAIL_COUNT // 2):
            offset_x = random.uniform(-base_size, base_size) * 0.7
            offset_y = random.uniform(-base_size, base_size) * 0.7
            
            bpy.ops.mesh.primitive_cone_add(
                vertices=6,
                radius1=base_size * 0.3,
                radius2=0.1,
                depth=rock_height * 0.7,
                location=({position['x']} + offset_x, {position['y']} + offset_y, rock_height * 0.35)
            )
            crystal = bpy.context.active_object
            crystal.name = f"AI_crystal_{{i}}_{index}"
            rock_parts.append(crystal)
        
    else:  # rounded or default
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=base_size,
            location=({position['x']}, {position['y']}, rock_height/2)
        )
        rock = bpy.context.active_object
        rock.scale = (1.0, 1.0, rock_height)
        bpy.ops.object.transform_apply(scale=True)
    
    rock.name = f"AI_{rock_shape}_rock_{index}"
    rock_parts.append(rock)
    
    return rock_parts

def create_ai_bush():
    """Create AI-designed bush with unique characteristics"""
    bush_parts = []
    
    bush_shape = "{bush_shape}"
    bush_size = 1.2 * WIDTH_MULT
    bush_height = 0.8 * HEIGHT_MULT
    
    if bush_shape == "spreading":
        # Create multiple small spheres spread out
        for i in range(DETAIL_COUNT):
            offset_x = random.uniform(-bush_size, bush_size) * 0.6
            offset_y = random.uniform(-bush_size, bush_size) * 0.6
            sphere_size = bush_size * random.uniform(0.3, 0.6)
            
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=1,
                radius=sphere_size,
                location=({position['x']} + offset_x, {position['y']} + offset_y, bush_height * 0.4)
            )
            sphere = bpy.context.active_object
            sphere.name = f"AI_spreading_bush_{{i}}_{index}"
            bush_parts.append(sphere)
    
    else:  # round or default
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=bush_size,
            location=({position['x']}, {position['y']}, bush_height/2)
        )
        bush = bpy.context.active_object
        bush.scale = (1.0, 1.0, bush_height)
        bpy.ops.object.transform_apply(scale=True)
        bush.name = f"AI_{bush_shape}_bush_{index}"
        bush_parts.append(bush)
    
    return bush_parts

def create_ai_well():
    """Create AI-designed well"""
    well_parts = []
    
    # Well base
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=1.0 * WIDTH_MULT,
        depth=0.5,
        location=({position['x']}, {position['y']}, 0.25)
    )
    base = bpy.context.active_object
    base.name = f"AI_well_base_{index}"
    well_parts.append(base)
    
    # Well wall
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.8 * WIDTH_MULT,
        depth=1.0 * HEIGHT_MULT,
        location=({position['x']}, {position['y']}, 0.5 * HEIGHT_MULT)
    )
    wall = bpy.context.active_object
    wall.name = f"AI_well_wall_{index}"
    well_parts.append(wall)
    
    # Well roof (optional)
    if random.random() > 0.5:  # 50% chance of roof
        bpy.ops.mesh.primitive_cone_add(
            vertices=8,
            radius1=1.2 * WIDTH_MULT,
            radius2=0.1,
            depth=0.8,
            location=({position['x']}, {position['y']}, HEIGHT_MULT + 0.4)
        )
        roof = bpy.context.active_object
        roof.name = f"AI_well_roof_{index}"
        well_parts.append(roof)
    
    return well_parts

def create_ai_generic_prop():
    """Create generic AI prop"""
    prop_parts = []
    
    # Simple geometric shape
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=0.5 * WIDTH_MULT,
        location=({position['x']}, {position['y']}, 0.5 * HEIGHT_MULT)
    )
    prop = bpy.context.active_object
    prop.name = f"AI_generic_prop_{index}"
    prop_parts.append(prop)
    
    return prop_parts

# Execute the creation
try:
    created_objects = create_ai_unique_{prop_type.replace(' ', '_')}()
    print(f"✅ Successfully created AI {prop_type} with {{len(created_objects)}} components")
    print(f"🎨 Style: {style_params}")
    print(f"🎯 Variations: {len(variations)}")
except Exception as e:
    print(f"❌ Error creating AI {prop_type}: {{e}}")
    import traceback
    traceback.print_exc()

print("🎯 AI-Creative Generation Script Complete!")
'''