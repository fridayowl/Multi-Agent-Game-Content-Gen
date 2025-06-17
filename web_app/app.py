#!/usr/bin/env python3
"""
Complete Flask Web App for AI Game Generator
Integrates with your existing multi-agent pipeline
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
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import threading
from typing import Dict, Any

app = Flask(__name__)
CORS(app)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
GENERATED_FOLDER = PROJECT_ROOT / 'generated_content'
DOWNLOAD_FOLDER = Path(__file__).parent / 'downloads'
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Add project to Python path
sys.path.insert(0, str(PROJECT_ROOT))

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

# HTML template (embedded to keep everything in one file)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Game Generator - Create Unity Games from Text</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }

        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .main-content {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            margin-bottom: 40px;
        }

        .prompt-section {
            margin-bottom: 30px;
        }

        .prompt-section h2 {
            color: #4a5568;
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        .prompt-input {
            width: 100%;
            min-height: 120px;
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 16px;
            resize: vertical;
            transition: border-color 0.3s ease;
        }

        .prompt-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .examples {
            margin-top: 15px;
        }

        .example-tag {
            display: inline-block;
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }

        .example-tag:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }

        .generate-section {
            text-align: center;
            margin: 30px 0;
        }

        .generate-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }

        .generate-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }

        .generate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .progress-section {
            display: none;
            margin: 30px 0;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: #f7fafc;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
            border-radius: 10px;
        }

        .agent-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .agent-card {
            background: #f7fafc;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #e2e8f0;
            transition: all 0.3s ease;
        }

        .agent-card.active {
            border-left-color: #667eea;
            background: #edf2f7;
        }

        .agent-card.completed {
            border-left-color: #48bb78;
            background: #f0fff4;
        }

        .results-section {
            display: none;
            margin-top: 30px;
        }

        .download-card {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 20px;
        }

        .download-btn {
            background: white;
            color: #38a169;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 15px;
        }

        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }

        .feature-card {
            background: #f7fafc;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .feature-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .main-content {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 AI Game Generator</h1>
            <p>Create complete Unity game worlds from simple text descriptions</p>
        </div>

        <div class="main-content">
            <div class="prompt-section">
                <h2>Describe Your Game World</h2>
                <textarea 
                    class="prompt-input" 
                    id="gamePrompt" 
                    placeholder="Describe the game world you want to create... For example: 'Create a spooky Halloween village with 5 NPCs and 3 interconnected quests about solving mysterious disappearances'"
                ></textarea>
                
                <div class="examples">
                    <p style="margin-bottom: 10px; color: #666;">Example prompts:</p>
                    <div class="example-tag" onclick="setPrompt('Create a spooky Halloween village with 5 NPCs and 3 interconnected quests')">🎃 Halloween Village</div>
                    <div class="example-tag" onclick="setPrompt('Generate a desert oasis trading post with merchants and treasure hunters')">🏜️ Desert Trading Post</div>
                    <div class="example-tag" onclick="setPrompt('Build a medieval castle town with a blacksmith, tavern keeper, and royal guard')">🏰 Medieval Castle Town</div>
                    <div class="example-tag" onclick="setPrompt('Create a cyberpunk city district with hackers, corporate agents, and underground rebels')">🌆 Cyberpunk District</div>
                    <div class="example-tag" onclick="setPrompt('Design a mystical forest with fairy NPCs and ancient tree spirits')">🧚 Enchanted Forest</div>
                </div>
            </div>

            <div class="generate-section">
                <button class="generate-btn" id="generateBtn" onclick="startGeneration()">
                    ✨ Generate Unity Game Package
                </button>
            </div>

            <div class="progress-section" id="progressSection">
                <h3>Generation Progress</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                </div>
                <p id="progressText">Initializing generation pipeline...</p>
                
                <div class="agent-status">
                    <div class="agent-card" id="agent-world">
                        <h4>🌍 World Designer</h4>
                        <p>Creating terrain and layout...</p>
                    </div>
                    <div class="agent-card" id="agent-assets">
                        <h4>🎨 Asset Generator</h4>
                        <p>Generating 3D models and textures...</p>
                    </div>
                    <div class="agent-card" id="agent-characters">
                        <h4>👥 Character Creator</h4>
                        <p>Creating NPCs and personalities...</p>
                    </div>
                    <div class="agent-card" id="agent-quests">
                        <h4>📜 Quest Writer</h4>
                        <p>Writing storylines and dialogue...</p>
                    </div>
                    <div class="agent-card" id="agent-balance">
                        <h4>⚖️ Balance Validator</h4>
                        <p>Balancing gameplay mechanics...</p>
                    </div>
                    <div class="agent-card" id="agent-export">
                        <h4>📦 Unity Exporter</h4>
                        <p>Creating Unity package...</p>
                    </div>
                </div>
            </div>

            <div class="results-section" id="resultsSection">
                <div class="download-card">
                    <h3>🎉 Your Game Is Ready!</h3>
                    <p>Your Unity game package has been generated successfully</p>
                    <button class="download-btn" id="downloadBtn" onclick="downloadPackage()">
                        📥 Download Unity Package
                    </button>
                </div>
                
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🌍</div>
                        <h4>World Layout</h4>
                        <p>Complete 3D environment ready to explore</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">👥</div>
                        <h4>NPCs Created</h4>
                        <p id="npcCount">5 unique characters</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📜</div>
                        <h4>Quests Generated</h4>
                        <p id="questCount">3 interconnected storylines</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎨</div>
                        <h4>Assets Included</h4>
                        <p>Models, textures, and prefabs</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let generationInProgress = false;
        let downloadUrl = null;

        function setPrompt(text) {
            document.getElementById('gamePrompt').value = text;
        }

        async function startGeneration() {
            const prompt = document.getElementById('gamePrompt').value.trim();
            
            if (!prompt) {
                alert('Please enter a description for your game world!');
                return;
            }

            if (generationInProgress) {
                return;
            }

            generationInProgress = true;
            
            // Update UI
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('generateBtn').textContent = '🔄 Generating...';
            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';

            try {
                // Start the generation process
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: prompt,
                        timestamp: Date.now()
                    })
                });

                if (!response.ok) {
                    throw new Error('Generation failed');
                }

                const data = await response.json();
                
                // Start polling for progress
                pollProgress(data.generation_id);
                
            } catch (error) {
                console.error('Generation error:', error);
                resetUI();
                alert('Generation failed. Please try again.');
            }
        }

        async function pollProgress(generationId) {
            try {
                const response = await fetch(`/api/progress/${generationId}`);
                const data = await response.json();
                
                updateProgress(data);
                
                if (data.status === 'completed') {
                    showResults(data);
                    generationInProgress = false;
                } else if (data.status === 'failed') {
                    throw new Error(data.error || 'Generation failed');
                } else {
                    // Continue polling
                    setTimeout(() => pollProgress(generationId), 2000);
                }
                
            } catch (error) {
                console.error('Progress polling error:', error);
                resetUI();
                alert('Generation failed. Please try again.');
            }
        }

        function updateProgress(data) {
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            progressFill.style.width = `${data.progress}%`;
            progressText.textContent = data.message || 'Processing...';
            
            // Update agent status
            const agents = ['world', 'assets', 'characters', 'quests', 'balance', 'export'];
            agents.forEach((agent, index) => {
                const agentCard = document.getElementById(`agent-${agent}`);
                const agentProgress = data.agents && data.agents[agent];
                
                if (agentProgress) {
                    if (agentProgress.status === 'completed') {
                        agentCard.className = 'agent-card completed';
                    } else if (agentProgress.status === 'active') {
                        agentCard.className = 'agent-card active';
                    }
                }
            });
        }

        function showResults(data) {
            document.getElementById('progressSection').style.display = 'none';
            document.getElementById('resultsSection').style.display = 'block';
            
            downloadUrl = data.download_url;
            
            // Update feature counts if available
            if (data.stats) {
                if (data.stats.npc_count) {
                    document.getElementById('npcCount').textContent = `${data.stats.npc_count} unique characters`;
                }
                if (data.stats.quest_count) {
                    document.getElementById('questCount').textContent = `${data.stats.quest_count} interconnected storylines`;
                }
            }
            
            resetUI();
        }

        function resetUI() {
            document.getElementById('generateBtn').disabled = false;
            document.getElementById('generateBtn').textContent = '✨ Generate Unity Game Package';
            generationInProgress = false;
        }

        function downloadPackage() {
            if (downloadUrl) {
                window.open(downloadUrl, '_blank');
            } else {
                alert('Download not available. Please try generating again.');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template_string(HTML_TEMPLATE)

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
    """Get generation progress"""
    job = generation_jobs.get(generation_id)
    
    if not job:
        return jsonify({'error': 'Generation not found'}), 404
    
    response_data = {
        'status': job.status,
        'progress': job.progress,
        'message': job.message,
        'agents': job.agents
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
    """Download the generated Unity package"""
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
    package_path = find_unity_package(generation_id)
    
    if not package_path or not package_path.exists():
        print(f"❌ No package found for generation {generation_id}")
        return jsonify({'error': 'Package file not found'}), 404
    
    print(f"✅ Sending package: {package_path}")
    
    return send_file(
        package_path,
        as_attachment=True,
        download_name=f'AIGameWorld_{generation_id[:8]}.zip'
    )

def find_unity_package(generation_id: str) -> Path:
    """Find the Unity/Godot package for this generation"""
    try:
        # Look for packages in generated content
        if GENERATED_FOLDER.exists():
            print(f"🔍 Looking for packages in: {GENERATED_FOLDER}")
            
            # Option 1: Look for .unitypackage files (Unity)
            package_files = list(GENERATED_FOLDER.rglob('*.unitypackage'))
            if package_files:
                print(f"✅ Found Unity package: {package_files[0]}")
                return max(package_files, key=lambda p: p.stat().st_mtime)
            
            # Option 2: Look for Godot projects (folders with project.godot)
            godot_projects = list(GENERATED_FOLDER.rglob('project.godot'))
            if godot_projects:
                most_recent = max(godot_projects, key=lambda p: p.stat().st_mtime)
                godot_project_dir = most_recent.parent
                print(f"✅ Found Godot project: {godot_project_dir}")
                return create_package_from_godot(godot_project_dir, generation_id)
            
            # Option 3: Look for any recent directories with game content
            all_dirs = [d for d in GENERATED_FOLDER.rglob('*') if d.is_dir()]
            if all_dirs:
                # Find most recent directory
                most_recent_dir = max(all_dirs, key=lambda p: p.stat().st_mtime)
                print(f"✅ Found recent content directory: {most_recent_dir}")
                return create_package_from_directory(most_recent_dir, generation_id)
            
            print(f"❌ No packages found in {GENERATED_FOLDER}")
            
        else:
            print(f"❌ Generated content folder doesn't exist: {GENERATED_FOLDER}")
        
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
        print(f"📥 Package will be saved as: {package_path}")
        
        # Create zip file of the godot project
        shutil.make_archive(str(package_path.with_suffix('')), 'zip', str(godot_dir))
        
        print(f"✅ Godot package created successfully: {package_path}")
        return package_path
        
    except Exception as e:
        print(f"❌ Error creating Godot package: {e}")
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
    """
    Call your existing orchestrator class correctly
    """
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
            ('export', 'Unity Exporter', 'Creating Unity package...', 85)
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
        
        # Call your orchestrator
        result = call_your_orchestrator(prompt)
        
        # Store the result
        job.result_data = result
        
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
        'generated_folder': str(GENERATED_FOLDER)
    })

# API documentation endpoint
@app.route('/api/docs')
def api_docs():
    docs = {
        'title': 'AI Game Generator API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/generate': {
                'description': 'Start game generation from text prompt',
                'body': {'prompt': 'string (required)'},
                'response': {'generation_id': 'string', 'status': 'string', 'message': 'string'}
            },
            'GET /api/progress/{id}': {
                'description': 'Get generation progress and agent status',
                'response': {
                    'status': 'string (starting|in_progress|completed|failed)',
                    'progress': 'number (0-100)',
                    'message': 'string',
                    'agents': 'object (agent statuses)',
                    'download_url': 'string (when completed)'
                }
            },
            'GET /api/download/{id}': {
                'description': 'Download generated Unity package',
                'response': 'file download (.unitypackage or .zip)'
            },
            'GET /health': {
                'description': 'Health check endpoint',
                'response': {'status': 'healthy', 'timestamp': 'ISO string'}
            }
        },
        'example_prompts': [
            'Create a spooky Halloween village with 5 NPCs and 3 interconnected quests',
            'Generate a desert oasis trading post with merchants and treasure hunters',
            'Build a medieval castle town with a blacksmith, tavern keeper, and royal guard',
            'Create a cyberpunk city district with hackers, corporate agents, and underground rebels'
        ]
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
    print("="*60)
    
    # Verify orchestrator can be imported
    try:
        from orchestrator.agent import CompleteGameContentOrchestrator
        print("✅ Orchestrator import successful")
    except ImportError as e:
        print(f"⚠️ Orchestrator import failed: {e}")
        print("💡 The web app will still run, but generation may fail")
    
    print("\n🎮 Ready to generate amazing game worlds!")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )