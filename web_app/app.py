#!/usr/bin/env python3
"""
Complete Flask App for Multi-Agent Game Generator
Includes dynamic game content overview integration
"""

from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for
import os
import json
import glob
from datetime import datetime
import logging

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'json'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with game generation interface"""
    return render_template('index.html')

@app.route('/game-overview')
def game_overview():
    """Serve the dynamic game overview UI"""
    return send_from_directory('static', 'enhanced_game_ui.html')

@app.route('/api/game-data')
def get_game_data():
    """API endpoint to serve game data to the frontend"""
    try:
        game_data = {}
        
        # Try to load world specification
        world_data = load_world_data()
        if world_data:
            game_data['world'] = world_data
            logger.info("Successfully loaded world data")
        
        # Try to load character data
        character_data = load_character_data()
        if character_data:
            game_data['characters'] = character_data
            logger.info("Successfully loaded character data")
        
        # Try to load quest data
        quest_data = load_quest_data()
        if quest_data:
            game_data['quests'] = quest_data
            logger.info("Successfully loaded quest data")
        
        # Try to load asset data
        asset_data = load_asset_data()
        if asset_data:
            game_data['assets'] = asset_data
            logger.info("Successfully loaded asset data")
        
        # Add metadata
        game_data['metadata'] = {
            'loaded_at': datetime.now().isoformat(),
            'has_world': bool(world_data),
            'has_characters': bool(character_data),
            'has_quests': bool(quest_data),
            'has_assets': bool(asset_data)
        }
        
        return jsonify(game_data)
    
    except Exception as e:
        logger.error(f"Error loading game data: {e}")
        return jsonify({'error': str(e)}), 500

def load_world_data():
    """Find and load the most recent world specification file"""
    try:
        # Define possible paths for world specification files
        search_patterns = [
            '../complete_game_content_pipeline/*/world_specification.json',
            '../legacy_generated_content/*/world_specification.json',
            'godot_export/*/world_specification.json',
            '*/world_specification.json'
        ]
        
        latest_file = None
        latest_time = 0
        
        for pattern in search_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    file_time = os.path.getmtime(file_path)
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_file = file_path
                except Exception as e:
                    logger.warning(f"Could not check file {file_path}: {e}")
        
        if latest_file:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded world data from: {latest_file}")
                return data
        
        logger.warning("No world specification file found")
        return None
        
    except Exception as e:
        logger.error(f"Error loading world data: {e}")
        return None

def load_character_data():
    """Find and load character data from various sources"""
    try:
        # Try JSON files first
        search_patterns = [
            '../generated_characters/*/characters.json',
            '../legacy_generated_content/*/characters.json',
            'godot_export/*/data/characters.json',
            '*/characters.json'
        ]
        
        for pattern in search_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        logger.info(f"Loaded character data from: {file_path}")
                        return data
                except Exception as e:
                    logger.warning(f"Could not load character file {file_path}: {e}")
        
        # Try to extract from GDScript files
        gdscript_patterns = [
            'godot_export/*/scripts/NPC.gd',
            '*/scripts/NPC.gd'
        ]
        
        for pattern in gdscript_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    characters = extract_characters_from_gdscript(file_path)
                    if characters:
                        logger.info(f"Extracted character data from GDScript: {file_path}")
                        return {'characters': characters}
                except Exception as e:
                    logger.warning(f"Could not extract from GDScript {file_path}: {e}")
        
        logger.warning("No character data found")
        return None
        
    except Exception as e:
        logger.error(f"Error loading character data: {e}")
        return None

def load_quest_data():
    """Find and load quest data"""
    try:
        search_patterns = [
            '../generated_quests/*/quests.json',
            'godot_export/*/data/quests.json',
            '../legacy_generated_content/*/quests.json',
            '*/quests.json'
        ]
        
        latest_file = None
        latest_time = 0
        
        for pattern in search_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    file_time = os.path.getmtime(file_path)
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_file = file_path
                except Exception as e:
                    logger.warning(f"Could not check quest file {file_path}: {e}")
        
        if latest_file:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded quest data from: {latest_file}")
                return data
        
        logger.warning("No quest data found")
        return None
        
    except Exception as e:
        logger.error(f"Error loading quest data: {e}")
        return None

def load_asset_data():
    """Find and load asset manifest data"""
    try:
        search_patterns = [
            '../complete_game_content_pipeline/*/assets/asset_manifest.json',
            '../legacy_generated_content/*/assets/asset_manifest.json',
            '*/assets/asset_manifest.json'
        ]
        
        latest_file = None
        latest_time = 0
        
        for pattern in search_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                try:
                    file_time = os.path.getmtime(file_path)
                    if file_time > latest_time:
                        latest_time = file_time
                        latest_file = file_path
                except Exception as e:
                    logger.warning(f"Could not check asset file {file_path}: {e}")
        
        if latest_file:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded asset data from: {latest_file}")
                return data
        
        logger.warning("No asset data found")
        return None
        
    except Exception as e:
        logger.error(f"Error loading asset data: {e}")
        return None

def extract_characters_from_gdscript(file_path):
    """Extract character information from GDScript files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        characters = []
        
        # Look for character data blocks in the GDScript
        import re
        
        # Pattern to match character objects
        character_pattern = r'"id":\s*"([^"]+)"[\s\S]*?"name":\s*"([^"]+)"[\s\S]*?"role":\s*"([^"]+)"'
        matches = re.findall(character_pattern, content)
        
        for match in matches:
            char_id, name, role = match
            
            # Try to extract additional info
            age_pattern = rf'"name":\s*"{re.escape(name)}"[\s\S]*?"age":\s*(\d+)'
            age_match = re.search(age_pattern, content)
            age = int(age_match.group(1)) if age_match else 25
            
            characters.append({
                'id': char_id,
                'name': name,
                'role': role,
                'age': age,
                'personality': {
                    'primary_trait': 'AI Generated',
                    'secondary_trait': 'Unique'
                },
                'relationships': []
            })
        
        # If no structured data found, try to extract known character names
        if not characters:
            known_chars = ['Brother Gareth', 'Master Aldric', 'Sister Gareth', 'Master Fiona']
            for char_name in known_chars:
                if char_name in content:
                    characters.append({
                        'name': char_name,
                        'role': 'Generated NPC',
                        'age': 30,
                        'personality': {'primary_trait': 'AI Generated'},
                        'relationships': []
                    })
        
        return characters
        
    except Exception as e:
        logger.error(f"Error extracting characters from GDScript: {e}")
        return []

@app.route('/api/generate-game', methods=['POST'])
def generate_game():
    """API endpoint for game generation (placeholder)"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Here you would integrate with your game generation pipeline
        # For now, return a success message
        result = {
            'status': 'success',
            'message': f'Game generation initiated for prompt: {prompt}',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in game generation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        status = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'available_endpoints': [
                '/api/game-data',
                '/api/generate-game',
                '/api/status',
                '/game-overview'
            ],
            'file_counts': get_file_counts()
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_file_counts():
    """Get counts of various generated files"""
    try:
        counts = {
            'world_files': len(glob.glob('../*/world_specification.json')),
            'character_files': len(glob.glob('../*/characters.json')),
            'quest_files': len(glob.glob('../*/quests.json')),
            'asset_files': len(glob.glob('../*/assets/asset_manifest.json'))
        }
        return counts
    except Exception as e:
        logger.error(f"Error getting file counts: {e}")
        return {}

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Development settings
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        threaded=True
    )