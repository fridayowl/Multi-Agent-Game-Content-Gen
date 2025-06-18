"""
TEXTURE GENERATOR MODULE
Specialized module for AI-guided texture creation
Handles procedural texture generation, material properties, and texture caching
"""

import hashlib
from typing import Dict, Any
from pathlib import Path
import logging
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

class TextureGenerator:
    """
    Specialized texture generation module
    Creates unique procedural textures based on AI descriptions
    """
    
    def __init__(self, output_dir: Path, ai_core):
        self.output_dir = output_dir
        self.ai_core = ai_core
        self.logger = logging.getLogger(__name__)
        
        # Texture-specific directories
        self.textures_dir = output_dir / "ai_textures"
        self.materials_dir = output_dir / "ai_materials"
        self.textures_dir.mkdir(exist_ok=True)
        self.materials_dir.mkdir(exist_ok=True)
        
        # Texture cache
        self.texture_cache = {}
        self.material_cache = {}
    
    async def generate_unique_ai_texture(self, description: str, texture_type: str, theme: str, index: int) -> str:
        """Generate a unique AI texture"""
        # Create unique texture identifier
        texture_id = hashlib.md5(f"{description}_{texture_type}_{theme}_{index}".encode()).hexdigest()[:8]
        texture_filename = f"{texture_type}_{theme}_{texture_id}.png"
        texture_path = self.textures_dir / texture_filename
        
        # Check cache first
        cache_key = f"{texture_type}_{theme}_{index}"
        if cache_key in self.texture_cache:
            return str(self.texture_cache[cache_key])
        
        # Generate procedural texture
        try:
            texture_image = self._create_procedural_texture(description, texture_type, theme)
            texture_image.save(texture_path)
            
            # Cache the result
            self.texture_cache[cache_key] = texture_path
            
            return str(texture_path)
            
        except Exception as e:
            self.logger.warning(f"Texture generation failed: {e}")
            return self._create_fallback_texture(texture_type, theme, texture_path)
    
    def _create_procedural_texture(self, description: str, texture_type: str, theme: str) -> Image.Image:
        """Create procedural texture based on description"""
        size = (256, 256)
        
        # Base colors by type and theme
        color_schemes = {
            'wood': {
                'medieval': [(139, 69, 19), (160, 82, 45), (101, 67, 33)],
                'spooky': [(64, 32, 16), (80, 40, 20), (48, 24, 12)],
                'fantasy': [(160, 120, 80), (180, 140, 100), (120, 90, 60)],
                'desert': [(205, 133, 63), (210, 180, 140), (139, 90, 43)]
            },
            'stone': {
                'medieval': [(128, 128, 128), (169, 169, 169), (105, 105, 105)],
                'spooky': [(64, 64, 64), (80, 80, 80), (48, 48, 48)],
                'fantasy': [(150, 150, 200), (180, 180, 220), (120, 120, 180)],
                'desert': [(238, 203, 173), (255, 218, 185), (205, 175, 149)]
            },
            'foliage': {
                'medieval': [(34, 139, 34), (50, 205, 50), (0, 100, 0)],
                'spooky': [(20, 60, 20), (30, 80, 30), (10, 40, 10)],
                'fantasy': [(100, 200, 100), (120, 255, 120), (80, 160, 80)],
                'desert': [(107, 142, 35), (85, 107, 47), (46, 139, 87)]
            },
            'metal': {
                'medieval': [(169, 169, 169), (192, 192, 192), (128, 128, 128)],
                'spooky': [(105, 105, 105), (119, 136, 153), (85, 85, 85)],
                'fantasy': [(255, 215, 0), (218, 165, 32), (184, 134, 11)],
                'desert': [(160, 82, 45), (205, 133, 63), (139, 90, 43)]
            }
        }
        
        # Get color scheme
        colors = color_schemes.get(texture_type, {}).get(theme, [(128, 128, 128), (160, 160, 160), (96, 96, 96)])
        
        # Create base image
        image = Image.new('RGB', size, colors[0])
        draw = ImageDraw.Draw(image)
        
        # Add texture patterns based on type
        if texture_type == 'wood':
            self._add_wood_grain(draw, size, colors, description)
        elif texture_type == 'stone':
            self._add_stone_pattern(draw, size, colors, description)
        elif texture_type == 'foliage':
            self._add_foliage_pattern(draw, size, colors, description)
        elif texture_type == 'metal':
            self._add_metal_pattern(draw, size, colors, description)
        else:
            self._add_generic_pattern(draw, size, colors, description)
        
        # Apply filters for realism
        image = image.filter(ImageFilter.GaussianBlur(0.5))
        
        # Enhance contrast slightly
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # Add subtle noise for texture variety
        image = self._add_noise(image, 0.1)
        
        return image
    
    def _add_wood_grain(self, draw, size, colors, description):
        """Add wood grain pattern"""
        import random
        
        # Analyze description for grain intensity
        grain_intensity = 4 if 'rough' in description.lower() else 6
        grain_intensity = 2 if 'smooth' in description.lower() else grain_intensity
        
        for i in range(0, size[1], grain_intensity):
            # Vary the line color
            color = colors[random.randint(0, len(colors) - 1)]
            # Add some waviness to wood grain
            points = []
            wave_amplitude = 8 if 'twisted' in description.lower() else 3
            
            for x in range(0, size[0], 8):
                y_offset = random.randint(-wave_amplitude, wave_amplitude)
                points.extend([x, i + y_offset])
            if len(points) >= 4:
                draw.line(points, fill=color, width=1)
        
        # Add knots if mentioned
        if 'gnarled' in description.lower() or 'knot' in description.lower():
            for _ in range(random.randint(1, 3)):
                x = random.randint(20, size[0] - 20)
                y = random.randint(20, size[1] - 20)
                radius = random.randint(8, 15)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                           fill=colors[2], outline=colors[0])
    
    def _add_stone_pattern(self, draw, size, colors, description):
        """Add stone pattern"""
        import random
        
        # Determine pattern density based on description
        density = size[0] // 3 if 'smooth' in description.lower() else size[0] // 4
        density = size[0] // 2 if 'rough' in description.lower() else density
        
        # Add random dots and small shapes for stone texture
        for _ in range(density):
            x = random.randint(0, size[0] - 1)
            y = random.randint(0, size[1] - 1)
            color = colors[random.randint(0, len(colors) - 1)]
            radius = random.randint(1, 4)
            
            if 'crystalline' in description.lower():
                # Angular crystals
                points = []
                for i in range(6):
                    angle = i * 60
                    px = x + radius * random.uniform(0.7, 1.3) * (1 if i % 2 else 0.5)
                    py = y + radius * random.uniform(0.7, 1.3) * (1 if i % 2 else 0.5)
                    points.append((px, py))
                draw.polygon(points, fill=color)
            else:
                draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
        
        # Add cracks if mentioned
        if 'cracked' in description.lower() or 'weathered' in description.lower():
            for _ in range(random.randint(2, 5)):
                start_x = random.randint(0, size[0])
                start_y = random.randint(0, size[1])
                end_x = start_x + random.randint(-50, 50)
                end_y = start_y + random.randint(-50, 50)
                draw.line([start_x, start_y, end_x, end_y], fill=colors[2], width=1)
    
    def _add_foliage_pattern(self, draw, size, colors, description):
        """Add foliage pattern"""
        import random
        
        # Determine leaf pattern based on description
        leaf_count = size[0] // 6 if 'sparse' in description.lower() else size[0] // 8
        leaf_count = size[0] // 4 if 'dense' in description.lower() else leaf_count
        
        # Add leaf-like shapes
        for _ in range(leaf_count):
            x = random.randint(0, size[0] - 10)
            y = random.randint(0, size[1] - 10)
            color = colors[random.randint(0, len(colors) - 1)]
            
            if 'needle' in description.lower():
                # Needle-like leaves
                draw.line([x, y, x + random.randint(3, 8), y + random.randint(-2, 2)], 
                         fill=color, width=1)
            elif 'broad' in description.lower():
                # Broad leaves
                draw.ellipse([x, y, x + 8, y + 6], fill=color)
                # Add leaf vein
                draw.line([x + 1, y + 3, x + 7, y + 3], fill=colors[2], width=1)
            else:
                # Simple leaf shape
                draw.ellipse([x, y, x + 6, y + 4], fill=color)
    
    def _add_metal_pattern(self, draw, size, colors, description):
        """Add metal pattern"""
        import random
        
        # Add scratches and wear patterns
        if 'scratched' in description.lower() or 'worn' in description.lower():
            for _ in range(random.randint(10, 20)):
                start_x = random.randint(0, size[0])
                start_y = random.randint(0, size[1])
                end_x = start_x + random.randint(-30, 30)
                end_y = start_y + random.randint(-5, 5)
                draw.line([start_x, start_y, end_x, end_y], fill=colors[2], width=1)
        
        # Add rust spots if mentioned
        if 'rust' in description.lower() or 'weathered' in description.lower():
            rust_color = (139, 69, 19)  # Brown rust color
            for _ in range(random.randint(5, 15)):
                x = random.randint(0, size[0] - 10)
                y = random.randint(0, size[1] - 10)
                radius = random.randint(2, 8)
                draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                           fill=rust_color)
        
        # Add polished highlights
        if 'polished' in description.lower() or 'shiny' in description.lower():
            for _ in range(random.randint(3, 8)):
                x = random.randint(0, size[0] - 20)
                y = random.randint(0, size[1] - 5)
                draw.ellipse([x, y, x + 20, y + 5], fill=colors[0])
    
    def _add_generic_pattern(self, draw, size, colors, description):
        """Add generic pattern"""
        import random
        
        # Simple noise pattern
        density = size[0] // 2
        for _ in range(density):
            x = random.randint(0, size[0] - 1)
            y = random.randint(0, size[1] - 1)
            color = colors[random.randint(0, len(colors) - 1)]
            draw.point([x, y], fill=color)
    
    def _add_noise(self, image: Image.Image, intensity: float) -> Image.Image:
        """Add subtle noise to texture for variety"""
        import random
        import numpy as np
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Generate noise
        noise = np.random.normal(0, intensity * 255, img_array.shape).astype(np.int16)
        
        # Add noise and clamp values
        noisy_array = np.clip(img_array.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        return Image.fromarray(noisy_array)
    
    def _create_fallback_texture(self, texture_type: str, theme: str, texture_path: Path) -> str:
        """Create simple fallback texture"""
        try:
            size = (64, 64)
            
            # Theme-based fallback colors
            fallback_colors = {
                'medieval': (139, 119, 101),
                'spooky': (64, 64, 64),
                'fantasy': (128, 128, 180),
                'desert': (205, 133, 63)
            }
            
            color = fallback_colors.get(theme, (128, 128, 128))
            image = Image.new('RGB', size, color)
            image.save(texture_path)
            return str(texture_path)
        except Exception:
            return "textures/fallback.png"
    
    async def generate_material_definition(self, material_name: str, texture_paths: Dict[str, str], 
                                         material_type: str, theme: str) -> Dict[str, Any]:
        """Generate complete material definition"""
        # Get AI-generated material properties
        material_props = await self.ai_core.generate_material_properties(material_type, theme)
        
        # Create material definition
        material_def = {
            'name': material_name,
            'type': material_type,
            'theme': theme,
            'properties': material_props,
            'textures': texture_paths,
            'shader_settings': self._generate_shader_settings(material_type, material_props),
            'export_formats': {
                'blender': f"{material_name}.blend",
                'unity': f"{material_name}.mat",
                'godot': f"{material_name}.tres"
            }
        }
        
        # Cache material definition
        cache_key = f"{material_name}_{material_type}_{theme}"
        self.material_cache[cache_key] = material_def
        
        # Save material file
        material_file = self.materials_dir / f"{material_name}.json"
        import json
        with open(material_file, 'w') as f:
            json.dump(material_def, f, indent=2)
        
        return material_def
    
    def _generate_shader_settings(self, material_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Generate shader-specific settings"""
        base_settings = {
            'shader_type': 'PBR',
            'two_sided': False,
            'alpha_mode': 'OPAQUE',
            'depth_write': True
        }
        
        # Material-specific shader adjustments
        if material_type == 'foliage':
            base_settings['two_sided'] = True
            base_settings['alpha_mode'] = 'MASK'
            base_settings['alpha_cutoff'] = 0.5
        elif material_type == 'glass':
            base_settings['alpha_mode'] = 'BLEND'
            base_settings['depth_write'] = False
        elif material_type == 'metal':
            base_settings['metallic_workflow'] = True
        
        # Apply properties to shader settings
        base_settings.update({
            'base_color_factor': properties.get('base_color', [128, 128, 128]),
            'metallic_factor': properties.get('metallic', 0.0),
            'roughness_factor': properties.get('roughness', 0.8),
            'emission_factor': properties.get('emission_strength', 0.0),
            'normal_scale': properties.get('normal_strength', 1.0)
        })
        
        return base_settings
    
    def get_texture_cache_info(self) -> Dict[str, Any]:
        """Get information about cached textures"""
        return {
            'total_textures': len(self.texture_cache),
            'total_materials': len(self.material_cache),
            'texture_types': list(set(key.split('_')[0] for key in self.texture_cache.keys())),
            'themes': list(set(key.split('_')[1] for key in self.texture_cache.keys() if len(key.split('_')) > 1)),
            'cache_size_mb': sum(
                path.stat().st_size for path in self.texture_cache.values() 
                if isinstance(path, Path) and path.exists()
            ) / (1024 * 1024)
        }
    
    def clear_cache(self):
        """Clear texture and material caches"""
        self.texture_cache.clear()
        self.material_cache.clear()
        self.logger.info("Texture and material caches cleared")