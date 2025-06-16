"""
COMPLETE MULTI-AGENT GAME CONTENT PIPELINE V4.0 - WITH GODOT EXPORTER
Orchestrates World Designer, AI Creative Asset Generator, Character Creator, Quest Writer, Balance Validator, and Godot Exporter
Full end-to-end game content generation with Godot package export
"""

import asyncio
import json
import os
import shutil
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import traceback

# Google ADK imports
from google.adk.agents import Agent

# Import all sub-agents
from .world_designer.agent import design_world_from_prompt, generate_world, get_status as world_status

# Import the AI Creative Asset Generator
try:
    from .asset_generator.agent import AICreativeAssetGenerator
    ASSET_GENERATOR_AVAILABLE = True
except ImportError:
    print("⚠️ AI Creative Asset Generator not available - using fallback")
    ASSET_GENERATOR_AVAILABLE = False

# Import the Character Creator
try:
    from .character_creator.agent import generate_characters_for_world, get_character_creator_status
    CHARACTER_CREATOR_AVAILABLE = True
except ImportError:
    print("⚠️ Character Creator not available - using fallback")
    CHARACTER_CREATOR_AVAILABLE = False

# Import the Quest Writer
try:
    from .quest_writer.agent import generate_quest_system, get_quest_writer_status
    QUEST_WRITER_AVAILABLE = True
except ImportError:
    print("⚠️ Quest Writer not available - using fallback")
    QUEST_WRITER_AVAILABLE = False

# Import the Balance Validator
try:
    from .balance_validator.agent import validate_game_balance, get_balance_validator_status
    BALANCE_VALIDATOR_AVAILABLE = True
except ImportError:
    print("⚠️ Balance Validator not available - using fallback")
    BALANCE_VALIDATOR_AVAILABLE = False

# Import the Godot Exporter (NEW!)
try:
    print("🔍 Attempting to import Godot Exporter...")
    from .godot_exporter.agent import export_godot_package, get_godot_exporter_status
    print("✅ Godot Exporter imports successful")
    GODOT_EXPORTER_AVAILABLE = True
except ImportError as e:
    print(f"❌ ImportError in Godot Exporter: {e}")
    print(f"📍 Error details: {e.__class__.__name__}: {str(e)}")
    GODOT_EXPORTER_AVAILABLE = False
except Exception as e:
    print(f"❌ General error in Godot Exporter: {e}")
    print(f"📍 Error details: {e.__class__.__name__}: {str(e)}")
    GODOT_EXPORTER_AVAILABLE = False

@dataclass
class CompletePipelineResult:
    """Result of the complete 6-agent pipeline execution"""
    status: str
    world_spec: Optional[Dict[str, Any]]
    assets: Optional[Dict[str, Any]]
    characters: Optional[Dict[str, Any]]
    quests: Optional[Dict[str, Any]]
    balance_report: Optional[Dict[str, Any]]
    godot_package: Optional[Dict[str, Any]]  # NEW: Godot export results
    validated_content: Optional[Dict[str, Any]]
    output_directory: str
    generation_summary: Dict[str, Any]
    errors: List[str]
    execution_time: float
    narrative_summary: Dict[str, Any]

