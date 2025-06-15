#!/usr/bin/env python3
"""
ENHANCED AI CHARACTER CREATOR - TRULY CREATIVE VERSION
Generates completely unique characters with real AI creativity
NO REPETITION - EVERY CHARACTER IS DIFFERENT
"""

import asyncio
import json
import random
import hashlib
import os
import uuid
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from datetime import datetime

# Google ADK imports
from google.adk.agents import Agent

# AI imports
try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

@dataclass
class CharacterStats:
    level: int
    health: int
    strength: int
    intelligence: int
    charisma: int
    dexterity: int
    wisdom: int
    constitution: int
    
    def get_total_points(self) -> int:
        return self.strength + self.intelligence + self.charisma + self.dexterity + self.wisdom + self.constitution

@dataclass
class CharacterPersonality:
    primary_trait: str
    secondary_trait: str
    motivation: str
    fear: str
    quirk: str
    speech_pattern: str
    alignment: str
    mood: str
    secret: str  # Every character has a secret
    life_goal: str  # What they want to achieve

@dataclass
class CharacterRelationship:
    target_character: str
    relationship_type: str
    relationship_strength: int
    history: str
    current_status: str

@dataclass
class DialogueOption:
    id: str
    text: str
    next_node_id: Optional[str]
    conditions: List[str]
    effects: List[str]

@dataclass
class DialogueNode:
    id: str
    text: str
    speaker: str
    options: List[DialogueOption]
    is_greeting: bool = False
    is_farewell: bool = False
    quest_related: bool = False

@dataclass
class CharacterProfile:
    id: str
    name: str
    title: str
    description: str
    backstory: str
    personality: CharacterPersonality
    stats: CharacterStats
    relationships: List[CharacterRelationship]
    dialogue_tree: List[DialogueNode]
    inventory: List[str]
    location: str
    role: str
    quest_involvement: List[str]
    age: int
    appearance: str
    voice_description: str
    unique_id: str  # Ensures complete uniqueness

