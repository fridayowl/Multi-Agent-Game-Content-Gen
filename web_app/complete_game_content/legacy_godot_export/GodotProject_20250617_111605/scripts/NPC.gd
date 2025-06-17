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
      "id": "master_aldric_3e072fec_0",
      "name": "Master Aldric",
      "title": "The Brave Noble",
      "description": "A 55-year-old Noble with a brave nature.",
      "backstory": "Master Aldric has worked as a Noble for many years.",
      "personality": {
        "primary_trait": "Brave",
        "secondary_trait": "Witty",
        "motivation": "To discover truth",
        "fear": "Losing control",
        "quirk": "Always carries a lucky charm",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 9,
        "health": 87,
        "strength": 13,
        "intelligence": 12,
        "charisma": 12,
        "dexterity": 12,
        "wisdom": 14,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Aldric 227",
          "relationship_type": "Rival",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "master aldric_greeting",
          "text": "Greetings! I'm Master Aldric, the local Noble.",
          "speaker": "Master Aldric",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "master aldric_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "master aldric_role",
          "text": "As a Noble, I to discover truth.",
          "speaker": "Master Aldric",
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
      "age": 55,
      "appearance": "A 55-year-old Noble with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "dcdf7def-95a3-4da0-9c23-8a0211ffb428"
    },
    {
      "id": "sir_dara_3e072fec_1",
      "name": "Sir Dara",
      "title": "The Fierce Bartender",
      "description": "A 52-year-old Bartender with a fierce nature.",
      "backstory": "Sir Dara has worked as a Bartender for many years.",
      "personality": {
        "primary_trait": "Fierce",
        "secondary_trait": "Cautious",
        "motivation": "To discover truth",
        "fear": "Failure",
        "quirk": "Collects unusual items",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 8,
        "health": 84,
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
          "relationship_type": "Neighbor",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sister Brenna",
          "relationship_type": "Rival",
          "relationship_strength": 7,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "sir dara_greeting",
          "text": "Greetings! I'm Sir Dara, the local Bartender.",
          "speaker": "Sir Dara",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "sir dara_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "sir dara_role",
          "text": "As a Bartender, I to discover truth.",
          "speaker": "Sir Dara",
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
      "location": "tavern",
      "role": "Bartender",
      "quest_involvement": [],
      "age": 52,
      "appearance": "A 52-year-old Bartender with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "c64ead6c-3300-442e-a800-7d6a3a4f6893"
    },
    {
      "id": "master_brenna_3e072fec_2",
      "name": "Master Brenna",
      "title": "The Compassionate Innkeeper",
      "description": "A 51-year-old Innkeeper with a compassionate nature.",
      "backstory": "Master Brenna has worked as a Innkeeper for many years.",
      "personality": {
        "primary_trait": "Compassionate",
        "secondary_trait": "Curious",
        "motivation": "To build something lasting",
        "fear": "Losing control",
        "quirk": "Never sits still",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 1,
        "health": 63,
        "strength": 11,
        "intelligence": 12,
        "charisma": 12,
        "dexterity": 12,
        "wisdom": 14,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Sir Dara",
          "relationship_type": "Neighbor",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "master brenna_greeting",
          "text": "Greetings! I'm Master Brenna, the local Innkeeper.",
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
          "text": "As a Innkeeper, I to build something lasting.",
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
      "location": "tavern",
      "role": "Innkeeper",
      "quest_involvement": [],
      "age": 51,
      "appearance": "A 51-year-old Innkeeper with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "0f7056f5-f5c3-46ed-8feb-afd6c30da51b"
    },
    {
      "id": "sister_brenna_3e072fec_3",
      "name": "Sister Brenna",
      "title": "The Determined Scholar",
      "description": "A 32-year-old Scholar with a determined nature.",
      "backstory": "Sister Brenna has worked as a Scholar for many years.",
      "personality": {
        "primary_trait": "Determined",
        "secondary_trait": "Practical",
        "motivation": "To discover truth",
        "fear": "Being misunderstood",
        "quirk": "Speaks to animals",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 5,
        "health": 75,
        "strength": 12,
        "intelligence": 12,
        "charisma": 12,
        "dexterity": 12,
        "wisdom": 12,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Sir Dara",
          "relationship_type": "Rival",
          "relationship_strength": 7,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Aldric 227",
          "relationship_type": "Rival",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "sister brenna_greeting",
          "text": "Greetings! I'm Sister Brenna, the local Scholar.",
          "speaker": "Sister Brenna",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "sister brenna_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "sister brenna_role",
          "text": "As a Scholar, I to discover truth.",
          "speaker": "Sister Brenna",
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
        "Books",
        "Quill and ink",
        "Research notes",
        "Leather pouch"
      ],
      "location": "market",
      "role": "Scholar",
      "quest_involvement": [],
      "age": 32,
      "appearance": "A 32-year-old Scholar with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "4332f8ff-d0a2-4911-ba62-15f421032f35"
    },
    {
      "id": "aldric_227_3e072fec_4",
      "name": "Aldric 227",
      "title": "The Honest Servant",
      "description": "A 36-year-old Servant with a honest nature.",
      "backstory": "Aldric 227 has worked as a Servant for many years.",
      "personality": {
        "primary_trait": "Honest",
        "secondary_trait": "Practical",
        "motivation": "To discover truth",
        "fear": "Being misunderstood",
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
        "strength": 12,
        "intelligence": 12,
        "charisma": 12,
        "dexterity": 12,
        "wisdom": 12,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Master Aldric",
          "relationship_type": "Rival",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sister Brenna",
          "relationship_type": "Rival",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "aldric 227_greeting",
          "text": "Greetings! I'm Aldric 227, the local Servant.",
          "speaker": "Aldric 227",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "aldric 227_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "aldric 227_role",
          "text": "As a Servant, I to discover truth.",
          "speaker": "Aldric 227",
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
      "location": "blacksmith",
      "role": "Servant",
      "quest_involvement": [],
      "age": 36,
      "appearance": "A 36-year-old Servant with distinctive features.",
      "voice_description": "Speaks with confidence",
      "unique_id": "06d7fa51-5025-4e7d-ab79-963430746f69"
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
