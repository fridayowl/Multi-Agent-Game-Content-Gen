
import bpy
import bmesh
import random
import math
from mathutils import Vector

# AI-GENERATED CREATIVE PROP
# Prop #2: dead_tree
# AI Description: A unique spooky dead_tree with distinctive characteristics
# Style Parameters: {'trunk_style': 'twisted', 'canopy_shape': 'round', 'branch_density': 'dense', 'leaf_type': 'none', 'seasonal_state': 'autumn', 'bark_texture': 'cracked', 'height_variation': 'giant'}
# Creative Variations: 2

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# AI Texture paths
ai_textures = {"bark": "complete_game_content/complete_game_20250617_111648_Create_a_spooky_Halloween_vill/ai_creative_assets/ai_textures/wood_spooky_abda1257.png"}

# AI-Generated Geometry Parameters
HEIGHT_MULT = 0.8121376782609959
WIDTH_MULT = 1.0553995099434568
COMPLEXITY = "medium"
DETAIL_COUNT = 3
ASYMMETRY = 0.19895066395012417

print(f"🎨 Creating AI-Designed dead_tree:")
print(f"   📐 Height: {HEIGHT_MULT:.2f}x, Width: {WIDTH_MULT:.2f}x")
print(f"   🔧 Complexity: {COMPLEXITY}")
print(f"   ✨ Details: {DETAIL_COUNT}")
print(f"   🎭 Asymmetry: {ASYMMETRY:.2f}")

def create_ai_unique_dead_tree():
    """Create dead_tree with AI-determined unique characteristics"""
    
    prop_objects = []
    
    if "dead_tree" in ["tree", "oak_tree", "dead_tree", "palm_tree"]:
        # Create AI-designed tree
        prop_objects = create_ai_tree()
        
    elif "dead_tree" in ["rock", "stone", "boulder"]:
        # Create AI-designed rock
        prop_objects = create_ai_rock()
        
    elif "dead_tree" in ["bush", "shrub", "plant"]:
        # Create AI-designed bush
        prop_objects = create_ai_bush()
        
    elif "dead_tree" == "well":
        # Create AI-designed well
        prop_objects = create_ai_well()
        
    else:
        # Create generic AI prop
        prop_objects = create_ai_generic_prop()
    
    # Join all components
    if len(prop_objects) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in prop_objects:
            if obj and obj.name in bpy.data.objects:
                obj.select_set(True)
        
        if prop_objects:
            bpy.context.view_layer.objects.active = prop_objects[0]
            bpy.ops.object.join()
            
            final_prop = bpy.context.active_object
            final_prop.name = f"AI_dead_tree_1"
            
            print(f"✅ Created AI dead_tree with {len(prop_objects)} components")
    
    return prop_objects

