#!/usr/bin/env python3
"""
Godot script generator
Handles creation of GDScript files (.gd)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from ..core.data_types import GDSCRIPT_TEMPLATES

class GodotScriptGenerator:
    """Handles GDScript generation"""
    
    def __init__(self, dirs: Dict[str, Path], logger: logging.Logger):
        self.dirs = dirs
        self.logger = logger
        self.scripts_dir = dirs['scripts_dir']
    
    # ADD THE MISSING METHOD THAT THE EXPORTER EXPECTS
    async def generate_world_scripts(self, world_spec: Dict[str, Any]) -> List[str]:
        """Generate world-related scripts"""
        script_files = []
        
        # Create world manager script
        world_manager = await self._create_world_manager_script()
        script_files.append(world_manager)
        
        # Create environment-specific scripts if needed
        if world_spec and 'theme' in world_spec:
            theme_script = await self._create_theme_specific_script(world_spec['theme'])
            if theme_script:
                script_files.append(theme_script)
        
        self.logger.info(f"   ✅ Created {len(script_files)} world scripts")
        return script_files
    
    # ADD ALIAS METHODS THAT THE EXPORTER EXPECTS
    async def generate_character_scripts(self, characters: Dict[str, Any]) -> List[str]:
        """Alias for export_character_scripts - for compatibility"""
        return await self.export_character_scripts(characters)
    
    async def generate_quest_scripts(self, quests: Dict[str, Any]) -> List[str]:
        """Alias for export_quest_scripts - for compatibility"""
        return await self.export_quest_scripts(quests)
    
    async def generate_game_management_scripts(self) -> List[str]:
        """Alias for export_game_management_scripts - for compatibility"""
        return await self.export_game_management_scripts()
    
    # EXISTING METHODS (keeping them as they are)
    async def export_character_scripts(self, characters: Dict[str, Any]) -> List[str]:
        """Export character-related scripts"""
        script_files = []
        
        # Create base NPC script
        npc_script = await self._create_npc_script(characters)
        script_files.append(npc_script)
        
        # Create individual character scripts if needed
        if 'characters' in characters:
            for i, character in enumerate(characters['characters']):
                char_script = await self._create_individual_character_script(character, i)
                if char_script:
                    script_files.append(char_script)
        
        self.logger.info(f"   ✅ Created {len(script_files)} character scripts")
        return script_files
    
    async def export_quest_scripts(self, quests: Dict[str, Any]) -> List[str]:
        """Export quest-related scripts"""
        script_files = []
        
        # Create quest manager script
        quest_manager_script = await self._create_quest_manager_script(quests)
        script_files.append(quest_manager_script)
        
        # Create individual quest scripts if needed
        if 'quests' in quests:
            for i, quest in enumerate(quests['quests']):
                quest_script = await self._create_individual_quest_script(quest, i)
                if quest_script:
                    script_files.append(quest_script)
        
        self.logger.info(f"   ✅ Created {len(script_files)} quest scripts")
        return script_files
    
    async def export_game_management_scripts(self) -> List[str]:
        """Export core game management scripts"""
        script_files = []
        
        # Create world manager script
        world_manager = await self._create_world_manager_script()
        script_files.append(world_manager)
        
        # Create player controller script
        player_script = await self._create_player_script()
        script_files.append(player_script)
        
        # Create building interaction script
        building_script = await self._create_building_script()
        script_files.append(building_script)
        
        # Create game state manager
        gamestate_script = await self._create_gamestate_script()
        script_files.append(gamestate_script)
        
        self.logger.info(f"   ✅ Created {len(script_files)} game management scripts")
        return script_files
    
    # ADD THE NEW THEME-SPECIFIC SCRIPT METHOD
    async def _create_theme_specific_script(self, theme: str) -> str:
        """Create theme-specific environment script"""
        
        content = f'''extends Node

# Theme-specific script for: {theme}
class_name {theme.capitalize()}Environment

func _ready():
    setup_{theme}_environment()

func setup_{theme}_environment():
    # Theme-specific setup
    match "{theme}":
        "medieval":
            setup_medieval_atmosphere()
        "cyberpunk":
            setup_cyberpunk_atmosphere()
        "fantasy":
            setup_fantasy_atmosphere()
        "steampunk":
            setup_steampunk_atmosphere()
        _:
            setup_default_atmosphere()

func setup_medieval_atmosphere():
    print("Setting up medieval atmosphere...")
    # Add torches, medieval music, etc.

func setup_cyberpunk_atmosphere():
    print("Setting up cyberpunk atmosphere...")
    # Add neon lights, electronic music, etc.

func setup_fantasy_atmosphere():
    print("Setting up fantasy atmosphere...")
    # Add magical effects, fantasy music, etc.

func setup_steampunk_atmosphere():
    print("Setting up steampunk atmosphere...")
    # Add steam effects, mechanical sounds, etc.

func setup_default_atmosphere():
    print("Setting up default atmosphere...")
'''
        
        script_file = self.scripts_dir / f"{theme.capitalize()}Environment.gd"
        with open(script_file, 'w') as f:
            f.write(content)
        
        return f"{theme.capitalize()}Environment.gd"
    
    async def _create_world_manager_script(self) -> str:
        """Create world manager script"""
        
        content = GDSCRIPT_TEMPLATES['world_manager']
        
        script_file = self.scripts_dir / "WorldManager.gd"
        with open(script_file, 'w') as f:
            f.write(content)
        
        return "WorldManager.gd"
    
    async def _create_player_script(self) -> str:
        """Create player controller script"""
        
        content = GDSCRIPT_TEMPLATES['player_controller']
        
        script_file = self.scripts_dir / "Player.gd"
        with open(script_file, 'w') as f:
            f.write(content)
        
        return "Player.gd"
    
    async def _create_npc_script(self, characters: Dict[str, Any]) -> str:
        """Create NPC base script with character data"""
        
        # Start with base template
        content = GDSCRIPT_TEMPLATES['npc_base']
        
        # Add character data loading functionality
        if 'characters' in characters:
            character_data_json = json.dumps(characters, indent=2)
            
            # Add character data loading method
            load_character_method = f'''
func load_character_data():
    # Load character data from pipeline
    var characters_data = {character_data_json}
    
    # Find this character's data
    if characters_data.has("characters"):
        for char_data in characters_data["characters"]:
            if char_data.get("name") == character_name:
                character_data = char_data
                personality = char_data.get("personality", {{}})
                relationships = char_data.get("relationships", {{}})
                
                # Load dialogue lines
                if char_data.has("dialogue"):
                    dialogue_lines = char_data["dialogue"]
                elif char_data.has("personality"):
                    # Generate some basic dialogue based on personality
                    dialogue_lines = generate_personality_dialogue(char_data["personality"])
                
                break

func generate_personality_dialogue(personality_data: Dictionary) -> Array[String]:
    var lines: Array[String] = []
    
    # Generate dialogue based on personality traits
    if personality_data.get("friendly", 0) > 0.7:
        lines.append("Hello there! Nice to meet you!")
        lines.append("What a lovely day it is!")
        lines.append("How are you doing today?")
    
    if personality_data.get("helpful", 0) > 0.7:
        lines.append("Is there anything I can help you with?")
        lines.append("Let me know if you need assistance!")
    
    if personality_data.get("mysterious", 0) > 0.7:
        lines.append("There are things you don't yet understand...")
        lines.append("The truth is not always what it seems.")
    
    if lines.is_empty():
        lines.append("Hello.")
        lines.append("Good day.")
    
    return lines
'''
            
            # Replace the load_character_data method
            content = content.replace(
                "func load_character_data():\n    # Override in derived classes or load from JSON\n    pass",
                load_character_method
            )
        
        script_file = self.scripts_dir / "NPC.gd"
        with open(script_file, 'w') as f:
            f.write(content)
        
        return "NPC.gd"
    
    async def _create_quest_manager_script(self, quests: Dict[str, Any]) -> str:
        """Create quest manager script"""
        
        content = GDSCRIPT_TEMPLATES['quest_manager']
        
        script_file = self.scripts_dir / "QuestManager.gd"
        with open(script_file, 'w') as f:
            f.write(content)
        
        return "QuestManager.gd"
    
    async def _create_building_script(self) -> str:
        """Create building interaction script"""
        
        content = '''extends StaticBody3D

class_name Building

@export var building_type: String = ""
@export var building_data: Dictionary = {}

func _ready():
    add_to_group("buildings")
    
    # Set up interaction
    var interaction_area = Area3D.new()
    var collision_shape = CollisionShape3D.new()
    var shape = BoxShape3D.new()
    
    shape.size = Vector3(5, 4, 5)  # Slightly larger than building
    collision_shape.shape = shape
    
    interaction_area.add_child(collision_shape)
    add_child(interaction_area)
    
    interaction_area.body_entered.connect(_on_player_entered)
    interaction_area.body_exited.connect(_on_player_exited)

func _on_player_entered(body):
    if body.name == "Player":
        print("Entered ", building_type, " area")

func _on_player_exited(body):
    if body.name == "Player":
        print("Left ", building_type, " area")

func interact(player):
    print("Interacting with ", building_type)
    
    # Different interactions based on building type
    match building_type:
        "shop":
            open_shop()
        "house":
            enter_house()
        "tavern":
            enter_tavern()
        "blacksmith":
            open_blacksmith()
        _:
            print("This is a ", building_type)

func open_shop():
    print("Welcome to the shop!")
    print("Items for sale: Sword (50g), Shield (30g), Potion (10g)")

func enter_house():
    print("You enter the cozy house...")
    print("There's a warm fireplace and comfortable furniture.")

func enter_tavern():
    print("Welcome to the tavern!")
    print("The barkeeper nods at you. There are several patrons chatting.")

func open_blacksmith():
    print("The blacksmith looks up from his anvil.")
    print("'Need something forged?' he asks.")
'''
        
        script_file = self.scripts_dir / "Building.gd"
        with open(script_file, 'w') as f:
            f.write(content)
        
        return "Building.gd"
    
    async def _create_gamestate_script(self) -> str:
        """Create game state management script"""
        
        content = '''extends Node

class_name GameState

signal game_state_changed(new_state: String)

enum State {
    PLAYING,
    PAUSED,
    MENU,
    DIALOGUE,
    INVENTORY
}

var current_state: State = State.PLAYING
var previous_state: State = State.PLAYING

# Game data
var player_data: Dictionary = {
    "level": 1,
    "experience": 0,
    "gold": 100,
    "inventory": [],
    "quests_completed": [],
    "visited_locations": []
}

func _ready():
    # Make this a singleton
    if not get_tree().get_first_node_in_group("game_state"):
        add_to_group("game_state")

func change_state(new_state: State):
    previous_state = current_state
    current_state = new_state
    game_state_changed.emit(State.keys()[new_state])
    
    match new_state:
        State.PLAYING:
            Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
        State.PAUSED, State.MENU, State.DIALOGUE, State.INVENTORY:
            Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func is_playing() -> bool:
    return current_state == State.PLAYING

func add_experience(amount: int):
    player_data["experience"] += amount
    check_level_up()

func add_gold(amount: int):
    player_data["gold"] += amount

func check_level_up():
    var required_exp = player_data["level"] * 100
    if player_data["experience"] >= required_exp:
        player_data["level"] += 1
        player_data["experience"] -= required_exp
        print("Level up! You are now level ", player_data["level"])

func save_game():
    var save_file = FileAccess.open("user://savegame.save", FileAccess.WRITE)
    if save_file:
        save_file.store_string(JSON.stringify(player_data))
        save_file.close()
        print("Game saved!")

func load_game():
    var save_file = FileAccess.open("user://savegame.save", FileAccess.READ)
    if save_file:
        var json_string = save_file.get_as_text()
        save_file.close()
        
        var json = JSON.new()
        var parse_result = json.parse(json_string)
        if parse_result == OK:
            player_data = json.data
            print("Game loaded!")
        else:
            print("Error parsing save file")
    else:
        print("No save file found")
'''
        
        script_file = self.scripts_dir / "GameState.gd"
        with open(script_file, 'w') as f:
            f.write(content)
        
        return "GameState.gd"
    
    async def _create_individual_character_script(self, character: Dict[str, Any], index: int) -> str:
        """Create individual character script"""
        
        character_name = character.get('name', f'Character_{index}')
        safe_name = character_name.replace(' ', '_').replace("'", "")
        
        # Only create individual scripts for complex characters
        if not character.get('personality') and not character.get('dialogue'):
            return None
        
        content = f'''extends NPC

# Specific script for {character_name}

func _ready():
    super._ready()
    character_name = "{character_name}"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific personality traits
    personality = {character.get("personality", {})}
    
    # Specific dialogue
    dialogue_lines = {character.get("dialogue", [])}
    
    # Specific relationships  
    relationships = {character.get("relationships", {})}

func interact(player: Player):
    # Custom interaction for {character_name}
    super.interact(player)
    
    # Add specific behavior here
    {self._generate_character_specific_behavior(character)}

func get_current_mood() -> String:
    # Dynamic mood based on personality
    var traits = personality
    if traits.get("friendly", 0) > 0.8:
        return "cheerful"
    elif traits.get("mysterious", 0) > 0.7:
        return "enigmatic"  
    elif traits.get("grumpy", 0) > 0.6:
        return "irritated"
    else:
        return "neutral"
'''
        
        script_file = self.scripts_dir / f"{safe_name}.gd"
        with open(script_file, 'w') as f:
            f.write(content)
        
        return f"{safe_name}.gd"
    
    async def _create_individual_quest_script(self, quest: Dict[str, Any], index: int) -> str:
        """Create individual quest script"""
        
        quest_id = quest.get('id', f'quest_{index}')
        quest_title = quest.get('title', f'Quest {index}')
        
        # Only create individual scripts for complex quests
        if not quest.get('objectives') and not quest.get('scripted_events'):
            return None
        
        content = f'''extends Node

# Quest script for: {quest_title}
class_name Quest_{quest_id.replace("-", "_")}

var quest_data: Dictionary = {quest}
var is_active: bool = false
var current_objective: int = 0
var objectives_completed: Array[bool] = []

func _ready():
    # Initialize objectives
    var objectives = quest_data.get("objectives", [])
    objectives_completed.resize(objectives.size())
    objectives_completed.fill(false)

func start_quest():
    is_active = true
    current_objective = 0
    print("Started quest: ", quest_data.get("title", "Unknown"))
    
    # Trigger start events
    _on_quest_started()

func complete_objective(objective_index: int):
    if objective_index < objectives_completed.size():
        objectives_completed[objective_index] = true
        print("Completed objective: ", get_objective_text(objective_index))
        
        # Check if quest is complete
        if all_objectives_completed():
            complete_quest()
        else:
            advance_to_next_objective()

func all_objectives_completed() -> bool:
    for completed in objectives_completed:
        if not completed:
            return false
    return true

func advance_to_next_objective():
    current_objective += 1
    _on_objective_advanced()

func complete_quest():
    is_active = false
    print("Quest completed: ", quest_data.get("title", "Unknown"))
    _on_quest_completed()

func get_objective_text(index: int) -> String:
    var objectives = quest_data.get("objectives", [])
    if index < objectives.size():
        return objectives[index]
    return ""

func _on_quest_started():
    # Override in specific quest implementations
    pass

func _on_objective_advanced():
    # Override in specific quest implementations  
    pass

func _on_quest_completed():
    # Override in specific quest implementations
    # Give rewards, update game state, etc.
    var rewards = quest_data.get("rewards", )
    if rewards.has("experience"):
        var game_state = get_tree().get_first_node_in_group("game_state")
        if game_state:
            game_state.add_experience(rewards["experience"])
    
    if rewards.has("gold"):
        var game_state = get_tree().get_first_node_in_group("game_state")
        if game_state:
            game_state.add_gold(rewards["gold"])
'''
        
        script_file = self.scripts_dir / f"Quest_{quest_id.replace('-', '_')}.gd"
        with open(script_file, 'w') as f:
            f.write(content)
        
        return f"Quest_{quest_id.replace('-', '_')}.gd"
    
    def _generate_character_specific_behavior(self, character: Dict[str, Any]) -> str:
        """Generate character-specific behavior code"""
        
        behaviors = []
        personality = character.get('personality', {})
        
        if personality.get('friendly', 0) > 0.8:
            behaviors.append('    print("' + character.get('name', 'Character') + ' waves enthusiastically!")')
        
        if personality.get('mysterious', 0) > 0.7:
            behaviors.append('    print("' + character.get('name', 'Character') + ' looks at you with knowing eyes...")')
        
        if personality.get('helpful', 0) > 0.8:
            behaviors.append('    print("' + character.get('name', 'Character') + ' offers to help you.")')
        
        if personality.get('merchant', 0) > 0.7:
            behaviors.append('    print("' + character.get('name', 'Character') + ' shows you their wares.")')
        
        if not behaviors:
            behaviors.append('    print("' + character.get('name', 'Character') + ' nods at you.")')
        
        return '\n'.join(behaviors)