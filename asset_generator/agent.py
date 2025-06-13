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

def generate_assets(world_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to generate 3D assets from world specification
    
    Args:
        world_spec: World specification from World Designer Agent
        
    Returns:
        Dictionary containing generated assets information
    """
    print(f"🎨 Starting asset generation...")
    
    try:
        # Parse world specification
        theme = world_spec.get('theme', 'medieval')
        buildings = world_spec.get('buildings', [])
        natural_features = world_spec.get('natural_features', [])
        paths = world_spec.get('paths', [])
        
        print(f"📦 Processing {len(buildings)} buildings, {len(natural_features)} features, {len(paths)} paths")
        
        # Create output directories
        output_dir = Path("generated_assets")
        output_dir.mkdir(exist_ok=True)
        
        models_dir = output_dir / "models"
        scripts_dir = output_dir / "blender_scripts"
        
        models_dir.mkdir(exist_ok=True)
        scripts_dir.mkdir(exist_ok=True)
        
        # Find Blender executable
        blender_path = _find_blender()
        
        # Generate assets
        building_assets = []
        environment_assets = []
        
        # Generate buildings
        for i, building in enumerate(buildings):
            print(f"🏠 Generating building {i+1}/{len(buildings)}: {building.get('type', 'house')}")
            
            # Create Blender script for this building
            script_content = _create_building_script(building, theme)
            script_path = scripts_dir / f"building_{building.get('type', 'house')}_{i}.py"
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # If Blender is available, run the script
            if blender_path:
                output_path = _run_blender_script(blender_path, script_path, models_dir)
                if output_path:
                    building_assets.append({
                        'type': building.get('type', 'house'),
                        'name': f"{building.get('type', 'house')}_{i}",
                        'file_path': str(output_path),
                        'position': building.get('position', {}),
                        'theme': theme,
                        'script_path': str(script_path)
                    })
            else:
                # Just record the script if Blender isn't available
                building_assets.append({
                    'type': building.get('type', 'house'),
                    'name': f"{building.get('type', 'house')}_{i}",
                    'file_path': None,
                    'position': building.get('position', {}),
                    'theme': theme,
                    'script_path': str(script_path)
                })
        
        # Generate natural features
        for i, feature in enumerate(natural_features[:10]):  # Limit to first 10 features
            print(f"🌿 Generating feature {i+1}: {feature.get('type', 'tree')}")
            
            script_content = _create_feature_script(feature, theme)
            script_path = scripts_dir / f"feature_{feature.get('type', 'tree')}_{i}.py"
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            if blender_path:
                output_path = _run_blender_script(blender_path, script_path, models_dir)
                if output_path:
                    environment_assets.append({
                        'type': feature.get('type', 'tree'),
                        'name': f"{feature.get('type', 'tree')}_{i}",
                        'file_path': str(output_path),
                        'position': feature.get('position', {}),
                        'theme': theme,
                        'script_path': str(script_path)
                    })
            else:
                environment_assets.append({
                    'type': feature.get('type', 'tree'),
                    'name': f"{feature.get('type', 'tree')}_{i}",
                    'file_path': None,
                    'position': feature.get('position', {}),
                    'theme': theme,
                    'script_path': str(script_path)
                })
        
        # Create asset manifest
        asset_manifest = {
            'theme': theme,
            'buildings': building_assets,
            'environment': environment_assets,
            'props': [],  # Can be extended later
            'output_directory': str(output_dir),
            'blender_available': blender_path is not None,
            'blender_path': blender_path,
            'generation_summary': {
                'total_assets': len(building_assets) + len(environment_assets),
                'buildings_count': len(building_assets),
                'environment_count': len(environment_assets),
                'props_count': 0
            }
        }
        
        # Save manifest
        manifest_path = output_dir / "asset_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(asset_manifest, f, indent=2)
        
        print(f"✅ Asset generation complete! Generated {asset_manifest['generation_summary']['total_assets']} assets")
        return asset_manifest
        
    except Exception as e:
        print(f"❌ Error in asset generation: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "fallback_available": True
        }

def _find_blender() -> Optional[str]:
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
        if Path(path).exists():
            return path
        elif path == "blender":
            try:
                subprocess.run([path, "--version"], capture_output=True, check=True)
                return path
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
    
    print("⚠️  Blender not found. Will generate scripts only.")
    return None

def _run_blender_script(blender_path: str, script_path: Path, models_dir: Path) -> Optional[Path]:
    """Run a Blender script and return output path"""
    try:
        output_name = script_path.stem
        output_path = models_dir / f"{output_name}.obj"
        
        cmd = [
            blender_path,
            "--background",
            "--python", str(script_path),
            "--",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and output_path.exists():
            print(f"✅ Successfully generated {output_path}")
            return output_path
        else:
            print(f"❌ Blender script failed for {script_path}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Blender script timed out: {script_path}")
        return None
    except Exception as e:
        print(f"💥 Error running Blender script: {e}")
        return None

def _create_building_script(building: Dict, theme: str) -> str:
    """Create Blender Python script for building generation"""
    building_type = building.get('type', 'house')
    position = building.get('position', {'x': 0, 'y': 0, 'z': 0})
    scale = building.get('scale', 1.0)
    
    # Building dimensions based on type
    dimensions = {
        'house': (6, 6, 4),
        'tavern': (8, 6, 5),
        'shop': (7, 5, 4),
        'market': (10, 8, 3),
        'church': (8, 12, 8),
        'blacksmith': (6, 4, 4),
        'fountain': (3, 3, 2),
        'tower': (4, 4, 12),
        'wall': (2, 8, 3)
    }
    
    width, depth, height = dimensions.get(building_type, (6, 6, 4))
    
    return f'''
import bpy
import sys
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create {building_type}
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=({position['x']}, {position['y']}, {position['z']} + {height/2})
)

building = bpy.context.active_object
building.name = "{building_type}_{position['x']}_{position['y']}"
building.scale = ({width}, {depth}, {height})

# Apply scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add architectural details based on building type
if "{building_type}" == "house":
    # Add a simple roof
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={{"value": (0, 0, 1)}})
    bpy.ops.transform.resize(value=(0.8, 0.8, 1))
    bpy.ops.object.mode_set(mode='OBJECT')

elif "{building_type}" == "tower":
    # Make tower taller and add crenellations
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')
    bpy.ops.mesh.select_all(action='INVERT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={{"value": (0, 0, 0.5)}})
    bpy.ops.object.mode_set(mode='OBJECT')

elif "{building_type}" == "church":
    # Add a cross on top
    bpy.ops.mesh.primitive_cube_add(
        size=0.5,
        location=({position['x']}, {position['y']}, {position['z']} + {height} + 1)
    )
    cross_v = bpy.context.active_object
    cross_v.scale = (0.2, 0.2, 2)
    
    bpy.ops.mesh.primitive_cube_add(
        size=0.5,
        location=({position['x']}, {position['y']}, {position['z']} + {height} + 1.5)
    )
    cross_h = bpy.context.active_object
    cross_h.scale = (0.8, 0.2, 0.2)
    
    # Select all objects and join them
    bpy.ops.object.select_all(action='DESELECT')
    building.select_set(True)
    cross_v.select_set(True)
    cross_h.select_set(True)
    bpy.context.view_layer.objects.active = building
    bpy.ops.object.join()

# Create material
material = bpy.data.materials.new(name="{theme}_{building_type}")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]

# Theme-based colors
theme_colors = {{
    'medieval': (0.6, 0.5, 0.4, 1.0),
    'spooky': (0.3, 0.2, 0.3, 1.0),
    'halloween': (0.3, 0.2, 0.3, 1.0),
    'fantasy': (0.7, 0.6, 0.8, 1.0),
    'desert': (0.9, 0.8, 0.6, 1.0)
}}

color = theme_colors.get("{theme}", (0.5, 0.5, 0.5, 1.0))
bsdf.inputs[0].default_value = color

# Add some roughness
bsdf.inputs[9].default_value = 0.8

building.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]  # Blender passes -- as argv[4]
    bpy.ops.object.select_all(action='DESELECT')
    building.select_set(True)
    bpy.context.view_layer.objects.active = building
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported {{building.name}} to {{output_path}}")
'''

def _create_feature_script(feature: Dict, theme: str) -> str:
    """Create Blender Python script for natural feature generation"""
    feature_type = feature.get('type', 'oak_tree')
    position = feature.get('position', {'x': 0, 'y': 0, 'z': 0})
    scale = feature.get('scale', 1.0)
    
    if 'tree' in feature_type:
        return f'''
import bpy
import sys
import random
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create tree trunk
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.3 * {scale},
    depth=3 * {scale},
    location=({position['x']}, {position['y']}, {position['z']} + 1.5 * {scale})
)
trunk = bpy.context.active_object
trunk.name = "Tree_Trunk"

# Create canopy
bpy.ops.mesh.primitive_ico_sphere_add(
    radius=2 * {scale},
    location=({position['x']}, {position['y']}, {position['z']} + 4 * {scale})
)
canopy = bpy.context.active_object
canopy.name = "Tree_Canopy"

# Add some randomness to the canopy
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.resize(value=(random.uniform(0.8, 1.2), random.uniform(0.8, 1.2), random.uniform(0.8, 1.2)))
bpy.ops.object.mode_set(mode='OBJECT')

# Create materials
trunk_material = bpy.data.materials.new(name="Tree_Bark")
trunk_material.use_nodes = True
trunk_bsdf = trunk_material.node_tree.nodes["Principled BSDF"]
trunk_bsdf.inputs[0].default_value = (0.3, 0.2, 0.1, 1.0)  # Brown
trunk_bsdf.inputs[9].default_value = 1.0  # Rough
trunk.data.materials.append(trunk_material)

canopy_material = bpy.data.materials.new(name="Tree_Leaves")
canopy_material.use_nodes = True
canopy_bsdf = canopy_material.node_tree.nodes["Principled BSDF"]
canopy_bsdf.inputs[0].default_value = (0.1, 0.4, 0.1, 1.0)  # Green
canopy.data.materials.append(canopy_material)

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
    
    elif feature_type == 'rock':
        return f'''
import bpy
import sys
import random

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create rock
bpy.ops.mesh.primitive_ico_sphere_add(
    radius=1.5 * {scale},
    location=({position['x']}, {position['y']}, {position['z']} + 0.5)
)
rock = bpy.context.active_object
rock.name = "Rock_{position['x']}_{position['y']}"

# Deform the rock
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.resize(value=(random.uniform(0.7, 1.3), random.uniform(0.7, 1.3), random.uniform(0.5, 0.8)))
bpy.ops.object.mode_set(mode='OBJECT')

# Create material
material = bpy.data.materials.new(name="Rock_Material")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.4, 0.4, 0.4, 1.0)  # Gray
bsdf.inputs[9].default_value = 0.9  # Rough
rock.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported rock to {{output_path}}")
'''
    
    else:
        # Generic feature (simple cube)
        return f'''
import bpy
import sys

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create generic feature
bpy.ops.mesh.primitive_cube_add(
    size={scale},
    location=({position['x']}, {position['y']}, {position['z']} + 0.5)
)
feature = bpy.context.active_object
feature.name = "{feature_type}_{position['x']}_{position['y']}"

# Create material
material = bpy.data.materials.new(name="{feature_type}_Material")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.5, 0.5, 0.5, 1.0)
feature.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported {feature_type} to {{output_path}}")
'''

def get_status() -> Dict[str, Any]:
    """Get asset generator status"""
    blender_path = _find_blender()
    return {
        'status': 'ready',
        'blender_available': blender_path is not None,
        'blender_path': blender_path,
        'output_directory': str(Path("generated_assets").resolve())
    }

# Create the ADK agent
root_agent = Agent(
    name="asset_generator",
    model="gemini-2.0-flash-exp",
    instruction="""You are an expert 3D asset generator for game development. You create high-quality 3D models and visual assets from world specifications.

Your capabilities include:
- Generating 3D building models with architectural details
- Creating natural features like trees, rocks, and environmental props
- Producing theme-consistent assets with appropriate materials and textures
- Exporting assets in standard formats (OBJ, FBX) ready for game engines
- Managing asset libraries and organizing output files

You work with Blender Python API to create procedural 3D content, but can also generate Blender scripts for external processing when direct API access isn't available.

When you receive an asset generation request, call the generate_assets function with the world specification.""",
    description="AI agent that generates 3D models and visual assets for game worlds using Blender and procedural generation",
    tools=[generate_assets, get_status]
)

# Test function for standalone usage
async def test_asset_generator():
    """Test the asset generator functions directly"""
    print("🎨 Testing Asset Generator Agent...")
    
    # Test world specification
    test_world_spec = {
        "theme": "medieval",
        "buildings": [
            {
                "type": "house",
                "position": {"x": 10, "y": 10, "z": 0},
                "scale": 1.0
            },
            {
                "type": "tavern",
                "position": {"x": 20, "y": 15, "z": 0},
                "scale": 1.2
            },
            {
                "type": "church",
                "position": {"x": 0, "y": 0, "z": 0},
                "scale": 1.5
            }
        ],
        "natural_features": [
            {
                "type": "oak_tree",
                "position": {"x": 5, "y": 5, "z": 0},
                "scale": 1.0
            },
            {
                "type": "rock",
                "position": {"x": 25, "y": 25, "z": 0},
                "scale": 0.8
            }
        ],
        "paths": []
    }
    
    try:
        # Test status
        status = get_status()
        print(f"✅ Status: {status}")
        
        # Test asset generation
        result = generate_assets(test_world_spec)
        
        if result.get("status") != "error":
            print(f"✅ Asset generation successful!")
            print(f"   Generated {result['generation_summary']['total_assets']} assets")
            print(f"   Output directory: {result['output_directory']}")
        else:
            print(f"❌ Asset generation failed: {result['error']}")
            
    except Exception as e:
        print(f"💥 Test failed: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_asset_generator())