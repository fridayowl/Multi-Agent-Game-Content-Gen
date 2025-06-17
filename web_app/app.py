#!/usr/bin/env python3
"""
Complete Flask Web App for AI Game Generator
Integrates with your existing multi-agent pipeline - GODOT VERSION
HTML template separated into templates/index.html for easy customization
Enhanced with detailed generation information display
"""

import os
import sys
import uuid
import asyncio
import json
import time
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import threading
from typing import Dict, Any

app = Flask(__name__)
CORS(app)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
GENERATED_FOLDER = PROJECT_ROOT / 'generated_content'
DOWNLOAD_FOLDER = Path(__file__).parent / 'downloads'

# Create directories if they don't exist
GENERATED_FOLDER.mkdir(exist_ok=True)
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Create templates directory for HTML files
TEMPLATES_FOLDER = Path(__file__).parent / 'templates'
TEMPLATES_FOLDER.mkdir(exist_ok=True)

# Add project to Python path
sys.path.insert(0, str(PROJECT_ROOT))

# Configure Flask to use our templates directory
app.template_folder = str(TEMPLATES_FOLDER)

# In-memory job storage (use Redis/database in production)
generation_jobs = {}

class GenerationJob:
    def __init__(self, generation_id: str, prompt: str):
        self.id = generation_id
        self.prompt = prompt
        self.status = 'starting'  # starting, in_progress, completed, failed
        self.progress = 0
        self.message = 'Initializing generation pipeline...'
        self.agents = {
            'world': {'status': 'pending', 'message': 'Waiting to start...'},
            'assets': {'status': 'pending', 'message': 'Waiting to start...'},
            'characters': {'status': 'pending', 'message': 'Waiting to start...'},
            'quests': {'status': 'pending', 'message': 'Waiting to start...'},
            'balance': {'status': 'pending', 'message': 'Waiting to start...'},
            'export': {'status': 'pending', 'message': 'Waiting to start...'}
        }
        self.download_url = None
        self.error = None
        self.result_data = None
        self.created_at = datetime.now()
        # Enhanced data storage for detailed information
        self.generation_details = {
            'world': None,
            'assets': None,
            'characters': None,
            'quests': None,
            'files': []
        }

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def start_generation():
    """Start a new game generation"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if len(prompt) < 10:
            return jsonify({'error': 'Please provide a more detailed prompt (at least 10 characters)'}), 400
        
        # Create new generation job
        generation_id = str(uuid.uuid4())
        job = GenerationJob(generation_id, prompt)
        generation_jobs[generation_id] = job
        
        print(f"🚀 Starting generation {generation_id} for prompt: {prompt[:100]}...")
        
        # Start generation in background thread
        thread = threading.Thread(
            target=run_generation_pipeline,
            args=(generation_id, prompt),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'generation_id': generation_id,
            'status': 'started',
            'message': 'Generation started successfully'
        })
        
    except Exception as e:
        print(f"❌ Generation start error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/progress/<generation_id>')
def get_progress(generation_id):
    """Get generation progress with detailed information"""
    job = generation_jobs.get(generation_id)
    
    if not job:
        return jsonify({'error': 'Generation not found'}), 404
    
    response_data = {
        'status': job.status,
        'progress': job.progress,
        'message': job.message,
        'agents': job.agents,
        'generation_details': job.generation_details  # Include detailed information
    }
    
    if job.status == 'completed' and job.download_url:
        response_data['download_url'] = job.download_url
        # Add stats from result if available
        if job.result_data and hasattr(job.result_data, 'characters'):
            response_data['stats'] = {
                'npc_count': len(job.result_data.characters) if job.result_data.characters else 5,
                'quest_count': len(job.result_data.quests) if hasattr(job.result_data, 'quests') and job.result_data.quests else 3,
                'world_size': 'Generated'
            }
        else:
            response_data['stats'] = {
                'npc_count': 5,
                'quest_count': 3,
                'world_size': 'Generated'
            }
    
    if job.status == 'failed' and job.error:
        response_data['error'] = job.error
    
    return jsonify(response_data)

@app.route('/api/download/<generation_id>')
def download_package(generation_id):
    """Download the generated Godot package"""
    job = generation_jobs.get(generation_id)
    
    if not job or job.status != 'completed':
        return jsonify({'error': 'Package not ready'}), 400
    
    print(f"🔍 Download request for generation: {generation_id}")
    print(f"📁 Looking in: {GENERATED_FOLDER}")
    
    # List what's actually in the generated content folder
    if GENERATED_FOLDER.exists():
        print(f"📂 Contents of {GENERATED_FOLDER}:")
        for item in GENERATED_FOLDER.rglob('*'):
            if item.is_file():
                print(f"  📄 {item}")
            elif item.is_dir():
                print(f"  📁 {item}/")
    else:
        print(f"❌ Generated content folder doesn't exist: {GENERATED_FOLDER}")
    
    # Find the package
    package_path = find_godot_package(generation_id)
    
    if not package_path or not package_path.exists():
        print(f"❌ No package found for generation {generation_id}")
        return jsonify({'error': 'Package file not found'}), 404
    
    print(f"✅ Sending package: {package_path}")
    
    return send_file(
        package_path,
        as_attachment=True,
        download_name=f'GodotGameWorld_{generation_id[:8]}.zip'
    )

def load_generation_details(session_dir: Path, job: GenerationJob):
    """Load detailed generation information from files"""
    try:
        # Load world specification
        world_file = session_dir / "world_specification.json"
        if world_file.exists():
            with open(world_file, 'r') as f:
                world_data = json.load(f)
                job.generation_details['world'] = extract_world_details(world_data)
        
        # Load asset information
        asset_manifest = session_dir / "ai_creative_assets" / "ai_creative_manifest.json"
        if asset_manifest.exists():
            with open(asset_manifest, 'r') as f:
                asset_data = json.load(f)
                job.generation_details['assets'] = extract_asset_details(asset_data, session_dir)
        elif session_dir.glob("assets"):
            # Fallback to assets folder
            assets_dir = session_dir / "assets"
            if assets_dir.exists():
                job.generation_details['assets'] = extract_asset_details_from_folder(assets_dir)
        
        # Load character information
        characters_file = session_dir / "characters.json"
        if characters_file.exists():
            with open(characters_file, 'r') as f:
                character_data = json.load(f)
                job.generation_details['characters'] = extract_character_details(character_data)
        
        # Load quest information
        quests_file = session_dir / "quests.json"
        if quests_file.exists():
            with open(quests_file, 'r') as f:
                quest_data = json.load(f)
                job.generation_details['quests'] = extract_quest_details(quest_data)
        
        # Load file structure
        job.generation_details['files'] = extract_file_structure(session_dir)
        
        print(f"✅ Loaded generation details for {job.id}")
        
    except Exception as e:
        print(f"❌ Error loading generation details: {e}")

def extract_world_details(world_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract world details for display"""
    return {
        'theme': world_data.get('theme', 'Unknown'),
        'description': world_data.get('description', 'A generated game world'),
        'size': world_data.get('size', [40, 40]),
        'buildings': world_data.get('buildings', []),
        'natural_features': world_data.get('natural_features', []),
        'paths': world_data.get('paths', []),
        'terrain': world_data.get('terrain_grid', []),
        'environment_type': world_data.get('environment_type', 'Mixed'),
        'mood': world_data.get('mood', 'Neutral')
    }

