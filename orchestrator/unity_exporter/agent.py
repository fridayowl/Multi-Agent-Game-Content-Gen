#!/usr/bin/env python3
"""
COMPLETE UNITY CODE EXPORTER AGENT v3.0 - MODULAR
Main agent entry point for Unity export functionality
Coordinates all export modules to create complete Unity packages
"""

from typing import Dict, Any
from google.adk.agents import Agent

# Import the main exporter class
from .core.exporter import UnityCodeExporter

# ADK Agent Functions
async def export_unity_package(world_spec: Dict[str, Any], 
                              assets: Dict[str, Any], 
                              characters: Dict[str, Any], 
                              quests: Dict[str, Any]) -> Dict[str, Any]:
    """Export complete Unity package - main entry point"""
    exporter = UnityCodeExporter()
    return await exporter.export_complete_package(world_spec, assets, characters, quests)

async def get_code_exporter_status() -> Dict[str, Any]:
    """Get code exporter status"""
    exporter = UnityCodeExporter()
    return await exporter.get_status()

# Create the ADK agent
root_agent = Agent(
    name="unity_code_exporter_agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are a Unity Code Exporter Agent that converts multi-agent game content into complete, ready-to-use Unity packages.

Your responsibilities:
- Convert world specifications into Unity scenes and GameObjects
- Generate C# scripts for NPCs, dialogue systems, and quest management
- Create player controllers and game management systems
- Export 3D models, textures, and materials to Unity format
- Package everything into importable .unitypackage files
- Generate comprehensive documentation and setup instructions

You create complete Unity projects that include:
🎮 Playable scenes with proper lighting and camera setup
🔧 C# scripts for all game systems (NPCs, quests, player control)
🌍 World objects positioned according to generated specifications
👥 Interactive NPCs with dialogue and quest systems
📦 Ready-to-import Unity packages with all dependencies
📚 Complete documentation and usage instructions

Your output is a professional Unity package ready for immediate import and gameplay.""",
    functions=[export_unity_package, get_code_exporter_status]
)