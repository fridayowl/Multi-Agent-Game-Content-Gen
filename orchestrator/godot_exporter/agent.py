#!/usr/bin/env python3
"""
Fixed Godot exporter agent wrapper with documentation generation support
Handles the integration with the main pipeline and provides robust error handling
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Import the fixed exporter
from .core.exporter import GodotExporter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global exporter instance
_exporter_instance = None

def get_exporter() -> GodotExporter:
    """Get or create the global exporter instance"""
    global _exporter_instance
    
    if _exporter_instance is None:
        # Default output directory
        output_dir = Path.cwd() / "godot_exports"
        output_dir.mkdir(exist_ok=True)
        _exporter_instance = GodotExporter(output_dir, logger)
    
    return _exporter_instance

# UPDATED FUNCTION SIGNATURE - Added balance_report and pipeline_log parameters
async def export_godot_package(world_spec: Dict[str, Any] = None,
                              assets: Dict[str, Any] = None,
                              characters: Dict[str, Any] = None,
                              quests: Dict[str, Any] = None,
                              balance_report: Dict[str, Any] = None,
                              pipeline_log: Dict[str, Any] = None,
                              project_name: str = "GeneratedGame") -> Dict[str, Any]:
    """
    Main export function called by the pipeline
    Now with comprehensive error handling, fallback mechanisms, and documentation generation
    """
    
    logger.info(f"🎮 Starting Godot package export for: {project_name}")
    
    try:
        # Get exporter instance
        exporter = get_exporter()
        
        # Validate inputs
        world_spec = world_spec or {}
        assets = assets or {}
        characters = characters or {}
        quests = quests or {}
        balance_report = balance_report or {}
        pipeline_log = pipeline_log or {}
        
        # Log what we're working with
        logger.info(f"📊 Input content:")
        logger.info(f"   🌍 World spec: {bool(world_spec)} ({len(world_spec.get('buildings', []))} buildings)")
        logger.info(f"   🎨 Assets: {bool(assets)} ({assets.get('generation_summary', {}).get('total_creative_assets', 0)} assets)")
        logger.info(f"   👥 Characters: {bool(characters)} ({len(characters.get('characters', []))} NPCs)")
        logger.info(f"   📜 Quests: {bool(quests)} ({len(quests.get('quests', []))} quests)")
        logger.info(f"   ⚖️ Balance Report: {bool(balance_report)} (Score: {balance_report.get('overall_score', 'N/A')})")
        logger.info(f"   📋 Pipeline Log: {bool(pipeline_log)} (Agents: {len(pipeline_log.get('agent_performance', {}))})")
        
        # Perform the export with all data including documentation generation
        result = await exporter.export_project(
            project_name=project_name,
            world_spec=world_spec,
            assets=assets,
            characters=characters,
            quests=quests,
            balance_report=balance_report,  # NEW: Pass balance report
            pipeline_log=pipeline_log       # NEW: Pass pipeline log
        )
        
        # Log the result
        if result.get('status') in ['success', 'partial_success']:
            logger.info(f"✅ Godot export completed: {result.get('status')}")
            logger.info(f"📁 Project path: {result.get('project_path', 'Unknown')}")
            logger.info(f"📊 File counts: {result.get('file_counts', {})}")
            
            # NEW: Log documentation generation result
            if result.get('documentation_path'):
                logger.info(f"📋 Documentation: {Path(result['documentation_path']).name}")
            
            if result.get('error'):
                logger.warning(f"⚠️ Export completed with warnings: {result.get('error')}")
        else:
            logger.error(f"❌ Godot export failed: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Critical error in Godot export: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Return fallback result
        return {
            'status': 'error',
            'error': f"Critical export failure: {str(e)}",
            'project_name': project_name,
            'project_path': '',
            'manifest': None,
            'output_directory': str(get_exporter().output_dir),
            'godot_project_path': '',
            'import_ready': False,
            'file_counts': {'scripts': 0, 'scenes': 0, 'resources': 0, 'assets': 0},
            'documentation_path': None  # NEW: Include in fallback
        }

async def get_godot_exporter_status() -> Dict[str, Any]:
    """Get the status of the Godot exporter"""
    
    try:
        exporter = get_exporter()
        status = await exporter.get_status()
        
        return {
            'available': True,
            'status': status.get('status', 'unknown'),
            'output_directory': status.get('output_dir', 'unknown'),
            'exported_projects': status.get('exported_projects', 0),
            'version': '4.4',  # Updated version
            'documentation_support': True  # NEW: Indicate documentation support
        }
        
    except Exception as e:
        logger.error(f"Error getting exporter status: {e}")
        return {
            'available': False,
            'error': str(e),
            'status': 'error',
            'documentation_support': False
        }

def set_export_directory(output_dir: Path):
    """Set custom export directory"""
    global _exporter_instance
    
    output_dir.mkdir(parents=True, exist_ok=True)
    _exporter_instance = GodotExporter(output_dir, logger)
    logger.info(f"📁 Godot export directory set to: {output_dir}")

# UPDATED: Compatibility functions for the pipeline with new parameters
async def create_godot_project(content: Dict[str, Any]) -> Dict[str, Any]:
    """Alternative function name for compatibility"""
    
    return await export_godot_package(
        world_spec=content.get('world_spec'),
        assets=content.get('assets'),
        characters=content.get('characters'),
        quests=content.get('quests'),
        balance_report=content.get('balance_report'),  # NEW: Support balance report
        pipeline_log=content.get('pipeline_log'),      # NEW: Support pipeline log
        project_name=content.get('project_name', 'GeneratedGame')
    )

# UPDATED: Root agent function for ADK compatibility with new parameters
async def root_agent(prompt: str = "", **kwargs) -> Dict[str, Any]:
    """Root agent function for ADK web interface compatibility"""
    
    logger.info(f"🎮 Godot exporter root agent called with prompt: {prompt}")
    
    # Extract content from kwargs
    world_spec = kwargs.get('world_spec')
    assets = kwargs.get('assets')
    characters = kwargs.get('characters')
    quests = kwargs.get('quests')
    balance_report = kwargs.get('balance_report')  # NEW: Extract balance report
    pipeline_log = kwargs.get('pipeline_log')      # NEW: Extract pipeline log
    project_name = kwargs.get('project_name', 'GeneratedGame')
    
    # If no content provided, return status
    if not any([world_spec, assets, characters, quests]):
        status = await get_godot_exporter_status()
        return {
            'message': 'Godot exporter is ready. Provide world_spec, assets, characters, or quests to export.',
            'status': status,
            'usage': 'Call with world_spec, assets, characters, quests, balance_report, and/or pipeline_log parameters',
            'features': [
                'Complete Godot project generation',
                'Comprehensive PDF documentation',
                'Agent collaboration analysis',
                'Game balance reporting',
                'Usage instructions'
            ]
        }
    
    # Perform export with all available data
    result = await export_godot_package(
        world_spec=world_spec,
        assets=assets,
        characters=characters,
        quests=quests,
        balance_report=balance_report,  # NEW: Pass balance report
        pipeline_log=pipeline_log,      # NEW: Pass pipeline log
        project_name=project_name
    )
    
    return result

# Make sure these functions are available for import
__all__ = [
    'export_godot_package',
    'get_godot_exporter_status', 
    'set_export_directory',
    'create_godot_project',
    'root_agent'
]

# UPDATED: Test function with new documentation features
async def test_godot_export():
    """Test function to verify the exporter works with documentation generation"""
    
    logger.info("🧪 Testing Godot export with documentation...")
    
    # Test data
    test_world = {
        'theme': 'fantasy',
        'size': [40, 40],
        'buildings': [
            {'name': 'Castle', 'position': {'x': 0, 'y': 0, 'z': 0}, 'type': 'castle'},
            {'name': 'Village', 'position': {'x': 10, 'y': 0, 'z': 10}, 'type': 'house'}
        ]
    }
    
    test_characters = {
        'characters': [
            {
                'name': 'Knight Arthur', 
                'personality': {'primary_trait': 'brave'}, 
                'role': 'Guard',
                'location': 'castle',
                'quest_giver': True
            },
            {
                'name': 'Merchant Bob', 
                'personality': {'primary_trait': 'friendly'}, 
                'role': 'Shopkeeper',
                'location': 'house',
                'quest_giver': False
            }
        ]
    }
    
    test_quests = {
        'quests': [
            {
                'name': 'Save the Princess', 
                'type': 'main',
                'giver': 'Knight Arthur',
                'objectives': ['Find the princess', 'Defeat the dragon'],
                'rewards': {'experience': 100, 'gold': 50}
            },
            {
                'name': 'Deliver Package', 
                'type': 'side',
                'giver': 'Merchant Bob',
                'objectives': ['Get package', 'Deliver to castle'],
                'rewards': {'experience': 25, 'gold': 15}
            }
        ]
    }
    
    test_balance = {
        'overall_score': 0.85,
        'xp_balance': {'xp_balance_ratio': 1.1},
        'economic_balance': {'economic_balance_score': 0.8, 'total_quest_gold': 65},
        'character_balance': {'interaction_balance': 0.9},
        'quest_balance': {'difficulty_balance': 0.8}
    }
    
    test_pipeline_log = {
        'agent_performance': {
            'world_designer': {'successful': True, 'available': True},
            'asset_generator': {'successful': True, 'available': True},
            'character_creator': {'successful': True, 'available': True},
            'quest_writer': {'successful': True, 'available': True},
            'balance_validator': {'successful': True, 'available': True},
            'godot_exporter': {'successful': True, 'available': True}
        },
        'content_statistics': {
            'world_buildings': 2,
            'generated_npcs': 2,
            'total_quests': 2,
            'balance_score': 0.85
        },
        'timestamp': '2024-12-15T14:30:52'
    }
    
    # Run test export with all new features
    result = await export_godot_package(
        world_spec=test_world,
        characters=test_characters,
        quests=test_quests,
        balance_report=test_balance,        # NEW: Test balance report
        pipeline_log=test_pipeline_log,     # NEW: Test pipeline log
        project_name="TestProjectWithDocs"
    )
    
    logger.info(f"🧪 Test result: {result.get('status', 'unknown')}")
    
    # NEW: Check documentation generation
    if result.get('documentation_path'):
        logger.info(f"📋 Documentation generated: {result['documentation_path']}")
        
        # Verify file exists
        doc_path = Path(result['documentation_path'])
        if doc_path.exists():
            logger.info(f"✅ Documentation file exists: {doc_path.name}")
            logger.info(f"📏 File size: {doc_path.stat().st_size} bytes")
        else:
            logger.warning("⚠️ Documentation file not found")
    else:
        logger.warning("⚠️ No documentation path in result")
    
    return result

# UPDATED: Pipeline integration helper with new parameters
def integrate_with_pipeline(pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to integrate with existing pipeline results including documentation data"""
    
    try:
        # Extract components from pipeline result
        components = {
            'world_spec': pipeline_result.get('world_spec'),
            'assets': pipeline_result.get('assets'), 
            'characters': pipeline_result.get('characters'),
            'quests': pipeline_result.get('quests'),
            'balance_report': pipeline_result.get('balance_report'),  # NEW: Extract balance report
            'pipeline_log': pipeline_result.get('pipeline_log'),      # NEW: Extract pipeline log
            'project_name': pipeline_result.get('project_name', 'PipelineGame')
        }
        
        # Filter out None values
        components = {k: v for k, v in components.items() if v is not None}
        
        logger.info(f"🔗 Integrating pipeline components: {list(components.keys())}")
        return components
        
    except Exception as e:
        logger.error(f"❌ Pipeline integration error: {e}")
        return {}

