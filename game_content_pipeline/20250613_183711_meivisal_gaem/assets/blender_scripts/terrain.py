
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
material = bpy.data.materials.new(name="medieval_terrain")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]

# Theme-based terrain colors
theme_colors = {
    'medieval': (0.2, 0.5, 0.1, 1.0),
    'halloween': (0.3, 0.2, 0.1, 1.0),
    'spooky': (0.3, 0.2, 0.1, 1.0),
    'fantasy': (0.1, 0.6, 0.2, 1.0),
    'desert': (0.9, 0.7, 0.4, 1.0)
}

color = theme_colors.get("medieval", (0.3, 0.4, 0.2, 1.0))
bsdf.inputs[0].default_value = color
terrain.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported terrain to {output_path}")
