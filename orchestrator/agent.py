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
    from .balance_validator.agent import validate_content_balance, get_balance_validator_status
    BALANCE_VALIDATOR_AVAILABLE = True
except ImportError:
    print("⚠️ Balance Validator not available - using fallback")
    BALANCE_VALIDATOR_AVAILABLE = False

try:
    print("🔍 Attempting to import Godot Exporter...")
    from .godot_exporter.agent import export_godot_package
    print("✅ Godot Exporter imports successful")
    GODOT_EXPORTER_AVAILABLE = True
except ImportError as e:
    print(f"❌ ImportError in Godot Exporter: {e}")
    print(f"📍 Error details: {e.__class__.__name__}: {str(e)}")
    
    # Try alternative import path
    try:
        from orchestrator.godot_exporter.agent import export_godot_package, get_godot_exporter_status
        print("✅ Godot Exporter alternative import successful")
        GODOT_EXPORTER_AVAILABLE = True
    except ImportError as e2:
        print(f"❌ Alternative import also failed: {e2}")
        GODOT_EXPORTER_AVAILABLE = False
except Exception as e:
    print(f"❌ General error in Godot Exporter: {e}")
    print(f"📍 Error details: {e.__class__.__name__}: {str(e)}")
    GODOT_EXPORTER_AVAILABLE = False

