"""
Spatial utility functions for distance calculations and positioning.
"""

import math
from typing import Dict

def _distance(pos1: Dict, pos2: Dict) -> float:
    """Calculate distance between positions"""
    dx = pos1["x"] - pos2["x"]
    dy = pos1["y"] - pos2["y"]
    return math.sqrt(dx*dx + dy*dy)