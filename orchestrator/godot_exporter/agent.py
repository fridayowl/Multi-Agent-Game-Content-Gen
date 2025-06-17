#!/usr/bin/env python3
"""
Fixed Godot exporter agent wrapper
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

async def export_godot_package(world_spec: Dict[str, Any] = None,
                              assets: Dict[str, Any] = None,
                              characters: Dict[str, Any] = None,
                              quests: Dict[str, Any] = None,
                              project_name: str = "GeneratedGame") -> Dict[str, Any]:
    """
    Main export function called by the pipeline
    Now with comprehensive error handling and fallback mechanisms
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
        
        # Log what we're working with
        logger.info(f"📊 Input content:")
        logger.info(f"   🌍 World spec: {bool(world_spec)} ({len(world_spec.get('buildings', []))} buildings)")
        logger.info(f"   🎨 Assets: {bool(assets)} ({assets.get('generation_summary', {}).get('total_creative_assets', 0)} assets)")
        logger.info(f"   👥 Characters: {bool(characters)} ({len(characters.get('characters', []))} NPCs)")
        logger.info(f"   📜 Quests: {bool(quests)} ({len(quests.get('quests', []))} quests)")
        
        # Perform the export
        result = await exporter.export_project(
            project_name=project_name,
            world_spec=world_spec,
            assets=assets,
            characters=characters,
            quests=quests
        )
        
        # Log the result
        if result.get('status') in ['success', 'partial_success']:
            logger.info(f"✅ Godot export completed: {result.get('status')}")
            logger.info(f"📁 Project path: {result.get('project_path', 'Unknown')}")
            logger.info(f"📊 File counts: {result.get('file_counts', {})}")
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
            'file_counts': {'scripts': 0, 'scenes': 0, 'resources': 0, 'assets': 0}
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
            'version': '4.3'
        }
        
    except Exception as e:
        logger.error(f"Error getting exporter status: {e}")
        return {
            'available': False,
            'error': str(e),
            'status': 'error'
        }

def set_export_directory(output_dir: Path):
    """Set custom export directory"""
    global _exporter_instance
    
    output_dir.mkdir(parents=True, exist_ok=True)
    _exporter_instance = GodotExporter(output_dir, logger)
    logger.info(f"📁 Godot export directory set to: {output_dir}")

# Compatibility functions for the pipeline
async def create_godot_project(content: Dict[str, Any]) -> Dict[str, Any]:
    """Alternative function name for compatibility"""
    
    return await export_godot_package(
        world_spec=content.get('world_spec'),
        assets=content.get('assets'),
        characters=content.get('characters'),
        quests=content.get('quests'),
        project_name=content.get('project_name', 'GeneratedGame')
    )

# Root agent function for ADK compatibility
async def root_agent(prompt: str = "", **kwargs) -> Dict[str, Any]:
    """Root agent function for ADK web interface compatibility"""
    
    logger.info(f"🎮 Godot exporter root agent called with prompt: {prompt}")
    
    # Extract content from kwargs
    world_spec = kwargs.get('world_spec')
    assets = kwargs.get('assets')
    characters = kwargs.get('characters')
    quests = kwargs.get('quests')
    project_name = kwargs.get('project_name', 'GeneratedGame')
    
    # If no content provided, return status
    if not any([world_spec, assets, characters, quests]):
        status = await get_godot_exporter_status()
        return {
            'message': 'Godot exporter is ready. Provide world_spec, assets, characters, or quests to export.',
            'status': status,
            'usage': 'Call with world_spec, assets, characters, and/or quests parameters'
        }
    
    # Perform export
    result = await export_godot_package(
        world_spec=world_spec,
        assets=assets,
        characters=characters,
        quests=quests,
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

# Test function for debugging
async def test_godot_export():
    """Test function to verify the exporter works"""
    
    logger.info("🧪 Testing Godot export...")
    
    # Test data
    test_world = {
        'theme': 'fantasy',
        'buildings': [
            {'name': 'Castle', 'position': [0, 0, 0]},
            {'name': 'Village', 'position': [10, 0, 10]}
        ]
    }
    
    test_characters = {
        'characters': [
            {'name': 'Knight', 'personality': 'brave'},
            {'name': 'Merchant', 'personality': 'friendly'}
        ]
    }
    
    test_quests = {
        'quests': [
            {'name': 'Save the Princess', 'type': 'main'},
            {'name': 'Deliver Package', 'type': 'side'}
        ]
    }
    
    # Run test export
    result = await export_godot_package(
        world_spec=test_world,
        characters=test_characters,
        quests=test_quests,
        project_name="TestProject"
    )
    
    logger.info(f"🧪 Test result: {result.get('status', 'unknown')}")
    return result

# Pipeline integration helper
def integrate_with_pipeline(pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to integrate with existing pipeline results"""
    
    try:
        # Extract components from pipeline result
        components = {
            'world_spec': pipeline_result.get('world_spec'),
            'assets': pipeline_result.get('assets'), 
            'characters': pipeline_result.get('characters'),
            'quests': pipeline_result.get('quests'),
            'project_name': pipeline_result.get('project_name', 'PipelineGame')
        }
        
        # Filter out None values
        components = {k: v for k, v in components.items() if v is not None}
        
        logger.info(f"🔗 Integrating pipeline components: {list(components.keys())}")
        return components
        
    except Exception as e:
        logger.error(f"❌ Pipeline integration error: {e}")
        return {}

# Error recovery helper
async def recover_from_failed_export(error_info: Dict[str, Any]) -> Dict[str, Any]:
    """Attempt to recover from a failed export"""
    
    logger.info("🔄 Attempting export recovery...")
    
    try:
        # Try with minimal content
        minimal_world = {'theme': 'basic', 'buildings': []}
        minimal_chars = {'characters': []}
        minimal_quests = {'quests': []}
        
        recovery_result = await export_godot_package(
            world_spec=minimal_world,
            characters=minimal_chars,
            quests=minimal_quests,
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