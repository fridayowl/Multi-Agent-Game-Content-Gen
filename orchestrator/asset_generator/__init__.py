"""
MODULAR AI CREATIVE ASSET GENERATOR - Package Initialization
Clean, maintainable modular architecture for AI-powered 3D asset generation

This package provides a complete modular system for generating unique 3D assets:
- AI Core: Central AI coordination and API management  
- Prop Generator: Natural features and props
- Building Generator: Architectural assets
- Texture Generator: AI-guided texture creation
- Environment Generator: Environmental assets and paths
- Material Library: Comprehensive material management
- Blender Integration: 3D model generation and scene setup

All modules work together through the main AICreativeAssetGenerator coordinator.
"""

from .ai_core import AICore
from .prop_generator import PropGenerator  
from .building_generator import BuildingGenerator
from .texture_generator import TextureGenerator
from .environment_generator import EnvironmentGenerator
from .material_library import MaterialLibrary
from .blender_integration import BlenderIntegration

# Import the main coordinator from agent.py
from .agent import AICreativeAssetGenerator, generate_creative_assets, get_creative_status, root_agent

# Package metadata
__version__ = "2.0.0-modular"
__author__ = "AI Creative Asset Generator Team"
__description__ = "Modular AI-powered creative asset generator for unique 3D content"

# Export main classes and functions
__all__ = [
    # Core coordinator
    'AICreativeAssetGenerator',
    'generate_creative_assets', 
    'get_creative_status',
    'root_agent',
    
    # Individual modules
    'AICore',
    'PropGenerator',
    'BuildingGenerator', 
    'TextureGenerator',
    'EnvironmentGenerator',
    'MaterialLibrary',
    'BlenderIntegration'
]

# Module information for external tools
MODULES = {
    'ai_core': {
        'class': AICore,
        'description': 'Central AI coordination and API management',
        'capabilities': ['ai_descriptions', 'material_properties', 'geometry_parameters']
    },
    'prop_generator': {
        'class': PropGenerator,
        'description': 'Natural features and environmental props',
        'capabilities': ['trees', 'rocks', 'bushes', 'wells', 'style_parameters']
    },
    'building_generator': {
        'class': BuildingGenerator,
        'description': 'Architectural assets and buildings',
        'capabilities': ['houses', 'taverns', 'churches', 'shops', 'architectural_details']
    },
    'texture_generator': {
        'class': TextureGenerator,
        'description': 'AI-guided procedural texture creation',
        'capabilities': ['procedural_textures', 'material_definitions', 'theme_variations']
    },
    'environment_generator': {
        'class': EnvironmentGenerator,
        'description': 'Environmental assets and world features',
        'capabilities': ['paths', 'water_features', 'terrain_features', 'atmospheric_elements']
    },
    'material_library': {
        'class': MaterialLibrary,
        'description': 'Comprehensive material management',
        'capabilities': ['material_catalogs', 'shader_settings', 'export_formats']
    },
    'blender_integration': {
        'class': BlenderIntegration,
        'description': '3D model generation and Blender operations',
        'capabilities': ['scene_creation', 'model_import', 'rendering', 'export']
    }
}

# Configuration constants
DEFAULT_THEMES = ['medieval', 'fantasy', 'spooky', 'desert']
SUPPORTED_ASSET_TYPES = {
    'props': ['tree', 'oak_tree', 'dead_tree', 'palm_tree', 'rock', 'stone', 'boulder', 'bush', 'shrub', 'well'],
    'buildings': ['house', 'tavern', 'church', 'shop', 'barn', 'castle', 'tower'],
    'environment': ['path', 'water_feature', 'terrain_feature', 'atmospheric_element']
}

def get_module_info(module_name: str = None):
    """Get information about available modules"""
    if module_name:
        return MODULES.get(module_name, None)
    return MODULES

def get_supported_themes():
    """Get list of supported themes"""
    return DEFAULT_THEMES.copy()

def get_supported_assets():
    """Get dictionary of supported asset types"""
    return SUPPORTED_ASSET_TYPES.copy()

def create_asset_generator(output_dir: str = "generated_assets"):
    """Factory function to create a new AICreativeAssetGenerator instance"""
    return AICreativeAssetGenerator(output_dir)

# Version check function
def check_dependencies():
    """Check if all required dependencies are available"""
    dependencies = {
        'core': True,  # Core Python modules always available
        'ai': False,
        'blender': False,
        'imaging': False
    }
    
    # Check AI dependencies
    try:
        import google.generativeai
        dependencies['ai'] = True
    except ImportError:
        pass
    
    # Check Blender dependencies  
    try:
        import bpy
        dependencies['blender'] = True
    except ImportError:
        pass
    
    # Check imaging dependencies
    try:
        from PIL import Image
        dependencies['imaging'] = True
    except ImportError:
        pass
    
    return dependencies

