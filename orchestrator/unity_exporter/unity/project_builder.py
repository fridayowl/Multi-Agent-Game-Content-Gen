#!/usr/bin/env python3
"""
Unity project builder
Handles creation of Unity project structure and settings
"""

from typing import Dict, Any
from pathlib import Path
import json
import logging
import random
import string

class ProjectBuilder:
    """Handles Unity project structure creation"""
    
    def __init__(self, output_dir: Path, logger: logging.Logger):
        self.output_dir = output_dir
        self.logger = logger
        
        # Unity project structure
        self.unity_project_dir = output_dir / "UnityProject"
        self.assets_dir = self.unity_project_dir / "Assets"
        self.scripts_dir = self.assets_dir / "Scripts"
        self.prefabs_dir = self.assets_dir / "Prefabs"
        self.scenes_dir = self.assets_dir / "Scenes"
        self.models_dir = self.assets_dir / "Models"
        self.textures_dir = self.assets_dir / "Textures"
        self.materials_dir = self.assets_dir / "Materials"
    
    async def create_project_structure(self, project_name: str):
        """Create Unity project structure"""
        self.logger.info("📁 Creating Unity project structure...")
        
        # Create directory structure
        for directory in [self.assets_dir, self.scripts_dir, self.prefabs_dir, 
                         self.scenes_dir, self.models_dir, self.textures_dir, self.materials_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create ProjectSettings
        project_settings_dir = self.unity_project_dir / "ProjectSettings"
        project_settings_dir.mkdir(exist_ok=True)
        
        # Create basic ProjectSettings files
        await self._create_project_settings_files(project_settings_dir, project_name)
        
        # Create Packages manifest
        packages_dir = self.unity_project_dir / "Packages"
        packages_dir.mkdir(exist_ok=True)
        
        await self._create_packages_manifest(packages_dir)
        
        self.logger.info("   ✅ Project structure created")
    
    async def _create_project_settings_files(self, settings_dir: Path, project_name: str):
        """Create essential Unity project settings files"""
        
        # ProjectSettings.asset
        project_settings = f'''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 23
  productGUID: {self._generate_guid()}
  AndroidProfiler: 0
  AndroidFilterTouchesWhenObscured: 0
  AndroidEnableSustainedPerformanceMode: 0
  defaultScreenOrientation: 4
  targetDevice: 2
  useOnDemandResources: 0
  accelerometerFrequency: 60
  companyName: AI Game Studio
  productName: {project_name}
  defaultCursor: {{fileID: 0}}
  cursorHotspot: {{x: 0, y: 0}}
  m_SplashScreenBackgroundColor: {{r: 0.13725491, g: 0.12156863, b: 0.1254902, a: 1}}
  m_ShowUnitySplashScreen: 1
  m_ShowUnitySplashLogo: 1
  m_SplashScreenOverlayOpacity: 1
  m_SplashScreenAnimation: 1
  m_SplashScreenLogoStyle: 1
  m_SplashScreenDrawMode: 0
  m_SplashScreenBackgroundAnimationZoom: 1
  m_SplashScreenLogoAnimationZoom: 1
  m_SplashScreenBackgroundLandscapeAspect: 1
  m_SplashScreenBackgroundPortraitAspect: 1
'''
        
        settings_file = settings_dir / "ProjectSettings.asset"
        with open(settings_file, 'w') as f:
            f.write(project_settings)
    
    async def _create_packages_manifest(self, packages_dir: Path):
        """Create Unity packages manifest"""
        
        manifest = {
            "dependencies": {
                "com.unity.collab-proxy": "2.0.5",
                "com.unity.feature.development": "1.0.1",
                "com.unity.textmeshpro": "3.0.6",
                "com.unity.timeline": "1.7.5",
                "com.unity.ugui": "1.0.0",
                "com.unity.visualscripting": "1.8.0",
                "com.unity.modules.ai": "1.0.0",
                "com.unity.modules.androidjni": "1.0.0",
                "com.unity.modules.animation": "1.0.0",
                "com.unity.modules.assetbundle": "1.0.0",
                "com.unity.modules.audio": "1.0.0",
                "com.unity.modules.cloth": "1.0.0",
                "com.unity.modules.director": "1.0.0",
                "com.unity.modules.imageconversion": "1.0.0",
                "com.unity.modules.imgui": "1.0.0",
                "com.unity.modules.jsonserialize": "1.0.0",
                "com.unity.modules.particlesystem": "1.0.0",
                "com.unity.modules.physics": "1.0.0",
                "com.unity.modules.physics2d": "1.0.0",
                "com.unity.modules.screencapture": "1.0.0",
                "com.unity.modules.terrain": "1.0.0",
                "com.unity.modules.terrainphysics": "1.0.0",
                "com.unity.modules.tilemap": "1.0.0",
                "com.unity.modules.ui": "1.0.0",
                "com.unity.modules.uielements": "1.0.0",
                "com.unity.modules.umbra": "1.0.0",
                "com.unity.modules.unityanalytics": "1.0.0",
                "com.unity.modules.unitywebrequest": "1.0.0",
                "com.unity.modules.unitywebrequestassetbundle": "1.0.0",
                "com.unity.modules.unitywebrequestaudio": "1.0.0",
                "com.unity.modules.unitywebrequesttexture": "1.0.0",
                "com.unity.modules.unitywebrequestwww": "1.0.0",
                "com.unity.modules.vehicles": "1.0.0",
                "com.unity.modules.video": "1.0.0",
                "com.unity.modules.vr": "1.0.0",
                "com.unity.modules.wind": "1.0.0",
                "com.unity.modules.xr": "1.0.0"
            }
        }
        
        manifest_file = packages_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    def _generate_guid(self) -> str:
        """Generate a Unity-style GUID"""
        # Generate 32 character hex string
        hex_chars = string.hexdigits.lower()[:16]  # 0-9, a-f
        guid = ''.join(random.choice(hex_chars) for _ in range(32))
        return guid
    
    def get_directories(self) -> Dict[str, Path]:
        """Get all project directories"""
        return {
            'unity_project_dir': self.unity_project_dir,
            'assets_dir': self.assets_dir,
            'scripts_dir': self.scripts_dir,
            'prefabs_dir': self.prefabs_dir,
            'scenes_dir': self.scenes_dir,
            'models_dir': self.models_dir,
            'textures_dir': self.textures_dir,
            'materials_dir': self.materials_dir
        }