def create_ai_tree():
    """Create AI-designed tree with unique characteristics"""
    tree_parts = []
    
    # Trunk parameters
    trunk_radius = 0.3 * WIDTH_MULT
    trunk_height = 3.0 * HEIGHT_MULT
    trunk_style = "twisted"
    
    if trunk_style == "twisted":
        # Create twisted trunk with multiple segments
        for i in range(max(2, DETAIL_COUNT // 2)):
            segment_height = trunk_height / max(2, DETAIL_COUNT // 2)
            twist_angle = i * (360 / max(2, DETAIL_COUNT // 2)) * ASYMMETRY
            
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=6,
                radius=trunk_radius * (1.0 - i * 0.1),
                depth=segment_height,
                location=(2.0, 0.0, i * segment_height + segment_height/2)
            )
            segment = bpy.context.active_object
            segment.name = f"AI_twisted_segment_{i}_1"
            segment.rotation_euler[2] = math.radians(twist_angle)
            tree_parts.append(segment)
            
    elif trunk_style == "gnarled":
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=trunk_radius * 1.2,
            depth=trunk_height * 0.8,
            location=(2.0, 0.0, trunk_height * 0.4)
        )
        trunk = bpy.context.active_object
        trunk.name = f"AI_gnarled_trunk_1"
        
        # Add gnarls (bumps)
        for i in range(DETAIL_COUNT):
            bump_radius = trunk_radius * 0.3
            angle = i * (2 * math.pi / DETAIL_COUNT)
            bump_x = 2.0 + math.cos(angle) * trunk_radius * 0.8
            bump_y = 0.0 + math.sin(angle) * trunk_radius * 0.8
            bump_z = random.uniform(0.5, trunk_height * 0.7)
            
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=1,
                radius=bump_radius,
                location=(bump_x, bump_y, bump_z)
            )
            bump = bpy.context.active_object
            bump.name = f"AI_gnarl_{i}_1"
            tree_parts.append(bump)
    
    elif trunk_style == "split":
        # Main trunk
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=trunk_radius,
            depth=trunk_height * 0.6,
            location=(2.0, 0.0, trunk_height * 0.3)
        )
        trunk = bpy.context.active_object
        trunk.name = f"AI_split_main_1"
        tree_parts.append(trunk)
        
        # Split branches
        for i in range(2):
            offset_x = (-1 if i == 0 else 1) * trunk_radius * 0.5
            offset_y = random.uniform(-trunk_radius, trunk_radius) * 0.3
            
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=6,
                radius=trunk_radius * 0.7,
                depth=trunk_height * 0.5,
                location=(2.0 + offset_x, 0.0 + offset_y, trunk_height * 0.75)
            )
            branch = bpy.context.active_object
            branch.name = f"AI_split_branch_{i}_1"
            branch.rotation_euler[0] = math.radians(30 + ASYMMETRY * 20)
            tree_parts.append(branch)
            
    else:  # straight
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=trunk_radius,
            depth=trunk_height,
            location=(2.0, 0.0, trunk_height/2)
        )
        trunk = bpy.context.active_object
        trunk.name = f"AI_straight_trunk_1"
        tree_parts.append(trunk)
    
    # Create AI-determined canopy
    canopy_shape = "round"
    canopy_size = 2.5 * WIDTH_MULT
    canopy_height = trunk_height + canopy_size * 0.5
    
    if canopy_shape == "round":
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=canopy_size,
            location=(2.0, 0.0, canopy_height)
        )
        canopy = bpy.context.active_object
        canopy.name = f"AI_round_canopy_1"
        tree_parts.append(canopy)
        
    elif canopy_shape == "oval":
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=canopy_size,
            location=(2.0, 0.0, canopy_height)
        )
        canopy = bpy.context.active_object
        canopy.scale = (1.0, 0.7, 1.3)  # Oval shape
        bpy.ops.object.transform_apply(scale=True)
        canopy.name = f"AI_oval_canopy_1"
        tree_parts.append(canopy)
        
    elif canopy_shape == "irregular":
        # Create multiple overlapping spheres for irregular shape
        for i in range(DETAIL_COUNT):
            offset_x = random.uniform(-1, 1) * ASYMMETRY
            offset_y = random.uniform(-1, 1) * ASYMMETRY
            offset_z = random.uniform(-0.5, 0.5) * ASYMMETRY
            size = canopy_size * random.uniform(0.6, 1.2)
            
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=1,
                radius=size,
                location=(2.0 + offset_x, 0.0 + offset_y, canopy_height + offset_z)
            )
            sphere = bpy.context.active_object
            sphere.name = f"AI_irregular_canopy_{i}_1"
            tree_parts.append(sphere)
    
    elif canopy_shape == "sparse":
        # Create few separate leaf clusters
        cluster_count = max(2, DETAIL_COUNT // 2)
        for i in range(cluster_count):
            angle = (i * 2 * math.pi / cluster_count) + (ASYMMETRY * random.uniform(-0.5, 0.5))
            radius = canopy_size * 0.7
            
            cluster_x = 2.0 + math.cos(angle) * radius
            cluster_y = 0.0 + math.sin(angle) * radius
            cluster_z = canopy_height + random.uniform(-0.5, 0.5)
            
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=1,
                radius=canopy_size * 0.4,
                location=(cluster_x, cluster_y, cluster_z)
            )
            cluster = bpy.context.active_object
            cluster.name = f"AI_sparse_cluster_{i}_1"
            tree_parts.append(cluster)
    
    elif canopy_shape == "palm_fronds":
        # Create palm fronds
        frond_count = max(6, DETAIL_COUNT)
        for i in range(frond_count):
            angle = i * (2 * math.pi / frond_count)
            frond_length = canopy_size * 1.5
            
            frond_x = 2.0 + math.cos(angle) * frond_length * 0.7
            frond_y = 0.0 + math.sin(angle) * frond_length * 0.7
            frond_z = canopy_height + random.uniform(-0.2, 0.2)
            
            bpy.ops.mesh.primitive_cube_add(
                size=0.2,
                location=(frond_x, frond_y, frond_z)
            )
            frond = bpy.context.active_object
            frond.scale = (0.3, frond_length, 0.1)
            bpy.ops.object.transform_apply(scale=True)
            frond.rotation_euler[2] = angle + math.radians(90)
            frond.name = f"AI_palm_frond_{i}_1"
            tree_parts.append(frond)
    
    else:  # Default round canopy
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=canopy_size,
            location=(2.0, 0.0, canopy_height)
        )
        canopy = bpy.context.active_object
        canopy.name = f"AI_default_canopy_1"
        tree_parts.append(canopy)
    
    return tree_parts

