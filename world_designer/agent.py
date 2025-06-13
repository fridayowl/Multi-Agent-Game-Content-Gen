import asyncio
import json
import random
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Google ADK imports (correct structure)
from google.adk.agents import Agent

class TerrainType(Enum):
    GRASS = "grass"
    DIRT = "dirt" 
    STONE = "stone"
    WATER = "water"
    SAND = "sand"
    FOREST = "forest"
    MOUNTAIN = "mountain"

@dataclass
class WorldPosition:
    x: float
    y: float
    z: float = 0.0

@dataclass
class WorldSpec:
    theme: str
    size: Tuple[int, int]
    terrain_map: List[List[str]]
    buildings: List[Dict]
    paths: List[Dict]
    natural_features: List[Dict]
    spawn_points: List[Dict]
    boundaries: Dict[str, float]
    metadata: Dict

def design_world_from_prompt(prompt: str):
    """
    Design a complete game world from a text prompt.
    
    Args:
        prompt: Natural language description of the world to create (e.g., "Create a spooky Halloween village")
        
    Returns:
        Complete world specification with buildings, terrain, paths, and features
    """
    constraints = {}  # Use empty dict as default
    
    print(f"🌍 Designing world from prompt: {prompt}")
    
    try:
        # Step 1: Analyze the prompt
        analysis = _analyze_design_prompt(prompt, constraints)
        print(f"📊 Analysis complete: {analysis.get('theme', 'unknown')} theme")
        
        # Step 2: Generate world specification  
        world_spec = _generate_world_spec(analysis)
        print(f"🏗️ Generated world: {len(world_spec.buildings)} buildings, {len(world_spec.paths)} paths")
        
        # Step 3: Validate design
        validated_spec = _validate_design(world_spec)
        
        # Step 4: Create visualization data
        visualization_data = _create_visualization_data(validated_spec)
        
        result = {
            "world_spec": asdict(validated_spec),
            "visualization_data": visualization_data,
            "analysis": analysis,
            "status": "success",
            "generation_time": "2-5 minutes",
            "complexity_score": _calculate_complexity(validated_spec.buildings, validated_spec.paths)
        }
        
        print(f"✅ World design completed successfully!")
        return result
        
    except Exception as e:
        print(f"❌ Error in world design: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "fallback_available": True
        }

def _analyze_design_prompt(prompt: str, constraints):
    """Analyze the design prompt to extract requirements"""
    
    # Parse prompt using keyword detection
    analysis = _parse_prompt_keywords(prompt)
    
    # Add enhanced analysis
    analysis["environmental_story"] = _generate_environmental_story(analysis)
    analysis["layout_type"] = _determine_optimal_layout(analysis)
    analysis["gameplay_flow"] = _analyze_gameplay_implications(analysis)
    
    return analysis

