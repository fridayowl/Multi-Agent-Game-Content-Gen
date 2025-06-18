"""
MATERIAL LIBRARY MODULE
Specialized module for material management and library creation
Handles material definitions, shader settings, and material catalogs
"""

import json
from typing import Dict, List, Any
from pathlib import Path
import logging

class MaterialLibrary:
    """
    Specialized material library management module
    Creates and manages comprehensive material catalogs
    """
    
    def __init__(self, output_dir: Path, ai_core):
        self.output_dir = output_dir
        self.ai_core = ai_core
        self.logger = logging.getLogger(__name__)
        
        # Material-specific directories
        self.materials_dir = output_dir / "ai_materials"
        self.library_dir = output_dir / "material_library"
        self.materials_dir.mkdir(exist_ok=True)
        self.library_dir.mkdir(exist_ok=True)
        
        # Material catalog
        self.material_catalog = {}
        self.material_sets = {}
    
    async def generate_ai_material_library(self, theme: str) -> Dict[str, Any]:
        """Generate comprehensive AI material library"""
    async def generate_ai_material_library(self, theme: str) -> Dict[str, Any]:
        """Generate comprehensive AI material library"""
        material_library = {
            'theme': theme,
            'version': '1.0',
            'material_sets': {},
            'total_materials': 0,
            'creation_timestamp': self._get_timestamp()
        }
        
        # Generate core material sets
        building_materials = await self._generate_building_material_set(theme)
        material_library['material_sets']['buildings'] = building_materials
        
        natural_materials = await self._generate_natural_material_set(theme)
        material_library['material_sets']['natural'] = natural_materials
        
        decorative_materials = await self._generate_decorative_material_set(theme)
        material_library['material_sets']['decorative'] = decorative_materials
        
        utility_materials = await self._generate_utility_material_set(theme)
        material_library['material_sets']['utility'] = utility_materials
        
        # Generate special theme materials
        special_materials = await self._generate_special_theme_materials(theme)
        material_library['material_sets']['special'] = special_materials
        
        # Calculate total materials
        total_count = sum(len(material_set.get('materials', [])) 
                         for material_set in material_library['material_sets'].values())
        material_library['total_materials'] = total_count
        
        # Save material library
        library_file = self.library_dir / f"{theme}_material_library.json"
        with open(library_file, 'w') as f:
            json.dump(material_library, f, indent=2)
        
        # Generate material preview catalog
        await self._generate_material_catalog(material_library, theme)
        
        self.logger.info(f"Generated {total_count} materials for {theme} theme")
        
        return material_library
    
    async def _generate_building_material_set(self, theme: str) -> Dict[str, Any]:
        """Generate materials for buildings"""
        building_materials = {
            'category': 'buildings',
            'description': f'Building materials for {theme} architecture',
            'materials': []
        }
        
        # Core building material types
        material_types = ['stone_wall', 'wood_beam', 'roof_tile', 'door_wood', 'window_glass', 'foundation_stone']
        
        for material_type in material_types:
            # Generate multiple variations of each type
            variations = await self._generate_material_variations(material_type, theme, 'building')
            building_materials['materials'].extend(variations)
        
        return building_materials
    
    async def _generate_natural_material_set(self, theme: str) -> Dict[str, Any]:
        """Generate materials for natural elements"""
        natural_materials = {
            'category': 'natural',
            'description': f'Natural materials for {theme} environment',
            'materials': []
        }
        
        # Natural material types
        material_types = ['tree_bark', 'leaf_foliage', 'grass_ground', 'rock_surface', 'dirt_path', 'water_surface']
        
        for material_type in material_types:
            variations = await self._generate_material_variations(material_type, theme, 'natural')
            natural_materials['materials'].extend(variations)
        
        return natural_materials
    
    async def _generate_decorative_material_set(self, theme: str) -> Dict[str, Any]:
        """Generate decorative and accent materials"""
        decorative_materials = {
            'category': 'decorative',
            'description': f'Decorative materials for {theme} aesthetics',
            'materials': []
        }
        
        # Decorative material types
        material_types = ['fabric_banner', 'metal_accent', 'carved_detail', 'painted_surface', 'crystal_gem', 'ornate_trim']
        
        for material_type in material_types:
            variations = await self._generate_material_variations(material_type, theme, 'decorative')
            decorative_materials['materials'].extend(variations)
        
        return decorative_materials
    
    async def _generate_utility_material_set(self, theme: str) -> Dict[str, Any]:
        """Generate utility and functional materials"""
        utility_materials = {
            'category': 'utility',
            'description': f'Utility materials for {theme} functionality',
            'materials': []
        }
        
        # Utility material types
        material_types = ['rope_cord', 'metal_tool', 'leather_goods', 'ceramic_pottery', 'cloth_covering', 'basket_weave']
        
        for material_type in material_types:
            variations = await self._generate_material_variations(material_type, theme, 'utility')
            utility_materials['materials'].extend(variations)
        
        return utility_materials
    
    async def _generate_special_theme_materials(self, theme: str) -> Dict[str, Any]:
        """Generate theme-specific special materials"""
        special_materials = {
            'category': 'special',
            'description': f'Special materials unique to {theme} theme',
            'materials': []
        }
        
        # Theme-specific materials
        theme_materials = {
            'medieval': ['chainmail_armor', 'castle_stone', 'banner_heraldry', 'iron_binding'],
            'fantasy': ['magical_crystal', 'enchanted_wood', 'glowing_rune', 'ethereal_mist'],
            'spooky': ['weathered_bone', 'tattered_cloth', 'rusted_metal', 'eerie_glow'],
            'desert': ['sun_bleached_stone', 'woven_carpet', 'brass_ornament', 'sand_texture']
        }
        
        material_types = theme_materials.get(theme, ['generic_special'])
        
        for material_type in material_types:
            variations = await self._generate_material_variations(material_type, theme, 'special')
            special_materials['materials'].extend(variations)
        
        return special_materials
    
    async def _generate_material_variations(self, base_type: str, theme: str, category: str) -> List[Dict[str, Any]]:
        """Generate multiple variations of a material type"""
        variations = []
        
        # Generate 2-4 variations per material type
        num_variations = 3  # Fixed number for consistency
        
        for i in range(num_variations):
            variation_name = f"{base_type}_{theme}_var_{i+1}"
            
            # Generate AI-guided material properties
            material_props = await self.ai_core.generate_material_properties(base_type, theme)
            
            # Generate material description
            description = await self._generate_material_description(base_type, theme, i+1)
            
            # Create material definition
            material_def = {
                'name': variation_name,
                'display_name': f"{base_type.replace('_', ' ').title()} - {theme.title()} Variant {i+1}",
                'base_type': base_type,
                'theme': theme,
                'category': category,
                'variation': i+1,
                'description': description,
                'properties': material_props,
                'shader_settings': self._generate_shader_settings(base_type, material_props),
                'texture_maps': self._generate_texture_map_definitions(base_type, theme),
                'export_formats': {
                    'blender': f"{variation_name}.blend",
                    'unity': f"{variation_name}.mat",
                    'godot': f"{variation_name}.tres",
                    'gltf': f"{variation_name}.json"
                },
                'usage_notes': self._generate_usage_notes(base_type, category)
            }
            
            # Save individual material file
            material_file = self.materials_dir / f"{variation_name}.json"
            with open(material_file, 'w') as f:
                json.dump(material_def, f, indent=2)
            
            variations.append(material_def)
        
        return variations
    
    async def _generate_material_description(self, base_type: str, theme: str, variation: int) -> str:
        """Generate AI description for material"""
        if not self.ai_core.ai_available:
            return f"A {theme} {base_type.replace('_', ' ')} material with unique properties"
        
        prompt = f"""Describe a {base_type.replace('_', ' ')} material in a {theme} setting.
        This is variation {variation}, so make it distinct from standard versions.
        Include details about:
        - Visual appearance and texture
        - Material properties and feel
        - How it would be used
        - Any special characteristics
        
        Keep it to 1-2 sentences."""
        
        response = await self.ai_core.call_gemini(prompt)
        return response if response else f"A {theme} {base_type.replace('_', ' ')} with distinctive {theme} characteristics"
    
    def _generate_shader_settings(self, base_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate shader settings for material type"""
        # Base shader settings templates
        shader_templates = {
            'wood': {
                'shader_type': 'PBR',
                'workflow': 'metallic_roughness',
                'two_sided': False,
                'alpha_mode': 'OPAQUE'
            },
            'stone': {
                'shader_type': 'PBR',
                'workflow': 'metallic_roughness',
                'two_sided': False,
                'alpha_mode': 'OPAQUE'
            },
            'metal': {
                'shader_type': 'PBR',
                'workflow': 'metallic_roughness',
                'two_sided': False,
                'alpha_mode': 'OPAQUE'
            },
            'glass': {
                'shader_type': 'PBR',
                'workflow': 'metallic_roughness',
                'two_sided': True,
                'alpha_mode': 'BLEND',
                'transmission': 0.9
            },
            'fabric': {
                'shader_type': 'PBR',
                'workflow': 'metallic_roughness',
                'two_sided': True,
                'alpha_mode': 'MASK',
                'alpha_cutoff': 0.5
            },
            'foliage': {
                'shader_type': 'PBR',
                'workflow': 'metallic_roughness',
                'two_sided': True,
                'alpha_mode': 'MASK',
                'alpha_cutoff': 0.5
            }
        }
        
        # Determine material category
        material_category = 'stone'  # Default
        if 'wood' in base_type:
            material_category = 'wood'
        elif 'metal' in base_type:
            material_category = 'metal'
        elif 'glass' in base_type:
            material_category = 'glass'
        elif 'fabric' in base_type or 'cloth' in base_type:
            material_category = 'fabric'
        elif 'leaf' in base_type or 'foliage' in base_type:
            material_category = 'foliage'
        
        # Get base settings
        shader_settings = shader_templates.get(material_category, shader_templates['stone']).copy()
        
        # Apply material properties
        shader_settings.update({
            'base_color_factor': self._normalize_color(properties.get('base_color', [128, 128, 128])),
            'metallic_factor': properties.get('metallic', 0.0),
            'roughness_factor': properties.get('roughness', 0.8),
            'emission_factor': properties.get('emission_strength', 0.0),
            'normal_scale': properties.get('normal_strength', 1.0)
        })
        
        return shader_settings
    
    def _normalize_color(self, color: List[int]) -> List[float]:
        """Normalize RGB color values to 0-1 range"""
        return [c / 255.0 for c in color]
    
    def _generate_texture_map_definitions(self, base_type: str, theme: str) -> Dict[str, str]:
        """Generate texture map definitions for the material"""
        # Standard PBR texture maps
        texture_maps = {
            'base_color': f"textures/{base_type}_{theme}_basecolor.png",
            'normal': f"textures/{base_type}_{theme}_normal.png",
            'roughness': f"textures/{base_type}_{theme}_roughness.png",
            'metallic': f"textures/{base_type}_{theme}_metallic.png"
        }
        
        # Add additional maps based on material type
        if 'wood' in base_type:
            texture_maps['ambient_occlusion'] = f"textures/{base_type}_{theme}_ao.png"
        elif 'metal' in base_type:
            texture_maps['reflection'] = f"textures/{base_type}_{theme}_reflection.png"
        elif 'glass' in base_type:
            texture_maps['transmission'] = f"textures/{base_type}_{theme}_transmission.png"
        elif 'fabric' in base_type:
            texture_maps['subsurface'] = f"textures/{base_type}_{theme}_subsurface.png"
        
        return texture_maps
    
    def _generate_usage_notes(self, base_type: str, category: str) -> List[str]:
        """Generate usage notes and recommendations"""
        usage_notes = [
            f"Optimized for {category} applications",
            "Supports all major 3D engines",
            "PBR workflow compatible"
        ]
        
        # Add specific notes based on material type
        if 'wood' in base_type:
            usage_notes.extend([
                "Natural wood grain patterns",
                "Suitable for architectural elements",
                "Good for furniture and structural components"
            ])
        elif 'stone' in base_type:
            usage_notes.extend([
                "High-resolution detail textures",
                "Suitable for buildings and terrain",
                "Weather-resistant appearance"
            ])
        elif 'metal' in base_type:
            usage_notes.extend([
                "Realistic metallic properties",
                "Suitable for tools and armor",
                "Supports weathering effects"
            ])
        
        return usage_notes
    
    async def _generate_material_catalog(self, material_library: Dict[str, Any], theme: str):
        """Generate visual material catalog"""
        catalog = {
            'title': f"{theme.title()} Material Catalog",
            'theme': theme,
            'total_materials': material_library['total_materials'],
            'categories': {},
            'quick_reference': []
        }
        
        # Process each material set
        for set_name, material_set in material_library['material_sets'].items():
            catalog['categories'][set_name] = {
                'name': set_name.title(),
                'description': material_set.get('description', ''),
                'material_count': len(material_set.get('materials', [])),
                'materials': []
            }
            
            # Add materials to catalog
            for material in material_set.get('materials', []):
                catalog_entry = {
                    'name': material['display_name'],
                    'id': material['name'],
                    'description': material['description'],
                    'base_color': material['properties'].get('base_color', [128, 128, 128]),
                    'metallic': material['properties'].get('metallic', 0.0),
                    'roughness': material['properties'].get('roughness', 0.8)
                }
                
                catalog['categories'][set_name]['materials'].append(catalog_entry)
                catalog['quick_reference'].append({
                    'name': material['display_name'],
                    'id': material['name'],
                    'category': set_name
                })
        
        # Save catalog
        catalog_file = self.library_dir / f"{theme}_material_catalog.json"
        with open(catalog_file, 'w') as f:
            json.dump(catalog, f, indent=2)
        
        # Generate human-readable catalog
        await self._generate_readable_catalog(catalog, theme)
    
    async def _generate_readable_catalog(self, catalog: Dict[str, Any], theme: str):
        """Generate human-readable material catalog"""
        catalog_text = f"""
# {catalog['title']}

**Theme**: {theme.title()}  
**Total Materials**: {catalog['total_materials']}  
**Generated**: {self._get_timestamp()}

## Material Categories

"""
        
        for category_id, category in catalog['categories'].items():
            catalog_text += f"### {category['name']}\n"
            catalog_text += f"*{category['description']}*\n"
            catalog_text += f"**Materials**: {category['material_count']}\n\n"
            
            for material in category['materials']:
                catalog_text += f"- **{material['name']}**\n"
                catalog_text += f"  - {material['description']}\n"
                catalog_text += f"  - Metallic: {material['metallic']:.1f}, Roughness: {material['roughness']:.1f}\n\n"
        
        catalog_text += """
## Usage Guidelines

1. **Building Materials**: Use for structural elements and architecture
2. **Natural Materials**: Apply to terrain and vegetation
3. **Decorative Materials**: Add visual interest and detail
4. **Utility Materials**: Functional elements and props
5. **Special Materials**: Theme-specific unique elements

## Export Formats

All materials are available in the following formats:
- Blender (.blend)
- Unity (.mat)
- Godot (.tres)
- glTF (.json)

---
*Generated by AI Creative Asset Generator - Modular Version*
"""
        
        catalog_file = self.library_dir / f"{theme}_catalog_readable.md"
        with open(catalog_file, 'w') as f:
            f.write(catalog_text)
    
    def get_material_library_size(self) -> int:
        """Get total number of materials in library"""
        return len(self.material_catalog)
    
    def get_material_by_id(self, material_id: str) -> Dict[str, Any]:
        """Get specific material by ID"""
        return self.material_catalog.get(material_id, {})
    
    def get_materials_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all materials in a specific category"""
        return [material for material in self.material_catalog.values() 
                if material.get('category') == category]
    
    def get_materials_by_theme(self, theme: str) -> List[Dict[str, Any]]:
        """Get all materials for a specific theme"""
        return [material for material in self.material_catalog.values() 
                if material.get('theme') == theme]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def export_material_library(self, export_format: str, output_path: Path) -> bool:
        """Export material library in specified format"""
        try:
            if export_format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(self.material_catalog, f, indent=2)
            elif export_format == 'csv':
                self._export_csv(output_path)
            elif export_format == 'xml':
                self._export_xml(output_path)
            else:
                self.logger.warning(f"Unsupported export format: {export_format}")
                return False
            
            self.logger.info(f"Material library exported to {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export material library: {e}")
            return False
    
    def _export_csv(self, output_path: Path):
        """Export material library as CSV"""
        import csv
        
        with open(output_path, 'w', newline='') as csvfile:
            fieldnames = ['name', 'category', 'theme', 'base_type', 'metallic', 'roughness', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for material in self.material_catalog.values():
                writer.writerow({
                    'name': material.get('name', ''),
                    'category': material.get('category', ''),
                    'theme': material.get('theme', ''),
                    'base_type': material.get('base_type', ''),
                    'metallic': material.get('properties', {}).get('metallic', 0.0),
                    'roughness': material.get('properties', {}).get('roughness', 0.8),
                    'description': material.get('description', '')
                })
    
    def _export_xml(self, output_path: Path):
        """Export material library as XML"""
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<MaterialLibrary>\n'
        
        for material in self.material_catalog.values():
            xml_content += f'  <Material name="{material.get("name", "")}">\n'
            xml_content += f'    <Category>{material.get("category", "")}</Category>\n'
            xml_content += f'    <Theme>{material.get("theme", "")}</Theme>\n'
            xml_content += f'    <BaseType>{material.get("base_type", "")}</BaseType>\n'
            xml_content += f'    <Description>{material.get("description", "")}</Description>\n'
            xml_content += f'    <Properties>\n'
            props = material.get('properties', {})
            xml_content += f'      <Metallic>{props.get("metallic", 0.0)}</Metallic>\n'
            xml_content += f'      <Roughness>{props.get("roughness", 0.8)}</Roughness>\n'
            xml_content += f'    </Properties>\n'
            xml_content += f'  </Material>\n'
        
        xml_content += '</MaterialLibrary>'
        
        with open(output_path, 'w') as f:
            f.write(xml_content)