#!/usr/bin/env python3
"""
Fixed Oyun Generator Web App - Corrected folder paths and added asset downloads
Now properly handles the actual folder structure from your orchestrator
"""

import asyncio
import json
import os
import shutil
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from flask import Flask, render_template, request, jsonify, send_file

# Get the absolute path to the project root (parent of web_app)
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

print(f"🚀 Oyun Generator Web App Starting...")
print(f"{'='*60}")
print(f"🌐 Web Interface: http://localhost:5001")
print(f"📚 API Documentation: http://localhost:5001/api/docs")
print(f"💚 Health Check: http://localhost:5001/health")
print(f"📁 Project Root: {PROJECT_ROOT}")

# CORRECTED Directory setup based on your actual folder structure
COMPLETE_GAME_CONTENT_FOLDER = PROJECT_ROOT / "complete_game_content"  # This is where orchestrator saves
GODOT_EXPORTS_FOLDER = PROJECT_ROOT / "godot_exports"  # This is where Godot packages are saved
DOWNLOAD_FOLDER = PROJECT_ROOT / "web_app" / "downloads"
TEMPLATES_FOLDER = PROJECT_ROOT / "web_app" / "templates"

print(f"📁 Complete Game Content: {COMPLETE_GAME_CONTENT_FOLDER}")
print(f"📁 Godot Exports: {GODOT_EXPORTS_FOLDER}")
print(f"📁 Templates Folder: {TEMPLATES_FOLDER}")

# Create necessary directories
COMPLETE_GAME_CONTENT_FOLDER.mkdir(exist_ok=True)
GODOT_EXPORTS_FOLDER.mkdir(exist_ok=True)
DOWNLOAD_FOLDER.mkdir(exist_ok=True)
TEMPLATES_FOLDER.mkdir(exist_ok=True)

# Initialize Flask app
app = Flask(__name__, template_folder=str(TEMPLATES_FOLDER))

# Generation job tracking
generation_jobs = {}

class GenerationJob:
    def __init__(self, generation_id: str, prompt: str):
        self.generation_id = generation_id
        self.prompt = prompt
        self.status = 'starting'  # starting, in_progress, completed, failed
        self.progress = 0  # 0-100
        self.message = 'Initializing...'
        self.error = None
        self.created_at = datetime.now()
        self.godot_download_url = None
        self.assets_download_url = None
        self.result_data = None
        
        # Individual agent tracking
        self.agents = {
            'world': {'status': 'pending', 'message': 'Waiting to start...'},
            'assets': {'status': 'pending', 'message': 'Waiting to start...'},
            'characters': {'status': 'pending', 'message': 'Waiting to start...'},
            'quests': {'status': 'pending', 'message': 'Waiting to start...'},
            'balance': {'status': 'pending', 'message': 'Waiting to start...'},
            'export': {'status': 'pending', 'message': 'Waiting to start...'}
        }
        
        # Detailed generation results
        self.generation_details = {
            'world': None,
            'assets': None, 
            'characters': None,
            'quests': None,
            'balance': None,
            'files': None,
            'godot_project_info': None
        }

def clear_existing_generated_content():
    """Clear existing folders in complete_game_content directory"""
    try:
        if not COMPLETE_GAME_CONTENT_FOLDER.exists():
            print("📁 Complete game content folder doesn't exist, creating...")
            COMPLETE_GAME_CONTENT_FOLDER.mkdir(exist_ok=True)
            return
            
        print("🧹 Clearing existing content in complete_game_content folder...")
        
        # List all items before clearing
        existing_items = list(COMPLETE_GAME_CONTENT_FOLDER.iterdir())
        if not existing_items:
            print("📂 Complete game content folder is already empty")
            return
            
        print(f"🗑️ Found {len(existing_items)} existing items to clear:")
        for item in existing_items:
            print(f"   - {item.name}")
        
        # Remove all existing items
        for item in existing_items:
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"✅ Removed directory: {item.name}")
                else:
                    item.unlink()
                    print(f"✅ Removed file: {item.name}")
            except Exception as e:
                print(f"⚠️ Warning: Could not remove {item.name}: {e}")
        
        print("🎉 Successfully cleared existing complete game content!")
        
    except Exception as e:
        print(f"❌ Error clearing complete game content: {e}")

