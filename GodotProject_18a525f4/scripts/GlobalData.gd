extends Node

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
