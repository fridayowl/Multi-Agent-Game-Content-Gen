"""
Utility functions and configuration data.
"""

from .spatial_utils import _distance
from .theme_configs import _get_terrain_weights, get_theme_feature_types, get_theme_defaults

__all__ = [
    "_distance",
    "_get_terrain_weights",
    "get_theme_feature_types", 
    "get_theme_defaults"
]