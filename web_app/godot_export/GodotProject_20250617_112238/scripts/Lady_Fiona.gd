extends NPC

# Specific script for Lady Fiona

func _ready():
    super._ready()
    character_name = "Lady Fiona"
    setup_specific_behavior()

func setup_specific_behavior():
    # Specific personality traits
    personality = {'primary_trait': 'Clever', 'secondary_trait': 'Curious', 'motivation': 'To discover truth', 'fear': 'Failure', 'quirk': 'Always hums while working', 'speech_pattern': 'Speaks with confidence', 'alignment': 'Neutral Good', 'mood': 'Generally positive', 'secret': 'Has an interesting past', 'life_goal': 'To live meaningfully'}
    
    # Specific dialogue
    dialogue_lines = []
    
    # Specific relationships  
    relationships = []

func interact(player: Player):
    # Custom interaction for Lady Fiona
    super.interact(player)
    
    # Add specific behavior here
        print("Lady Fiona nods at you.")

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