def extract_asset_details(asset_data: Dict[str, Any], session_dir: Path) -> Dict[str, Any]:
    """Extract asset details for display"""
    assets = {
        'total_count': asset_data.get('total_assets', 0),
        'categories': {
            'buildings': [],
            'props': [],
            'environment': [],
            'textures': [],
            'materials': []
        },
        'blender_files': [],
        'model_files': []
    }
    
    # Extract asset categories
    if 'assets' in asset_data:
        for asset in asset_data['assets']:
            category = asset.get('category', 'unknown')
            if category in assets['categories']:
                assets['categories'][category].append({
                    'name': asset.get('name', 'Unknown'),
                    'file': asset.get('filename', ''),
                    'description': asset.get('description', ''),
                    'type': asset.get('type', '')
                })
    
    # Find Blender files
    blender_dir = session_dir / "ai_creative_assets" / "blender_scripts"
    if blender_dir.exists():
        for blend_file in blender_dir.glob("*.py"):
            assets['blender_files'].append(blend_file.name)
    
    # Find model files
    models_dir = session_dir / "ai_creative_assets" / "models"
    if models_dir.exists():
        for model_file in models_dir.rglob("*.obj"):
            assets['model_files'].append(str(model_file.relative_to(models_dir)))
    
    return assets

def extract_asset_details_from_folder(assets_dir: Path) -> Dict[str, Any]:
    """Extract asset details from folder structure (fallback)"""
    assets = {
        'total_count': 0,
        'categories': {
            'buildings': [],
            'props': [],
            'environment': [],
            'textures': [],
            'materials': []
        },
        'blender_files': [],
        'model_files': []
    }
    
    # Count files
    model_files = list(assets_dir.rglob("*.obj"))
    assets['total_count'] = len(model_files)
    
    # Find Blender files
    for blend_file in assets_dir.rglob("*.py"):
        assets['blender_files'].append(blend_file.name)
    
    # Find model files
    for model_file in model_files:
        relative_path = str(model_file.relative_to(assets_dir))
        assets['model_files'].append(relative_path)
        
        # Categorize by folder name
        parts = model_file.parts
        if 'buildings' in parts:
            assets['categories']['buildings'].append({
                'name': model_file.stem,
                'file': relative_path,
                'description': f'3D building model',
                'type': 'obj'
            })
        elif 'props' in parts:
            assets['categories']['props'].append({
                'name': model_file.stem,
                'file': relative_path,
                'description': f'3D prop model',
                'type': 'obj'
            })
        else:
            assets['categories']['environment'].append({
                'name': model_file.stem,
                'file': relative_path,
                'description': f'3D environment model',
                'type': 'obj'
            })
    
    return assets

