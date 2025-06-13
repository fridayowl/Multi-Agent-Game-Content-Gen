
import bpy
import sys
import os

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create house
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(32.0, 20.0, 0.0)
)

building = bpy.context.active_object
building.name = "house_32.0_20.0"
building.scale = (8, 6, 5)

# Apply transforms
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add basic roof (simplified)
bpy.context.view_layer.objects.active = building
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, 0, 1)})
bpy.ops.transform.resize(value=(1.2, 1.2, 1))
bpy.ops.object.mode_set(mode='OBJECT')

# Create material
material = bpy.data.materials.new(name="medieval_house")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]

# Theme-based colors
theme_colors = {
    'medieval': (0.6, 0.5, 0.4, 1.0),
    'halloween': (0.3, 0.2, 0.3, 1.0),
    'spooky': (0.3, 0.2, 0.3, 1.0),
    'fantasy': (0.7, 0.6, 0.8, 1.0),
    'desert': (0.9, 0.8, 0.6, 1.0)
}

color = theme_colors.get("medieval", (0.5, 0.5, 0.5, 1.0))
bsdf.inputs[0].default_value = color
building.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]  # Blender passes -- as argv[4]
    bpy.ops.object.select_all(action='DESELECT')
    building.select_set(True)
    bpy.context.view_layer.objects.active = building
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported to {output_path}")
