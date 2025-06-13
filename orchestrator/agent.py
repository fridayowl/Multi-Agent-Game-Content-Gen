"""
Main Orchestrator Agent
Multi-Agent Game Content Pipeline - Coordinates World Designer and Asset Generator
"""

import asyncio
import json
import os
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
from .asset_generator.agent import CreativeAssetGeneratorAgent as AssetGeneratorAgent


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
    Main orchestrator that coordinates World Designer and Asset Generator agents
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
        
        # Initialize asset generator
        self.asset_generator = None
    
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
    
    async def generate_complete_content(self, prompt: str) -> PipelineResult:
        """
        Main pipeline function - generates complete game content
        """
        start_time = asyncio.get_event_loop().time()
        
        # Create session directory
        self.current_session_dir = self._create_session_directory(prompt)
        
        print(f"\n🎮 MULTI-AGENT GAME CONTENT PIPELINE")
        print(f"{'='*60}")
        print(f"📝 Prompt: {prompt}")
        print(f"📁 Session Dir: {self.current_session_dir}")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # Step 1: World Design
            await self._step_1_world_design(prompt)
            
            # Step 2: Asset Generation
            await self._step_2_asset_generation()
            
            # Step 3: Final Package Assembly
            final_result = await self._step_3_final_assembly()
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"{'='*60}")
            print(f"⏱️  Total Time: {execution_time:.2f} seconds")
            print(f"📁 Output: {self.current_session_dir}")
            
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
            error_msg = f"Pipeline failed: {str(e)}"
            self.errors.append(error_msg)
            
            print(f"\n❌ PIPELINE FAILED!")
            print(f"{'='*60}")
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
    
    async def _step_2_asset_generation(self):
        """Step 2: Generate 3D assets from world specification"""
        print(f"\n🏗️  STEP 2: ASSET GENERATION")
        print(f"{'='*40}")
        
        try:
            # Initialize asset generator with session directory
            assets_dir = self.current_session_dir / "assets"
            self.asset_generator = AssetGeneratorAgent(output_dir=str(assets_dir))
            
            # Check asset generator status
            status = await self.asset_generator.get_status()
            print(f"🔍 Asset Generator Status: {status.get('status', 'unknown')}")
            print(f"🔧 Blender Available: {status.get('blender_available', False)}")
            if status.get('blender_path'):
                print(f"📍 Blender Path: {status.get('blender_path')}")
            
            # Generate assets
            print(f"🎯 Generating assets from world specification...")
            self.assets = await self.asset_generator.generate_assets(self.world_spec)
            
            # Log results
            print(f"✅ Asset Generation Complete!")
            summary = self.assets.get('generation_summary', {})
            print(f"   Total Assets: {summary.get('total_assets', 0)}")
            print(f"   Buildings: {summary.get('buildings_count', 0)}")
            print(f"   Environment: {summary.get('environment_count', 0)}")
            print(f"   Props: {summary.get('props_count', 0)}")
            print(f"   Theme: {self.assets.get('theme', 'Unknown')}")
            
            # Show generated files
            output_dir = Path(self.assets.get('output_directory', assets_dir))
            if output_dir.exists():
                self._log_generated_files(output_dir)
            
        except Exception as e:
            error_msg = f"Asset generation failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            raise
    
    def _log_generated_files(self, output_dir: Path):
        """Log the generated files structure"""
        print(f"📁 Generated Files Structure:")
        
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
        
        # Scripts  
        scripts_dir = output_dir / "blender_scripts"
        if scripts_dir.exists():
            script_files = list(scripts_dir.glob("*.py"))
            print(f"   📜 Blender Scripts: {len(script_files)} files")
            for file in script_files[:3]:  # Show first 3
                print(f"     - {file.name}")
            if len(script_files) > 3:
                print(f"     ... and {len(script_files) - 3} more")
        
        # Manifest
        manifest_file = output_dir / "asset_manifest.json"
        if manifest_file.exists():
            print(f"   📄 Asset Manifest: ✅ Created")
        else:
            print(f"   📄 Asset Manifest: ❌ Missing")
    
    async def _step_3_final_assembly(self) -> Dict[str, Any]:
        """Step 3: Assemble final package"""
        print(f"\n📦 STEP 3: FINAL ASSEMBLY")
        print(f"{'='*40}")
        
        try:
            # Create master manifest
            master_manifest = {
                "pipeline_info": {
                    "version": "1.0.0",
                    "timestamp": datetime.now().isoformat(),
                    "session_id": self.current_session_dir.name
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
                    "directory": "assets/",
                    "manifest": "assets/asset_manifest.json"
                },
                "file_structure": {
                    "world_specification.json": "Complete world design specification",
                    "assets/": "Directory containing all 3D models and scripts",
                    "assets/models/": "3D model files (.obj format)",
                    "assets/blender_scripts/": "Blender Python scripts for regeneration",
                    "assets/asset_manifest.json": "Asset inventory and metadata",
                    "master_manifest.json": "This file - complete package overview",
                    "pipeline_log.json": "Detailed execution log"
                },
                "usage_instructions": [
                    "1. Import 3D models from assets/models/ into your game engine",
                    "2. Use world_specification.json for level layout and positioning",
                    "3. Run Blender scripts from assets/blender_scripts/ to regenerate models",
                    "4. Refer to asset_manifest.json for detailed asset information"
                ],
                "next_steps": [
                    "Add Character Creator Agent for NPCs",
                    "Add Quest Writer Agent for storylines",
                    "Add Balance Validator Agent for gameplay",
                    "Add Code Exporter Agent for Unity integration"
                ],
                "errors": self.errors if self.errors else None
            }
            
            # Save master manifest
            manifest_file = self.current_session_dir / "master_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(master_manifest, f, indent=2)
            
            # Create pipeline log
            pipeline_log = {
                "session_info": {
                    "session_directory": str(self.current_session_dir),
                    "timestamp": datetime.now().isoformat(),
                    "pipeline_version": "1.0.0"
                },
                "execution_steps": [
                    {"step": 1, "name": "World Design", "status": "completed" if self.world_spec else "failed"},
                    {"step": 2, "name": "Asset Generation", "status": "completed" if self.assets else "failed"},
                    {"step": 3, "name": "Final Assembly", "status": "completed"}
                ],
                "world_stats": {
                    "theme": self.world_spec.get('theme') if self.world_spec else None,
                    "buildings_generated": len(self.world_spec.get('buildings', [])) if self.world_spec else 0,
                    "features_generated": len(self.world_spec.get('natural_features', [])) if self.world_spec else 0
                },
                "asset_stats": self.assets.get('generation_summary') if self.assets else {},
                "errors": self.errors
            }
            
            log_file = self.current_session_dir / "pipeline_log.json"
            with open(log_file, 'w') as f:
                json.dump(pipeline_log, f, indent=2)
            
            print(f"✅ Final Assembly Complete!")
            print(f"📄 Master manifest: {manifest_file.name}")
            print(f"📊 Pipeline log: {log_file.name}")
            print(f"📁 Complete package: {self.current_session_dir}")
            
            return master_manifest
            
        except Exception as e:
            error_msg = f"Final assembly failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            raise
    
    async def _save_error_log(self, exception: Exception):
        """Save detailed error log"""
        try:
            error_log = {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "traceback": traceback.format_exc(),
                "pipeline_state": {
                    "world_spec_available": self.world_spec is not None,
                    "assets_available": self.assets is not None,
                    "session_directory": str(self.current_session_dir)
                },
                "all_errors": self.errors
            }
            
            error_file = self.current_session_dir / "error_log.json"
            with open(error_file, 'w') as f:
                json.dump(error_log, f, indent=2)
            
            print(f"📝 Error log saved: {error_file.name}")
            
        except Exception as log_error:
            print(f"❌ Failed to save error log: {log_error}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "status": "ready",
            "base_output_dir": str(self.base_output_dir),
            "current_session": str(self.current_session_dir) if self.current_session_dir else None,
            "world_designer_available": True,
            "asset_generator_available": True,
            "pipeline_version": "1.0.0"
        }