def extract_character_details(character_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract character details for display"""
    characters = {
        'total_count': 0,
        'npcs': []
    }
    
    if 'characters' in character_data:
        character_list = character_data['characters']
        characters['total_count'] = len(character_list)
        
        for char in character_list:
            characters['npcs'].append({
                'name': char.get('name', 'Unknown NPC'),
                'role': char.get('role', 'Villager'),
                'personality': char.get('personality', 'Friendly'),
                'background': char.get('background', 'A mysterious individual'),
                'location': char.get('location', 'Village'),
                'age': char.get('age', 'Adult'),
                'appearance': char.get('appearance', 'Average height'),
                'relationships': char.get('relationships', []),
                'dialogue_style': char.get('dialogue_style', 'Casual'),
                'quests_involved': char.get('quests', [])
            })
    
    return characters

def extract_quest_details(quest_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract quest details for display"""
    quests = {
        'total_count': 0,
        'main_quests': 0,
        'side_quests': 0,
        'quest_list': []
    }
    
    if 'quests' in quest_data:
        quest_list = quest_data['quests']
        quests['total_count'] = len(quest_list)
        
        for quest in quest_list:
            quest_type = quest.get('type', 'side')
            if quest_type == 'main':
                quests['main_quests'] += 1
            else:
                quests['side_quests'] += 1
            
            quests['quest_list'].append({
                'title': quest.get('title', 'Untitled Quest'),
                'type': quest_type,
                'description': quest.get('description', 'A mysterious task awaits'),
                'objective': quest.get('objective', 'Complete the task'),
                'giver': quest.get('quest_giver', 'Unknown'),
                'location': quest.get('location', 'Village'),
                'rewards': quest.get('rewards', []),
                'requirements': quest.get('requirements', []),
                'difficulty': quest.get('difficulty', 'Medium'),
                'estimated_time': quest.get('estimated_time', '15 minutes')
            })
    
    return quests

def extract_file_structure(session_dir: Path) -> list:
    """Extract file structure for display"""
    files = []
    
    try:
        for item in session_dir.rglob('*'):
            if item.is_file():
                relative_path = str(item.relative_to(session_dir))
                file_info = {
                    'name': item.name,
                    'path': relative_path,
                    'size': item.stat().st_size,
                    'type': item.suffix.lower().lstrip('.') or 'file',
                    'category': categorize_file(item)
                }
                files.append(file_info)
    except Exception as e:
        print(f"❌ Error extracting file structure: {e}")
    
    return files

def categorize_file(file_path: Path) -> str:
    """Categorize file based on extension and path"""
    ext = file_path.suffix.lower()
    path_str = str(file_path).lower()
    
    if ext in ['.obj', '.fbx', '.dae', '.gltf']:
        return '3D Model'
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff']:
        return 'Texture'
    elif ext in ['.blend']:
        return 'Blender File'
    elif ext in ['.py']:
        return 'Python Script'
    elif ext in ['.json']:
        return 'Data File'
    elif ext in ['.gd', '.cs']:
        return 'Game Script'
    elif ext in ['.tscn', '.scene']:
        return 'Game Scene'
    elif ext in ['.md', '.txt']:
        return 'Documentation'
    else:
        return 'Other'

def find_godot_package(generation_id: str) -> Path:
    """Find the Godot package for this generation"""
    try:
        # Check multiple possible locations
        possible_locations = [
            GENERATED_FOLDER,
            PROJECT_ROOT / 'generated_content',
            Path.cwd() / 'generated_content',
            PROJECT_ROOT / 'godot_export',
            Path.cwd() / 'godot_export',
            PROJECT_ROOT / 'godot_export' / 'GodotProject',
            Path.cwd() / 'godot_export' / 'GodotProject'
        ]
        
        for location in possible_locations:
            print(f"🔍 Checking location: {location}")
            if location.exists():
                print(f"✅ Location exists: {location}")
                
                # Look for Godot projects (folders with project.godot)
                godot_projects = list(location.rglob('project.godot'))
                if godot_projects:
                    most_recent = max(godot_projects, key=lambda p: p.stat().st_mtime)
                    godot_project_dir = most_recent.parent
                    print(f"✅ Found Godot project: {godot_project_dir}")
                    return create_package_from_godot(godot_project_dir, generation_id)
                
                # Look for GodotProject directories specifically
                godot_project_dirs = [d for d in location.rglob('*') if d.is_dir() and d.name == 'GodotProject']
                if godot_project_dirs:
                    most_recent_dir = max(godot_project_dirs, key=lambda p: p.stat().st_mtime)
                    print(f"✅ Found GodotProject directory: {most_recent_dir}")
                    return create_package_from_godot(most_recent_dir, generation_id)
                
                # Look for directories with Godot-like structure
                for subdir in location.rglob('*'):
                    if subdir.is_dir():
                        subdirs = [d.name for d in subdir.iterdir() if d.is_dir()]
                        if any(name in subdirs for name in ['assets', 'scenes', 'scripts']):
                            print(f"✅ Found Godot-like project structure: {subdir}")
                            return create_package_from_godot(subdir, generation_id)
                
                # Look for recent directories with content
                recent_dirs = [d for d in location.rglob('*') if d.is_dir() and len(list(d.iterdir())) > 0]
                if recent_dirs:
                    most_recent_dir = max(recent_dirs, key=lambda p: p.stat().st_mtime)
                    print(f"✅ Found recent content directory: {most_recent_dir}")
                    return create_package_from_directory(most_recent_dir, generation_id)
        
        print(f"❌ No packages found in any location")
        return None
        
    except Exception as e:
        print(f"❌ Error finding package: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_package_from_godot(godot_dir: Path, generation_id: str) -> Path:
    """Create a downloadable package from Godot project"""
    try:
        package_name = f'GodotGameWorld_{generation_id[:8]}.zip'
        package_path = DOWNLOAD_FOLDER / package_name
        
        print(f"📦 Creating Godot package from: {godot_dir}")
        print(f"📥 Package will be saved as: {package_path}")
        
        # Create zip file of the entire godot project directory
        print(f"🗜️ Creating archive...")
        shutil.make_archive(str(package_path.with_suffix('')), 'zip', str(godot_dir))
        
        # Verify the created package
        if package_path.exists():
            size_mb = package_path.stat().st_size / (1024 * 1024)
            print(f"✅ Godot package created successfully: {package_path}")
            print(f"📊 Package size: {size_mb:.2f} MB")
            return package_path
        else:
            print(f"❌ Package creation failed - file doesn't exist")
            return None
        
    except Exception as e:
        print(f"❌ Error creating Godot package: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_package_from_directory(content_dir: Path, generation_id: str) -> Path:
    """Create a downloadable package from any content directory"""
    try:
        package_name = f'AIGameWorld_{generation_id[:8]}.zip'
        package_path = DOWNLOAD_FOLDER / package_name
        
        print(f"📦 Creating package from: {content_dir}")
        print(f"📥 Package will be saved as: {package_path}")
        
        # Create zip file of the content directory
        shutil.make_archive(str(package_path.with_suffix('')), 'zip', str(content_dir))
        
        print(f"✅ Package created successfully: {package_path}")
        return package_path
        
    except Exception as e:
        print(f"❌ Error creating package: {e}")
        return None

def call_your_orchestrator(prompt: str):
    """Call your existing orchestrator class correctly"""
    try:
        print(f"🚀 Importing orchestrator...")
        
        # Import your orchestrator class
        from orchestrator.agent import CompleteGameContentOrchestrator
        
        print(f"🎯 Creating orchestrator instance...")
        
        # Create orchestrator instance
        orchestrator = CompleteGameContentOrchestrator()
        
        print(f"🎮 Starting pipeline for prompt: {prompt[:100]}...")
        
        # Call the main generation method
        result = asyncio.run(orchestrator.generate_complete_game_content(
            prompt=prompt,
            character_count=5,
            quest_count=3
        ))
        
        print(f"✅ Pipeline completed successfully!")
        
        # Return the result
        return result
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"💡 Current working directory: {os.getcwd()}")
        print(f"💡 Python path: {sys.path[:3]}...")
        raise Exception(f"Could not import orchestrator: {e}")
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        raise Exception(f"Pipeline failed: {e}")

def run_generation_pipeline(generation_id: str, prompt: str):
    """Run the generation pipeline"""
    job = generation_jobs.get(generation_id)
    if not job:
        return
    
    try:
        print(f"🎮 Running pipeline for generation {generation_id}")
        print(f"📝 Prompt: {prompt}")
        
        # Update status
        job.status = 'in_progress'
        job.progress = 10
        job.message = 'Starting multi-agent coordination...'
        
        # Simulate agent progression with real names from your pipeline
        agents_sequence = [
            ('world', 'World Designer', 'Creating terrain and layout...', 15),
            ('assets', 'Asset Generator', 'Generating 3D models and textures...', 30),
            ('characters', 'Character Creator', 'Creating NPCs and personalities...', 45),
            ('quests', 'Quest Writer', 'Writing storylines and dialogue...', 60),
            ('balance', 'Balance Validator', 'Balancing gameplay mechanics...', 75),
            ('export', 'Godot Exporter', 'Creating Godot package...', 85)
        ]
        
        # Update each agent status gradually
        for agent_key, agent_name, agent_message, progress in agents_sequence:
            job.agents[agent_key]['status'] = 'active'
            job.agents[agent_key]['message'] = agent_message
            job.progress = progress
            job.message = f"Running {agent_name}..."
            
            print(f"  🤖 {agent_name}: {agent_message}")
            time.sleep(2)  # Short delay to show progress
            
            job.agents[agent_key]['status'] = 'completed'
            job.agents[agent_key]['message'] = 'Completed successfully!'
        
        # NOW call your actual orchestrator
        print("🚀 Calling actual orchestrator...")
        job.message = 'Running AI pipeline...'
        job.progress = 90
        
        # Change to the project root directory for orchestrator
        original_cwd = os.getcwd()
        try:
            os.chdir(PROJECT_ROOT)
            print(f"📁 Changed to project root: {PROJECT_ROOT}")
            
            # Call your orchestrator
            result = call_your_orchestrator(prompt)
            
            # Store the result
            job.result_data = result
            
            # Load detailed generation information
            # Find the most recent session directory
            session_dirs = list(GENERATED_FOLDER.glob('*'))
            if session_dirs:
                most_recent_session = max(session_dirs, key=lambda p: p.stat().st_mtime)
                print(f"📂 Loading details from: {most_recent_session}")
                load_generation_details(most_recent_session, job)
            
        finally:
            # Always change back to original directory
            os.chdir(original_cwd)
        
        # Mark as completed
        job.status = 'completed'
        job.progress = 100
        job.message = 'Generation completed successfully!'
        job.download_url = f'/api/download/{generation_id}'
        
        print(f"✅ Generation {generation_id} completed successfully!")
        
    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        job.message = f'Generation failed: {str(e)}'
        print(f"❌ Generation {generation_id} failed: {e}")
        import traceback
        traceback.print_exc()

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'project_root': str(PROJECT_ROOT),
        'generated_folder': str(GENERATED_FOLDER),
        'templates_folder': str(TEMPLATES_FOLDER)
    })

