extends Resource

class_name CharacterData

@export var character_name: String = ""
@export var personality: Dictionary = {}
@export var dialogue_lines: Array[String] = []
@export var relationships: Dictionary = {}
@export var stats: Dictionary = {}
@export var inventory: Array[String] = []
@export var location: String = ""

func _init():
    pass



func add_dialogue_line(line: String):
    if line not in dialogue_lines:
        dialogue_lines.append(line)

func get_relationship_with(character: String) -> String:
    return relationships.get(character, "neutral")