# Individual functions for ADK tools
async def generate_game_content(prompt: str) -> Dict[str, Any]:
    """
    Generate complete game content from a text prompt
    Main entry point for the orchestrator
    """
    orchestrator = GameContentOrchestrator()
    result = await orchestrator.generate_complete_content(prompt)
    return asdict(result)

async def get_orchestrator_status() -> Dict[str, Any]:
    """Get orchestrator status"""
    orchestrator = GameContentOrchestrator()
    return await orchestrator.get_status()

# Create the main ADK agent
root_agent = Agent(
    name="game_content_orchestrator",
    model="gemini-2.0-flash-exp",
    instruction="""You are the master orchestrator for the Multi-Agent Game Content Pipeline. You coordinate specialized agents to create complete game content packages from simple text prompts.

Your pipeline includes:
1. World Designer Agent - Creates detailed world layouts and environments
2. Asset Generator Agent - Generates 3D models and visual assets

Your responsibilities:
- Coordinate seamless data flow between agents
- Handle error recovery and provide detailed status updates
- Ensure all generated content is compatible and cohesive
- Create comprehensive deliverable packages
- Manage file organization and documentation

You understand game development workflows and ensure professional-quality output that's ready for integration into game engines.

When you receive a content generation request, call the generate_game_content function with the user's prompt.""",
    description="Master orchestrator that coordinates World Designer and Asset Generator agents to create complete game content packages",
    tools=[generate_game_content, get_orchestrator_status]
)

# Standalone testing
if __name__ == "__main__":
    async def main():
        print("🎮 Testing Main Orchestrator Agent")
        print("="*50)
        
        orchestrator = GameContentOrchestrator()
        
        test_prompts = [
            "Create a medieval village with a blacksmith, tavern, and church",
            "Generate a spooky Halloween town with haunted houses"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n🧪 TEST {i}: {prompt}")
            print("-" * 50)
            
            try:
                result = await orchestrator.generate_complete_content(prompt)
                
                if result.status == "success":
                    print(f"🏆 SUCCESS!")
                    print(f"📁 Output: {result.output_directory}")
                    print(f"⏱️  Time: {result.execution_time:.2f}s")
                else:
                    print(f"💥 FAILED: {result.errors}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
    
    asyncio.run(main())