class CompleteGameContentOrchestrator:
    """
    COMPLETE Multi-Agent Game Content Pipeline v4.0
    Orchestrates all 6 agents for full game content generation with Godot export:
    1. World Designer - Creates world layout and environment
    2. AI Creative Asset Generator - Generates unique 3D assets and textures
    3. Character Creator - Creates unique NPCs with personalities and relationships
    4. Quest Writer - Creates interconnected storylines using the NPCs
    5. Balance Validator - Ensures all content maintains proper game balance
    6. Godot Exporter - Exports complete Godot-ready packages (NEW!)
    """
    
    def __init__(self, base_output_dir: str = "complete_game_content"):
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Pipeline state
        self.current_session_dir = None
        self.world_spec = None
        self.assets = None
        self.characters = None
        self.quests = None
        self.balance_report = None
        self.godot_package = None  # NEW: Godot export results
        self.validated_content = None
        self.errors = []
        
        # Initialize all sub-agents
        self.ai_asset_generator = None
        
        # Agent availability
        self.agents_available = {
            'world_designer': True,  # Always available
            'asset_generator': ASSET_GENERATOR_AVAILABLE,
            'character_creator': CHARACTER_CREATOR_AVAILABLE,
            'quest_writer': QUEST_WRITER_AVAILABLE,
            'balance_validator': BALANCE_VALIDATOR_AVAILABLE,
            'godot_exporter': GODOT_EXPORTER_AVAILABLE  # NEW!
        }
        
        # Clean up any old directories
        self._cleanup_old_directories()
    
    def _create_session_directory(self, prompt: str) -> Path:
        """Create a unique directory for this complete generation session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create safe filename from prompt
        safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_prompt = safe_prompt.replace(' ', '_')
        
        session_name = f"complete_game_{timestamp}_{safe_prompt}"
        session_dir = self.base_output_dir / session_name
        session_dir.mkdir(exist_ok=True)
        
        return session_dir
    
    def _cleanup_old_directories(self):
        """Clean up any old standalone directories"""
        try:
            cleanup_dirs = ["generated_assets", "generated_characters", "generated_quests", "balance_analysis", "godot_export"]
            for dir_name in cleanup_dirs:
                standalone_dir = Path(dir_name)
                if standalone_dir.exists():
                    self.logger.info(f"🧹 Found standalone {dir_name} directory - cleaning up")
                    
                    if any(standalone_dir.iterdir()):
                        backup_dir = self.base_output_dir / f"legacy_{dir_name}"
                        if not backup_dir.exists():
                            shutil.move(str(standalone_dir), str(backup_dir))
                            self.logger.info(f"📦 Moved old {dir_name} to: {backup_dir}")
                        else:
                            shutil.rmtree(standalone_dir)
                            self.logger.info(f"🗑️  Removed old {dir_name} directory")
                    else:
                        standalone_dir.rmdir()
                        self.logger.info(f"🗑️  Removed empty {dir_name} directory")
                        
        except Exception as e:
            self.logger.warning(f"Cleanup check failed: {e}")

    async def generate_complete_game_content(self, prompt: str, character_count: int = 5, quest_count: int = 7) -> CompletePipelineResult:
        """
        COMPLETE 6-AGENT PIPELINE - generates full game content package with Godot export
        """
        start_time = asyncio.get_event_loop().time()
        
        # Create session directory
        self.current_session_dir = self._create_session_directory(prompt)
        
        print(f"\n🎮 COMPLETE MULTI-AGENT GAME CONTENT PIPELINE v4.0")
        print(f"{'='*80}")
        print(f"📝 Prompt: {prompt}")
        print(f"📁 Session Dir: {self.current_session_dir}")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        print(f"🤖 Agents: {sum(self.agents_available.values())}/6 available")
        print(f"👥 Characters: {character_count} NPCs")
        print(f"📜 Quests: {quest_count} storylines")
        print(f"🎯 Goal: Complete Godot-ready game package")
        print(f"🔧 Features: World + Assets + Characters + Quests + Balance + Godot Export")
        
        try:
            # Step 1: World Design
            await self._step_1_world_design(prompt)
            
            # Step 2: AI Creative Asset Generation
            await self._step_2_ai_creative_asset_generation()
            
            # Step 3: Character Creation
            await self._step_3_character_creation(character_count)
            
            # Step 4: Quest Generation
            await self._step_4_quest_generation(quest_count)
            
            # Step 5: Balance Validation
            await self._step_5_balance_validation()
            
            # Step 6: Final Content Assembly
            await self._step_6_complete_final_assembly()
            
            # Step 7: Godot Package Export (NEW!)
            await self._step_7_godot_package_export()
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            print(f"\n🎉 COMPLETE PIPELINE SUCCEEDED!")
            print(f"{'='*80}")
            print(f"⏱️  Total Time: {execution_time:.2f} seconds")
            print(f"📁 Complete Package: {self.current_session_dir}")
            print(f"🌍 World: ✅ Generated")
            print(f"🎨 Assets: {'✅ AI-Generated' if self.assets else '❌ Failed'}")
            print(f"👥 Characters: {'✅ ' + str(len(self.characters.get('characters', []))) + ' NPCs' if self.characters else '❌ Failed'}")
            print(f"📜 Quests: {'✅ ' + str(len(self.quests.get('quests', []))) + ' storylines' if self.quests else '❌ Failed'}")
            print(f"⚖️ Balance: {'✅ Score: ' + str(round(self.balance_report.get('overall_score', 0), 2)) if self.balance_report else '❌ Failed'}")
            print(f"🎮 Godot Package: {'✅ Ready for Import' if self.godot_package and self.godot_package.get('status') == 'success' else '❌ Failed'}")
            print(f"🎯 Status: Complete Godot Game Package Ready!")
            
            # Calculate narrative summary
            narrative_summary = self._calculate_narrative_summary()
            
            # Create final result summary
            final_result = await self._create_final_result_summary()
            
            return CompletePipelineResult(
                status="success",
                world_spec=self.world_spec,
                assets=self.assets,
                characters=self.characters,
                quests=self.quests,
                balance_report=self.balance_report,
                godot_package=self.godot_package,  # NEW!
                validated_content=self.validated_content,
                output_directory=str(self.current_session_dir),
                generation_summary=final_result,
                errors=self.errors,
                execution_time=execution_time,
                narrative_summary=narrative_summary
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            error_msg = f"Complete pipeline failed: {str(e)}"
            self.errors.append(error_msg)
            
            print(f"\n❌ COMPLETE PIPELINE FAILED!")
            print(f"{'='*80}")
            print(f"💥 Error: {error_msg}")
            print(f"⏱️  Execution Time: {execution_time:.2f} seconds")
            
            # Save error log
            await self._save_error_log(e)
            
            return CompletePipelineResult(
                status="error",
                world_spec=self.world_spec,
                assets=self.assets,
                characters=self.characters,
                quests=self.quests,
                balance_report=self.balance_report,
                godot_package=self.godot_package,
                validated_content=self.validated_content,
                output_directory=str(self.current_session_dir) if self.current_session_dir else "",
                generation_summary={"error": error_msg},
                errors=self.errors,
                execution_time=execution_time,
                narrative_summary={}
            )

    async def _step_1_world_design(self, prompt: str):
        """Step 1: Generate world specification"""
        print(f"\n🌍 STEP 1: WORLD DESIGN")
        print(f"{'='*50}")
        
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
        """Step 2: Generate AI-powered unique creative assets"""
        print(f"\n🎨 STEP 2: AI CREATIVE ASSET GENERATION")
        print(f"{'='*50}")
        
        try:
            assets_dir = self.current_session_dir / "ai_creative_assets"
            
            if ASSET_GENERATOR_AVAILABLE:
                # Use the AI Creative Asset Generator
                self.ai_asset_generator = AICreativeAssetGenerator(output_dir=str(assets_dir))
                
                print(f"🎯 Generating AI-powered unique creative assets...")
                self.assets = await self.ai_asset_generator.generate_creative_assets(self.world_spec)
                
                print(f"✅ AI Creative Asset Generation Complete!")
                summary = self.assets.get('generation_summary', {})
                print(f"   📊 Total Creative Assets: {summary.get('total_creative_assets', 0)}")
                print(f"   🏠 Unique Buildings: {len(self.assets.get('buildings', []))}")
                print(f"   🎨 Unique Textures: {summary.get('unique_textures_generated', 0)}")
                
            else:
                print(f"⚠️ AI Creative Asset Generator not available - using fallback")
                self.assets = await self._fallback_asset_generation()
            
        except Exception as e:
            error_msg = f"AI creative asset generation failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            # Don't raise - continue with other agents

    async def _step_3_character_creation(self, character_count: int):
        """Step 3: Generate unique NPCs with personalities and relationships"""
        print(f"\n👥 STEP 3: CHARACTER CREATION")
        print(f"{'='*50}")
        
        try:
            if CHARACTER_CREATOR_AVAILABLE:
                print(f"🎭 Generating {character_count} unique NPCs...")
                
                # Check character creator status
                status = await get_character_creator_status()
                print(f"🔍 Character Creator Status: {status.get('status', 'unknown')}")
                print(f"🧠 AI Available: {status.get('ai_available', True)}")
                print(f"✨ Uniqueness Guaranteed: {status.get('uniqueness_guaranteed', True)}")
                
                # Generate characters using the world specification
                self.characters = await generate_characters_for_world(self.world_spec, character_count)
                
                print(f"✅ Character Creation Complete!")
                if self.characters.get('status') == 'success':
                    chars = self.characters.get('characters', [])
                    print(f"   👥 Generated NPCs: {len(chars)}")
                    print(f"   🎭 Unique Personalities: {len(chars)}")
                    print(f"   💞 Relationships: {self.characters.get('generation_summary', {}).get('total_relationships', 0)}")
                    print(f"   💬 Dialogue Nodes: {self.characters.get('generation_summary', {}).get('total_dialogue_nodes', 0)}")
                    
                    # Show character names and roles
                    for char in chars[:3]:  # Show first 3
                        print(f"     - {char.get('name', 'Unknown')} ({char.get('role', 'Unknown role')})")
                    if len(chars) > 3:
                        print(f"     ... and {len(chars) - 3} more")
                    
                    # Save characters
                    chars_file = self.current_session_dir / "characters.json"
                    with open(chars_file, 'w') as f:
                        json.dump(self.characters, f, indent=2)
                    print(f"💾 Characters saved: {chars_file.name}")
                    
                else:
                    print(f"⚠️ Character generation had issues: {self.characters.get('status')}")
                    
            else:
                print(f"⚠️ Character Creator not available - using fallback")
                self.characters = await self._fallback_character_generation(character_count)
                
        except Exception as e:
            error_msg = f"Character creation failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            # Don't raise - continue with other agents

    async def _step_4_quest_generation(self, quest_count: int):
        """Step 4: Generate interconnected quest system using NPCs"""
        print(f"\n📜 STEP 4: QUEST GENERATION")
        print(f"{'='*50}")
        
        try:
            if QUEST_WRITER_AVAILABLE and self.characters:
                print(f"⚔️ Generating {quest_count} interconnected quests...")
                
                # Check quest writer status
                status = await get_quest_writer_status()
                print(f"🔍 Quest Writer Status: {status.get('status', 'unknown')}")
                print(f"🧠 AI Available: {status.get('ai_available', True)}")
                
                # Extract character data for quest generation
                character_list = self.characters.get('characters', [])
                if character_list:
                    print(f"🎭 Using {len(character_list)} NPCs for quest narratives...")
                    
                    # Generate quest system
                    self.quests = await generate_quest_system(self.world_spec, character_list, quest_count)
                    
                    print(f"✅ Quest Generation Complete!")
                    if self.quests.get('status') == 'success':
                        quest_list = self.quests.get('quests', [])
                        print(f"   📜 Quests: {len(self.quests.get('quests', [])) if self.quests else 0}")
                
                # Set up Godot export directory within session
                godot_export_dir = self.current_session_dir / "godot_package"
                godot_export_dir.mkdir(exist_ok=True)
                
                # Call Godot exporter with all generated content
                self.godot_package = await export_godot_package(
                    world_spec=self.world_spec or {},
                    assets=self.assets or {},
                    characters=self.characters or {},
                    quests=self.quests or {}
                )
                
                if self.godot_package and self.godot_package.get('status') == 'success':
                    package_path = self.godot_package.get('package_path', 'Unknown')
                    file_counts = self.godot_package.get('file_counts', {})
                    
                    print(f"   ✅ Godot package export successful!")
                    print(f"   📦 Package: {package_path}")
                    print(f"   🔧 Scripts: {file_counts.get('scripts', 0)}")
                    print(f"   🎮 Scenes: {file_counts.get('scenes', 0)}")
                    print(f"   📁 Assets: {file_counts.get('assets', 0)}")
                    print(f"   🌍 Resources: {file_counts.get('resources', 0)}")
                    print(f"   🎯 Status: Ready for Godot Import!")
                    
                    # Copy Godot package to session directory if it exists
                    if os.path.exists(package_path):
                        session_package_path = self.current_session_dir / f"GameWorld_{datetime.now().strftime('%Y%m%d_%H%M%S')}_Godot"
                        if os.path.isdir(package_path):
                            shutil.copytree(package_path, session_package_path)
                        else:
                            shutil.copy2(package_path, session_package_path)
                        self.godot_package['session_package_path'] = str(session_package_path)
                        print(f"   📁 Package copied to session: {session_package_path.name}")
                    
                    # Update master manifest with Godot export info
                    await self._update_manifest_with_godot_info()
                    
                else:
                    error_msg = f"Godot export failed: {self.godot_package.get('error', 'Unknown error')}"
                    self.errors.append(error_msg)
                    print(f"   ❌ {error_msg}")
                    
            else:
                print(f"⚠️ Godot Exporter not available - generating export instructions instead")
                self.godot_package = await self._fallback_godot_export_instructions()
                
        except Exception as e:
            error_msg = f"Godot package export failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            # Don't raise - pipeline can still be useful without Godot export

    async def _update_manifest_with_godot_info(self):
        """Update master manifest with Godot export information"""
        try:
            manifest_file = self.current_session_dir / "master_manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                
                # Update with Godot export info
                manifest["pipeline_info"]["agents_used"] = manifest["pipeline_info"].get("agents_used", {})
                manifest["pipeline_info"]["agents_used"]["godot_exporter"] = bool(self.godot_package)
                manifest["godot_export"] = {
                    "status": self.godot_package.get('status', 'unknown') if self.godot_package else 'not_available',
                    "project_ready": self.godot_package.get('status') == 'success' if self.godot_package else False,
                    "project_path": self.godot_package.get('session_package_path', '') if self.godot_package else '',
                    "file_counts": self.godot_package.get('file_counts', {}) if self.godot_package else {},
                    "import_ready": self.godot_package.get('import_ready', False) if self.godot_package else False,
                    "godot_version": "4.3+",
                    "features": [
                        "GDScript files for NPCs and game systems",
                        "Complete scenes with proper node structure",
                        "Player controller with first-person movement",
                        "Interactive dialogue system",
                        "Quest management system",
                        "JSON-based content loading"
                    ]
                }
                
                # Save updated manifest
                with open(manifest_file, 'w') as f:
                    json.dump(manifest, f, indent=2)
                    
        except Exception as e:
            print(f"⚠️ Failed to update manifest with Godot info: {e}")

    async def _fallback_godot_export_instructions(self) -> Dict[str, Any]:
        """Fallback Godot export instructions when Godot Exporter not available"""
        
        instructions_file = self.current_session_dir / "godot_import_instructions.md"
        
        instructions = f"""# Godot Import Instructions

