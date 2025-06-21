extends NPC

# Specific script for Sir Aldric

func _ready():
    super._ready()
    character_name = "Sir Aldric"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific dialogue - FIXED SYNTAX  
    var dialogue_array = []
    for line in dialogue_array:
        add_dialogue_line(str(line))
    
    # Specific relationships - FIXED SYNTAX
    relationships = [
    {
    "target_character": "Master Brenna",
    "relationship_type": "Colleague",
    "relationship_strength": 7,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Lady Dara",
    "relationship_type": "Acquaintance",
    "relationship_strength": 8,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Sister Brenna",
    "relationship_type": "Friend",
    "relationship_strength": 8,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Master Aldric",
    "relationship_type": "Ally",
    "relationship_strength": 7,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
}
]

func interact(player: Variant):
    # Custom interaction for Sir Aldric
    super.interact(player)
    
    # Add specific behavior here
    print("Sir Aldric nods at you.")

func get_current_mood() -> String:
    # Simple mood system without personality traits
    return "neutral"
