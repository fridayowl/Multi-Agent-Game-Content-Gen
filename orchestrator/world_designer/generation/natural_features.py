"""
Natural feature placement and generation.
"""

import random
from typing import Dict, List
from ..utils.spatial_utils import _distance
from ..utils.theme_configs import get_theme_feature_types

def _place_natural_features(analysis: Dict, terrain_map: List[List[str]], buildings: List[Dict]) -> List[Dict]:
    """Place natural features and decorative elements"""
    
    features = []
    theme = analysis.get("theme", "medieval")
    
    print(f"🌿 Adding natural features for {theme} theme")
    
    # Get theme-specific feature types
    available_features = get_theme_feature_types(theme)
    
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