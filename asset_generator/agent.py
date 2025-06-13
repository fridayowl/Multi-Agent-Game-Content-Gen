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

# ADK imports
try:
    from adk import Agent, message
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    print("Warning: ADK not available. Creating standalone agent.")

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
            environment = world_spec.get('environment', {})
            props = world_spec.get('props', [])
            
            if BLENDER_AVAILABLE:
                # Direct Blender generation
                building_assets = await self._generate_buildings(buildings, theme)
                environment_assets = await self._generate_environment(environment, theme)
                prop_assets = await self._generate_props(props, theme)
            else:
                # Generate Blender scripts and run externally
                building_assets = await self._generate_buildings_external(buildings, theme)
                environment_assets = await self._generate_environment_external(environment, theme)
                prop_assets = await self._generate_props_external(props, theme)
            
            # Compile asset manifest
            asset_manifest = {
                'theme': theme,
                'buildings': building_assets,
                'environment': environment_assets,
                'props': prop_assets,
                'materials': self.material_library,
                'output_directory': str(self.output_dir),
                'generation_summary': {
                    'total_assets': len(building_assets) + len(environment_assets) + len(prop_assets),
                    'buildings_count': len(building_assets),
                    'environment_count': len(environment_assets),
                    'props_count': len(prop_assets)
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
    
    async def _generate_buildings_external(self, buildings: List[Dict], theme: str) -> List[Dict]:
        """Generate buildings using external Blender process"""
        building_assets = []
        
        for building in buildings:
            # Generate Blender script for this building
            script_content = self._create_building_script(building, theme)
            script_path = self.scripts_dir / f"building_{building.get('type', 'house')}_{building.get('position', {}).get('x', 0)}.py"
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Run Blender script
            if self.blender_path:
                output_path = self._run_blender_script(script_path)
                if output_path:
                    building_assets.append({
                        'type': building.get('type', 'house'),
                        'name': f"{building.get('type', 'house')}_{building.get('position', {}).get('x', 0)}_{building.get('position', {}).get('y', 0)}",
                        'file_path': output_path,
                        'position': building.get('position', {}),
                        'size': building.get('size', {}),
                        'theme': theme,
                        'script_path': str(script_path)
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
        
        return environment_assets
    
    async def _generate_props_external(self, props: List[Dict], theme: str) -> List[Dict]:
        """Generate props using external Blender process"""
        prop_assets = []
        
        for prop in props:
            script_content = self._create_prop_script(prop, theme)
            script_path = self.scripts_dir / f"prop_{prop.get('type', 'generic')}_{prop.get('position', {}).get('x', 0)}.py"
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            if self.blender_path:
                output_path = self._run_blender_script(script_path)
                if output_path:
                    prop_assets.append({
                        'type': prop.get('type', 'generic'),
                        'name': f"{prop.get('type', 'generic')}_{prop.get('position', {}).get('x', 0)}_{prop.get('position', {}).get('y', 0)}",
                        'file_path': output_path,
                        'position': prop.get('position', {}),
                        'theme': theme,
                        'script_path': str(script_path)
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
    'fantasy': (0.7, 0.6, 0.8, 1.0)
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
        
        if prop_type == 'tree':
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

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported tree to {{output_path}}")
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


# ADK-compatible root agent
if ADK_AVAILABLE:
    class ADKAssetGenerator(Agent):
        """ADK-compatible Asset Generator Agent"""
        
        def __init__(self):
            super().__init__()
            self.asset_generator = AssetGeneratorAgent()
        
        @message
        async def generate_assets(self, world_spec: Dict[str, Any]) -> Dict[str, Any]:
            """Handle asset generation requests from other agents"""
            return await self.asset_generator.generate_assets(world_spec)
        
        @message
        async def get_status(self) -> Dict[str, Any]:
            """Get asset generator status"""
            return {
                'status': 'ready',
                'blender_available': BLENDER_AVAILABLE,
                'blender_path': self.asset_generator.blender_path,
                'output_directory': str(self.asset_generator.output_dir)
            }
    
    # This is what ADK looks for
    root_agent = ADKAssetGenerator()

else:
    # Fallback for non-ADK environments
    root_agent = AssetGeneratorAgent()


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
                "size": {"width": 8, "depth": 6, "height": 5}
            },
            {
                "type": "shop",
                "position": {"x": 25, "y": 10, "z": 0},
                "size": {"width": 10, "depth": 8, "height": 6}
            }
        ],
        "environment": {
            "terrain": {"type": "hills", "size": 100},
            "paths": [
                {
                    "start": {"x": 0, "y": 0},
                    "end": {"x": 50, "y": 0},
                    "width": 3
                }
            ]
        },
        "props": [
            {
                "type": "tree",
                "subtype": "oak",
                "position": {"x": 5, "y": 15, "z": 0}
            },
            {
                "type": "barrel",
                "position": {"x": 30, "y": 12, "z": 0}
            }
        ]
    }
    
    async def main():
        if ADK_AVAILABLE:
            # Use ADK agent
            agent = ADKAssetGenerator()
            assets = await agent.generate_assets(example_world_spec)
        else:
            # Use standalone agent
            agent = AssetGeneratorAgent(output_dir="medieval_village_assets")
            assets = await agent.generate_assets(example_world_spec)
        
        print(f"Generated {assets['generation_summary']['total_assets']} assets")
    
    asyncio.run(main())