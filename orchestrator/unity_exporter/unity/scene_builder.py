#!/usr/bin/env python3
"""
Unity scene builder
Handles creation of Unity scene files with game objects
"""

from typing import List
from pathlib import Path
import logging

from ..core.data_types import UnityScene, UnityGameObject, UnityComponent

class SceneBuilder:
    """Handles Unity scene creation"""
    
    def __init__(self, scenes_dir: Path, logger: logging.Logger):
        self.scenes_dir = scenes_dir
        self.logger = logger
        self.exported_scenes = []
    
    async def create_main_scene(self, world_objects: List[UnityGameObject], 
                                character_objects: List[UnityGameObject],
                                quest_objects: List[UnityGameObject], 
                                asset_objects: List[UnityGameObject]) -> UnityScene:
        """Create main Unity scene"""
        self.logger.info("🌍 Creating main scene...")
        
        all_objects = []
        
        # Add lighting and camera
        all_objects.extend([
            UnityGameObject(
                name="Main Camera",
                transform={"position": [0, 10, -10], "rotation": [0.3, 0, 0, 1], "scale": [1, 1, 1]},
                components=[
                    UnityComponent("Camera", {"fieldOfView": 60, "nearClipPlane": 0.3, "farClipPlane": 1000}),
                    UnityComponent("PlayerController", {})
                ],
                children=[]
            ),
            UnityGameObject(
                name="Directional Light",
                transform={"position": [0, 10, 0], "rotation": [0.4, -0.3, 0.1, 0.8], "scale": [1, 1, 1]},
                components=[
                    UnityComponent("Light", {"type": "Directional", "color": [1, 0.96, 0.84, 1], "intensity": 1})
                ],
                children=[]
            )
        ])
        
        # Add all generated objects
        all_objects.extend(world_objects)
        all_objects.extend(character_objects) 
        all_objects.extend(quest_objects)
        all_objects.extend(asset_objects)
        
        scene = UnityScene(
            name="GeneratedGameScene",
            game_objects=all_objects,
            settings={
                "ambientMode": "Skybox",
                "ambientIntensity": 1.0,
                "skyboxMaterial": "Default-Skybox"
            }
        )
        
        # Write scene file
        await self._write_scene_file(scene)
        
        self.logger.info(f"   ✅ Main scene created with {len(all_objects)} objects")
        return scene
    
    async def _write_scene_file(self, scene: UnityScene):
        """Write Unity scene file"""
        
        # Create a simplified Unity scene file format
        scene_content = f'''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!29 &1
OcclusionCullingSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_OcclusionBakeSettings:
    smallestOccluder: 5
    smallestHole: 0.25
    backfaceThreshold: 100
  m_SceneGUID: 00000000000000000000000000000000
  m_OcclusionCullingData: {{fileID: 0}}
--- !u!104 &2
RenderSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 9
  m_Fog: 0
  m_FogColor: {{r: 0.5, g: 0.5, b: 0.5, a: 1}}
  m_FogMode: 3
  m_FogDensity: 0.01
  m_LinearFogStart: 0
  m_LinearFogEnd: 300
  m_AmbientMode: {scene.settings.get('ambientMode', 0)}
  m_AmbientIntensity: {scene.settings.get('ambientIntensity', 1.0)}
  m_AmbientGroundColor: {{r: 0.047, g: 0.043, b: 0.035, a: 1}}
  m_AmbientEquatorColor: {{r: 0.114, g: 0.125, b: 0.133, a: 1}}
  m_AmbientSkyColor: {{r: 0.212, g: 0.227, b: 0.259, a: 1}}
--- !u!157 &3
LightmapSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 12
  m_GIWorkflowMode: 1
--- !u!196 &4
NavMeshSettings:
  serializedVersion: 2
  m_ObjectHideFlags: 0
  m_BuildSettings:
    serializedVersion: 2
    agentTypeID: 0
    agentRadius: 0.5
    agentHeight: 2
    agentSlope: 45
    agentClimb: 0.4
    ledgeDropHeight: 0
    maxJumpAcrossDistance: 0
    minRegionArea: 2
    manualCellSize: 0
    cellSize: 0.16666667
    manualTileSize: 0
    tileSize: 256
    accuratePlacement: 0
    debug:
      m_Flags: 0
  m_NavMeshData: {{fileID: 0}}
'''
        
        scene_path = self.scenes_dir / f"{scene.name}.unity"
        with open(scene_path, 'w') as f:
            f.write(scene_content)
        
        self.exported_scenes.append(f"Scenes/{scene.name}.unity")
        self.logger.info(f"   ✅ Scene file created: {scene.name}.unity")
    
    def get_exported_scenes(self) -> List[str]:
        """Get list of exported scene files"""
        return self.exported_scenes.copy()