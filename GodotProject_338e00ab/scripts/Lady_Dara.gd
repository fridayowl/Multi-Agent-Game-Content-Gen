extends NPC

# Specific script for Lady Dara

func _ready():
    super._ready()
    character_name = "Lady Dara"
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
    "relationship_type": "Neighbor",
    "relationship_strength": 8,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Sir Aldric",
    "relationship_type": "Acquaintance",
    "relationship_strength": 8,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Sister Brenna",
    "relationship_type": "Friend",
    "relationship_strength": 5,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Master Aldric",
    "relationship_type": "Neighbor",
    "relationship_strength": 4,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
}
]

func interact(player: Variant):
    # Custom interaction for Lady Dara
    super.interact(player)
    
    # Add specific behavior here
    print("Lady Dara nods at you.")

func get_current_mood() -> String:
    # Simple mood system without personality traits
    return "neutral"