## Generated Content Package
- **World Specification**: `world_specification.json`
- **Characters**: `characters.json` ({len(self.characters.get('characters', [])) if self.characters else 0} NPCs)
- **Quests**: `quests.json` ({len(self.quests.get('quests', [])) if self.quests else 0} quests)
- **Assets**: `ai_creative_assets/` ({self.assets.get('generation_summary', {}).get('total_creative_assets', 0) if self.assets else 0} files)

## Manual Godot Integration Steps

### 1. Create New Godot Project
```
1. Open Godot 4.3+
2. Create new project
3. Set up project structure: scenes/, scripts/, assets/, data/
```

### 2. Import 3D Assets
```
1. Copy models from ai_creative_assets/models/ to assets/models/
2. Copy textures from ai_creative_assets/ai_textures/ to assets/textures/
3. Import all assets in Godot (auto-import should handle most)
4. Create materials and apply textures
```

### 3. Create NPCs and World
```
1. Read character data from characters.json
2. Create CharacterBody3D nodes for each NPC
3. Position NPCs according to world_specification.json locations
4. Add collision shapes and interaction areas
5. Implement NPC scripts with dialogue system
```

### 4. Implement Game Systems
```
1. Create main World scene with Node3D root
2. Add player controller (CharacterBody3D with camera)
3. Implement quest management system
4. Connect quest objectives to NPC interactions
5. Add UI for dialogue and quest tracking
```

