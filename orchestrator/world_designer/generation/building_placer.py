"""
Building placement and layout algorithms.
"""

import math
import random
from typing import Dict, List, Tuple
from ..utils.spatial_utils import _distance

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