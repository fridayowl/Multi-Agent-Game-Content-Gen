"""
AI CORE MODULE
Central AI coordination and API management for the asset generator
Handles all AI model interactions and API calls
"""

import os
import logging
from typing import Optional

# Google AI imports
try:
    import google.generativeai as genai
    from google.cloud import aiplatform
    AI_AVAILABLE = False
except ImportError:
    AI_AVAILABLE = False

class AICore:
    """
    Central AI coordination module
    Manages all AI model interactions and API calls
    """
    
    def __init__(self):
        self.ai_available = AI_AVAILABLE
        self.logger = logging.getLogger(__name__)
        self.gemini_model = None
        
        if self.ai_available:
            self._initialize_ai()
        else:
            self.logger.warning("⚠️ AI libraries not available, using fallback modes")
    
    def _initialize_ai(self):
        """Initialize AI services for REAL creativity"""
        try:
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY', 'your-api-key-here'))
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.logger.info("✅ AI services initialized for creative generation")
        except Exception as e:
            self.logger.warning(f"⚠️ AI initialization failed: {e}")
            self.ai_available = False
    
    async def call_gemini(self, prompt: str) -> Optional[str]:
        """Helper method to call Gemini AI"""
        if not self.ai_available or not self.gemini_model:
            return None
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.warning(f"Gemini API call failed: {e}")
            return None
    
    async def generate_prop_description(self, prop_type: str, theme: str, index: int) -> str:
        """Generate unique AI description for each prop"""
        if not self.ai_available:
            return f"A unique {theme} {prop_type} with distinctive characteristics"
        
        try:
            prompt = f"""Create a UNIQUE and CREATIVE description for a {prop_type} in a {theme} game world.
            
            This is prop #{index + 1}, so make it completely different from others.
            Include specific details about:
            - Visual appearance and distinctive features
            - Size, shape, and proportions
            - Materials and surface textures
            - Any special characteristics
            
            Keep it to 2-3 sentences. Be creative and specific."""
            
            response = await self.call_gemini(prompt)
            if response:
                return response.strip()
                
        except Exception as e:
            self.logger.warning(f"AI prop description failed: {e}")
        
        return f"A unique {theme} {prop_type} with distinctive characteristics #{index + 1}"

    async def generate_prop_variations(self, prop_type: str, theme: str) -> list:
        """Generate creative variations for props"""
        if not self.ai_available:
            return [f"Standard {prop_type}", f"Enhanced {prop_type}"]
        
        try:
            prompt = f"""Create 3 creative variations for a {prop_type} in a {theme} theme.
            Each should be visually distinct with different:
            - Size and shape
            - Materials and textures
            - Special features
            - Color schemes
            
            Format as numbered list, 1-2 sentences each."""
            
            response = await self.call_gemini(prompt)
            if response:
                variations = [line.strip() for line in response.split('\n') if line.strip() and any(c.isdigit() for c in line)]
                return variations[:3] if variations else [f"Creative {prop_type}"]
            
        except Exception as e:
            self.logger.warning(f"AI prop variations failed: {e}")
        
        return [f"Unique {prop_type}", f"Enhanced {prop_type}"]

    async def generate_building_description(self, building_type: str, theme: str, index: int) -> str:
        """Generate unique AI description for buildings"""
        if not self.ai_available:
            return f"A unique {theme} {building_type} with architectural details"
        
        try:
            prompt = f"""Create a UNIQUE architectural description for a {building_type} in a {theme} game world.
            
            This is building #{index + 1}, so make it architecturally distinct.
            Include specific details about:
            - Architectural style and design elements
            - Building materials and construction
            - Size, proportions, and layout
            - Unique features or decorative elements
            
            Keep it to 2-3 sentences. Be architecturally creative."""
            
            response = await self.call_gemini(prompt)
            if response:
                return response.strip()
                
        except Exception as e:
            self.logger.warning(f"AI building description failed: {e}")
        
        return f"A unique {theme} {building_type} with architectural details #{index + 1}"

    async def generate_building_variations(self, building_type: str, theme: str) -> list:
        """Generate creative variations for buildings"""
        if not self.ai_available:
            return [f"Standard {building_type}", f"Enhanced {building_type}"]
        
        try:
            prompt = f"""Create 3 architectural variations for a {building_type} in a {theme} theme.
            Each should be architecturally distinct with different:
            - Structural design and layout
            - Building materials and finishes
            - Decorative elements and features
            - Size and proportions
            
            Format as numbered list, 1-2 sentences each."""
            
            response = await self.call_gemini(prompt)
            if response:
                variations = [line.strip() for line in response.split('\n') if line.strip() and any(c.isdigit() for c in line)]
                return variations[:3] if variations else [f"Creative {building_type}"]
            
        except Exception as e:
            self.logger.warning(f"AI building variations failed: {e}")
        
        return [f"Unique {building_type}", f"Enhanced {building_type}"]

    async def generate_geometry_parameters(self, asset_type: str, description: str) -> dict:
        """Generate unique geometry parameters for assets"""
        if not self.ai_available:
            return self._get_fallback_geometry(asset_type)
        
        try:
            prompt = f"""Based on: "{description}"
            
            Generate geometry parameters for this {asset_type}:
            - Height multiplier (0.5 to 3.0)
            - Width multiplier (0.5 to 2.5)
            - Complexity level (simple, medium, complex)
            - Detail count (1 to 10)
            - Asymmetry factor (0.0 to 1.0)
            
            Format: HEIGHT:1.5 WIDTH:1.2 COMPLEXITY:medium DETAILS:5 ASYMMETRY:0.3"""
            
            response = await self.call_gemini(prompt)
            if response:
                return self._parse_geometry(response)
                
        except Exception as e:
            self.logger.warning(f"AI geometry generation failed: {e}")
        
        return self._get_fallback_geometry(asset_type)

    def _parse_geometry(self, ai_response: str) -> dict:
        """Parse AI geometry parameters"""
        params = {}
        
        try:
            import re
            
            height_match = re.search(r'HEIGHT:([\d.]+)', ai_response)
            if height_match:
                params['height_multiplier'] = float(height_match.group(1))
            
            width_match = re.search(r'WIDTH:([\d.]+)', ai_response)
            if width_match:
                params['width_multiplier'] = float(width_match.group(1))
            
            complexity_match = re.search(r'COMPLEXITY:(\w+)', ai_response)
            if complexity_match:
                params['complexity'] = complexity_match.group(1)
            
            details_match = re.search(r'DETAILS:(\d+)', ai_response)
            if details_match:
                params['detail_count'] = int(details_match.group(1))
            
            asymmetry_match = re.search(r'ASYMMETRY:([\d.]+)', ai_response)
            if asymmetry_match:
                params['asymmetry_factor'] = float(asymmetry_match.group(1))
                
        except Exception as e:
            self.logger.warning(f"Failed to parse geometry: {e}")
        
        # Fill in any missing defaults
        return self._fill_geometry_defaults(params)

    def _fill_geometry_defaults(self, params: dict) -> dict:
        """Fill in default geometry parameters"""
        defaults = {
            'height_multiplier': 1.0,
            'width_multiplier': 1.0,
            'complexity': 'medium',
            'detail_count': 3,
            'asymmetry_factor': 0.2
        }
        
        for key, default_value in defaults.items():
            if key not in params:
                params[key] = default_value
        
        return params

    def _get_fallback_geometry(self, asset_type: str) -> dict:
        """Get fallback geometry parameters"""
        import random
        
        base_params = {
            'height_multiplier': random.uniform(0.8, 1.5),
            'width_multiplier': random.uniform(0.8, 1.3),
            'complexity': random.choice(['simple', 'medium', 'complex']),
            'detail_count': random.randint(2, 6),
            'asymmetry_factor': random.uniform(0.1, 0.4)
        }
        
        # Asset-specific adjustments
        if asset_type in ['tree', 'oak_tree']:
            base_params['height_multiplier'] = random.uniform(1.2, 2.5)
        elif asset_type == 'rock':
            base_params['height_multiplier'] = random.uniform(0.5, 1.2)
            base_params['width_multiplier'] = random.uniform(0.8, 1.8)
        
        return base_params

    async def generate_material_properties(self, material_type: str, theme: str) -> dict:
        """Generate AI-guided material properties"""
        if not self.ai_available:
            return self._get_fallback_material(material_type, theme)
        
        try:
            prompt = f"""Generate material properties for {material_type} in a {theme} theme:
            - Metallic value (0.0 to 1.0)
            - Roughness value (0.0 to 1.0)
            - Base color (RGB values 0-255)
            - Emission strength (0.0 to 2.0)
            - Normal strength (0.0 to 2.0)
            
            Format: METALLIC:0.2 ROUGHNESS:0.8 COLOR:120,80,60 EMISSION:0.1 NORMAL:1.0"""
            
            response = await self.call_gemini(prompt)
            if response:
                return self._parse_material(response)
                
        except Exception as e:
            self.logger.warning(f"AI material generation failed: {e}")
        
        return self._get_fallback_material(material_type, theme)

    def _parse_material(self, ai_response: str) -> dict:
        """Parse AI material parameters"""
        import re
        
        params = {}
        
        try:
            metallic_match = re.search(r'METALLIC:([\d.]+)', ai_response)
            if metallic_match:
                params['metallic'] = float(metallic_match.group(1))
            
            roughness_match = re.search(r'ROUGHNESS:([\d.]+)', ai_response)
            if roughness_match:
                params['roughness'] = float(roughness_match.group(1))
            
            color_match = re.search(r'COLOR:(\d+),(\d+),(\d+)', ai_response)
            if color_match:
                params['base_color'] = [
                    int(color_match.group(1)),
                    int(color_match.group(2)),
                    int(color_match.group(3))
                ]
            
            emission_match = re.search(r'EMISSION:([\d.]+)', ai_response)
            if emission_match:
                params['emission_strength'] = float(emission_match.group(1))
            
            normal_match = re.search(r'NORMAL:([\d.]+)', ai_response)
            if normal_match:
                params['normal_strength'] = float(normal_match.group(1))
                
        except Exception as e:
            self.logger.warning(f"Failed to parse material: {e}")
        
        return self._fill_material_defaults(params)

    def _fill_material_defaults(self, params: dict) -> dict:
        """Fill in default material parameters"""
        defaults = {
            'metallic': 0.0,
            'roughness': 0.8,
            'base_color': [128, 128, 128],
            'emission_strength': 0.0,
            'normal_strength': 1.0
        }
        
        for key, default_value in defaults.items():
            if key not in params:
                params[key] = default_value
        
        return params

    def _get_fallback_material(self, material_type: str, theme: str) -> dict:
        """Get fallback material properties"""
        import random
        
        # Base material templates
        material_templates = {
            'wood': {'metallic': 0.0, 'roughness': 0.8, 'base_color': [139, 69, 19]},
            'stone': {'metallic': 0.0, 'roughness': 0.9, 'base_color': [128, 128, 128]},
            'metal': {'metallic': 0.9, 'roughness': 0.2, 'base_color': [160, 160, 160]},
            'fabric': {'metallic': 0.0, 'roughness': 0.9, 'base_color': [180, 120, 80]}
        }
        
        base = material_templates.get(material_type, material_templates['stone'])
        
        return {
            'metallic': base['metallic'] + random.uniform(-0.1, 0.1),
            'roughness': max(0.0, min(1.0, base['roughness'] + random.uniform(-0.2, 0.2))),
            'base_color': [
                max(0, min(255, base['base_color'][0] + random.randint(-30, 30))),
                max(0, min(255, base['base_color'][1] + random.randint(-30, 30))),
                max(0, min(255, base['base_color'][2] + random.randint(-30, 30)))
            ],
            'emission_strength': random.uniform(0.0, 0.2),
            'normal_strength': random.uniform(0.8, 1.2)
        }