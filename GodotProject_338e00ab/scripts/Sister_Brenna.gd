extends NPC

# Specific script for Sister Brenna

func _ready():
    super._ready()
    character_name = "Sister Brenna"
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
    "relationship_type": "Acquaintance",
    "relationship_strength": 5,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Sir Aldric",
    "relationship_type": "Friend",
    "relationship_strength": 8,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Lady Dara",
    "relationship_type": "Friend",
    "relationship_strength": 5,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Master Aldric",
    "relationship_type": "Acquaintance",
    "relationship_strength": 6,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
}
]

func interact(player: Variant):
    # Custom interaction for Sister Brenna
    super.interact(player)
    
    # Add specific behavior here
    print("Sister Brenna nods at you.")

func get_current_mood() -> String:
    # Simple mood system without personality traits
    return "neutral"
