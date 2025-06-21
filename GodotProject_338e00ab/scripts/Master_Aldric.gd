extends NPC

# Specific script for Master Aldric

func _ready():
    super._ready()
    character_name = "Master Aldric"
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
    "relationship_strength": 6,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Sir Aldric",
    "relationship_type": "Ally",
    "relationship_strength": 7,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Lady Dara",
    "relationship_type": "Neighbor",
    "relationship_strength": 4,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Sister Brenna",
    "relationship_type": "Acquaintance",
    "relationship_strength": 6,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
}
]

func interact(player: Variant):
    # Custom interaction for Master Aldric
    super.interact(player)
    
    # Add specific behavior here
    print("Master Aldric nods at you.")

func get_current_mood() -> String:
    # Simple mood system without personality traits
    return "neutral"