def run_orchestrator_sync(prompt: str, job: GenerationJob):
    """
    Run orchestrator synchronously in a way that works with Flask threading
    This matches exactly how your working Python command runs
    """
    try:
        print(f"🚀 Starting orchestrator for prompt: {prompt[:100]}...")
        job.progress = 15
        job.message = 'Importing orchestrator...'
        
        # Import exactly as your working command does
        from orchestrator.agent import CompleteGameContentOrchestrator
        
        print(f"🎯 Creating orchestrator instance...")
        job.progress = 20
        job.message = 'Creating orchestrator instance...'
        
        # Create orchestrator instance
        orchestrator = CompleteGameContentOrchestrator()
        
        print(f"🎮 Running orchestrator for: {prompt}")
        job.progress = 25
        job.message = 'Running orchestrator pipeline...'
        
        # Update first agent
        job.agents['world']['status'] = 'active'
        job.agents['world']['message'] = 'Starting world generation...'
        
        # This is the key fix: Run asyncio.run() in the same thread context
        # exactly like your working Python command
        def run_async_in_thread():
            # Create new event loop for this thread
            asyncio.set_event_loop(asyncio.new_event_loop())
            
            # Run the orchestrator exactly like your working command
            result = asyncio.run(
                orchestrator.generate_complete_game_content(
                    prompt=prompt,
                    character_count=5,
                    quest_count=3
                )
            )
            return result
        
        # Execute the async call
        result = run_async_in_thread()
        
        print(f"✅ Orchestrator completed!")
        #print(f"📊 Result: {result}")
        
        # Update agent statuses based on result
        if result and hasattr(result, 'status'):
            print(f"🎯 Result status: {result.status}")
            
            if result.status == "success":
                # Mark all agents as completed for successful run
                for agent_key in job.agents:
                    job.agents[agent_key]['status'] = 'completed'
                    job.agents[agent_key]['message'] = 'Completed successfully!'
                
                # Check specific components
                if hasattr(result, 'output_directory'):
                    print(f"📁 Output directory: {result.output_directory}")
                    
            else:
                # Mark as failed
                for agent_key in job.agents:
                    job.agents[agent_key]['status'] = 'failed'
                    job.agents[agent_key]['message'] = f'Pipeline failed: {result.status}'
        else:
            print("⚠️ No result or invalid result structure")
            for agent_key in job.agents:
                job.agents[agent_key]['status'] = 'failed'
                job.agents[agent_key]['message'] = 'No valid result returned'
        
        return result
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"💡 Current working directory: {os.getcwd()}")
        print(f"💡 Python path includes: {PROJECT_ROOT}")
        
        for agent_key in job.agents:
            job.agents[agent_key]['status'] = 'failed'
            job.agents[agent_key]['message'] = f'Import error: {str(e)}'
        
        raise Exception(f"Could not import orchestrator: {e}")
        
    except Exception as e:
        print(f"❌ Pipeline execution error: {e}")
        import traceback
        traceback.print_exc()
        
        for agent_key in job.agents:
            job.agents[agent_key]['status'] = 'failed'
            job.agents[agent_key]['message'] = f'Execution error: {str(e)}'
        
        raise Exception(f"Pipeline failed: {e}")