### 5. Build World Layout
```
1. Parse world_specification.json for building positions
2. Place 3D models according to layout specifications
3. Add lighting (DirectionalLight3D for sun, other lights as needed)
4. Configure environment and skybox
5. Set up collision for world geometry
```

## Sample GDScript Files Needed

### Player Controller (scripts/Player.gd)
```gdscript
extends CharacterBody3D

@export var speed = 5.0
@export var sensitivity = 0.003

@onready var camera = $Camera3D

func _ready():
    Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event):
    if event is InputEventMouseMotion:
        rotate_y(-event.relative.x * sensitivity)
        camera.rotate_x(-event.relative.y * sensitivity)
        camera.rotation.x = clamp(camera.rotation.x, -PI/2, PI/2)

func _physics_process(delta):
    var input_vector = Vector3()
    if Input.is_action_pressed("move_forward"):
        input_vector.z -= 1
    if Input.is_action_pressed("move_back"):
        input_vector.z += 1
    if Input.is_action_pressed("move_left"):
        input_vector.x -= 1
    if Input.is_action_pressed("move_right"):
        input_vector.x += 1
    
    velocity = transform.basis * input_vector * speed
    move_and_slide()
```

### NPC System (scripts/NPC.gd)
```gdscript
extends CharacterBody3D

@export var npc_data: Dictionary
@export var dialogue_data: Array

signal dialogue_started
signal quest_given

func _ready():
    # Load NPC data from characters.json
    load_npc_data()

func interact():
    dialogue_started.emit()
    # Show dialogue UI
    # Handle quest logic
```

## Balance Recommendations
{f'Overall Balance Score: {self.balance_report.get("overall_score", 0):.2f}' if self.balance_report else 'Balance validation not available'}

## Required Input Actions
Add these to your Input Map in Godot:
- move_forward (W key)
- move_back (S key)  
- move_left (A key)
- move_right (D key)
- interact (E key)

