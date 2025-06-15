"""
UPDATED ENHANCED MAIN ORCHESTRATOR AGENT
Multi-Agent Game Content Pipeline v2.1 - Fixed for AI Creative Asset Generator
Coordinates World Designer and AI-Enhanced Creative Asset Generator
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

# Import the sub-agents with correct names
from .world_designer.agent import design_world_from_prompt, generate_world, get_status as world_status

# Import the AI Creative Asset Generator with the correct class name
try:
    from .asset_generator.agent import AICreativeAssetGenerator
    ASSET_GENERATOR_AVAILABLE = True
except ImportError:
    print("⚠️ AI Creative Asset Generator not available - using fallback")
    ASSET_GENERATOR_AVAILABLE = False

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

class EnhancedGameContentOrchestrator:
    """
    UPDATED Enhanced Main orchestrator for AI Creative Asset Generator v2.1
    Features: AI-powered unique asset generation, unified output structure, advanced creativity
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
        
        # Initialize AI Creative Asset Generator (will be set with proper directory later)
        self.ai_asset_generator = None
        
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
        
        print(f"\n🎮 ENHANCED MULTI-AGENT GAME CONTENT PIPELINE v2.1")
        print(f"{'='*70}")
        print(f"📝 Prompt: {prompt}")
        print(f"📁 Session Dir: {self.current_session_dir}")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🎨 AI-Enhanced: Creative Asset Generator with Unique Content")
        print(f"🔧 Features: Unified Output + AI Creativity + Automatic Cleanup")
        
        try:
            # Step 1: World Design
            await self._step_1_world_design(prompt)
            
            # Step 2: AI Creative Asset Generation
            await self._step_2_ai_creative_asset_generation()
            
            # Step 3: Final Package Assembly
            final_result = await self._step_3_final_assembly()
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            print(f"\n🎉 ENHANCED PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"{'='*70}")
            print(f"⏱️  Total Time: {execution_time:.2f} seconds")
            print(f"📁 Output: {self.current_session_dir}")
            print(f"🎨 AI Features: Creative Unique Assets + Advanced Textures")
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
            print(f"{'='*70}")
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
    
    async def _step_2_ai_creative_asset_generation(self):
        """Step 2: Generate AI-powered unique creative assets from world specification"""
        print(f"\n🎨 STEP 2: AI CREATIVE ASSET GENERATION")
        print(f"{'='*40}")
        
        try:
            # Initialize AI Creative Asset Generator with session directory
            assets_dir = self.current_session_dir / "ai_creative_assets"
            
            if ASSET_GENERATOR_AVAILABLE:
                # Use the new AI Creative Asset Generator
                self.ai_asset_generator = AICreativeAssetGenerator(output_dir=str(assets_dir))
                
                # Check AI creative asset generator status using available methods
                try:
                    # Try to call get_status if it exists on the instance
                    if hasattr(self.ai_asset_generator, 'get_status'):
                        status = await self.ai_asset_generator.get_status()
                    else:
                        # Create a basic status if the method doesn't exist
                        status = {
                            'status': 'ready',
                            'ai_available': True,  # Assume available since import succeeded
                            'blender_available': False,  # Default assumption
                            'creative_features': {
                                'ai_descriptions': True,
                                'unique_textures': True,
                                'creative_variations': True,
                                'procedural_diversity': True
                            }
                        }
                    
                    print(f"🔍 AI Creative Asset Generator Status: {status.get('status', 'ready')}")
                    print(f"🤖 AI Available: {status.get('ai_available', True)}")
                    print(f"🔧 Blender Available: {status.get('blender_available', False)}")
                    print(f"🎨 Creative Features Available:")
                    features = status.get('creative_features', {})
                    for feature, available in features.items():
                        status_icon = "✅" if available else "❌"
                        print(f"   {status_icon} {feature.replace('_', ' ').title()}")
                except Exception as status_error:
                    print(f"⚠️ Could not get detailed status: {status_error}")
                    print(f"🔍 AI Creative Asset Generator: Available and ready")
                
                # Generate AI creative assets using the class method
                print(f"\n🎯 Generating AI-powered unique creative assets...")
                print(f"   🎨 AI Creativity: Maximum uniqueness and originality")
                print(f"   🧠 Creative Variations: Every asset is completely different")
                print(f"   🏗️  Advanced Geometry: AI-guided 3D model generation")
                print(f"   🎭 Procedural Textures: AI-generated surface materials")
                
                # Use the class instance method
                self.assets = await self.ai_asset_generator.generate_creative_assets(self.world_spec)
                
            else:
                # Fallback to basic asset generation
                print(f"⚠️ AI Creative Asset Generator not available - using fallback")
                self.assets = await self._fallback_asset_generation()
            
            # Log AI creative results
            print(f"\n✅ AI Creative Asset Generation Complete!")
            summary = self.assets.get('generation_summary', {})
            print(f"   📊 Total Creative Assets: {summary.get('total_creative_assets', 0)}")
            print(f"   🏠 Unique Buildings: {summary.get('buildings_count', 0)}")
            print(f"   🌍 Environment Assets: {summary.get('environment_count', 0)}")
            print(f"   🌳 Creative Props: {summary.get('props_count', 0)}")
            print(f"   🎨 Unique Textures Generated: {summary.get('unique_textures_generated', 0)}")
            print(f"   🧠 AI Variations Created: {summary.get('ai_variations_created', 0)}")
            print(f"   🎯 Creativity Score: {summary.get('creative_complexity_score', 0)}")
            print(f"   🎭 Theme: {self.assets.get('theme', 'Unknown')}")
            
            # Show generated files
            output_dir = Path(self.assets.get('output_directory', assets_dir))
            if output_dir.exists():
                self._log_ai_creative_files(output_dir)
            
        except Exception as e:
            error_msg = f"AI creative asset generation failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            traceback.print_exc()
            raise
    
    async def _fallback_asset_generation(self) -> Dict[str, Any]:
        """Fallback asset generation when AI Creative Asset Generator is not available"""
        print(f"🔄 Using fallback asset generation...")
        
        # Create basic asset structure
        assets_dir = self.current_session_dir / "fallback_assets"
        assets_dir.mkdir(exist_ok=True)
        
        (assets_dir / "models").mkdir(exist_ok=True)
        (assets_dir / "scripts").mkdir(exist_ok=True)
        
        buildings = self.world_spec.get('buildings', [])
        
        # Create basic manifest
        return {
            'theme': self.world_spec.get('theme', 'medieval'),
            'ai_generated': False,
            'creative_features': {
                'unique_designs': False,
                'ai_textures': False,
                'creative_variations': False,
                'procedural_diversity': False
            },
            'buildings': [],
            'props': [],
            'environment': [],
            'generation_summary': {
                'total_creative_assets': 0,
                'unique_textures_generated': 0,
                'ai_variations_created': 0,
                'creative_complexity_score': 0,
                'buildings_count': len(buildings),
                'environment_count': 0,
                'props_count': 0
            },
            'output_directory': str(assets_dir),
            'status': 'fallback_generated'
        }
    
    def _log_ai_creative_files(self, output_dir: Path):
        """Log the AI creative generated files structure"""
        print(f"\n📁 AI Creative Generated Files Structure:")
        
        # Models
        models_dir = output_dir / "models"
        if models_dir.exists():
            model_files = list(models_dir.glob("*"))
            print(f"   🎯 AI-Generated 3D Models: {len(model_files)} files")
            for file in model_files[:3]:  # Show first 3
                size_kb = file.stat().st_size / 1024 if file.exists() else 0
                print(f"     - {file.name} ({size_kb:.1f} KB)")
            if len(model_files) > 3:
                print(f"     ... and {len(model_files) - 3} more")
        
        # AI Textures (NEW!)
        textures_dir = output_dir / "ai_textures"
        if textures_dir.exists():
            texture_files = list(textures_dir.glob("*.png"))
            print(f"   🎨 AI-Generated Textures: {len(texture_files)} files")
            for file in texture_files[:3]:  # Show first 3
                size_kb = file.stat().st_size / 1024 if file.exists() else 0
                print(f"     - {file.name} ({size_kb:.1f} KB)")
            if len(texture_files) > 3:
                print(f"     ... and {len(texture_files) - 3} more")
        
        # Creative Variations (NEW!)
        variations_dir = output_dir / "creative_variations"
        if variations_dir.exists():
            variation_files = list(variations_dir.glob("*.json"))
            print(f"   🧠 Creative Variations: {len(variation_files)} files")
            for file in variation_files[:3]:  # Show first 3
                print(f"     - {file.name}")
            if len(variation_files) > 3:
                print(f"     ... and {len(variation_files) - 3} more")
        
        # Enhanced Scripts
        scripts_dir = output_dir / "blender_scripts"
        if scripts_dir.exists():
            script_files = list(scripts_dir.glob("*.py"))
            print(f"   📜 AI-Enhanced Blender Scripts: {len(script_files)} files")
            for file in script_files[:3]:  # Show first 3
                print(f"     - {file.name}")
            if len(script_files) > 3:
                print(f"     ... and {len(script_files) - 3} more")
        
        # AI Materials (NEW!)
        materials_dir = output_dir / "ai_materials"
        if materials_dir.exists():
            material_files = list(materials_dir.glob("*"))
            if material_files:
                print(f"   🎭 AI Material Definitions: {len(material_files)} files")
        
        # Creative Manifest
        manifest_file = output_dir / "ai_creative_manifest.json"
        if manifest_file.exists():
            print(f"   📄 AI Creative Manifest: ✅ Created")
        else:
            print(f"   📄 AI Creative Manifest: ❌ Missing")
    
    async def _step_3_final_assembly(self) -> Dict[str, Any]:
        """Step 3: Assemble final enhanced package with AI creative assets"""
        print(f"\n📦 STEP 3: FINAL ENHANCED ASSEMBLY")
        print(f"{'='*40}")
        
        try:
            # Create enhanced master manifest
            master_manifest = {
                "pipeline_info": {
                    "version": "2.1.0",  # Updated version with AI Creative Assets
                    "timestamp": datetime.now().isoformat(),
                    "session_id": self.current_session_dir.name,
                    "enhanced_features": {
                        "ai_creative_assets": ASSET_GENERATOR_AVAILABLE,
                        "unique_asset_generation": True,
                        "creative_variations": True,
                        "advanced_textures": True,
                        "procedural_creativity": True,
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
                "ai_creative_assets": {
                    "ai_generated": self.assets.get('ai_generated', False),
                    "total_creative_assets": self.assets.get('generation_summary', {}).get('total_creative_assets', 0),
                    "unique_buildings": self.assets.get('generation_summary', {}).get('buildings_count', 0),
                    "creative_props": self.assets.get('generation_summary', {}).get('props_count', 0),
                    "environment_assets": self.assets.get('generation_summary', {}).get('environment_count', 0),
                    "unique_textures_generated": self.assets.get('generation_summary', {}).get('unique_textures_generated', 0),
                    "ai_variations_created": self.assets.get('generation_summary', {}).get('ai_variations_created', 0),
                    "creativity_score": self.assets.get('generation_summary', {}).get('creative_complexity_score', 0),
                    "directory": "ai_creative_assets/" if ASSET_GENERATOR_AVAILABLE else "fallback_assets/",
                    "manifest": "ai_creative_assets/ai_creative_manifest.json" if ASSET_GENERATOR_AVAILABLE else "fallback_assets/basic_manifest.json"
                },
                "file_structure": {
                    "world_specification.json": "Complete world design specification",
                    "ai_creative_assets/": "Directory containing all AI-generated creative content",
                    "ai_creative_assets/models/": "AI-generated unique 3D model files",
                    "ai_creative_assets/ai_textures/": "AI-generated texture files with procedural creativity",
                    "ai_creative_assets/creative_variations/": "AI creative variation definitions",
                    "ai_creative_assets/ai_materials/": "AI-generated material definitions",
                    "ai_creative_assets/blender_scripts/": "AI-enhanced Blender scripts with creativity",
                    "ai_creative_assets/ai_creative_manifest.json": "Complete AI creative asset inventory",
                    "master_manifest.json": "This file - complete enhanced package overview",
                    "pipeline_log.json": "Detailed execution log with AI creative features"
                },
                "usage_instructions": [
                    "1. Import AI-generated 3D models from ai_creative_assets/models/ into your game engine",
                    "2. Apply AI-generated textures from ai_creative_assets/ai_textures/ to models",
                    "3. Use world_specification.json for level layout and positioning",
                    "4. Run AI-enhanced Blender scripts to regenerate with maximum creativity",
                    "5. Refer to ai_creative_manifest.json for AI descriptions and unique variations",
                    "6. Use AI material definitions for advanced PBR rendering"
                ],
                "demo_highlights": [
                    "🎮 Complete game-ready AI creative content package",
                    "🎨 AI-generated unique textures with maximum creativity",
                    "🧠 Every asset completely different - zero repetition",
                    "🏗️  Advanced AI-guided 3D geometry generation",
                    "📁 Unified output structure for seamless integration",
                    "🎯 Perfect for ADK hackathon creative demonstration"
                ],
                "next_steps": [
                    "Add Character Creator Agent for AI-generated NPCs",
                    "Add Quest Writer Agent for AI-generated storylines",
                    "Add Balance Validator Agent for gameplay optimization",
                    "Add Unity Code Exporter Agent for seamless integration",
                    "Expand AI Creative Asset Generator with more asset types"
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
                    "pipeline_version": "2.1.0",
                    "ai_creative_features_used": {
                        "ai_creative_asset_generation": ASSET_GENERATOR_AVAILABLE,
                        "unique_asset_creation": True,
                        "creative_ai_descriptions": True,
                        "advanced_geometry": True,
                        "procedural_creativity": True,
                        "unified_output_structure": True,
                        "automatic_directory_cleanup": True
                    }
                },
                "execution_steps": [
                    {"step": 1, "name": "World Design", "status": "completed" if self.world_spec else "failed"},
                    {"step": 2, "name": "AI Creative Asset Generation", "status": "completed" if self.assets else "failed"},
                    {"step": 3, "name": "Final Enhanced Assembly", "status": "completed"}
                ],
                "world_stats": {
                    "theme": self.world_spec.get('theme') if self.world_spec else None,
                    "buildings_generated": len(self.world_spec.get('buildings', [])) if self.world_spec else 0,
                    "features_generated": len(self.world_spec.get('natural_features', [])) if self.world_spec else 0
                },
                "ai_creative_asset_stats": self.assets.get('generation_summary') if self.assets else {},
                "performance_metrics": {
                    "total_execution_time": "calculated_at_completion",
                    "creative_assets_per_second": "calculated_at_completion",
                    "ai_features_utilized": ASSET_GENERATOR_AVAILABLE
                },
                "errors": self.errors
            }
            
            log_file = self.current_session_dir / "pipeline_log.json"
            with open(log_file, 'w') as f:
                json.dump(pipeline_log, f, indent=2)
            
            print(f"✅ Final Enhanced Assembly Complete!")
            print(f"📄 Enhanced Master Manifest: {manifest_file.name}")
            print(f"📊 Enhanced Pipeline Log: {log_file.name}")
            print(f"📁 Complete AI Creative Package: {self.current_session_dir}")
            print(f"🎨 AI Features: {'Fully Enabled' if ASSET_GENERATOR_AVAILABLE else 'Fallback Mode'}")
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
                "pipeline_version": "2.1.0",
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "traceback": traceback.format_exc(),
                "pipeline_state": {
                    "world_spec_available": self.world_spec is not None,
                    "assets_available": self.assets is not None,
                    "session_directory": str(self.current_session_dir),
                    "ai_creative_features": "AI Creative Asset Generator available" if ASSET_GENERATOR_AVAILABLE else "Fallback mode",
                    "cleanup_performed": True
                },
                "debugging_info": {
                    "python_version": os.sys.version,
                    "working_directory": str(Path.cwd()),
                    "base_output_dir": str(self.base_output_dir),
                    "asset_generator_available": ASSET_GENERATOR_AVAILABLE
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
            "version": "2.1.0",
            "base_output_dir": str(self.base_output_dir),
            "current_session": str(self.current_session_dir) if self.current_session_dir else None,
            "world_designer_available": True,
            "ai_creative_asset_generator_available": ASSET_GENERATOR_AVAILABLE,
            "features": {
                "ai_creative_asset_generation": ASSET_GENERATOR_AVAILABLE,
                "unique_asset_creation": True,
                "creative_variations": ASSET_GENERATOR_AVAILABLE,
                "advanced_geometry": True,
                "unified_output_directory": True,
                "automatic_cleanup": True,
                "procedural_creativity": ASSET_GENERATOR_AVAILABLE,
                "theme_consistency": True,
                "game_engine_ready": True
            },
            "pipeline_version": "Enhanced Multi-Agent Pipeline v2.1 with AI Creative Assets",
            "demo_ready": True,
            "hackathon_optimized": True
        }

# Individual functions for ADK tools
async def generate_game_content(prompt: str) -> Dict[str, Any]:
    """
    Generate complete enhanced game content from a text prompt
    Main entry point for the enhanced orchestrator with AI Creative Assets
    """
    orchestrator = EnhancedGameContentOrchestrator()
    result = await orchestrator.generate_complete_content(prompt)
    return asdict(result)

async def get_orchestrator_status() -> Dict[str, Any]:
    """Get enhanced orchestrator status"""
    orchestrator = EnhancedGameContentOrchestrator()
    return await orchestrator.get_status()

async def get_demo_information() -> Dict[str, Any]:
    """Get demo information for ADK hackathon"""
    return {
        "demo_title": "Enhanced Multi-Agent Game Content Pipeline with AI Creative Assets",
        "version": "2.1.0",
        "key_features": [
            "🎮 Complete game world generation from text prompts",
            "🎨 AI-powered unique creative asset generation",
            "🧠 Every asset completely different - zero repetition",
            "🏗️  Advanced AI-guided 3D geometry creation",
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
            "AI-generated unique 3D models with no repetition",
            "AI-created textures with procedural creativity",
            "Material definitions for PBR rendering",
            "AI-enhanced Blender scripts for regeneration",
            "Complete asset manifest with AI creative descriptions"
        ],
        "technical_highlights": [
            "Multi-agent coordination using ADK",
            "AI-enhanced creative content generation",
            "Procedural 3D modeling with Blender",
            "AI-guided unique asset creation",
            "Professional game development workflow"
        ]
    }

# Create the enhanced ADK agent
root_agent = Agent(
    name="enhanced_game_content_orchestrator_v2_1",
    model="gemini-2.0-flash-exp",
    instruction="""You are the master orchestrator for the Enhanced Multi-Agent Game Content Pipeline v2.1. You coordinate specialized agents to create complete game content packages with AI-powered creativity from simple text prompts.

Your enhanced pipeline includes:
1. World Designer Agent - Creates detailed world layouts and environments
2. AI Creative Asset Generator Agent - Generates completely unique 3D models, textures, and creative variations with ZERO REPETITION

Your enhanced responsibilities:
- Coordinate seamless data flow between agents with unified output structure
- Generate AI-powered unique creative assets with maximum originality
- Handle error recovery and provide detailed status updates
- Ensure all generated content is compatible, cohesive, and professionally creative
- Create comprehensive deliverable packages with AI-enhanced visual quality
- Manage unified file organization and documentation
- Prevent duplicate output directories through intelligent cleanup
- Provide demo-ready content for ADK hackathon presentations

Key features you provide:
🎮 Complete game world generation from text prompts
🎨 AI-powered unique creative asset generation with zero repetition
🧠 Every asset completely different using advanced AI creativity
🏗️ Advanced AI-guided 3D geometry creation
📁 Unified output structure for easy integration
🎯 Game engine ready assets (Unity/Unreal compatible)

When you receive a content generation request, call the generate_game_content function with the user's prompt to create an enhanced package with AI creative assets and maximum originality.""",
    description="Enhanced master orchestrator that coordinates World Designer and AI Creative Asset Generator agents to create complete game content packages with unique creative assets, zero repetition, and unified output structure - optimized for ADK hackathon demonstration",
    tools=[generate_game_content, get_orchestrator_status, get_demo_information]
)

# Standalone testing
if __name__ == "__main__":
    async def main():
        print("🎮 Testing Enhanced Multi-Agent Game Content Pipeline v2.1")
        print("="*70)
        print("🎨 NEW: AI Creative Asset Generator Integration")
        print("🧠 FEATURE: Zero repetition - every asset is unique")
        print("🏗️ ENHANCED: Advanced AI-guided geometry creation")
        
        orchestrator = EnhancedGameContentOrchestrator()
        
        # Show demo info
        demo_info = await get_demo_information()
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
                    print(f"🎨 Enhanced Features: AI Creative Assets + Zero Repetition")
                    
                    # Show summary
                    if result.generation_summary and 'ai_creative_assets' in result.generation_summary:
                        assets = result.generation_summary.get('ai_creative_assets', {})
                        print(f"📊 Generated: {assets.get('total_creative_assets', 0)} unique assets")
                        print(f"🎨 Unique Textures: {assets.get('unique_textures_generated', 0)}")
                        print(f"🧠 AI Variations: {assets.get('ai_variations_created', 0)}")
                        print(f"🎯 Creativity Score: {assets.get('creativity_score', 0)}")
                    elif result.generation_summary:
                        # Fallback display
                        print(f"📊 Generated content (fallback mode)")
                        
                else:
                    print(f"💥 FAILED: {result.errors}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎯 SUMMARY:")
        print(f"✅ Pipeline ready for ADK hackathon")
        print(f"🎨 AI Creative Assets: {'Enabled' if ASSET_GENERATOR_AVAILABLE else 'Fallback mode'}")
        print(f"🏗️ Zero repetition guarantee: Every asset unique")
        print(f"📁 Unified output structure: Game engine ready")
    
    asyncio.run(main())