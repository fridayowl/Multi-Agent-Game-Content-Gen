extends NPC

# Specific script for Brother Gareth

func _ready():
    super._ready()
    character_name = "Brother Gareth"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific personality traits
    personality = {'primary_trait': 'Honest', 'secondary_trait': 'Ambitious', 'motivation': 'To find adventure', 'fear': 'The unknown', 'quirk': 'Collects unusual items', 'speech_pattern': 'Speaks with confidence', 'alignment': 'Neutral Good', 'mood': 'Generally positive', 'secret': 'Has an interesting past', 'life_goal': 'To live meaningfully'}
    
    # Specific dialogue
    dialogue_lines = []
    
    # Specific relationships  
    relationships = [{'target_character': 'Sister Aldric', 'relationship_type': 'Ally', 'relationship_strength': 5, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}]

func interact(player: Player):
    # Custom interaction for Brother Gareth
    super.interact(player)
    
    # Add specific behavior here
        print("Brother Gareth nods at you.")

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
