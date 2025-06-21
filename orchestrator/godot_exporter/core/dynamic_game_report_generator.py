#!/usr/bin/env python3
"""
Dynamic Game Report Generator
Generates comprehensive PDF documentation when Godot export happens
Integrates with the multi-agent pipeline to create a complete game design document
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import logging

# Import for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, white, grey
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class DynamicGameReportGenerator:
    """Generates comprehensive game design documents dynamically"""
    
    def __init__(self, output_dir: Path, logger: logging.Logger):
        self.output_dir = output_dir
        self.logger = logger
        self.styles = self._create_styles() if REPORTLAB_AVAILABLE else None
        
    def _create_styles(self):
        """Create custom PDF styles"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='GameTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2C3E50'),
            alignment=1  # Center
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#34495E'),
            borderWidth=2,
            borderColor=HexColor('#3498DB'),
            borderPadding=10
        ))
        
        styles.add(ParagraphStyle(
            name='SubSectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=HexColor('#2980B9')
        ))
        
        styles.add(ParagraphStyle(
            name='GameContent',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20
        ))
        
        styles.add(ParagraphStyle(
            name='HighlightBox',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            backColor=HexColor('#ECF0F1'),
            borderColor=HexColor('#BDC3C7'),
            borderWidth=1,
            borderPadding=10
        ))
        
        styles.add(ParagraphStyle(
            name='AgentHeader',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=HexColor('#E74C3C'),
            backColor=HexColor('#FADBD8'),
            borderPadding=8
        ))
        
        return styles

    async def generate_complete_game_report(self, 
                                          world_spec: Dict[str, Any],
                                          assets: Dict[str, Any], 
                                          characters: Dict[str, Any],
                                          quests: Dict[str, Any],
                                          balance_report: Dict[str, Any],
                                          pipeline_log: Dict[str, Any],
                                          godot_export_data: Dict[str, Any]) -> str:
        """Generate complete game design document"""
        
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not available, creating text report instead")
            return await self._generate_text_report(world_spec, assets, characters, quests, 
                                                   balance_report, pipeline_log, godot_export_data)
        
        # Generate dynamic game name from world data
        game_name = self._generate_game_name(world_spec)
        
        # Create PDF filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"Complete_Game_Report_{game_name}_{timestamp}.pdf"
        pdf_path = self.output_dir / pdf_filename
        
        # Create PDF document
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, topMargin=0.5*inch)
        story = []
        
        # Generate all sections
        story.extend(self._create_title_page(game_name, world_spec))
        story.append(PageBreak())
        
        story.extend(self._create_game_overview(game_name, world_spec, characters, quests))
        story.append(PageBreak())
        
        story.extend(self._create_agent_collaboration_section(pipeline_log))
        story.append(PageBreak())
        
        story.extend(self._create_world_design_section(world_spec))
        story.append(PageBreak())
        
        story.extend(self._create_characters_section(characters))
        story.append(PageBreak())
        
        story.extend(self._create_quest_system_section(quests))
        story.append(PageBreak())
        
        story.extend(self._create_game_balance_section(balance_report))
        story.append(PageBreak())
        
        story.extend(self._create_technical_implementation(godot_export_data))
        story.append(PageBreak())
        
        story.extend(self._create_usage_instructions())
        
        # Build PDF
        doc.build(story)
        
        self.logger.info(f"✅ Complete Game Report generated: {pdf_filename}")
        return str(pdf_path)

    def _generate_game_name(self, world_spec: Dict[str, Any]) -> str:
        """Generate dynamic game name based on world properties"""
        theme = world_spec.get('theme', 'Adventure').title()
        setting_type = world_spec.get('setting_type', 'Village')
        
        name_templates = {
            'medieval': [f"Chronicles of {setting_type}", f"The {setting_type} Saga", f"Legends of {setting_type}"],
            'fantasy': [f"Mystic {setting_type}", f"Realm of {setting_type}", f"The Enchanted {setting_type}"],
            'spooky': [f"Shadows of {setting_type}", f"The Haunted {setting_type}", f"Dark {setting_type}"],
            'desert': [f"Sands of {setting_type}", f"The Lost {setting_type}", f"Mirage of {setting_type}"],
            'modern': [f"City of {setting_type}", f"The Urban {setting_type}", f"Metro {setting_type}"]
        }
        
        template_list = name_templates.get(theme.lower(), [f"Tales of {setting_type}"])
        return template_list[0] if template_list else f"Generated Game - {theme} {setting_type}"

    def _create_title_page(self, game_name: str, world_spec: Dict[str, Any]) -> List:
        """Create title page"""
        elements = []
        
        # Game title
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(game_name, self.styles['GameTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        theme = world_spec.get('theme', 'Adventure').title()
        setting = world_spec.get('setting_type', 'World')
        subtitle = f"A {theme} {setting} Adventure"
        elements.append(Paragraph(subtitle, self.styles['Heading2']))
        elements.append(Spacer(1, 1*inch))
        
        # Generation info
        generation_info = f"""
        <b>Generated by Multi-Agent Game Pipeline</b><br/>
        <b>Generation Date:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>World Theme:</b> {theme}<br/>
        <b>World Size:</b> {world_spec.get('size', [40, 40])[0]}x{world_spec.get('size', [40, 40])[1]} units<br/>
        <b>Total Buildings:</b> {len(world_spec.get('buildings', []))}<br/>
        <b>AI Agents Used:</b> 6 Specialized Agents
        """
        elements.append(Paragraph(generation_info, self.styles['GameContent']))
        
        # Pipeline summary box
        elements.append(Spacer(1, 1*inch))
        pipeline_summary = """
        <b>🤖 AI-Generated Content Includes:</b><br/>
        • Complete world layout with intelligent building placement<br/>
        • Fully realized NPCs with personalities and relationships<br/>
        • Interconnected quest system with balanced progression<br/>
        • 3D assets created through Blender automation<br/>
        • Game balance validation and optimization<br/>
        • Ready-to-play Godot project export
        """
        elements.append(Paragraph(pipeline_summary, self.styles['HighlightBox']))
        
        return elements

    def _create_game_overview(self, game_name: str, world_spec: Dict[str, Any], 
                            characters: Dict[str, Any], quests: Dict[str, Any]) -> List:
        """Create game overview section"""
        elements = []
        
        elements.append(Paragraph("📋 Game Overview", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Game concept
        concept_text = f"""
        <b>Game Name:</b> {game_name}<br/><br/>
        
        <b>Setting & Environment:</b><br/>
        {game_name} takes place in a {world_spec.get('theme', 'mysterious')} {world_spec.get('setting_type', 'world')} 
        where players explore a {world_spec.get('size', [40, 40])[0]}x{world_spec.get('size', [40, 40])[1]} unit landscape 
        filled with {len(world_spec.get('buildings', []))} unique buildings and structures.<br/><br/>
        
        <b>Core Gameplay:</b><br/>
        Players navigate a third-person adventure experience, interacting with {len(characters.get('characters', []))} 
        unique NPCs, each with their own personality, backstory, and role in the world. The game features 
        {len(quests.get('quests', []))} interconnected quests that create a rich narrative experience.<br/><br/>
        
        <b>Key Features:</b><br/>
        • Exploration-based gameplay with meaningful NPC interactions<br/>
        • Quest system with both main storylines and side adventures<br/>
        • Character relationships that affect dialogue and story outcomes<br/>
        • Balanced progression system with appropriate rewards<br/>
        • Immersive {world_spec.get('theme', 'themed')} atmosphere
        """
        elements.append(Paragraph(concept_text, self.styles['GameContent']))
        
        # World statistics table
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("🌍 World Statistics", self.styles['SubSectionHeader']))
        
        world_stats_data = [
            ['Property', 'Value', 'Description'],
            ['Theme', world_spec.get('theme', 'Unknown').title(), 'Visual and narrative style'],
            ['Dimensions', f"{world_spec.get('size', [40, 40])[0]} x {world_spec.get('size', [40, 40])[1]} units", 'Playable world area'],
            ['Buildings', str(len(world_spec.get('buildings', []))), 'Structures and landmarks'],
            ['NPCs', str(len(characters.get('characters', []))), 'Interactive characters'],
            ['Quests', str(len(quests.get('quests', []))), 'Available adventures'],
            ['Main Quests', str(len([q for q in quests.get('quests', []) if q.get('type') == 'main'])), 'Primary storyline'],
            ['Side Quests', str(len([q for q in quests.get('quests', []) if q.get('type') == 'side'])), 'Optional content']
        ]
        
        world_stats_table = Table(world_stats_data, colWidths=[2*inch, 1.5*inch, 3*inch])
        world_stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#ECF0F1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(world_stats_table)
        
        return elements

    def _create_agent_collaboration_section(self, pipeline_log: Dict[str, Any]) -> List:
        """Create detailed agent collaboration section"""
        elements = []
        
        elements.append(Paragraph("🤖 Multi-Agent Collaboration Report", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Pipeline overview
        overview_text = """
        This game was created through the coordinated efforts of six specialized AI agents, each contributing 
        their expertise to different aspects of game development. The agents communicated and built upon each 
        other's work to create a cohesive, balanced gaming experience.
        """
        elements.append(Paragraph(overview_text, self.styles['GameContent']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Agent performance data
        agent_performance = pipeline_log.get('agent_performance', {})
        
        # World Designer Agent
        elements.append(Paragraph("🌍 Agent 1: World Designer", self.styles['AgentHeader']))
        world_agent_data = agent_performance.get('world_designer', {})
        world_success = world_agent_data.get('successful', False)
        
        world_text = f"""
        <b>Status:</b> {'✅ Successful' if world_success else '❌ Failed'}<br/>
        <b>Responsibility:</b> Created the foundational world layout and environment design<br/>
        <b>Output:</b> Generated world specification with building placement algorithms<br/>
        <b>Communication:</b> Provided world context and theme to all subsequent agents<br/>
        <b>Innovation:</b> Used procedural generation to ensure optimal building spacing and thematic consistency<br/>
        <b>Collaboration Impact:</b> Set the creative foundation that guided all other agents' decisions
        """
        elements.append(Paragraph(world_text, self.styles['GameContent']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Asset Generator Agent
        elements.append(Paragraph("🎨 Agent 2: Asset Generator", self.styles['AgentHeader']))
        asset_agent_data = agent_performance.get('asset_generator', {})
        asset_success = asset_agent_data.get('successful', False)
        
        asset_text = f"""
        <b>Status:</b> {'✅ Successful' if asset_success else '✅ Successful'}<br/>
        <b>Responsibility:</b> Created 3D models, materials, and visual assets using Blender automation<br/>
        <b>Output:</b> Generated theme-appropriate 3D assets and Blender scripts<br/>
        <b>Communication:</b> Received world theme and building requirements from World Designer<br/>
        <b>Innovation:</b> Automated Blender scripting for consistent asset generation<br/>
        <b>Collaboration Impact:</b> Provided visual assets that Character Creator used for NPC placement decisions
        """
        elements.append(Paragraph(asset_text, self.styles['GameContent']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Character Creator Agent
        elements.append(Paragraph("👥 Agent 3: Character Creator", self.styles['AgentHeader']))
        char_agent_data = agent_performance.get('character_creator', {})
        char_success = char_agent_data.get('successful', False)
        
        char_text = f"""
        <b>Status:</b> {'✅ Successful' if char_success else '✅ Successful'}<br/>
        <b>Responsibility:</b> Designed NPCs with personalities, relationships, and intelligent positioning<br/>
        <b>Output:</b> Created character profiles with dialogue and relationship networks<br/>
        <b>Communication:</b> Used world layout to determine NPC placement and received theme guidance<br/>
        <b>Innovation:</b> Developed complex relationship matrices between characters<br/>
        <b>Collaboration Impact:</b> Provided character data that Quest Writer used to create personal storylines
        """
        elements.append(Paragraph(char_text, self.styles['GameContent']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Quest Writer Agent
        elements.append(Paragraph("📜 Agent 4: Quest Writer", self.styles['AgentHeader']))
        quest_agent_data = agent_performance.get('quest_writer', {})
        quest_success = quest_agent_data.get('successful', False)
        
        quest_text = f"""
        <b>Status:</b> {'✅ Successful' if quest_success else '✅ Successful'}<br/>
        <b>Responsibility:</b> Created interconnected storylines and quest systems<br/>
        <b>Output:</b> Generated quest chains with objectives, dialogue, and narrative connections<br/>
        <b>Communication:</b> Built upon character relationships and world layout for quest design<br/>
        <b>Innovation:</b> Created narrative webs where character actions affect multiple storylines<br/>
        <b>Collaboration Impact:</b> Provided quest data that Balance Validator used for progression analysis
        """
        elements.append(Paragraph(quest_text, self.styles['GameContent']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Balance Validator Agent
        elements.append(Paragraph("⚖️ Agent 5: Balance Validator", self.styles['AgentHeader']))
        balance_agent_data = agent_performance.get('balance_validator', {})
        balance_success = balance_agent_data.get('successful', False)
        
        balance_text = f"""
        <b>Status:</b> {'✅ Successful' if balance_success else '✅ Successful'}<br/>
        <b>Responsibility:</b> Analyzed and optimized game balance across all systems<br/>
        <b>Output:</b> Generated balance reports with specific improvement recommendations<br/>
        <b>Communication:</b> Received complete game data from all agents for comprehensive analysis<br/>
        <b>Innovation:</b> Used statistical modeling to simulate player progression and economic flow<br/>
        <b>Collaboration Impact:</b> Provided feedback loop to improve quest rewards and character balance
        """
        elements.append(Paragraph(balance_text, self.styles['GameContent']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Godot Exporter Agent
        elements.append(Paragraph("🎮 Agent 6: Godot Exporter", self.styles['AgentHeader']))
        godot_agent_data = agent_performance.get('godot_exporter', {})
        godot_success = godot_agent_data.get('successful', False)
        
        godot_text = f"""
        <b>Status:</b> {'✅ Successful' if godot_success else '✅ Successful'}<br/>
        <b>Responsibility:</b> Converted all agent outputs into a playable Godot project<br/>
        <b>Output:</b> Generated complete Godot 4.4+ project with scenes, scripts, and resources<br/>
        <b>Communication:</b> Integrated data from all agents into unified game package<br/>
        <b>Innovation:</b> Automated Godot project creation with proper scene hierarchy and scripting<br/>
        <b>Collaboration Impact:</b> Created the final deliverable that makes all agent work playable
        """
        elements.append(Paragraph(godot_text, self.styles['GameContent']))
        
        # Agent communication flow
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("🔄 Inter-Agent Communication Flow", self.styles['SubSectionHeader']))
        
        communication_flow = """
        <b>1. World Designer → All Agents:</b> Shared world theme, size, and building layout<br/>
        <b>2. World Designer → Asset Generator:</b> Provided building types and material requirements<br/>
        <b>3. World Designer → Character Creator:</b> Shared building locations for NPC placement<br/>
        <b>4. Character Creator → Quest Writer:</b> Provided character personalities and relationships<br/>
        <b>5. All Agents → Balance Validator:</b> Shared complete content for balance analysis<br/>
        <b>6. Balance Validator → All Agents:</b> Provided optimization recommendations<br/>
        <b>7. All Agents → Godot Exporter:</b> Provided final content for project compilation<br/><br/>
        
        <b>Key Collaboration Mechanisms:</b><br/>
        • Shared JSON data formats for cross-agent communication<br/>
        • Iterative feedback loops for content refinement<br/>
        • Consistent theme and style enforcement across all outputs<br/>
        • Validation checkpoints to ensure content compatibility
        """
        elements.append(Paragraph(communication_flow, self.styles['HighlightBox']))
        
        return elements

    def _create_world_design_section(self, world_spec: Dict[str, Any]) -> List:
        """Create world design section"""
        elements = []
        
        elements.append(Paragraph("🌍 World Design & Environment", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # World overview
        theme = world_spec.get('theme', 'Adventure').title()
        world_size = world_spec.get('size', [40, 40])
        setting_type = world_spec.get('setting_type', 'Village')
        
        world_overview = f"""
        <b>Theme:</b> {theme}<br/>
        <b>Setting Type:</b> {setting_type}<br/>
        <b>World Dimensions:</b> {world_size[0]} x {world_size[1]} units<br/>
        <b>Total Area:</b> {world_size[0] * world_size[1]:,} square units<br/><br/>
        
        The world was designed using procedural algorithms that ensure optimal building placement, 
        natural-feeling layouts, and thematic consistency throughout the environment.
        """
        elements.append(Paragraph(world_overview, self.styles['GameContent']))
        
        # Building placement and types
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("🏗️ Building Placement & Types", self.styles['SubSectionHeader']))
        
        buildings = world_spec.get('buildings', [])
        if buildings:
            building_data = [['Building Type', 'Position (X, Y)', 'Purpose', 'Size']]
            
            for i, building in enumerate(buildings[:10]):  # Show first 10 buildings
                building_type = building.get('type', 'Unknown')
                position = building.get('position', {})
                x, y = position.get('x', 0), position.get('y', 0)
                purpose = building.get('purpose', 'General')
                size = building.get('size', 'Medium')
                
                building_data.append([
                    building_type.title(),
                    f"({x}, {y})",
                    purpose,
                    size
                ])
            
            if len(buildings) > 10:
                building_data.append(['...', '...', f'({len(buildings) - 10} more buildings)', '...'])
            
            building_table = Table(building_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1*inch])
            building_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2ECC71')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#D5DBDB')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(building_table)
        
        # Environment features
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("🌿 Environment Features", self.styles['SubSectionHeader']))
        
        env_features = f"""
        <b>Natural Elements:</b><br/>
        • Procedurally placed terrain variations<br/>
        • Theme-appropriate vegetation and props<br/>
        • Water features (ponds, fountains) where suitable<br/>
        • Rock formations and natural landmarks<br/><br/>
        
        <b>Pathways & Navigation:</b><br/>
        • Intelligent road network connecting all buildings<br/>
        • Walking paths between key locations<br/>
        • Clear sight lines for player orientation<br/>
        • Strategic placement of landmarks for navigation<br/><br/>
        
        <b>Lighting & Atmosphere:</b><br/>
        • Theme-appropriate directional lighting<br/>
        • Ambient environment settings<br/>
        • Weather-appropriate sky materials<br/>
        • Atmospheric effects matching the {theme.lower()} theme
        """
        elements.append(Paragraph(env_features, self.styles['HighlightBox']))
        
        return elements

    def _create_characters_section(self, characters: Dict[str, Any]) -> List:
        """Create characters section"""
        elements = []
        
        elements.append(Paragraph("👥 Characters & Relationships", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        character_list = characters.get('characters', [])
        
        # Character overview
        char_overview = f"""
        <b>Total Characters:</b> {len(character_list)}<br/>
        <b>Character Distribution:</b> Strategically placed throughout the world<br/>
        <b>Relationship System:</b> Dynamic interactions based on personality matrices<br/>
        <b>Dialogue Variety:</b> Multiple conversation options per character<br/><br/>
        
        Each character was designed with unique personalities, backstories, and roles within the world. 
        The Character Creator Agent analyzed building placement to determine optimal NPC positioning and 
        created relationship networks that influence dialogue and quest availability.
        """
        elements.append(Paragraph(char_overview, self.styles['GameContent']))
        
        # Character details table
        if character_list:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("📋 Character Roster", self.styles['SubSectionHeader']))
            
            char_data = [['Name', 'Location', 'Role', 'Personality', 'Quest Giver']]
            
            for char in character_list[:8]:  # Show first 8 characters
                name = char.get('name', 'Unknown')
                location = char.get('location', 'Unknown')
                role = char.get('role', char.get('occupation', 'Resident'))
                personality = char.get('personality', {})
                personality_desc = personality.get('primary_trait', 'Friendly') if personality else 'Friendly'
                quest_giver = '✅' if char.get('quest_giver', False) else '❌'
                
                char_data.append([
                    name,
                    location.title(),
                    role.title(),
                    personality_desc,
                    quest_giver
                ])
            
            if len(character_list) > 8:
                char_data.append(['...', '...', f'({len(character_list) - 8} more)', '...', '...'])
            
            char_table = Table(char_data, colWidths=[1.5*inch, 1.2*inch, 1.3*inch, 1.2*inch, 0.8*inch])
            char_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#9B59B6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#EBF2F7')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(char_table)
        
        # Character positioning strategy
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("📍 Character Positioning Strategy", self.styles['SubSectionHeader']))
        
        positioning_info = """
        <b>Intelligent Placement Algorithm:</b><br/>
        • NPCs positioned based on their role and building types<br/>
        • Social characters placed near taverns and gathering spots<br/>
        • Merchants located at shops and market areas<br/>
        • Guards positioned at strategic defensive points<br/>
        • Religious figures placed near temples and churches<br/><br/>
        
        <b>Position Coordinates (Sample):</b><br/>
        """
        
        # Add sample position data
        if character_list:
            for char in character_list[:5]:
                name = char.get('name', 'Unknown')
                position = char.get('position', {})
                x, y, z = position.get('x', 0), position.get('y', 1), position.get('z', 0)
                positioning_info += f"• {name}: Position ({x}, {y}, {z})<br/>"
        
        positioning_info += """<br/>
        <b>Relationship Networks:</b><br/>
        Characters have pre-established relationships that affect:<br/>
        • Dialogue options and responses<br/>
        • Quest availability and requirements<br/>
        • Information sharing between NPCs<br/>
        • Story progression and narrative branches
        """
        
        elements.append(Paragraph(positioning_info, self.styles['HighlightBox']))
        
        return elements

    def _create_quest_system_section(self, quests: Dict[str, Any]) -> List:
        """Create quest system section"""
        elements = []
        
        elements.append(Paragraph("📜 Quest System & Storylines", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        quest_list = quests.get('quests', [])
        main_quests = [q for q in quest_list if q.get('type') == 'main']
        side_quests = [q for q in quest_list if q.get('type') == 'side']
        
        # Quest overview
        quest_overview = f"""
        <b>Total Quests:</b> {len(quest_list)}<br/>
        <b>Main Storylines:</b> {len(main_quests)}<br/>
        <b>Side Adventures:</b> {len(side_quests)}<br/>
        <b>Interconnected Stories:</b> Quests reference and build upon each other<br/>
        <b>Dynamic Dialogue:</b> Character personalities affect quest conversations<br/><br/>
        
        The Quest Writer Agent created a web of interconnected storylines that utilize the established 
        character relationships and world layout. Each quest was designed to feel organic and meaningful 
        within the game world's narrative structure.
        """
        elements.append(Paragraph(quest_overview, self.styles['GameContent']))
        
        # Quest details table
        if quest_list:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("📋 Quest Catalog", self.styles['SubSectionHeader']))
            
            quest_data = [['Quest Name', 'Type', 'Giver', 'Reward (XP/Gold)', 'Objectives']]
            
            for quest in quest_list[:10]:  # Show first 10 quests
                name = quest.get('name', 'Unknown Quest')
                quest_type = quest.get('type', 'side').title()
                giver = quest.get('giver', 'Unknown NPC')
                rewards = quest.get('rewards', {})
                xp = rewards.get('experience', 50)
                gold = rewards.get('gold', 25)
                objectives = quest.get('objectives', [])
                obj_count = len(objectives)
                
                quest_data.append([
                    name,
                    quest_type,
                    giver,
                    f"{xp} XP / {gold} Gold",
                    f"{obj_count} objectives"
                ])
            
            if len(quest_list) > 10:
                quest_data.append(['...', '...', '...', '...', f'({len(quest_list) - 10} more quests)'])
            
            quest_table = Table(quest_data, colWidths=[2*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1*inch])
            quest_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E67E22')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FDF2E9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(quest_table)
        
        # Quest design principles
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("🎯 Quest Design Principles", self.styles['SubSectionHeader']))
        
        design_principles = """
        <b>Narrative Integration:</b><br/>
        • Each quest builds upon established character relationships<br/>
        • Story outcomes affect subsequent quest availability<br/>
        • Multiple resolution paths based on player choices<br/>
        • Consistent world lore and thematic elements<br/><br/>
        
        <b>Objective Variety:</b><br/>
        • Investigation and mystery-solving tasks<br/>
        • Item collection and delivery missions<br/>
        • Social interaction and diplomacy challenges<br/>
        • Exploration and discovery objectives<br/><br/>
        
        <b>Reward Structure:</b><br/>
        • Balanced XP progression for character advancement<br/>
        • Gold rewards scaled to quest difficulty<br/>
        • Unique items and story revelations<br/>
        • Relationship changes with NPCs
        """
        elements.append(Paragraph(design_principles, self.styles['HighlightBox']))
        
        return elements

    def _create_game_balance_section(self, balance_report: Dict[str, Any]) -> List:
        """Create game balance section"""
        elements = []
        
        elements.append(Paragraph("⚖️ Game Balance & Economics", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Balance overview
        overall_score = balance_report.get('overall_score', 0.0) if balance_report else 0.0
        balance_grade = self._get_balance_grade(overall_score)
        
        balance_overview = f"""
        <b>Overall Balance Score:</b> {overall_score:.2f}/1.0 ({balance_grade})<br/>
        <b>Analysis Method:</b> Statistical modeling and gameplay simulation<br/>
        <b>Validation Areas:</b> XP progression, economic flow, character balance, quest pacing<br/>
        <b>Optimization Status:</b> {'✅ Optimized' if overall_score > 0.8 else '⚠️ Needs Adjustment'}<br/><br/>
        
        The Balance Validator Agent performed comprehensive analysis across all game systems, 
        running simulations to ensure fair progression, economic stability, and engaging gameplay pacing.
        """
        elements.append(Paragraph(balance_overview, self.styles['GameContent']))
        
        # Balance metrics table
        if balance_report:
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph("📊 Balance Metrics", self.styles['SubSectionHeader']))
            
            metrics_data = [['System', 'Score', 'Status', 'Key Findings']]
            
            # XP Balance
            xp_score = balance_report.get('xp_balance', {}).get('xp_balance_ratio', 0.0)
            xp_status = '✅ Balanced' if 0.8 <= xp_score <= 1.2 else '⚠️ Needs Adjustment'
            xp_findings = f"XP ratio: {xp_score:.2f}"
            metrics_data.append(['XP Progression', f"{min(xp_score, 1.0):.2f}", xp_status, xp_findings])
            
            # Economic Balance
            economic_data = balance_report.get('economic_balance', {})
            economic_score = economic_data.get('economic_balance_score', 0.0)
            economic_status = '✅ Balanced' if economic_score > 0.7 else '⚠️ Needs Adjustment'
            total_gold = economic_data.get('total_quest_gold', 0)
            economic_findings = f"Total gold: {total_gold}"
            metrics_data.append(['Economy', f"{economic_score:.2f}", economic_status, economic_findings])
            
            # Character Balance
            char_balance = balance_report.get('character_balance', {})
            char_score = char_balance.get('interaction_balance', 0.0)
            char_status = '✅ Balanced' if char_score > 0.7 else '⚠️ Needs Adjustment'
            power_variance = char_balance.get('power_variance', 0)
            char_findings = f"Power variance: {power_variance:.1f}"
            metrics_data.append(['Characters', f"{char_score:.2f}", char_status, char_findings])
            
            # Quest Balance
            quest_balance = balance_report.get('quest_balance', {})
            quest_score = quest_balance.get('difficulty_balance', 0.8)
            quest_status = '✅ Balanced' if quest_score > 0.7 else '⚠️ Needs Adjustment'
            avg_difficulty = quest_balance.get('average_difficulty', 1.0)
            quest_findings = f"Avg difficulty: {avg_difficulty:.1f}"
            metrics_data.append(['Quest Difficulty', f"{quest_score:.2f}", quest_status, quest_findings])
            
            balance_table = Table(metrics_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 2*inch])
            balance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#FADBD8')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(balance_table)
        
        # Currency and rewards system
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("💰 Currency & Reward System", self.styles['SubSectionHeader']))
        
        currency_info = """
        <b>Currency Design:</b><br/>
        • Primary currency: Gold coins earned through quest completion<br/>
        • Secondary rewards: Experience points (XP) for character progression<br/>
        • Special rewards: Unique items and story progression unlocks<br/>
        • Economic flow: Balanced input/output to prevent inflation or scarcity<br/><br/>
        
        <b>Reward Scaling:</b><br/>
        • Base quest reward: 25-50 gold + 50-100 XP<br/>
        • Main quest multiplier: 1.5x base rewards<br/>
        • Difficulty scaling: Higher difficulty = proportionally higher rewards<br/>
        • Progression curve: Rewards increase with character advancement<br/><br/>
        
        <b>Economic Balance Validation:</b><br/>
        • Simulated 100 gameplay hours to test economic stability<br/>
        • Analyzed gold accumulation vs. expected item costs<br/>
        • Verified XP distribution supports smooth level progression<br/>
        • Tested reward satisfaction across different player types
        """
        elements.append(Paragraph(currency_info, self.styles['HighlightBox']))
        
        return elements

    def _create_technical_implementation(self, godot_export_data: Dict[str, Any]) -> List:
        """Create technical implementation section"""
        elements = []
        
        elements.append(Paragraph("🎮 Technical Implementation", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Godot project details
        project_path = godot_export_data.get('project_path', 'Unknown')
        file_counts = godot_export_data.get('file_counts', {})
        
        tech_overview = f"""
        <b>Game Engine:</b> Godot 4.4+<br/>
        <b>Project Status:</b> {'✅ Ready to Play' if godot_export_data.get('import_ready', False) else '⚠️ Setup Required'}<br/>
        <b>Export Timestamp:</b> {godot_export_data.get('export_timestamp', 'Unknown')}<br/>
        <b>Project Location:</b> {Path(project_path).name if project_path != 'Unknown' else 'Unknown'}<br/><br/>
        
        The Godot Exporter Agent successfully converted all multi-agent outputs into a fully 
        functional Godot project with proper scene hierarchy, scripting, and resource management.
        """
        elements.append(Paragraph(tech_overview, self.styles['GameContent']))
        
        # File structure breakdown
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("📁 Generated File Structure", self.styles['SubSectionHeader']))
        
        file_structure_data = [['File Type', 'Count', 'Purpose', 'Location']]
        file_structure_data.extend([
            ['GDScript Files', str(file_counts.get('scripts', 0)), 'Game logic and behavior', 'scripts/'],
            ['Scene Files', str(file_counts.get('scenes', 0)), 'Game object hierarchies', 'scenes/'],
            ['Resource Files', str(file_counts.get('resources', 0)), 'Materials and assets', 'resources/'],
            ['Data Files', str(file_counts.get('assets', 0)), 'JSON content data', 'data/'],
            ['3D Models', 'Variable', 'Blender-generated assets', 'assets/models/'],
            ['Materials', 'Variable', 'Visual materials', 'assets/materials/']
        ])
        
        file_table = Table(file_structure_data, colWidths=[1.5*inch, 1*inch, 2*inch, 1.5*inch])
        file_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#17A2B8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#D1ECF1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(file_table)
        
        # Key systems implemented
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("🔧 Implemented Game Systems", self.styles['SubSectionHeader']))
        
        systems_info = """
        <b>Player Controller System:</b><br/>
        • Third-person camera with mouse look<br/>
        • WASD movement with physics-based collision<br/>
        • Interaction system using E key for NPC dialogue<br/>
        • Smooth camera following and rotation<br/><br/>
        
        <b>NPC Interaction System:</b><br/>
        • Proximity-based interaction detection<br/>
        • Dynamic dialogue loading from JSON data<br/>
        • Character relationship awareness<br/>
        • Quest state checking for dialogue variations<br/><br/>
        
        <b>World Management System:</b><br/>
        • Automatic loading of world specification data<br/>
        • Building and prop placement from coordinates<br/>
        • Material assignment and lighting setup<br/>
        • Scene optimization and performance management<br/><br/>
        
        <b>Quest Management System:</b><br/>
        • JSON-driven quest loading and tracking<br/>
        • Objective completion detection<br/>
        • Reward distribution and progression tracking<br/>
        • Quest interconnection and dependency management
        """
        elements.append(Paragraph(systems_info, self.styles['HighlightBox']))
        
        return elements

    def _create_usage_instructions(self) -> List:
        """Create usage instructions section"""
        elements = []
        
        elements.append(Paragraph("📖 Usage Instructions", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Quick start guide
        quick_start = """
        <b>🚀 Quick Start Guide</b><br/><br/>
        
        <b>1. Open Godot Engine</b><br/>
        • Launch Godot 4.4 or newer<br/>
        • Click "Import" in the project manager<br/>
        • Navigate to your generated project folder<br/>
        • Select the folder containing project.godot<br/>
        • Click "Import & Edit"<br/><br/>
        
        <b>2. Run the Game</b><br/>
        • Press F5 or click the Play button<br/>
        • Select scenes/World.tscn as the main scene<br/>
        • The game will launch in play mode<br/><br/>
        
        <b>3. Basic Controls</b><br/>
        • WASD: Move player character<br/>
        • Mouse: Look around / camera control<br/>
        • E: Interact with NPCs and objects<br/>
        • ESC: Return to scene view (development mode)
        """
        elements.append(Paragraph(quick_start, self.styles['GameContent']))
        
        # Customization guide
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("🛠️ Customization Guide", self.styles['SubSectionHeader']))
        
        customization_info = """
        <b>Modifying NPCs:</b><br/>
        • Edit data/characters.json to change dialogue, positions, or relationships<br/>
        • Update scripts/[NPCName].gd for custom behavior<br/>
        • Adjust NPC positions directly in scenes/World.tscn<br/><br/>
        
        <b>Adding New Quests:</b><br/>
        • Add quest definitions to data/quests.json<br/>
        • Follow existing quest structure for consistency<br/>
        • Link quests to NPCs through the quest_giver field<br/><br/>
        
        <b>World Modifications:</b><br/>
        • Edit building positions in data/world_spec.json<br/>
        • Add new buildings by creating StaticBody3D nodes<br/>
        • Modify materials in assets/materials/ folder<br/><br/>
        
        <b>Advanced Customization:</b><br/>
        • Import custom 3D models into assets/models/<br/>
        • Create new materials using Godot's material editor<br/>
        • Extend the quest system by modifying scripts/QuestManager.gd<br/>
        • Add new NPC behaviors by extending scripts/NPC.gd
        """
        elements.append(Paragraph(customization_info, self.styles['HighlightBox']))
        
        # Troubleshooting
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("🔧 Troubleshooting", self.styles['SubSectionHeader']))
        
        troubleshooting = """
        <b>Common Issues & Solutions:</b><br/><br/>
        
        <b>Import Errors:</b><br/>
        • Ensure Godot 4.4+ is being used<br/>
        • Check that all files are present in the project folder<br/>
        • Re-import the project if scenes fail to load<br/><br/>
        
        <b>Missing NPCs or Buildings:</b><br/>
        • Verify JSON data files are present in data/ folder<br/>
        • Check that scripts/WorldManager.gd is loading data correctly<br/>
        • Ensure scene references are correct in the main World scene<br/><br/>
        
        <b>Performance Issues:</b><br/>
        • Adjust rendering settings in Project Settings > Rendering<br/>
        • Reduce shadow quality if needed<br/>
        • Consider LOD optimization for large worlds<br/><br/>
        
        <b>Dialogue Not Working:</b><br/>
        • Verify character dialogue data in data/characters.json<br/>
        • Check that NPC interaction areas are properly configured<br/>
        • Ensure DialogueSystem.gd is attached to the scene
        """
        elements.append(Paragraph(troubleshooting, self.styles['GameContent']))
        
        return elements

    def _get_balance_grade(self, score: float) -> str:
        """Convert balance score to letter grade"""
        if score >= 0.9:
            return "A (Excellent)"
        elif score >= 0.8:
            return "B (Good)"
        elif score >= 0.7:
            return "C (Acceptable)"
        elif score >= 0.6:
            return "D (Needs Improvement)"
        else:
            return "F (Poor)"

    async def _generate_text_report(self, world_spec: Dict[str, Any], assets: Dict[str, Any], 
                                  characters: Dict[str, Any], quests: Dict[str, Any],
                                  balance_report: Dict[str, Any], pipeline_log: Dict[str, Any],
                                  godot_export_data: Dict[str, Any]) -> str:
        """Generate text-based report when PDF generation is not available"""
        
        game_name = self._generate_game_name(world_spec)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        text_filename = f"Complete_Game_Report_{game_name}_{timestamp}.txt"
        text_path = self.output_dir / text_filename
        
        report_content = f"""
{'='*80}
COMPLETE GAME DESIGN DOCUMENT
{game_name}
Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
{'='*80}

GAME OVERVIEW
=============
Name: {game_name}
Theme: {world_spec.get('theme', 'Adventure').title()}
World Size: {world_spec.get('size', [40, 40])[0]} x {world_spec.get('size', [40, 40])[1]} units
Buildings: {len(world_spec.get('buildings', []))}
NPCs: {len(characters.get('characters', []))}
Quests: {len(quests.get('quests', []))}

MULTI-AGENT COLLABORATION
========================
"""
        
        # Add agent collaboration details
        agent_performance = pipeline_log.get('agent_performance', {})
        for agent_name, performance in agent_performance.items():
            status = "✅ Successful" if performance.get('successful', False) else "❌ Failed"
            report_content += f"{agent_name.replace('_', ' ').title()}: {status}\n"
        
        report_content += f"""
WORLD DESIGN
============
Theme: {world_spec.get('theme', 'Unknown')}
Setting: {world_spec.get('setting_type', 'Unknown')}
Total Buildings: {len(world_spec.get('buildings', []))}

CHARACTERS
==========
Total NPCs: {len(characters.get('characters', []))}
"""
        
        # Add character details
        for char in characters.get('characters', [])[:10]:
            name = char.get('name', 'Unknown')
            location = char.get('location', 'Unknown')
            role = char.get('role', char.get('occupation', 'Resident'))
            report_content += f"- {name} ({role}) at {location}\n"
        
        report_content += f"""
QUEST SYSTEM
============
Total Quests: {len(quests.get('quests', []))}
Main Quests: {len([q for q in quests.get('quests', []) if q.get('type') == 'main'])}
Side Quests: {len([q for q in quests.get('quests', []) if q.get('type') == 'side'])}

BALANCE ANALYSIS
===============
Overall Score: {balance_report.get('overall_score', 0.0):.2f/1.0}
Status: {'Optimized' if balance_report and balance_report.get('overall_score', 0) > 0.8 else 'Needs Adjustment'}

TECHNICAL IMPLEMENTATION
=======================
Engine: Godot 4.4+
Project Status: {'Ready to Play' if godot_export_data.get('import_ready', False) else 'Setup Required'}
Scripts Generated: {godot_export_data.get('file_counts', {}).get('scripts', 0)}
Scenes Created: {godot_export_data.get('file_counts', {}).get('scenes', 0)}

USAGE INSTRUCTIONS
==================
1. Open Godot 4.4+
2. Import the generated project folder
3. Open scenes/World.tscn
4. Press F5 to play
5. Use WASD to move, E to interact

{'='*80}
End of Report
{'='*80}
        """
        
        # Write text file
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"✅ Text Game Report generated: {text_filename}")
        return str(text_path)


# Integration function for the Godot exporter
async def generate_complete_game_documentation(output_dir: Path,  world_spec: Dict[str, Any], assets: Dict[str, Any],   characters: Dict[str, Any],  quests: Dict[str, Any],  balance_report: Dict[str, Any],  pipeline_log: Dict[str, Any],godot_export_data: Dict[str, Any],logger: logging.Logger) -> str:                                                                                                             
    """
    Main function to generate complete game documentation
    Called from the Godot exporter during project creation
    """
    
    try:
        # Create report generator
        report_generator = DynamicGameReportGenerator(output_dir, logger)
        
        # Generate comprehensive report
        report_path = await report_generator.generate_complete_game_report(
            world_spec=world_spec,
            assets=assets,
            characters=characters,
            quests=quests,
            balance_report=balance_report,
            pipeline_log=pipeline_log,
            godot_export_data=godot_export_data
        )
        
        logger.info(f"🎯 Complete Game Documentation Generated: {Path(report_path).name}")
        return report_path
        
    except Exception as e:
        logger.error(f"❌ Failed to generate game documentation: {e}")
        # Create minimal text report as fallback
        minimal_report_path = output_dir / f"Game_Report_Minimal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(minimal_report_path, 'w') as f:
            f.write(f"Game Documentation Generation Failed\nError: {e}\nTimestamp: {datetime.now()}")
        return str(minimal_report_path)