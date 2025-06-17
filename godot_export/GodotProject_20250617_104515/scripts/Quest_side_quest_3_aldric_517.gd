extends Node

# Quest script for: Personal Favor
class_name Quest_side_quest_3_aldric_517

var quest_data: Dictionary = {'id': 'side_quest_3_aldric_517', 'title': 'Personal Favor', 'description': 'Aldric 517 needs help with a personal matter.', 'summary': 'Help Aldric 517 with personal favor', 'giver_npc': 'Aldric 517', 'objectives': [{'id': 'side_quest_3_obj_1', 'description': 'Listen to the problem', 'type': 'talk_to_npc', 'target': 'Aldric 517', 'quantity': 1, 'optional': False, 'prerequisites': None}, {'id': 'side_quest_3_obj_2', 'description': 'Help solve it', 'type': 'talk_to_npc', 'target': 'Aldric 517', 'quantity': 1, 'optional': False, 'prerequisites': None}, {'id': 'side_quest_3_obj_3', 'description': 'Return for thanks', 'type': 'talk_to_npc', 'target': 'Aldric 517', 'quantity': 1, 'optional': False, 'prerequisites': None}], 'rewards': {'experience': 77, 'gold': 32, 'items': ['Thank You Gift'], 'relationship_changes': None}, 'prerequisites': None, 'level_requirement': 1, 'estimated_duration': '15-30 minutes', 'quest_type': 'side', 'interconnected_quests': ['main_quest_2_brother_aldric', 'side_quest_2_brother_aldric'], 'narrative_importance': 'low'}
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