def run_generation_pipeline(generation_id: str, prompt: str):
    """Run the REAL generation pipeline - NO SIMULATION!"""
    job = generation_jobs.get(generation_id)
    if not job:
        print(f"❌ Job {generation_id} not found")
        return
    
    try:
        print(f"🚀 Running REAL pipeline for generation {generation_id}")
        print(f"📝 Prompt: {prompt}")
        
        job.status = 'in_progress'
        job.progress = 10
        job.message = 'Starting real orchestrator...'
        
        # Change to project root directory (like your working command)
        original_cwd = os.getcwd()
        try:
            os.chdir(PROJECT_ROOT)
            print(f"📁 Changed to project root: {PROJECT_ROOT}")
            
            # Call orchestrator
            result = run_orchestrator_sync(prompt, job)
            job.result_data = result
            
            job.progress = 85
            job.message = 'Processing generated content...'
            
            # Load generation details if content was created
            # Look in COMPLETE_GAME_CONTENT_FOLDER (the correct folder)
            session_dirs = list(COMPLETE_GAME_CONTENT_FOLDER.glob('*'))
            if session_dirs:
                most_recent_session = max(session_dirs, key=lambda p: p.stat().st_mtime)
                print(f"📂 Loading details from: {most_recent_session}")
                load_generation_details(most_recent_session, job)
            else:
                print("⚠️ No session directories found in complete_game_content")
            
        finally:
            # Always change back to original directory
            os.chdir(original_cwd)
        
        # Mark as completed
        job.status = 'completed'
        job.progress = 100
        job.message = 'Real generation completed successfully!'
        job.godot_download_url = f'/api/download/{generation_id}/godot'
        job.assets_download_url = f'/api/download/{generation_id}/assets'
        
        print(f"✅ Generation {generation_id} completed successfully!")
        
    except Exception as e:
        job.status = 'failed'
        job.error = str(e)
        job.message = f'Generation failed: {str(e)}'
        print(f"❌ Generation {generation_id} failed: {e}")
        import traceback
        traceback.print_exc()

def load_generation_details(session_dir: Path, job: GenerationJob):
    """Load detailed generation information from session directory"""
    try:
        print(f"📋 Loading generation details from: {session_dir}")
        
        # Load world specification
        world_file = session_dir / "world_spec.json"
        if world_file.exists():
            with open(world_file, 'r') as f:
                job.generation_details['world'] = json.load(f)
            print(f"✅ Loaded world spec: {len(job.generation_details['world'].get('buildings', []))} buildings")
        
        # Load assets information
        assets_file = session_dir / "ai_creative_manifest.json"
        if assets_file.exists():
            with open(assets_file, 'r') as f:
                job.generation_details['assets'] = json.load(f)
            print(f"✅ Loaded assets manifest")
        
        # Load characters
        characters_file = session_dir / "character_profiles.json"
        if characters_file.exists():
            with open(characters_file, 'r') as f:
                job.generation_details['characters'] = json.load(f)
            print(f"✅ Loaded characters: {len(job.generation_details['characters'].get('characters', []))} characters")
        
        # Load quests
        quests_file = session_dir / "quest_system.json"
        if quests_file.exists():
            with open(quests_file, 'r') as f:
                job.generation_details['quests'] = json.load(f)
            print(f"✅ Loaded quests: {len(job.generation_details['quests'].get('quests', []))} quests")
        
        # Load balance report
        balance_file = session_dir / "balance_report.json"
        if balance_file.exists():
            with open(balance_file, 'r') as f:
                job.generation_details['balance'] = json.load(f)
            print(f"✅ Loaded balance report")
        
        # Create file structure overview
        job.generation_details['files'] = create_file_structure_overview(session_dir)
        
        # Check for Godot project info
        godot_info_file = session_dir / "godot_export_info.json"
        if godot_info_file.exists():
            with open(godot_info_file, 'r') as f:
                job.generation_details['godot_project_info'] = json.load(f)
            print(f"✅ Found Godot project info")
        
    except Exception as e:
        print(f"⚠️ Error loading generation details: {e}")

