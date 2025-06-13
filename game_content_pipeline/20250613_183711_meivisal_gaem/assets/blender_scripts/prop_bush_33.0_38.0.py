
import bpy
import sys

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create prop
bpy.ops.mesh.primitive_cube_add(location=(33.0, 38.0, 0.0))
prop = bpy.context.active_object
prop.name = "bush_33.0_38.0"

# Create material
material = bpy.data.materials.new(name="bush_Material")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.6, 0.6, 0.6, 1.0)  # Gray
prop.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported {prop_type} to {output_path}")