# UPDATED: Error recovery helper with documentation support
async def recover_from_failed_export(error_info: Dict[str, Any]) -> Dict[str, Any]:
    """Attempt to recover from a failed export with minimal documentation"""
    
    logger.info("🔄 Attempting export recovery...")
    
    try:
        # Try with minimal content
        minimal_world = {'theme': 'basic', 'buildings': [], 'size': [20, 20]}
        minimal_chars = {'characters': []}
        minimal_quests = {'quests': []}
        minimal_balance = {'overall_score': 0.5}
        minimal_log = {
            'agent_performance': {'godot_exporter': {'successful': True, 'available': True}},
            'content_statistics': {'recovery_mode': True}
        }
        
        recovery_result = await export_godot_package(
            world_spec=minimal_world,
            characters=minimal_chars,
            quests=minimal_quests,
            balance_report=minimal_balance,  # NEW: Include minimal balance
            pipeline_log=minimal_log,        # NEW: Include minimal log
            project_name="RecoveredProject"
        )
        
        if recovery_result.get('status') in ['success', 'partial_success']:
            logger.info("✅ Export recovery successful")
            recovery_result['recovered'] = True
            recovery_result['original_error'] = error_info
            return recovery_result
        else:
            logger.error("❌ Export recovery also failed")
            return error_info
            
    except Exception as e:
        logger.error(f"❌ Recovery attempt failed: {e}")
        return error_info

