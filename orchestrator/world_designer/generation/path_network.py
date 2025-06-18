"""
Path network generation and routing.
"""

from typing import List, Dict, Tuple
from ..utils.spatial_utils import _distance

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