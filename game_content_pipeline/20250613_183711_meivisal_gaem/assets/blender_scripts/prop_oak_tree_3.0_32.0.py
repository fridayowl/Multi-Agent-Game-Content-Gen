
import bpy
import sys

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create tree trunk
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.3,
    depth=3,
    location=(3.0, 32.0, 0.0 + 1.5)
)
trunk = bpy.context.active_object
trunk.name = "Tree_Trunk"

# Create canopy
bpy.ops.mesh.primitive_ico_sphere_add(
    radius=2,
    location=(3.0, 32.0, 0.0 + 4)
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
tree.name = "Tree_3.0_32.0"

# Create materials
trunk_material = bpy.data.materials.new(name="Trunk_Material")
trunk_material.use_nodes = True
trunk_bsdf = trunk_material.node_tree.nodes["Principled BSDF"]
trunk_bsdf.inputs[0].default_value = (0.4, 0.2, 0.1, 1.0)  # Brown

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported tree to {output_path}")
