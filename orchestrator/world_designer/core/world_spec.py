"""
World specification data structures.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

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