def _parse_prompt_keywords(prompt: str):
    """Parse prompt using keyword detection and rules"""
    prompt_lower = prompt.lower()
    
    # Theme detection
    theme_keywords = {
        "medieval": ["medieval", "castle", "knight", "blacksmith", "tavern"],
        "spooky": ["spooky", "halloween", "ghost", "haunted", "scary", "dark"],
        "halloween": ["halloween", "pumpkin", "witch", "skeleton", "zombie"],
        "desert": ["desert", "oasis", "sand", "trading post", "merchant", "dune"],
        "fantasy": ["fantasy", "magic", "wizard", "dragon", "elf", "dwarf"],
        "modern": ["modern", "city", "urban", "contemporary"],
        "sci-fi": ["sci-fi", "space", "futuristic", "cyber", "robot"]
    }
    
    detected_theme = "medieval"  # default
    for theme, keywords in theme_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_theme = theme
            break
    
    # Scale detection
    scale_keywords = {
        "outpost": ["outpost", "camp", "small settlement"],
        "village": ["village", "hamlet", "small town"],
        "town": ["town", "large village"],
        "city": ["city", "large town", "metropolis"]
    }
    
    detected_scale = "village"  # default
    for scale, keywords in scale_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_scale = scale
            break
    
    # Feature extraction
    building_keywords = {
        "house": ["house", "home", "residence", "dwelling"],
        "shop": ["shop", "store", "merchant"],
        "tavern": ["tavern", "inn", "pub", "bar"],
        "church": ["church", "temple", "shrine", "cathedral"],
        "blacksmith": ["blacksmith", "forge", "smithy"],
        "market": ["market", "bazaar", "marketplace"],
        "fountain": ["fountain", "well", "water feature"],
        "tower": ["tower", "spire", "lookout"],
        "wall": ["wall", "fortification", "defense"]
    }
    
    detected_features = []
    for building, keywords in building_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_features.append(building)
    
    # If no specific features mentioned, add defaults based on theme
    if not detected_features:
        theme_defaults = {
            "medieval": ["house", "tavern", "blacksmith", "market"],
            "spooky": ["house", "church", "tower"],
            "halloween": ["house", "church", "tower"],
            "desert": ["house", "market", "fountain"],
            "fantasy": ["house", "tavern", "market", "tower"]
        }
        detected_features = theme_defaults.get(detected_theme, ["house", "tavern"])
    
    # NPC and quest detection
    npc_count = 5  # default
    quest_count = 3  # default
    
    # Look for numbers in prompt
    import re
    numbers = re.findall(r'\d+', prompt)
    if numbers:
        for i, num in enumerate(numbers):
            if "npc" in prompt_lower or "character" in prompt_lower:
                npc_count = int(num)
            elif "quest" in prompt_lower:
                quest_count = int(num)
    
    return {
        "theme": detected_theme,
        "scope": detected_scale,
        "key_features": detected_features,
        "npc_count": npc_count,
        "quest_count": quest_count,
        "mood": _infer_mood(detected_theme, prompt_lower),
        "size": _calculate_size_from_scope(detected_scale)
    }

def _infer_mood(theme: str, prompt_lower: str) -> str:
    """Infer mood from theme and prompt content"""
    mood_keywords = {
        "dark": ["dark", "gloomy", "ominous", "forbidding"],
        "cheerful": ["bright", "cheerful", "happy", "welcoming"],
        "mysterious": ["mysterious", "enigmatic", "hidden", "secret"],
        "bustling": ["busy", "bustling", "active", "lively"]
    }
    
    for mood, keywords in mood_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return mood
    
    # Default moods by theme
    theme_moods = {
        "medieval": "rustic",
        "spooky": "dark", 
        "halloween": "dark",
        "desert": "mysterious",
        "fantasy": "magical"
    }
    
    return theme_moods.get(theme, "neutral")

def _calculate_size_from_scope(scope: str) -> Tuple[int, int]:
    """Calculate world size based on scope"""
    size_map = {
        "outpost": (20, 20),
        "village": (40, 40),
        "town": (60, 60),
        "city": (100, 100)
    }
    return size_map.get(scope, (40, 40))

def _generate_environmental_story(analysis: Dict) -> str:
    """Generate environmental storytelling elements"""
    theme = analysis.get("theme", "medieval")
    scope = analysis.get("scope", "village")
    mood = analysis.get("mood", "neutral")
    
    stories = {
        ("medieval", "village"): "A peaceful farming community with a central market square where travelers rest",
        ("spooky", "village"): "An abandoned settlement where shadows move between crumbling buildings",
        ("halloween", "village"): "A village celebrating eternal Halloween where pumpkins glow mysteriously",
        ("desert", "village"): "An oasis trading post where merchants gather to exchange exotic goods"
    }
    
    return stories.get((theme, scope), f"A {mood} {scope} with {theme} architecture")

def _determine_optimal_layout(analysis: Dict) -> str:
    """Determine optimal layout pattern"""
    scope = analysis.get("scope", "village")
    
    layout_rules = {
        "outpost": "linear",
        "village": "radial", 
        "town": "grid",
        "city": "complex_grid"
    }
    
    return layout_rules.get(scope, "radial")

