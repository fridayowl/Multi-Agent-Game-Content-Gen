"""
World Designer - Modular game world generation system.
"""

from .main_designer import design_world_from_prompt, generate_world, get_status
from .core.world_spec import WorldSpec
from .core.data_types import TerrainType, WorldPosition
from .analysis import * 
__version__ = "1.0.0"
__all__ = [
    "design_world_from_prompt",
    "generate_world", 
    "get_status",
    "WorldSpec",
    "TerrainType",
    "WorldPosition"
]
