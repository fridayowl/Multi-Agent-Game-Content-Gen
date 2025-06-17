extends Node3D

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