def _analyze_gameplay_implications(analysis: Dict) -> Dict:
    """Analyze gameplay flow implications"""
    return {
        "player_spawn_areas": ["main_entrance", "central_square"],
        "quest_hubs": analysis.get("key_features", [])[:3],
        "exploration_points": ["outskirts", "hidden_areas"],
        "social_areas": ["tavern", "market", "fountain"]
    }

def _generate_world_spec(analysis):
    """Generate detailed world specification"""
    
    theme = analysis.get("theme", "medieval")
    size = analysis.get("size", (40, 40))
    layout_type = analysis.get("layout_type", "radial")
    
    print(f"🗺️ Generating {size[0]}x{size[1]} {theme} world with {layout_type} layout")
    
    # Generate terrain map
    terrain_map = _generate_terrain_map(size, theme)
    
    # Plan and place buildings
    buildings = _plan_building_placement(analysis, size, terrain_map)
    
    # Generate path network
    paths = _generate_path_network(buildings, size)
    
    # Place natural features
    natural_features = _place_natural_features(analysis, terrain_map, buildings)
    
    # Calculate spawn points
    spawn_points = _calculate_spawn_points(buildings, paths)
    
    # Create world specification
    world_spec = WorldSpec(
        theme=theme,
        size=size,
        terrain_map=terrain_map,
        buildings=buildings,
        paths=paths,
        natural_features=natural_features,
        spawn_points=spawn_points,
        boundaries={"min_x": 0, "max_x": size[0], "min_y": 0, "max_y": size[1]},
        metadata={
            "analysis": analysis,
            "layout_type": layout_type,
            "building_count": len(buildings),
            "complexity_score": _calculate_complexity(buildings, paths),
            "estimated_build_time": f"{len(buildings) * 2 + len(natural_features)} minutes"
        }
    )
    
    return world_spec

def _generate_terrain_map(size: Tuple[int, int], theme: str) -> List[List[str]]:
    """Generate terrain map using theme-based procedural generation"""
    
    print(f"🌱 Generating terrain map for {theme} theme")
    
    # Get terrain weights for theme
    terrain_weights = _get_terrain_weights(theme)
    
    # Initialize terrain map
    terrain_map = []
    
    # Generate base terrain using simple noise
    for y in range(size[1]):
        row = []
        for x in range(size[0]):
            terrain_type = _select_terrain_type(x, y, size, terrain_weights)
            row.append(terrain_type)
        terrain_map.append(row)
    
    # Apply smoothing passes
    terrain_map = _smooth_terrain(terrain_map)
    
    # Add theme-specific features
    terrain_map = _add_terrain_features(terrain_map, theme)
    
    return terrain_map

def _get_terrain_weights(theme: str) -> Dict[str, float]:
    """Get terrain distribution weights by theme"""
    weights = {
        "medieval": {"grass": 0.4, "dirt": 0.3, "stone": 0.2, "water": 0.1},
        "spooky": {"dirt": 0.5, "stone": 0.3, "grass": 0.2},
        "halloween": {"dirt": 0.5, "stone": 0.3, "grass": 0.2},
        "desert": {"sand": 0.7, "stone": 0.2, "water": 0.1},
        "fantasy": {"grass": 0.3, "forest": 0.3, "stone": 0.2, "water": 0.2}
    }
    return weights.get(theme, weights["medieval"])

def _select_terrain_type(x: int, y: int, size: Tuple[int, int], weights: Dict[str, float]) -> str:
    """Select terrain type using weighted probability"""
    # Simple procedural selection with position influence
    center_x, center_y = size[0] // 2, size[1] // 2
    distance_from_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
    edge_distance = min(x, y, size[0] - x, size[1] - y)
    
    # Modify weights based on position
    modified_weights = weights.copy()
    
    # Water more likely at edges
    if "water" in modified_weights and edge_distance < 3:
        modified_weights["water"] *= 2
    
    # Center areas more likely to be grass/clear
    if "grass" in modified_weights and distance_from_center < size[0] // 4:
        modified_weights["grass"] *= 1.5
    
    # Weighted random selection
    terrain_types = list(modified_weights.keys())
    terrain_probs = list(modified_weights.values())
    
    # Normalize
    total = sum(terrain_probs)
    terrain_probs = [p / total for p in terrain_probs]
    
    # Select
    rand = random.random()
    cumulative = 0
    for i, prob in enumerate(terrain_probs):
        cumulative += prob
        if rand <= cumulative:
            return terrain_types[i]
    
    return terrain_types[0]

