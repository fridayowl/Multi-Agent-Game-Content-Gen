extends Node

class_name QuestManager

var active_quests: Array = []
var completed_quests: Array = []

func _ready():
    print("Quest Manager initialized")

func start_quest(quest_id: String):
    print("Starting quest: ", quest_id)

func complete_quest(quest_id: String):
    print("Completing quest: ", quest_id)
