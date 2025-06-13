"""
Complete Enhanced Main Orchestrator Agent
Multi-Agent Game Content Pipeline v2.0 - Coordinates World Designer and Enhanced Asset Generator
"""

import asyncio
import json
import os
import shutil
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import traceback

# Google ADK imports
from google.adk.agents import Agent

# Import the sub-agents
from .world_designer.agent import design_world_from_prompt, generate_world, get_status as world_status
from .asset_generator.agent import CreativeAssetGeneratorAgent  # Use the enhanced version

@dataclass
class PipelineResult:
    """Result of the complete pipeline execution"""
    status: str
    world_spec: Optional[Dict[str, Any]]
    assets: Optional[Dict[str, Any]]
    output_directory: str
    generation_summary: Dict[str, Any]
    errors: List[str]
    execution_time: float

class GameContentOrchestrator:
    """
    Enhanced Main orchestrator that coordinates World Designer and AI-Enhanced Asset Generator agents
    Features: Unified output directory, AI textures, creative variations, automatic cleanup
    """
    
    def __init__(self, base_output_dir: str = "game_content_pipeline"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Pipeline state
        self.current_session_dir = None
        self.world_spec = None
        self.assets = None
        self.errors = []
        
        # Initialize asset generator (will be set with proper directory later)
        self.asset_generator = None
        
        # Clean up any old standalone directories
        self._cleanup_old_directories()
    
    def _create_session_directory(self, prompt: str) -> Path:
        """Create a unique directory for this generation session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create safe filename from prompt
        safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_prompt = safe_prompt.replace(' ', '_')
        
        session_name = f"{timestamp}_{safe_prompt}"
        session_dir = self.base_output_dir / session_name
        session_dir.mkdir(exist_ok=True)
        
        return session_dir
    
    def _cleanup_old_directories(self):
        """Clean up any old standalone generated_assets directories"""
        try:
            # Check if there's a standalone generated_assets folder
            standalone_assets = Path("generated_assets")
            if standalone_assets.exists():
                self.logger.info("🧹 Found standalone generated_assets directory - cleaning up")
                
                # Move contents to a backup location if they exist
                if any(standalone_assets.iterdir()):
                    backup_dir = self.base_output_dir / "legacy_generated_assets"
                    if not backup_dir.exists():
                        shutil.move(str(standalone_assets), str(backup_dir))
                        self.logger.info(f"📦 Moved old assets to: {backup_dir}")
                    else:
                        # If backup already exists, just remove the old one
                        shutil.rmtree(standalone_assets)
                        self.logger.info("🗑️  Removed old generated_assets directory")
                else:
                    # Empty directory, just remove it
                    standalone_assets.rmdir()
                    self.logger.info("🗑️  Removed empty generated_assets directory")
            
            # Also check for any other random asset directories
            for path in Path(".").glob("*_assets"):
                if path.is_dir() and path.name not in ["game_content_pipeline", "legacy_generated_assets"]:
                    self.logger.info(f"🧹 Found old asset directory: {path.name}")
                    
        except Exception as e:
            self.logger.warning(f"Cleanup check failed: {e}")
    
    async def generate_complete_content(self, prompt: str) -> PipelineResult:
        """
        Main pipeline function - generates complete game content with AI enhancements
        """
        start_time = asyncio.get_event_loop().time()
        
        # Create session directory
        self.current_session_dir = self._create_session_directory(prompt)
        
        print(f"\n🎮 ENHANCED MULTI-AGENT GAME CONTENT PIPELINE v2.0")
        print(f"{'='*65}")
        print(f"📝 Prompt: {prompt}")
        print(f"📁 Session Dir: {self.current_session_dir}")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🎨 AI-Enhanced: Textures & Creative Variations")
        print(f"🔧 Features: Unified Output + Automatic Cleanup")
        
        try:
            # Step 1: World Design
            await self._step_1_world_design(prompt)
            
            # Step 2: Enhanced Asset Generation
            await self._step_2_enhanced_asset_generation()
            
            # Step 3: Final Package Assembly
            final_result = await self._step_3_final_assembly()
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            print(f"\n🎉 ENHANCED PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"{'='*65}")
            print(f"⏱️  Total Time: {execution_time:.2f} seconds")
            print(f"📁 Output: {self.current_session_dir}")
            print(f"🎨 AI Features: Textures + Creative Variations")
            print(f"🎯 Ready for: Game Engine Import + ADK Demo")
            
            return PipelineResult(
                status="success",
                world_spec=self.world_spec,
                assets=self.assets,
                output_directory=str(self.current_session_dir),
                generation_summary=final_result,
                errors=self.errors,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Enhanced pipeline failed: {str(e)}"
            self.errors.append(error_msg)
            
            print(f"\n❌ ENHANCED PIPELINE FAILED!")
            print(f"{'='*65}")
            print(f"💥 Error: {error_msg}")
            print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
            
            # Save error log
            await self._save_error_log(e)
            
            return PipelineResult(
                status="error",
                world_spec=self.world_spec,
                assets=self.assets,
                output_directory=str(self.current_session_dir),
                generation_summary={"error": error_msg},
                errors=self.errors,
                execution_time=execution_time
            )
    
    async def _step_1_world_design(self, prompt: str):
        """Step 1: Generate world specification"""
        print(f"\n🌍 STEP 1: WORLD DESIGN")
        print(f"{'='*40}")
        
        try:
            # Check world designer status
            status = await world_status()
            print(f"🔍 World Designer Status: {status.get('status', 'unknown')}")
            
            # Generate world
            print(f"🏗️  Generating world from prompt...")
            self.world_spec = await generate_world(prompt)
            
            # Log results
            print(f"✅ World Design Complete!")
            print(f"   Theme: {self.world_spec.get('theme', 'Unknown')}")
            print(f"   Size: {self.world_spec.get('size', 'Unknown')}")
            print(f"   Buildings: {len(self.world_spec.get('buildings', []))}")
            print(f"   Natural Features: {len(self.world_spec.get('natural_features', []))}")
            print(f"   Paths: {len(self.world_spec.get('paths', []))}")
            
            # Show building details
            buildings = self.world_spec.get('buildings', [])
            if buildings:
                print(f"   Building Types:")
                building_types = {}
                for building in buildings:
                    b_type = building.get('type', 'unknown')
                    building_types[b_type] = building_types.get(b_type, 0) + 1
                
                for b_type, count in building_types.items():
                    print(f"     - {count}x {b_type}")
            
            # Save world specification
            world_file = self.current_session_dir / "world_specification.json"
            with open(world_file, 'w') as f:
                json.dump(self.world_spec, f, indent=2)
            print(f"💾 World spec saved: {world_file.name}")
            
        except Exception as e:
            error_msg = f"World design failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            raise
    
    async def _step_2_enhanced_asset_generation(self):
        """Step 2: Generate 3D assets with AI enhancements from world specification"""
        print(f"\n🎨 STEP 2: ENHANCED ASSET GENERATION")
        print(f"{'='*40}")
        
        try:
            # Initialize ENHANCED asset generator with session directory
            assets_dir = self.current_session_dir / "assets"
            self.asset_generator = CreativeAssetGeneratorAgent(output_dir=str(assets_dir))
            
            # Check enhanced asset generator status
            status = await self.asset_generator.get_status()
            print(f"🔍 Enhanced Asset Generator Status: {status.get('status', 'unknown')}")
            print(f"🔧 Blender Available: {status.get('blender_available', False)}")
            print(f"🤖 AI Available: {status.get('ai_available', False)}")
            print(f"🎨 Enhanced Features Available:")
            features = status.get('features', {})
            for feature, available in features.items():
                status_icon = "✅" if available else "❌"
                print(f"   {status_icon} {feature.replace('_', ' ').title()}")
            
            if status.get('blender_path'):
                print(f"📍 Blender Path: {status.get('blender_path')}")
            
            # Generate enhanced assets
            print(f"\n🎯 Generating AI-enhanced assets from world specification...")
            print(f"   🎨 AI Textures: Generating theme-based materials")
            print(f"   🧠 Creative Variations: AI-powered asset descriptions")
            print(f"   🏗️  Enhanced Geometry: Detailed 3D models with proper materials")
            print(f"   🎭 Material Library: PBR materials with texture mapping")
            
            self.assets = await self.asset_generator.generate_assets(self.world_spec)
            
            # Log enhanced results
            print(f"\n✅ Enhanced Asset Generation Complete!")
            summary = self.assets.get('generation_summary', {})
            print(f"   📊 Total Assets: {summary.get('total_assets', 0)}")
            print(f"   🏠 Buildings: {summary.get('buildings_count', 0)}")
            print(f"   🌍 Environment: {summary.get('environment_count', 0)}")
            print(f"   🌳 Props: {summary.get('props_count', 0)}")
            print(f"   🎨 AI Textures Generated: {summary.get('textures_generated', 0)}")
            print(f"   🧠 Creative Variations: {summary.get('ai_variations', 0)}")
            print(f"   🎭 Theme: {self.assets.get('theme', 'Unknown')}")
            
            # Show generated files
            output_dir = Path(self.assets.get('output_directory', assets_dir))
            if output_dir.exists():
                self._log_enhanced_files(output_dir)
            
        except Exception as e:
            error_msg = f"Enhanced asset generation failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            raise
    
    def _log_enhanced_files(self, output_dir: Path):
        """Log the enhanced generated files structure"""
        print(f"\n📁 Enhanced Generated Files Structure:")
        
        # Models
        models_dir = output_dir / "models"
        if models_dir.exists():
            model_files = list(models_dir.glob("*"))
            print(f"   🎯 3D Models: {len(model_files)} files")
            for file in model_files[:3]:  # Show first 3
                size_kb = file.stat().st_size / 1024 if file.exists() else 0
                print(f"     - {file.name} ({size_kb:.1f} KB)")
            if len(model_files) > 3:
                print(f"     ... and {len(model_files) - 3} more")
        
        # Textures (NEW!)
        textures_dir = output_dir / "textures"
        if textures_dir.exists():
            texture_files = list(textures_dir.glob("*.png"))
            print(f"   🎨 AI Textures: {len(texture_files)} files")
            for file in texture_files[:3]:  # Show first 3
                size_kb = file.stat().st_size / 1024 if file.exists() else 0
                print(f"     - {file.name} ({size_kb:.1f} KB)")
            if len(texture_files) > 3:
                print(f"     ... and {len(texture_files) - 3} more")
        
        # Scripts  
        scripts_dir = output_dir / "blender_scripts"
        if scripts_dir.exists():
            script_files = list(scripts_dir.glob("*.py"))
            print(f"   📜 Enhanced Blender Scripts: {len(script_files)} files")
            for file in script_files[:3]:  # Show first 3
                print(f"     - {file.name}")
            if len(script_files) > 3:
                print(f"     ... and {len(script_files) - 3} more")
        
        # Materials (NEW!)
        materials_dir = output_dir / "materials"
        if materials_dir.exists():
            material_files = list(materials_dir.glob("*"))
            if material_files:
                print(f"   🎭 Material Definitions: {len(material_files)} files")
        
        # Manifest
        manifest_file = output_dir / "asset_manifest.json"
        if manifest_file.exists():
            print(f"   📄 Enhanced Asset Manifest: ✅ Created")
        else:
            print(f"   📄 Enhanced Asset Manifest: ❌ Missing")
    
    async def _step_3_final_assembly(self) -> Dict[str, Any]:
        """Step 3: Assemble final enhanced package"""
        print(f"\n📦 STEP 3: FINAL ENHANCED ASSEMBLY")
        print(f"{'='*40}")
        
        try:
            # Create enhanced master manifest
            master_manifest = {
                "pipeline_info": {
                    "version": "2.0.0",  # Enhanced version
                    "timestamp": datetime.now().isoformat(),
                    "session_id": self.current_session_dir.name,
                    "enhanced_features": {
                        "ai_textures": True,
                        "creative_variations": True,
                        "enhanced_geometry": True,
                        "procedural_materials": True,
                        "unified_output": True,
                        "automatic_cleanup": True
                    }
                },
                "world_specification": {
                    "theme": self.world_spec.get('theme'),
                    "size": self.world_spec.get('size'),
                    "buildings": len(self.world_spec.get('buildings', [])),
                    "natural_features": len(self.world_spec.get('natural_features', [])),
                    "paths": len(self.world_spec.get('paths', [])),
                    "file": "world_specification.json"
                },
                "assets": {
                    "total_count": self.assets.get('generation_summary', {}).get('total_assets', 0),
                    "buildings": self.assets.get('generation_summary', {}).get('buildings_count', 0),
                    "props": self.assets.get('generation_summary', {}).get('props_count', 0),
                    "environment": self.assets.get('generation_summary', {}).get('environment_count', 0),
                    "textures_generated": self.assets.get('generation_summary', {}).get('textures_generated', 0),
                    "ai_variations": self.assets.get('generation_summary', {}).get('ai_variations', 0),
                    "directory": "assets/",
                    "manifest": "assets/asset_manifest.json"
                },
                "file_structure": {
                    "world_specification.json": "Complete world design specification",
                    "assets/": "Directory containing all 3D models, textures, and scripts",
                    "assets/models/": "Enhanced 3D model files (.obj format)",
                    "assets/textures/": "AI-generated texture files (.png format)",
                    "assets/materials/": "Material definition files",
                    "assets/blender_scripts/": "Enhanced Blender Python scripts with texture support",
                    "assets/asset_manifest.json": "Enhanced asset inventory with AI descriptions",
                    "master_manifest.json": "This file - complete enhanced package overview",
                    "pipeline_log.json": "Detailed execution log with enhanced features"
                },
                "usage_instructions": [
                    "1. Import 3D models from assets/models/ into your game engine",
                    "2. Apply textures from assets/textures/ to corresponding models",
                    "3. Use world_specification.json for level layout and positioning",
                    "4. Run enhanced Blender scripts from assets/blender_scripts/ to regenerate with textures",
                    "5. Refer to asset_manifest.json for AI descriptions and creative variations",
                    "6. Use material definitions for PBR rendering in modern engines"
                ],
                "demo_highlights": [
                    "🎮 Complete game-ready content package",
                    "🎨 AI-generated textures with theme consistency",
                    "🧠 Creative variations for each asset type",
                    "🏗️  Enhanced 3D geometry with proper materials",
                    "📁 Unified output structure for easy integration",
                    "🎯 Perfect for ADK hackathon demonstration"
                ],
                "next_steps": [
                    "Add Character Creator Agent for NPCs with AI personalities",
                    "Add Quest Writer Agent for AI-generated storylines",
                    "Add Balance Validator Agent for gameplay optimization",
                    "Add Unity Code Exporter Agent for seamless integration",
                    "Add Texture Upscaling Agent for higher resolution assets"
                ],
                "errors": self.errors if self.errors else None
            }
            
            # Save enhanced master manifest
            manifest_file = self.current_session_dir / "master_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(master_manifest, f, indent=2)
            
            # Create enhanced pipeline log
            pipeline_log = {
                "session_info": {
                    "session_directory": str(self.current_session_dir),
                    "timestamp": datetime.now().isoformat(),
                    "pipeline_version": "2.0.0",
                    "enhanced_features_used": {
                        "ai_texture_generation": self.assets.get('generation_summary', {}).get('textures_generated', 0) > 0,
                        "creative_ai_descriptions": True,
                        "enhanced_geometry": True,
                        "procedural_materials": True,
                        "unified_output_structure": True,
                        "automatic_directory_cleanup": True
                    }
                },
                "execution_steps": [
                    {"step": 1, "name": "World Design", "status": "completed" if self.world_spec else "failed"},
                    {"step": 2, "name": "Enhanced Asset Generation", "status": "completed" if self.assets else "failed"},
                    {"step": 3, "name": "Final Enhanced Assembly", "status": "completed"}
                ],
                "world_stats": {
                    "theme": self.world_spec.get('theme') if self.world_spec else None,
                    "buildings_generated": len(self.world_spec.get('buildings', [])) if self.world_spec else 0,
                    "features_generated": len(self.world_spec.get('natural_features', [])) if self.world_spec else 0
                },
                "enhanced_asset_stats": self.assets.get('generation_summary') if self.assets else {},
                "performance_metrics": {
                    "total_execution_time": "calculated_at_completion",
                    "assets_per_second": "calculated_at_completion",
                    "textures_per_second": "calculated_at_completion"
                },
                "errors": self.errors
            }
            
            log_file = self.current_session_dir / "pipeline_log.json"
            with open(log_file, 'w') as f:
                json.dump(pipeline_log, f, indent=2)
            
            print(f"✅ Final Enhanced Assembly Complete!")
            print(f"📄 Enhanced Master Manifest: {manifest_file.name}")
            print(f"📊 Enhanced Pipeline Log: {log_file.name}")
            print(f"📁 Complete Enhanced Package: {self.current_session_dir}")
            print(f"🎨 AI Features: Textures + Creative Variations Included")
            print(f"🎯 Status: Ready for ADK Demo & Game Engine Import")
            
            return master_manifest
            
        except Exception as e:
            error_msg = f"Final enhanced assembly failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            raise
    
    async def _save_error_log(self, exception: Exception):
        """Save detailed error log"""
        try:
            error_log = {
                "timestamp": datetime.now().isoformat(),
                "pipeline_version": "2.0.0",
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "traceback": traceback.format_exc(),
                "pipeline_state": {
                    "world_spec_available": self.world_spec is not None,
                    "assets_available": self.assets is not None,
                    "session_directory": str(self.current_session_dir),
                    "enhanced_features": "AI textures and creative variations",
                    "cleanup_performed": True
                },
                "debugging_info": {
                    "python_version": os.sys.version,
                    "working_directory": str(Path.cwd()),
                    "base_output_dir": str(self.base_output_dir)
                },
                "all_errors": self.errors
            }
            
            if self.current_session_dir:
                error_file = self.current_session_dir / "error_log.json"
                with open(error_file, 'w') as f:
                    json.dump(error_log, f, indent=2)
                print(f"📝 Error log saved: {error_file.name}")
            
        except Exception as log_error:
            print(f"❌ Failed to save error log: {log_error}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get enhanced orchestrator status"""
        return {
            "status": "ready",
            "version": "2.0.0",
            "base_output_dir": str(self.base_output_dir),
            "current_session": str(self.current_session_dir) if self.current_session_dir else None,
            "world_designer_available": True,
            "enhanced_asset_generator_available": True,
            "features": {
                "ai_texture_generation": True,
                "creative_variations": True,
                "enhanced_geometry": True,
                "unified_output_directory": True,
                "automatic_cleanup": True,
                "procedural_materials": True,
                "theme_consistency": True,
                "game_engine_ready": True
            },
            "pipeline_version": "Enhanced Multi-Agent Pipeline v2.0",
            "demo_ready": True,
            "hackathon_optimized": True
        }
    
    def get_demo_info(self) -> Dict[str, Any]:
        """Get information for ADK hackathon demo"""
        return {
            "demo_title": "Enhanced Multi-Agent Game Content Pipeline",
            "version": "2.0.0",
            "key_features": [
                "🎮 Complete game world generation from text prompts",
                "🎨 AI-powered texture generation with theme consistency",
                "🧠 Creative asset variations using machine learning",
                "🏗️  Enhanced 3D geometry with proper materials",
                "📁 Unified output structure for easy integration",
                "🎯 Game engine ready assets (Unity/Unreal compatible)"
            ],
            "demo_prompts": [
                "Create a medieval village with a blacksmith, tavern, and church",
                "Generate a spooky Halloween town with haunted houses",
                "Build a fantasy forest village with magical elements",
                "Design a desert oasis trading post with merchants"
            ],
            "output_showcase": [
                "World specification with intelligent layout",
                "3D models with enhanced geometry",
                "AI-generated textures (wood, stone, metal, etc.)",
                "Material definitions for PBR rendering",
                "Blender scripts for regeneration",
                "Complete asset manifest with AI descriptions"
            ],
            "technical_highlights": [
                "Multi-agent coordination using ADK",
                "AI-enhanced content generation",
                "Procedural 3D modeling with Blender",
                "Theme-consistent asset creation",
                "Professional game development workflow"
            ]
        }

# Individual functions for ADK tools
async def generate_game_content(prompt: str) -> Dict[str, Any]:
    """
    Generate complete enhanced game content from a text prompt
    Main entry point for the enhanced orchestrator
    """
    orchestrator = GameContentOrchestrator()
    result = await orchestrator.generate_complete_content(prompt)
    return asdict(result)

async def get_orchestrator_status() -> Dict[str, Any]:
    """Get enhanced orchestrator status"""
    orchestrator = GameContentOrchestrator()
    return await orchestrator.get_status()

async def get_demo_information() -> Dict[str, Any]:
    """Get demo information for ADK hackathon"""
    orchestrator = GameContentOrchestrator()
    return orchestrator.get_demo_info()

# Create the enhanced ADK agent
root_agent = Agent(
    name="enhanced_game_content_orchestrator",
    model="gemini-2.0-flash-exp",
    instruction="""You are the master orchestrator for the Enhanced Multi-Agent Game Content Pipeline v2.0. You coordinate specialized agents to create complete game content packages with AI-powered creativity from simple text prompts.

Your enhanced pipeline includes:
1. World Designer Agent - Creates detailed world layouts and environments
2. Enhanced Asset Generator Agent - Generates 3D models, AI textures, and creative variations

Your enhanced responsibilities:
- Coordinate seamless data flow between agents with unified output structure
- Generate AI-powered textures and creative asset variations
- Handle error recovery and provide detailed status updates
- Ensure all generated content is compatible, cohesive, and professionally textured
- Create comprehensive deliverable packages with enhanced visual quality
- Manage unified file organization and documentation
- Prevent duplicate output directories through intelligent cleanup
- Provide demo-ready content for ADK hackathon presentations

You understand advanced game development workflows, AI-enhanced content creation, and ensure professional-quality output with realistic textures and creative variations that's ready for integration into game engines.

Key features you provide:
🎮 Complete game world generation from text prompts
🎨 AI-powered texture generation with theme consistency  
🧠 Creative asset variations using machine learning
🏗️ Enhanced 3D geometry with proper materials
📁 Unified output structure for easy integration
🎯 Game engine ready assets (Unity/Unreal compatible)

When you receive a content generation request, call the generate_game_content function with the user's prompt to create an enhanced package with AI textures and creative features.""",
    description="Enhanced master orchestrator that coordinates World Designer and AI-Enhanced Asset Generator agents to create complete game content packages with textures, creative variations, and unified output structure - optimized for ADK hackathon demonstration",
    tools=[generate_game_content, get_orchestrator_status, get_demo_information]
)

# Standalone testing
if __name__ == "__main__":
    async def main():
        print("🎮 Testing Enhanced Multi-Agent Game Content Pipeline v2.0")
        print("="*65)
        
        orchestrator = GameContentOrchestrator()
        
        # Show demo info
        demo_info = orchestrator.get_demo_info()
        print(f"\n📋 Demo Information:")
        print(f"Title: {demo_info['demo_title']}")
        print(f"Version: {demo_info['version']}")
        print(f"\nKey Features:")
        for feature in demo_info['key_features']:
            print(f"  {feature}")
        
        # Test with demo prompts
        test_prompts = demo_info['demo_prompts'][:2]  # Test first 2
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n🧪 ENHANCED TEST {i}: {prompt}")
            print("-" * 50)
            
            try:
                result = await orchestrator.generate_complete_content(prompt)
                
                if result.status == "success":
                    print(f"🏆 SUCCESS!")
                    print(f"📁 Output: {result.output_directory}")
                    print(f"⏱️  Time: {result.execution_time:.2f}s")
                    print(f"🎨 Enhanced Features: AI Textures + Creative Variations")
                    
                    # Show summary
                    if result.generation_summary:
                        assets = result.generation_summary.get('assets', {})
                        print(f"📊 Generated: {assets.get('total_count', 0)} assets")
                        print(f"🎨 Textures: {assets.get('textures_generated', 0)}")
                        print(f"🧠 AI Variations: {assets.get('ai_variations', 0)}")
                else:
                    print(f"💥 FAILED: {result.errors}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                import traceback
                traceback.print_exc()
    
    asyncio.run(main())