# NEW: Helper function to create mock pipeline log for testing
def create_mock_pipeline_log(session_id: str = "test_session") -> Dict[str, Any]:
    """Create a mock pipeline log for testing documentation generation"""
    
    from datetime import datetime
    
    return {
        'agent_performance': {
            'world_designer': {
                'successful': True, 
                'available': True,
                'output_summary': "Fantasy world with castles and villages"
            },
            'asset_generator': {
                'successful': True, 
                'available': True,
                'output_summary': "Medieval themed 3D assets"
            },
            'character_creator': {
                'successful': True, 
                'available': True,
                'output_summary': "Knights and merchants with relationships"
            },
            'quest_writer': {
                'successful': True, 
                'available': True,
                'output_summary': "Heroic quests and merchant tasks"
            },
            'balance_validator': {
                'successful': True, 
                'available': True,
                'output_summary': "Balanced economy and progression"
            },
            'godot_exporter': {
                'successful': True, 
                'available': True,
                'output_summary': "Complete game with documentation"
            }
        },
        'content_statistics': {
            'world_buildings': 2,
            'creative_assets': 5,
            'generated_npcs': 2,
            'total_quests': 2,
            'main_quests': 1,
            'side_quests': 1,
            'balance_score': 0.85
        },
        'errors': [],
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'total_execution_time': '45 seconds'
    }

