#!/usr/bin/env python3
"""
FIXED Godot script generator - Resolves NPC inheritance errors
Handles creation of GDScript files (.gd) with proper Python-to-GDScript conversion
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List

# Define GDSCRIPT_TEMPLATES with FIXED NPC base class
GDSCRIPT_TEMPLATES = {
    'world_manager': '''extends Node

class_name WorldManager

var world_data: Dictionary = {}

func _ready():
    print("World Manager initialized")
    load_world_data()

func load_world_data():
    # Load world configuration from JSON
    var file = FileAccess.open("res://data/world_spec.json", FileAccess.READ)
    if file:
        var json_string = file.get_as_text()
        file.close()
        
        var json = JSON.new()
        var parse_result = json.parse(json_string)
        if parse_result == OK:
            world_data = json.data
            print("World data loaded")
        else:
            push_error("Error parsing world data")
    else:
        push_error("Could not open world data file")
''',
    
    # FIXED: Proper NPC base class with class_name declaration
    'npc_base': '''extends CharacterBody3D

class_name NPC

@export var character_name: String = "NPC"
@export var can_interact: bool = true

var character_data: Dictionary = {}
var relationships: Array = []
var dialogue_lines: Array[String] = []
var current_dialogue_index: int = 0

func _ready():
    add_to_group("npcs")
    load_character_data()

func interact(player: Variant):
    if not can_interact:
        return
    
    print(character_name, " interacts with player")
    start_dialogue()

func start_dialogue():
    if dialogue_lines.size() > 0:
        speak_line(dialogue_lines[current_dialogue_index])
        current_dialogue_index = (current_dialogue_index + 1) % dialogue_lines.size()
    else:
        speak_line("Hello there!")

func speak_line(text: String):
    print(character_name + ": " + text)

func add_dialogue_line(line: String):
    dialogue_lines.append(line)

func load_character_data():
    # Override in derived classes or load from JSON
    if character_data.has("dialogue"):
        var dialogue_array = character_data["dialogue"]
        for line in dialogue_array:
            add_dialogue_line(str(line))
'''
}

class GodotScriptGenerator:
    """FIXED Handles GDScript generation with proper syntax conversion"""
    
    def __init__(self, dirs: Dict[str, Path], logger: logging.Logger):
        self.dirs = dirs
        self.logger = logger
        self.scripts_dir = dirs['scripts_dir']
        
        # Ensure scripts directory exists
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
    
    def python_to_gdscript_converter(self, data) -> str:
        """Convert Python data structures to GDScript syntax"""
        
        if isinstance(data, dict):
            if not data:  # Empty dict
                return "{}"
            items = []
            for key, value in data.items():
                key_str = f'"{key}"'
                value_str = self.python_to_gdscript_converter(value)
                items.append(f"    {key_str}: {value_str}")
            return "{\n" + ",\n".join(items) + "\n}"
        
        elif isinstance(data, list):
            if not data:  # Empty list
                return "[]"
            items = [self.python_to_gdscript_converter(item) for item in data]
            if len(items) == 1:
                return "[" + items[0] + "]"
            return "[\n    " + ",\n    ".join(items) + "\n]"
        
        elif isinstance(data, str):
            # Escape quotes properly for GDScript
            escaped = data.replace('"', '\\"').replace('\n', '\\n')
            return f'"{escaped}"'
        
        elif isinstance(data, bool):
            return "true" if data else "false"
        
        elif data is None:
            return "null"
        
        elif isinstance(data, (int, float)):
            return str(data)
        
        else:
            # Fallback - convert to string
            escaped = str(data).replace('"', '\\"').replace('\n', '\\n')
            return f'"{escaped}"'
    
    def _sanitize_class_name(self, name: str) -> str:
        """Sanitize name for use in class_name declarations"""
        if not name:
            return "UnnamedQuest"
        
        # Remove dots and other invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Ensure it starts with a letter or underscore
        if sanitized and sanitized[0].isdigit():
            sanitized = f"Quest_{sanitized}"
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        return sanitized if sanitized else "UnnamedQuest"
    
    # CRITICAL FIX: Create NPC base class FIRST
    async def export_game_management_scripts(self) -> List[str]:
        """Export core game management scripts - FIXED ORDER"""
        script_files = []
        
        # STEP 1: Create NPC base class FIRST - this is critical!
        npc_base_script = await self._create_npc_base_script()
        script_files.append(npc_base_script)
        
        # STEP 2: Create CharacterData resource script (fixes parameter error)
        character_data_script = await self._create_character_data_script()
        script_files.append(character_data_script)
        
        # STEP 3: Create other base classes
        world_manager = await self._create_world_manager_script()
        script_files.append(world_manager)
        
        player_script = await self._create_player_script()
        script_files.append(player_script)
        
        building_script = await self._create_building_script()
        script_files.append(building_script)
        
        gamestate_script = await self._create_gamestate_script()
        script_files.append(gamestate_script)
        
        globaldata_script = await self._create_globaldata_script()
        script_files.append(globaldata_script)
        
        self.logger.info(f"   ✅ Created {len(script_files)} game management scripts")
        return script_files
    
    # CRITICAL FIX: Separate NPC base creation method
    async def _create_npc_base_script(self) -> str:
        """Create NPC base script with proper class_name - CRITICAL FIX"""
        
        content = GDSCRIPT_TEMPLATES['npc_base']
        
        script_file = self.scripts_dir / "NPC.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info("✅ Created NPC base class with proper class_name")
        return "NPC.gd"
    
    # CRITICAL FIX: Create CharacterData resource script
    async def _create_character_data_script(self) -> str:
        """Create CharacterData resource script with proper syntax - FIXES parameter error"""
        
        content = '''extends Resource

class_name CharacterData

# Character data resource - NO @export parameters (this was causing the error)
# Resources use direct property assignment, not @export

var character_name: String = ""
var dialogue_lines: Array[String] = []
var relationships: Array = []
var stats: Dictionary = {}
var inventory: Array = []
var location: String = ""

func _init():
    # Initialize with defaults
    pass

func get_dialogue_for_mood(mood: String) -> Array[String]:
    # Return appropriate dialogue based on mood
    if dialogue_lines.size() > 0:
        return dialogue_lines
    else:
        return ["Hello there!"]

func add_dialogue_line(line: String):
    if line not in dialogue_lines:
        dialogue_lines.append(line)

func get_relationship_with(character: String) -> String:
    # Search through relationships array for the character
    for relationship in relationships:
        if relationship.get("target_character") == character:
            return relationship.get("relationship_type", "neutral")
    return "neutral"

func has_trait(trait_name: String) -> bool:
    return false  # No personality traits in this version
'''
        
        script_file = self.scripts_dir / "CharacterData.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info("✅ Created CharacterData resource script with fixed syntax")
        return "CharacterData.gd"
    
    async def export_character_scripts(self, characters: Dict[str, Any]) -> List[str]:
        """Export character-related scripts - FIXED to not recreate NPC base"""
        script_files = []
        
        # NOTE: NPC base script is created in export_game_management_scripts()
        
        # Create individual character scripts if needed
        if 'characters' in characters:
            for i, character in enumerate(characters['characters']):
                char_script = await self._create_individual_character_script(character, i)
                if char_script:
                    script_files.append(char_script)
        
        self.logger.info(f"   ✅ Created {len(script_files)} character scripts")
        return script_files
    
    async def _create_individual_character_script(self, character: Dict[str, Any], index: int) -> str:
        """Create individual character script - FIXED VERSION"""
        
        character_name = character.get('name', f'Character_{index}')
        safe_name = character_name.replace(' ', '_').replace("'", "").replace(".", "_")
        
        # Only create individual scripts for complex characters
        if not character.get('personality') and not character.get('dialogue'):
            return None
        
        # FIXED: Convert Python data to GDScript syntax
        dialogue_gdscript = self.python_to_gdscript_converter(character.get("dialogue", []))
        relationships_gdscript = self.python_to_gdscript_converter(character.get("relationships", []))
        character_behavior = self._generate_character_specific_behavior(character)
        
        content = f'''extends NPC

# Specific script for {character_name}

func _ready():
    super._ready()
    character_name = "{character_name}"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific dialogue - FIXED SYNTAX  
    var dialogue_array = {dialogue_gdscript}
    for line in dialogue_array:
        add_dialogue_line(str(line))
    
    # Specific relationships - FIXED SYNTAX
    relationships = {relationships_gdscript}

func interact(player: Variant):
    # Custom interaction for {character_name}
    super.interact(player)
    
    # Add specific behavior here
{character_behavior}

func get_current_mood() -> String:
    # Simple mood system without personality traits
    return "neutral"
'''
        
        script_file = self.scripts_dir / f"{safe_name}.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"{safe_name}.gd"
    
    def _generate_character_specific_behavior(self, character: Dict[str, Any]) -> str:
        """Generate character-specific behavior code - SIMPLIFIED VERSION"""
        
        character_name = character.get('name', 'Character')
        
        # Escape character name for GDScript strings
        escaped_name = character_name.replace('"', '\\"')
        
        # Simple behavior without personality checks
        return f'    print("{escaped_name} nods at you.")'
    
    # Additional required methods from original code
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
    
    async def generate_character_scripts(self, characters: Dict[str, Any]) -> List[str]:
        """Alias for export_character_scripts - for compatibility"""
        return await self.export_character_scripts(characters)
    
    async def generate_quest_scripts(self, quests: Dict[str, Any]) -> List[str]:
        """Alias for export_quest_scripts - for compatibility"""
        return await self.export_quest_scripts(quests)
    
    async def generate_game_management_scripts(self) -> List[str]:
        """Alias for export_game_management_scripts - for compatibility"""
        return await self.export_game_management_scripts()
    
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
    
    # Rest of the methods from the original file...
    async def _create_globaldata_script(self) -> str:
        """Create GlobalData autoload script"""
        
        content = '''extends Node

# Global game data autoload

var world_data: Dictionary = {}
var character_data: Dictionary = {}
var quest_data: Dictionary = {}
var game_config: Dictionary = {}

func _ready():
    load_all_data()

func load_all_data():
    world_data = load_json_file("res://data/world_spec.json")
    character_data = load_json_file("res://data/characters.json")
    quest_data = load_json_file("res://data/quests.json")
    game_config = load_json_file("res://data/game_config.json")
    
    print("Global data loaded successfully")

func load_json_file(file_path: String) -> Dictionary:
    var file = FileAccess.open(file_path, FileAccess.READ)
    if file:
        var json_string = file.get_as_text()
        file.close()
        
        var json = JSON.new()
        var parse_result = json.parse(json_string)
        if parse_result == OK:
            return json.data
        else:
            print("Error parsing JSON file: ", file_path)
            return {}
    else:
        print("Could not open file: ", file_path)
        return {}

func get_character_by_name(chname: String) -> Dictionary:
    if character_data.has("characters"):
        for character in character_data["characters"]:
            if character.get("name") == chname:
                return character
    return {}

func get_quest_by_id(quest_id: String) -> Dictionary:
    if quest_data.has("quests"):
        for quest in quest_data["quests"]:
            if quest.get("id") == quest_id:
                return quest
    return {}
'''
        
        script_file = self.scripts_dir / "GlobalData.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return "GlobalData.gd"
    
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

func setup_cyberpunk_atmosphere():
    print("Setting up cyberpunk atmosphere...")

func setup_fantasy_atmosphere():
    print("Setting up fantasy atmosphere...")

func setup_steampunk_atmosphere():
    print("Setting up steampunk atmosphere...")

func setup_default_atmosphere():
    print("Setting up default atmosphere...")
'''
        
        script_file = self.scripts_dir / f"{theme.capitalize()}Environment.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"{theme.capitalize()}Environment.gd"
    
    async def _create_world_manager_script(self) -> str:
        """Create world manager script"""
        
        content = GDSCRIPT_TEMPLATES['world_manager']
        
        script_file = self.scripts_dir / "WorldManager.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return "WorldManager.gd"
    
    async def _create_player_script(self) -> str:
        """Create player controller script"""
        
        content = '''extends CharacterBody3D

class_name Player

@export var speed: float = 5.0
@export var jump_velocity: float = 4.5

var gravity = ProjectSettings.get_setting("physics/3d/default_gravity")

func _ready():
    add_to_group("player")

func _physics_process(delta):
    # Add gravity
    if not is_on_floor():
        velocity.y -= gravity * delta

    # Handle jump
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity

    # Handle movement
    var input_dir = Input.get_vector("move_left", "move_right", "move_forward", "move_backward")
    var direction = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    if direction:
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        velocity.z = move_toward(velocity.z, 0, speed)

    move_and_slide()
'''
        
        script_file = self.scripts_dir / "Player.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return "Player.gd"
    
    async def _create_quest_manager_script(self, quests: Dict[str, Any]) -> str:
        """Create quest manager script"""
        
        content = '''extends Node

class_name QuestManager

var active_quests: Array = []
var completed_quests: Array = []

func _ready():
    print("Quest Manager initialized")

func start_quest(quest_id: String):
    print("Starting quest: ", quest_id)

func complete_quest(quest_id: String):
    print("Completing quest: ", quest_id)
'''
        
        script_file = self.scripts_dir / "QuestManager.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
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
    setup_interaction_area()

func setup_interaction_area():
    # Set up interaction area
    var interaction_area = Area3D.new()
    var collision_shape = CollisionShape3D.new()
    var shape = BoxShape3D.new()
    
    shape.size = Vector3(5, 4, 5)
    collision_shape.shape = shape
    
    interaction_area.add_child(collision_shape)
    add_child(interaction_area)
    
    interaction_area.body_entered.connect(_on_player_entered)
    interaction_area.body_exited.connect(_on_player_exited)

func _on_player_entered(body):
    if body.is_in_group("player"):
        print("Entered ", building_type, " area")

func _on_player_exited(body):
    if body.is_in_group("player"):
        print("Left ", building_type, " area")

func interact(player: Variant):
    print("Interacting with ", building_type)

func open_shop():
    print("Welcome to the shop!")

func enter_house():
    print("You enter the cozy house...")

func enter_tavern():
    print("Welcome to the tavern!")

func open_blacksmith():
    print("The blacksmith looks up from his anvil.")
'''
        
        script_file = self.scripts_dir / "Building.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
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
    if not get_tree().get_first_node_in_group("game_state"):
        add_to_group("game_state")

func change_state(new_state: State):
    previous_state = current_state
    current_state = new_state
    game_state_changed.emit(State.keys()[new_state])

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
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return "GameState.gd"
    
    async def _create_individual_quest_script(self, quest: Dict[str, Any], index: int) -> str:
        """Create individual quest script"""
        
        quest_id = quest.get('id', f'quest_{index}')
        quest_title = quest.get('title', f'Quest {index}')
        
        # Only create individual scripts for complex quests
        if not quest.get('objectives') and not quest.get('scripted_events'):
            return None
        
        quest_data_gdscript = self.python_to_gdscript_converter(quest)
        safe_quest_id = self._sanitize_class_name(quest_id)
        
        content = f'''extends Node

# Quest script for: {quest_title}
class_name Quest_{safe_quest_id}

var quest_data: Dictionary = {quest_data_gdscript}
var is_active: bool = false
var current_objective: int = 0
var objectives_completed: Array[bool] = []

func _ready():
    var objectives = quest_data.get("objectives", [])
    objectives_completed.resize(objectives.size())
    objectives_completed.fill(false)

func start_quest():
    is_active = true
    current_objective = 0
    print("Started quest: ", quest_data.get("title", "Unknown"))
    _on_quest_started()

func complete_objective(objective_index: int):
    if objective_index < objectives_completed.size():
        objectives_completed[objective_index] = true
        print("Completed objective: ", get_objective_text(objective_index))
        
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
        var obj = objectives[index]
        if typeof(obj) == TYPE_DICTIONARY:
            return obj.get("description", "")
        else:
            return str(obj)
    return ""

func _on_quest_started():
    pass

func _on_objective_advanced():
    pass

func _on_quest_completed():
    var rewards = quest_data.get("rewards", {{}})
    if rewards.has("experience"):
        var game_state = get_tree().get_first_node_in_group("game_state")
        if game_state:
            game_state.add_experience(rewards["experience"])
    
    if rewards.has("gold"):
        var game_state = get_tree().get_first_node_in_group("game_state")
        if game_state:
            game_state.add_gold(rewards["gold"])
'''
        
        script_file = self.scripts_dir / f"Quest_{safe_quest_id}.gd"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Quest_{safe_quest_id}.gd"
