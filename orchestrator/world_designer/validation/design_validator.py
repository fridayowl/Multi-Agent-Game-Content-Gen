"""
Design validation and optimization.
"""

from typing import List, Dict
from ..core.world_spec import WorldSpec

def _validate_design(world_spec: WorldSpec) -> WorldSpec:
    """Validate and optimize the world design"""
    
    validation_issues = []
    
    # Check building accessibility
    if not _validate_accessibility(world_spec.buildings, world_spec.paths):
        validation_issues.append("Some buildings may not be accessible")
    
    # Check spawn points
    if not world_spec.spawn_points:
        validation_issues.append("No spawn points defined")
        # Add default spawn
        world_spec.spawn_points = [{"x": 20.0, "y": 20.0, "z": 0.0, "type": "default"}]
    
    # Check minimum buildings
    if len(world_spec.buildings) < 3:
        validation_issues.append("Very few buildings - consider adding more")
    
    # Log validation results
    if validation_issues:
        print(f"⚠️ Validation issues: {validation_issues}")
    else:
        print("✅ World design validation passed")
    
    # Add validation metadata
    world_spec.metadata["validation_issues"] = validation_issues
    world_spec.metadata["validation_passed"] = len(validation_issues) == 0
    
    return world_spec

def _validate_accessibility(buildings: List[Dict], paths: List[Dict]) -> bool:
    """Simple accessibility check"""
    if not buildings:
        return True
    if len(buildings) == 1:
        return True
    if not paths:
        return len(buildings) <= 2
    
    # In real implementation, would do proper graph traversal
    # For now, assume connected if paths exist
    return len(paths) > 0