#!/usr/bin/env python3
"""
QUEST WRITER AGENT - AI-POWERED STORYLINE GENERATOR
Creates interconnected quest systems using existing NPCs and world data
"""

import asyncio
import json
import random
import hashlib
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Google ADK imports
from google.adk.agents import Agent

# AI imports
try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

@dataclass
class QuestObjective:
    id: str
    description: str
    type: str  # talk_to_npc, collect_item, go_to_location, defeat_enemy
    target: str
    quantity: int = 1
    optional: bool = False
    prerequisites: List[str] = None

@dataclass
class QuestReward:
    experience: int
    gold: int
    items: List[str] = None
    relationship_changes: List[Dict[str, Any]] = None

@dataclass
class QuestDefinition:
    id: str
    title: str
    description: str
    summary: str
    giver_npc: str
    objectives: List[QuestObjective]
    rewards: QuestReward
    prerequisites: List[str] = None
    level_requirement: int = 1
    estimated_duration: str = "15-30 minutes"
    quest_type: str = "main"  # main, side, chain
    interconnected_quests: List[str] = None
    narrative_importance: str = "medium"

class AIQuestWriter:
    """
    AI-POWERED QUEST WRITER
    - Analyzes existing NPCs and creates interconnected storylines
    - Generates quest chains that utilize character relationships
    - Creates branching narratives with meaningful choices
    - Ensures quest balance and progression
    """
    
    def __init__(self, output_dir: str = "generated_quests"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Quest directories
        self.quests_dir = self.output_dir / "quest_definitions"
        self.chains_dir = self.output_dir / "quest_chains"
        self.dialogue_dir = self.output_dir / "quest_dialogues"
        
        for dir_path in [self.quests_dir, self.chains_dir, self.dialogue_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Quest tracking
        self.generated_quests = []
        self.quest_chains = {}
        self.npc_quest_involvement = {}
        
        # Initialize logging FIRST
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI AFTER logger is ready
        self._initialize_ai()
    
    def _initialize_ai(self):
        """Initialize AI for quest generation"""
        if not AI_AVAILABLE:
            self.logger.warning("AI not available - using template-based generation")
            return
            
        try:
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                self.logger.warning("No API key found for AI quest generation")
                return
                
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config=genai.types.GenerationConfig(
                    temperature=0.9,  # Creative but coherent
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=1500,
                )
            )
            self.logger.info("✅ AI initialized for quest generation")
        except Exception as e:
            self.logger.error(f"AI initialization failed: {e}")
    
    async def generate_quest_system(self, world_spec: Dict[str, Any], 
                                   characters: List[Dict[str, Any]], 
                                   quest_count: int = 5) -> Dict[str, Any]:
        """
        Generate complete interconnected quest system
        """
        self.logger.info(f"🗡️ Generating {quest_count} interconnected quests...")
        
        theme = world_spec.get('theme', 'medieval')
        buildings = world_spec.get('buildings', [])
        
        # Analyze NPCs for quest potential
        print(f"\n📊 Analyzing {len(characters)} NPCs for quest opportunities...")
        npc_analysis = await self._analyze_npcs_for_quests(characters, theme)
        
        # Generate main quest chain
        print(f"\n⚔️ Creating main quest chain...")
        main_quest_chain = await self._generate_main_quest_chain(npc_analysis, theme, buildings)
        
        # Generate side quests
        print(f"\n🌟 Creating side quests...")
        side_quests = await self._generate_side_quests(npc_analysis, theme, quest_count - len(main_quest_chain))
        
        # Combine all quests
        all_quests = main_quest_chain + side_quests
        
        # Create quest interconnections
        print(f"\n🔗 Creating quest interconnections...")
        interconnected_quests = await self._create_quest_interconnections(all_quests, npc_analysis)
        
        # Generate quest dialogues
        print(f"\n💬 Generating quest dialogues...")
        quest_dialogues = await self._generate_quest_dialogues(interconnected_quests, npc_analysis)
        
        # Save quest system
        print(f"\n💾 Saving quest system...")
        quest_manifest = await self._save_quest_system(interconnected_quests, quest_dialogues, theme, world_spec)
        
        print(f"\n🎉 Quest System Generation Complete!")
        print(f"   📜 Total Quests: {len(interconnected_quests)}")
        print(f"   🔗 Interconnected: {sum(1 for q in interconnected_quests if q.interconnected_quests)}")
        print(f"   👥 NPCs Involved: {len(set(q.giver_npc for q in interconnected_quests))}")
        
        return {
            'quests': [asdict(quest) for quest in interconnected_quests],
            'quest_dialogues': quest_dialogues,
            'npc_involvement': self.npc_quest_involvement,
            'generation_summary': {
                'total_quests': len(interconnected_quests),
                'main_quests': len([q for q in interconnected_quests if q.quest_type == 'main']),
                'side_quests': len([q for q in interconnected_quests if q.quest_type == 'side']),
                'interconnected_count': sum(1 for q in interconnected_quests if q.interconnected_quests),
                'npcs_involved': len(set(q.giver_npc for q in interconnected_quests)),
                'total_objectives': sum(len(q.objectives) for q in interconnected_quests),
                'estimated_playtime': self._calculate_total_playtime(interconnected_quests)
            },
            'theme': theme,
            'quest_manifest': quest_manifest,
            'output_directory': str(self.output_dir),
            'status': 'success'
        }
    
    async def _analyze_npcs_for_quests(self, characters: List[Dict[str, Any]], theme: str) -> Dict[str, Any]:
        """Analyze NPCs to determine their quest-giving potential"""
        
        npc_analysis = {}
        
        for char in characters:
            char_name = char.get('name', 'Unknown')
            char_role = char.get('role', 'villager')
            personality = char.get('personality', {})
            relationships = char.get('relationships', [])
            
            # Determine quest-giving potential
            quest_potential = await self._assess_quest_potential(char, theme)
            
            # Analyze relationship conflicts for quest opportunities
            relationship_conflicts = self._find_relationship_conflicts(char, characters)
            
            npc_analysis[char_name] = {
                'character': char,
                'quest_potential': quest_potential,
                'role': char_role,
                'personality': personality,
                'relationships': relationships,
                'relationship_conflicts': relationship_conflicts,
                'quest_types': quest_potential.get('suitable_quest_types', []),
                'narrative_importance': quest_potential.get('narrative_importance', 'low')
            }
        
        return npc_analysis
    
    async def _assess_quest_potential(self, character: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Assess an NPC's potential for quest-giving using AI"""
        
        char_name = character.get('name', 'Unknown')
        char_role = character.get('role', 'villager')
        personality = character.get('personality', {})
        
        if AI_AVAILABLE and hasattr(self, 'gemini_model'):
            try:
                assessment_prompt = f"""Analyze this NPC's quest-giving potential in a {theme} game:
                
                Name: {char_name}
                Role: {char_role}
                Personality: {personality.get('primary_trait', 'unknown')}, {personality.get('secondary_trait', 'unknown')}
                Motivation: {personality.get('motivation', 'unknown')}
                Fear: {personality.get('fear', 'unknown')}
                Secret: {personality.get('secret', 'has hidden depths')}
                
                Determine:
                1. Quest-giving potential (1-10 scale)
                2. Suitable quest types (fetch, escort, mystery, conflict, etc.)
                3. Narrative importance (low, medium, high)
                4. Potential quest themes based on their personality
                5. What kind of problems they might have
                
                Format as:
                POTENTIAL: [1-10 score]
                QUEST_TYPES: [list of suitable types]
                IMPORTANCE: [low/medium/high]
                THEMES: [potential quest themes]
                PROBLEMS: [what issues they might need help with]"""
                
                response = await self._call_gemini(assessment_prompt)
                if response:
                    return self._parse_quest_potential(response)
            except Exception as e:
                self.logger.warning(f"AI assessment failed for {char_name}: {e}")
        
        # Fallback assessment
        return self._fallback_quest_assessment(character)
    
    def _parse_quest_potential(self, response: str) -> Dict[str, Any]:
        """Parse AI quest potential assessment"""
        potential_data = {}
        
        for line in response.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if key == 'POTENTIAL':
                    try:
                        potential_data['potential_score'] = int(value)
                    except ValueError:
                        potential_data['potential_score'] = 5
                elif key == 'QUEST_TYPES':
                    potential_data['suitable_quest_types'] = [t.strip() for t in value.split(',')]
                elif key == 'IMPORTANCE':
                    potential_data['narrative_importance'] = value.lower()
                elif key == 'THEMES':
                    potential_data['quest_themes'] = [t.strip() for t in value.split(',')]
                elif key == 'PROBLEMS':
                    potential_data['potential_problems'] = [p.strip() for p in value.split(',')]
        
        return potential_data
    
    def _fallback_quest_assessment(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback quest assessment without AI"""
        
        role = character.get('role', 'villager')
        personality = character.get('personality', {})
        
        # Role-based quest potential
        role_potential = {
            'merchant': 8, 'blacksmith': 7, 'guard': 9, 'priest': 8, 'noble': 9,
            'farmer': 5, 'innkeeper': 7, 'healer': 6, 'messenger': 6
        }
        
        potential_score = role_potential.get(role, 5)
        
        # Role-specific quest types
        role_quest_types = {
            'merchant': ['fetch', 'delivery', 'economic'],
            'blacksmith': ['craft', 'resource_gathering', 'protection'],
            'guard': ['patrol', 'investigation', 'combat'],
            'priest': ['mystery', 'spiritual', 'healing'],
            'noble': ['political', 'social', 'conflict'],
            'farmer': ['resource_gathering', 'protection', 'seasonal'],
            'innkeeper': ['social', 'information', 'hospitality'],
            'healer': ['rescue', 'gathering', 'humanitarian'],
            'messenger': ['delivery', 'information', 'travel']
        }
        
        quest_types = role_quest_types.get(role, ['fetch', 'social'])
        
        return {
            'potential_score': potential_score,
            'suitable_quest_types': quest_types,
            'narrative_importance': 'high' if potential_score >= 8 else 'medium' if potential_score >= 6 else 'low',
            'quest_themes': [f"{role} duties", "community service"],
            'potential_problems': [f"Issues with {role} work", "Community conflicts"]
        }
    
    def _find_relationship_conflicts(self, character: Dict[str, Any], all_characters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find relationship conflicts that could drive quests"""
        
        conflicts = []
        char_relationships = character.get('relationships', [])
        
        for relationship in char_relationships:
            if relationship.get('relationship_strength', 0) < -20:  # Negative relationships
                target_name = relationship.get('target_character')
                conflict_type = relationship.get('relationship_type', 'rival')
                
                conflicts.append({
                    'with': target_name,
                    'type': conflict_type,
                    'strength': relationship.get('relationship_strength', 0),
                    'history': relationship.get('history', ''),
                    'quest_potential': 'high' if relationship.get('relationship_strength', 0) < -50 else 'medium'
                })
        
        return conflicts
    
    async def _generate_main_quest_chain(self, npc_analysis: Dict[str, Any], theme: str, buildings: List[Dict]) -> List[QuestDefinition]:
        """Generate main quest chain with narrative progression"""
        
        # Find NPCs suitable for main quests
        main_quest_npcs = [
            name for name, data in npc_analysis.items() 
            if data['quest_potential'].get('narrative_importance', 'low') in ['high', 'medium']
        ]
        
        if not main_quest_npcs:
            main_quest_npcs = list(npc_analysis.keys())[:2]
        
        main_quests = []
        
        # Generate 2-3 main quests
        for i, npc_name in enumerate(main_quest_npcs[:3]):
            npc_data = npc_analysis[npc_name]
            quest = await self._create_main_quest(npc_data, theme, i + 1, buildings)
            if quest:
                main_quests.append(quest)
                self._track_npc_involvement(npc_name, quest.id)
        
        return main_quests
    
    async def _create_main_quest(self, npc_data: Dict[str, Any], theme: str, quest_number: int, buildings: List[Dict]) -> Optional[QuestDefinition]:
        """Create a main quest for specific NPC"""
        
        npc_name = npc_data['character']['name']
        npc_role = npc_data['role']
        potential_themes = npc_data['quest_potential'].get('quest_themes', [])
        
        if AI_AVAILABLE and hasattr(self, 'gemini_model'):
            quest_data = await self._generate_ai_main_quest(npc_data, theme, quest_number)
            if quest_data:
                return self._build_quest_from_ai_data(quest_data, npc_name, 'main')
        
        # Fallback main quest generation
        return self._create_fallback_main_quest(npc_data, theme, quest_number, buildings)
    
    async def _generate_ai_main_quest(self, npc_data: Dict[str, Any], theme: str, quest_number: int) -> Optional[Dict[str, Any]]:
        """Generate main quest using AI"""
        
        npc = npc_data['character']
        conflicts = npc_data['relationship_conflicts']
        
        main_quest_prompt = f"""Create a main quest for a {theme} game:
        
        Quest Giver: {npc['name']}
        Role: {npc['role']}
        Personality: {npc['personality']['primary_trait']}, {npc['personality']['secondary_trait']}
        Motivation: {npc['personality']['motivation']}
        Secret: {npc['personality']['secret']}
        
        Relationship Conflicts: {conflicts if conflicts else 'None'}
        
        This is main quest #{quest_number}, so make it significant to the story.
        
        Create:
        1. Quest title (epic and memorable)
        2. Quest description (the problem/situation)
        3. Summary (brief overview)
        4. 3-5 objectives (variety of tasks)
        5. Rewards (appropriate to difficulty)
        6. Estimated duration
        
        Make it:
        - Narratively important
        - Use the NPC's personality and conflicts
        - Appropriate for {theme} setting
        - Engaging and memorable
        
        Format as:
        TITLE: [quest title]
        DESCRIPTION: [detailed description]
        SUMMARY: [brief summary]
        OBJECTIVES: [objective 1] | [objective 2] | [objective 3]
        REWARDS: [experience] XP, [gold] gold, [items]
        DURATION: [time estimate]"""
        
        try:
            response = await self._call_gemini(main_quest_prompt)
            if response:
                return self._parse_quest_response(response)
        except Exception as e:
            self.logger.warning(f"AI main quest generation failed: {e}")
        
        return None
    
    def _create_fallback_main_quest(self, npc_data: Dict[str, Any], theme: str, quest_number: int, buildings: List[Dict]) -> QuestDefinition:
        """Create fallback main quest without AI"""
        
        npc_name = npc_data['character']['name']
        npc_role = npc_data['role']
        
        # Template main quests by theme
        main_quest_templates = {
            'medieval': [
                {
                    'title': 'The Village Crisis',
                    'description': f'{npc_name} needs help resolving a crisis that threatens the village.',
                    'objectives': ['Investigate the problem', 'Gather information from villagers', 'Find a solution', 'Report back']
                },
                {
                    'title': 'Ancient Secrets',
                    'description': f'{npc_name} has discovered something that could change everything.',
                    'objectives': ['Learn about the discovery', 'Search for more clues', 'Uncover the truth', 'Decide what to do']
                }
            ]
        }
        
        templates = main_quest_templates.get(theme, main_quest_templates['medieval'])
        template = templates[quest_number - 1] if quest_number <= len(templates) else templates[0]
        
        # Create objectives
        objectives = []
        for i, obj_desc in enumerate(template['objectives']):
            objectives.append(QuestObjective(
                id=f"main_quest_{quest_number}_obj_{i+1}",
                description=obj_desc,
                type='talk_to_npc' if 'talk' in obj_desc.lower() else 'investigate',
                target=npc_name if 'back' in obj_desc.lower() else 'location',
                quantity=1
            ))
        
        # Create rewards
        base_exp = 100 * quest_number
        base_gold = 50 * quest_number
        
        rewards = QuestReward(
            experience=base_exp,
            gold=base_gold,
            items=[f'Quest Item {quest_number}'] if quest_number == 1 else []
        )
        
        return QuestDefinition(
            id=f"main_quest_{quest_number}_{npc_name.lower().replace(' ', '_')}",
            title=template['title'],
            description=template['description'],
            summary=f"Help {npc_name} with {template['title'].lower()}",
            giver_npc=npc_name,
            objectives=objectives,
            rewards=rewards,
            level_requirement=quest_number,
            quest_type='main',
            narrative_importance='high'
        )
    
    async def _generate_side_quests(self, npc_analysis: Dict[str, Any], theme: str, count: int) -> List[QuestDefinition]:
        """Generate side quests for various NPCs"""
        
        side_quests = []
        available_npcs = list(npc_analysis.keys())
        
        for i in range(min(count, len(available_npcs))):
            npc_name = available_npcs[i]
            npc_data = npc_analysis[npc_name]
            
            quest = await self._create_side_quest(npc_data, theme, i + 1)
            if quest:
                side_quests.append(quest)
                self._track_npc_involvement(npc_name, quest.id)
        
        return side_quests
    
    async def _create_side_quest(self, npc_data: Dict[str, Any], theme: str, quest_number: int) -> Optional[QuestDefinition]:
        """Create a side quest for specific NPC"""
        
        npc_name = npc_data['character']['name']
        quest_types = npc_data['quest_potential'].get('suitable_quest_types', ['fetch'])
        
        if AI_AVAILABLE and hasattr(self, 'gemini_model'):
            quest_data = await self._generate_ai_side_quest(npc_data, theme)
            if quest_data:
                return self._build_quest_from_ai_data(quest_data, npc_name, 'side')
        
        # Fallback side quest
        return self._create_fallback_side_quest(npc_data, theme, quest_number)
    
    async def _generate_ai_side_quest(self, npc_data: Dict[str, Any], theme: str) -> Optional[Dict[str, Any]]:
        """Generate side quest using AI"""
        
        npc = npc_data['character']
        quest_types = npc_data['quest_potential'].get('suitable_quest_types', [])
        
        side_quest_prompt = f"""Create a side quest for a {theme} game:
        
        Quest Giver: {npc['name']}
        Role: {npc['role']}
        Personality: {npc['personality']['primary_trait']}
        Suitable Quest Types: {', '.join(quest_types)}
        
        Create a side quest that:
        - Fits their role and personality
        - Is interesting but not world-changing
        - Takes 10-20 minutes to complete
        - Uses their skills/profession
        - Has a personal motivation
        
        Format as:
        TITLE: [quest title]
        DESCRIPTION: [description]
        SUMMARY: [brief summary]
        OBJECTIVES: [objective 1] | [objective 2] | [objective 3]
        REWARDS: [experience] XP, [gold] gold, [items]
        DURATION: [time estimate]"""
        
        try:
            response = await self._call_gemini(side_quest_prompt)
            if response:
                return self._parse_quest_response(response)
        except Exception as e:
            self.logger.warning(f"AI side quest generation failed: {e}")
        
        return None
    
    def _create_fallback_side_quest(self, npc_data: Dict[str, Any], theme: str, quest_number: int) -> QuestDefinition:
        """Create fallback side quest without AI"""
        
        npc_name = npc_data['character']['name']
        npc_role = npc_data['role']
        
        # Role-based side quest templates
        role_quests = {
            'merchant': {
                'title': 'Supply Run',
                'description': f'{npc_name} needs help gathering supplies for their business.',
                'objectives': ['Collect 5 trade goods', 'Return to merchant']
            },
            'farmer': {
                'title': 'Crop Protection',
                'description': f'{npc_name} needs help protecting their crops from pests.',
                'objectives': ['Patrol the fields', 'Deal with threats', 'Report back']
            },
            'guard': {
                'title': 'Security Patrol',
                'description': f'{npc_name} needs assistance with a security patrol.',
                'objectives': ['Join the patrol', 'Check key locations', 'File report']
            }
        }
        
        template = role_quests.get(npc_role, {
            'title': 'Personal Favor',
            'description': f'{npc_name} needs help with a personal matter.',
            'objectives': ['Listen to the problem', 'Help solve it', 'Return for thanks']
        })
        
        # Create objectives
        objectives = []
        for i, obj_desc in enumerate(template['objectives']):
            objectives.append(QuestObjective(
                id=f"side_quest_{quest_number}_obj_{i+1}",
                description=obj_desc,
                type='collect_item' if 'collect' in obj_desc.lower() else 'talk_to_npc',
                target='items' if 'collect' in obj_desc.lower() else npc_name,
                quantity=5 if 'collect' in obj_desc.lower() and '5' in obj_desc else 1
            ))
        
        rewards = QuestReward(
            experience=50,
            gold=25,
            items=['Thank You Gift'] if 'favor' in template['title'].lower() else []
        )
        
        return QuestDefinition(
            id=f"side_quest_{quest_number}_{npc_name.lower().replace(' ', '_')}",
            title=template['title'],
            description=template['description'],
            summary=f"Help {npc_name} with {template['title'].lower()}",
            giver_npc=npc_name,
            objectives=objectives,
            rewards=rewards,
            level_requirement=1,
            quest_type='side',
            narrative_importance='low'
        )
    
    def _parse_quest_response(self, response: str) -> Dict[str, Any]:
        """Parse AI quest response"""
        quest_data = {}
        
        for line in response.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if key == 'TITLE':
                    quest_data['title'] = value
                elif key == 'DESCRIPTION':
                    quest_data['description'] = value
                elif key == 'SUMMARY':
                    quest_data['summary'] = value
                elif key == 'OBJECTIVES':
                    quest_data['objectives'] = [obj.strip() for obj in value.split('|')]
                elif key == 'REWARDS':
                    quest_data['rewards'] = value
                elif key == 'DURATION':
                    quest_data['duration'] = value
        
        return quest_data
    
    def _build_quest_from_ai_data(self, quest_data: Dict[str, Any], npc_name: str, quest_type: str) -> QuestDefinition:
        """Build QuestDefinition from AI-generated data"""
        
        # Parse objectives
        objectives = []
        for i, obj_desc in enumerate(quest_data.get('objectives', [])):
            objectives.append(QuestObjective(
                id=f"{quest_type}_quest_obj_{i+1}",
                description=obj_desc,
                type=self._determine_objective_type(obj_desc),
                target=self._determine_objective_target(obj_desc, npc_name),
                quantity=self._extract_quantity(obj_desc)
            ))
        
        # Parse rewards
        rewards = self._parse_rewards(quest_data.get('rewards', '50 XP, 25 gold'))
        
        quest_id = f"{quest_type}_quest_{npc_name.lower().replace(' ', '_')}_{len(self.generated_quests)}"
        
        return QuestDefinition(
            id=quest_id,
            title=quest_data.get('title', f'Quest for {npc_name}'),
            description=quest_data.get('description', f'Help {npc_name} with their request.'),
            summary=quest_data.get('summary', f'Assist {npc_name}'),
            giver_npc=npc_name,
            objectives=objectives,
            rewards=rewards,
            level_requirement=1 if quest_type == 'side' else 2,
            estimated_duration=quest_data.get('duration', '15-20 minutes'),
            quest_type=quest_type,
            narrative_importance='high' if quest_type == 'main' else 'medium'
        )
    
    def _determine_objective_type(self, description: str) -> str:
        """Determine objective type from description"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['talk', 'speak', 'ask', 'tell']):
            return 'talk_to_npc'
        elif any(word in desc_lower for word in ['collect', 'gather', 'find', 'get']):
            return 'collect_item'
        elif any(word in desc_lower for word in ['go', 'travel', 'visit', 'reach']):
            return 'go_to_location'
        elif any(word in desc_lower for word in ['defeat', 'kill', 'fight', 'battle']):
            return 'defeat_enemy'
        elif any(word in desc_lower for word in ['investigate', 'search', 'examine']):
            return 'investigate'
        else:
            return 'talk_to_npc'
    
    def _determine_objective_target(self, description: str, npc_name: str) -> str:
        """Determine objective target from description"""
        desc_lower = description.lower()
        
        if 'back' in desc_lower or 'report' in desc_lower:
            return npc_name
        elif any(word in desc_lower for word in ['item', 'supply', 'resource']):
            return 'items'
        elif any(word in desc_lower for word in ['location', 'place', 'area']):
            return 'location'
        else:
            return 'target'
    
    def _extract_quantity(self, description: str) -> int:
        """Extract quantity from objective description"""
        import re
        numbers = re.findall(r'\d+', description)
        return int(numbers[0]) if numbers else 1
    
    def _parse_rewards(self, reward_text: str) -> QuestReward:
        """Parse reward text into QuestReward object"""
        experience = 50
        gold = 25
        items = []
        
        try:
            # Extract numbers and keywords
            import re
            
            # Find XP/experience
            exp_match = re.search(r'(\d+)\s*(?:XP|experience|exp)', reward_text, re.IGNORECASE)
            if exp_match:
                experience = int(exp_match.group(1))
            
            # Find gold
            gold_match = re.search(r'(\d+)\s*gold', reward_text, re.IGNORECASE)
            if gold_match:
                gold = int(gold_match.group(1))
            
            # Find items (simple extraction)
            if 'item' in reward_text.lower():
                items = ['Quest Reward Item']
        
        except Exception:
            pass  # Use defaults
        
        return QuestReward(
            experience=experience,
            gold=gold,
            items=items if items else None
        )
    
    async def _create_quest_interconnections(self, quests: List[QuestDefinition], npc_analysis: Dict[str, Any]) -> List[QuestDefinition]:
        """Create interconnections between quests"""
        
        print(f"   🔗 Creating connections between {len(quests)} quests...")
        
        for i, quest in enumerate(quests):
            # Find quests that could be connected
            connected_quests = []
            
            # Connect based on NPC relationships
            giver_npc = quest.giver_npc
            if giver_npc in npc_analysis:
                relationships = npc_analysis[giver_npc]['relationships']
                
                for relationship in relationships:
                    related_npc = relationship.get('target_character')
                    
                    # Find quests from related NPCs
                    related_quests = [
                        q.id for q in quests 
                        if q.giver_npc == related_npc and q.id != quest.id
                    ]
                    connected_quests.extend(related_quests[:2])  # Limit connections
            
            # Connect main quests in sequence
            if quest.quest_type == 'main' and i > 0:
                prev_main_quest = next((q for q in quests[:i] if q.quest_type == 'main'), None)
                if prev_main_quest:
                    quest.prerequisites = [prev_main_quest.id]
            
            quest.interconnected_quests = connected_quests[:3]  # Max 3 connections
        
        return quests
    
    async def _generate_quest_dialogues(self, quests: List[QuestDefinition], npc_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dialogue trees for quest interactions"""
        
        print(f"   💬 Generating dialogue for {len(quests)} quests...")
        
        quest_dialogues = {}
        
        for quest in quests:
            giver_npc = quest.giver_npc
            
            if giver_npc in npc_analysis:
                npc_data = npc_analysis[giver_npc]
                dialogue = await self._create_quest_dialogue(quest, npc_data)
                quest_dialogues[quest.id] = dialogue
        
        return quest_dialogues
    
    async def _create_quest_dialogue(self, quest: QuestDefinition, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create dialogue tree for a specific quest"""
        
        npc_name = npc_data['character']['name']
        personality = npc_data['character']['personality']
        
        if AI_AVAILABLE and hasattr(self, 'gemini_model'):
            ai_dialogue = await self._generate_ai_quest_dialogue(quest, npc_data)
            if ai_dialogue:
                return ai_dialogue
        
        # Fallback dialogue
        return self._create_fallback_quest_dialogue(quest, npc_data)
    
    async def _generate_ai_quest_dialogue(self, quest: QuestDefinition, npc_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate quest dialogue using AI"""
        
        npc = npc_data['character']
        
        dialogue_prompt = f"""Create quest dialogue for:
        
        Quest: {quest.title}
        Description: {quest.description}
        NPC: {npc['name']} ({npc['role']})
        Personality: {npc['personality']['primary_trait']}, {npc['personality']['secondary_trait']}
        Speech Pattern: {npc['personality'].get('speech_pattern', 'normal')}
        
        Create dialogue for:
        1. Quest Introduction (when player first talks to NPC)
        2. Quest Acceptance (when player agrees to help)
        3. Quest Progress (checking on progress)
        4. Quest Completion (when objectives are done)
        5. Quest Reward (giving rewards)
        
        Make the dialogue:
        - Match the NPC's personality and speech pattern
        - Explain the quest clearly
        - Be engaging and natural
        - Include player response options
        
        Format as:
        INTRODUCTION: [NPC introduces the problem/quest]
        ACCEPTANCE: [NPC responds when player accepts]
        PROGRESS: [NPC checks on quest progress]
        COMPLETION: [NPC responds when quest is done]
        REWARD: [NPC gives rewards and thanks]"""
        
        try:
            response = await self._call_gemini(dialogue_prompt)
            if response:
                return self._parse_dialogue_response(response, quest.id, npc['name'])
        except Exception as e:
            self.logger.warning(f"AI dialogue generation failed: {e}")
        
        return None
    
    def _create_fallback_quest_dialogue(self, quest: QuestDefinition, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback quest dialogue"""
        
        npc_name = npc_data['character']['name']
        
        return {
            'quest_id': quest.id,
            'npc_name': npc_name,
            'dialogue_nodes': {
                'introduction': {
                    'text': f"I have a problem that needs solving. {quest.description}",
                    'options': [
                        {'text': "I'll help you.", 'next': 'acceptance'},
                        {'text': "Tell me more.", 'next': 'details'},
                        {'text': "I'm not interested.", 'next': 'decline'}
                    ]
                },
                'acceptance': {
                    'text': "Thank you! I knew I could count on you.",
                    'options': [
                        {'text': "What exactly do I need to do?", 'next': 'objectives'},
                        {'text': "I'll get started right away.", 'next': 'farewell'}
                    ]
                },
                'completion': {
                    'text': f"Excellent work! Here's your reward: {quest.rewards.experience} XP and {quest.rewards.gold} gold.",
                    'options': [
                        {'text': "Thank you.", 'next': 'farewell'},
                        {'text': "Happy to help.", 'next': 'farewell'}
                    ]
                }
            }
        }
    
    def _parse_dialogue_response(self, response: str, quest_id: str, npc_name: str) -> Dict[str, Any]:
        """Parse AI dialogue response"""
        
        dialogue_data = {
            'quest_id': quest_id,
            'npc_name': npc_name,
            'dialogue_nodes': {}
        }
        
        current_section = None
        
        for line in response.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().upper()
                value = value.strip()
                
                if key in ['INTRODUCTION', 'ACCEPTANCE', 'PROGRESS', 'COMPLETION', 'REWARD']:
                    current_section = key.lower()
                    dialogue_data['dialogue_nodes'][current_section] = {
                        'text': value,
                        'options': [
                            {'text': "Continue", 'next': 'next_node'},
                            {'text': "I understand", 'next': 'farewell'}
                        ]
                    }
        
        return dialogue_data
    
    def _track_npc_involvement(self, npc_name: str, quest_id: str):
        """Track which NPCs are involved in which quests"""
        if npc_name not in self.npc_quest_involvement:
            self.npc_quest_involvement[npc_name] = []
        self.npc_quest_involvement[npc_name].append(quest_id)
    
    def _calculate_total_playtime(self, quests: List[QuestDefinition]) -> str:
        """Calculate estimated total playtime"""
        total_minutes = 0
        
        for quest in quests:
            # Extract minutes from duration string
            duration = quest.estimated_duration
            if 'minute' in duration:
                import re
                numbers = re.findall(r'\d+', duration)
                if numbers:
                    # Take average of range or single number
                    if len(numbers) >= 2:
                        total_minutes += (int(numbers[0]) + int(numbers[1])) // 2
                    else:
                        total_minutes += int(numbers[0])
            else:
                total_minutes += 15  # Default estimate
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        if hours > 0:
            return f"{hours} hours {minutes} minutes"
        else:
            return f"{minutes} minutes"
    
    async def _save_quest_system(self, quests: List[QuestDefinition], quest_dialogues: Dict[str, Any], 
                                theme: str, world_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Save complete quest system"""
        
        from datetime import datetime
        
        # Save individual quest files
        for quest in quests:
            quest_file = self.quests_dir / f"{quest.id}.json"
            with open(quest_file, 'w') as f:
                json.dump(asdict(quest), f, indent=2)
        
        # Save quest dialogues
        dialogues_file = self.dialogue_dir / "quest_dialogues.json"
        with open(dialogues_file, 'w') as f:
            json.dump(quest_dialogues, f, indent=2)
        
        # Create quest chains mapping
        quest_chains = {}
        for quest in quests:
            if quest.quest_type == 'main':
                chain_name = f"main_chain_{quest.id}"
                quest_chains[chain_name] = {
                    'type': 'main',
                    'quests': [quest.id],
                    'connected_quests': quest.interconnected_quests or []
                }
        
        chains_file = self.chains_dir / "quest_chains.json"
        with open(chains_file, 'w') as f:
            json.dump(quest_chains, f, indent=2)
        
        # Create master quest manifest
        manifest = {
            'generation_info': {
                'timestamp': datetime.now().isoformat(),
                'theme': theme,
                'world_size': world_spec.get('size', (0, 0)),
                'quest_count': len(quests),
                'ai_enhanced': AI_AVAILABLE and hasattr(self, 'gemini_model')
            },
            'quest_summary': {
                'total_quests': len(quests),
                'main_quests': len([q for q in quests if q.quest_type == 'main']),
                'side_quests': len([q for q in quests if q.quest_type == 'side']),
                'chain_quests': len([q for q in quests if q.quest_type == 'chain']),
                'interconnected_count': sum(1 for q in quests if q.interconnected_quests),
                'total_objectives': sum(len(q.objectives) for q in quests),
                'estimated_playtime': self._calculate_total_playtime(quests)
            },
            'npc_involvement': self.npc_quest_involvement,
            'quests': {
                quest.id: {
                    'title': quest.title,
                    'giver_npc': quest.giver_npc,
                    'type': quest.quest_type,
                    'level_requirement': quest.level_requirement,
                    'objectives_count': len(quest.objectives),
                    'rewards': {
                        'experience': quest.rewards.experience,
                        'gold': quest.rewards.gold,
                        'items': quest.rewards.items or []
                    },
                    'estimated_duration': quest.estimated_duration,
                    'narrative_importance': quest.narrative_importance,
                    'quest_file': f"quest_definitions/{quest.id}.json"
                }
                for quest in quests
            },
            'integration_info': {
                'unity_compatible': True,
                'dialogue_system_ready': True,
                'objective_tracking_ready': True,
                'reward_system_ready': True,
                'character_integration': True
            }
        }
        
        # Save manifest
        manifest_file = self.output_dir / "quest_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest
    
    async def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini AI for quest generation"""
        if not AI_AVAILABLE or not hasattr(self, 'gemini_model'):
            return None
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.warning(f"Gemini API call failed: {e}")
            return None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get quest writer status"""
        return {
            'status': 'ready',
            'ai_available': AI_AVAILABLE and hasattr(self, 'gemini_model'),
            'output_directory': str(self.output_dir),
            'generated_quests': len(self.generated_quests),
            'npc_involvement': len(self.npc_quest_involvement),
            'capabilities': [
                'main_quest_generation',
                'side_quest_creation',
                'quest_interconnection',
                'dialogue_generation',
                'objective_tracking',
                'reward_balancing',
                'npc_integration'
            ],
            'ai_features': {
                'quest_narrative_generation': AI_AVAILABLE and hasattr(self, 'gemini_model'),
                'dialogue_creation': AI_AVAILABLE and hasattr(self, 'gemini_model'),
                'objective_planning': AI_AVAILABLE and hasattr(self, 'gemini_model'),
                'reward_calculation': True
            }
        }

# ADK Agent Functions
async def generate_quest_system(world_spec: Dict[str, Any], characters: List[Dict[str, Any]], quest_count: int = 5) -> Dict[str, Any]:
    """Generate complete quest system - main entry point"""
    quest_writer = AIQuestWriter()
    return await quest_writer.generate_quest_system(world_spec, characters, quest_count)

async def get_quest_writer_status() -> Dict[str, Any]:
    """Get quest writer status"""
    quest_writer = AIQuestWriter()
    return await quest_writer.get_status()

# Create the ADK agent
root_agent = Agent(
    name="quest_writer_agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are an AI-powered Quest Writer Agent that creates engaging, interconnected storylines for game worlds using existing NPCs and world data.

Your advanced capabilities include:
- NARRATIVE INTEGRATION: Creates quests that utilize existing NPCs, their personalities, and relationships
- QUEST INTERCONNECTION: Builds meaningful connections between quests for narrative flow
- ADAPTIVE STORYTELLING: Generates quests that match the world theme and character motivations  
- DIALOGUE GENERATION: Creates natural conversations that reflect NPC personalities
- OBJECTIVE BALANCING: Ensures quest objectives are varied, interesting, and appropriately challenging
- REWARD SYSTEMS: Calculates balanced rewards based on quest difficulty and progression

Your quest system features:
📜 MAIN QUEST CHAINS: Epic storylines that drive the core narrative
🌟 SIDE QUESTS: Personal stories that flesh out individual NPCs
🔗 INTERCONNECTED NARRATIVES: Quests that reference and build upon each other
💬 CHARACTER-DRIVEN DIALOGUE: Conversations that match each NPC's unique personality
🎯 VARIED OBJECTIVES: Mix of investigation, collection, social, and exploration tasks
⚖️ BALANCED PROGRESSION: Appropriate difficulty curves and reward structures

Your quests are:
✨ Narratively Cohesive - All quests feel part of the same world
🎭 Character-Driven - NPCs have personal stakes and believable motivations  
🔄 Interconnected - Actions in one quest affect others
🎮 Gameplay-Focused - Objectives are fun and varied
📈 Progression-Aware - Difficulty and rewards scale appropriately

When you receive a quest generation request, you analyze the existing NPCs and their relationships to create a web of interconnected stories that bring the world to life.""",
    description="AI-powered Quest Writer Agent that creates interconnected storylines and quest systems using existing NPCs, their relationships, and world context",
    tools=[generate_quest_system, get_quest_writer_status]
)

# Standalone testing
if __name__ == "__main__":
    async def main():
        print("🗡️ Testing AI Quest Writer Agent")
        print("="*50)
        
        # Test world spec
        test_world = {
            "theme": "medieval",
            "size": (40, 40),
            "buildings": [
                {"type": "tavern", "position": {"x": 20, "y": 20, "z": 0}},
                {"type": "blacksmith", "position": {"x": 15, "y": 25, "z": 0}},
                {"type": "church", "position": {"x": 25, "y": 15, "z": 0}}
            ]
        }
        
        # Test characters (simplified)
        test_characters = [
            {
                "name": "Marcus the Blacksmith",
                "role": "blacksmith",
                "personality": {
                    "primary_trait": "dedicated",
                    "secondary_trait": "proud",
                    "motivation": "perfect craftsmanship",
                    "secret": "lost his masterwork hammer"
                },
                "relationships": [
                    {
                        "target_character": "Elena the Merchant",
                        "relationship_type": "business_partner",
                        "relationship_strength": 60,
                        "history": "They work together on trade deals"
                    }
                ]
            },
            {
                "name": "Elena the Merchant", 
                "role": "merchant",
                "personality": {
                    "primary_trait": "shrewd",
                    "secondary_trait": "ambitious", 
                    "motivation": "wealth and influence",
                    "secret": "knows about stolen goods"
                },
                "relationships": [
                    {
                        "target_character": "Marcus the Blacksmith",
                        "relationship_type": "business_partner", 
                        "relationship_strength": 55,
                        "history": "They work together but have some tension"
                    }
                ]
            }
        ]
        
        quest_writer = AIQuestWriter("test_quests")
        
        print("\n🧪 Testing Quest System Generation...")
        
        try:
            result = await quest_writer.generate_quest_system(test_world, test_characters, 3)
            
            if result['status'] == 'success':
                print(f"\n✅ Quest Generation Success!")
                summary = result['generation_summary']
                print(f"   📜 Total Quests: {summary['total_quests']}")
                print(f"   ⚔️ Main Quests: {summary['main_quests']}")
                print(f"   🌟 Side Quests: {summary['side_quests']}")
                print(f"   🔗 Interconnected: {summary['interconnected_count']}")
                print(f"   ⏱️ Estimated Playtime: {summary['estimated_playtime']}")
                
                print(f"\n📋 Generated Quests:")
                for quest_data in result['quests']:
                    print(f"   • {quest_data['title']}")
                    print(f"     Giver: {quest_data['giver_npc']}")
                    print(f"     Type: {quest_data['quest_type']}")
                    print(f"     Objectives: {len(quest_data['objectives'])}")
                    print()
                
                print(f"📁 Output: test_quests/")
                print("🚀 Quest system ready for integration!")
                
            else:
                print(f"❌ Quest Generation Failed!")
                
        except Exception as e:
            print(f"💥 Exception: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main())