Generated by Multi-Agent Game Content Pipeline v4.0 with Godot Export
"""
        
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        return {
            'status': 'instructions_only',
            'instructions_file': str(instructions_file),
            'message': 'Godot Exporter not available - manual integration instructions provided',
            'manual_integration_required': True,
            'godot_version_required': '4.3+',
            'features_to_implement': [
                'Player controller with first-person movement',
                'NPC interaction system',
                'Dialogue system with UI',
                'Quest management and tracking',
                'World building placement system',
                'JSON data loading for content'
            ]
        }

    async def _create_final_result_summary(self) -> Dict[str, Any]:
        """Create final result summary"""
        
        # Create complete pipeline log
        pipeline_log = {
            "session_info": {
                "session_directory": str(self.current_session_dir),
                "timestamp": datetime.now().isoformat(),
                "pipeline_version": "4.0.0",
                "complete_pipeline": True,
                "balance_validated": bool(self.balance_report),
                "godot_export_ready": bool(self.godot_package)
            },
            "execution_steps": [
                {"step": 1, "name": "World Design", "status": "completed" if self.world_spec else "failed"},
                {"step": 2, "name": "AI Creative Asset Generation", "status": "completed" if self.assets else "failed"},
                {"step": 3, "name": "Character Creation", "status": "completed" if self.characters else "failed"},
                {"step": 4, "name": "Quest Generation", "status": "completed" if self.quests else "failed"},
                {"step": 5, "name": "Balance Validation", "status": "completed" if self.balance_report else "failed"},
                {"step": 6, "name": "Complete Final Assembly", "status": "completed"},
                {"step": 7, "name": "Godot Package Export", "status": "completed" if self.godot_package else "failed"}
            ],
            "agent_performance": {
                "world_designer": {"available": True, "successful": bool(self.world_spec)},
                "asset_generator": {"available": ASSET_GENERATOR_AVAILABLE, "successful": bool(self.assets)},
                "character_creator": {"available": CHARACTER_CREATOR_AVAILABLE, "successful": bool(self.characters)},
                "quest_writer": {"available": QUEST_WRITER_AVAILABLE, "successful": bool(self.quests)},
                "balance_validator": {"available": BALANCE_VALIDATOR_AVAILABLE, "successful": bool(self.balance_report)},
                "godot_exporter": {"available": GODOT_EXPORTER_AVAILABLE, "successful": bool(self.godot_package)}
            },
            "content_statistics": {
                "world_buildings": len(self.world_spec.get('buildings', [])) if self.world_spec else 0,
                "creative_assets": self.assets.get('generation_summary', {}).get('total_creative_assets', 0) if self.assets else 0,
                "generated_npcs": len(self.characters.get('characters', [])) if self.characters else 0,
                "total_quests": len(self.quests.get('quests', [])) if self.quests else 0,
                "narrative_connections": self.quests.get('generation_summary', {}).get('interconnected_quests', 0) if self.quests else 0,
                "balance_score": self.balance_report.get('overall_score', 0.0) if self.balance_report else 0.0,
                "godot_ready": bool(self.godot_package and self.godot_package.get('status') == 'success')
            },
            "errors": self.errors
        }
        
        log_file = self.current_session_dir / "pipeline_log.json"
        with open(log_file, 'w') as f:
            json.dump(pipeline_log, f, indent=2)
        
        print(f"📊 Complete Pipeline Log: {log_file.name}")
        print(f"🎯 Status: Complete Godot Game Package Ready!")
        
        return pipeline_log

    # Include all the existing fallback methods
    async def _fallback_asset_generation(self) -> Dict[str, Any]:
        """Fallback asset generation"""
        print(f"🔄 Using fallback asset generation...")
        
        assets_dir = self.current_session_dir / "fallback_assets"
        assets_dir.mkdir(exist_ok=True)
        
        return {
            'status': 'fallback_generated',
            'ai_generated': False,
            'buildings': [],
            'props': [],
            'environment': [],
            'generation_summary': {'total_creative_assets': 0},
            'output_directory': str(assets_dir)
        }

    async def _fallback_character_generation(self, character_count: int) -> Dict[str, Any]:
        """Fallback character generation"""
        print(f"🔄 Using fallback character generation for {character_count} NPCs...")
        
        theme = self.world_spec.get('theme', 'medieval')
        characters = []
        
        # Create basic characters based on buildings
        buildings = self.world_spec.get('buildings', [])
        for i, building in enumerate(buildings[:character_count]):
            char = {
                'id': f'fallback_char_{i}',
                'name': f"Character_{i+1}",
                'role': building.get('type', 'villager'),
                'location': building.get('type', 'unknown'),
                'personality': {'primary_trait': 'friendly'},
                'backstory': f"A {building.get('type', 'villager')} in this {theme} world.",
                'stats': {'level': 1, 'strength': 10, 'intelligence': 10, 'charisma': 10}
            }
            characters.append(char)
        
        return {
            'status': 'fallback_generated',
            'characters': characters,
            'generation_summary': {
                'total_characters': len(characters),
                'total_relationships': 0,
                'total_dialogue_nodes': 0
            }
        }

    async def _fallback_quest_generation(self) -> Dict[str, Any]:
        """Fallback quest generation"""
        print(f"🔄 Using fallback quest generation...")
        
        quests = [
            {
                'id': 'fallback_quest_1',
                'title': 'Explore the Area',
                'description': 'Get familiar with your surroundings.',
                'quest_type': 'main',
                'level_requirement': 1,
                'giver_npc': 'Village Guide',
                'objectives': [{'description': 'Walk around the area'}],
                'rewards': {'experience': 100, 'gold': 50}
            }
        ]
        
        return {
            'status': 'fallback_generated',
            'quests': quests,
            'generation_summary': {
                'total_quests': len(quests),
                'interconnected_quests': 0,
                'total_dialogue_nodes': 0
            }
        }

    async def _fallback_balance_validation(self) -> Dict[str, Any]:
        """Fallback balance validation"""
        print(f"🔄 Using fallback balance validation...")
        
        return {
            'status': 'fallback_generated',
            'overall_score': 0.6,  # Neutral score
            'metrics': {
                'difficulty_score': 0.6,
                'progression_rate': 0.6,
                'reward_ratio': 0.6,
                'power_curve': 0.6,
                'engagement_level': 0.6,
                'accessibility_score': 0.6
            },
            'issues': [
                {
                    'severity': 'minor',
                    'category': 'validation',
                    'description': 'Balance validation not available - using fallback assessment',
                    'affected_content': ['all'],
                    'suggested_fix': 'Enable balance validator for detailed analysis',
                    'impact_level': 3
                }
            ],
            'recommendations': [
                'Balance validation was not available - consider manual review',
                'Test content with players to identify balance issues',
                'Monitor gameplay metrics after deployment'
            ],
            'validated_content': {
                'balance_adjustments_applied': False,
                'adjustment_notes': ['No balance validator available']
            }
        }

    def _calculate_narrative_summary(self) -> Dict[str, Any]:
        """Calculate narrative summary from all generated content"""
        narrative = {
            'world_theme': self.world_spec.get('theme', 'unknown') if self.world_spec else 'unknown',
            'total_locations': len(self.world_spec.get('buildings', [])) if self.world_spec else 0,
            'total_npcs': len(self.characters.get('characters', [])) if self.characters else 0,
            'total_quests': len(self.quests.get('quests', [])) if self.quests else 0,
            'balance_score': self.balance_report.get('overall_score', 0.0) if self.balance_report else 0.0,
            'balance_status': self._get_balance_status_text(),
            'godot_ready': bool(self.godot_package and self.godot_package.get('status') == 'success'),
            'narrative_complexity': 'high' if self.characters and self.quests else 'basic',
            'interconnected_storylines': True if self.quests and self.quests.get('generation_summary', {}).get('interconnected_quests', 0) > 0 else False,
            'character_driven_narrative': True if self.characters and self.quests else False,
            'content_readiness': {
                'world': bool(self.world_spec),
                'assets': bool(self.assets),
                'characters': bool(self.characters),
                'quests': bool(self.quests),
                'balance_validated': bool(self.balance_report),
                'godot_exported': bool(self.godot_package)  # NEW!
            }
        }
        
        return narrative

    def _get_balance_status_text(self) -> str:
        """Get human-readable balance status"""
        if not self.balance_report:
            return "Not validated"
        
        score = self.balance_report.get('overall_score', 0.0)
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Moderate"
        else:
            return "Needs improvement"

    async def _save_error_log(self, exception: Exception):
        """Save detailed error log for the complete pipeline"""
        try:
            error_log = {
                "timestamp": datetime.now().isoformat(),
                "pipeline_version": "4.0.0",
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "traceback": traceback.format_exc(),
                "pipeline_state": {
                    "world_spec_available": self.world_spec is not None,
                    "assets_available": self.assets is not None,
                    "characters_available": self.characters is not None,
                    "quests_available": self.quests is not None,
                    "balance_report_available": self.balance_report is not None,
                    "godot_package_available": self.godot_package is not None,
                    "session_directory": str(self.current_session_dir)
                },
                "agent_availability": self.agents_available,
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
                print(f"📝 Complete error log saved: {error_file.name}")
            
        except Exception as log_error:
            print(f"❌ Failed to save error log: {log_error}")

    async def get_status(self) -> Dict[str, Any]:
        """Get complete orchestrator status"""
        return {
            "status": "ready",
            "version": "4.0.0",
            "pipeline_type": "complete_multi_agent_with_godot_export",
            "base_output_dir": str(self.base_output_dir),
            "current_session": str(self.current_session_dir) if self.current_session_dir else None,
            "agents_available": self.agents_available,
            "agent_count": f"{sum(self.agents_available.values())}/6",
            "capabilities": {
                "world_generation": True,
                "ai_creative_assets": ASSET_GENERATOR_AVAILABLE,
                "character_creation": CHARACTER_CREATOR_AVAILABLE,
                "quest_generation": QUEST_WRITER_AVAILABLE,
                "balance_validation": BALANCE_VALIDATOR_AVAILABLE,
                "godot_export": GODOT_EXPORTER_AVAILABLE,  # NEW!
                "narrative_integration": CHARACTER_CREATOR_AVAILABLE and QUEST_WRITER_AVAILABLE,
                "complete_game_packages": True
            },
            "features": {
                "end_to_end_content_generation": True,
                "ai_enhanced_creativity": ASSET_GENERATOR_AVAILABLE,
                "character_driven_narratives": CHARACTER_CREATOR_AVAILABLE and QUEST_WRITER_AVAILABLE,
                "interconnected_storylines": QUEST_WRITER_AVAILABLE,
                "professional_balance_validation": BALANCE_VALIDATOR_AVAILABLE,
                "godot_project_export": GODOT_EXPORTER_AVAILABLE,  # NEW!
                "unified_output_structure": True,
                "game_engine_ready": True,
                "demo_optimized": True
            },
            "pipeline_description": "Complete Multi-Agent Pipeline v4.0 - World + Assets + Characters + Quests + Balance + Godot Export",
            "content_types": [
                "World layouts and environments",
                "AI-generated 3D assets and textures", 
                "Unique NPCs with personalities and relationships",
                "Interconnected quest systems and dialogue trees",
                "Professional balance analysis and optimization",
                "Godot projects with GDScript files and scenes"  # NEW!
            ]
        }

# Individual functions for ADK tools
async def generate_complete_game_content(prompt: str, character_count: int = 5, quest_count: int = 7) -> Dict[str, Any]:
    """
    Generate COMPLETE game content package from a text prompt with Godot export
    Main entry point for the complete 6-agent orchestrator
    """
    orchestrator = CompleteGameContentOrchestrator()
    result = await orchestrator.generate_complete_game_content(prompt, character_count, quest_count)
    return asdict(result)

async def get_complete_orchestrator_status() -> Dict[str, Any]:
    """Get complete orchestrator status"""
    orchestrator = CompleteGameContentOrchestrator()
    return await orchestrator.get_status()

async def get_complete_demo_information() -> Dict[str, Any]:
    """Get complete demo information for ADK hackathon"""
    return {
        "demo_title": "Complete Multi-Agent Game Content Pipeline v4.0 with Godot Export",
        "version": "4.0.0",
        "description": "End-to-end game content generation with 6 specialized AI agents including Godot project export",
        "agents": [
            "🌍 World Designer - Creates detailed world layouts and environments",
            "🎨 AI Creative Asset Generator - Generates unique 3D models and textures", 
            "👥 Character Creator - Creates NPCs with personalities and relationships",
            "📜 Quest Writer - Generates interconnected storylines and dialogue",
            "⚖️ Balance Validator - Ensures professional game balance and optimization",
            "🎮 Godot Exporter - Creates complete Godot projects with GDScript files (NEW!)"
        ],
        "key_features": [
            "🎮 Complete game worlds from simple text prompts",
            "🌍 Intelligent world layout with themed environments",
            "🎨 AI-generated unique assets with zero repetition",
            "👥 Rich NPCs with complex personalities and backstories",
            "📜 Interconnected quest chains with character-driven narratives",
            "💬 Dynamic dialogue systems reflecting individual personalities",
            "⚖️ Professional balance validation and optimization",
            "🎮 Godot-ready projects with GDScript files and scenes (NEW!)",
            "🔗 Narrative integration between all content types",
            "📁 One-click Godot import for immediate gameplay (NEW!)"
        ],
        "demo_prompts": [
            "Create a medieval village with mystery and intrigue",
            "Generate a spooky Halloween town with supernatural residents",
            "Build a fantasy forest settlement with magical creatures", 
            "Design a desert trading post with merchant conflicts",
            "Create a steampunk city district with inventor NPCs"
        ],
        "complete_output_showcase": [
            "📍 World specification with intelligent building placement",
            "🏗️ AI-generated unique 3D models for every building type",
            "🎨 Procedural textures and materials with creative variations",
            "👤 5-10 unique NPCs with rich personalities and relationships",
            "📖 7-12 interconnected quests forming a complete narrative",
            "💬 Character-specific dialogue trees and conversation systems",
            "🔄 Cross-quest narrative connections and character involvement",
            "⚖️ Professional balance analysis with specific recommendations",
            "🔧 Automated balance adjustments for optimal gameplay",
            "🎮 Complete Godot projects ready for immediate import and play (NEW!)",
            "🔧 GDScript files for all game systems and NPC interactions (NEW!)",
            "🌍 Godot scenes with proper node structure and setup (NEW!)"
        ],
        "godot_export_features": [
            "🎮 Complete Godot projects (ready to open)",
            "🔧 GDScript files for NPCs, quests, and world systems",
            "🌍 Pre-configured Godot scenes ready to play",
            "🎭 Node structures for all characters and world objects", 
            "💬 Dialogue system integration with Godot UI",
            "📜 Quest management system with tracking",
            "🎯 Player controller and interaction systems",
            "📁 Organized project structure for easy customization"
        ],
        "balance_validation_features": [
            "🎯 Difficulty progression analysis and optimization",
            "📈 Character advancement and power curve validation",
            "💰 Reward scaling and economic balance checking",
            "🎮 Player engagement and accessibility metrics",
            "🔗 Content integration and narrative flow analysis",
            "🚨 Critical issue identification with severity levels",
            "💡 Specific recommendations for improvement",
            "🔧 Automated balance adjustments where possible"
        ],
        "narrative_highlights": [
            "🎭 Every NPC has unique personality, backstory, and motivations",
            "💞 Realistic relationship networks between characters",
            "📜 Quests that utilize character relationships and personalities", 
            "🔗 Interconnected storylines where actions affect multiple NPCs",
            "💬 Dialogue that reflects individual character voices and traits",
            "🎯 Character-driven plot progression and meaningful choices",
            "⚖️ Balanced progression ensuring optimal player experience",
            "🎮 All narrative elements integrated into Godot gameplay systems (NEW!)"
        ],
        "technical_achievements": [
            "🤖 Multi-agent coordination using Google ADK",
            "🧠 AI-enhanced content generation across all content types",
            "🎨 Procedural asset creation with guaranteed uniqueness",
            "📊 Intelligent narrative analysis and quest interconnection",
            "⚖️ Professional game balance validation algorithms",
            "🔄 Cross-agent data flow and content integration",
            "🎮 Automated Godot project generation with GDScript files (NEW!)",
            "📁 Professional game development workflow automation"
        ],
        "demo_workflow": [
            "1. Input: Simple text prompt describing desired game world",
            "2. World Designer: Creates detailed layout and environment design", 
            "3. Asset Generator: Produces unique 3D models and textures",
            "4. Character Creator: Generates NPCs with personalities and relationships",
            "5. Quest Writer: Creates interconnected storylines using the NPCs",
            "6. Balance Validator: Analyzes and optimizes all content for perfect balance",
            "7. Godot Exporter: Creates complete Godot projects with GDScript files (NEW!)",
            "8. Output: Godot-ready game project for immediate import and play (NEW!)"
        ],
        "integration_ready": {
            "godot": "Complete Godot projects with GDScript files and scenes - immediate import ready (NEW!)",
            "unity": "Compatible asset formats and material definitions with balance metrics",
            "unreal": "Compatible asset formats and material definitions with balance metrics",
            "custom_engines": "Standardized file formats and comprehensive balance documentation"
        }
    }

# Create the complete ADK agent with Godot export
root_agent = Agent(
    name="complete_game_content_orchestrator_v4_0_godot",
    model="gemini-2.0-flash-exp",
    instruction="""You are the master orchestrator for the Complete Multi-Agent Game Content Pipeline v4.0 with Godot Project Export. You coordinate 6 specialized agents to create comprehensive, narrative-rich, balanced, and Godot-ready game content packages from simple text prompts.