def _smooth_terrain(terrain_map: List[List[str]]) -> List[List[str]]:
    """Apply smoothing to reduce noise in terrain"""
    height, width = len(terrain_map), len(terrain_map[0])
    
    # One smoothing pass
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            neighbors = [
                terrain_map[y-1][x], terrain_map[y+1][x],
                terrain_map[y][x-1], terrain_map[y][x+1]
            ]
            
            # Count neighbor types
            neighbor_counts = {}
            for neighbor in neighbors:
                neighbor_counts[neighbor] = neighbor_counts.get(neighbor, 0) + 1
            
            # If 3+ neighbors are same type, convert
            most_common = max(neighbor_counts.items(), key=lambda x: x[1])
            if most_common[1] >= 3:
                terrain_map[y][x] = most_common[0]
    
    return terrain_map

def _add_terrain_features(terrain_map: List[List[str]], theme: str) -> List[List[str]]:
    """Add theme-specific terrain features"""
    if theme in ["spooky", "halloween"]:
        _add_scattered_terrain(terrain_map, "dirt", density=0.1)
    elif theme == "desert":
        _add_clustered_terrain(terrain_map, "water", cluster_size=2, count=1)
    
    return terrain_map

def _add_scattered_terrain(terrain_map: List[List[str]], terrain_type: str, density: float):
    """Add scattered terrain patches"""
    height, width = len(terrain_map), len(terrain_map[0])
    for y in range(height):
        for x in range(width):
            if random.random() < density:
                terrain_map[y][x] = terrain_type

def _add_clustered_terrain(terrain_map: List[List[str]], terrain_type: str, cluster_size: int, count: int):
    """Add clustered terrain features"""
    height, width = len(terrain_map), len(terrain_map[0])
    
    for _ in range(count):
        center_x = random.randint(cluster_size, width - cluster_size - 1)
        center_y = random.randint(cluster_size, height - cluster_size - 1)
        
        for dy in range(-cluster_size, cluster_size + 1):
            for dx in range(-cluster_size, cluster_size + 1):
                if dx*dx + dy*dy <= cluster_size*cluster_size:
                    x, y = center_x + dx, center_y + dy
                    if 0 <= x < width and 0 <= y < height:
                        terrain_map[y][x] = terrain_type

def _plan_building_placement(analysis: Dict, size: Tuple[int, int], terrain_map: List[List[str]]) -> List[Dict]:
    """Plan intelligent building placement"""
    
    buildings = []
    theme = analysis.get("theme", "medieval")
    layout_type = analysis.get("layout_type", "radial")
    key_features = analysis.get("key_features", ["house", "tavern"])
    
    print(f"🏘️ Placing buildings: {key_features}")
    
    center_x, center_y = size[0] // 2, size[1] // 2
    
    if layout_type == "radial":
        buildings = _create_radial_layout(key_features, center_x, center_y, theme)
    elif layout_type == "grid":
        buildings = _create_grid_layout(key_features, size, theme)
    elif layout_type == "linear":
        buildings = _create_linear_layout(key_features, size, theme)
    else:
        buildings = _create_radial_layout(key_features, center_x, center_y, theme)
    
    # Add additional houses to fill out the settlement
    buildings.extend(_add_residential_buildings(buildings, size, theme))
    
    return buildings

