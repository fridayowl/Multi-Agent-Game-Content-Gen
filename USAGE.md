# Usage Guide

## Overview

Oyun  offers three main ways to generate game content:

1. **Web Interface** (Recommended for beginners)
2. **Command Line** (For developers and automation)
3. **Individual Agent Testing** (For debugging and development)

## Option 1: Web Interface (Recommended)

### ADK Web Server

Start the ADK web server:

```bash
adk web run
```

Access the interface at: `http://localhost:8080`

### Alternative: Flask Web App

If you prefer the Flask interface:

```bash
cd web_app
python app.py
```

Access at: `http://localhost:5001`

### Web Interface Usage Steps

1. Open `http://localhost:8080` (ADK Web) or `http://localhost:5001` (Flask)
2. Enter your game world prompt (e.g., "Create a medieval village with a blacksmith and tavern")
3. Adjust character and quest counts using the sliders
4. Click "Generate Game World"
5. Wait for generation to complete
6. Download the generated Unity/Godot packages

## Option 2: Command Line

### Run the Main Orchestrator

```bash
python -c "
from orchestrator.agent import generate_complete_game_content
import asyncio

async def main():
    result = await generate_complete_game_content('Create a medieval village with a blacksmith and tavern')
    print('Game content generated successfully!')

asyncio.run(main())
"
```

### Quick Test Pipeline

```bash
python quick_test.py
```

### Programmatic Usage

```python
from orchestrator.agent import generate_complete_game_content
import asyncio

async def create_fantasy_world():
    result = await generate_complete_game_content(
        prompt="Create a magical forest village with elves and ancient ruins",
        character_count=8,
        quest_count=10
    )
    print(f"Generated world: {result['world_name']}")
    print(f"Characters created: {len(result['characters'])}")
    print(f"Quests generated: {len(result['quests'])}")

# Run the function
asyncio.run(create_fantasy_world())
```

## Option 3: Individual Agent Testing

Test specific agents directly for debugging or development:

```bash
# Test world designer
python orchestrator/world_designer/agent.py

# Test asset generator  
python orchestrator/asset_generator/agent.py

# Test character creator
python orchestrator/character_creator/agent.py

# Test quest writer
python orchestrator/quest_writer/agent.py

# Test balance validator
python orchestrator/balance_validator/agent.py

# Test godot exporter
python orchestrator/godot_exporter/agent.py
```

## Advanced Usage

### Custom Configuration

You can customize generation parameters:

```python
from orchestrator.agent import generate_complete_game_content

result = await generate_complete_game_content(
    prompt="Create a cyberpunk city district",
    character_count=12,
    quest_count=15,
    world_size="large",
    theme="cyberpunk",
    difficulty="hard"
)
```

### Batch Generation

Generate multiple worlds:

```python
prompts = [
    "Medieval castle town",
    "Futuristic space station",
    "Underwater research facility"
]

for prompt in prompts:
    result = await generate_complete_game_content(prompt)
    print(f"Generated: {result['world_name']}")
```

## Output Locations

Generated content is saved to:

- **Main Output**: `generated_content/complete_game_content/`
- **Godot Projects**: `godot_exports/`
- **Unity Packages**: `generated_content/{world_name}/unity_package/`

## Tips for Better Results

1. **Be Specific**: "Medieval village with blacksmith, tavern, and town square" works better than "village"
2. **Include Atmosphere**: "Dark, mysterious forest with ancient ruins" creates better ambiance
3. **Specify Relationships**: "Village where the blacksmith and tavern owner are rivals"
4. **Consider Scale**: Small villages (3-5 characters) generate faster than large cities (10+ characters) 
