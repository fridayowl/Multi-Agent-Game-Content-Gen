"""
Visualization data creation and formatting.
"""

from typing import Dict, List
from ..core.world_spec import WorldSpec
from ..visualization.color_schemes import _get_building_color, _get_feature_color, _get_terrain_color_map

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