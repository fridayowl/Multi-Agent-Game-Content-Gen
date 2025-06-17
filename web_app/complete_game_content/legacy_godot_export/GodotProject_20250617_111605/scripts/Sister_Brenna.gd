extends NPC

# Specific script for Sister Brenna

func _ready():
    super._ready()
    character_name = "Sister Brenna"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific personality traits
    personality = {'primary_trait': 'Determined', 'secondary_trait': 'Practical', 'motivation': 'To discover truth', 'fear': 'Being misunderstood', 'quirk': 'Speaks to animals', 'speech_pattern': 'Speaks with confidence', 'alignment': 'Neutral Good', 'mood': 'Generally positive', 'secret': 'Has an interesting past', 'life_goal': 'To live meaningfully'}
    
    # Specific dialogue
    dialogue_lines = []
    
    # Specific relationships  
    relationships = [{'target_character': 'Sir Dara', 'relationship_type': 'Rival', 'relationship_strength': 7, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}, {'target_character': 'Aldric 227', 'relationship_type': 'Rival', 'relationship_strength': 6, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}]

func interact(player: Player):
    # Custom interaction for Sister Brenna
    super.interact(player)
    
    # Add specific behavior here
        print("Sister Brenna nods at you.")

func get_current_mood() -> String:
    # Dynamic mood based on personality
    var traits = personality
    if traits.get("friendly", 0) > 0.8:
        return "cheerful"
    elif traits.get("mysterious", 0) > 0.7:
        return "enigmatic"  
    elif traits.get("grumpy", 0) > 0.6:
        return "irritated"
    else:
        return "neutral"