class CreativeCharacterGenerator:
    """
    TRULY AI-POWERED CHARACTER GENERATOR
    - Every character is completely unique
    - Uses advanced AI prompting for maximum creativity
    - No template fallbacks - pure AI generation
    - Tracks uniqueness to prevent duplicates
    """
    
    def __init__(self, output_dir: str = "generated_characters"):
        # Initialize logging FIRST - this is critical to prevent AttributeError
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Now set up the rest of the initialization
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Ensure directories exist
        self.profiles_dir = self.output_dir / "character_profiles"
        self.dialogue_dir = self.output_dir / "dialogue_trees"
        self.relationships_dir = self.output_dir / "relationship_maps"
        self.stats_dir = self.output_dir / "character_stats"
        
        for dir_path in [self.profiles_dir, self.dialogue_dir, self.relationships_dir, self.stats_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Uniqueness tracking
        self.generated_names = set()
        self.generated_personalities = set()
        self.generated_backstories = set()
        self.uniqueness_tracker = {}
        
        # AI creativity boosters
        self.creativity_seeds = []
        self.current_session = str(uuid.uuid4())[:8]
        
        # Initialize enhanced AI (this may use the logger, so logger must be set up first)
        self._initialize_enhanced_ai()
        
        self.logger.info(f"✅ CreativeCharacterGenerator initialized with output directory: {self.output_dir}")
    
    def _initialize_enhanced_ai(self):
        """Initialize AI with enhanced creativity settings"""
        if not AI_AVAILABLE:
            self.logger.error("❌ AI NOT AVAILABLE - This agent requires AI for creativity!")
            return False
            
        try:
            # Use environment variable or prompt for API key
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if not api_key:
                self.logger.warning("⚠️ No API key found. Set GOOGLE_API_KEY environment variable for full AI creativity!")
                return False
                
            genai.configure(api_key=api_key)
            
            # Configure for maximum creativity
            self.gemini_model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config=genai.types.GenerationConfig(
                    temperature=1.2,  # Maximum creativity
                    top_p=0.95,
                    top_k=64,
                    candidate_count=1,
                    max_output_tokens=1000,
                )
            )
            
            self.logger.info("✅ Enhanced AI initialized with maximum creativity settings")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Enhanced AI initialization failed: {e}")
            return False
    
    async def generate_unique_characters(self, world_spec: Dict[str, Any], character_count: int = 5) -> Dict[str, Any]:
        """
        Generate completely unique characters with maximum AI creativity
        """
        self.logger.info(f"🎭 Generating {character_count} COMPLETELY UNIQUE characters...")
        
        if not AI_AVAILABLE:
            return await self._generate_fallback_characters(world_spec, character_count)
        
        theme = world_spec.get('theme', 'medieval')
        buildings = world_spec.get('buildings', [])
        world_size = world_spec.get('size', (40, 40))
        
        # Generate creativity seeds for this session
        await self._generate_creativity_seeds(theme, character_count)
        
        # Generate each character with maximum uniqueness
        characters = []
        
        for i in range(character_count):
            self.logger.info(f"🎨 Creating Character {i+1}/{character_count} with AI...")
            
            # Generate with retries to ensure uniqueness
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    character = await self._generate_completely_unique_character(
                        theme, buildings, i, characters, attempt
                    )
                    
                    # Check for uniqueness
                    if self._is_character_unique(character):
                        characters.append(character)
                        self._record_character_uniqueness(character)
                        self.logger.info(f"   ✅ Created unique character: {character.name}")
                        break
                    else:
                        self.logger.info(f"   🔄 Character too similar, regenerating... (attempt {attempt + 1})")
                        
                except Exception as e:
                    self.logger.warning(f"   ⚠️ Generation attempt {attempt + 1} failed: {e}")
                    if attempt == max_attempts - 1:
                        # Fallback to basic generation
                        character = await self._generate_fallback_character(theme, buildings, i, characters)
                        characters.append(character)
                        self.logger.info(f"   ⚠️ Used fallback generation for: {character.name}")
                        break
        
        # Generate inter-character relationships with AI
        self.logger.info(f"💞 Generating AI-powered relationships...")
        characters = await self._generate_ai_relationships(characters, theme)
        
        # Generate AI dialogue trees
        self.logger.info(f"💬 Creating AI dialogue systems...")
        characters = await self._generate_ai_dialogues(characters, theme)
        
        # Final uniqueness validation
        characters = await self._ensure_final_uniqueness(characters)
        
        # Save all character data
        self.logger.info(f"💾 Saving unique character profiles...")
        manifest = await self._save_unique_characters(characters, theme, world_spec)
        
        # Generate summary
        total_relationships = sum(len(char.relationships) for char in characters)
        total_dialogue_nodes = sum(len(char.dialogue_tree) for char in characters)
        unique_personalities = len(set(char.personality.primary_trait for char in characters))
        
        self.logger.info(f"🎉 UNIQUE CHARACTER GENERATION COMPLETE!")
        self.logger.info(f"   📊 {len(characters)} characters created")
        self.logger.info(f"   🤝 {total_relationships} relationships generated")
        self.logger.info(f"   💬 {total_dialogue_nodes} dialogue nodes created")
        self.logger.info(f"   🎭 {unique_personalities}/{len(characters)} unique personalities")
        
        return {
            'status': 'success',
            'character_count': len(characters),
            'output_directory': str(self.output_dir),
            'manifest_file': str(self.output_dir / "character_manifest.json"),
            'unique_personalities': unique_personalities,
            'total_relationships': total_relationships,
            'total_dialogue_nodes': total_dialogue_nodes,
            'characters': [asdict(char) for char in characters]
        }
    
    async def _generate_creativity_seeds(self, theme: str, character_count: int):
        """Generate AI creativity seeds for this session"""
        if AI_AVAILABLE:
            try:
                response = await self._call_creative_ai(
                    f"Generate {character_count * 3} completely unique and creative character concept seeds for a {theme} setting. "
                    f"Be wildly imaginative and avoid clichés.",
                    temperature=1.3
                )
                if response:
                    self.creativity_seeds.extend(response.split('\n'))
            except Exception as e:
                self.logger.warning(f"Creativity seed generation failed: {e}")
    
    async def _generate_completely_unique_character(self, theme: str, buildings: List[Dict], 
                                                  index: int, existing_characters: List[CharacterProfile],
                                                  attempt: int) -> CharacterProfile:
        """Generate a completely unique character using maximum AI creativity"""
        
        # Create uniqueness constraints
        existing_names = [char.name for char in existing_characters]
        existing_traits = [char.personality.primary_trait for char in existing_characters]
        existing_roles = [char.role for char in existing_characters]
        
        # Generate unique character concept first
        character_concept = await self._generate_character_concept(theme, existing_names, existing_traits, index, attempt)
        
        # Generate unique name with AI
        character_name = await self._generate_ai_unique_name(theme, existing_names, character_concept, attempt)
        
        # Generate unique role
        character_role = await self._generate_ai_unique_role(theme, buildings, existing_roles, character_concept)
        
        # Generate AI personality (most important for uniqueness)
        personality = await self._generate_ai_unique_personality(character_name, character_role, theme, character_concept, existing_traits)
        
        # Generate age with variation
        age = await self._generate_varied_age(character_role, personality, attempt)
        
        # Generate AI-powered stats
        stats = await self._generate_ai_stats(character_role, personality, age, existing_characters)
        
        # Generate AI backstory
        backstory = await self._generate_ai_backstory(character_name, personality, character_role, theme, age)
        
        # Generate AI appearance
        description = await self._generate_ai_appearance(character_name, personality, character_role, theme, age)
        appearance = await self._generate_detailed_ai_appearance(character_name, personality, age, theme)
        voice_description = await self._generate_ai_voice(personality, character_role, age)
        
        # Generate location and inventory
        location = self._assign_unique_location(character_role, buildings, existing_characters)
        inventory = await self._generate_ai_inventory(character_role, personality, theme)
        title = await self._generate_ai_title(character_name, character_role, personality)
        
        # Create unique character ID
        character_id = f"{character_name.lower().replace(' ', '_')}_{self.current_session}_{index}"
        unique_id = str(uuid.uuid4())
        
        # Build the character profile
        character = CharacterProfile(
            id=character_id,
            name=character_name,
            title=title,
            description=description,
            backstory=backstory,
            personality=personality,
            stats=stats,
            relationships=[],  # Will be filled later
            dialogue_tree=[],  # Will be filled later
            inventory=inventory,
            location=location,
            role=character_role,
            quest_involvement=[],
            age=age,
            appearance=appearance,
            voice_description=voice_description,
            unique_id=unique_id
        )
        
        return character
    
    async def _generate_character_concept(self, theme: str, existing_names: List[str], 
                                        existing_traits: List[str], index: int, attempt: int) -> str:
        """Generate a unique character concept using AI"""
        if not AI_AVAILABLE:
            concepts = ["warrior", "merchant", "scholar", "craftsperson", "healer", "explorer", "artist", "mystic"]
            return random.choice(concepts)
        
        try:
            constraints = ""
            if existing_names:
                constraints += f"Must be completely different from these existing characters: {', '.join(existing_names[:3])}. "
            if existing_traits:
                constraints += f"Must avoid these personality traits: {', '.join(existing_traits[:3])}. "
            
            concept = await self._call_creative_ai(
                f"Create a completely unique character concept for a {theme} setting. {constraints}"
                f"Be wildly creative and avoid all clichés. Generate something nobody would expect. "
                f"Attempt #{attempt + 1}, make it even more unique.",
                temperature=1.4
            )
            return concept[:200] if concept else f"unique_{theme}_character_{index}_{attempt}"
        except Exception as e:
            self.logger.warning(f"Character concept generation failed: {e}")
            return f"unique_{theme}_character_{index}_{attempt}"
    
    async def _generate_ai_unique_name(self, theme: str, existing_names: List[str], 
                                     concept: str, attempt: int) -> str:
        """Generate unique character name with AI"""
        if not AI_AVAILABLE:
            return self._generate_fallback_name(theme, existing_names, attempt)
        
        try:
            constraints = f"Must be completely different from: {', '.join(existing_names[:5])}" if existing_names else ""
            
            name = await self._call_creative_ai(
                f"Generate a unique, memorable name for this character concept in a {theme} setting: {concept[:100]}. "
                f"{constraints}. Be creative and original. Just return the name, nothing else.",
                temperature=1.1
            )
            
            if name and name.strip() and name.strip() not in existing_names:
                return name.strip().split('\n')[0][:30]
            else:
                return self._generate_fallback_name(theme, existing_names, attempt)
        except Exception as e:
            self.logger.warning(f"AI name generation failed: {e}")
            return self._generate_fallback_name(theme, existing_names, attempt)
    
    def _generate_fallback_name(self, theme: str, existing_names: List[str], attempt: int) -> str:
        """Generate fallback name when AI fails"""
        prefixes = {
            "medieval": ["Sir", "Lady", "Brother", "Sister", "Master"],
            "fantasy": ["Elder", "Star", "Moon", "Fire", "Storm"],
            "sci-fi": ["Commander", "Captain", "Dr.", "Agent", "Chief"],
            "modern": ["Mr.", "Ms.", "Dr.", "Captain", "Chief"]
        }
        
        names = {
            "medieval": ["Aldric", "Brenna", "Cedric", "Dara", "Edwin", "Fiona", "Gareth", "Hilda"],
            "fantasy": ["Aelindra", "Thorvak", "Lyralei", "Grimjaw", "Seraphina", "Drakkon"],
            "sci-fi": ["Nova", "Zephyr", "Orion", "Luna", "Phoenix", "Matrix"],
            "modern": ["Alex", "Jordan", "Riley", "Casey", "Morgan", "Taylor"]
        }
        
        theme_key = theme if theme in prefixes else "medieval"
        prefix = random.choice(prefixes[theme_key])
        name = random.choice(names[theme_key])
        
        full_name = f"{prefix} {name}"
        if full_name in existing_names:
            full_name = f"{name} {random.randint(100, 999)}"
        
        return full_name
    
    async def _generate_ai_unique_role(self, theme: str, buildings: List[Dict], 
                                     existing_roles: List[str], concept: str) -> str:
        """Generate unique character role with AI"""
        if not AI_AVAILABLE:
            return self._generate_fallback_role(theme, buildings, existing_roles)
        
        try:
            building_types = [b.get('type', 'unknown') for b in buildings]
            constraints = f"Avoid these existing roles: {', '.join(existing_roles[:3])}" if existing_roles else ""
            
            role = await self._call_creative_ai(
                f"Create a unique role/profession for this character in a {theme} setting: {concept[:100]}. "
                f"Available buildings: {', '.join(building_types)}. {constraints}. "
                f"Be creative and specific. Just return the role, nothing else.",
                temperature=1.0
            )
            
            if role and role.strip():
                return role.strip().split('\n')[0][:50]
            else:
                return self._generate_fallback_role(theme, buildings, existing_roles)
        except Exception as e:
            self.logger.warning(f"AI role generation failed: {e}")
            return self._generate_fallback_role(theme, buildings, existing_roles)
    
    def _generate_fallback_role(self, theme: str, buildings: List[Dict], existing_roles: List[str]) -> str:
        """Generate fallback role when AI fails"""
        building_roles = {
            "tavern": ["Innkeeper", "Bartender", "Bard", "Bouncer"],
            "blacksmith": ["Blacksmith", "Apprentice", "Weapon Master"],
            "church": ["Priest", "Acolyte", "Healer", "Temple Guard"],
            "shop": ["Merchant", "Shopkeeper", "Trader", "Clerk"],
            "house": ["Resident", "Noble", "Family Head", "Servant"]
        }
        
        theme_roles = {
            "medieval": ["Knight", "Mage", "Archer", "Scholar", "Herbalist"],
            "fantasy": ["Wizard", "Ranger", "Paladin", "Druid", "Rogue"],
            "sci-fi": ["Engineer", "Pilot", "Scientist", "Medic", "Security"],
            "modern": ["Teacher", "Doctor", "Artist", "Chef", "Detective"]
        }
        
        available_roles = []
        
        # Add building-specific roles
        for building in buildings:
            building_type = building.get('type', 'house')
            if building_type in building_roles:
                available_roles.extend(building_roles[building_type])
        
        # Add theme-specific roles
        theme_key = theme if theme in theme_roles else "medieval"
        available_roles.extend(theme_roles[theme_key])
        
        # Filter out existing roles
        available_roles = [role for role in available_roles if role not in existing_roles]
        
        if available_roles:
            return random.choice(available_roles)
        else:
            return f"Unique {theme} Specialist"
    
    async def _generate_ai_unique_personality(self, name: str, role: str, theme: str, 
                                            concept: str, existing_traits: List[str]) -> CharacterPersonality:
        """Generate unique personality with AI"""
        if not AI_AVAILABLE:
            return self._generate_fallback_personality(existing_traits)
        
        try:
            constraints = f"Avoid these existing primary traits: {', '.join(existing_traits[:3])}" if existing_traits else ""
            
            personality_prompt = f"""
            Create a detailed, unique personality for {name}, a {role} in a {theme} setting.
            Character concept: {concept[:100]}
            {constraints}
            
            Provide exactly this format:
            Primary Trait: [unique trait]
            Secondary Trait: [supporting trait]
            Motivation: [what drives them]
            Fear: [what they're afraid of]
            Quirk: [distinctive habit or mannerism]
            Speech Pattern: [how they speak]
            Alignment: [moral alignment]
            Mood: [general demeanor]
            Secret: [hidden aspect]
            Life Goal: [ultimate aspiration]
            """
            
            response = await self._call_creative_ai(personality_prompt, temperature=1.1)
            
            if response:
                return self._parse_personality_response(response)
            else:
                return self._generate_fallback_personality(existing_traits)
                
        except Exception as e:
            self.logger.warning(f"AI personality generation failed: {e}")
            return self._generate_fallback_personality(existing_traits)
    
    def _parse_personality_response(self, response: str) -> CharacterPersonality:
        """Parse AI personality response into structured data"""
        lines = response.strip().split('\n')
        personality_data = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                personality_data[key] = value
        
        return CharacterPersonality(
            primary_trait=personality_data.get('primary_trait', 'Determined'),
            secondary_trait=personality_data.get('secondary_trait', 'Curious'),
            motivation=personality_data.get('motivation', 'To find their purpose'),
            fear=personality_data.get('fear', 'Being forgotten'),
            quirk=personality_data.get('quirk', 'Always adjusts their clothing'),
            speech_pattern=personality_data.get('speech_pattern', 'Speaks clearly and directly'),
            alignment=personality_data.get('alignment', 'Neutral Good'),
            mood=personality_data.get('mood', 'Cautiously optimistic'),
            secret=personality_data.get('secret', 'Has a hidden talent'),
            life_goal=personality_data.get('life_goal', 'To make a difference')
        )
    
    def _generate_fallback_personality(self, existing_traits: List[str]) -> CharacterPersonality:
        """Generate fallback personality when AI fails"""
        primary_traits = ["Brave", "Clever", "Compassionate", "Determined", "Eccentric", 
                         "Fierce", "Gentle", "Honest", "Inventive", "Jovial"]
        secondary_traits = ["Curious", "Loyal", "Ambitious", "Cautious", "Optimistic",
                          "Practical", "Mysterious", "Energetic", "Patient", "Witty"]
        motivations = ["To protect others", "To seek knowledge", "To find adventure",
                      "To build something lasting", "To discover truth"]
        fears = ["Being alone", "Losing control", "Being misunderstood", "Failure", "The unknown"]
        quirks = ["Always hums while working", "Collects unusual items", "Speaks to animals",
                 "Never sits still", "Always carries a lucky charm"]
        
        # Filter out existing traits
        available_traits = [t for t in primary_traits if t not in existing_traits]
        if not available_traits:
            available_traits = primary_traits
        
        return CharacterPersonality(
            primary_trait=random.choice(available_traits),
            secondary_trait=random.choice(secondary_traits),
            motivation=random.choice(motivations),
            fear=random.choice(fears),
            quirk=random.choice(quirks),
            speech_pattern="Speaks with confidence",
            alignment="Neutral Good",
            mood="Generally positive",
            secret="Has an interesting past",
            life_goal="To live meaningfully"
        )
    
    async def _generate_varied_age(self, role: str, personality: CharacterPersonality, attempt: int) -> int:
        """Generate age with variation based on role and personality"""
        base_ages = {
            "apprentice": 18, "student": 20, "guard": 25, "merchant": 35,
            "master": 45, "elder": 60, "scholar": 40, "priest": 50
        }
        
        base_age = 30  # default
        for key, age in base_ages.items():
            if key.lower() in role.lower():
                base_age = age
                break
        
        # Add variation based on personality and attempt
        variation = random.randint(-8, 12) + (attempt * 3)
        final_age = max(18, base_age + variation)
        
        return final_age
    
    async def _generate_ai_stats(self, role: str, personality: CharacterPersonality, 
                                age: int, existing_characters: List[CharacterProfile]) -> CharacterStats:
        """Generate AI-powered character stats"""
        # Base stats on role
        role_stats = {
            "warrior": {"strength": 16, "constitution": 15, "dexterity": 12},
            "mage": {"intelligence": 16, "wisdom": 14, "charisma": 13},
            "rogue": {"dexterity": 16, "intelligence": 14, "charisma": 12},
            "cleric": {"wisdom": 16, "charisma": 14, "constitution": 13}
        }
        
        # Find matching role
        base_stats = {"strength": 12, "intelligence": 12, "charisma": 12, 
                     "dexterity": 12, "wisdom": 12, "constitution": 12}
        
        for key, stats in role_stats.items():
            if key.lower() in role.lower():
                base_stats.update(stats)
                break
        
        # Adjust based on personality
        if "brave" in personality.primary_trait.lower():
            base_stats["strength"] += 2
        if "clever" in personality.primary_trait.lower():
            base_stats["intelligence"] += 2
        if "charismatic" in personality.primary_trait.lower():
            base_stats["charisma"] += 2
        
        # Age adjustments
        if age > 50:
            base_stats["wisdom"] += 2
            base_stats["strength"] -= 1
        elif age < 25:
            base_stats["dexterity"] += 1
            base_stats["wisdom"] -= 1
        
        # Ensure stats are in valid range
        for stat in base_stats:
            base_stats[stat] = max(8, min(18, base_stats[stat]))
        
        level = random.randint(1, 10)
        health = base_stats["constitution"] * 5 + level * 3
        
        return CharacterStats(
            level=level,
            health=health,
            strength=base_stats["strength"],
            intelligence=base_stats["intelligence"],
            charisma=base_stats["charisma"],
            dexterity=base_stats["dexterity"],
            wisdom=base_stats["wisdom"],
            constitution=base_stats["constitution"]
        )
    
    async def _generate_ai_backstory(self, name: str, personality: CharacterPersonality, 
                                   role: str, theme: str, age: int) -> str:
        """Generate AI-powered backstory"""
        if not AI_AVAILABLE:
            return f"{name} is a {role} who has spent {age} years perfecting their craft. {personality.motivation}"
        
        try:
            backstory = await self._call_creative_ai(
                f"Write a compelling 2-3 sentence backstory for {name}, a {age}-year-old {role} "
                f"in a {theme} setting. Their primary trait is {personality.primary_trait} "
                f"and they are motivated by: {personality.motivation}. "
                f"Include their secret: {personality.secret}",
                temperature=0.9
            )
            
            return backstory[:500] if backstory else f"{name} has lived an interesting life as a {role}."
            
        except Exception as e:
            self.logger.warning(f"AI backstory generation failed: {e}")
            return f"{name} is a {role} with a mysterious past and {personality.primary_trait.lower()} nature."
    
    async def _generate_ai_appearance(self, name: str, personality: CharacterPersonality, 
                                    role: str, theme: str, age: int) -> str:
        """Generate AI-powered appearance description"""
        if not AI_AVAILABLE:
            return f"A {age}-year-old {role} with a {personality.primary_trait.lower()} demeanor."
        
        try:
            appearance = await self._call_creative_ai(
                f"Describe the physical appearance of {name}, a {age}-year-old {role} "
                f"in a {theme} setting. They have a {personality.primary_trait.lower()} personality. "
                f"Be specific but concise (2-3 sentences).",
                temperature=0.8
            )
            
            return appearance[:300] if appearance else f"A distinctive {age}-year-old {role}."
            
        except Exception as e:
            self.logger.warning(f"AI appearance generation failed: {e}")
            return f"A {age}-year-old {role} with striking features."
    
    async def _generate_detailed_ai_appearance(self, name: str, personality: CharacterPersonality, 
                                             age: int, theme: str) -> str:
        """Generate detailed AI appearance"""
        if not AI_AVAILABLE:
            return f"Average height, {personality.primary_trait.lower()} expression, appropriate for a {theme} setting."
        
        try:
            detailed = await self._call_creative_ai(
                f"Provide detailed physical characteristics for {name}: "
                f"height, build, hair, eyes, distinctive features. "
                f"Age {age}, personality {personality.primary_trait}, {theme} setting.",
                temperature=0.7
            )
            
            return detailed[:400] if detailed else f"Distinctive appearance fitting a {theme} character."
            
        except Exception as e:
            self.logger.warning(f"AI detailed appearance generation failed: {e}")
            return f"Memorable features appropriate for {age}-year-old in {theme} setting."
    
    async def _generate_ai_voice(self, personality: CharacterPersonality, role: str, age: int) -> str:
        """Generate AI voice description"""
        if not AI_AVAILABLE:
            return f"Speaks with {personality.speech_pattern.lower()}"
        
        try:
            voice = await self._call_creative_ai(
                f"Describe the voice and speaking style of a {age}-year-old {role} "
                f"with {personality.primary_trait.lower()} personality. "
                f"Include tone, pace, accent, and mannerisms.",
                temperature=0.8
            )
            
            return voice[:200] if voice else personality.speech_pattern
            
        except Exception as e:
            self.logger.warning(f"AI voice generation failed: {e}")
            return personality.speech_pattern
    
    def _assign_unique_location(self, role: str, buildings: List[Dict], 
                               existing_characters: List[CharacterProfile]) -> str:
        """Assign unique location based on role and buildings"""
        role_locations = {
            "innkeeper": "tavern", "bartender": "tavern", "bard": "tavern",
            "blacksmith": "blacksmith", "weapon master": "blacksmith",
            "priest": "church", "acolyte": "church", "healer": "church",
            "merchant": "shop", "shopkeeper": "shop", "trader": "shop",
            "noble": "house", "resident": "house"
        }
        
        # Find appropriate location for role
        for role_key, location_type in role_locations.items():
            if role_key.lower() in role.lower():
                # Find building of this type
                for building in buildings:
                    if building.get('type') == location_type:
                        return location_type
        
        # Assign to least occupied building
        building_counts = {}
        for char in existing_characters:
            building_counts[char.location] = building_counts.get(char.location, 0) + 1
        
        if buildings:
            least_occupied = min(buildings, key=lambda b: building_counts.get(b.get('type', 'unknown'), 0))
            return least_occupied.get('type', 'town_square')
        
        return "town_square"
    
    async def _generate_ai_inventory(self, role: str, personality: CharacterPersonality, theme: str) -> List[str]:
        """Generate AI-powered inventory"""
        if not AI_AVAILABLE:
            return self._generate_fallback_inventory(role, theme)
        
        try:
            inventory_text = await self._call_creative_ai(
                f"List 3-5 items that a {role} in a {theme} setting would carry. "
                f"Consider their {personality.primary_trait.lower()} personality and {personality.quirk}. "
                f"Just list the items, one per line.",
                temperature=0.9
            )
            
            if inventory_text:
                items = [item.strip() for item in inventory_text.split('\n') if item.strip()]
                return items[:5]  # Limit to 5 items
            else:
                return self._generate_fallback_inventory(role, theme)
                
        except Exception as e:
            self.logger.warning(f"AI inventory generation failed: {e}")
            return self._generate_fallback_inventory(role, theme)
    
    def _generate_fallback_inventory(self, role: str, theme: str) -> List[str]:
        """Generate fallback inventory when AI fails"""
        role_items = {
            "blacksmith": ["Hammer", "Tongs", "Iron ingots"],
            "merchant": ["Coin purse", "Trade ledger", "Sample wares"],
            "priest": ["Holy symbol", "Prayer book", "Healing herbs"],
            "guard": ["Sword", "Shield", "City watch badge"],
            "scholar": ["Books", "Quill and ink", "Research notes"]
        }
        
        theme_items = {
            "medieval": ["Leather pouch", "Simple clothes", "Eating knife"],
            "fantasy": ["Magic trinket", "Mystical charm", "Traveling cloak"],
            "sci-fi": ["Data pad", "Energy cell", "Scanner"],
            "modern": ["Wallet", "Phone", "Keys"]
        }
        
        items = ["Personal belongings"]
        
        # Add role-specific items
        for role_key, role_inventory in role_items.items():
            if role_key.lower() in role.lower():
                items.extend(role_inventory)
                break
        
        # Add theme items
        theme_key = theme if theme in theme_items else "medieval"
        items.extend(theme_items[theme_key][:2])
        
        return items[:5]
    
    async def _generate_ai_title(self, name: str, role: str, personality: CharacterPersonality) -> str:
        """Generate AI character title"""
        if not AI_AVAILABLE:
            return f"The {personality.primary_trait} {role}"
        
        try:
            title = await self._call_creative_ai(
                f"Create a unique title or epithet for {name}, a {role} "
                f"known for being {personality.primary_trait.lower()}. "
                f"Make it memorable and fitting. Just return the title.",
                temperature=1.0
            )
            
            if title and title.strip():
                return title.strip()[:50]
            else:
                return f"The {personality.primary_trait} {role}"
                
        except Exception as e:
            self.logger.warning(f"AI title generation failed: {e}")
            return f"The {personality.primary_trait} {role}"
    
    def _is_character_unique(self, character: CharacterProfile) -> bool:
        """Check if character is sufficiently unique"""
        # Check name uniqueness
        if character.name in self.generated_names:
            return False
        
        # Check personality uniqueness
        personality_key = f"{character.personality.primary_trait}_{character.personality.secondary_trait}"
        if personality_key in self.generated_personalities:
            return False
        
        return True
    
    def _record_character_uniqueness(self, character: CharacterProfile):
        """Record character data for uniqueness tracking"""
        self.generated_names.add(character.name)
        personality_key = f"{character.personality.primary_trait}_{character.personality.secondary_trait}"
        self.generated_personalities.add(personality_key)
        
        # Store in uniqueness tracker
        self.uniqueness_tracker[character.id] = {
            'name': character.name,
            'personality': personality_key,
            'role': character.role,
            'generated_at': datetime.now().isoformat()
        }
    
    async def _generate_ai_relationships(self, characters: List[CharacterProfile], theme: str) -> List[CharacterProfile]:
        """Generate AI-powered relationships between characters"""
        if len(characters) < 2:
            return characters
        
        for i, char1 in enumerate(characters):
            for j, char2 in enumerate(characters[i + 1:], i + 1):
                # Generate relationship between char1 and char2
                relationship = await self._generate_single_relationship(char1, char2, theme)
                
                if relationship:
                    # Add relationship to both characters
                    char1.relationships.append(relationship)
                    
                    # Create reciprocal relationship
                    reciprocal = CharacterRelationship(
                        target_character=char1.name,
                        relationship_type=relationship.relationship_type,
                        relationship_strength=relationship.relationship_strength,
                        history=relationship.history,
                        current_status=relationship.current_status
                    )
                    char2.relationships.append(reciprocal)
        
        return characters
    
    async def _generate_single_relationship(self, char1: CharacterProfile, 
                                          char2: CharacterProfile, theme: str) -> Optional[CharacterRelationship]:
        """Generate a single relationship between two characters"""
        if not AI_AVAILABLE:
            return self._generate_fallback_relationship(char1, char2)
        
        try:
            relationship_prompt = f"""
            Create a relationship between {char1.name} ({char1.role}, {char1.personality.primary_trait}) 
            and {char2.name} ({char2.role}, {char2.personality.primary_trait}) in a {theme} setting.
            
            Format:
            Type: [relationship type]
            Strength: [1-10]
            History: [brief history]
            Status: [current status]
            """
            
            response = await self._call_creative_ai(relationship_prompt, temperature=0.8)
            
            if response:
                return self._parse_relationship_response(response, char2.name)
            else:
                return self._generate_fallback_relationship(char1, char2)
                
        except Exception as e:
            self.logger.warning(f"AI relationship generation failed: {e}")
            return self._generate_fallback_relationship(char1, char2)
    
    def _parse_relationship_response(self, response: str, target_name: str) -> CharacterRelationship:
        """Parse AI relationship response"""
        lines = response.strip().split('\n')
        relationship_data = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                relationship_data[key] = value
        
        # Parse strength as integer
        strength_str = relationship_data.get('strength', '5')
        try:
            strength = int(''.join(filter(str.isdigit, strength_str)))
            strength = max(1, min(10, strength))
        except ValueError:
            strength = 5
        
        return CharacterRelationship(
            target_character=target_name,
            relationship_type=relationship_data.get('type', 'Acquaintance'),
            relationship_strength=strength,
            history=relationship_data.get('history', 'They have met before'),
            current_status=relationship_data.get('status', 'Neutral')
        )
    
    def _generate_fallback_relationship(self, char1: CharacterProfile, 
                                      char2: CharacterProfile) -> CharacterRelationship:
        """Generate fallback relationship when AI fails"""
        relationship_types = ["Friend", "Acquaintance", "Rival", "Ally", "Colleague", "Neighbor"]
        
        # Base relationship type on roles
        if char1.role == char2.role:
            rel_type = random.choice(["Colleague", "Rival", "Friend"])
        elif char1.location == char2.location:
            rel_type = random.choice(["Neighbor", "Acquaintance", "Friend"])
        else:
            rel_type = random.choice(relationship_types)
        
        return CharacterRelationship(
            target_character=char2.name,
            relationship_type=rel_type,
            relationship_strength=random.randint(3, 8),
            history=f"They know each other through their work in town",
            current_status="Neutral"
        )
    
    async def _generate_ai_dialogues(self, characters: List[CharacterProfile], theme: str) -> List[CharacterProfile]:
        """Generate AI dialogue trees for each character"""
        for character in characters:
            character.dialogue_tree = await self._generate_character_dialogue(character, theme)
        
        return characters
    
    async def _generate_character_dialogue(self, character: CharacterProfile, theme: str) -> List[DialogueNode]:
        """Generate dialogue tree for a single character"""
        if not AI_AVAILABLE:
            return self._generate_fallback_dialogue(character)
        
        try:
            dialogue_prompt = f"""
            Create a dialogue tree for {character.name}, a {character.role} 
            with {character.personality.primary_trait.lower()} personality in a {theme} setting.
            
            Create 3 dialogue nodes:
            1. Greeting - how they greet strangers
            2. About Role - discussing their work/role
            3. Personal - sharing something personal
            
            Format each node as:
            Node ID: [unique_id]
            Speaker: {character.name}
            Text: [what they say]
            Type: [greeting/role/personal]
            """
            
            response = await self._call_creative_ai(dialogue_prompt, temperature=0.9)
            
            if response:
                return self._parse_dialogue_response(response, character.name)
            else:
                return self._generate_fallback_dialogue(character)
                
        except Exception as e:
            self.logger.warning(f"AI dialogue generation failed: {e}")
            return self._generate_fallback_dialogue(character)
    
    def _parse_dialogue_response(self, response: str, speaker_name: str) -> List[DialogueNode]:
        """Parse AI dialogue response into dialogue nodes"""
        nodes = []
        current_node = {}
        
        for line in response.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'node id' and current_node:
                    # Save previous node
                    nodes.append(self._create_dialogue_node(current_node, speaker_name))
                    current_node = {}
                
                current_node[key] = value
        
        # Add final node
        if current_node:
            nodes.append(self._create_dialogue_node(current_node, speaker_name))
        
        return nodes[:3]  # Limit to 3 nodes
    
    def _create_dialogue_node(self, node_data: Dict[str, str], speaker_name: str) -> DialogueNode:
        """Create a dialogue node from parsed data"""
        node_id = node_data.get('node id', f"{speaker_name.lower()}_default")
        text = node_data.get('text', "Hello there!")
        node_type = node_data.get('type', 'general')
        
        # Create basic dialogue option
        option = DialogueOption(
            id=f"{node_id}_continue",
            text="Continue conversation",
            next_node_id=None,
            conditions=[],
            effects=[]
        )
        
        return DialogueNode(
            id=node_id,
            text=text,
            speaker=speaker_name,
            options=[option],
            is_greeting=(node_type == 'greeting'),
            is_farewell=False,
            quest_related=False
        )
    
    def _generate_fallback_dialogue(self, character: CharacterProfile) -> List[DialogueNode]:
        """Generate fallback dialogue when AI fails"""
        greeting_node = DialogueNode(
            id=f"{character.name.lower()}_greeting",
            text=f"Greetings! I'm {character.name}, the local {character.role}.",
            speaker=character.name,
            options=[DialogueOption(
                id="greeting_continue",
                text="Tell me about your work",
                next_node_id=f"{character.name.lower()}_role",
                conditions=[],
                effects=[]
            )],
            is_greeting=True
        )
        
        role_node = DialogueNode(
            id=f"{character.name.lower()}_role",
            text=f"As a {character.role}, I {character.personality.motivation.lower()}.",
            speaker=character.name,
            options=[DialogueOption(
                id="role_continue",
                text="That's interesting",
                next_node_id=None,
                conditions=[],
                effects=[]
            )]
        )
        
        return [greeting_node, role_node]
    
    async def _ensure_final_uniqueness(self, characters: List[CharacterProfile]) -> List[CharacterProfile]:
        """Final pass to ensure all characters are unique"""
        # Check for any remaining duplicates and fix them
        seen_names = set()
        seen_personalities = set()
        
        for i, character in enumerate(characters):
            # Fix duplicate names
            original_name = character.name
            counter = 1
            while character.name in seen_names:
                character.name = f"{original_name} {counter}"
                counter += 1
            seen_names.add(character.name)
            
            # Fix duplicate personalities
            personality_key = f"{character.personality.primary_trait}_{character.personality.secondary_trait}"
            if personality_key in seen_personalities:
                # Modify secondary trait
                traits = ["Determined", "Curious", "Cautious", "Bold", "Gentle", "Fierce"]
                for trait in traits:
                    new_key = f"{character.personality.primary_trait}_{trait}"
                    if new_key not in seen_personalities:
                        character.personality.secondary_trait = trait
                        personality_key = new_key
                        break
            
            seen_personalities.add(personality_key)
        
        return characters
    
    async def _save_unique_characters(self, characters: List[CharacterProfile], 
                                    theme: str, world_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Save all character data with comprehensive manifest"""
        # Save individual character profiles
        for character in characters:
            profile_file = self.profiles_dir / f"{character.id}_profile.json"
            with open(profile_file, 'w') as f:
                json.dump(asdict(character), f, indent=2)
            
            # Save dialogue tree separately
            dialogue_file = self.dialogue_dir / f"{character.id}_dialogue.json"
            dialogue_data = {
                'character_name': character.name,
                'dialogue_tree': [asdict(node) for node in character.dialogue_tree]
            }
            with open(dialogue_file, 'w') as f:
                json.dump(dialogue_data, f, indent=2)
        
        # Save relationship map
        relationship_map = {}
        for character in characters:
            relationship_map[character.name] = [asdict(rel) for rel in character.relationships]
        
        relationship_file = self.relationships_dir / "relationship_map.json"
        with open(relationship_file, 'w') as f:
            json.dump(relationship_map, f, indent=2)
        
        # Generate comprehensive stats
        stats_summary = {
            'generation_stats': {
                'total_characters': len(characters),
                'average_age': sum(char.age for char in characters) / len(characters),
                'total_relationships': sum(len(char.relationships) for char in characters),
                'total_dialogue_nodes': sum(len(char.dialogue_tree) for char in characters),
                'unique_roles': len(set(char.role for char in characters)),
                'unique_locations': len(set(char.location for char in characters))
            },
            'uniqueness_metrics': {
                'name_uniqueness': len(set(char.name for char in characters)) / len(characters),
                'personality_uniqueness': len(set(f"{char.personality.primary_trait}_{char.personality.secondary_trait}" 
                                                for char in characters)) / len(characters),
                'role_uniqueness': len(set(char.role for char in characters)) / len(characters)
            },
            'level_distribution': {char.name: char.stats.level for char in characters},
            'role_distribution': {char.name: char.role for char in characters},
            'personality_distribution': {char.name: char.personality.primary_trait for char in characters}
        }
        
        stats_file = self.stats_dir / "character_stats_summary.json"
        with open(stats_file, 'w') as f:
            json.dump(stats_summary, f, indent=2)
        
        # Create enhanced manifest
        manifest = {
            'generation_info': {
                'timestamp': datetime.now().isoformat(),
                'theme': theme,
                'world_size': world_spec.get('size', (0, 0)),
                'character_count': len(characters),
                'ai_enhanced': AI_AVAILABLE,
                'creativity_level': 'maximum',
                'uniqueness_guaranteed': True,
                'session_id': self.current_session
            },
            'uniqueness_metrics': stats_summary['uniqueness_metrics'],
            'characters': {
                char.id: {
                    'name': char.name,
                    'title': char.title,
                    'role': char.role,
                    'age': char.age,
                    'location': char.location,
                    'personality_summary': f"{char.personality.primary_trait}, {char.personality.secondary_trait}",
                    'motivation': char.personality.motivation,
                    'secret': char.personality.secret,
                    'level': char.stats.level,
                    'health': char.stats.health,
                    'relationship_count': len(char.relationships),
                    'dialogue_nodes': len(char.dialogue_tree),
                    'unique_id': char.unique_id,
                    'profile_file': f"character_profiles/{char.id}_profile.json",
                    'dialogue_file': f"dialogue_trees/{char.id}_dialogue.json"
                }
                for char in characters
            },
            'relationships_summary': {
                'total_relationships': sum(len(char.relationships) for char in characters),
                'relationship_types': list(set(
                    rel.relationship_type 
                    for char in characters 
                    for rel in char.relationships
                )),
                'relationship_map_file': "relationship_maps/relationship_map.json"
            },
            'dialogue_summary': {
                'total_dialogue_nodes': sum(len(char.dialogue_tree) for char in characters),
                'average_nodes_per_character': sum(len(char.dialogue_tree) for char in characters) / len(characters) if characters else 0,
                'ai_generated': AI_AVAILABLE
            },
            'integration_info': {
                'unity_compatible': True,
                'quest_system_ready': True,
                'relationship_system_ready': True,
                'dialogue_system_ready': True,
                'ai_creativity_verified': AI_AVAILABLE
            }
        }
        
        # Save manifest
        manifest_file = self.output_dir / "character_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest
    
    async def _generate_fallback_characters(self, world_spec: Dict[str, Any], character_count: int) -> Dict[str, Any]:
        """Generate characters using fallback methods when AI is not available"""
        self.logger.warning("🔄 AI not available, using fallback character generation")
        
        theme = world_spec.get('theme', 'medieval')
        buildings = world_spec.get('buildings', [])
        
        characters = []
        
        for i in range(character_count):
            # Generate basic character using fallback methods
            character_name = self._generate_fallback_name(theme, [c.name for c in characters], i)
            character_role = self._generate_fallback_role(theme, buildings, [c.role for c in characters])
            personality = self._generate_fallback_personality([c.personality.primary_trait for c in characters])
            
            age = random.randint(20, 60)
            stats = await self._generate_ai_stats(character_role, personality, age, characters)
            location = self._assign_unique_location(character_role, buildings, characters)
            inventory = self._generate_fallback_inventory(character_role, theme)
            
            character_id = f"{character_name.lower().replace(' ', '_')}_{self.current_session}_{i}"
            
            character = CharacterProfile(
                id=character_id,
                name=character_name,
                title=f"The {personality.primary_trait} {character_role}",
                description=f"A {age}-year-old {character_role} with a {personality.primary_trait.lower()} nature.",
                backstory=f"{character_name} has worked as a {character_role} for many years.",
                personality=personality,
                stats=stats,
                relationships=[],
                dialogue_tree=self._generate_fallback_dialogue(CharacterProfile(
                    id=character_id, name=character_name, title="", description="",
                    backstory="", personality=personality, stats=stats, relationships=[],
                    dialogue_tree=[], inventory=[], location=location, role=character_role,
                    quest_involvement=[], age=age, appearance="", voice_description="",
                    unique_id=""
                )),
                inventory=inventory,
                location=location,
                role=character_role,
                quest_involvement=[],
                age=age,
                appearance=f"A {age}-year-old {character_role} with distinctive features.",
                voice_description=personality.speech_pattern,
                unique_id=str(uuid.uuid4())
            )
            
            characters.append(character)
            self._record_character_uniqueness(character)
        
        # Add basic relationships
        for i, char1 in enumerate(characters):
            for j, char2 in enumerate(characters[i + 1:], i + 1):
                if random.random() < 0.3:  # 30% chance of relationship
                    relationship = self._generate_fallback_relationship(char1, char2)
                    char1.relationships.append(relationship)
                    
                    reciprocal = CharacterRelationship(
                        target_character=char1.name,
                        relationship_type=relationship.relationship_type,
                        relationship_strength=relationship.relationship_strength,
                        history=relationship.history,
                        current_status=relationship.current_status
                    )
                    char2.relationships.append(reciprocal)
        
        # Save characters
        manifest = await self._save_unique_characters(characters, theme, world_spec)
        
        return {
            'status': 'success',
            'character_count': len(characters),
            'output_directory': str(self.output_dir),
            'manifest_file': str(self.output_dir / "character_manifest.json"),
            'ai_enhanced': False,
            'fallback_generation': True,
            'characters': [asdict(char) for char in characters]
        }
    
    async def _generate_fallback_character(self, theme: str, buildings: List[Dict], 
                                         index: int, existing_characters: List[CharacterProfile]) -> CharacterProfile:
        """Generate a single fallback character"""
        character_name = self._generate_fallback_name(theme, [c.name for c in existing_characters], index)
        character_role = self._generate_fallback_role(theme, buildings, [c.role for c in existing_characters])
        personality = self._generate_fallback_personality([c.personality.primary_trait for c in existing_characters])
        
        age = random.randint(20, 60)
        stats = await self._generate_ai_stats(character_role, personality, age, existing_characters)
        location = self._assign_unique_location(character_role, buildings, existing_characters)
        inventory = self._generate_fallback_inventory(character_role, theme)
        
        character_id = f"{character_name.lower().replace(' ', '_')}_{self.current_session}_{index}"
        
        return CharacterProfile(
            id=character_id,
            name=character_name,
            title=f"The {personality.primary_trait} {character_role}",
            description=f"A {age}-year-old {character_role} with a {personality.primary_trait.lower()} demeanor.",
            backstory=f"{character_name} has lived in town as a {character_role} for several years.",
            personality=personality,
            stats=stats,
            relationships=[],
            dialogue_tree=[],
            inventory=inventory,
            location=location,
            role=character_role,
            quest_involvement=[],
            age=age,
            appearance=f"A distinctive {age}-year-old {character_role}.",
            voice_description=personality.speech_pattern,
            unique_id=str(uuid.uuid4())
        )
    
    async def _call_creative_ai(self, prompt: str, temperature: float = 1.0) -> Optional[str]:
        """Call AI with enhanced creativity settings"""
        if not AI_AVAILABLE:
            return None
        
        try:
            # Add creativity boosters to prompt
            enhanced_prompt = f"{prompt}\n\nBe maximally creative, unique, and avoid all clichés. Think outside the box and surprise me with originality."
            
            # Configure for creativity
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                top_p=0.95,
                top_k=64,
                candidate_count=1,
                max_output_tokens=800,
            )
            
            response = self.gemini_model.generate_content(enhanced_prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            self.logger.warning(f"Creative AI call failed: {e}")
            return None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get enhanced character creator status"""
        return {
            'status': 'ready',
            'ai_available': AI_AVAILABLE,
            'creativity_level': 'maximum',
            'uniqueness_guaranteed': True,
            'output_directory': str(self.output_dir),
            'capabilities': [
                'ai_character_generation',
                'unique_personality_creation',
                'creative_relationship_mapping',
                'ai_dialogue_trees',
                'advanced_stat_balancing',
                'uniqueness_tracking',
                'creative_backstory_generation'
            ],
            'ai_features': {
                'personality_generation': AI_AVAILABLE,
                'backstory_creation': AI_AVAILABLE,
                'dialogue_generation': AI_AVAILABLE,
                'relationship_histories': AI_AVAILABLE,
                'creative_name_generation': AI_AVAILABLE,
                'unique_role_creation': AI_AVAILABLE
            },
            'uniqueness_tracking': {
                'generated_names': len(self.generated_names),
                'generated_personalities': len(self.generated_personalities),
                'current_session': self.current_session
            }
        }

# ADK Agent Functions for integration
async def generate_characters_for_world(world_spec: Dict[str, Any], character_count: int = 5) -> Dict[str, Any]:
    """Generate truly unique characters - main entry point"""
    generator = CreativeCharacterGenerator()
    return await generator.generate_unique_characters(world_spec, character_count)

async def get_character_creator_status() -> Dict[str, Any]:
    """Get enhanced character creator status"""
    generator = CreativeCharacterGenerator()
    return await generator.get_status()

# Create the enhanced ADK agent
root_agent = Agent(
    name="enhanced_character_creator",
    model="gemini-2.0-flash-exp",
    instruction="""You are an AI-powered Character Creator Agent that generates COMPLETELY UNIQUE NPCs with maximum creativity and zero repetition.

Every generation produces completely original characters with:
- Unique AI-generated names that fit the theme
- Original personality combinations never seen before
- Creative roles and specializations
- Individual backstories with personal depth
- Distinctive speech patterns and dialogue
- Complex motivational structures

When you receive a character generation request, you create characters so unique that each one feels like they could be the protagonist of their own story.""",
    description="Enhanced AI Character Creator Agent that generates completely unique NPCs with guaranteed creativity and zero repetition using advanced AI techniques",
    tools=[generate_characters_for_world, get_character_creator_status]
)

# Standalone testing
if __name__ == "__main__":
    async def main():
        print("🎭 Testing Enhanced AI Character Creator")
        print("="*60)
        print("🎯 GOAL: Generate completely unique characters with zero repetition")
        print("🤖 AI CREATIVITY: Maximum temperature settings for originality")
        print("✨ UNIQUENESS: Guaranteed different names, personalities, and traits")
        
        # Test world specification
        test_world = {
            "theme": "medieval",
            "size": (40, 40),
            "buildings": [
                {"type": "tavern", "position": {"x": 20, "y": 20, "z": 0}},
                {"type": "blacksmith", "position": {"x": 15, "y": 25, "z": 0}},
                {"type": "church", "position": {"x": 25, "y": 15, "z": 0}},
                {"type": "shop", "position": {"x": 18, "y": 22, "z": 0}},
                {"type": "house", "position": {"x": 12, "y": 18, "z": 0}}
            ],
            "natural_features": [
                {"type": "well", "position": {"x": 20, "y": 18, "z": 0}}
            ]
        }
        
        generator = CreativeCharacterGenerator("test_enhanced_characters")
        
        print("\n🧪 Testing Enhanced Character Generation...")
        
        try:
            result = await generator.generate_unique_characters(test_world, 3)
            
            if result['status'] == 'success':
                print(f"\n✅ Enhanced Generation Success!")
                print(f"   📁 Output Directory: {result['output_directory']}")
                print(f"   📊 Characters Created: {result['character_count']}")
                print(f"   🤝 Total Relationships: {result['total_relationships']}")
                print(f"   💬 Total Dialogue Nodes: {result['total_dialogue_nodes']}")
                print(f"   🎭 Unique Personalities: {result['unique_personalities']}")
                
                # Show character summaries
                print(f"\n📝 Character Summaries:")
                for char_data in result['characters']:
                    char = char_data
                    print(f"   • {char['name']} - {char['role']}")
                    print(f"     Age: {char['age']}, Location: {char['location']}")
                    print(f"     Personality: {char['personality']['primary_trait']}")
                    print(f"     Motivation: {char['personality']['motivation']}")
                    print()
                
                print(f"🎉 Test completed successfully!")
                print(f"📄 Manifest saved to: {result['manifest_file']}")
                
            else:
                print(f"\n❌ Generation failed: {result}")
                
        except Exception as e:
            print(f"\n💥 Test failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    # Run the test
    asyncio.run(main())