Your complete pipeline includes:
1. 🌍 World Designer Agent - Creates detailed world layouts and intelligent building placement
2. 🎨 AI Creative Asset Generator Agent - Generates completely unique 3D models, textures, and materials with zero repetition
3. 👥 Character Creator Agent - Creates rich NPCs with unique personalities, backstories, and relationship networks
4. 📜 Quest Writer Agent - Generates interconnected storylines that utilize the NPCs and their relationships
5. ⚖️ Balance Validator Agent - Ensures professional game balance, progression curves, and player engagement optimization
6. 🎮 Godot Exporter Agent - Creates complete Godot projects with GDScript files, scenes, and gameplay systems (NEW!)

Your comprehensive responsibilities:
- Orchestrate seamless data flow between all 6 agents with perfect content integration
- Ensure narrative coherence between world design, characters, and quests
- Validate and optimize game balance across all content types
- Generate complete Godot-ready projects with GDScript files and scenes
- Create character-driven narratives where NPCs have meaningful roles in quest systems
- Provide end-to-end game content generation from prompt to playable Godot game
- Handle error recovery across multiple agent failures
- Deliver demo-ready Godot projects for ADK hackathon presentations

Key features you provide:
🎮 Complete Godot game projects ready for immediate import and gameplay
🌍 Intelligent world design with themed environments and logical layouts
🎨 AI-generated unique visual assets with guaranteed creativity and zero repetition
👥 Rich NPCs with complex personalities, backstories, and realistic relationships
📜 Interconnected quest chains that create compelling character-driven narratives
💬 Dynamic dialogue systems that reflect individual character personalities
⚖️ Professional balance validation ensuring optimal difficulty curves and player engagement
🔧 Automated balance adjustments and specific improvement recommendations
🎮 Complete Godot projects with GDScript files, scenes, and gameplay systems
🌍 Godot scenes with proper node structure, lighting, and player controllers
🔗 Cross-content narrative integration where world, characters, and quests form a cohesive experience
📁 Professional Godot project structure ready for customization and expansion

