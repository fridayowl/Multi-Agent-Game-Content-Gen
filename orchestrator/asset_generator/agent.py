"""
MODULAR AI CREATIVE ASSET GENERATOR - MAIN AGENT
This is the main entry point that coordinates all asset generation modules
Follows the same modular pattern as the world designer
"""

import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Google ADK imports
from google.adk.agents import Agent

# Import all modular components
from .ai_core import AICore
from .prop_generator import PropGenerator
from .building_generator import BuildingGenerator
from .texture_generator import TextureGenerator
from .environment_generator import EnvironmentGenerator
from .material_library import MaterialLibrary
from .blender_integration import BlenderIntegration

class AICreativeAssetGenerator:
    """
    MODULAR AI-POWERED CREATIVE ASSET GENERATOR
    Main coordinator class that orchestrates all asset generation modules
    - Uses AI to generate unique 3D model descriptions
    - Creates diverse textures based on AI descriptions
    - Generates creative variations for each asset
    - No two assets are the same!
    - MODULAR: Split into focused, reusable components
    """
    
    def __init__(self, output_dir: str = "generated_assets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Initialize all modules
        self.ai_core = AICore()
        self.prop_generator = PropGenerator(self.output_dir, self.ai_core)
        self.building_generator = BuildingGenerator(self.output_dir, self.ai_core)
        self.texture_generator = TextureGenerator(self.output_dir, self.ai_core)
        self.environment_generator = EnvironmentGenerator(self.output_dir, self.ai_core)
        self.material_library = MaterialLibrary(self.output_dir, self.ai_core)
        self.blender_integration = BlenderIntegration(self.output_dir)
        
        # Shared state
        self.creative_cache = {}
        self.texture_cache = {}
        self.model_variations = {}
        
        logging.basicConfig(level=logging.INFO)
        
    async def generate_creative_assets(self, world_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        MAIN CREATIVE GENERATION FUNCTION
        Creates unique, AI-designed assets for every building/prop
        """
        self.logger.info("🎨 Starting MODULAR AI Creative Asset Generation")
        
        theme = world_spec.get('theme', 'medieval')
        buildings = world_spec.get('buildings', [])
        natural_features = world_spec.get('natural_features', [])
        
        # Generate AI-creative buildings using building module
        creative_buildings = await self.building_generator.generate_ai_creative_buildings(
            buildings, theme
        )
        
        # Generate AI-creative props using prop module
        creative_props = await self.prop_generator.generate_ai_creative_props(
            natural_features, theme
        )
        
        # Generate AI-creative environment using environment module
        creative_environment = await self.environment_generator.generate_ai_creative_environment(
            world_spec, theme
        )
        
        # Create AI material library using material module
        ai_materials = await self.material_library.generate_ai_material_library(theme)
        
        # Compile creative manifest
        creative_manifest = {
            'theme': theme,
            'ai_generated': True,
            'creative_features': {
                'unique_designs': True,
                'ai_textures': True,
                'creative_variations': True,
                'procedural_diversity': True
            },
            'buildings': creative_buildings,
            'props': creative_props,
            'environment': creative_environment,
            'ai_materials': ai_materials,
            'generation_summary': {
                'total_creative_assets': len(creative_buildings) + len(creative_props) + len(creative_environment),
                'unique_textures_generated': len(self.texture_generator.texture_cache),
                'ai_variations_created': sum(len(b.get('creative_variations', [])) for b in creative_buildings),
                'creative_complexity_score': self._calculate_creativity_score(),
                'buildings_count': len(creative_buildings),
                'props_count': len(creative_props),
                'environment_count': len(creative_environment)
            },
            'output_directory': str(self.output_dir)
        }
        
        # Save creative manifest
        manifest_path = self.output_dir / "ai_creative_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(creative_manifest, f, indent=2)
        
        self.logger.info(f"🎉 Modular AI Creative Generation Complete! Generated {creative_manifest['generation_summary']['total_creative_assets']} unique assets")
        
        return creative_manifest

    def _calculate_creativity_score(self) -> float:
        """Calculate overall creativity score using module data"""
        texture_score = len(self.texture_generator.texture_cache) * 2
        variation_score = len(self.creative_cache) * 1.5
        material_score = self.material_library.get_material_library_size() * 1
        return texture_score + variation_score + material_score

    async def get_status(self) -> Dict[str, Any]:
        """Get AI Creative Asset Generator status"""
        return {
            'status': 'ready',
            'ai_available': self.ai_core.ai_available,
            'blender_available': self.blender_integration.blender_available,
            'creative_features': {
                'ai_descriptions': self.ai_core.ai_available,
                'unique_textures': True,
                'creative_variations': self.ai_core.ai_available,
                'procedural_diversity': True,
                'ai_materials': self.ai_core.ai_available
            },
            'modules': {
                'ai_core': 'ready',
                'prop_generator': 'ready',
                'building_generator': 'ready',
                'texture_generator': 'ready',
                'environment_generator': 'ready',
                'material_library': 'ready',
                'blender_integration': 'ready'
            },
            'version': 'AI Creative v2.0 - MODULAR',
            'output_directory': str(self.output_dir),
            'texture_cache_size': len(self.texture_generator.texture_cache),
            'creative_cache_size': len(self.creative_cache)
        }

# Enhanced ADK Agent Entry Points
async def generate_creative_assets(world_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Generate AI-creative assets - main entry point"""
    generator = AICreativeAssetGenerator()
    return await generator.generate_creative_assets(world_spec)

async def get_creative_status() -> Dict[str, Any]:
    """Get creative generator status"""
    generator = AICreativeAssetGenerator()
    return await generator.get_status()

# Create enhanced ADK agent
root_agent = Agent(
    name="ai_creative_asset_generator_modular",
    model="gemini-2.0-flash-exp",
    instruction="""You are a MODULAR AI-powered creative asset generator that creates UNIQUE 3D content for game worlds. You never create identical assets - every building, prop, and texture is completely unique and creative.

Your REAL AI capabilities:
- Generate unique descriptions for every single asset using AI
- Create diverse textures based on AI-guided parameters  
- Produce creative variations for each asset type
- Generate unique geometric parameters for every model
- Apply theme-consistent but varied styling
- Create realistic material properties

MODULAR ARCHITECTURE:
✨ AI Core - Central AI coordination and API management
🏗️ Building Generator - Specialized building creation
🌳 Prop Generator - Natural features and props
🎨 Texture Generator - AI-guided texture creation
🌍 Environment Generator - Environmental assets
📚 Material Library - Comprehensive material management
🔧 Blender Integration - 3D model generation

You NEVER produce repetitive or identical content. Every asset has:
✨ Unique AI-generated description
🎨 Custom textures created specifically for that asset
🏗️ Varied geometry and proportions
🎭 Creative architectural/design variations
🧠 AI-enhanced material properties

FIXED FEATURES:
- All style parameters properly defined with defaults
- canopy_shape, trunk_style, and other variables always available
- Robust error handling for missing parameters
- Fallback values for all geometry and style parameters

When you receive an asset generation request, you create a completely unique experience every time with genuine AI creativity and procedural diversity.""",
    description="MODULAR AI-powered creative asset generator that produces completely unique 3D models, textures, and variations using real AI creativity - no two assets are ever the same. Built with clean, modular architecture for maximum maintainability.",
    tools=[generate_creative_assets, get_creative_status]
)

# Standalone testing
if __name__ == "__main__":
    async def main():
        print("🎨 Testing MODULAR AI Creative Asset Generator v2.0")
        print("="*60)
        print("🏗️ MODULAR: Split into focused, reusable components")
        print("✅ MODULAR: Clean separation of concerns")
        
        # Test world spec
        test_world = {
            "theme": "medieval",
            "buildings": [
                {"type": "house", "position": {"x": 10, "y": 10, "z": 0}},
                {"type": "tavern", "position": {"x": 20, "y": 15, "z": 0}},
                {"type": "church", "position": {"x": 30, "y": 20, "z": 0}}
            ],
            "natural_features": [
                {"type": "oak_tree", "position": {"x": 5, "y": 5, "z": 0}},
                {"type": "rock", "position": {"x": 25, "y": 8, "z": 0}},
                {"type": "well", "position": {"x": 15, "y": 25, "z": 0}}
            ],
            "terrain_map": [
                ["grass", "grass", "dirt"],
                ["dirt", "grass", "stone"],
                ["grass", "stone", "grass"]
            ],
            "size": (40, 40)
        }
        
        generator = AICreativeAssetGenerator("test_modular_ai_assets")
        
        print("\n🧪 Testing MODULAR AI Creative Generation...")
        result = await generator.generate_creative_assets(test_world)
        
        print(f"\n🎉 MODULAR AI Creative Generation Results:")
        print(f"   🏠 Unique Buildings: {len(result.get('buildings', []))}")
        print(f"   🌳 Unique Props: {len(result.get('props', []))}")
        print(f"   🌍 Environment Assets: {len(result.get('environment', []))}")
        print(f"   🎨 AI Textures Generated: {result['generation_summary']['unique_textures_generated']}")
        print(f"   🧠 Creative Variations: {result['generation_summary']['ai_variations_created']}")
        print(f"   🎯 Creativity Score: {result['generation_summary']['creative_complexity_score']}")
        
        print(f"\n📁 Output Directory: {result['output_directory']}")
        print("✅ Modular architecture implemented!")
        print("🔧 Clean separation of concerns achieved!")
        
    asyncio.run(main())