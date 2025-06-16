#!/usr/bin/env python3
"""
Godot data types and structures
Defines the core data structures used throughout the Godot export system
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

@dataclass
class GodotNode:
    """Godot node definition"""
    name: str
    type: str
    properties: Dict[str, Any]
    script_path: Optional[str] = None
    children: List['GodotNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

@dataclass
class GodotScene:
    """Godot scene definition"""
    name: str
    root_node: GodotNode
    load_steps: int
    format_version: int = 3
    external_resources: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.external_resources is None:
            self.external_resources = []

@dataclass
class GodotScript:
    """Godot script definition"""
    name: str
    content: str
    class_name: Optional[str] = None
    extends: str = "Node"
    script_type: str = "gd"

@dataclass
class GodotResource:
    """Godot resource definition"""
    name: str
    type: str
    content: Dict[str, Any]
    file_extension: str = "tres"

@dataclass
class GodotExportManifest:
    """Complete export package manifest"""
    project_name: str
    godot_version: str
    export_timestamp: str
    content_summary: Dict[str, Any]
    file_structure: Dict[str, str]
    import_instructions: List[str]
    scene_files: List[str]
    script_files: List[str]
    resource_files: List[str]
    asset_files: List[str]

@dataclass
class GodotExportResult:
    """Result of Godot export operation"""
    status: str
    project_name: str
    project_path: str
    manifest: Optional[GodotExportManifest]
    output_directory: str
    godot_project_path: str
    import_ready: bool
    file_counts: Dict[str, int]
    error: Optional[str] = None

@dataclass
class GodotProjectSettings:
    """Godot project settings"""
    name: str
    main_scene: str
    features: List[str]
    rendering_method: str = "gl_compatibility"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'application': {
                'config/name': self.name,
                'run/main_scene': self.main_scene,
                'config/features': self.features
            },
            'rendering': {
                'renderer/rendering_method': self.rendering_method,
                'renderer/rendering_method.mobile': self.rendering_method
            }
        }

# Common node types and their default properties
GODOT_NODE_TEMPLATES = {
    'Node3D': {
        'transform': 'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)'
    },
    'CharacterBody3D': {
        'transform': 'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)'
    },
    'StaticBody3D': {
        'transform': 'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)'
    },
    'MeshInstance3D': {
        'transform': 'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)'
    },
    'CollisionShape3D': {
        'transform': 'Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)'
    },
    'Camera3D': {
        'transform': 'Transform3D(1, 0, 0, 0, 0.866025, 0.5, 0, -0.5, 0.866025, 0, 1.5, 1.5)'
    },
    'DirectionalLight3D': {
        'transform': 'Transform3D(0.707107, -0.5, 0.5, 0, 0.707107, 0.707107, -0.707107, -0.5, 0.5, 0, 10, 0)',
        'light_energy': 1.0
    }
}

# Common script templates
GDSCRIPT_TEMPLATES = {
    'player_controller': '''extends CharacterBody3D

@export var speed: float = 5.0
@export var jump_velocity: float = 4.5
@export var mouse_sensitivity: float = 0.002

@onready var camera: Camera3D = $Camera3D
@onready var interaction_ray: RayCast3D = $Camera3D/InteractionRay

var gravity = ProjectSettings.get_setting("physics/3d/default_gravity")

func _ready():
    Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _input(event):
    if event is InputEventMouseMotion:
        rotate_y(-event.relative.x * mouse_sensitivity)
        camera.rotate_x(-event.relative.y * mouse_sensitivity)
        camera.rotation.x = clamp(camera.rotation.x, -PI/2, PI/2)
    
    if event.is_action_pressed("interact"):
        try_interact()

func _physics_process(delta):
    if not is_on_floor():
        velocity.y -= gravity * delta
    
    if Input.is_action_just_pressed("ui_accept") and is_on_floor():
        velocity.y = jump_velocity
    
    var input_dir = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    var direction = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
    
    if direction:
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        velocity.z = move_toward(velocity.z, 0, speed)
    
    move_and_slide()

func try_interact():
    if interaction_ray.is_colliding():
        var collider = interaction_ray.get_collider()
        if collider.has_method("interact"):
            collider.interact(self)
''',
    
    'world_manager': '''extends Node3D

class_name WorldManager

@export var world_size: Vector2 = Vector2(40, 40)
@export var spawn_point: Vector3 = Vector3(0, 1, 0)

var npcs: Array[NPC] = []
var quest_manager: QuestManager

func _ready():
    setup_world()
    setup_npcs()
    setup_quests()
    print("World initialized successfully!")

func setup_world():
    var world_data = load_world_data()
    if world_data:
        print("World loaded: ", world_data.get("theme", "Unknown"))

func setup_npcs():
    var npc_nodes = get_tree().get_nodes_in_group("npcs")
    for npc_node in npc_nodes:
        if npc_node is NPC:
            npcs.append(npc_node)
    print("Found ", npcs.size(), " NPCs")

func setup_quests():
    quest_manager = QuestManager.new()
    add_child(quest_manager)

func load_world_data() -> Dictionary:
    var file = FileAccess.open("res://data/world_spec.json", FileAccess.READ)
    if file:
        var json_string = file.get_as_text()
        file.close()
        var json = JSON.new()
        var parse_result = json.parse(json_string)
        if parse_result == OK:
            return json.data
    return {}

func get_npc_by_name(npc_name: String) -> NPC:
    for npc in npcs:
        if npc.character_name == npc_name:
            return npc
    return null
''',
    
    'npc_base': '''extends CharacterBody3D

class_name NPC

@export var character_name: String = ""
@export var character_data: Dictionary = {}

var personality: Dictionary = {}
var relationships: Dictionary = {}
var dialogue_lines: Array[String] = []

func _ready():
    load_character_data()
    add_to_group("npcs")

func load_character_data():
    # Override in derived classes or load from JSON
    pass

func interact(player: Player):
    print("Interacting with ", character_name)
    start_dialogue(player)

func start_dialogue(player: Player):
    if dialogue_lines.size() > 0:
        var random_line = dialogue_lines[randi() % dialogue_lines.size()]
        show_dialogue(random_line)
    else:
        show_dialogue("Hello there!")

func show_dialogue(text: String):
    print(character_name + ": " + text)

func get_relationship_with(other_character: String) -> Dictionary:
    return relationships.get(other_character, {})

func has_quest() -> bool:
    return character_data.get("has_quest", false)
''',
    
    'quest_manager': '''extends Node

class_name QuestManager

var active_quests: Array[Dictionary] = []
var completed_quests: Array[Dictionary] = []
var available_quests: Array[Dictionary] = []

func _ready():
    load_quest_data()

func load_quest_data():
    var file = FileAccess.open("res://data/quests.json", FileAccess.READ)
    if file:
        var json_string = file.get_as_text()
        file.close()
        var json = JSON.new()
        var parse_result = json.parse(json_string)
        if parse_result == OK:
            var quest_data = json.data
            if quest_data.has("quests"):
                for quest in quest_data["quests"]:
                    available_quests.append(quest)
    print("Loaded ", available_quests.size(), " quests")

func start_quest(quest_id: String) -> bool:
    var quest = find_quest_by_id(quest_id)
    if quest and not is_quest_active(quest_id):
        active_quests.append(quest)
        print("Started quest: ", quest.get("title", "Unknown"))
        return true
    return false

func complete_quest(quest_id: String) -> bool:
    for i in range(active_quests.size()):
        if active_quests[i].get("id") == quest_id:
            var quest = active_quests[i]
            completed_quests.append(quest)
            active_quests.remove_at(i)
            print("Completed quest: ", quest.get("title", "Unknown"))
            return true
    return false

func find_quest_by_id(quest_id: String) -> Dictionary:
    for quest in available_quests:
        if quest.get("id") == quest_id:
            return quest
    return {}

func is_quest_active(quest_id: String) -> bool:
    for quest in active_quests:
        if quest.get("id") == quest_id:
            return true
    return false
'''
}