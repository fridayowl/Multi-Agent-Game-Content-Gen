"""
Theme-specific configuration data and mappings.
"""

from typing import Dict, List

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

def get_theme_feature_types(theme: str) -> List[str]:
    """Get natural feature types for a theme"""
    feature_types = {
        "medieval": ["oak_tree", "rock", "bush", "flower_patch", "well"],
        "spooky": ["dead_tree", "tombstone", "raven_perch", "fog_patch", "skeleton"],
        "halloween": ["pumpkin", "dead_tree", "skeleton", "spider_web", "cauldron"],
        "desert": ["palm_tree", "cactus", "sand_dune", "oasis_rock", "desert_flower"],
        "fantasy": ["magic_tree", "crystal", "mushroom_ring", "fairy_circle", "ancient_stone"]
    }
    return feature_types.get(theme, feature_types["medieval"])

def get_theme_defaults(theme: str) -> List[str]:
    """Get default building features for a theme"""
    theme_defaults = {
        "medieval": ["house", "tavern", "blacksmith", "market"],
        "spooky": ["house", "church", "tower"],
        "halloween": ["house", "church", "tower"],
        "desert": ["house", "market", "fountain"],
        "fantasy": ["house", "tavern", "market", "tower"]
    }
    return theme_defaults.get(theme, ["house", "tavern"])

def get_theme_moods() -> Dict[str, str]:
    """Get default moods by theme"""
    return {
        "medieval": "rustic",
        "spooky": "dark", 
        "halloween": "dark",
        "desert": "mysterious",
        "fantasy": "magical"
    }