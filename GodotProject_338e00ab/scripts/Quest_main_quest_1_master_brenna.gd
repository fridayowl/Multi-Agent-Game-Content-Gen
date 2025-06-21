extends Node

# Quest script for: The Village Crisis
class_name Quest_main_quest_1_master_brenna

var quest_data: Dictionary = {
    "id": "main_quest_1_master_brenna",
    "title": "The Village Crisis",
    "description": "Master Brenna needs help resolving a crisis that threatens the village.",
    "summary": "Help Master Brenna with the village crisis",
    "giver_npc": "Master Brenna",
    "objectives": [
    {
    "id": "main_quest_1_obj_1",
    "description": "Investigate the problem",
    "type": "investigate",
    "target": "location",
    "quantity": 1,
    "optional": false,
    "prerequisites": null
},
    {
    "id": "main_quest_1_obj_2",
    "description": "Gather information from villagers",
    "type": "investigate",
    "target": "location",
    "quantity": 1,
    "optional": false,
    "prerequisites": null
},
    {
    "id": "main_quest_1_obj_3",
    "description": "Find a solution",
    "type": "investigate",
    "target": "location",
    "quantity": 1,
    "optional": false,
    "prerequisites": null
},
    {
    "id": "main_quest_1_obj_4",
    "description": "Report back",
    "type": "investigate",
    "target": "Master Brenna",
    "quantity": 1,
    "optional": false,
    "prerequisites": null
}
],
    "rewards": {
    "experience": 156,
    "gold": 65,
    "items": ["Quest Item 1"],
    "relationship_changes": null
},
    "prerequisites": null,
    "level_requirement": 1,
    "estimated_duration": "15-30 minutes",
    "quest_type": "main",
    "interconnected_quests": ["main_quest_2_sir_aldric"],
    "narrative_importance": "high"
}
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
    var rewards = quest_data.get("rewards", {})
    if rewards.has("experience"):
        var game_state = get_tree().get_first_node_in_group("game_state")
        if game_state:
            game_state.add_experience(rewards["experience"])
    
    if rewards.has("gold"):
        var game_state = get_tree().get_first_node_in_group("game_state")
        if game_state:
            game_state.add_gold(rewards["gold"])