def create_file_structure_overview(session_dir: Path) -> Dict[str, Any]:
    """Create a file structure overview for the UI"""
    try:
        def build_tree(path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict:
            if current_depth >= max_depth:
                return {}
            
            tree = {}
            try:
                for item in sorted(path.iterdir()):
                    if item.is_dir():
                        tree[item.name] = build_tree(item, max_depth, current_depth + 1)
                    else:
                        tree[item.name] = f"file ({item.stat().st_size} bytes)"
            except PermissionError:
                tree["<access_denied>"] = "Permission denied"
            return tree
        
        file_structure = build_tree(session_dir)
        total_files = sum(1 for _ in session_dir.rglob('*') if _.is_file())
        
        return {
            'file_structure': file_structure,
            'total_files_generated': total_files,
            'session_directory': str(session_dir)
        }
    except Exception as e:
        print(f"⚠️ Error creating file structure overview: {e}")
        return {'error': str(e)}

def find_godot_package(generation_id: str) -> Optional[Path]:
    """Find the Godot package for a generation"""
    try:
        print(f"🔍 Looking for Godot package for generation: {generation_id}")
        
        # Look for pre-built packages in downloads folder
        for package in DOWNLOAD_FOLDER.glob(f'*{generation_id[:8]}*'):
            if package.suffix.lower() == '.zip' and 'godot' in package.name.lower():
                print(f"📦 Found existing Godot package: {package}")
                return package
        
        # Look for recent Godot exports in godot_exports folder
        if GODOT_EXPORTS_FOLDER.exists():
            godot_projects = list(GODOT_EXPORTS_FOLDER.glob('GodotProject_*'))
            if godot_projects:
                # Get most recent one
                most_recent_godot = max(godot_projects, key=lambda p: p.stat().st_mtime)
                print(f"📂 Found recent Godot project: {most_recent_godot}")
                return create_godot_package(most_recent_godot, generation_id)
        
        # Look for Godot project directories in complete_game_content
        for session_dir in COMPLETE_GAME_CONTENT_FOLDER.iterdir():
            if session_dir.is_dir():
                # Look for Godot project reference
                godot_info_file = session_dir / "godot_export_info.json"
                if godot_info_file.exists():
                    try:
                        with open(godot_info_file, 'r') as f:
                            godot_info = json.load(f)
                        if 'project_path' in godot_info:
                            godot_path = Path(godot_info['project_path'])
                            if godot_path.exists():
                                print(f"📂 Found Godot project from info: {godot_path}")
                                return create_godot_package(godot_path, generation_id)
                    except Exception as e:
                        print(f"⚠️ Error reading Godot info: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ Error finding Godot package: {e}")
        return None

def find_assets_content(generation_id: str) -> Optional[Path]:
    """Find the complete assets/content for a generation"""
    try:
        print(f"🔍 Looking for assets content for generation: {generation_id}")
        
        # Look for pre-built assets packages in downloads folder
        for package in DOWNLOAD_FOLDER.glob(f'*{generation_id[:8]}*'):
            if package.suffix.lower() == '.zip' and 'assets' in package.name.lower():
                print(f"📦 Found existing assets package: {package}")
                return package
        
        # Look for complete content in complete_game_content folder
        session_dirs = list(COMPLETE_GAME_CONTENT_FOLDER.glob('*'))
        if session_dirs:
            most_recent_session = max(session_dirs, key=lambda p: p.stat().st_mtime)
            print(f"📂 Found complete content directory: {most_recent_session}")
            return create_assets_package(most_recent_session, generation_id)
        
        return None
        
    except Exception as e:
        print(f"❌ Error finding assets content: {e}")
        return None

def create_godot_package(godot_dir: Path, generation_id: str) -> Path:
    """Create a downloadable Godot package"""
    try:
        package_name = f'GodotProject_{generation_id[:8]}.zip'
        package_path = DOWNLOAD_FOLDER / package_name
        
        print(f"📦 Creating Godot package from: {godot_dir}")
        
        # Create zip file
        shutil.make_archive(str(package_path.with_suffix('')), 'zip', str(godot_dir))
        
        if package_path.exists():
            size_mb = package_path.stat().st_size / (1024 * 1024)
            print(f"✅ Godot package created: {package_path} ({size_mb:.2f} MB)")
            return package_path
        else:
            print(f"❌ Godot package creation failed")
            return None
        
    except Exception as e:
        print(f"❌ Error creating Godot package: {e}")
        return None

def create_assets_package(content_dir: Path, generation_id: str) -> Path:
    """Create a downloadable assets package from complete content"""
    try:
        package_name = f'GameAssets_{generation_id[:8]}.zip'
        package_path = DOWNLOAD_FOLDER / package_name
        
        print(f"📦 Creating assets package from: {content_dir}")
        
        # Create zip file
        shutil.make_archive(str(package_path.with_suffix('')), 'zip', str(content_dir))
        
        if package_path.exists():
            size_mb = package_path.stat().st_size / (1024 * 1024)
            print(f"✅ Assets package created: {package_path} ({size_mb:.2f} MB)")
            return package_path
        else:
            return None
        
    except Exception as e:
        print(f"❌ Error creating assets package: {e}")
        return None

# Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <h1>Oyun Generator</h1>
        <p>Template not found. Please save your HTML as {TEMPLATES_FOLDER}/index.html</p>
        <p>Error: {e}</p>
        <p><a href="/health">Health Check</a> | <a href="/api/docs">API Docs</a></p>
        """

@app.route('/api/generate', methods=['POST'])
def start_generation():
    """Start a new game generation - REAL VERSION"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if len(prompt) < 10:
            return jsonify({'error': 'Please provide a more detailed prompt (at least 10 characters)'}), 400
        
        # Clear existing content
        clear_existing_generated_content()
        
        # Create new generation job
        generation_id = str(uuid.uuid4())
        job = GenerationJob(generation_id, prompt)
        generation_jobs[generation_id] = job
        
        print(f"🚀 Starting REAL generation {generation_id} for prompt: {prompt[:100]}...")
        
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
            'message': 'Real generation started successfully'
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
    
    return jsonify({
        'generation_id': generation_id,
        'status': job.status,
        'progress': job.progress,
        'message': job.message,
        'error': job.error,
        'agents': job.agents,
        'generation_details': job.generation_details,
        'godot_download_url': job.godot_download_url,
        'assets_download_url': job.assets_download_url,
        'created_at': job.created_at.isoformat()
    })

@app.route('/api/download/<generation_id>/<download_type>')
def download_package(generation_id, download_type):
    """Download the generated package - godot or assets"""
    job = generation_jobs.get(generation_id)
    
    if not job:
        return jsonify({'error': 'Generation not found'}), 404
    
    if job.status != 'completed':
        return jsonify({'error': f'Package not ready. Status: {job.status}'}), 400
    
    print(f"🔍 Download request for generation: {generation_id}, type: {download_type}")
    
    if download_type == 'godot':
        # Find Godot package
        package_path = find_godot_package(generation_id)
        download_name = f'GodotProject_{generation_id[:8]}.zip'
        
    elif download_type == 'assets':
        # Find assets package
        package_path = find_assets_content(generation_id)
        download_name = f'GameAssets_{generation_id[:8]}.zip'
        
    else:
        return jsonify({'error': 'Invalid download type. Use "godot" or "assets"'}), 400
    
    if not package_path or not package_path.exists():
        print(f"❌ No {download_type} package found for generation {generation_id}")
        return jsonify({'error': f'No {download_type} package available'}), 404
    
    print(f"✅ Sending {download_type} package: {package_path}")
    
    try:
        return send_file(
            package_path,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as send_error:
        print(f"❌ Error sending file: {send_error}")
        return jsonify({'error': f'Failed to send {download_type} package file'}), 500

@app.route('/api/game-data')
def get_game_data():
    """Get detailed game data for UI display"""
    try:
        # Find the most recent generation
        if not generation_jobs:
            return jsonify({'error': 'No generations available'}), 404
        
        # Get the most recent completed job
        completed_jobs = [job for job in generation_jobs.values() if job.status == 'completed']
        if not completed_jobs:
            return jsonify({'error': 'No completed generations available'}), 404
        
        latest_job = max(completed_jobs, key=lambda j: j.created_at)
        
        return jsonify({
            'generation_id': latest_job.generation_id,
            'prompt': latest_job.prompt,
            'status': latest_job.status,
            'world': latest_job.generation_details.get('world'),
            'assets': latest_job.generation_details.get('assets'),
            'characters': latest_job.generation_details.get('characters'),
            'quests': latest_job.generation_details.get('quests'),
            'balance': latest_job.generation_details.get('balance'),
            'files': latest_job.generation_details.get('files'),
            'godot_project_info': latest_job.generation_details.get('godot_project_info'),
            'godot_download_url': latest_job.godot_download_url,
            'assets_download_url': latest_job.assets_download_url
        })
        
    except Exception as e:
        print(f"❌ Error getting game data: {e}")
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    orchestrator_status = "unknown"
    try:
        from orchestrator.agent import CompleteGameContentOrchestrator
        orchestrator_status = "available"
    except Exception as e:
        orchestrator_status = f"failed: {e}"
    
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'version': '2.2.0-fixed-paths-assets',
        'project_root': str(PROJECT_ROOT),
        'complete_game_content_folder': str(COMPLETE_GAME_CONTENT_FOLDER),
        'godot_exports_folder': str(GODOT_EXPORTS_FOLDER),
        'templates_folder': str(TEMPLATES_FOLDER),
        'orchestrator_status': orchestrator_status,
        'mode': 'real_orchestrator_fixed_paths'
    })

