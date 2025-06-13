
import bpy
import sys

# AI Description: 

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Texture paths
textures = {"stone": "textures/stone_medieval_e10455c3.png", "wood": "textures/wood_medieval_94c27939.png"}

# Create well base (stone cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=1.2,
    depth=1.0,
    location=(2.0, 6.0, 0.5)
)
well_base = bpy.context.active_object
well_base.name = "Well_Base"

# Create well rim
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.3,
    minor_radius=0.1,
    location=(2.0, 6.0, 1.1)
)
well_rim = bpy.context.active_object
well_rim.name = "Well_Rim"

# Create wooden roof support posts
for i, angle in enumerate([0, 1.57, 3.14, 4.71]):  # 90 degree intervals
    import math
    x_offset = 1.8 * math.cos(angle)
    y_offset = 1.8 * math.sin(angle)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.08,
        depth=2.5,
        location=(2.0 + x_offset, 6.0 + y_offset, 2.25)
    )
    post = bpy.context.active_object
    post.name = f"Well_Post_{i}"

# Create roof
bpy.ops.mesh.primitive_cone_add(
    vertices=8,
    radius1=2.2,
    radius2=0.3,
    depth=1.5,
    location=(2.0, 6.0, 3.8)
)
roof = bpy.context.active_object
roof.name = "Well_Roof"

# Create bucket (optional detail)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=12,
    radius=0.3,
    depth=0.4,
    location=(2.0 + 0.8, 6.0, 1.2)
)
bucket = bpy.context.active_object
bucket.name = "Well_Bucket"

# Join all well parts
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.name.startswith("Well_"):
        obj.select_set(True)

well_base.select_set(True)
bpy.context.view_layer.objects.active = well_base
bpy.ops.object.join()

well = bpy.context.active_object
well.name = "Enhanced_Well_2.0_6.0"

# Create well material with stone texture
material = bpy.data.materials.new(name="medieval_well")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

for node in nodes:
    nodes.remove(node)

bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

if "stone" in textures and textures["stone"]:
    try:
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        mapping = nodes.new(type='ShaderNodeMapping')
        img_tex = nodes.new(type='ShaderNodeTexImage')
        
        img = bpy.data.images.load(textures["stone"])
        img_tex.image = img
        
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], img_tex.inputs['Vector'])
        links.new(img_tex.outputs['Color'], bsdf.inputs['Base Color'])
    except:
        bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.5, 1.0)
else:
    bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.5, 1.0)

bsdf.inputs['Roughness'].default_value = 0.8
well.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported enhanced well to {output_path}")
