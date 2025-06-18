"""
Color mappings and theme schemes for visualization.
"""

from typing import Dict

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