def _create_radial_layout(key_features: List[str], center_x: float, center_y: float, theme: str) -> List[Dict]:
    """Create radial layout with center plaza"""
    buildings = []
    
    # Central feature (fountain, market, etc.)
    if "fountain" in key_features or "market" in key_features:
        central_type = "fountain" if "fountain" in key_features else "market"
        buildings.append({
            "id": "building_center",
            "type": central_type,
            "position": {"x": center_x, "y": center_y, "z": 0.0},
            "rotation": 0.0,
            "scale": 1.2,
            "properties": {"importance": "high", "central": True}
        })
    
    # Place key buildings in circle around center
    radius = 12
    for i, building_type in enumerate(key_features[:6]):  # Max 6 key buildings
        if building_type in ["fountain", "market"] and len(buildings) > 0:
            continue  # Already placed as central feature
            
        angle = (i * 2 * math.pi) / len(key_features)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        
        buildings.append({
            "id": f"building_{len(buildings)}",
            "type": building_type,
            "position": {"x": x, "y": y, "z": 0.0},
            "rotation": math.degrees(angle + math.pi),  # Face center
            "scale": 1.0,
            "properties": {"importance": "high" if building_type in ["tavern", "church"] else "normal"}
        })
    
    return buildings

def _create_grid_layout(key_features: List[str], size: Tuple[int, int], theme: str) -> List[Dict]:
    """Create grid-based town layout"""
    buildings = []
    
    # Define main street grid
    grid_spacing = 8
    start_x = size[0] // 4
    start_y = size[1] // 4
    
    # Place buildings on grid intersections
    for i, building_type in enumerate(key_features):
        grid_x = i % 3
        grid_y = i // 3
        
        x = start_x + grid_x * grid_spacing
        y = start_y + grid_y * grid_spacing
        
        buildings.append({
            "id": f"building_{len(buildings)}",
            "type": building_type,
            "position": {"x": x, "y": y, "z": 0.0},
            "rotation": random.uniform(0, 360),
            "scale": 1.0,
            "properties": {"importance": "high" if building_type in ["market", "church"] else "normal"}
        })
    
    return buildings

def _create_linear_layout(key_features: List[str], size: Tuple[int, int], theme: str) -> List[Dict]:
    """Create linear outpost layout"""
    buildings = []
    
    # Main road through center
    road_y = size[1] // 2
    spacing = size[0] // (len(key_features) + 1)
    
    for i, building_type in enumerate(key_features):
        x = spacing * (i + 1)
        y = road_y + random.uniform(-3, 3)  # Slight variation
        
        buildings.append({
            "id": f"building_{len(buildings)}",
            "type": building_type,
            "position": {"x": x, "y": y, "z": 0.0},
            "rotation": random.uniform(-30, 30),
            "scale": 1.0,
            "properties": {"importance": "normal"}
        })
    
    return buildings

def _add_residential_buildings(existing_buildings: List[Dict], size: Tuple[int, int], theme: str) -> List[Dict]:
    """Add residential buildings to fill out the settlement"""
    houses = []
    
    # Add 3-6 additional houses
    house_count = random.randint(3, 6)
    
    for i in range(house_count):
        # Find position away from existing buildings
        attempts = 0
        while attempts < 20:
            x = random.uniform(5, size[0] - 5)
            y = random.uniform(5, size[1] - 5)
            
            # Check distance from existing buildings
            too_close = any(
                _distance({"x": x, "y": y}, b["position"]) < 6
                for b in existing_buildings
            )
            
            if not too_close:
                houses.append({
                    "id": f"house_{len(houses)}",
                    "type": "house",
                    "position": {"x": x, "y": y, "z": 0.0},
                    "rotation": random.uniform(0, 360),
                    "scale": random.uniform(0.8, 1.2),
                    "properties": {"importance": "low", "residential": True}
                })
                break
            
            attempts += 1
    
    return houses

def _distance(pos1: Dict, pos2: Dict) -> float:
    """Calculate distance between positions"""
    dx = pos1["x"] - pos2["x"]
    dy = pos1["y"] - pos2["y"]
    return math.sqrt(dx*dx + dy*dy)

