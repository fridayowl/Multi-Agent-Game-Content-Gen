#!/usr/bin/env python3
"""
Fixed AI Game Generator Web App - Works with your exact folder structure
Properly handles async orchestrator calls in Flask threading context
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

print(f"🚀 AI Game Generator Web App Starting...")
print(f"{'='*60}")
print(f"🌐 Web Interface: http://localhost:5001")
print(f"📚 API Documentation: http://localhost:5001/api/docs")
print(f"💚 Health Check: http://localhost:5001/health")
print(f"📁 Project Root: {PROJECT_ROOT}")

# Directory setup based on your folder structure
GENERATED_FOLDER = PROJECT_ROOT / "generated_content"
DOWNLOAD_FOLDER = PROJECT_ROOT / "web_app" / "downloads"
TEMPLATES_FOLDER = PROJECT_ROOT / "web_app" / "templates"

print(f"📁 Generated Content: {GENERATED_FOLDER}")
print(f"📁 Templates Folder: {TEMPLATES_FOLDER}")

# Create necessary directories
GENERATED_FOLDER.mkdir(exist_ok=True)
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
        self.download_url = None
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
            'package_info': None
        }

def clear_existing_generated_content():
    """Clear existing folders in generated_content directory"""
    try:
        if not GENERATED_FOLDER.exists():
            print("📁 Generated content folder doesn't exist, creating...")
            GENERATED_FOLDER.mkdir(exist_ok=True)
            return
            
        print("🧹 Clearing existing content in generated_content folder...")
        
        # List all items before clearing
        existing_items = list(GENERATED_FOLDER.iterdir())
        if not existing_items:
            print("📂 Generated content folder is already empty")
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
        
        print("🎉 Successfully cleared existing generated content!")
        
    except Exception as e:
        print(f"❌ Error clearing generated content: {e}")

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
        print(f"📊 Result: {result}")
        
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
            session_dirs = list(GENERATED_FOLDER.glob('*'))
            if session_dirs:
                most_recent_session = max(session_dirs, key=lambda p: p.stat().st_mtime)
                print(f"📂 Loading details from: {most_recent_session}")
                load_generation_details(most_recent_session, job)
            else:
                print("⚠️ No session directories found in generated_content")
            
        finally:
            # Always change back to original directory
            os.chdir(original_cwd)
        
        # Mark as completed
        job.status = 'completed'
        job.progress = 100
        job.message = 'Real generation completed successfully!'
        job.download_url = f'/api/download/{generation_id}'
        
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
        
        # Check for Godot project
        godot_dir = session_dir / "godot_project"
        if godot_dir.exists():
            job.generation_details['package_info'] = {
                'godot_project_exists': True,
                'godot_project_path': str(godot_dir),
                'files_count': len(list(godot_dir.rglob('*')))
            }
            print(f"✅ Found Godot project: {job.generation_details['package_info']['files_count']} files")
        
    except Exception as e:
        print(f"⚠️ Error loading generation details: {e}")

def find_godot_package(generation_id: str) -> Optional[Path]:
    """Find the Godot package for a generation"""
    try:
        # Look for pre-built packages in downloads folder
        for package in DOWNLOAD_FOLDER.glob(f'*{generation_id[:8]}*'):
            if package.suffix.lower() == '.zip':
                print(f"📦 Found existing package: {package}")
                return package
        
        # Look for Godot project directories to package
        for session_dir in GENERATED_FOLDER.iterdir():
            if session_dir.is_dir():
                godot_dir = session_dir / "godot_project"
                if godot_dir.exists():
                    print(f"📂 Found Godot project directory: {godot_dir}")
                    return create_package_from_godot(godot_dir, generation_id)
        
        return None
        
    except Exception as e:
        print(f"❌ Error finding package: {e}")
        return None

def create_package_from_godot(godot_dir: Path, generation_id: str) -> Path:
    """Create a downloadable package from Godot project"""
    try:
        package_name = f'GodotGameWorld_{generation_id[:8]}.zip'
        package_path = DOWNLOAD_FOLDER / package_name
        
        print(f"📦 Creating Godot package from: {godot_dir}")
        
        # Create zip file
        shutil.make_archive(str(package_path.with_suffix('')), 'zip', str(godot_dir))
        
        if package_path.exists():
            size_mb = package_path.stat().st_size / (1024 * 1024)
            print(f"✅ Godot package created: {package_path} ({size_mb:.2f} MB)")
            return package_path
        else:
            print(f"❌ Package creation failed")
            return None
        
    except Exception as e:
        print(f"❌ Error creating Godot package: {e}")
        return None

def create_package_from_directory(content_dir: Path, generation_id: str) -> Path:
    """Create a downloadable package from any content directory"""
    try:
        package_name = f'AIGameWorld_{generation_id[:8]}.zip'
        package_path = DOWNLOAD_FOLDER / package_name
        
        print(f"📦 Creating package from: {content_dir}")
        
        # Create zip file
        shutil.make_archive(str(package_path.with_suffix('')), 'zip', str(content_dir))
        
        if package_path.exists():
            size_mb = package_path.stat().st_size / (1024 * 1024)
            print(f"✅ Package created: {package_path} ({size_mb:.2f} MB)")
            return package_path
        else:
            return None
        
    except Exception as e:
        print(f"❌ Error creating package: {e}")
        return None

# Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <h1>AI Game Generator</h1>
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
        'download_url': job.download_url,
        'created_at': job.created_at.isoformat()
    })

@app.route('/api/download/<generation_id>')
def download_package(generation_id):
    """Download the generated package"""
    job = generation_jobs.get(generation_id)
    
    if not job:
        return jsonify({'error': 'Generation not found'}), 404
    
    if job.status != 'completed':
        return jsonify({'error': f'Package not ready. Status: {job.status}'}), 400
    
    print(f"🔍 Download request for generation: {generation_id}")
    
    # Find the package
    package_path = find_godot_package(generation_id)
    
    if not package_path or not package_path.exists():
        print(f"❌ No package found for generation {generation_id}")
        
        # Try to create a fallback package
        try:
            session_dirs = [d for d in GENERATED_FOLDER.iterdir() if d.is_dir()]
            if session_dirs:
                most_recent_session = max(session_dirs, key=lambda p: p.stat().st_mtime)
                package_path = create_package_from_directory(most_recent_session, generation_id)
                
                if not package_path or not package_path.exists():
                    return jsonify({'error': 'Could not create package from available content'}), 500
            else:
                return jsonify({'error': 'No content available for packaging'}), 500
                
        except Exception as fallback_error:
            print(f"❌ Fallback package creation failed: {fallback_error}")
            return jsonify({'error': 'Package file not found and fallback failed'}), 404
    
    print(f"✅ Sending package: {package_path}")
    
    try:
        return send_file(
            package_path,
            as_attachment=True,
            download_name=f'GodotGameWorld_{generation_id[:8]}.zip'
        )
    except Exception as send_error:
        print(f"❌ Error sending file: {send_error}")
        return jsonify({'error': 'Failed to send package file'}), 500

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
            'package_info': latest_job.generation_details.get('package_info')
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
        'version': '2.1.0-thread-fixed',
        'project_root': str(PROJECT_ROOT),
        'generated_folder': str(GENERATED_FOLDER),
        'templates_folder': str(TEMPLATES_FOLDER),
        'orchestrator_status': orchestrator_status,
        'mode': 'real_orchestrator_thread_fixed'
    })

# API documentation endpoint
@app.route('/api/docs')
def api_docs():
    docs = {
        'title': 'AI Game Generator API - Thread-Fixed Real Version',
        'version': '2.1.0-thread-fixed',
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
                    'download_url': 'string (when completed)'
                }
            },
            'GET /api/download/{id}': {
                'description': 'Download the generated Godot package',
                'response': 'ZIP file containing complete Godot project'
            }
        },
        'fixes_in_v2_1_0': [
            'Fixed async handling in threading context',
            'Matches working Python command execution pattern',
            'Proper event loop management per thread',
            'Enhanced error logging and debugging'
        ]
    }
    return jsonify(docs)

if __name__ == '__main__':
    print(f"{'='*80}")
    print(f"🎨 AI Game Generator - Thread-Fixed Version 2.1.0")
    print(f"{'='*80}")
    print(f"🏗️ REAL ORCHESTRATOR: Direct calls, matching working command")
    print(f"🧵 THREAD-SAFE: Proper async handling in Flask context")
    print(f"📁 Project structure detected:")
    print(f"   📂 {PROJECT_ROOT}")
    print(f"   ├── orchestrator/")
    print(f"   ├── web_app/")
    print(f"   └── generated_content/")
    
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
    
    print(f"🎮 Ready to generate Godot game worlds!")
    print(f"💡 This version matches your working Python command execution")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=True)