# Module initialization message
def print_module_info():
    """Print module information on import"""
    print("🎨 AI Creative Asset Generator - Modular Version 2.0")
    print("="*60)
    print("🏗️ MODULAR: Clean, maintainable architecture")
    print("✨ AI-POWERED: Unique assets every time")
    print("🔧 COMPREHENSIVE: Buildings, props, textures, materials")
    print("")
    
    deps = check_dependencies()
    print("📦 Module Status:")
    print(f"   ✅ Core Python modules: Ready")
    print(f"   {'✅' if deps['ai'] else '⚠️'} AI services: {'Ready' if deps['ai'] else 'Fallback mode'}")
    print(f"   {'✅' if deps['blender'] else '⚠️'} Blender API: {'Ready' if deps['blender'] else 'Script generation only'}")
    print(f"   {'✅' if deps['imaging'] else '⚠️'} Image processing: {'Ready' if deps['imaging'] else 'Limited textures'}")
    print("")
    
    print("🎯 Available Modules:")
    for module_name, module_info in MODULES.items():
        print(f"   • {module_name}: {module_info['description']}")
    print("")
    
    print("🌍 Supported Themes:", ", ".join(DEFAULT_THEMES))
    print("🏗️ Asset Types:", sum(len(assets) for assets in SUPPORTED_ASSET_TYPES.values()), "total")
    print("="*60)

# Auto-print info when module is imported (optional - can be disabled)
import os
if os.getenv('AI_ASSET_GENERATOR_QUIET') != '1':
    print_module_info()

# Convenience functions for quick usage
def quick_generate(theme: str = 'medieval', buildings: int = 3, props: int = 5, output_dir: str = "quick_assets"):
    """Quick generation function for simple use cases"""
    import asyncio
    
    # Create simple world spec
    world_spec = {
        'theme': theme,
        'size': (30, 30),
        'buildings': [
            {'type': 'house', 'position': {'x': 10, 'y': 10, 'z': 0}},
            {'type': 'tavern', 'position': {'x': 20, 'y': 15, 'z': 0}},
            {'type': 'church', 'position': {'x': 15, 'y': 20, 'z': 0}}
        ][:buildings],
        'natural_features': [
            {'type': 'oak_tree', 'position': {'x': 5, 'y': 5, 'z': 0}},
            {'type': 'rock', 'position': {'x': 25, 'y': 8, 'z': 0}},
            {'type': 'well', 'position': {'x': 15, 'y': 25, 'z': 0}},
            {'type': 'bush', 'position': {'x': 8, 'y': 18, 'z': 0}},
            {'type': 'tree', 'position': {'x': 22, 'y': 22, 'z': 0}}
        ][:props]
    }
    
    async def _generate():
        generator = AICreativeAssetGenerator(output_dir)
        return await generator.generate_creative_assets(world_spec)
    
    return asyncio.run(_generate())

def quick_status():
    """Get quick status of the asset generator"""
    import asyncio
    
    async def _get_status():
        generator = AICreativeAssetGenerator("temp_status_check")
        return await generator.get_status()
    
    return asyncio.run(_get_status())

# Module validation
def validate_installation():
    """Validate that the module is properly installed and configured"""
    issues = []
    deps = check_dependencies()
    
    if not deps['imaging']:
        issues.append("PIL/Pillow not available - texture generation will be limited")
    
    if not deps['ai']:
        issues.append("Google AI libraries not available - using fallback descriptions")
    
    if not deps['blender']:
        issues.append("Blender API not available - scripts will be generated for external execution")
    
    if issues:
        print("⚠️ Installation Issues:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n💡 Tip: The generator will work with fallback modes, but full functionality requires all dependencies.")
    else:
        print("✅ Installation validated - all dependencies available!")
    
    return len(issues) == 0

# Export configuration for tools
EXPORT_CONFIG = {
    'formats': {
        'blender': {
            'extension': '.blend',
            'description': 'Native Blender format',
            'requires': 'blender'
        },
        'gltf': {
            'extension': '.gltf',
            'description': 'Standard 3D format',
            'requires': 'blender'
        },
        'obj': {
            'extension': '.obj', 
            'description': 'Wavefront OBJ format',
            'requires': 'blender'
        },
        'scripts': {
            'extension': '.py',
            'description': 'Blender Python scripts',
            'requires': 'core'
        }
    },
    'textures': {
        'png': {'extension': '.png', 'description': 'PNG images'},
        'jpg': {'extension': '.jpg', 'description': 'JPEG images'}
    },
    'materials': {
        'json': {'extension': '.json', 'description': 'Material definitions'},
        'blend': {'extension': '.blend', 'description': 'Blender materials'},
        'csv': {'extension': '.csv', 'description': 'Material catalog'}
    }
}