def _generate_path_network(buildings: List[Dict], size: Tuple[int, int]) -> List[Dict]:
    """Generate intelligent path network"""
    
    paths = []
    
    if not buildings:
        return paths
    
    print(f"🛤️ Creating path network for {len(buildings)} buildings")
    
    # Find important buildings for main roads
    important_buildings = [b for b in buildings if b["properties"].get("importance") == "high"]
    if not important_buildings:
        important_buildings = buildings[:max(1, len(buildings) // 3)]
    
    # Create main paths between important buildings
    for i, building1 in enumerate(important_buildings):
        for building2 in important_buildings[i+1:]:
            path = {
                "id": f"main_path_{len(paths)}",
                "start": building1["position"].copy(),
                "end": building2["position"].copy(),
                "width": 3.0,
                "surface_type": "cobblestone",
                "properties": {"type": "main_road", "importance": "high"}
            }
            paths.append(path)
    
    # Connect other buildings to nearest important building
    for building in buildings:
        if building not in important_buildings:
            nearest = min(important_buildings, 
                         key=lambda b: _distance(building["position"], b["position"]))
            
            path = {
                "id": f"side_path_{len(paths)}",
                "start": building["position"].copy(),
                "end": nearest["position"].copy(),
                "width": 2.0,
                "surface_type": "dirt",
                "properties": {"type": "side_road", "importance": "normal"}
            }
            paths.append(path)
    
    return paths

def _place_natural_features(analysis: Dict, terrain_map: List[List[str]], buildings: List[Dict]) -> List[Dict]:
    """Place natural features and decorative elements"""
    
    features = []
    theme = analysis.get("theme", "medieval")
    
    print(f"🌿 Adding natural features for {theme} theme")
    
    # Theme-specific feature types
    feature_types = {
        "medieval": ["oak_tree", "rock", "bush", "flower_patch", "well"],
        "spooky": ["dead_tree", "tombstone", "raven_perch", "fog_patch", "skeleton"],
        "halloween": ["pumpkin", "dead_tree", "skeleton", "spider_web", "cauldron"],
        "desert": ["palm_tree", "cactus", "sand_dune", "oasis_rock", "desert_flower"],
        "fantasy": ["magic_tree", "crystal", "mushroom_ring", "fairy_circle", "ancient_stone"]
    }
    
    available_features = feature_types.get(theme, feature_types["medieval"])
    
    # Place features avoiding building areas
    height, width = len(terrain_map), len(terrain_map[0])
    feature_density = 0.08  # 8% of tiles get features
    
    for y in range(height):
        for x in range(width):
            if random.random() < feature_density:
                # Check if too close to buildings
                too_close_to_building = any(
                    _distance({"x": x, "y": y}, b["position"]) < 4
                    for b in buildings
                )
                
                if not too_close_to_building:
                    feature_type = random.choice(available_features)
                    
                    # Some features are rarer
                    rare_features = ["well", "skeleton", "cauldron", "crystal", "ancient_stone"]
                    if feature_type in rare_features and random.random() > 0.3:
                        continue
                    
                    feature = {
                        "id": f"feature_{len(features)}",
                        "type": feature_type,
                        "position": {"x": float(x), "y": float(y), "z": 0.0},
                        "rotation": random.uniform(0, 360),
                        "scale": random.uniform(0.7, 1.3),
                        "properties": {
                            "terrain_type": terrain_map[y][x],
                            "interactive": feature_type in ["well", "cauldron", "crystal", "ancient_stone"],
                            "decorative": True
                        }
                    }
                    features.append(feature)
    
    return features

def _calculate_spawn_points(buildings: List[Dict], paths: List[Dict]) -> List[Dict]:
    """Calculate appropriate player spawn points"""
    spawn_points = []
    
    if not buildings:
        return [{"x": 20.0, "y": 20.0, "z": 0.0, "type": "default"}]
    
    # Main entrance spawn (edge of settlement)
    center_x = sum(b["position"]["x"] for b in buildings) / len(buildings)
    center_y = sum(b["position"]["y"] for b in buildings) / len(buildings)
    
    # Find edge spawn point
    edge_spawn = {
        "x": center_x - 15,
        "y": center_y,
        "z": 0.0,
        "type": "main_entrance",
        "description": "Main entrance to settlement"
    }
    spawn_points.append(edge_spawn)
    
    # Secondary spawn near important buildings
    important_buildings = [b for b in buildings if b["properties"].get("importance") == "high"]
    if important_buildings:
        building = important_buildings[0]
        secondary_spawn = {
            "x": building["position"]["x"] + 5,
            "y": building["position"]["y"] + 5,
            "z": 0.0,
            "type": "secondary",
            "description": f"Near {building['type']}"
        }
        spawn_points.append(secondary_spawn)
    
    return spawn_points

def _validate_design(world_spec: WorldSpec) -> WorldSpec:
    """Validate and optimize the world design"""
    
    validation_issues = []
    
    # Check building accessibility
    if not _validate_accessibility(world_spec.buildings, world_spec.paths):
        validation_issues.append("Some buildings may not be accessible")
    
    # Check spawn points
    if not world_spec.spawn_points:
        validation_issues.append("No spawn points defined")
        # Add default spawn
        world_spec.spawn_points = [{"x": 20.0, "y": 20.0, "z": 0.0, "type": "default"}]
    
    # Check minimum buildings
    if len(world_spec.buildings) < 3:
        validation_issues.append("Very few buildings - consider adding more")
    
    # Log validation results
    if validation_issues:
        print(f"⚠️ Validation issues: {validation_issues}")
    else:
        print("✅ World design validation passed")
    
    # Add validation metadata
    world_spec.metadata["validation_issues"] = validation_issues
    world_spec.metadata["validation_passed"] = len(validation_issues) == 0
    
    return world_spec

def _validate_accessibility(buildings: List[Dict], paths: List[Dict]) -> bool:
    """Simple accessibility check"""
    if not buildings:
        return True
    if len(buildings) == 1:
        return True
    if not paths:
        return len(buildings) <= 2
    
    # In real implementation, would do proper graph traversal
    # For now, assume connected if paths exist
    return len(paths) > 0

def _create_visualization_data(world_spec: WorldSpec) -> Dict:
    """Create visualization metadata for the world"""
    
    return {
        "2d_layout": {
            "image_path": f"layouts/{world_spec.theme}_{len(world_spec.buildings)}_buildings.png",
            "width": world_spec.size[0],
            "height": world_spec.size[1]
        },
        "building_markers": [
            {
                "id": b["id"],
                "x": b["position"]["x"],
                "y": b["position"]["y"],
                "type": b["type"],
                "importance": b["properties"].get("importance", "normal"),
                "color": _get_building_color(b["type"]),
                "size": b["scale"]
            }
            for b in world_spec.buildings
        ],
        "path_lines": [
            {
                "id": p["id"],
                "start": [p["start"]["x"], p["start"]["y"]],
                "end": [p["end"]["x"], p["end"]["y"]],
                "width": p["width"],
                "color": "#8B4513" if p["surface_type"] == "dirt" else "#696969",
                "type": p["properties"]["type"]
            }
            for p in world_spec.paths
        ],
        "natural_features": [
            {
                "id": f["id"],
                "x": f["position"]["x"],
                "y": f["position"]["y"],
                "type": f["type"],
                "color": _get_feature_color(f["type"]),
                "interactive": f["properties"].get("interactive", False)
            }
            for f in world_spec.natural_features
        ],
        "spawn_points": [
            {
                "x": sp["x"],
                "y": sp["y"],
                "type": sp["type"],
                "color": "#00FF00"
            }
            for sp in world_spec.spawn_points
        ],
        "terrain_colors": _get_terrain_color_map(world_spec.theme),
        "legend": _create_visualization_legend(world_spec)
    }

def _get_building_color(building_type: str) -> str:
    """Get color for building type in visualization"""
    colors = {
        "house": "#8B4513",
        "tavern": "#CD853F", 
        "shop": "#DEB887",
        "market": "#F4A460",
        "church": "#D2B48C",
        "blacksmith": "#A0522D",
        "fountain": "#4682B4",
        "tower": "#708090",
        "wall": "#696969"
    }
    return colors.get(building_type, "#8B4513")

def _get_feature_color(feature_type: str) -> str:
    """Get color for natural feature in visualization"""
    colors = {
        "oak_tree": "#228B22",
        "dead_tree": "#8B4513",
        "palm_tree": "#32CD32",
        "rock": "#696969",
        "tombstone": "#2F4F4F",
        "crystal": "#9370DB",
        "cactus": "#9ACD32",
        "pumpkin": "#FF4500"
    }
    return colors.get(feature_type, "#228B22")

def _get_terrain_color_map(theme: str) -> Dict[str, str]:
    """Get terrain color mapping for theme"""
    base_colors = {
        "grass": "#228B22",
        "dirt": "#8B4513", 
        "stone": "#696969",
        "water": "#4682B4",
        "sand": "#F4A460",
        "forest": "#006400"
    }
    
    # Theme modifications
    if theme in ["spooky", "halloween"]:
        base_colors["grass"] = "#556B2F"  # Darker grass
        base_colors["dirt"] = "#654321"   # Darker dirt
    
    return base_colors

def _create_visualization_legend(world_spec: WorldSpec) -> Dict:
    """Create legend for visualization"""
    return {
        "buildings": list(set(b["type"] for b in world_spec.buildings)),
        "features": list(set(f["type"] for f in world_spec.natural_features)),
        "terrain": list(set(t for row in world_spec.terrain_map for t in row)),
        "theme": world_spec.theme,
        "scale": "1 unit = 1 meter"
    }

def _calculate_complexity(buildings: List[Dict], paths: List[Dict]) -> float:
    """Calculate design complexity score"""
    building_score = len(buildings) * 1.0
    path_score = len(paths) * 0.5
    
    # Bonus for variety
    building_types = len(set(b["type"] for b in buildings))
    variety_bonus = building_types * 0.3
    
    return building_score + path_score + variety_bonus

# Create the ADK agent
root_agent = Agent(
    name="world_designer",
    model="gemini-2.0-flash-exp",
    instruction="""You are an expert game world designer. You create detailed, engaging game environments from simple text prompts. 

Your capabilities include:
- Analyzing natural language prompts to understand world requirements
- Generating themed terrain maps with appropriate distributions
- Placing buildings intelligently with spatial reasoning
- Creating path networks that connect all areas logically
- Adding natural features and decorative elements
- Ensuring proper spawn points for players

You understand spatial relationships, environmental storytelling, game balance, and player flow. Always consider the player experience when designing worlds.

When you receive a world design request, call the design_world_from_prompt function with the user's prompt.""",
    description="AI agent that designs complete game worlds from text prompts using procedural generation and spatial reasoning",
    tools=[design_world_from_prompt]
)

# Test function that can be run independently
async def test_world_designer_standalone():
    """Test the world designer functions directly"""
    print("🚀 Testing World Designer Agent (Standalone)...")
    
    # Test prompts
    test_prompts = [
        "Create a spooky Halloween village with 5 NPCs and 3 interconnected quests",
        "Generate a desert oasis trading post with merchants and treasure hunters", 
        "Build a medieval village with a blacksmith, tavern, and church"
    ]
    
    for i, prompt in enumerate(test_prompts):
        print(f"\n📝 Test {i+1}: {prompt}")
        
        try:
            result = design_world_from_prompt(prompt)
            
            if result["status"] == "success":
                spec = result["world_spec"]
                print(f"✅ Success! Generated {spec['theme']} world:")
                print(f"   - Size: {spec['size']}")
                print(f"   - Buildings: {len(spec['buildings'])}")
                print(f"   - Paths: {len(spec['paths'])}")
                print(f"   - Features: {len(spec['natural_features'])}")
                print(f"   - Complexity: {result['complexity_score']:.1f}")
            else:
                print(f"❌ Failed: {result['error']}")
                
        except Exception as e:
            print(f"💥 Exception: {e}")
    
    print("\n🎉 World Designer testing complete!")

if __name__ == "__main__":
    # Run standalone test
    asyncio.run(test_world_designer_standalone())