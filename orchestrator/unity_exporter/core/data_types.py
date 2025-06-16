#!/usr/bin/env python3
"""
Unity data types and structures
Defines the core data structures used throughout the Unity export system
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class UnityComponent:
    """Unity component definition"""
    component_type: str
    properties: Dict[str, Any]
    script_path: Optional[str] = None

@dataclass
class UnityGameObject:
    """Unity GameObject definition"""
    name: str
    transform: Dict[str, Any]
    components: List[UnityComponent]
    children: List['UnityGameObject']
    prefab_path: Optional[str] = None

@dataclass
class UnityScene:
    """Unity scene definition"""
    name: str
    game_objects: List[UnityGameObject]
    settings: Dict[str, Any]

@dataclass
class ExportManifest:
    """Complete export package manifest"""
    project_name: str
    unity_version: str
    export_timestamp: str
    content_summary: Dict[str, Any]
    file_structure: Dict[str, str]
    import_instructions: List[str]
    scene_files: List[str]
    script_files: List[str]
    prefab_files: List[str]
    asset_files: List[str]

@dataclass
class ExportResult:
    """Result of Unity export operation"""
    status: str
    project_name: str
    package_path: str
    manifest: ExportManifest
    output_directory: str
    unity_project_path: str
    import_ready: bool
    file_counts: Dict[str, int]
    error: Optional[str] = None