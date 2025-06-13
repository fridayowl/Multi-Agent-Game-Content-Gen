"""
ADK-Compatible Asset Generator Agent
Multi-Agent Game Content Pipeline
"""

import json
import os
import subprocess
import sys
import random
from typing import Dict, List, Any, Tuple, Optional
import logging
from pathlib import Path

# Google ADK imports (correct structure)
from google.adk.agents import Agent

# Blender imports - these will only work when running inside Blender
try:
    import bpy
    import bmesh
    from mathutils import Vector, Euler
    BLENDER_AVAILABLE = True
except ImportError:
    BLENDER_AVAILABLE = False
    print("Warning: Blender Python API not available. Running in standalone mode.")

class AssetGeneratorAgent:
    """
    Asset Generator Agent for Multi-Agent Game Content Pipeline
    Generates 3D models and visual assets from World Designer specifications
    """
    
    def __init__(self, output_dir: str = "generated_assets", blender_path: str = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Asset directories
        self.models_dir = self.output_dir / "models"
        self.textures_dir = self.output_dir / "textures"
        self.materials_dir = self.output_dir / "materials"
        self.scripts_dir = self.output_dir / "blender_scripts"
        
        for dir_path in [self.models_dir, self.textures_dir, self.materials_dir, self.scripts_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.generated_assets = []
        self.material_library = {}
        self.blender_path = blender_path or self._find_blender()
        
        # Initialize Blender environment if available
        if BLENDER_AVAILABLE:
            self._initialize_blender()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _find_blender(self) -> Optional[str]:
        """Find Blender executable path"""
        common_paths = [
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 3.6\\blender.exe",
            "blender"  # If in PATH
        ]
        
        for path in common_paths:
            if Path(path).exists() or self._command_exists(path):
                return path
        
        self.logger.warning("Blender not found automatically. Please specify blender_path manually.")
        return None
    
    def _command_exists(self, command: str) -> bool:
        """Check if command exists in PATH"""
        try:
            subprocess.run([command, "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _initialize_blender(self):
        """Initialize Blender environment and clear default scene"""
        if not BLENDER_AVAILABLE:
            return
            
        # Clear existing mesh objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False, confirm=False)
        
        # Enable required add-ons
        bpy.ops.preferences.addon_enable(module="io_scene_obj")
        bpy.ops.preferences.addon_enable(module="io_scene_fbx")
    
    async def generate_assets(self, world_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for asset generation
        Compatible with ADK message handling
        """
        self.logger.info("Starting asset generation from world specification")
        
        try:
            # Parse world specification
            theme = world_spec.get('theme', 'medieval')
            buildings = world_spec.get('buildings', [])
            natural_features = world_spec.get('natural_features', [])
            terrain_map = world_spec.get('terrain_map', [])
            
            # Convert buildings to assets format
            building_assets = []
            for building in buildings:
                building_assets.append({
                    'type': building.get('type', 'house'),
                    'position': building.get('position', {}),
                    'size': self._get_building_size(building.get('type', 'house')),
                    'scale': building.get('scale', 1.0)
                })
            
            # Convert natural features to props
            prop_assets = []
            for feature in natural_features:
                prop_assets.append({
                    'type': feature.get('type', 'tree'),
                    'position': feature.get('position', {}),
                    'scale': feature.get('scale', 1.0)
                })
            
            # Environment data
            environment = {
                'terrain': {
                    'type': 'heightmap',
                    'size': world_spec.get('size', (40, 40)),
                    'terrain_map': terrain_map
                }
            }
            
            if BLENDER_AVAILABLE:
                # Direct Blender generation
                building_results = await self._generate_buildings(building_assets, theme)
                environment_results = await self._generate_environment(environment, theme)
                prop_results = await self._generate_props(prop_assets, theme)
            else:
                # Generate Blender scripts and run externally
                building_results = await self._generate_buildings_external(building_assets, theme)
                environment_results = await self._generate_environment_external(environment, theme)
                prop_results = await self._generate_props_external(prop_assets, theme)
            
            # Compile asset manifest
            asset_manifest = {
                'theme': theme,
                'buildings': building_results,
                'environment': environment_results,
                'props': prop_results,
                'materials': self.material_library,
                'output_directory': str(self.output_dir),
                'generation_summary': {
                    'total_assets': len(building_results) + len(environment_results) + len(prop_results),
                    'buildings_count': len(building_results),
                    'environment_count': len(environment_results),
                    'props_count': len(prop_results)
                }
            }
            
            # Save manifest
            manifest_path = self.output_dir / "asset_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(asset_manifest, f, indent=2)
            
            self.logger.info(f"Asset generation complete. Generated {asset_manifest['generation_summary']['total_assets']} assets")
            return asset_manifest
            
        except Exception as e:
            self.logger.error(f"Asset generation failed: {str(e)}")
            raise
    
    def _get_building_size(self, building_type: str) -> Dict[str, float]:
        """Get standard building dimensions"""
        sizes = {
            'house': {'width': 8, 'depth': 6, 'height': 5},
            'tavern': {'width': 12, 'depth': 10, 'height': 6},
            'shop': {'width': 10, 'depth': 8, 'height': 6},
            'church': {'width': 15, 'depth': 20, 'height': 12},
            'blacksmith': {'width': 8, 'depth': 8, 'height': 6},
            'market': {'width': 20, 'depth': 15, 'height': 4},
            'fountain': {'width': 4, 'depth': 4, 'height': 3},
            'tower': {'width': 6, 'depth': 6, 'height': 20},
            'wall': {'width': 1, 'depth': 10, 'height': 4}
        }
        return sizes.get(building_type, sizes['house'])
    
    async def _generate_buildings_external(self, buildings: List[Dict], theme: str) -> List[Dict]:
        """Generate buildings using external Blender process"""
        building_assets = []
        
        for building in buildings:
            # Generate Blender script for this building
            script_content = self._create_building_script(building, theme)
            building_id = f"{building.get('type', 'house')}_{building.get('position', {}).get('x', 0)}_{building.get('position', {}).get('y', 0)}"
            script_path = self.scripts_dir / f"building_{building_id}.py"
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Run Blender script
            if self.blender_path:
                output_path = self._run_blender_script(script_path)
                if output_path:
                    building_assets.append({
                        'type': building.get('type', 'house'),
                        'name': building_id,
                        'file_path': output_path,
                        'position': building.get('position', {}),
                        'size': building.get('size', {}),
                        'theme': theme,
                        'script_path': str(script_path)
                    })
                else:
                    # Even if Blender fails, record the script
                    building_assets.append({
                        'type': building.get('type', 'house'),
                        'name': building_id,
                        'file_path': None,
                        'position': building.get('position', {}),
                        'size': building.get('size', {}),
                        'theme': theme,
                        'script_path': str(script_path),
                        'status': 'script_generated'
                    })
        
        return building_assets
    
    async def _generate_environment_external(self, environment: Dict, theme: str) -> List[Dict]:
        """Generate environment using external Blender process"""
        environment_assets = []
        
        # Generate terrain script
        if environment.get('terrain'):
            script_content = self._create_terrain_script(environment['terrain'], theme)
            script_path = self.scripts_dir / "terrain.py"
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            if self.blender_path:
                output_path = self._run_blender_script(script_path)
                if output_path:
                    environment_assets.append({
                        'type': 'terrain',
                        'name': 'terrain',
                        'file_path': output_path,
                        'theme': theme,
                        'script_path': str(script_path)
                    })
                else:
                    environment_assets.append({
                        'type': 'terrain',
                        'name': 'terrain',
                        'file_path': None,
                        'theme': theme,
                        'script_path': str(script_path),
                        'status': 'script_generated'
                    })
        
        return environment_assets
    
    async def _generate_props_external(self, props: List[Dict], theme: str) -> List[Dict]:
        """Generate props using external Blender process"""
        prop_assets = []
        
        for prop in props:
            script_content = self._create_prop_script(prop, theme)
            prop_id = f"{prop.get('type', 'generic')}_{prop.get('position', {}).get('x', 0)}_{prop.get('position', {}).get('y', 0)}"
            script_path = self.scripts_dir / f"prop_{prop_id}.py"
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            if self.blender_path:
                output_path = self._run_blender_script(script_path)
                if output_path:
                    prop_assets.append({
                        'type': prop.get('type', 'generic'),
                        'name': prop_id,
                        'file_path': output_path,
                        'position': prop.get('position', {}),
                        'theme': theme,
                        'script_path': str(script_path)
                    })
                else:
                    prop_assets.append({
                        'type': prop.get('type', 'generic'),
                        'name': prop_id,
                        'file_path': None,
                        'position': prop.get('position', {}),
                        'theme': theme,
                        'script_path': str(script_path),
                        'status': 'script_generated'
                    })
        
        return prop_assets
    
    def _run_blender_script(self, script_path: Path) -> Optional[str]:
        """Run a Blender script and return output path"""
        try:
            output_name = script_path.stem
            output_path = self.models_dir / f"{output_name}.obj"
            
            cmd = [
                self.blender_path,
                "--background",
                "--python", str(script_path),
                "--",
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                self.logger.info(f"Successfully generated {output_path}")
                return str(output_path)
            else:
                self.logger.error(f"Blender script failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Blender script timed out: {script_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error running Blender script: {e}")
            return None
    
    def _create_building_script(self, building: Dict, theme: str) -> str:
        """Create Blender Python script for building generation"""
        building_type = building.get('type', 'house')
        position = building.get('position', {'x': 0, 'y': 0, 'z': 0})
        size = building.get('size', {'width': 10, 'depth': 10, 'height': 8})
        
        return f'''
import bpy
import sys
import os

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create {building_type}
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=({position['x']}, {position['y']}, {position['z']})
)

building = bpy.context.active_object
building.name = "{building_type}_{position['x']}_{position['y']}"
building.scale = ({size['width']}, {size['depth']}, {size['height']})

# Apply transforms
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add basic roof (simplified)
bpy.context.view_layer.objects.active = building
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={{"value": (0, 0, 1)}})
bpy.ops.transform.resize(value=(1.2, 1.2, 1))
bpy.ops.object.mode_set(mode='OBJECT')

# Create material
material = bpy.data.materials.new(name="{theme}_{building_type}")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]

# Theme-based colors
theme_colors = {{
    'medieval': (0.6, 0.5, 0.4, 1.0),
    'halloween': (0.3, 0.2, 0.3, 1.0),
    'spooky': (0.3, 0.2, 0.3, 1.0),
    'fantasy': (0.7, 0.6, 0.8, 1.0),
    'desert': (0.9, 0.8, 0.6, 1.0)
}}

color = theme_colors.get("{theme}", (0.5, 0.5, 0.5, 1.0))
bsdf.inputs[0].default_value = color
building.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]  # Blender passes -- as argv[4]
    bpy.ops.object.select_all(action='DESELECT')
    building.select_set(True)
    bpy.context.view_layer.objects.active = building
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported to {{output_path}}")
'''
    
    def _create_terrain_script(self, terrain: Dict, theme: str) -> str:
        """Create Blender Python script for terrain generation"""
        return f'''
import bpy
import sys

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create terrain
bpy.ops.mesh.primitive_plane_add(size=100)
terrain = bpy.context.active_object
terrain.name = "Terrain"

# Add subdivision for detail
bpy.ops.object.modifier_add(type='SUBSURF')
terrain.modifiers["Subdivision Surface"].levels = 2

# Create material
material = bpy.data.materials.new(name="{theme}_terrain")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]

# Theme-based terrain colors
theme_colors = {{
    'medieval': (0.2, 0.5, 0.1, 1.0),
    'halloween': (0.3, 0.2, 0.1, 1.0),
    'spooky': (0.3, 0.2, 0.1, 1.0),
    'fantasy': (0.1, 0.6, 0.2, 1.0),
    'desert': (0.9, 0.7, 0.4, 1.0)
}}

color = theme_colors.get("{theme}", (0.3, 0.4, 0.2, 1.0))
bsdf.inputs[0].default_value = color
terrain.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported terrain to {{output_path}}")
'''
    
    def _create_prop_script(self, prop: Dict, theme: str) -> str:
        """Create Blender Python script for prop generation"""
        prop_type = prop.get('type', 'generic')
        position = prop.get('position', {'x': 0, 'y': 0, 'z': 0})
        
        if prop_type in ['tree', 'oak_tree', 'dead_tree', 'palm_tree']:
            return f'''
import bpy
import sys

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create tree trunk
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.3,
    depth=3,
    location=({position['x']}, {position['y']}, {position['z']} + 1.5)
)
trunk = bpy.context.active_object
trunk.name = "Tree_Trunk"

# Create canopy
bpy.ops.mesh.primitive_ico_sphere_add(
    radius=2,
    location=({position['x']}, {position['y']}, {position['z']} + 4)
)
canopy = bpy.context.active_object
canopy.name = "Tree_Canopy"

# Join objects
bpy.ops.object.select_all(action='DESELECT')
trunk.select_set(True)
canopy.select_set(True)
bpy.context.view_layer.objects.active = trunk
bpy.ops.object.join()

tree = bpy.context.active_object
tree.name = "Tree_{position['x']}_{position['y']}"

# Create materials
trunk_material = bpy.data.materials.new(name="Trunk_Material")
trunk_material.use_nodes = True
trunk_bsdf = trunk_material.node_tree.nodes["Principled BSDF"]
trunk_bsdf.inputs[0].default_value = (0.4, 0.2, 0.1, 1.0)  # Brown

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported tree to {{output_path}}")
'''
        elif prop_type in ['rock', 'stone']:
            return f'''
import bpy
import sys

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create rock
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    location=({position['x']}, {position['y']}, {position['z']})
)
rock = bpy.context.active_object
rock.name = "Rock_{position['x']}_{position['y']}"
rock.scale = (1.5, 1.2, 0.8)

# Apply scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Create material
material = bpy.data.materials.new(name="Rock_Material")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.4, 0.4, 0.4, 1.0)  # Gray
bsdf.inputs[7].default_value = 0.8  # Roughness
rock.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported rock to {{output_path}}")
'''
        else:
            # Generic prop (cube)
            return f'''
import bpy
import sys

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create prop
bpy.ops.mesh.primitive_cube_add(location=({position['x']}, {position['y']}, {position['z']}))
prop = bpy.context.active_object
prop.name = "{prop_type}_{position['x']}_{position['y']}"

# Create material
material = bpy.data.materials.new(name="{prop_type}_Material")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.6, 0.6, 0.6, 1.0)  # Gray
prop.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported {{prop_type}} to {{output_path}}")
'''

    # Placeholder methods for direct Blender API (when available)
    async def _generate_buildings(self, buildings: List[Dict], theme: str) -> List[Dict]:
        """Generate building assets (when Blender API is available)"""
        if not BLENDER_AVAILABLE:
            return []
        # Implementation would go here for direct Blender API usage
        return []
    
    async def _generate_environment(self, environment: Dict, theme: str) -> List[Dict]:
        """Generate environment assets (when Blender API is available)"""
        if not BLENDER_AVAILABLE:
            return []
        # Implementation would go here for direct Blender API usage
        return []
    
    async def _generate_props(self, props: List[Dict], theme: str) -> List[Dict]:
        """Generate prop assets (when Blender API is available)"""
        if not BLENDER_AVAILABLE:
            return []
        # Implementation would go here for direct Blender API usage
        return []

    async def get_status(self) -> Dict[str, Any]:
        """Get asset generator status"""
        return {
            'status': 'ready',
            'blender_available': BLENDER_AVAILABLE,
            'blender_path': self.blender_path,
            'output_directory': str(self.output_dir)
        }


# Create the ADK agent
root_agent = Agent(
    name="asset_generator",
    model="gemini-2.0-flash-exp",
    instruction="""You are an expert 3D asset generator for game development. You create 3D models, textures, and materials from world specifications.

Your capabilities include:
- Converting world designs into 3D assets
- Generating Blender Python scripts for model creation
- Creating theme-consistent materials and textures
- Optimizing assets for game engine compatibility
- Managing asset libraries and dependencies

You understand 3D modeling principles, game asset optimization, and procedural generation techniques.

When you receive an asset generation request, call the generate_assets function with the world specification.""",
    description="AI agent that generates 3D models and visual assets for game worlds using Blender automation",
    tools=[AssetGeneratorAgent().generate_assets, AssetGeneratorAgent().get_status]
)

# Standalone usage
if __name__ == "__main__":
    import asyncio
    
    # Example world specification
    example_world_spec = {
        "theme": "medieval",
        "buildings": [
            {
                "type": "house",
                "position": {"x": 10, "y": 10, "z": 0},
                "scale": 1.0
            },
            {
                "type": "shop",
                "position": {"x": 25, "y": 10, "z": 0},
                "scale": 1.0
            }
        ],
        "natural_features": [
            {
                "type": "oak_tree",
                "position": {"x": 5, "y": 15, "z": 0},
                "scale": 1.0
            },
            {
                "type": "rock",
                "position": {"x": 30, "y": 12, "z": 0},
                "scale": 1.0
            }
        ],
        "terrain_map": [
            ["grass", "grass", "dirt"],
            ["dirt", "grass", "grass"],
            ["grass", "dirt", "grass"]
        ],
        "size": (40, 40)
    }
    
    async def main():
        agent = AssetGeneratorAgent(output_dir="medieval_village_assets")
        assets = await agent.generate_assets(example_world_spec)
        print(f"Generated {assets['generation_summary']['total_assets']} assets")
        print(f"Output directory: {assets['output_directory']}")
    
    asyncio.run(main())