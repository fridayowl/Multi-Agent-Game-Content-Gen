
import bpy
import sys
import bmesh
from mathutils import Vector
import random

# AI Description: 

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Texture paths
textures = {"bark": "textures/wood_medieval_78e0ac7d.png", "leaves": "textures/generic_medieval_8c4304ea.png"}

# Create enhanced tree with more realistic geometry
def create_enhanced_tree():
    # Create trunk with taper
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.4,
        depth=4,
        location=(7.0, 33.0, 2.0)
    )
    trunk = bpy.context.active_object
    trunk.name = "Tree_Trunk"
    
    # Add taper to trunk
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(0.7, 0.7, 1), constraint_axis=(True, True, False))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create main canopy
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=2.5,
        location=(7.0, 33.0, 5.0)
    )
    main_canopy = bpy.context.active_object
    main_canopy.name = "Tree_Canopy_Main"
    
    # Add secondary canopy layers for fuller look
    for i in range(2):
        offset_x = random.uniform(-1, 1)
        offset_y = random.uniform(-1, 1)
        offset_z = random.uniform(-0.5, 0.5)
        radius = random.uniform(1.5, 2.0)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=radius,
            location=(7.0 + offset_x, 33.0 + offset_y, 4.5 + offset_z)
        )
        canopy = bpy.context.active_object
        canopy.name = f"Tree_Canopy_{i}"
    
    # Select all parts
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.name.startswith("Tree_"):
            obj.select_set(True)
    
    # Set trunk as active and join
    trunk.select_set(True)
    bpy.context.view_layer.objects.active = trunk
    bpy.ops.object.join()
    
    tree = bpy.context.active_object
    tree.name = "Enhanced_Tree_7.0_33.0"
    
    return tree

# Create the tree
tree = create_enhanced_tree()

# Apply enhanced materials with textures
def apply_tree_materials(tree_obj):
    # Create bark material
    bark_material = bpy.data.materials.new(name="medieval_tree_bark")
    bark_material.use_nodes = True
    nodes = bark_material.node_tree.nodes
    links = bark_material.node_tree.links
    
    # Clear default
    for node in nodes:
        nodes.remove(node)
    
    # Add nodes
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Add bark texture if available
    if "bark" in textures and textures["bark"]:
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        mapping.inputs['Scale'].default_value = (2, 2, 2)
        links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
        
        img_tex = nodes.new(type='ShaderNodeTexImage')
        img_tex.location = (-200, 0)
        links.new(mapping.outputs['Vector'], img_tex.inputs['Vector'])
        
        try:
            img = bpy.data.images.load(textures["bark"])
            img_tex.image = img
            links.new(img_tex.outputs['Color'], bsdf.inputs['Base Color'])
        except:
            bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.1, 1.0)
    else:
        bsdf.inputs['Base Color'].default_value = (0.4, 0.2, 0.1, 1.0)
    
    bsdf.inputs['Roughness'].default_value = 0.8
    
    # Create leaves material
    leaves_material = bpy.data.materials.new(name="medieval_tree_leaves")
    leaves_material.use_nodes = True
    l_nodes = leaves_material.node_tree.nodes
    l_links = leaves_material.node_tree.links
    
    for node in l_nodes:
        l_nodes.remove(node)
    
    l_bsdf = l_nodes.new(type='ShaderNodeBsdfPrincipled')
    l_output = l_nodes.new(type='ShaderNodeOutputMaterial')
    l_links.new(l_bsdf.outputs['BSDF'], l_output.inputs['Surface'])
    
    # Theme-based leaf colors
    leaf_colors = {
        'medieval': (0.2, 0.6, 0.1, 1.0),
        'spooky': (0.3, 0.2, 0.1, 1.0),
        'halloween': (0.4, 0.2, 0.0, 1.0),
        'fantasy': (0.3, 0.8, 0.2, 1.0),
        'desert': (0.6, 0.4, 0.2, 1.0)
    }
    
    l_bsdf.inputs['Base Color'].default_value = leaf_colors.get("medieval", (0.2, 0.6, 0.1, 1.0))
    l_bsdf.inputs['Subsurface'].default_value = 0.1  # Slight subsurface for leaves
    
    # Apply materials to different parts
    tree_obj.data.materials.append(bark_material)
    tree_obj.data.materials.append(leaves_material)

apply_tree_materials(tree)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported enhanced tree to {output_path}")
