extends NPC

# Specific script for Fiona 181

func _ready():
    super._ready()
    character_name = "Fiona 181"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific personality traits
    personality = {'primary_trait': 'Clever', 'secondary_trait': 'Ambitious', 'motivation': 'To seek knowledge', 'fear': 'Failure', 'quirk': 'Never sits still', 'speech_pattern': 'Speaks with confidence', 'alignment': 'Neutral Good', 'mood': 'Generally positive', 'secret': 'Has an interesting past', 'life_goal': 'To live meaningfully'}
    
    # Specific dialogue
    dialogue_lines = []
    
    # Specific relationships  
    relationships = [{'target_character': 'Brother Edwin', 'relationship_type': 'Ally', 'relationship_strength': 8, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}, {'target_character': 'Sir Fiona', 'relationship_type': 'Rival', 'relationship_strength': 5, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}, {'target_character': 'Brother Brenna', 'relationship_type': 'Rival', 'relationship_strength': 6, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}, {'target_character': 'Lady Hilda', 'relationship_type': 'Ally', 'relationship_strength': 4, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}]

func interact(player: Player):
    # Custom interaction for Fiona 181
    super.interact(player)
    
    # Add specific behavior here
        print("Fiona 181 nods at you.")

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
