extends Node

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
