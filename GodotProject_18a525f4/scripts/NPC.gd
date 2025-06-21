extends CharacterBody3D

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
