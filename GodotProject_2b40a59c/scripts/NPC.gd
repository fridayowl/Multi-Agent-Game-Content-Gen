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
  "unique_personalities": 5,
  "total_relationships": 20,
  "total_dialogue_nodes": 10,
  "characters": [
    {
      "id": "brother_edwin_01341835_0",
      "name": "Brother Edwin",
      "title": "The Eccentric Archer",
      "description": "A distinctive 38-year-old Archer.",
      "backstory": "Brother Edwin has lived an interesting life as a Archer.",
      "personality": {
        "primary_trait": "Eccentric",
        "secondary_trait": "Witty",
        "motivation": "To seek knowledge",
        "fear": "Failure",
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
          "target_character": "Sir Fiona",
          "relationship_type": "Acquaintance",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Brother Brenna",
          "relationship_type": "Friend",
          "relationship_strength": 8,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Fiona 181",
          "relationship_type": "Ally",
          "relationship_strength": 8,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Lady Hilda",
          "relationship_type": "Acquaintance",
          "relationship_strength": 4,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "brother edwin_greeting",
          "text": "Greetings! I'm Brother Edwin, the local Archer.",
          "speaker": "Brother Edwin",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "brother edwin_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "brother edwin_role",
          "text": "As a Archer, I to seek knowledge.",
          "speaker": "Brother Edwin",
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
      "role": "Archer",
      "quest_involvement": [],
      "age": 38,
      "appearance": "Distinctive appearance fitting a spooky character.",
      "voice_description": "Speaks with confidence",
      "unique_id": "42b451b4-01f3-4762-9f5a-cc2f59749b32"
    },
    {
      "id": "sir_fiona_01341835_1",
      "name": "Sir Fiona",
      "title": "The Jovial Noble",
      "description": "A distinctive 23-year-old Noble.",
      "backstory": "Sir Fiona has lived an interesting life as a Noble.",
      "personality": {
        "primary_trait": "Jovial",
        "secondary_trait": "Energetic",
        "motivation": "To discover truth",
        "fear": "Being misunderstood",
        "quirk": "Never sits still",
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
          "target_character": "Brother Edwin",
          "relationship_type": "Acquaintance",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Brother Brenna",
          "relationship_type": "Acquaintance",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Fiona 181",
          "relationship_type": "Rival",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Lady Hilda",
          "relationship_type": "Rival",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "sir fiona_greeting",
          "text": "Greetings! I'm Sir Fiona, the local Noble.",
          "speaker": "Sir Fiona",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "sir fiona_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "sir fiona_role",
          "text": "As a Noble, I to discover truth.",
          "speaker": "Sir Fiona",
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
      "age": 23,
      "appearance": "Distinctive appearance fitting a spooky character.",
      "voice_description": "Speaks with confidence",
      "unique_id": "c4c603ca-7a55-4396-8700-379b591922bd"
    },
    {
      "id": "brother_brenna_01341835_2",
      "name": "Brother Brenna",
      "title": "The Determined Resident",
      "description": "A distinctive 25-year-old Resident.",
      "backstory": "Brother Brenna has lived an interesting life as a Resident.",
      "personality": {
        "primary_trait": "Determined",
        "secondary_trait": "Curious",
        "motivation": "To seek knowledge",
        "fear": "The unknown",
        "quirk": "Collects unusual items",
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
          "target_character": "Brother Edwin",
          "relationship_type": "Friend",
          "relationship_strength": 8,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sir Fiona",
          "relationship_type": "Acquaintance",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Fiona 181",
          "relationship_type": "Rival",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Lady Hilda",
          "relationship_type": "Acquaintance",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "brother brenna_greeting",
          "text": "Greetings! I'm Brother Brenna, the local Resident.",
          "speaker": "Brother Brenna",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "brother brenna_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "brother brenna_role",
          "text": "As a Resident, I to seek knowledge.",
          "speaker": "Brother Brenna",
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
      "role": "Resident",
      "quest_involvement": [],
      "age": 25,
      "appearance": "Distinctive appearance fitting a spooky character.",
      "voice_description": "Speaks with confidence",
      "unique_id": "e6953982-3688-4aa1-9208-8038b565a47c"
    },
    {
      "id": "fiona_181_01341835_3",
      "name": "Fiona 181",
      "title": "The Clever Mage",
      "description": "A distinctive 33-year-old Mage.",
      "backstory": "Fiona 181 has lived an interesting life as a Mage.",
      "personality": {
        "primary_trait": "Clever",
        "secondary_trait": "Ambitious",
        "motivation": "To seek knowledge",
        "fear": "Failure",
        "quirk": "Never sits still",
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
        "intelligence": 18,
        "charisma": 13,
        "dexterity": 12,
        "wisdom": 14,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Brother Edwin",
          "relationship_type": "Ally",
          "relationship_strength": 8,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sir Fiona",
          "relationship_type": "Rival",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Brother Brenna",
          "relationship_type": "Rival",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Lady Hilda",
          "relationship_type": "Ally",
          "relationship_strength": 4,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "fiona 181_greeting",
          "text": "Greetings! I'm Fiona 181, the local Mage.",
          "speaker": "Fiona 181",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "fiona 181_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "fiona 181_role",
          "text": "As a Mage, I to seek knowledge.",
          "speaker": "Fiona 181",
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
      "location": "church",
      "role": "Mage",
      "quest_involvement": [],
      "age": 33,
      "appearance": "Distinctive appearance fitting a spooky character.",
      "voice_description": "Speaks with confidence",
      "unique_id": "8dc32fd2-baa6-4536-8ba2-46f81dcec216"
    },
    {
      "id": "lady_hilda_01341835_4",
      "name": "Lady Hilda",
      "title": "The Gentle Knight",
      "description": "A distinctive 33-year-old Knight.",
      "backstory": "Lady Hilda has lived an interesting life as a Knight.",
      "personality": {
        "primary_trait": "Gentle",
        "secondary_trait": "Curious",
        "motivation": "To build something lasting",
        "fear": "Being alone",
        "quirk": "Never sits still",
        "speech_pattern": "Speaks with confidence",
        "alignment": "Neutral Good",
        "mood": "Generally positive",
        "secret": "Has an interesting past",
        "life_goal": "To live meaningfully"
      },
      "stats": {
        "level": 10,
        "health": 90,
        "strength": 12,
        "intelligence": 12,
        "charisma": 12,
        "dexterity": 12,
        "wisdom": 12,
        "constitution": 12
      },
      "relationships": [
        {
          "target_character": "Brother Edwin",
          "relationship_type": "Acquaintance",
          "relationship_strength": 4,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Sir Fiona",
          "relationship_type": "Rival",
          "relationship_strength": 5,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Brother Brenna",
          "relationship_type": "Acquaintance",
          "relationship_strength": 6,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        },
        {
          "target_character": "Fiona 181",
          "relationship_type": "Ally",
          "relationship_strength": 4,
          "history": "They know each other through their work in town",
          "current_status": "Neutral"
        }
      ],
      "dialogue_tree": [
        {
          "id": "lady hilda_greeting",
          "text": "Greetings! I'm Lady Hilda, the local Knight.",
          "speaker": "Lady Hilda",
          "options": [
            {
              "id": "greeting_continue",
              "text": "Tell me about your work",
              "next_node_id": "lady hilda_role",
              "conditions": [],
              "effects": []
            }
          ],
          "is_greeting": true,
          "is_farewell": false,
          "quest_related": false
        },
        {
          "id": "lady hilda_role",
          "text": "As a Knight, I to build something lasting.",
          "speaker": "Lady Hilda",
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
      "location": "tower",
      "role": "Knight",
      "quest_involvement": [],
      "age": 33,
      "appearance": "Distinctive appearance fitting a spooky character.",
      "voice_description": "Speaks with confidence",
      "unique_id": "1cb7f279-0a19-4c78-abac-67a0a9f44c64"
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
