# Output Formats Guide

## Overview

The Oyun generates comprehensive game content in multiple formats, ready for integration with popular game engines.

## Generated Content Structure
 
```
generated_content/
└── {world_name}_{timestamp}/
    ├── 📁 world_design/              # World layouts and maps
    │   ├── world_manifest.json       # World overview and metadata
    │   ├── layout_description.json   # Detailed world layout
    │   ├── environment_data.json     # Environmental features
    │   └── world_map.png             # Visual world map
    │
    ├── 📁 generated_assets/          # 3D models and textures
    │   ├── asset_manifest.json       # Asset inventory
    │   ├── 📁 models/                # 3D model descriptions
    │   │   ├── building_01.json      # Building model data
    │   │   ├── character_01.json     # Character model data
    │   │   └── prop_01.json          # Prop model data
    │   │
    │   ├── 📁 textures/              # Texture descriptions
    │   │   ├── stone_wall.json       # Texture specifications
    │   │   ├── wood_plank.json       # Material definitions
    │   │   └── grass_ground.json     # Ground texture data
    │   │
    │   └── 📁 materials/             # Material definitions
    │       ├── materials.json        # Material properties
    │       └── shader_configs.json   # Shader configurations
    │
    ├── 📁 character_profiles/        # NPC data and personalities
    │   ├── character_manifest.json   # Character overview
    │   ├── character_01_profile.json # Individual character data
    │   ├── character_02_profile.json # Personality and stats
    │   ├── relationship_map.json     # Character relationships
    │   └── character_stats.json      # Game statistics
    │
    ├── 📁 quest_system/              # Storylines and dialogue
    │   ├── quest_manifest.json       # Quest overview
    │   ├── 📁 quest_definitions/     # Individual quest data
    │   │   ├── main_quest_01.json    # Main storyline quests
    │   │   ├── side_quest_01.json    # Side quest content
    │   │   └── daily_quest_01.json   # Repeatable quests
    │   │
    │   ├── 📁 dialogue_trees/        # Conversation systems
    │   │   ├── npc_01_dialogue.json  # Character conversations
    │   │   ├── quest_dialogue.json   # Quest-specific dialogue
    │   │   └── ambient_dialogue.json # Background conversations
    │   │
    │   └── 📁 quest_chains/          # Quest interconnections
    │       ├── main_storyline.json   # Primary story arc
    │       └── side_storylines.json  # Optional quest chains
    │
    ├── 📁 balance_reports/           # Game balance analysis
    │   ├── balance_summary.json      # Overall balance assessment
    │   ├── character_balance.json    # Character stat analysis
    │   ├── quest_balance.json        # Quest difficulty analysis
    │   ├── economy_balance.json      # Economic balance report
    │   └── recommendations.json      # Optimization suggestions
    │
    └── 📁 godot_project/             # Complete Godot project
        ├── project.godot             # Godot project file
        ├── 📁 scenes/                # Godot scene files
        │   ├── World.tscn            # Main world scene
        │   ├── Character.tscn        # Character scene template
        │   └── UI.tscn               # User interface scene
        │
        ├── 📁 scripts/               # GDScript files
        │   ├── WorldManager.gd       # World management
        │   ├── CharacterController.gd # Character behavior
        │   ├── QuestManager.gd       # Quest system
        │   └── DialogueSystem.gd     # Dialogue management
        │
        ├── 📁 assets/                # Game assets
        │   ├── 📁 models/            # 3D models (when available)
        │   ├── 📁 textures/          # Texture files
        │   ├── 📁 audio/             # Sound files
        │   └── 📁 ui/                # UI assets
        │
        └── setup_instructions.txt    # Import instructions
```

## File Format Details

### World Design Files

#### world_manifest.json

```json
{
  "world_name": "Elderwood Village",
  "theme": "medieval_fantasy",
  "size": "medium",
  "population": 45,
  "main_locations": [
    "Village Center",
    "Blacksmith Shop", 
    "Tavern",
    "Temple"
  ],
  "environment_type": "temperate_forest",
  "generation_timestamp": "2025-06-22T14:30:00Z"
}
```

#### layout_description.json

```json
{
  "world_layout": {
    "center": {
      "type": "village_square",
      "coordinates": [0, 0],
      "description": "Central gathering place with fountain"
    },
    "buildings": [
      {
        "name": "Ironforge Smithy",
        "type": "blacksmith",
        "coordinates": [15, -10],
        "owner": "Gareth Ironforge",
        "description": "Stone building with smoking chimney"
      }
    ],
    "paths": [
      {
        "from": "village_square",
        "to": "blacksmith",
        "type": "cobblestone",
        "length": 18
      }
    ]
  }
}
```

### Character Profile Files

#### character_01_profile.json

```json
{
  "character_id": "char_001",
  "name": "Gareth Ironforge",
  "role": "Village Blacksmith",
  "personality": {
    "traits": ["hardworking", "gruff", "reliable"],
    "alignment": "neutral_good",
    "motivation": "Master his craft and provide for village",
    "quirks": ["Always has soot on hands", "Hums while working"]
  },
  "stats": {
    "level": 25,
    "strength": 18,
    "dexterity": 14,
    "constitution": 16,
    "intelligence": 13,
    "wisdom": 15,
    "charisma": 11
  },
  "relationships": [
    {
      "character": "Mayor Aldric",
      "relationship": "respected_authority",
      "description": "Respects the mayor's leadership"
    }
  ],
  "inventory": [
    "Master Smithing Tools",
    "Leather Apron",
    "Family Heirloom Hammer"
  ]
}
```

### Quest System Files

#### main_quest_01.json

```json
{
  "quest_id": "main_001",
  "title": "The Missing Ore Shipment", 
  "type": "main_quest",
  "giver": "Gareth Ironforge",
  "description": "Investigate the missing iron ore shipment from the mines",
  "objectives": [
    {
      "id": "obj_001",
      "description": "Talk to the mine foreman",
      "type": "dialogue",
      "target": "Mine Foreman Marcus"
    },
    {
      "id": "obj_002", 
      "description": "Search the mining tunnels",
      "type": "exploration",
      "location": "Copper Hill Mines"
    }
  ],
  "rewards": {
    "experience": 250,
    "gold": 50,
    "items": ["Iron Ingot", "Smithing Manual"]
