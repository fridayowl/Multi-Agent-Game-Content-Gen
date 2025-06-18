"""
Core data types and enums for the world designer system.
"""

from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

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