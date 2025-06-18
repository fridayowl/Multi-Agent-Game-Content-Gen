"""
BLENDER INTEGRATION MODULE
Specialized module for Blender Python API integration
Handles 3D model generation, scene setup, and Blender-specific operations
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Blender imports with fallback
try:
    import bpy
    import bmesh
    from mathutils import Vector, Euler
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False

class BlenderIntegration:
    """
    Specialized Blender integration module
    Handles all Blender-specific operations and 3D model generation
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.blender_available = BLENDER_AVAILABLE
        self.logger = logging.getLogger(__name__)
        
        # Blender-specific directories
        self.models_dir = output_dir / "models"
        self.scenes_dir = output_dir / "blender_scenes"
        self.scripts_dir = output_dir / "blender_scripts"
        
        for dir_path in [self.models_dir, self.scenes_dir, self.scripts_dir]:
            dir_path.mkdir(exist_ok=True)
        
        if not self.blender_available:
            self.logger.warning("⚠️ Blender Python API not available - scripts will be generated for external execution")
    
    def create_master_scene(self, world_spec: Dict[str, Any], assets: Dict[str, Any]) -> Optional[str]:
        """Create master Blender scene with all assets"""
        if not self.blender_available:
            return self._create_master_scene_script(world_spec, assets)
        
        try:
            # Clear existing scene
            self._clear_scene()
            
            # Setup scene basics
            self._setup_scene_basics(world_spec)
            
            # Import all generated assets
            self._import_generated_assets(assets)
            
            # Setup lighting
            self._setup_scene_lighting(world_spec.get('theme', 'medieval'))
            
            # Setup camera
            self._setup_scene_camera(world_spec)
            
            # Save master scene
            scene_file = self.scenes_dir / f"master_scene_{world_spec.get('theme', 'world')}.blend"
            bpy.ops.wm.save_as_mainfile(filepath=str(scene_file))
            
            self.logger.info(f"Master scene saved: {scene_file}")
            return str(scene_file)
            
        except Exception as e:
            self.logger.error(f"Failed to create master scene: {e}")
            return None
    
    def _clear_scene(self):
        """Clear all objects from the scene"""
        if self.blender_available:
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete(use_global=False, confirm=False)
    
    def _setup_scene_basics(self, world_spec: Dict[str, Any]):
        """Setup basic scene properties"""
        if not self.blender_available:
            return
        
        scene = bpy.context.scene
        
        # Set scene name
        scene.name = f"AI_World_{world_spec.get('theme', 'default')}"
        
        # Set units
        scene.unit_settings.system = 'METRIC'
        scene.unit_settings.length_unit = 'METERS'
        
        # Set frame range for animations
        scene.frame_start = 1
        scene.frame_end = 250
        
        # Setup world background
        world = bpy.context.scene.world
        if world:
            world.name = f"World_{world_spec.get('theme', 'default')}"
    
    def _import_generated_assets(self, assets: Dict[str, Any]):
        """Import all generated assets into the scene"""
        if not self.blender_available:
            return
        
        # Import buildings
        for building in assets.get('buildings', []):
            self._import_building(building)
        
        # Import props
        for prop in assets.get('props', []):
            self._import_prop(prop)
        
        # Import environment features
        for env_feature in assets.get('environment', []):
            self._import_environment_feature(env_feature)
    
    def _import_building(self, building: Dict[str, Any]):
        """Import a building into the scene"""
        # This would execute the building's generated script
        # For now, create a placeholder
        position = building.get('position', {'x': 0, 'y': 0, 'z': 0})
        
        if self.blender_available:
            bpy.ops.mesh.primitive_cube_add(
                size=4,
                location=(position['x'], position['y'], position['z'] + 2)
            )
            building_obj = bpy.context.active_object
            building_obj.name = f"Building_{building.get('type', 'house')}_{building.get('id', '0')}"
    
    def _import_prop(self, prop: Dict[str, Any]):
        """Import a prop into the scene"""
        position = prop.get('position', {'x': 0, 'y': 0, 'z': 0})
        
        if self.blender_available:
            if prop.get('type') in ['tree', 'oak_tree']:
                # Create tree
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.3,
                    depth=3,
                    location=(position['x'], position['y'], 1.5)
                )
                trunk = bpy.context.active_object
                trunk.name = f"Tree_trunk_{prop.get('id', '0')}"
                
                bpy.ops.mesh.primitive_ico_sphere_add(
                    radius=2,
                    location=(position['x'], position['y'], 4)
                )
                canopy = bpy.context.active_object
                canopy.name = f"Tree_canopy_{prop.get('id', '0')}"
            else:
                # Generic prop
                bpy.ops.mesh.primitive_ico_sphere_add(
                    radius=1,
                    location=(position['x'], position['y'], 0.5)
                )
                prop_obj = bpy.context.active_object
                prop_obj.name = f"Prop_{prop.get('type', 'generic')}_{prop.get('id', '0')}"
    
    def _import_environment_feature(self, env_feature: Dict[str, Any]):
        """Import environment feature into the scene"""
        if env_feature.get('type') == 'path':
            self._create_path(env_feature)
        elif env_feature.get('type') == 'water_feature':
            self._create_water_feature(env_feature)
        elif env_feature.get('type') == 'terrain_feature':
            self._create_terrain_feature(env_feature)
    
    def _create_path(self, path_data: Dict[str, Any]):
        """Create a path in the scene"""
        if not self.blender_available:
            return
        
        path_points = path_data.get('path_points', [])
        if len(path_points) < 2:
            return
        
        # Create path curve
        curve_data = bpy.data.curves.new(name=f"Path_{path_data.get('id', '0')}", type='CURVE')
        curve_data.dimensions = '3D'
        
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(len(path_points) - 1)
        
        for i, point in enumerate(path_points):
            bezier_point = spline.bezier_points[i]
            bezier_point.co = (point['x'], point['y'], point.get('z', 0))
            bezier_point.handle_left_type = 'AUTO'
            bezier_point.handle_right_type = 'AUTO'
        
        # Create curve object
        curve_obj = bpy.data.objects.new(f"Path_{path_data.get('id', '0')}", curve_data)
        bpy.context.collection.objects.link(curve_obj)
    
    def _create_water_feature(self, water_data: Dict[str, Any]):
        """Create water feature in the scene"""
        if not self.blender_available:
            return
        
    def _create_water_feature(self, water_data: Dict[str, Any]):
        """Create water feature in the scene"""
        if not self.blender_available:
            return
        
        position = water_data.get('position', {'x': 0, 'y': 0, 'z': 0})
        water_type = water_data.get('water_type', 'pond')
        
        if water_type == 'pond':
            bpy.ops.mesh.primitive_cylinder_add(
                radius=4,
                depth=0.5,
                location=(position['x'], position['y'], position['z'] - 0.25)
            )
        elif water_type == 'fountain':
            # Fountain base
            bpy.ops.mesh.primitive_cylinder_add(
                radius=2,
                depth=0.5,
                location=(position['x'], position['y'], position['z'] + 0.25)
            )
            base = bpy.context.active_object
            base.name = f"Fountain_base_{water_data.get('id', '0')}"
            
            # Fountain spout
            bpy.ops.mesh.primitive_cylinder_add(
                radius=0.1,
                depth=2,
                location=(position['x'], position['y'], position['z'] + 1.5)
            )
        
        water_obj = bpy.context.active_object
        water_obj.name = f"Water_{water_type}_{water_data.get('id', '0')}"
    
    def _create_terrain_feature(self, terrain_data: Dict[str, Any]):
        """Create terrain feature in the scene"""
        if not self.blender_available:
            return
        
        position = terrain_data.get('position', {'x': 0, 'y': 0, 'z': 0})
        feature_type = terrain_data.get('feature_type', 'hill')
        
        if feature_type == 'clearing':
            bpy.ops.mesh.primitive_cylinder_add(
                radius=8,
                depth=0.1,
                location=(position['x'], position['y'], position['z'] + 0.05)
            )
        elif feature_type == 'rocky_outcrop':
            # Create rock formation
            for i in range(5):
                offset_x = (i - 2) * 1.5
                offset_y = (i % 2) * 1.5
                bpy.ops.mesh.primitive_ico_sphere_add(
                    radius=1.5,
                    location=(position['x'] + offset_x, position['y'] + offset_y, position['z'] + 1)
                )
                rock = bpy.context.active_object
                rock.name = f"Rock_{i}_{terrain_data.get('id', '0')}"
        
        terrain_obj = bpy.context.active_object
        terrain_obj.name = f"Terrain_{feature_type}_{terrain_data.get('id', '0')}"
    
    def _setup_scene_lighting(self, theme: str):
        """Setup theme-appropriate lighting"""
        if not self.blender_available:
            return
        
        # Remove default light
        if 'Light' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['Light'], do_unlink=True)
        
        # Add sun light
        bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
        sun = bpy.context.active_object
        sun.name = f"Sun_{theme}"
        
        # Theme-specific lighting settings
        sun_light = sun.data
        if theme == 'medieval':
            sun_light.energy = 4.0
            sun_light.color = (1.0, 0.95, 0.8)
        elif theme == 'fantasy':
            sun_light.energy = 3.0
            sun_light.color = (0.9, 0.95, 1.0)
        elif theme == 'spooky':
            sun_light.energy = 1.5
            sun_light.color = (0.7, 0.7, 0.8)
        elif theme == 'desert':
            sun_light.energy = 5.0
            sun_light.color = (1.0, 0.9, 0.7)
        
        # Add ambient lighting
        world = bpy.context.scene.world
        if world and world.use_nodes:
            bg_node = world.node_tree.nodes.get('Background')
            if bg_node:
                bg_node.inputs[1].default_value = 0.3  # Ambient strength
    
    def _setup_scene_camera(self, world_spec: Dict[str, Any]):
        """Setup scene camera"""
        if not self.blender_available:
            return
        
        # Remove default camera
        if 'Camera' in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects['Camera'], do_unlink=True)
        
        # Calculate world center
        size = world_spec.get('size', (40, 40))
        center_x = size[0] / 2
        center_y = size[1] / 2
        
        # Add new camera
        bpy.ops.object.camera_add(
            location=(center_x + 20, center_y - 20, 25)
        )
        camera = bpy.context.active_object
        camera.name = f"Camera_{world_spec.get('theme', 'world')}"
        
        # Point camera at world center
        camera.rotation_euler = (1.1, 0, 0.785)  # 63°, 0°, 45°
        
        # Set as active camera
        bpy.context.scene.camera = camera
    
    def _create_master_scene_script(self, world_spec: Dict[str, Any], assets: Dict[str, Any]) -> str:
        """Create master scene script for external Blender execution"""
        theme = world_spec.get('theme', 'default')
        size = world_spec.get('size', (40, 40))
        
        script_content = f'''
import bpy
import bmesh
from mathutils import Vector, Euler

# AI-GENERATED MASTER SCENE SCRIPT
# Theme: {theme}
# Size: {size[0]} x {size[1]}
# Assets: {len(assets.get('buildings', []))} buildings, {len(assets.get('props', []))} props

def create_master_scene():
    """Create complete world scene with all assets"""
    print("🌍 Creating AI-Generated Master Scene...")
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    
    # Setup scene properties
    scene = bpy.context.scene
    scene.name = "AI_World_{theme}"
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    
    print(f"📐 Scene setup complete: {{scene.name}}")
    
    # Create world terrain base
    create_terrain_base()
    
    # Import buildings
    buildings_created = 0
    for building_data in {assets.get('buildings', [])}:
        try:
            create_building_placeholder(building_data)
            buildings_created += 1
        except Exception as e:
            print(f"⚠️ Failed to create building: {{e}}")
    
    print(f"🏠 Created {{buildings_created}} buildings")
    
    # Import props
    props_created = 0
    for prop_data in {assets.get('props', [])}:
        try:
            create_prop_placeholder(prop_data)
            props_created += 1
        except Exception as e:
            print(f"⚠️ Failed to create prop: {{e}}")
    
    print(f"🌳 Created {{props_created}} props")
    
    # Import environment features
    env_created = 0
    for env_data in {assets.get('environment', [])}:
        try:
            create_environment_placeholder(env_data)
            env_created += 1
        except Exception as e:
            print(f"⚠️ Failed to create environment feature: {{e}}")
    
    print(f"🌍 Created {{env_created}} environment features")
    
    # Setup lighting
    setup_scene_lighting()
    
    # Setup camera
    setup_scene_camera()
    
    print("✅ Master scene creation complete!")
    return True

def create_terrain_base():
    """Create base terrain plane"""
    bpy.ops.mesh.primitive_plane_add(
        size=max({size[0]}, {size[1]}),
        location=({size[0]}/2, {size[1]}/2, 0)
    )
    terrain = bpy.context.active_object
    terrain.name = "Terrain_Base"
    
    # Add subdivision for detail
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=10)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"🌱 Created terrain base: {{terrain.name}}")

def create_building_placeholder(building_data):
    """Create building placeholder"""
    position = building_data.get('position', {{'x': 0, 'y': 0, 'z': 0}})
    building_type = building_data.get('type', 'house')
    
    # Create main building structure
    bpy.ops.mesh.primitive_cube_add(
        size=4,
        location=(position['x'], position['y'], position['z'] + 2)
    )
    building = bpy.context.active_object
    building.name = f"Building_{{building_type}}_{{building_data.get('id', '0')}}"
    
    # Scale based on building type
    if building_type == 'church':
        building.scale = (1.5, 2.0, 2.0)
    elif building_type == 'tavern':
        building.scale = (1.2, 1.5, 1.2)
    elif building_type == 'shop':
        building.scale = (1.0, 1.2, 0.8)
    
    bpy.ops.object.transform_apply(scale=True)

def create_prop_placeholder(prop_data):
    """Create prop placeholder"""
    position = prop_data.get('position', {{'x': 0, 'y': 0, 'z': 0}})
    prop_type = prop_data.get('type', 'generic')
    
    if prop_type in ['tree', 'oak_tree', 'dead_tree']:
        # Create tree trunk
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.3,
            depth=3,
            location=(position['x'], position['y'], 1.5)
        )
        trunk = bpy.context.active_object
        trunk.name = f"Tree_trunk_{{prop_data.get('id', '0')}}"
        
        if prop_type != 'dead_tree':
            # Create canopy
            bpy.ops.mesh.primitive_ico_sphere_add(
                radius=2,
                location=(position['x'], position['y'], 4)
            )
            canopy = bpy.context.active_object
            canopy.name = f"Tree_canopy_{{prop_data.get('id', '0')}}"
    
    elif prop_type in ['rock', 'stone', 'boulder']:
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=1,
            location=(position['x'], position['y'], 0.5)
        )
        rock = bpy.context.active_object
        rock.scale = (1.2, 0.8, 0.6)  # Make it rock-like
        bpy.ops.object.transform_apply(scale=True)
        rock.name = f"Rock_{{prop_data.get('id', '0')}}"
    
    elif prop_type in ['bush', 'shrub']:
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=0.8,
            location=(position['x'], position['y'], 0.4)
        )
        bush = bpy.context.active_object
        bush.scale = (1.0, 1.0, 0.6)
        bpy.ops.object.transform_apply(scale=True)
        bush.name = f"Bush_{{prop_data.get('id', '0')}}"
    
    elif prop_type == 'well':
        # Well base
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1,
            depth=0.5,
            location=(position['x'], position['y'], 0.25)
        )
        base = bpy.context.active_object
        base.name = f"Well_base_{{prop_data.get('id', '0')}}"
        
        # Well wall
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.8,
            depth=1,
            location=(position['x'], position['y'], 0.75)
        )
        wall = bpy.context.active_object
        wall.name = f"Well_wall_{{prop_data.get('id', '0')}}"

def create_environment_placeholder(env_data):
    """Create environment feature placeholder"""
    env_type = env_data.get('type', 'generic')
    position = env_data.get('position', {{'x': 0, 'y': 0, 'z': 0}})
    
    if env_type == 'path':
        path_points = env_data.get('path_points', [])
        if len(path_points) >= 2:
            # Create simple path as connected cubes
            for i, point in enumerate(path_points[:-1]):
                next_point = path_points[i + 1]
                mid_x = (point['x'] + next_point['x']) / 2
                mid_y = (point['y'] + next_point['y']) / 2
                
                bpy.ops.mesh.primitive_cube_add(
                    size=1,
                    location=(mid_x, mid_y, 0.05)
                )
                segment = bpy.context.active_object
                segment.scale = (2, 0.5, 0.1)
                bpy.ops.object.transform_apply(scale=True)
                segment.name = f"Path_segment_{{i}}_{{env_data.get('id', '0')}}"
    
    elif env_type == 'water_feature':
        water_type = env_data.get('water_type', 'pond')
        if water_type == 'pond':
            bpy.ops.mesh.primitive_cylinder_add(
                radius=4,
                depth=0.5,
                location=(position['x'], position['y'], -0.25)
            )
        elif water_type == 'fountain':
            bpy.ops.mesh.primitive_cylinder_add(
                radius=2,
                depth=0.5,
                location=(position['x'], position['y'], 0.25)
            )
        
        water = bpy.context.active_object
        water.name = f"Water_{{water_type}}_{{env_data.get('id', '0')}}"

def setup_scene_lighting():
    """Setup theme-appropriate lighting"""
    # Remove default light if it exists
    if 'Light' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects['Light'], do_unlink=True)
    
    # Add sun light
    bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
    sun = bpy.context.active_object
    sun.name = f"Sun_{theme}"
    
    # Theme-specific lighting
    sun_light = sun.data
    theme_lighting = {{
        'medieval': {{'energy': 4.0, 'color': (1.0, 0.95, 0.8)}},
        'fantasy': {{'energy': 3.0, 'color': (0.9, 0.95, 1.0)}},
        'spooky': {{'energy': 1.5, 'color': (0.7, 0.7, 0.8)}},
        'desert': {{'energy': 5.0, 'color': (1.0, 0.9, 0.7)}}
    }}
    
    lighting = theme_lighting.get('{theme}', theme_lighting['medieval'])
    sun_light.energy = lighting['energy']
    sun_light.color = lighting['color']
    
    print(f"💡 Lighting setup complete for {theme} theme")

def setup_scene_camera():
    """Setup scene camera"""
    # Remove default camera if it exists
    if 'Camera' in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects['Camera'], do_unlink=True)
    
    # Calculate optimal camera position
    center_x = {size[0]} / 2
    center_y = {size[1]} / 2
    
    # Add camera
    bpy.ops.object.camera_add(
        location=(center_x + 20, center_y - 20, 25)
    )
    camera = bpy.context.active_object
    camera.name = f"Camera_{theme}"
    
    # Point camera at world center
    camera.rotation_euler = (1.1, 0, 0.785)  # Look down at world
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    print(f"📷 Camera setup complete: {{camera.name}}")

# Execute scene creation
if __name__ == "__main__":
    try:
        success = create_master_scene()
        if success:
            print("🎉 Master scene generation successful!")
            
            # Save the scene
            import os
            output_file = os.path.join(bpy.path.abspath("//"), f"master_scene_{theme}.blend")
            bpy.ops.wm.save_as_mainfile(filepath=output_file)
            print(f"💾 Scene saved: {{output_file}}")
        else:
            print("❌ Master scene generation failed!")
    except Exception as e:
        print(f"💥 Critical error in scene generation: {{e}}")
        import traceback
        traceback.print_exc()

print("🎯 Master Scene Script Complete!")
'''
        
        script_path = self.scripts_dir / f"master_scene_{theme}.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.logger.info(f"Master scene script created: {script_path}")
        return str(script_path)
    
    def execute_blender_script(self, script_path: str) -> bool:
        """Execute a Blender script"""
        if not self.blender_available:
            self.logger.warning("Blender not available - script saved for external execution")
            return False
        
        try:
            # Execute script in current Blender context
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            exec(script_content)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute Blender script: {e}")
            return False
    
    def export_scene(self, scene_file: str, export_format: str, output_path: str) -> bool:
        """Export scene to various formats"""
        if not self.blender_available:
            return False
        
        try:
            # Load scene if not current
            if scene_file != bpy.data.filepath:
                bpy.ops.wm.open_mainfile(filepath=scene_file)
            
            if export_format.lower() == 'gltf':
                bpy.ops.export_scene.gltf(filepath=output_path)
            elif export_format.lower() == 'obj':
                bpy.ops.export_scene.obj(filepath=output_path)
            elif export_format.lower() == 'fbx':
                bpy.ops.export_scene.fbx(filepath=output_path)
            elif export_format.lower() == 'dae':
                bpy.ops.wm.collada_export(filepath=output_path)
            else:
                self.logger.error(f"Unsupported export format: {export_format}")
                return False
            
            self.logger.info(f"Scene exported to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export scene: {e}")
            return False
    
    def create_asset_preview_renders(self, assets: Dict[str, Any]) -> List[str]:
        """Create preview renders of generated assets"""
        if not self.blender_available:
            return []
        
        render_paths = []
        renders_dir = self.output_dir / "preview_renders"
        renders_dir.mkdir(exist_ok=True)
        
        try:
            # Setup render settings
            scene = bpy.context.scene
            scene.render.resolution_x = 512
            scene.render.resolution_y = 512
            scene.render.engine = 'EEVEE'
            
            # Render building previews
            for i, building in enumerate(assets.get('buildings', [])):
                render_path = renders_dir / f"building_{building.get('type', 'house')}_{i}.png"
                
                # Clear scene and create building
                self._clear_scene()
                self._import_building(building)
                
                # Setup preview lighting and camera
                self._setup_preview_lighting()
                self._setup_preview_camera()
                
                # Render
                scene.render.filepath = str(render_path)
                bpy.ops.render.render(write_still=True)
                render_paths.append(str(render_path))
            
            # Render prop previews
            for i, prop in enumerate(assets.get('props', [])):
                render_path = renders_dir / f"prop_{prop.get('type', 'generic')}_{i}.png"
                
                # Clear scene and create prop
                self._clear_scene()
                self._import_prop(prop)
                
                # Setup preview lighting and camera
                self._setup_preview_lighting()
                self._setup_preview_camera()
                
                # Render
                scene.render.filepath = str(render_path)
                bpy.ops.render.render(write_still=True)
                render_paths.append(str(render_path))
            
        except Exception as e:
            self.logger.error(f"Failed to create preview renders: {e}")
        
        return render_paths
    
    def _setup_preview_lighting(self):
        """Setup lighting for preview renders"""
        if not self.blender_available:
            return
        
        # Add key light
        bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
        key_light = bpy.context.active_object
        key_light.data.energy = 3.0
        
        # Add fill light
        bpy.ops.object.light_add(type='AREA', location=(-3, 3, 5))
        fill_light = bpy.context.active_object
        fill_light.data.energy = 1.0
    
    def _setup_preview_camera(self):
        """Setup camera for preview renders"""
        if not self.blender_available:
            return
        
        bpy.ops.object.camera_add(location=(7, -7, 5))
        camera = bpy.context.active_object
        camera.rotation_euler = (1.1, 0, 0.785)
        bpy.context.scene.camera = camera
    
    def get_blender_info(self) -> Dict[str, Any]:
        """Get Blender installation and capability info"""
        info = {
            'blender_available': self.blender_available,
            'can_create_scenes': self.blender_available,
            'can_export': self.blender_available,
            'can_render': self.blender_available
        }
        
        if self.blender_available:
            info.update({
                'blender_version': f"{bpy.app.version[0]}.{bpy.app.version[1]}.{bpy.app.version[2]}",
                'supported_formats': ['blend', 'gltf', 'obj', 'fbx', 'dae'],
                'render_engines': ['EEVEE', 'CYCLES'],
                'python_api': True
            })
        else:
            info.update({
                'message': 'Blender Python API not available - scripts generated for external execution',
                'supported_formats': ['scripts_only'],
                'render_engines': [],
                'python_api': False
            })
        
        return info