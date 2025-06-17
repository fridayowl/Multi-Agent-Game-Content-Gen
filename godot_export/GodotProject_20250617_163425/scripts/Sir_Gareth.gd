extends NPC

# Specific script for Sir Gareth

func _ready():
    super._ready()
    character_name = "Sir Gareth"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific personality traits
    personality = {'primary_trait': 'Jovial', 'secondary_trait': 'Patient', 'motivation': 'To protect others', 'fear': 'The unknown', 'quirk': 'Always carries a lucky charm', 'speech_pattern': 'Speaks with confidence', 'alignment': 'Neutral Good', 'mood': 'Generally positive', 'secret': 'Has an interesting past', 'life_goal': 'To live meaningfully'}
    
    # Specific dialogue
    dialogue_lines = []
    
    # Specific relationships  
    relationships = [{'target_character': 'Master Brenna', 'relationship_type': 'Neighbor', 'relationship_strength': 3, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}, {'target_character': 'Sister Hilda', 'relationship_type': 'Acquaintance', 'relationship_strength': 8, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}, {'target_character': 'Sir Aldric', 'relationship_type': 'Friend', 'relationship_strength': 5, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}, {'target_character': 'Sister Aldric', 'relationship_type': 'Neighbor', 'relationship_strength': 5, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}]

func interact(player: Player):
    # Custom interaction for Sir Gareth
    super.interact(player)
    
    # Add specific behavior here
        print("Sir Gareth nods at you.")

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