# NEW: Documentation-specific test function
async def test_documentation_only():
    """Test just the documentation generation component"""
    
    logger.info("🧪 Testing documentation generation only...")
    
    try:
        from .core.dynamic_game_report_generator import generate_complete_game_documentation
        
        # Create test output directory
        test_output_dir = Path.cwd() / "test_documentation_output"
        test_output_dir.mkdir(exist_ok=True)
        
        # Create comprehensive test data
        test_data = {
            'world_spec': {
                'theme': 'medieval',
                'size': [40, 40],
                'setting_type': 'Village',
                'buildings': [
                    {'type': 'castle', 'position': {'x': 20, 'y': 20, 'z': 0}},
                    {'type': 'house', 'position': {'x': 10, 'y': 10, 'z': 0}},
                    {'type': 'shop', 'position': {'x': 30, 'y': 15, 'z': 0}}
                ]
            },
            'assets': {'buildings': [], 'generation_summary': {'total_creative_assets': 15}},
            'characters': {
                'characters': [
                    {'name': 'Sir Lancelot', 'role': 'Knight', 'location': 'castle', 'quest_giver': True},
                    {'name': 'Baker Anne', 'role': 'Baker', 'location': 'shop', 'quest_giver': False}
                ]
            },
            'quests': {
                'quests': [
                    {'name': 'The Dragon Quest', 'type': 'main', 'giver': 'Sir Lancelot'},
                    {'name': 'Daily Bread', 'type': 'side', 'giver': 'Baker Anne'}
                ]
            },
            'balance_report': {
                'overall_score': 0.82,
                'xp_balance': {'xp_balance_ratio': 1.05},
                'economic_balance': {'economic_balance_score': 0.8, 'total_quest_gold': 125},
                'character_balance': {'interaction_balance': 0.85},
                'quest_balance': {'difficulty_balance': 0.8}
            },
            'pipeline_log': create_mock_pipeline_log(),
            'godot_export_data': {
                'project_path': str(test_output_dir / "TestProject"),
                'file_counts': {'scripts': 12, 'scenes': 5, 'resources': 8, 'assets': 15},
                'import_ready': True,
                'export_timestamp': datetime.now().isoformat()
            }
        }
        
        # Generate documentation
        documentation_path = await generate_complete_game_documentation(
            output_dir=test_output_dir,
            logger=logger,
            **test_data
        )
        
        logger.info(f"✅ Documentation generation test passed")
        logger.info(f"📋 Generated: {documentation_path}")
        
        # Verify file
        if Path(documentation_path).exists():
            file_size = Path(documentation_path).stat().st_size
            logger.info(f"📏 File size: {file_size} bytes")
            return True
        else:
            logger.error("❌ Documentation file not created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Documentation test failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

# Main execution for testing
if __name__ == "__main__":
    print("🎮 Godot Exporter Agent - Enhanced with Documentation Generation")
    print("="*70)
    
    async def run_tests():
        print("\n🧪 Running comprehensive tests...")
        
        # Test 1: Documentation generation only
        print("\n1️⃣ Testing documentation generation...")
        doc_test = await test_documentation_only()
        
        # Test 2: Full export with documentation
        print("\n2️⃣ Testing full export with documentation...")
        export_test = await test_godot_export()
        
        # Test 3: Status check
        print("\n3️⃣ Testing status check...")
        status = await get_godot_exporter_status()
        print(f"Status: {status}")
        
        print(f"\n✅ Test Results:")
        print(f"   📋 Documentation: {'✅ PASS' if doc_test else '❌ FAIL'}")
        print(f"   🎮 Full Export: {'✅ PASS' if export_test.get('status') == 'success' else '❌ FAIL'}")
        print(f"   📊 Status Check: {'✅ PASS' if status.get('available') else '❌ FAIL'}")
    
    # Run tests
    asyncio.run(run_tests())