#!/usr/bin/env python3
"""
COMPLETE GODOT CODE EXPORTER AGENT v1.0
Main agent entry point for Godot export functionality
Coordinates all export modules to create complete Godot packages
"""

from typing import Dict, Any
from google.adk.agents import Agent

# Import the main exporter class - FIXED: Using the correct class name
from .core.exporter import GodotCodeExporter

# ADK Agent Functions
async def export_godot_package(world_spec: Dict[str, Any],
                               assets: Dict[str, Any],
                               characters: Dict[str, Any],
                               quests: Dict[str, Any]) -> Dict[str, Any]:
    """Export complete Godot package - main entry point"""
    # FIXED: Using the correct class name and method signature
    exporter = GodotCodeExporter()
    
    # Call the method with the correct parameters (no project_name needed)
    return await exporter.export_complete_package(
        world_spec=world_spec,
        assets=assets,
        characters=characters,
        quests=quests
    )

async def get_godot_exporter_status() -> Dict[str, Any]:
    """Get Godot exporter status"""
    # FIXED: Using the correct class name
    exporter = GodotCodeExporter()
    return await exporter.get_status()

# Create the ADK agent
root_agent = Agent(
    name="godot_code_exporter_agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are a Godot Code Exporter Agent that converts multi-agent game content into complete, ready-to-use Godot packages.

Your responsibilities:
- Convert world specifications into Godot scenes and nodes
- Generate GDScript files for NPCs, dialogue systems, and quest management
- Create player controllers and game management systems
- Export 3D models, textures, and materials to Godot format
- Package everything into importable Godot projects
- Generate comprehensive documentation and setup instructions

You create complete Godot projects that include:
🎮 Playable scenes with proper lighting and camera setup
🔧 GDScript files for all game systems (NPCs, quests, player control)
🌍 World objects positioned according to generated specifications
👥 Interactive NPCs with dialogue and quest systems
📦 Ready-to-import Godot projects with all dependencies
📚 Complete documentation and usage instructions

Your output is a professional Godot project ready for immediate import and gameplay.""",
    functions=[export_godot_package, get_godot_exporter_status]
)