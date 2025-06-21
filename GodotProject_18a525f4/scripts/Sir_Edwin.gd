extends NPC

# Specific script for Sir Edwin

func _ready():
    super._ready()
    character_name = "Sir Edwin"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific dialogue - FIXED SYNTAX  
    var dialogue_array = []
    for line in dialogue_array:
        add_dialogue_line(str(line))
    
    # Specific relationships - FIXED SYNTAX
    relationships = [
    {
    "target_character": "Brother Cedric",
    "relationship_type": "Acquaintance",
    "relationship_strength": 5,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Master Aldric",
    "relationship_type": "Rival",
    "relationship_strength": 6,
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
    "relationship_strength": 5,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
}
]

func interact(player: Variant):
    # Custom interaction for Sir Edwin
    super.interact(player)
    
    # Add specific behavior here
    print("Sir Edwin nods at you.")

func get_current_mood() -> String:
    # Simple mood system without personality traits
    return "neutral"
