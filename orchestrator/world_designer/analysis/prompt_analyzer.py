"""
Prompt analysis and parsing functionality.
"""

import re
from typing import Dict, Tuple
from ..utils.theme_configs import get_theme_defaults, get_theme_moods

def _analyze_design_prompt(prompt: str, constraints):
    """Analyze the design prompt to extract requirements"""
    
    # Parse prompt using keyword detection
    analysis = _parse_prompt_keywords(prompt)
    
    # Add enhanced analysis
    analysis["environmental_story"] = _generate_environmental_story(analysis)
    analysis["layout_type"] = _determine_optimal_layout(analysis)
    analysis["gameplay_flow"] = _analyze_gameplay_implications(analysis)
    
    return analysis

def _parse_prompt_keywords(prompt: str):
    """Parse prompt using keyword detection and rules"""
    prompt_lower = prompt.lower()
    
    # Theme detection
    theme_keywords = {
        "medieval": ["medieval", "castle", "knight", "blacksmith", "tavern"],
        "spooky": ["spooky", "halloween", "ghost", "haunted", "scary", "dark"],
        "halloween": ["halloween", "pumpkin", "witch", "skeleton", "zombie"],
        "desert": ["desert", "oasis", "sand", "trading post", "merchant", "dune"],
        "fantasy": ["fantasy", "magic", "wizard", "dragon", "elf", "dwarf"],
        "modern": ["modern", "city", "urban", "contemporary"],
        "sci-fi": ["sci-fi", "space", "futuristic", "cyber", "robot"]
    }
    
    detected_theme = "medieval"  # default
    for theme, keywords in theme_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_theme = theme
            break
    
    # Scale detection
    scale_keywords = {
        "outpost": ["outpost", "camp", "small settlement"],
        "village": ["village", "hamlet", "small town"],
        "town": ["town", "large village"],
        "city": ["city", "large town", "metropolis"]
    }
    
    detected_scale = "village"  # default
    for scale, keywords in scale_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_scale = scale
            break
    
    # Feature extraction
    building_keywords = {
        "house": ["house", "home", "residence", "dwelling"],
        "shop": ["shop", "store", "merchant"],
        "tavern": ["tavern", "inn", "pub", "bar"],
        "church": ["church", "temple", "shrine", "cathedral"],
        "blacksmith": ["blacksmith", "forge", "smithy"],
        "market": ["market", "bazaar", "marketplace"],
        "fountain": ["fountain", "well", "water feature"],
        "tower": ["tower", "spire", "lookout"],
        "wall": ["wall", "fortification", "defense"]
    }
    
    detected_features = []
    for building, keywords in building_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_features.append(building)
    
    # If no specific features mentioned, add defaults based on theme
    if not detected_features:
        detected_features = get_theme_defaults(detected_theme)
    
    # NPC and quest detection
    npc_count = 5  # default
    quest_count = 3  # default
    
    # Look for numbers in prompt
    numbers = re.findall(r'\d+', prompt)
    if numbers:
        for i, num in enumerate(numbers):
            if "npc" in prompt_lower or "character" in prompt_lower:
                npc_count = int(num)
            elif "quest" in prompt_lower:
                quest_count = int(num)
    
    return {
        "theme": detected_theme,
        "scope": detected_scale,
        "key_features": detected_features,
        "npc_count": npc_count,
        "quest_count": quest_count,
        "mood": _infer_mood(detected_theme, prompt_lower),
        "size": _calculate_size_from_scope(detected_scale)
    }

def _infer_mood(theme: str, prompt_lower: str) -> str:
    """Infer mood from theme and prompt content"""
    mood_keywords = {
        "dark": ["dark", "gloomy", "ominous", "forbidding"],
        "cheerful": ["bright", "cheerful", "happy", "welcoming"],
        "mysterious": ["mysterious", "enigmatic", "hidden", "secret"],
        "bustling": ["busy", "bustling", "active", "lively"]
    }
    
    for mood, keywords in mood_keywords.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return mood
    
    # Default moods by theme
    theme_moods = get_theme_moods()
    return theme_moods.get(theme, "neutral")

def _calculate_size_from_scope(scope: str) -> Tuple[int, int]:
    """Calculate world size based on scope"""
    size_map = {
        "outpost": (20, 20),
        "village": (40, 40),
        "town": (60, 60),
        "city": (100, 100)
    }
    return size_map.get(scope, (40, 40))

def _generate_environmental_story(analysis: Dict) -> str:
    """Generate environmental storytelling elements"""
    theme = analysis.get("theme", "medieval")
    scope = analysis.get("scope", "village")
    mood = analysis.get("mood", "neutral")
    
    stories = {
        ("medieval", "village"): "A peaceful farming community with a central market square where travelers rest",
        ("spooky", "village"): "An abandoned settlement where shadows move between crumbling buildings",
        ("halloween", "village"): "A village celebrating eternal Halloween where pumpkins glow mysteriously",
        ("desert", "village"): "An oasis trading post where merchants gather to exchange exotic goods"
    }
    
    return stories.get((theme, scope), f"A {mood} {scope} with {theme} architecture")

def _determine_optimal_layout(analysis: Dict) -> str:
    """Determine optimal layout pattern"""
    scope = analysis.get("scope", "village")
    
    layout_rules = {
        "outpost": "linear",
        "village": "radial", 
        "town": "grid",
        "city": "complex_grid"
    }
    
    return layout_rules.get(scope, "radial")

def _analyze_gameplay_implications(analysis: Dict) -> Dict:
    """Analyze gameplay flow implications"""
    return {
        "player_spawn_areas": ["main_entrance", "central_square"],
        "quest_hubs": analysis.get("key_features", [])[:3],
        "exploration_points": ["outskirts", "hidden_areas"],
        "social_areas": ["tavern", "market", "fountain"]
    }