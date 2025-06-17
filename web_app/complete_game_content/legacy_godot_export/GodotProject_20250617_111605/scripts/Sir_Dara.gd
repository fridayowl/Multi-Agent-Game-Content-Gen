extends NPC

# Specific script for Sir Dara

func _ready():
    super._ready()
    character_name = "Sir Dara"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific personality traits
    personality = {'primary_trait': 'Fierce', 'secondary_trait': 'Cautious', 'motivation': 'To discover truth', 'fear': 'Failure', 'quirk': 'Collects unusual items', 'speech_pattern': 'Speaks with confidence', 'alignment': 'Neutral Good', 'mood': 'Generally positive', 'secret': 'Has an interesting past', 'life_goal': 'To live meaningfully'}
    
    # Specific dialogue
    dialogue_lines = []
    
    # Specific relationships  
    relationships = [{'target_character': 'Master Brenna', 'relationship_type': 'Neighbor', 'relationship_strength': 6, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}, {'target_character': 'Sister Brenna', 'relationship_type': 'Rival', 'relationship_strength': 7, 'history': 'They know each other through their work in town', 'current_status': 'Neutral'}]

func interact(player: Player):
    # Custom interaction for Sir Dara
    super.interact(player)
    
    # Add specific behavior here
        print("Sir Dara nods at you.")

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