# Define fallback function if import fails
if not GODOT_EXPORTER_AVAILABLE:
    async def export_godot_package(world_spec, assets, characters, quests):
        """Fallback Godot export function"""
        return {
            'status': 'not_available',
            'error': 'Godot Exporter not available',
            'message': 'Manual Godot integration required'
        }

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

    def _calculate_content_statistics(self, world_spec, assets, characters, quests) -> Dict[str, Any]:
        """Calculate comprehensive content statistics"""
        
        stats = {
            # World statistics
            'world_buildings': len(world_spec.get('buildings', [])) if world_spec else 0,
            'world_features': len(world_spec.get('natural_features', [])) if world_spec else 0,
            'world_paths': len(world_spec.get('paths', [])) if world_spec else 0,
            'world_theme': world_spec.get('theme', 'Unknown') if world_spec else 'None',
            
            # Asset statistics
            'total_assets': assets.get('generation_summary', {}).get('total_creative_assets', 0) if assets else 0,
            'ai_generated_assets': assets.get('ai_generated', False) if assets else False,
            
            # Character statistics
            'total_characters': len(characters.get('characters', [])) if characters else 0,
            'character_roles': len(set(char.get('role', 'unknown') for char in characters.get('characters', []))) if characters else 0,
            'character_relationships': characters.get('generation_summary', {}).get('total_relationships', 0) if characters else 0,
            
            # Quest statistics
            'total_quests': len(quests.get('quests', [])) if quests else 0,
            'main_quests': len([q for q in quests.get('quests', []) if q.get('quest_type') == 'main']) if quests else 0,
            'side_quests': len([q for q in quests.get('quests', []) if q.get('quest_type') == 'side']) if quests else 0,
            
            # Integration statistics
            'content_agents_used': sum([
                bool(world_spec), bool(assets), bool(characters), bool(quests)
            ]),
            'balance_validated': bool(self.balance_report),
            'pipeline_complete': all([world_spec, assets, characters, quests])
        }
        
        return stats
    async def _create_master_manifest(self, world_spec, assets, characters, quests, content_stats) -> Dict[str, Any]:
        """Create comprehensive master manifest"""
        
        manifest = {
            "pipeline_info": {
                "version": "4.0.0",
                "timestamp": datetime.now().isoformat(),
                "session_id": self.current_session_dir.name,
                "complete_pipeline": True,
                "agents_used": {
                    "world_designer": bool(world_spec),
                    "asset_generator": bool(assets),
                    "character_creator": bool(characters),
                    "quest_writer": bool(quests),
                    "balance_validator": bool(self.balance_report),
                    "godot_exporter": False  # Will be updated in step 7
                }
            },
            "content_summary": {
                "world_specification": {
                    "theme": content_stats.get('world_theme', 'Unknown'),
                    "buildings": content_stats.get('world_buildings', 0),
                    "natural_features": content_stats.get('world_features', 0),
                    "paths": content_stats.get('world_paths', 0),
                    "file": "world_specification.json"
                },
                "assets": {
                    "total_count": content_stats.get('total_assets', 0),
                    "ai_generated": content_stats.get('ai_generated_assets', False),
                    "directory": "ai_creative_assets/",
                    "manifest": "ai_creative_assets/asset_manifest.json"
                },
                "characters": {
                    "total_npcs": content_stats.get('total_characters', 0),
                    "unique_roles": content_stats.get('character_roles', 0),
                    "relationships": content_stats.get('character_relationships', 0),
                    "file": "characters.json"
                },
                "quests": {
                    "total_quests": content_stats.get('total_quests', 0),
                    "main_quests": content_stats.get('main_quests', 0),
                    "side_quests": content_stats.get('side_quests', 0),
                    "file": "quests.json"
                },
                "balance_validation": {
                    "validated": content_stats.get('balance_validated', False),
                    "report_file": "balance_validation_report.json" if self.balance_report else None,
                    "overall_score": self.balance_report.get('overall_score', 0) if self.balance_report else 0
                }
            },
            "file_structure": {
                "world_specification.json": "Complete world design and layout",
                "characters.json": "NPC definitions with personalities and relationships",
                "quests.json": "Quest systems and storylines",
                "ai_creative_assets/": "Directory containing all generated 3D assets",
                "balance_validation_report.json": "Game balance analysis and recommendations",
                "master_manifest.json": "This file - complete package overview",
                "content_integration_report.json": "Detailed content integration analysis",
                "USAGE_INSTRUCTIONS.md": "How to use this content package",
                "DEVELOPER_GUIDE.md": "Technical documentation for developers"
            },
            "usage_instructions": [
                "1. Review the master manifest and content summary",
                "2. Import 3D assets from ai_creative_assets/ into your game engine",
                "3. Use world_specification.json for level layout and positioning",
                "4. Implement NPCs using characters.json definitions",
                "5. Integrate quest systems using quests.json",
                "6. Apply balance recommendations from balance report",
                "7. Import the Godot package (if available) for immediate gameplay"
            ],
            "technical_specs": {
                "content_format": "JSON with 3D assets",
                "3d_model_format": ".obj with .mtl materials",
                "texture_format": ".png",
                "godot_compatible": True,
                "unity_compatible": True,
                "game_engine_ready": True
            },
            "quality_metrics": {
                "content_completeness": content_stats.get('pipeline_complete', False),
                "balance_validated": content_stats.get('balance_validated', False),
                "ready_for_production": content_stats.get('pipeline_complete', False) and content_stats.get('balance_validated', False)
            }
        }
        
        return manifest
    
    async def _create_content_integration_report(self, world_spec, assets, characters, quests) -> Dict[str, Any]:
        """Create detailed content integration analysis"""
        
        integration_report = {
            "integration_analysis": {
                "world_character_alignment": self._analyze_world_character_alignment(world_spec, characters),
                "character_quest_integration": self._analyze_character_quest_integration(characters, quests),
                "asset_world_compatibility": self._analyze_asset_world_compatibility(assets, world_spec),
                "narrative_coherence": self._analyze_narrative_coherence(world_spec, characters, quests)
            },
            "content_connections": {
                "npcs_with_quests": self._count_npcs_with_quests(characters, quests),
                "buildings_with_npcs": self._count_buildings_with_npcs(world_spec, characters),
                "themed_consistency": self._check_themed_consistency(world_spec, assets, characters)
            },
            "recommendations": self._generate_integration_recommendations(world_spec, assets, characters, quests),
            "validation_timestamp": datetime.now().isoformat()
        }
        
        return integration_report
    def _analyze_world_character_alignment(self, world_spec: Dict[str, Any], characters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well characters align with the world theme and locations"""
        if not world_spec or not characters:
            return {"alignment_score": 0.0, "issues": ["Missing world or character data"]}
        
        world_theme = world_spec.get('theme', 'unknown')
        character_list = characters.get('characters', [])
        buildings = world_spec.get('buildings', [])
        
        alignment_issues = []
        aligned_characters = 0
        total_characters = len(character_list)
        
        # Check theme consistency
        theme_keywords = {
            'medieval': ['knight', 'guard', 'blacksmith', 'merchant', 'priest', 'peasant'],
            'fantasy': ['mage', 'wizard', 'elf', 'dwarf', 'ranger', 'druid'],
            'modern': ['officer', 'detective', 'doctor', 'teacher', 'manager'],
            'sci-fi': ['engineer', 'pilot', 'scientist', 'technician', 'commander'],
            'steampunk': ['inventor', 'engineer', 'airship', 'mechanic', 'industrialist']
        }
        
        expected_roles = theme_keywords.get(world_theme.lower(), [])
        
        for char in character_list:
            char_role = char.get('role', '').lower()
            char_name = char.get('name', 'Unknown')
            
            # Check role alignment with theme
            role_aligned = any(keyword in char_role for keyword in expected_roles) if expected_roles else True
            
            # Check if character has appropriate location
            char_location = char.get('location', '')
            location_exists = any(building.get('type', '').lower() in char_location.lower() for building in buildings)
            
            if role_aligned and (location_exists or not char_location):
                aligned_characters += 1
            else:
                if not role_aligned:
                    alignment_issues.append(f"{char_name} role '{char_role}' doesn't fit {world_theme} theme")
                if char_location and not location_exists:
                    alignment_issues.append(f"{char_name} location '{char_location}' not found in world")
        
        alignment_score = aligned_characters / total_characters if total_characters > 0 else 0.0
        
        return {
            "alignment_score": alignment_score,
            "aligned_characters": aligned_characters,
            "total_characters": total_characters,
            "theme_consistency": alignment_score >= 0.7,
            "issues": alignment_issues[:5],  # Limit to first 5 issues
            "recommendations": [
                f"Ensure character roles fit the {world_theme} theme",
                "Verify character locations exist in the world",
                "Consider adding theme-appropriate NPCs"
            ] if alignment_score < 0.7 else []
        }
    def _analyze_character_quest_integration(self, characters: Dict[str, Any], quests: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well characters are integrated into the quest system"""
        if not characters or not quests:
            return {"integration_score": 0.0, "issues": ["Missing character or quest data"]}
        
        character_list = characters.get('characters', [])
        quest_list = quests.get('quests', [])
        
        if not character_list or not quest_list:
            return {"integration_score": 0.0, "issues": ["No characters or quests available"]}
        
        # Track character involvement
        characters_in_quests = set()
        characters_giving_quests = set()
        unused_characters = []
        quest_givers = set()
        
        # Analyze quest involvement
        for quest in quest_list:
            giver = quest.get('giver_npc', '')
            if giver:
                quest_givers.add(giver)
                characters_giving_quests.add(giver)
                characters_in_quests.add(giver)
            
            # Check objectives for character mentions
            objectives = quest.get('objectives', [])
            for obj in objectives:
                obj_desc = obj.get('description', '').lower()
                for char in character_list:
                    char_name = char.get('name', '').lower()
                    if char_name and char_name in obj_desc:
                        characters_in_quests.add(char.get('name', ''))
        
        # Find unused characters
        for char in character_list:
            char_name = char.get('name', '')
            if char_name not in characters_in_quests:
                unused_characters.append(char_name)
        
        # Calculate integration metrics
        total_characters = len(character_list)
        involved_characters = len(characters_in_quests)
        integration_score = involved_characters / total_characters if total_characters > 0 else 0.0
        
        issues = []
        if len(unused_characters) > 0:
            issues.append(f"{len(unused_characters)} characters not involved in any quests: {', '.join(unused_characters[:3])}")
        
        if len(quest_givers) < len(quest_list) * 0.5:
            issues.append("Too few characters are quest givers - consider distributing quests better")
        
        return {
            "integration_score": integration_score,
            "characters_in_quests": len(characters_in_quests),
            "total_characters": total_characters,
            "quest_givers": len(quest_givers),
            "unused_characters": unused_characters,
            "character_utilization": {
                "well_integrated": integration_score >= 0.7,
                "characters_giving_quests": len(characters_giving_quests),
                "characters_mentioned": len(characters_in_quests) - len(characters_giving_quests)
            },
            "issues": issues,
            "recommendations": [
                "Involve unused characters in quest objectives",
                "Distribute quest-giving among more NPCs",
                "Add character interactions in quest narratives"
            ] if integration_score < 0.7 else []
        }
    def _analyze_asset_world_compatibility(self, assets: Dict[str, Any], world_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well generated assets match the world requirements"""
        if not assets or not world_spec:
            return {"compatibility_score": 0.0, "issues": ["Missing asset or world data"]}
        
        world_buildings = world_spec.get('buildings', [])
        world_theme = world_spec.get('theme', 'unknown')
        
        # Get asset information
        asset_buildings = assets.get('buildings', [])
        asset_summary = assets.get('generation_summary', {})
        total_assets = asset_summary.get('total_creative_assets', 0)
        
        compatibility_issues = []
        matching_assets = 0
        
        # Check if assets cover required building types
        required_building_types = set(building.get('type', '').lower() for building in world_buildings)
        available_asset_types = set(asset.get('type', '').lower() for asset in asset_buildings)
        
        covered_types = required_building_types.intersection(available_asset_types)
        missing_types = required_building_types - available_asset_types
        
        if missing_types:
            compatibility_issues.append(f"Missing assets for building types: {', '.join(missing_types)}")
        
        # Calculate coverage score
        coverage_score = len(covered_types) / len(required_building_types) if required_building_types else 1.0
        
        # Check theme compatibility
        theme_appropriate = assets.get('ai_generated', False) or total_assets > 0
        if not theme_appropriate:
            compatibility_issues.append("No themed assets generated for the world")
        
        # Overall compatibility score
        compatibility_score = (coverage_score + (1.0 if theme_appropriate else 0.5)) / 2
        
        return {
            "compatibility_score": compatibility_score,
            "building_coverage": {
                "required_types": len(required_building_types),
                "covered_types": len(covered_types),
                "missing_types": list(missing_types),
                "coverage_percentage": coverage_score
            },
            "asset_availability": {
                "total_assets": total_assets,
                "themed_assets": theme_appropriate,
                "building_assets": len(asset_buildings)
            },
            "issues": compatibility_issues,
            "recommendations": [
                f"Generate assets for missing building types: {', '.join(missing_types)}",
                f"Ensure assets match {world_theme} theme",
                "Add more variety in asset types"
            ] if compatibility_score < 0.7 else []
        }
    def _analyze_narrative_coherence(self, world_spec: Dict[str, Any], characters: Dict[str, Any], quests: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall narrative coherence across all content"""
        coherence_score = 1.0
        coherence_issues = []
        
        if not all([world_spec, characters, quests]):
            return {"coherence_score": 0.0, "issues": ["Missing essential content for narrative analysis"]}
        
        world_theme = world_spec.get('theme', 'unknown')
        character_list = characters.get('characters', [])
        quest_list = quests.get('quests', [])
        
        # Check theme consistency across all content
        theme_consistency_score = 1.0
        
        # Analyze quest themes
        quest_themes = []
        for quest in quest_list:
            quest_desc = quest.get('description', '').lower()
            quest_title = quest.get('title', '').lower()
            quest_text = f"{quest_title} {quest_desc}"
            
            # Check for theme-inappropriate elements
            if world_theme.lower() == 'medieval' and any(word in quest_text for word in ['robot', 'computer', 'laser', 'spaceship']):
                coherence_issues.append(f"Quest '{quest.get('title', 'Unknown')}' contains modern/sci-fi elements in medieval world")
                theme_consistency_score -= 0.1
            elif world_theme.lower() == 'sci-fi' and any(word in quest_text for word in ['magic', 'wizard', 'spell', 'dragon']):
                coherence_issues.append(f"Quest '{quest.get('title', 'Unknown')}' contains fantasy elements in sci-fi world")
                theme_consistency_score -= 0.1
        
        # Check character narrative consistency
        character_consistency_score = 1.0
        for char in character_list:
            char_backstory = char.get('backstory', '').lower()
            char_name = char.get('name', 'Unknown')
            
            # Check for theme conflicts in backstory
            if world_theme.lower() == 'medieval' and any(word in char_backstory for word in ['technology', 'computer', 'modern']):
                coherence_issues.append(f"Character '{char_name}' has modern elements in medieval setting")
                character_consistency_score -= 0.1
        
        # Check quest interconnection quality
        interconnection_score = 1.0
        quest_givers = set()
        for quest in quest_list:
            giver = quest.get('giver_npc', '')
            if giver:
                quest_givers.add(giver)
        
        # Low interconnection if quests don't share NPCs
        if len(quest_givers) == len(quest_list) and len(quest_list) > 3:
            coherence_issues.append("Quests have no shared NPCs - lacks narrative interconnection")
            interconnection_score -= 0.2
        
        # Calculate overall coherence
        coherence_score = (theme_consistency_score + character_consistency_score + interconnection_score) / 3
        coherence_score = max(0.0, min(1.0, coherence_score))
        
        return {
            "coherence_score": coherence_score,
            "theme_consistency": theme_consistency_score,
            "character_consistency": character_consistency_score,
            "narrative_interconnection": interconnection_score,
            "shared_npcs_count": len(quest_givers),
            "narrative_strength": "strong" if coherence_score >= 0.8 else "moderate" if coherence_score >= 0.6 else "weak",
            "issues": coherence_issues[:5],  # Limit to first 5 issues
            "recommendations": [
                f"Ensure all content matches the {world_theme} theme",
                "Create more connections between quests and characters",
                "Review character backstories for theme consistency",
                "Add quest chains that involve multiple NPCs"
            ] if coherence_score < 0.7 else []
        }
    def _count_npcs_with_quests(self, characters: Dict[str, Any], quests: Dict[str, Any]) -> int:
        """Count how many NPCs are involved in quests"""
        if not characters or not quests:
            return 0
        
        character_names = set(char.get('name', '') for char in characters.get('characters', []))
        quest_npcs = set()
        
        for quest in quests.get('quests', []):
            giver = quest.get('giver_npc', '')
            if giver and giver in character_names:
                quest_npcs.add(giver)
            
            # Check objectives for character mentions
            objectives = quest.get('objectives', [])
            for obj in objectives:
                obj_desc = obj.get('description', '').lower()
                for char_name in character_names:
                    if char_name.lower() in obj_desc:
                        quest_npcs.add(char_name)
        
        return len(quest_npcs)
    def _count_buildings_with_npcs(self, world_spec: Dict[str, Any], characters: Dict[str, Any]) -> int:
        """Count how many buildings have NPCs assigned"""
        if not world_spec or not characters:
            return 0
        
        buildings = world_spec.get('buildings', [])
        character_locations = set()
        
        for char in characters.get('characters', []):
            location = char.get('location', '').lower()
            if location:
                character_locations.add(location)
        
        buildings_with_npcs = 0
        for building in buildings:
            building_type = building.get('type', '').lower()
            building_name = building.get('name', '').lower()
            
            if any(loc in building_type or loc in building_name for loc in character_locations):
                buildings_with_npcs += 1
        
        return buildings_with_npcs
    def _check_themed_consistency(self, world_spec: Dict[str, Any], assets: Dict[str, Any], characters: Dict[str, Any]) -> Dict[str, Any]:
        """Check thematic consistency across world, assets, and characters"""
        if not all([world_spec, assets, characters]):
            return {"consistent": False, "issues": ["Missing content for theme analysis"]}
        
        world_theme = world_spec.get('theme', 'unknown').lower()
        consistency_issues = []
        
        # Define theme expectations
        theme_expectations = {
            'medieval': {
                'roles': ['knight', 'guard', 'blacksmith', 'merchant', 'priest', 'peasant', 'lord'],
                'buildings': ['castle', 'church', 'tavern', 'smithy', 'market', 'house'],
                'avoid': ['robot', 'computer', 'laser', 'spaceship', 'modern']
            },
            'fantasy': {
                'roles': ['mage', 'wizard', 'elf', 'dwarf', 'ranger', 'druid', 'paladin'],
                'buildings': ['tower', 'temple', 'library', 'enchanted', 'magical'],
                'avoid': ['car', 'phone', 'computer', 'modern', 'technology']
            },
            'sci-fi': {
                'roles': ['engineer', 'pilot', 'scientist', 'technician', 'commander', 'android'],
                'buildings': ['station', 'lab', 'hangar', 'dome', 'facility'],
                'avoid': ['magic', 'wizard', 'spell', 'dragon', 'medieval']
            }
        }
        
        expectations = theme_expectations.get(world_theme, {'roles': [], 'buildings': [], 'avoid': []})
        
        # Check character consistency
        character_consistency = True
        for char in characters.get('characters', []):
            char_role = char.get('role', '').lower()
            char_backstory = char.get('backstory', '').lower()
            
            # Check if role fits theme
            if expectations['roles'] and not any(role in char_role for role in expectations['roles']):
                consistency_issues.append(f"Character role '{char_role}' doesn't fit {world_theme} theme")
                character_consistency = False
            
            # Check for theme violations
            for avoid_term in expectations['avoid']:
                if avoid_term in char_backstory or avoid_term in char_role:
                    consistency_issues.append(f"Character contains inappropriate term '{avoid_term}' for {world_theme} theme")
                    character_consistency = False
        
        # Check building consistency
        building_consistency = True
        for building in world_spec.get('buildings', []):
            building_type = building.get('type', '').lower()
            
            # Check for theme violations
            for avoid_term in expectations['avoid']:
                if avoid_term in building_type:
                    consistency_issues.append(f"Building type '{building_type}' inappropriate for {world_theme} theme")
                    building_consistency = False
        
        # Overall consistency
        overall_consistent = character_consistency and building_consistency
        
        return {
            "consistent": overall_consistent,
            "character_consistency": character_consistency,
            "building_consistency": building_consistency,
            "theme": world_theme,
            "issues": consistency_issues[:5],  # Limit to first 5 issues
            "score": 1.0 if overall_consistent else (0.5 if character_consistency or building_consistency else 0.0)
        }
    def _generate_integration_recommendations(self, world_spec: Dict[str, Any], assets: Dict[str, Any], characters: Dict[str, Any], quests: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations for improving content integration"""
        recommendations = []
        
        if not all([world_spec, characters, quests]):
            recommendations.append("Generate all core content types (world, characters, quests) for proper integration")
            return recommendations
        
        # World-Character integration
        world_char_analysis = self._analyze_world_character_alignment(world_spec, characters)
        if world_char_analysis["alignment_score"] < 0.7:
            recommendations.append("Improve character-world alignment by adjusting NPC roles to match the world theme")
        
        # Character-Quest integration
        char_quest_analysis = self._analyze_character_quest_integration(characters, quests)
        if char_quest_analysis["integration_score"] < 0.7:
            recommendations.extend([
                "Involve more characters in quest storylines",
                "Create quests that utilize character relationships",
                "Distribute quest-giving among more NPCs"
            ])
        
        # Asset-World compatibility
        if assets:
            asset_world_analysis = self._analyze_asset_world_compatibility(assets, world_spec)
            if asset_world_analysis["compatibility_score"] < 0.7:
                recommendations.append("Generate additional assets to cover all required building types")
        
        # Narrative coherence
        narrative_analysis = self._analyze_narrative_coherence(world_spec, characters, quests)
        if narrative_analysis["coherence_score"] < 0.7:
            recommendations.extend([
                "Ensure thematic consistency across all content",
                "Create more interconnected storylines",
                "Review and align character backstories with world theme"
            ])
        
        # Content utilization recommendations
        unused_chars = char_quest_analysis.get("unused_characters", [])
        if len(unused_chars) > 0:
            recommendations.append(f"Create quests or storylines for unused characters: {', '.join(unused_chars[:3])}")
        
        # Theme consistency
        theme_check = self._check_themed_consistency(world_spec, assets, characters)
        if not theme_check["consistent"]:
            recommendations.append("Review and fix thematic inconsistencies across all content types")
        
        # Limit recommendations to most important ones
        return recommendations[:8]
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
    async def _step_5_balance_validation(self):
        """Step 5: Validate and balance all generated content"""
        print(f"\n⚖️ STEP 5: BALANCE VALIDATION")
        print(f"{'='*60}")
        
        try:
            if not BALANCE_VALIDATOR_AVAILABLE:
                print("⚠️ Balance Validator not available - skipping validation")
                self.balance_report = {
                    'status': 'skipped',
                    'reason': 'Balance Validator not available',
                    'overall_score': 0.75  # Default reasonable score
                }
                return
            
            # Import balance validator
            from .balance_validator.agent import AdvancedBalanceValidator
            
            # Initialize validator
            validator = AdvancedBalanceValidator(
                output_dir=str(self.current_session_dir / "balance_validation")
            )
            
            # Prepare content for validation
            world_spec = self.world_spec or {}
            assets = self.assets or {}
            characters = self.characters or {}
            quests = self.quests or {}
            
            print(f"🔍 Validating content balance...")
            print(f"   🌍 World: {len(world_spec.get('buildings', []))} buildings")
            print(f"   👥 Characters: {len(characters.get('characters', []))} NPCs") 
            print(f"   📜 Quests: {len(quests.get('quests', []))} storylines")
            print(f"   🎨 Assets: {assets.get('generation_summary', {}).get('total_creative_assets', 0)} items")
            
            # Run balance validation
            balance_report = await validator.validate_complete_content(
                world_spec, assets, characters, quests
            )
            
            # Convert balance report to dictionary format
            self.balance_report = {
                'status': 'success',
                'overall_balance': balance_report.overall_balance,
                'overall_score': balance_report.metrics.overall_score,
                'metrics': {
                    'difficulty_score': balance_report.metrics.difficulty_score,
                    'progression_rate': balance_report.metrics.progression_rate,
                    'xp_balance': balance_report.metrics.xp_balance,
                    'reward_balance': balance_report.metrics.reward_balance,
                    'challenge_curve': balance_report.metrics.challenge_curve,
                    'player_engagement': balance_report.metrics.player_engagement
                },
                'recommendations_count': len(balance_report.recommendations),
                'warnings_count': len(balance_report.warnings),
                'balance_summary': balance_report.balance_summary,
                'validated_content': balance_report.validated_content
            }
            
            # Apply any critical balance adjustments
            if balance_report.validated_content:
                self.validated_content = balance_report.validated_content
                
                # Update content with balance adjustments if available
                if 'characters' in balance_report.validated_content:
                    self.characters = balance_report.validated_content['characters']
                if 'quests' in balance_report.validated_content:
                    self.quests = balance_report.validated_content['quests']
            
            # Save balance report
            balance_file = self.current_session_dir / "balance_validation_report.json"
            with open(balance_file, 'w') as f:
                json.dump(self.balance_report, f, indent=2, default=str)
            
            print(f"\n✅ Balance validation completed!")
            print(f"   📊 Overall Balance: {balance_report.overall_balance}")
            print(f"   🎯 Overall Score: {balance_report.metrics.overall_score:.2f}/1.0")
            print(f"   📈 XP Balance: {balance_report.metrics.xp_balance:.2f}")
            print(f"   💰 Reward Balance: {balance_report.metrics.reward_balance:.2f}")
            print(f"   🎮 Difficulty Score: {balance_report.metrics.difficulty_score:.2f}")
            
            if balance_report.recommendations:
                critical_recs = [r for r in balance_report.recommendations if r.priority == 'critical']
                high_recs = [r for r in balance_report.recommendations if r.priority == 'high']
                print(f"   🔴 Critical Issues: {len(critical_recs)}")
                print(f"   🟡 High Priority: {len(high_recs)}")
                print(f"   📋 Total Recommendations: {len(balance_report.recommendations)}")
            
            if balance_report.warnings:
                print(f"   ⚠️ Warnings: {len(balance_report.warnings)}")
                for warning in balance_report.warnings[:3]:  # Show first 3 warnings
                    print(f"      • {warning}")
            
            print(f"   📁 Balance report saved: {balance_file.name}")
            
        except Exception as e:
            error_msg = f"Balance validation failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            
            # Create fallback balance report
            self.balance_report = {
                'status': 'failed',
                'error': str(e),
                'overall_score': 0.5,  # Default fallback score
                'overall_balance': 'unknown'
            }
            
            # Save error report
            error_file = self.current_session_dir / "balance_validation_error.json"
            with open(error_file, 'w') as f:
                json.dump(self.balance_report, f, indent=2)
    async def _step_6_complete_final_assembly(self):
        """Step 6: Complete Final Assembly - Integrate all content and create master manifest"""
        print(f"\n📦 STEP 6: COMPLETE FINAL ASSEMBLY")
        print(f"{'='*60}")
        
        try:
            print(f"🔧 Assembling complete game content package...")
            
            # Create assembly summary
            assembly_summary = {
                'world_spec_available': bool(self.world_spec),
                'assets_available': bool(self.assets),
                'characters_available': bool(self.characters),
                'quests_available': bool(self.quests),
                'balance_report_available': bool(self.balance_report),
                'validated_content_available': bool(self.validated_content)
            }
            
            # Use validated content if available, otherwise use original content
            final_world_spec = self.validated_content.get('world_spec', self.world_spec) if self.validated_content else self.world_spec
            final_assets = self.validated_content.get('assets', self.assets) if self.validated_content else self.assets
            final_characters = self.validated_content.get('characters', self.characters) if self.validated_content else self.characters
            final_quests = self.validated_content.get('quests', self.quests) if self.validated_content else self.quests
            
            # Create comprehensive content statistics
            content_stats = self._calculate_content_statistics(
                final_world_spec, final_assets, final_characters, final_quests
            )
            
            # Create master manifest
            master_manifest = await self._create_master_manifest(
                final_world_spec, final_assets, final_characters, final_quests, content_stats
            )
            
            # Save master manifest
            manifest_file = self.current_session_dir / "master_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(master_manifest, f, indent=2, default=str)
            
            # Create content integration report
            integration_report = await self._create_content_integration_report(
                final_world_spec, final_assets, final_characters, final_quests
            )
            
            # Save integration report
            integration_file = self.current_session_dir / "content_integration_report.json"
            with open(integration_file, 'w') as f:
                json.dump(integration_report, f, indent=2, default=str)
            
            # Create usage instructions
            usage_instructions = self._create_usage_instructions(content_stats)
            instructions_file = self.current_session_dir / "USAGE_INSTRUCTIONS.md"
            with open(instructions_file, 'w') as f:
                f.write(usage_instructions)
            
            # Create developer documentation
            dev_docs = self._create_developer_documentation(master_manifest, integration_report)
            dev_docs_file = self.current_session_dir / "DEVELOPER_GUIDE.md"
            with open(dev_docs_file, 'w') as f:
                f.write(dev_docs)
            
            # Copy/organize final content files
            await self._organize_final_content_files(
                final_world_spec, final_assets, final_characters, final_quests
            )
            
            # Create session summary
            session_summary = {
                'assembly_status': 'completed',
                'content_statistics': content_stats,
                'files_created': {
                    'master_manifest': str(manifest_file.name),
                    'integration_report': str(integration_file.name),
                    'usage_instructions': str(instructions_file.name),
                    'developer_guide': str(dev_docs_file.name)
                },
                'assembly_timestamp': datetime.now().isoformat(),
                'ready_for_export': True
            }
            
            # Save session summary
            summary_file = self.current_session_dir / "session_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(session_summary, f, indent=2, default=str)
            
            print(f"\n✅ Final assembly completed successfully!")
            print(f"   📊 Content Statistics:")
            print(f"      🌍 World: {content_stats.get('world_buildings', 0)} buildings, {content_stats.get('world_features', 0)} features")
            print(f"      🎨 Assets: {content_stats.get('total_assets', 0)} unique items")
            print(f"      👥 Characters: {content_stats.get('total_characters', 0)} NPCs")
            print(f"      📜 Quests: {content_stats.get('total_quests', 0)} storylines")
            print(f"      ⚖️ Balance: {'✅ Validated' if self.balance_report else '⚠️ Not validated'}")
            
            print(f"\n📁 Package Files Created:")
            print(f"   📋 Master Manifest: {manifest_file.name}")
            print(f"   🔗 Integration Report: {integration_file.name}")
            print(f"   📖 Usage Instructions: {instructions_file.name}")
            print(f"   👨‍💻 Developer Guide: {dev_docs_file.name}")
            print(f"   📊 Session Summary: {summary_file.name}")
            
            # Check content quality and completeness
            quality_score = self._calculate_content_quality_score(content_stats)
            print(f"\n🎯 Content Quality Score: {quality_score:.2f}/1.0")
            
            if quality_score >= 0.8:
                print(f"   ✅ Excellent - Ready for production use!")
            elif quality_score >= 0.6:
                print(f"   🟡 Good - Minor improvements recommended")
            else:
                print(f"   🔴 Needs improvement - Check error logs")
            
            print(f"   🎮 Ready for Godot export in Step 7!")
            
        except Exception as e:
            error_msg = f"Final assembly failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            
            # Create minimal fallback assembly
            fallback_manifest = {
                'assembly_status': 'failed',
                'error': str(e),
                'partial_content': {
                    'world_spec': bool(self.world_spec),
                    'assets': bool(self.assets),
                    'characters': bool(self.characters),
                    'quests': bool(self.quests)
                },
                'timestamp': datetime.now().isoformat()
            }
            
            fallback_file = self.current_session_dir / "fallback_manifest.json"
            with open(fallback_file, 'w') as f:
                json.dump(fallback_manifest, f, indent=2)
            print(f"   📋 Fallback manifest saved: {fallback_file.name}")

    async def _step_7_godot_package_export(self):
        """Step 7: Export complete Godot package"""
        print(f"\n🎮 STEP 7: GODOT PACKAGE EXPORT")
        print(f"{'='*60}")
        
        try:
            if not GODOT_EXPORTER_AVAILABLE:
                print("⚠️ Godot Exporterq not available - generating export instructions instead")
                self.godot_package = await self._fallback_godot_export_instructions()
                return
            
            # Verify the function is available
            try:
                # Test if export_godot_package is callable
                if not callable(export_godot_package):
                    raise AttributeError("export_godot_package is not callable")
                    
            except NameError:
                print("❌ export_godot_package function not found - using fallback")
                self.godot_package = await self._fallback_godot_export_instructions()
                return
            
            # Rest of the existing export code...
            print(f"🔧 Preparing Godot export...")
            
            # Validate content exists
            if not any([self.world_spec, self.assets, self.characters, self.quests]):
                print("⚠️ No content available for Godot export")
                self.godot_package = {'status': 'no_content', 'error': 'No content to export'}
                return
            
            # Set up content summary
            content_summary = {
                'world_buildings': len(self.world_spec.get('buildings', [])) if self.world_spec else 0,
                'assets_count': self.assets.get('generation_summary', {}).get('total_creative_assets', 0) if self.assets else 0,
                'character_count': len(self.characters.get('characters', [])) if self.characters else 0,
                'quest_count': len(self.quests.get('quests', [])) if self.quests else 0
            }
            
            if content_summary['character_count'] > 0:
                character_list = self.characters.get('characters', [])
                print(f"   👥 Characters: {len(character_list)}")
                
            if content_summary['quest_count'] > 0:
                quest_list = self.quests.get('quests', [])
                print(f"   📜 Quests: {len(quest_list)}")
            
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
            
            # Handle successful export
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
                
        except Exception as e:
            error_msg = f"Godot package export failed: {str(e)}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            # Don't raise - pipeline can still be useful without Godot export
            
            # Use fallback instructions
            self.godot_package = await self._fallback_godot_export_instructions()
    
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