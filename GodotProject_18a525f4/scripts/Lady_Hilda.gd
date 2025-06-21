extends NPC

# Specific script for Lady Hilda

func _ready():
    super._ready()
    character_name = "Lady Hilda"
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
    "relationship_type": "Neighbor",
    "relationship_strength": 5,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Brother Cedric",
    "relationship_type": "Neighbor",
    "relationship_strength": 3,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Master Aldric",
    "relationship_type": "Ally",
    "relationship_strength": 7,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
},
    {
    "target_character": "Brother Aldric",
    "relationship_type": "Ally",
    "relationship_strength": 3,
    "history": "They know each other through their work in town",
    "current_status": "Neutral"
}
]

func interact(player: Variant):
    # Custom interaction for Lady Hilda
    super.interact(player)
    
    # Add specific behavior here
    print("Lady Hilda nods at you.")

func get_current_mood() -> String:
    # Simple mood system without personality traits
    return "neutral"
