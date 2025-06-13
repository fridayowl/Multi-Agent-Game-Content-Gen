
import bpy
import sys
import bmesh
import random

# AI Description: 

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Texture paths
textures = {"surface": "textures/stone_medieval_42e2299f.png"}

# Create enhanced rock with irregular shape
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=3,
    radius=1.0,
    location=(33.0, 39.0, 0.5)
)
rock = bpy.context.active_object
rock.name = "Enhanced_Rock_33.0_39.0"

# Make rock irregular
rock.scale = (random.uniform(1.2, 2.0), random.uniform(1.0, 1.8), random.uniform(0.6, 1.2))
bpy.ops.object.transform_apply(scale=True)

# Add surface detail
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')

# Add some random displacement
bpy.ops.transform.vertex_random(offset=0.2, uniform=0.1)
bpy.ops.object.mode_set(mode='OBJECT')

# Add displacement modifier for surface detail
bpy.ops.object.modifier_add(type='DISPLACE')
rock.modifiers["Displace"].strength = 0.3

# Create enhanced rock material
material = bpy.data.materials.new(name="medieval_enhanced_rock")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

for node in nodes:
    nodes.remove(node)

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Add procedural rock texture
tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-800, 0)

mapping = nodes.new(type='ShaderNodeMapping')
mapping.location = (-600, 0)
mapping.inputs['Scale'].default_value = (3, 3, 3)
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

# Use surface texture if available
if "surface" in textures and textures["surface"]:
    try:
        img_tex = nodes.new(type='ShaderNodeTexImage')
        img_tex.location = (-400, 0)
        img = bpy.data.images.load(textures["surface"])
        img_tex.image = img
        links.new(mapping.outputs['Vector'], img_tex.inputs['Vector'])
        links.new(img_tex.outputs['Color'], bsdf.inputs['Base Color'])
    except:
        # Fallback to procedural
        noise = nodes.new(type='ShaderNodeTexNoise')
        noise.location = (-400, 0)
        noise.inputs['Scale'].default_value = 8.0
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
        
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-200, 0)
        color_ramp.color_ramp.elements[0].color = (0.3, 0.3, 0.3, 1.0)
        color_ramp.color_ramp.elements[1].color = (0.6, 0.6, 0.6, 1.0)
        
        links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
else:
    # Theme-based rock colors
    rock_colors = {
        'medieval': (0.4, 0.4, 0.4, 1.0),
        'spooky': (0.2, 0.25, 0.2, 1.0),
        'halloween': (0.3, 0.2, 0.3, 1.0),
        'fantasy': (0.5, 0.4, 0.6, 1.0),
        'desert': (0.7, 0.6, 0.4, 1.0)
    }
    bsdf.inputs['Base Color'].default_value = rock_colors.get("medieval", (0.4, 0.4, 0.4, 1.0))

bsdf.inputs['Roughness'].default_value = 0.9
rock.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported enhanced rock to {output_path}")
