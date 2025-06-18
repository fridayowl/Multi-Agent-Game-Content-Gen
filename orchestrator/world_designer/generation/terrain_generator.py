"""
Terrain generation functionality.
"""

import math
import random
from typing import List, Tuple, Dict
from ..utils.theme_configs import _get_terrain_weights

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