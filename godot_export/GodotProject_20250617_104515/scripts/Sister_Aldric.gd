extends NPC

# Specific script for Sister Aldric

func _ready():
    super._ready()
    character_name = "Sister Aldric"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific personality traits
    personality = {'primary_trait': 'Eccentric', 'secondary_trait': 'Energetic', 'motivation': 'To protect others', 'fear': 'Being alone', 'quirk': 'Always hums while working', 'speech_pattern': 'Speaks with confidence', 'alignment': 'Neutral Good', 'mood': 'Generally positive', 'secret': 'Has an interesting past', 'life_goal': 'To live meaningfully'}
    
    # Specific dialogue
    dialogue_lines = []
    
    # Specific relationships  
    relationships = [{'target_character': 'Brother Hilda', 'relationship_type': 'Friend', 'relationship_strength': 7, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}]

func interact(player: Player):
    # Custom interaction for Sister Aldric
    super.interact(player)
    
    # Add specific behavior here
        print("Sister Aldric nods at you.")

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
