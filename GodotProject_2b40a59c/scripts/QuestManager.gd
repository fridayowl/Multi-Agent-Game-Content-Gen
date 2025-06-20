extends Node

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
