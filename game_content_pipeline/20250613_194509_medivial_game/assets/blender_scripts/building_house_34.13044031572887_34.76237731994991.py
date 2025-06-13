
import bpy
import sys
import os

# AI Description: 

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Texture paths
textures = {"walls": "textures/wood_medieval_4c39b5ed.png", "roof": "textures/stone_medieval_4c2f2196.png"}

# Create house
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(34.13044031572887, 34.76237731994991, 0.0)
)

building = bpy.context.active_object
building.name = "house_34.13044031572887_34.76237731994991"
building.scale = (8, 6, 5)

# Apply transforms
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add detailed geometry based on type
if "house" == "church":
    # Add tower for church
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(34.13044031572887, 37.76237731994991, 2.5)
    )
    tower = bpy.context.active_object
    tower.name = "church_tower"
    tower.scale = (3, 3, 8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Join with main building
    bpy.ops.object.select_all(action='DESELECT')
    building.select_set(True)
    tower.select_set(True)
    bpy.context.view_layer.objects.active = building
    bpy.ops.object.join()

elif "house" == "blacksmith":
    # Add chimney for blacksmith
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.5,
        depth=3,
        location=(36.79710698239553, 34.76237731994991, 6.5)
    )
    chimney = bpy.context.active_object
    chimney.name = "blacksmith_chimney"
    
    # Join with main building
    bpy.ops.object.select_all(action='DESELECT')
    building.select_set(True)
    chimney.select_set(True)
    bpy.context.view_layer.objects.active = building
    bpy.ops.object.join()

# Add basic roof (enhanced)
bpy.context.view_layer.objects.active = building
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 1)})
bpy.ops.transform.resize(value=(1.2, 1.2, 1))
bpy.ops.object.mode_set(mode='OBJECT')

# Create enhanced materials with textures
def create_material_with_texture(name, texture_path, base_color):
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Add principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Add output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Add texture if available
    if texture_path and os.path.exists(texture_path):
        # Add texture coordinate node
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        
        # Add mapping node
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
        
        # Add image texture node
        img_tex = nodes.new(type='ShaderNodeTexImage')
        img_tex.location = (-200, 0)
        links.new(mapping.outputs['Vector'], img_tex.inputs['Vector'])
        
        # Load image
        try:
            img = bpy.data.images.load(texture_path)
            img_tex.image = img
            links.new(img_tex.outputs['Color'], bsdf.inputs['Base Color'])
        except:
            bsdf.inputs['Base Color'].default_value = base_color
    else:
        bsdf.inputs['Base Color'].default_value = base_color
    
    return material

# Theme-based colors
theme_colors = {
    'medieval': (0.6, 0.5, 0.4, 1.0),
    'halloween': (0.3, 0.2, 0.3, 1.0),
    'spooky': (0.3, 0.2, 0.3, 1.0),
    'fantasy': (0.7, 0.6, 0.8, 1.0),
    'desert': (0.9, 0.8, 0.6, 1.0)
}

base_color = theme_colors.get("medieval", (0.5, 0.5, 0.5, 1.0))

# Apply materials with textures
if "walls" in textures:
    wall_material = create_material_with_texture("medieval_house_walls", textures["walls"], base_color)
    building.data.materials.append(wall_material)
elif "roof" in textures:
    roof_material = create_material_with_texture("medieval_house_roof", textures["roof"], base_color)
    building.data.materials.append(roof_material)
else:
    # Fallback material
    material = bpy.data.materials.new(name="medieval_house")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = base_color
    building.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.object.select_all(action='DESELECT')
    building.select_set(True)
    bpy.context.view_layer.objects.active = building
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported enhanced {building_type} to {output_path}")
