extends CharacterBody3D

class_name NPC

@export var character_name: String = ""
@export var character_data: Dictionary = {}

var personality: Dictionary = {}
var relationships: Dictionary = {}
var dialogue_lines: Array[String] = []

func _ready():
    load_character_data()
    add_to_group("npcs")


func load_character_data():
    # Load character data from pipeline
    var characters_data = {
  "status": "success",
  "character_count": 5,
  "output_directory": "generated_characters",
  "manifest_file": "generated_characters/character_manifest.json",
  "ai_enhanced": false,
  "fallback_generation": true,
  "characters": [
    {
      "id": "master_brenna_623e6415_0",
      "name": "Master Brenna",
      "title": "The Honest Herbalist",
      "description": "A 24-year-old Herbalist with a honest nature.",
      "backstory": "Master Brenna has worked as a Herbalist for many years.",
      "personality": {
        "primary_trait": "Honest",
        "secondary_trait": "Ambitious",
        "motivation": "To seek knowledge",
        "fear": "Being alone",
        "quirk": "Collects unusual items",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 2,
        "health": 66,
        "strength": 12,
        "intelligence": 12,
        "charisma": 12,
        "dexterity": 13,
        "wisdom": 11,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Sister Aldric",
          "relationship_type": "Friend",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sir Gareth",
          "relationship_type": "Neighbor",
          "relationship_strength": 3,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "master brenna_greeting",
          "text": "Greetings! I'm Master Brenna, the local Herbalist.",
          "speaker": "Master Brenna",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "master brenna_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "master brenna_role",
          "text": "As a Herbalist, I to seek knowledge.",
          "speaker": "Master Brenna",
          "options": [
            {
              "id": "role_continue",
              "text": "That's interesting",
              "next_node_id": null,
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": false,
          "is_farewell": false,
          "quest_related": false
        }
      ],
      "inventory": [
        "Personal belongings",
        "Leather pouch",
        "Simple clothes"
      ],
      "location": "shop",
      "role": "Herbalist",
      "quest_involvement": [],
      "age": 24,
      "appearance": "A 24-year-old Herbalist with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "a0340c7f-a886-4c9c-ac2e-9199f2f25e21"
    },
    {
      "id": "sister_hilda_623e6415_1",
      "name": "Sister Hilda",
      "title": "The Clever Clerk",
      "description": "A 48-year-old Clerk with a clever nature.",
      "backstory": "Sister Hilda has worked as a Clerk for many years.",
      "personality": {
        "primary_trait": "Clever",
        "secondary_trait": "Mysterious",
        "motivation": "To find adventure",
        "fear": "Failure",
        "quirk": "Speaks to animals",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 2,
        "health": 66,
        "strength": 12,
        "intelligence": 14,
        "charisma": 12,
        "dexterity": 12,
        "wisdom": 12,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Sir Aldric",
          "relationship_type": "Acquaintance",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sir Gareth",
          "relationship_type": "Acquaintance",
          "relationship_strength": 8,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "sister hilda_greeting",
          "text": "Greetings! I'm Sister Hilda, the local Clerk.",
          "speaker": "Sister Hilda",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "sister hilda_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "sister hilda_role",
          "text": "As a Clerk, I to find adventure.",
          "speaker": "Sister Hilda",
          "options": [
            {
              "id": "role_continue",
              "text": "That's interesting",
              "next_node_id": null,
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": false,
          "is_farewell": false,
          "quest_related": false
        }
      ],
      "inventory": [
        "Personal belongings",
        "Leather pouch",
        "Simple clothes"
      ],
      "location": "house",
      "role": "Clerk",
      "quest_involvement": [],
      "age": 48,
      "appearance": "A 48-year-old Clerk with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "38d117ce-c7d9-4195-8a60-4acf1160fdce"
    },
    {
      "id": "sir_aldric_623e6415_2",
      "name": "Sir Aldric",
      "title": "The Gentle Noble",
      "description": "A 56-year-old Noble with a gentle nature.",
      "backstory": "Sir Aldric has worked as a Noble for many years.",
      "personality": {
        "primary_trait": "Gentle",
        "secondary_trait": "Witty",
        "motivation": "To discover truth",
        "fear": "The unknown",
        "quirk": "Speaks to animals",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 4,
        "health": 72,
        "strength": 11,
        "intelligence": 12,
        "charisma": 12,
        "dexterity": 12,
        "wisdom": 14,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Sister Hilda",
          "relationship_type": "Acquaintance",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sir Gareth",
          "relationship_type": "Friend",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "sir aldric_greeting",
          "text": "Greetings! I'm Sir Aldric, the local Noble.",
          "speaker": "Sir Aldric",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "sir aldric_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "sir aldric_role",
          "text": "As a Noble, I to discover truth.",
          "speaker": "Sir Aldric",
          "options": [
            {
              "id": "role_continue",
              "text": "That's interesting",
              "next_node_id": null,
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": false,
          "is_farewell": false,
          "quest_related": false
        }
      ],
      "inventory": [
        "Personal belongings",
        "Leather pouch",
        "Simple clothes"
      ],
      "location": "house",
      "role": "Noble",
      "quest_involvement": [],
      "age": 56,
      "appearance": "A 56-year-old Noble with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "cde8777f-82f3-4122-abae-e0ccd26014b4"
    },
    {
      "id": "sister_aldric_623e6415_3",
      "name": "Sister Aldric",
      "title": "The Compassionate Trader",
      "description": "A 56-year-old Trader with a compassionate nature.",
      "backstory": "Sister Aldric has worked as a Trader for many years.",
      "personality": {
        "primary_trait": "Compassionate",
        "secondary_trait": "Patient",
        "motivation": "To protect others",
        "fear": "Being alone",
        "quirk": "Always carries a lucky charm",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 10,
        "health": 90,
        "strength": 11,
        "intelligence": 12,
        "charisma": 12,
        "dexterity": 12,
        "wisdom": 14,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Master Brenna",
          "relationship_type": "Friend",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sir Gareth",
          "relationship_type": "Neighbor",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "sister aldric_greeting",
          "text": "Greetings! I'm Sister Aldric, the local Trader.",
          "speaker": "Sister Aldric",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "sister aldric_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "sister aldric_role",
          "text": "As a Trader, I to protect others.",
          "speaker": "Sister Aldric",
          "options": [
            {
              "id": "role_continue",
              "text": "That's interesting",
              "next_node_id": null,
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": false,
          "is_farewell": false,
          "quest_related": false
        }
      ],
      "inventory": [
        "Personal belongings",
        "Leather pouch",
        "Simple clothes"
      ],
      "location": "shop",
      "role": "Trader",
      "quest_involvement": [],
      "age": 56,
      "appearance": "A 56-year-old Trader with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "3b535d85-bbc6-4b5f-ad28-7fe656ca0045"
    },
    {
      "id": "sir_gareth_623e6415_4",
      "name": "Sir Gareth",
      "title": "The Jovial Family Head",
      "description": "A 41-year-old Family Head with a jovial nature.",
      "backstory": "Sir Gareth has worked as a Family Head for many years.",
      "personality": {
        "primary_trait": "Jovial",
        "secondary_trait": "Patient",
        "motivation": "To protect others",
        "fear": "The unknown",
        "quirk": "Always carries a lucky charm",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 6,
        "health": 78,
        "strength": 12,
        "intelligence": 12,
        "charisma": 12,
        "dexterity": 12,
        "wisdom": 12,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Master Brenna",
          "relationship_type": "Neighbor",
          "relationship_strength": 3,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sister Hilda",
          "relationship_type": "Acquaintance",
          "relationship_strength": 8,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sir Aldric",
          "relationship_type": "Friend",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sister Aldric",
          "relationship_type": "Neighbor",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "sir gareth_greeting",
          "text": "Greetings! I'm Sir Gareth, the local Family Head.",
          "speaker": "Sir Gareth",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "sir gareth_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "sir gareth_role",
          "text": "As a Family Head, I to protect others.",
          "speaker": "Sir Gareth",
          "options": [
            {
              "id": "role_continue",
              "text": "That's interesting",
              "next_node_id": null,
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": false,
          "is_farewell": false,
          "quest_related": false
        }
      ],
      "inventory": [
        "Personal belongings",
        "Leather pouch",
        "Simple clothes"
      ],
      "location": "shop",
      "role": "Family Head",
      "quest_involvement": [],
      "age": 41,
      "appearance": "A 41-year-old Family Head with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "1fac4206-3346-4542-b8f1-371fb901db02"
    }
  ]
}
    
    # Find this character's data
    if characters_data.has("characters"):
        for char_data in characters_data["characters"]:
            if char_data.get("name") == character_name:
                character_data = char_data
                personality = char_data.get("personality", {})
                relationships = char_data.get("relationships", {})
                
                # Load dialogue lines
                if char_data.has("dialogue"):
                    dialogue_lines = char_data["dialogue"]
                elif char_data.has("personality"):
                    # Generate some basic dialogue based on personality
                    dialogue_lines = generate_personality_dialogue(char_data["personality"])
                
                break

func generate_personality_dialogue(personality_data: Dictionary) -> Array[String]:
    var lines: Array[String] = []
    
    # Generate dialogue based on personality traits
    if personality_data.get("friendly", 0) > 0.7:
        lines.append("Hello there! Nice to meet you!")
        lines.append("What a lovely day it is!")
        lines.append("How are you doing today?")
    
    if personality_data.get("helpful", 0) > 0.7:
        lines.append("Is there anything I can help you with?")
        lines.append("Let me know if you need assistance!")
    
    if personality_data.get("mysterious", 0) > 0.7:
        lines.append("There are things you don't yet understand...")
        lines.append("The truth is not always what it seems.")
    
    if lines.is_empty():
        lines.append("Hello.")
        lines.append("Good day.")
    
    return lines


func interact(player: Player):
    print("Interacting with ", character_name)
    start_dialogue(player)

func start_dialogue(player: Player):
    if dialogue_lines.size() > 0:
        var random_line = dialogue_lines[randi() % dialogue_lines.size()]
        show_dialogue(random_line)
    else:
        show_dialogue("Hello there!")

func show_dialogue(text: String):
    print(character_name + ": " + text)

func get_relationship_with(other_character: String) -> Dictionary:
    return relationships.get(other_character, {})

func has_quest() -> bool:
    return character_data.get("has_quest", false)