# API documentation endpoint
@app.route('/api/docs')
def api_docs():
    docs = {
        'title': 'Oyun Generator API - Fixed Paths and Asset Downloads',
        'version': '2.2.0-fixed-paths-assets',
        'description': 'Generate complete Godot game worlds from text descriptions',
        'working_test_command': 'python -c "import asyncio; from orchestrator.agent import CompleteGameContentOrchestrator; orchestrator = CompleteGameContentOrchestrator(); result = asyncio.run(orchestrator.generate_complete_game_content(\'test village\')); print(f\'Success: {result.status}\')"',
        'endpoints': {
            'POST /api/generate': {
                'description': 'Start REAL Godot game generation from text prompt',
                'body': {'prompt': 'string (required)'},
                'response': {'generation_id': 'string', 'status': 'string', 'message': 'string'}
            },
            'GET /api/progress/{id}': {
                'description': 'Get real-time generation progress and agent status',
                'response': {
                    'status': 'string (starting|in_progress|completed|failed)',
                    'progress': 'number (0-100)',
                    'message': 'string',
                    'agents': 'object (real agent statuses)',
                    'generation_details': 'object (actual generated content)',
                    'godot_download_url': 'string (when completed)',
                    'assets_download_url': 'string (when completed)'
                }
            },
            'GET /api/download/{id}/godot': {
                'description': 'Download the Godot project package',
                'response': 'ZIP file containing Godot project'
            },
            'GET /api/download/{id}/assets': {
                'description': 'Download the complete assets package',
                'response': 'ZIP file containing all generated content'
            }
        },
        'fixes_in_v2_2_0': [
            'Fixed folder paths to use complete_game_content and godot_exports',
            'Added separate asset download functionality',
            'Enhanced file structure overview',
            'Better package detection and creation'
        ]
    }
    return jsonify(docs)