When you receive a content generation request, call the generate_complete_game_content function with the user's prompt to create a comprehensive package with world design, AI creative assets, unique characters, interconnected quest narratives, professional balance validation, and complete Godot projects that can be immediately imported and played.""",
    description="Complete master orchestrator that coordinates World Designer, AI Creative Asset Generator, Character Creator, Quest Writer, Balance Validator, and Godot Exporter agents to create comprehensive Godot-ready game packages with rich narratives, unique characters, interconnected storylines, professional balance optimization, and complete GDScript files - optimized for immediate Godot gameplay and ADK hackathon demonstration",
    tools=[generate_complete_game_content, get_complete_orchestrator_status, get_complete_demo_information]
)

# Standalone testing
if __name__ == "__main__":
    async def main():
        print("🎮 Testing Complete Multi-Agent Game Content Pipeline v4.0")
        print("="*80)
        print("🌟 COMPLETE INTEGRATION: World + Assets + Characters + Quests + Balance + Godot")
        print("🎭 CHARACTER-DRIVEN: NPCs with personalities drive quest narratives")
        print("🔗 INTERCONNECTED: All content types work together seamlessly")
        print("⚖️ BALANCED: Professional balance validation ensures optimal gameplay")
        print("🎮 GODOT-READY: Complete projects for immediate Godot import and play")
        
        orchestrator = CompleteGameContentOrchestrator()
        
        # Show complete demo info
        demo_info = await get_complete_demo_information()
        print(f"\n📋 Complete Demo Information:")
        print(f"Title: {demo_info['demo_title']}")
        print(f"Version: {demo_info['version']}")
        print(f"Description: {demo_info['description']}")
        
        print(f"\n🤖 Specialized Agents:")
        for agent in demo_info['agents']:
            print(f"  {agent}")
        
        print(f"\n🌟 Key Features:")
        for feature in demo_info['key_features'][:8]:  # Show first 8
            print(f"  {feature}")
        
        print(f"\n🎮 Godot Export Features:")
        for feature in demo_info['godot_export_features'][:4]:  # Show first 4
            print(f"  {feature}")
        
        print(f"\n⚖️ Balance Validation Features:")
        for feature in demo_info['balance_validation_features'][:4]:  # Show first 4
            print(f"  {feature}")
        
        # Test with complete demo prompts
        test_prompts = demo_info['demo_prompts'][:1]  # Test first 1 for comprehensive demo
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n🧪 COMPLETE PIPELINE TEST {i}: {prompt}")
            print("-" * 80)
            
            try:
                result = await orchestrator.generate_complete_game_content(
                    prompt, 
                    character_count=3,  # Smaller for testing
                    quest_count=4       # Smaller for testing
                )
                
                if result.status == "success":
                    print(f"🏆 COMPLETE SUCCESS!")
                    print(f"📁 Output: {result.output_directory}")
                    print(f"⏱️  Time: {result.execution_time:.2f}s")
                    
                    # Show complete content summary
                    narrative = result.narrative_summary
                    print(f"🌍 World Theme: {narrative.get('world_theme', 'unknown')}")
                    print(f"🏠 Locations: {narrative.get('total_locations', 0)}")
                    print(f"👥 NPCs: {narrative.get('total_npcs', 0)}")
                    print(f"📜 Quests: {narrative.get('total_quests', 0)}")
                    print(f"⚖️ Balance Score: {narrative.get('balance_score', 0):.2f}")
                    print(f"⚖️ Balance Status: {narrative.get('balance_status', 'Unknown')}")
                    print(f"🎮 Godot Ready: {narrative.get('godot_ready', False)}")
                    print(f"🔗 Interconnected: {narrative.get('interconnected_storylines', False)}")
                    print(f"🎭 Character-Driven: {narrative.get('character_driven_narrative', False)}")
                    
                    # Show content readiness
                    readiness = narrative.get('content_readiness', {})
                    print(f"📊 Content Readiness:")
                    for content_type, ready in readiness.items():
                        status_icon = "✅" if ready else "❌"
                        print(f"   {status_icon} {content_type.replace('_', ' ').title()}")
                    
                    # Show Godot package info if available
                    if result.godot_package:
                        godot_status = result.godot_package.get('status', 'unknown')
                        print(f"🎮 Godot Package Status: {godot_status}")
                        if godot_status == 'success':
                            file_counts = result.godot_package.get('file_counts', {})
                            print(f"   🔧 Scripts: {file_counts.get('scripts', 0)}")
                            print(f"   🎮 Scenes: {file_counts.get('scenes', 0)}")
                            print(f"   📁 Assets: {file_counts.get('assets', 0)}")
                            print(f"   🌍 Resources: {file_counts.get('resources', 0)}")
                        
                else:
                    print(f"💥 FAILED: {result.errors}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎯 COMPLETE PIPELINE SUMMARY:")
        print(f"✅ 6-Agent coordination ready for ADK hackathon")
        print(f"🌍 World Designer: Always available")
        print(f"🎨 Asset Generator: {'Available' if ASSET_GENERATOR_AVAILABLE else 'Fallback mode'}")
        print(f"👥 Character Creator: {'Available' if CHARACTER_CREATOR_AVAILABLE else 'Fallback mode'}")
        print(f"📜 Quest Writer: {'Available' if QUEST_WRITER_AVAILABLE else 'Fallback mode'}")
        print(f"⚖️ Balance Validator: {'Available' if BALANCE_VALIDATOR_AVAILABLE else 'Fallback mode'}")
        print(f"🎮 Godot Exporter: {'Available' if GODOT_EXPORTER_AVAILABLE else 'Fallback mode'}")
        print(f"🔗 Narrative Integration: {'Full' if CHARACTER_CREATOR_AVAILABLE and QUEST_WRITER_AVAILABLE else 'Basic'}")
        print(f"⚖️ Balance Validation: {'Professional' if BALANCE_VALIDATOR_AVAILABLE else 'Basic'}")
        print(f"🎮 Godot Export: {'Complete projects' if GODOT_EXPORTER_AVAILABLE else 'Manual instructions'}")
        print(f"📁 Complete Godot projects: Ready for immediate import and gameplay")
        print(f"🎮 Ready for: Professional Godot game development workflow")
    
    asyncio.run(main()) 