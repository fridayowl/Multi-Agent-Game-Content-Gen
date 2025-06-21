extends Node

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
