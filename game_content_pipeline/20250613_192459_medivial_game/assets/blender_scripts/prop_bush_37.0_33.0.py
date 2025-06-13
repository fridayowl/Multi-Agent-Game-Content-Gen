
import bpy
import sys
import random

# AI Description: 

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Texture paths  
textures = {"foliage": "textures/generic_medieval_d99bbc32.png"}

# Create enhanced bush
if "bush" == "bush":
    # Create multiple spheres for fuller bush
    for i in range(3):
        offset_x = random.uniform(-0.5, 0.5)
        offset_y = random.uniform(-0.5, 0.5)
        offset_z = random.uniform(0, 0.3)
        radius = random.uniform(0.6, 1.2)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=radius,
            location=(37.0 + offset_x, 33.0 + offset_y, 0.5 + offset_z)
        )
        sphere = bpy.context.active_object
        sphere.name = f"Bush_Part_{i}"
    
    # Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.name.startswith("Bush_Part_"):
            obj.select_set(True)
    
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    
    prop = bpy.context.active_object
    prop.name = "Enhanced_Bush_37.0_33.0"
    
    # Bush material
    material = bpy.data.materials.new(name="medieval_bush")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    
    bush_colors = {
        'medieval': (0.2, 0.5, 0.1, 1.0),
        'spooky': (0.3, 0.3, 0.1, 1.0),
        'halloween': (0.4, 0.2, 0.0, 1.0),
        'fantasy': (0.1, 0.6, 0.3, 1.0),
        'desert': (0.5, 0.4, 0.2, 1.0)
    }
    
    bsdf.inputs['Base Color'].default_value = bush_colors.get("medieval", (0.2, 0.5, 0.1, 1.0))
    bsdf.inputs['Subsurface'].default_value = 0.1
    prop.data.materials.append(material)

elif "bush" == "flower_patch":
    # Create ground patch
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16,
        radius=1.0,
        depth=0.1,
        location=(37.0, 33.0, 0.05)
    )
    ground = bpy.context.active_object
    ground.name = "Flower_Ground"
    
    # Add small flower details
    for i in range(8):
        angle = i * 0.785  # 45 degrees
        import math
        x_offset = 0.7 * math.cos(angle)
        y_offset = 0.7 * math.sin(angle)
        
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=1,
            radius=0.05,
            location=(37.0 + x_offset, 33.0 + y_offset, 0.15)
        )
        flower = bpy.context.active_object
        flower.name = f"Flower_{i}"
    
    # Join all parts
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.name.startswith("Flower_"):
            obj.select_set(True)
    ground.select_set(True)
    
    bpy.context.view_layer.objects.active = ground
    bpy.ops.object.join()
    
    prop = bpy.context.active_object
    prop.name = "Enhanced_FlowerPatch_37.0_33.0"
    
    # Flower material
    material = bpy.data.materials.new(name="medieval_flowers")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    
    flower_colors = {
        'medieval': (0.8, 0.4, 0.6, 1.0),
        'spooky': (0.4, 0.2, 0.5, 1.0),
        'halloween': (0.9, 0.5, 0.0, 1.0),
        'fantasy': (0.9, 0.3, 0.8, 1.0),
        'desert': (0.9, 0.8, 0.3, 1.0)
    }
    
    bsdf.inputs['Base Color'].default_value = flower_colors.get("medieval", (0.8, 0.4, 0.6, 1.0))
    bsdf.inputs['Emission'].default_value = flower_colors.get("medieval", (0.8, 0.4, 0.6, 1.0))
    bsdf.inputs['Emission Strength'].default_value = 0.2
    prop.data.materials.append(material)

else:
    # Generic enhanced prop
    bpy.ops.mesh.primitive_cube_add(location=(37.0, 33.0, 0.5))
    prop = bpy.context.active_object
    prop.name = "Enhanced_bush_37.0_33.0"
    
    # Add some detail
    prop.scale = (random.uniform(0.8, 1.2), random.uniform(0.8, 1.2), random.uniform(0.8, 1.2))
    bpy.ops.object.transform_apply(scale=True)
    
    # Generic material
    material = bpy.data.materials.new(name="medieval_bush")
    material.use_nodes = True
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (0.6, 0.6, 0.6, 1.0)
    prop.data.materials.append(material)

# Export
if len(sys.argv) > 4:
    output_path = sys.argv[5]
    bpy.ops.export_scene.obj(filepath=output_path, use_selection=True)
    print(f"Exported enhanced {prop_type} to {output_path}")