def get_export_info():
    """Get information about available export formats"""
    return EXPORT_CONFIG.copy()

# Helper for integration with other tools
class ModularAssetGeneratorAPI:
    """Simplified API interface for external tool integration"""
    
    def __init__(self, output_dir: str = "api_assets"):
        self.generator = AICreativeAssetGenerator(output_dir)
    
    async def generate_building(self, building_type: str, theme: str, position: dict = None):
        """Generate a single building"""
        if position is None:
            position = {'x': 0, 'y': 0, 'z': 0}
        
        world_spec = {
            'theme': theme,
            'buildings': [{'type': building_type, 'position': position}],
            'natural_features': []
        }
        
        result = await self.generator.generate_creative_assets(world_spec)
        return result['buildings'][0] if result['buildings'] else None
    
    async def generate_prop(self, prop_type: str, theme: str, position: dict = None):
        """Generate a single prop"""
        if position is None:
            position = {'x': 0, 'y': 0, 'z': 0}
        
        world_spec = {
            'theme': theme,
            'buildings': [],
            'natural_features': [{'type': prop_type, 'position': position}]
        }
        
        result = await self.generator.generate_creative_assets(world_spec)
        return result['props'][0] if result['props'] else None
    
    async def generate_material_set(self, theme: str):
        """Generate a complete material set for a theme"""
        return await self.generator.material_library.generate_ai_material_library(theme)
    
    async def get_generator_status(self):
        """Get current generator status"""
        return await self.generator.get_status()

def create_api(output_dir: str = "api_assets"):
    """Create a simplified API instance"""
    return ModularAssetGeneratorAPI(output_dir)

# Error classes for better error handling
class AssetGeneratorError(Exception):
    """Base exception for asset generator errors"""
    pass

class AIServiceError(AssetGeneratorError):
    """Raised when AI services are unavailable or fail"""
    pass

class BlenderError(AssetGeneratorError):
    """Raised when Blender operations fail"""
    pass

class TextureGenerationError(AssetGeneratorError):
    """Raised when texture generation fails"""
    pass

class MaterialLibraryError(AssetGeneratorError):
    """Raised when material library operations fail"""
    pass

# Configuration management
class Config:
    """Configuration management for the asset generator"""
    
    DEFAULT_CONFIG = {
        'ai': {
            'api_key_env': 'GOOGLE_API_KEY',
            'model': 'gemini-2.0-flash-exp',
            'timeout': 30
        },
        'textures': {
            'default_size': (256, 256),
            'max_size': (1024, 1024),
            'format': 'PNG'
        },
        'blender': {
            'auto_save': True,
            'preview_renders': True,
            'export_formats': ['blend', 'gltf']
        },
        'output': {
            'organize_by_theme': True,
            'create_manifest': True,
            'compress_assets': False
        }
    }
    
    @classmethod
    def get_default_config(cls):
        """Get default configuration"""
        return cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def load_config(cls, config_file: str = None):
        """Load configuration from file"""
        if config_file and os.path.exists(config_file):
            import json
            with open(config_file, 'r') as f:
                return json.load(f)
        return cls.get_default_config()
    
    @classmethod
    def save_config(cls, config: dict, config_file: str):
        """Save configuration to file"""
        import json
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

# Logging setup
def setup_logging(level: str = 'INFO', log_file: str = None):
    """Setup logging for the asset generator"""
    import logging
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    logger = logging.getLogger('ai_creative_asset_generator')
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Performance monitoring
class PerformanceMonitor:
    """Simple performance monitoring for asset generation"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        import time
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str):
        """End timing an operation"""
        import time
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
            del self.start_times[operation]
            return duration
        return None
    
    def get_stats(self):
        """Get performance statistics"""
        stats = {}
        for operation, times in self.metrics.items():
            stats[operation] = {
                'count': len(times),
                'total_time': sum(times),
                'average_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times)
            }
        return stats
    
    def clear_metrics(self):
        """Clear all metrics"""
        self.metrics.clear()
        self.start_times.clear()

# Add performance monitor to package exports
__all__.extend([
    'ModularAssetGeneratorAPI',
    'create_api',
    'quick_generate',
    'quick_status',
    'validate_installation',
    'get_module_info',
    'get_supported_themes',
    'get_supported_assets',
    'get_export_info',
    'Config',
    'setup_logging',
    'PerformanceMonitor',
    'AssetGeneratorError',
    'AIServiceError',
    'BlenderError',
    'TextureGenerationError',
    'MaterialLibraryError'
])