def create_ai_rock():
    """Create AI-designed rock with unique characteristics"""
    rock_parts = []
    
    # Base rock
    rock_shape = "rounded"
    base_size = 1.0 * WIDTH_MULT
    rock_height = 0.8 * HEIGHT_MULT
    
    if rock_shape == "angular":
        bpy.ops.mesh.primitive_cube_add(
            size=base_size,
            location=(2.0, 0.0, rock_height/2)
        )
        rock = bpy.context.active_object
        rock.scale = (1.0, 0.8, rock_height)
        
        # Add random rotation for natural look
        rock.rotation_euler = (
            random.uniform(-0.2, 0.2) * ASYMMETRY,
            random.uniform(-0.2, 0.2) * ASYMMETRY,
            random.uniform(0, 2*math.pi) * ASYMMETRY
        )
        
    elif rock_shape == "crystalline":
        # Create crystal-like rock
        bpy.ops.mesh.primitive_cone_add(
            vertices=6,
            radius1=base_size,
            radius2=0.2,
            depth=rock_height * 1.5,
            location=(2.0, 0.0, rock_height * 0.75)
        )
        rock = bpy.context.active_object
        
        # Add smaller crystals
        for i in range(DETAIL_COUNT // 2):
            offset_x = random.uniform(-base_size, base_size) * 0.7
            offset_y = random.uniform(-base_size, base_size) * 0.7
            
            bpy.ops.mesh.primitive_cone_add(
                vertices=6,
                radius1=base_size * 0.3,
                radius2=0.1,
                depth=rock_height * 0.7,
                location=(2.0 + offset_x, 0.0 + offset_y, rock_height * 0.35)
            )
            crystal = bpy.context.active_object
            crystal.name = f"AI_crystal_{i}_1"
            rock_parts.append(crystal)
        
    else:  # rounded or default
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=base_size,
            location=(2.0, 0.0, rock_height/2)
        )
        rock = bpy.context.active_object
        rock.scale = (1.0, 1.0, rock_height)
        bpy.ops.object.transform_apply(scale=True)
    
    rock.name = f"AI_rounded_rock_1"
    rock_parts.append(rock)
    
    return rock_parts

def create_ai_bush():
    """Create AI-designed bush with unique characteristics"""
    bush_parts = []
    
    bush_shape = "round"
    bush_size = 1.2 * WIDTH_MULT
    bush_height = 0.8 * HEIGHT_MULT
    
    if bush_shape == "spreading":
        # Create multiple small spheres spread out
        for i in range(DETAIL_COUNT):
            offset_x = random.uniform(-bush_size, bush_size) * 0.6
            offset_y = random.uniform(-bush_size, bush_size) * 0.6
            sphere_size = bush_size * random.uniform(0.3, 0.6)
            
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=1,
                radius=sphere_size,
                location=(2.0 + offset_x, 0.0 + offset_y, bush_height * 0.4)
            )
            sphere = bpy.context.active_object
            sphere.name = f"AI_spreading_bush_{i}_1"
            bush_parts.append(sphere)
    
    else:  # round or default
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=bush_size,
            location=(2.0, 0.0, bush_height/2)
        )
        bush = bpy.context.active_object
        bush.scale = (1.0, 1.0, bush_height)
        bpy.ops.object.transform_apply(scale=True)
        bush.name = f"AI_round_bush_1"
        bush_parts.append(bush)
    
    return bush_parts

def create_ai_well():
    """Create AI-designed well"""
    well_parts = []
    
    # Well base
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=1.0 * WIDTH_MULT,
        depth=0.5,
        location=(2.0, 0.0, 0.25)
    )
    base = bpy.context.active_object
    base.name = f"AI_well_base_1"
    well_parts.append(base)
    
    # Well wall
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.8 * WIDTH_MULT,
        depth=1.0 * HEIGHT_MULT,
        location=(2.0, 0.0, 0.5 * HEIGHT_MULT)
    )
    wall = bpy.context.active_object
    wall.name = f"AI_well_wall_1"
    well_parts.append(wall)
    
    # Well roof (optional)
    if random.random() > 0.5:  # 50% chance of roof
        bpy.ops.mesh.primitive_cone_add(
            vertices=8,
            radius1=1.2 * WIDTH_MULT,
            radius2=0.1,
            depth=0.8,
            location=(2.0, 0.0, HEIGHT_MULT + 0.4)
        )
        roof = bpy.context.active_object
        roof.name = f"AI_well_roof_1"
        well_parts.append(roof)
    
    return well_parts

def create_ai_generic_prop():
    """Create generic AI prop"""
    prop_parts = []
    
    # Simple geometric shape
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=0.5 * WIDTH_MULT,
        location=(2.0, 0.0, 0.5 * HEIGHT_MULT)
    )
    prop = bpy.context.active_object
    prop.name = f"AI_generic_prop_1"
    prop_parts.append(prop)
    
    return prop_parts

# Execute the creation
try:
    created_objects = create_ai_unique_dead_tree()
    print(f"✅ Successfully created AI dead_tree with {len(created_objects)} components")
    print(f"🎨 Style: {'trunk_style': 'twisted', 'canopy_shape': 'round', 'branch_density': 'dense', 'leaf_type': 'none', 'seasonal_state': 'autumn', 'bark_texture': 'cracked', 'height_variation': 'giant'}")
    print(f"🎯 Variations: 2")
except Exception as e:
    print(f"❌ Error creating AI dead_tree: {e}")
    import traceback
    traceback.print_exc()

print("🎯 AI-Creative Generation Script Complete!")
