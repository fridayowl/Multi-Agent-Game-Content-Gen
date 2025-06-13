
import bpy
import sys
import bmesh

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Texture paths
textures = {"grass": "textures/generic_medieval_459765a5.png", "dirt": "textures/generic_medieval_2c2daa7e.png", "stone": "textures/stone_medieval_2df9eb03.png", "water": "textures/generic_medieval_34dc039f.png"}

# Create enhanced terrain with multiple zones
bpy.ops.mesh.primitive_plane_add(size=100)
terrain = bpy.context.active_object
terrain.name = "Enhanced_Terrain"

# Add subdivision for detail
bpy.ops.object.modifier_add(type='SUBSURF')
terrain.modifiers["Subdivision Surface"].levels = 3

# Add displacement for height variation
bpy.ops.object.modifier_add(type='DISPLACE')
terrain.modifiers["Displace"].strength = 2.0

# Create enhanced materials with multiple textures
def create_terrain_material():
    material = bpy.data.materials.new(name="medieval_enhanced_terrain")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Add principled BSDF and output
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Add texture coordinate
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    # Add mapping
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (4, 4, 4)  # Tile the texture
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    
    # Use first available texture or create procedural
    if textures:
        first_texture = list(textures.values())[0]
        if first_texture and os.path.exists(first_texture):
            img_tex = nodes.new(type='ShaderNodeTexImage')
            img_tex.location = (-400, 0)
            links.new(mapping.outputs['Vector'], img_tex.inputs['Vector'])
            
            try:
                img = bpy.data.images.load(first_texture)
                img_tex.image = img
                links.new(img_tex.outputs['Color'], bsdf.inputs['Base Color'])
            except:
                # Fallback to theme color
                theme_colors = {
                    'medieval': (0.2, 0.5, 0.1, 1.0),
                    'halloween': (0.3, 0.2, 0.1, 1.0),
                    'spooky': (0.3, 0.2, 0.1, 1.0),
                    'fantasy': (0.1, 0.6, 0.2, 1.0),
                    'desert': (0.9, 0.7, 0.4, 1.0)
                }
                bsdf.inputs['Base Color'].default_value = theme_colors.get("medieval", (0.3, 0.4, 0.2, 1.0))
        else:
            # Create procedural texture
            noise = nodes.new(type='ShaderNodeTexNoise')
            noise.location = (-400, 0)
            noise.inputs['Scale'].default_value = 5.0
            links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
            
            # Color ramp for terrain variation
            color_ramp = nodes.new(type='ShaderNodeValToRGB')
            color_ramp.location = (-200, 0)
            
            # Set colors based on theme
            if "medieval" == "desert":
                color_ramp.color_ramp.elements[0].color = (0.9, 0.7, 0.4, 1.0)
                color_ramp.color_ramp.elements[1].color = (0.8, 0.6, 0.3, 1.0)
            elif "medieval" in ["spooky", "halloween"]:
                color_ramp.color_ramp.elements[0].color = (0.3, 0.2, 0.1, 1.0)
                color_ramp.color_ramp.elements[1].color = (0.2, 0.3, 0.1, 1.0)
            else:
                color_ramp.color_ramp.elements[0].color = (0.2, 0.5, 0.1, 1.0)
                color_ramp.color_ramp.elements[1].color = (0.4, 0.3, 0.2, 1.0)
            
            links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
            links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Add some roughness variation
    bsdf.inputs['Roughness'].default_value = 0.8
    
    return material

# Apply enhanced material
enhanced_material = create_terrain_material()
terrain.data.materials.append(enhanced_material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported enhanced terrain to {output_path}")
