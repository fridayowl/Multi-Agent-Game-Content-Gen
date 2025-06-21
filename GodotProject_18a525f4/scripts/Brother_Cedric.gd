extends NPC

# Specific script for Brother Cedric

func _ready():
    super._ready()
    character_name = "Brother Cedric"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific dialogue - FIXED SYNTAX  
    var dialogue_array = []
    for line in dialogue_array:
        add_dialogue_line(str(line))
    
    # Specific relationships - FIXED SYNTAX
    relationships = [
    {
    "target_character": "Sir Edwin",
    "relationship_type": "Acquaintance",
    "relationship_strength": 5,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Master Aldric",
    "relationship_type": "Colleague",
    "relationship_strength": 3,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Brother Aldric",
    "relationship_type": "Friend",
    "relationship_strength": 3,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Lady Hilda",
    "relationship_type": "Neighbor",
    "relationship_strength": 3,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
}
]

func interact(player: Variant):
    # Custom interaction for Brother Cedric
    super.interact(player)
    
    # Add specific behavior here
    print("Brother Cedric nods at you.")

func get_current_mood() -> String:
    # Simple mood system without personality traits
    return "neutral"