# API documentation endpoint
@app.route('/api/docs')
def api_docs():
    docs = {
        'title': 'AI Game Generator API - Godot Edition',
        'version': '1.0.0',
        'description': 'Generate complete Godot game worlds from text descriptions',
        'endpoints': {
            'POST /api/generate': {
                'description': 'Start Godot game generation from text prompt',
                'body': {'prompt': 'string (required)'},
                'response': {'generation_id': 'string', 'status': 'string', 'message': 'string'}
            },
            'GET /api/progress/{id}': {
                'description': 'Get generation progress and agent status with detailed information',
                'response': {
                    'status': 'string (starting|in_progress|completed|failed)',
                    'progress': 'number (0-100)',
                    'message': 'string',
                    'agents': 'object (agent statuses)',
                    'generation_details': 'object (detailed generation information)',
                    'download_url': 'string (when completed)'
                }
            },
            'GET /api/download/{id}': {
                'description': 'Download generated Godot package',
                'response': 'file download (.zip containing Godot project)'
            },
            'GET /health': {
                'description': 'Health check endpoint',
                'response': {'status': 'healthy', 'timestamp': 'ISO string'}
            }
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    print("🚀 AI Game Generator Web App Starting...")
    print("="*60)
    print(f"🌐 Web Interface: http://localhost:5001")
    print(f"📚 API Documentation: http://localhost:5001/api/docs") 
    print(f"💚 Health Check: http://localhost:5001/health")
    print(f"📁 Project Root: {PROJECT_ROOT}")
    print(f"📁 Generated Content: {GENERATED_FOLDER}")
    print(f"📁 Templates Folder: {TEMPLATES_FOLDER}")
    print("="*60)
    
    # Verify orchestrator can be imported
    try:
        from orchestrator.agent import CompleteGameContentOrchestrator
        print("✅ Orchestrator import successful")
    except ImportError as e:
        print(f"⚠️ Orchestrator import failed: {e}")
        print("💡 The web app will still run, but generation may fail")
    
    # Check if templates directory exists and has index.html
    index_template = TEMPLATES_FOLDER / 'index.html'
    if index_template.exists():
        print("✅ HTML template found: templates/index.html")
    else:
        print("⚠️ HTML template missing: templates/index.html")
        print("💡 Please save the HTML template as templates/index.html")
    
    print("\n🎮 Ready to generate amazing Godot game worlds!")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )