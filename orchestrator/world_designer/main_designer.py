"""
Main world designer orchestration and public API.
"""

import asyncio
from dataclasses import asdict
from typing import Dict, Any

from .core.world_spec import WorldSpec
from .analysis.prompt_analyzer import _analyze_design_prompt
from .generation.terrain_generator import _generate_terrain_map
from .generation.building_placer import _plan_building_placement
from .generation.path_network import _generate_path_network
from .generation.natural_features import _place_natural_features, _calculate_spawn_points
from .validation.design_validator import _validate_design
from .visualization.viz_data_creator import _create_visualization_data, _calculate_complexity

def design_world_from_prompt(prompt: str):
    """
    Design a complete game world from a text prompt.
    
    Args:
        prompt: Natural language description of the world to create (e.g., "Create a spooky Halloween village")
        
    Returns:
        Complete world specification with buildings, terrain, paths, and features
    """
    constraints = {}  # Use empty dict as default
    
    print(f"🌍 Designing world from prompt: {prompt}")
    
    try:
        # Step 1: Analyze the prompt
        analysis = _analyze_design_prompt(prompt, constraints)
        print(f"📊 Analysis complete: {analysis.get('theme', 'unknown')} theme")
        
        # Step 2: Generate world specification  
        world_spec = _generate_world_spec(analysis)
        print(f"🏗️ Generated world: {len(world_spec.buildings)} buildings, {len(world_spec.paths)} paths")
        
        # Step 3: Validate design
        validated_spec = _validate_design(world_spec)
        
        # Step 4: Create visualization data
        visualization_data = _create_visualization_data(validated_spec)
        
        result = {
            "world_spec": asdict(validated_spec),
            "visualization_data": visualization_data,
            "analysis": analysis,
            "status": "success",
            "generation_time": "2-5 minutes",
            "complexity_score": _calculate_complexity(validated_spec.buildings, validated_spec.paths)
        }
        
        print(f"✅ World design completed successfully!")
        return result
        
    except Exception as e:
        print(f"❌ Error in world design: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "fallback_available": True
        }

def _generate_world_spec(analysis):
    """Generate detailed world specification"""
    
    theme = analysis.get("theme", "medieval")
    size = analysis.get("size", (40, 40))
    layout_type = analysis.get("layout_type", "radial")
    
    print(f"🗺️ Generating {size[0]}x{size[1]} {theme} world with {layout_type} layout")
    
    # Generate terrain map
    terrain_map = _generate_terrain_map(size, theme)
    
    # Plan and place buildings
    buildings = _plan_building_placement(analysis, size, terrain_map)
    
    # Generate path network
    paths = _generate_path_network(buildings, size)
    
    # Place natural features
    natural_features = _place_natural_features(analysis, terrain_map, buildings)
    
    # Calculate spawn points
    spawn_points = _calculate_spawn_points(buildings, paths)
    
    # Create world specification
    world_spec = WorldSpec(
        theme=theme,
        size=size,
        terrain_map=terrain_map,
        buildings=buildings,
        paths=paths,
        natural_features=natural_features,
        spawn_points=spawn_points,
        boundaries={"min_x": 0, "max_x": size[0], "min_y": 0, "max_y": size[1]},
        metadata={
            "analysis": analysis,
            "layout_type": layout_type,
            "building_count": len(buildings),
            "complexity_score": _calculate_complexity(buildings, paths),
            "estimated_build_time": f"{len(buildings) * 2 + len(natural_features)} minutes"
        }
    )
    
    return world_spec

# Additional functions for ADK compatibility
async def generate_world(prompt: str) -> Dict[str, Any]:
    """
    Generate world from prompt - wrapper for design_world_from_prompt
    This method is expected by the quick_test.py
    """
    result = design_world_from_prompt(prompt)
    if result["status"] == "success":
        return result["world_spec"]
    else:
        raise Exception(f"World generation failed: {result.get('error', 'Unknown error')}")

async def get_status() -> Dict[str, Any]:
    """Get world designer status"""
    return {
        'status': 'ready',
        'model': 'gemini-2.0-flash-exp',
        'capabilities': ['world_design', 'procedural_generation', 'spatial_reasoning']
    }

# Test function that can be run independently
async def test_world_designer_standalone():
    """Test the world designer functions directly"""
    print("🚀 Testing World Designer Agent (Standalone)...")
    
    # Test prompts
    test_prompts = [
        "Create a spooky Halloween village with 5 NPCs and 3 interconnected quests",
        "Generate a desert oasis trading post with merchants and treasure hunters", 
        "Build a medieval village with a blacksmith, tavern, and church"
    ]
    
    for i, prompt in enumerate(test_prompts):
        print(f"\n📝 Test {i+1}: {prompt}")
        
        try:
            result = design_world_from_prompt(prompt)
            
            if result["status"] == "success":
                spec = result["world_spec"]
                print(f"✅ Success! Generated {spec['theme']} world:")
                print(f"   - Size: {spec['size']}")
                print(f"   - Buildings: {len(spec['buildings'])}")
                print(f"   - Paths: {len(spec['paths'])}")
                print(f"   - Features: {len(spec['natural_features'])}")
                print(f"   - Complexity: {result['complexity_score']:.1f}")
            else:
                print(f"❌ Failed: {result['error']}")
                
        except Exception as e:
            print(f"💥 Exception: {e}")
    
    print("\n🎉 World Designer testing complete!")

if __name__ == "__main__":
    # Run standalone test
    asyncio.run(test_world_designer_standalone())