
import bpy
import sys

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create rock
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    location=(19.0, 7.0, 0.0)
)
rock = bpy.context.active_object
rock.name = "Rock_19.0_7.0"
rock.scale = (1.5, 1.2, 0.8)

# Apply scale
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Create material
material = bpy.data.materials.new(name="Rock_Material")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.4, 0.4, 0.4, 1.0)  # Gray
bsdf.inputs[7].default_value = 0.8  # Roughness
rock.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported rock to {output_path}")