if __name__ == '__main__':
    print(f"{'='*80}")
    print(f"🎨 Oyun Generator - Fixed Paths & Asset Downloads v2.2.0")
    print(f"{'='*80}")
    print(f"🏗️ REAL ORCHESTRATOR: Direct calls, matching working command")
    print(f"📁 FIXED PATHS: Using correct complete_game_content and godot_exports folders")
    print(f"📦 DUAL DOWNLOADS: Separate Godot project and assets packages")
    print(f"📁 Project structure detected:")
    print(f"   📂 {PROJECT_ROOT}")
    print(f"   ├── orchestrator/")
    print(f"   ├── web_app/")
    print(f"   ├── complete_game_content/")
    print(f"   └── godot_exports/")
    
    # Test orchestrator import
    try:
        print(f"🔍 Testing orchestrator import...")
        from orchestrator.agent import CompleteGameContentOrchestrator
        print(f"✅ Orchestrator import successful")
    except Exception as e:
        print(f"❌ Orchestrator import failed: {e}")
        print(f"💡 The web app will still run, but generation will fail")
    
    # Check HTML template
    template_path = TEMPLATES_FOLDER / "index.html"
    if template_path.exists():
        print(f"✅ HTML template found: {template_path}")
    else:
        print(f"⚠️ HTML template missing: {template_path}")
        print(f"💡 Save your HTML content as: {template_path}")
    
    # Check folder structure
    print(f"📁 Checking folder structure:")
    print(f"   Complete Game Content: {'✅' if COMPLETE_GAME_CONTENT_FOLDER.exists() else '❌'} {COMPLETE_GAME_CONTENT_FOLDER}")
    print(f"   Godot Exports: {'✅' if GODOT_EXPORTS_FOLDER.exists() else '❌'} {GODOT_EXPORTS_FOLDER}")
    print(f"   Downloads: {'✅' if DOWNLOAD_FOLDER.exists() else '❌'} {DOWNLOAD_FOLDER}")
    
    print(f"🎮 Ready to generate Godot game worlds with dual download options!")
    print(f"💡 This version uses the correct folder paths from your orchestrator")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)