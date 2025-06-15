#!/usr/bin/env python3
"""
BALANCE VALIDATOR AGENT v1.0 - COMPLETE IMPLEMENTATION
Validates and balances all generated content for optimal gameplay
Ensures proper XP curves, quest difficulty, character balance, and progression
"""

import asyncio
import json
import random
import math
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from datetime import datetime
import statistics

# Google ADK imports
from google.adk.agents import Agent

# AI imports for advanced balance calculations
try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

@dataclass
class BalanceMetrics:
    """Core balance metrics for validation"""
    difficulty_score: float
    progression_rate: float
    xp_balance: float
    reward_balance: float
    challenge_curve: float
    player_engagement: float
    overall_score: float

@dataclass
class BalanceRecommendation:
    """Balance adjustment recommendation"""
    category: str  # 'xp', 'rewards', 'difficulty', 'progression'
    target: str    # what to adjust
    current_value: Any
    recommended_value: Any
    reason: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    impact: str    # description of impact

@dataclass
class BalanceReport:
    """Complete balance validation report"""
    overall_balance: str  # 'excellent', 'good', 'needs_adjustment', 'critical_issues'
    metrics: BalanceMetrics
    recommendations: List[BalanceRecommendation]
    warnings: List[str]
    validated_content: Dict[str, Any]
    balance_summary: Dict[str, Any]

class AdvancedBalanceValidator:
    """
    ADVANCED GAME BALANCE VALIDATOR
    - Validates XP curves and level progression
    - Balances quest rewards and difficulty
    - Ensures character stat distribution
    - Validates economic balance (gold/items)
    - Checks progression pacing
    - Provides detailed recommendations
    """
    
    def __init__(self, output_dir: str = "balance_validation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Balance validation directories
        self.reports_dir = self.output_dir / "balance_reports"
        self.metrics_dir = self.output_dir / "balance_metrics"
        self.recommendations_dir = self.output_dir / "recommendations"
        self.simulations_dir = self.output_dir / "playtesting_simulations"
        
        for dir_path in [self.reports_dir, self.metrics_dir, self.recommendations_dir, self.simulations_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Balance configuration
        self.balance_config = self._load_balance_config()
        
        # Initialize AI for advanced balance analysis
        if AI_AVAILABLE:
            self._initialize_ai()
        
        self.logger.info(f"✅ AdvancedBalanceValidator initialized: {self.output_dir}")
    
    def _load_balance_config(self) -> Dict[str, Any]:
        """Load balance configuration parameters"""
        return {
            # XP and Level Balance
            'xp_curves': {
                'linear': lambda level: level * 1000,
                'polynomial': lambda level: level ** 1.5 * 500,
                'exponential': lambda level: 100 * (1.5 ** level),
                'logarithmic': lambda level: 1000 * math.log(level + 1) * level
            },
            'target_levels': {
                'beginner_friendly': 10,
                'standard_rpg': 20,
                'hardcore_rpg': 50
            },
            
            # Quest Balance
            'quest_difficulty': {
                'trivial': {'xp_mult': 0.5, 'time_minutes': 5},
                'easy': {'xp_mult': 1.0, 'time_minutes': 15},
                'medium': {'xp_mult': 1.5, 'time_minutes': 30},
                'hard': {'xp_mult': 2.0, 'time_minutes': 60},
                'epic': {'xp_mult': 3.0, 'time_minutes': 120}
            },
            
            # Character Balance
            'stat_ranges': {
                'min_stat': 8,
                'max_stat': 18,
                'total_points_level_1': 72,  # 6 stats * 12 average
                'points_per_level': 2
            },
            
            # Economic Balance
            'economy': {
                'gold_per_hour_base': 50,
                'gold_per_hour_growth': 1.2,  # 20% per level
                'item_cost_multiplier': 0.2,  # 20% of level gold
                'quest_gold_ratio': 0.3      # 30% of quest XP as gold value
            },
            
            # Progression Pacing
            'pacing': {
                'quests_per_level': 3,
                'max_level_gap': 2,  # Max level difference for balanced content
                'difficulty_increase_rate': 0.15  # 15% increase per level
            }
        }
    
    def _initialize_ai(self):
        """Initialize AI for advanced balance analysis"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel(
                    'gemini-2.0-flash-exp',
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,  # Lower temperature for analytical tasks
                        top_p=0.8,
                        max_output_tokens=1000
                    )
                )
                self.logger.info("✅ AI initialized for advanced balance analysis")
            else:
                self.logger.warning("⚠️ No API key found for AI balance analysis")
                
        except Exception as e:
            self.logger.warning(f"⚠️ AI initialization failed: {e}")
    
    async def validate_complete_content(self, 
                                      world_spec: Dict[str, Any],
                                      assets: Dict[str, Any],
                                      characters: Dict[str, Any], 
                                      quests: Dict[str, Any]) -> BalanceReport:
        """
        MAIN VALIDATION FUNCTION - validates all content for optimal balance
        """
        self.logger.info("⚖️ Starting Complete Content Balance Validation...")
        
        try:
            # Step 1: Extract and analyze all content
            content_analysis = await self._analyze_content_structure(
                world_spec, assets, characters, quests
            )
            
            # Step 2: Validate XP and level progression
            self.logger.info("📊 Validating XP and level progression...")
            xp_balance = await self._validate_xp_progression(characters, quests)
            
            # Step 3: Validate quest difficulty and rewards
            self.logger.info("🎯 Validating quest difficulty and rewards...")
            quest_balance = await self._validate_quest_balance(quests, characters)
            
            # Step 4: Validate character balance
            self.logger.info("👥 Validating character balance...")
            character_balance = await self._validate_character_balance(characters)
            
            # Step 5: Validate economic balance
            self.logger.info("💰 Validating economic balance...")
            economic_balance = await self._validate_economic_balance(quests, characters)
            
            # Step 6: Validate progression pacing
            self.logger.info("⏱️ Validating progression pacing...")
            pacing_balance = await self._validate_progression_pacing(
                world_spec, characters, quests
            )
            
            # Step 7: Simulate gameplay balance
            self.logger.info("🎮 Running gameplay simulations...")
            simulation_results = await self._run_balance_simulations(
                content_analysis, xp_balance, quest_balance, character_balance
            )
            
            # Step 8: Calculate overall balance metrics
            metrics = self._calculate_balance_metrics(
                xp_balance, quest_balance, character_balance, 
                economic_balance, pacing_balance, simulation_results
            )
            
            # Step 9: Generate recommendations
            recommendations = await self._generate_balance_recommendations(
                metrics, xp_balance, quest_balance, character_balance,
                economic_balance, pacing_balance
            )
            
            # Step 10: Create validated content with adjustments
            validated_content = await self._apply_balance_adjustments(
                world_spec, assets, characters, quests, recommendations
            )
            
            # Step 11: Generate final report
            balance_report = BalanceReport(
                overall_balance=self._determine_overall_balance(metrics),
                metrics=metrics,
                recommendations=recommendations,
                warnings=self._generate_balance_warnings(metrics, recommendations),
                validated_content=validated_content,
                balance_summary=self._create_balance_summary(metrics, recommendations)
            )
            
            # Step 12: Save validation results
            await self._save_balance_report(balance_report)
            
            self.logger.info(f"✅ Balance validation complete: {balance_report.overall_balance}")
            return balance_report
            
        except Exception as e:
            self.logger.error(f"❌ Balance validation failed: {e}")
            raise
    
    async def _analyze_content_structure(self, world_spec: Dict, assets: Dict, 
                                       characters: Dict, quests: Dict) -> Dict[str, Any]:
        """Analyze the structure of all generated content"""
        
        character_list = characters.get('characters', [])
        quest_list = quests.get('quests', [])
        
        analysis = {
            'world': {
                'theme': world_spec.get('theme', 'unknown'),
                'size': world_spec.get('size', (0, 0)),
                'building_count': len(world_spec.get('buildings', [])),
                'feature_count': len(world_spec.get('natural_features', []))
            },
            'characters': {
                'total_count': len(character_list),
                'level_range': self._analyze_character_levels(character_list),
                'stat_distribution': self._analyze_character_stats(character_list),
                'role_distribution': self._analyze_character_roles(character_list)
            },
            'quests': {
                'total_count': len(quest_list),
                'type_distribution': self._analyze_quest_types(quest_list),
                'reward_range': self._analyze_quest_rewards(quest_list),
                'difficulty_spread': self._analyze_quest_difficulty(quest_list)
            },
            'assets': {
                'total_assets': assets.get('generation_summary', {}).get('total_creative_assets', 0),
                'ai_generated': assets.get('ai_generated', False)
            }
        }
        
        return analysis
    
    def _analyze_character_levels(self, characters: List[Dict]) -> Dict[str, int]:
        """Analyze character level distribution"""
        if not characters:
            return {'min': 1, 'max': 1, 'average': 1}
        
        levels = [char.get('stats', {}).get('level', 1) for char in characters]
        return {
            'min': min(levels),
            'max': max(levels),
            'average': sum(levels) / len(levels)
        }
    
    def _analyze_character_stats(self, characters: List[Dict]) -> Dict[str, float]:
        """Analyze character stat distribution"""
        if not characters:
            return {'average_total': 72, 'balance_score': 1.0}
        
        total_stats = []
        for char in characters:
            stats = char.get('stats', {})
            total = (stats.get('strength', 12) + stats.get('intelligence', 12) + 
                    stats.get('charisma', 12) + stats.get('dexterity', 12) + 
                    stats.get('wisdom', 12) + stats.get('constitution', 12))
            total_stats.append(total)
        
        average_total = sum(total_stats) / len(total_stats)
        target_total = self.balance_config['stat_ranges']['total_points_level_1']
        balance_score = min(average_total / target_total, target_total / average_total)
        
        return {
            'average_total': average_total,
            'balance_score': balance_score,
            'stat_variance': statistics.variance(total_stats) if len(total_stats) > 1 else 0
        }
    
    def _analyze_character_roles(self, characters: List[Dict]) -> Dict[str, int]:
        """Analyze character role distribution"""
        role_counts = {}
        for char in characters:
            role = char.get('role', 'unknown')
            role_counts[role] = role_counts.get(role, 0) + 1
        return role_counts
    
    def _analyze_quest_types(self, quests: List[Dict]) -> Dict[str, int]:
        """Analyze quest type distribution"""
        type_counts = {}
        for quest in quests:
            quest_type = quest.get('quest_type', 'unknown')
            type_counts[quest_type] = type_counts.get(quest_type, 0) + 1
        return type_counts
    
    def _analyze_quest_rewards(self, quests: List[Dict]) -> Dict[str, float]:
        """Analyze quest reward distribution"""
        if not quests:
            return {'min_xp': 0, 'max_xp': 0, 'average_xp': 0, 'min_gold': 0, 'max_gold': 0}
        
        xp_rewards = []
        gold_rewards = []
        
        for quest in quests:
            rewards = quest.get('rewards', {})
            xp_rewards.append(rewards.get('experience', 50))
            gold_rewards.append(rewards.get('gold', 25))
        
        return {
            'min_xp': min(xp_rewards),
            'max_xp': max(xp_rewards),
            'average_xp': sum(xp_rewards) / len(xp_rewards),
            'min_gold': min(gold_rewards),
            'max_gold': max(gold_rewards),
            'average_gold': sum(gold_rewards) / len(gold_rewards)
        }
    
    def _analyze_quest_difficulty(self, quests: List[Dict]) -> Dict[str, float]:
        """Analyze quest difficulty distribution"""
        if not quests:
            return {'average_difficulty': 1.0, 'difficulty_variance': 0}
        
        difficulties = []
        for quest in quests:
            # Estimate difficulty based on objectives, level requirement, and rewards
            objective_count = len(quest.get('objectives', []))
            level_req = quest.get('level_requirement', 1)
            xp_reward = quest.get('rewards', {}).get('experience', 50)
            
            # Simple difficulty score calculation
            difficulty = (objective_count * 0.3) + (level_req * 0.4) + (xp_reward / 100 * 0.3)
            difficulties.append(difficulty)
        
        return {
            'average_difficulty': sum(difficulties) / len(difficulties),
            'difficulty_variance': statistics.variance(difficulties) if len(difficulties) > 1 else 0
        }
    
    async def _validate_xp_progression(self, characters: Dict, quests: Dict) -> Dict[str, Any]:
        """Validate XP progression and level curves"""
        
        character_list = characters.get('characters', [])
        quest_list = quests.get('quests', [])
        
        # Calculate total available XP
        total_quest_xp = sum(
            quest.get('rewards', {}).get('experience', 50) 
            for quest in quest_list
        )
        
        # Determine target level progression
        max_char_level = max(
            char.get('stats', {}).get('level', 1) 
            for char in character_list
        ) if character_list else 5
        
        # Calculate XP curve efficiency
        target_curve = self.balance_config['xp_curves']['polynomial']
        total_needed_xp = sum(target_curve(level) for level in range(1, max_char_level + 1))
        
        xp_balance_ratio = total_quest_xp / total_needed_xp if total_needed_xp > 0 else 0
        
        return {
            'total_available_xp': total_quest_xp,
            'total_needed_xp': total_needed_xp,
            'xp_balance_ratio': xp_balance_ratio,
            'max_achievable_level': max_char_level,
            'xp_curve_type': 'polynomial',
            'balance_score': min(xp_balance_ratio, 2.0 - xp_balance_ratio) if xp_balance_ratio <= 2 else 0,
            'recommended_adjustments': self._calculate_xp_adjustments(xp_balance_ratio)
        }
    
    def _calculate_xp_adjustments(self, ratio: float) -> List[str]:
        """Calculate recommended XP adjustments"""
        adjustments = []
        
        if ratio < 0.8:
            adjustments.append("Increase quest XP rewards by 25%")
            adjustments.append("Add more side quests for additional XP")
        elif ratio > 1.5:
            adjustments.append("Reduce quest XP rewards by 20%")
            adjustments.append("Increase XP requirements for higher levels")
        elif 0.8 <= ratio <= 1.2:
            adjustments.append("XP progression is well balanced")
        
        return adjustments
    
    async def _validate_quest_balance(self, quests: Dict, characters: Dict) -> Dict[str, Any]:
        """Validate quest difficulty and reward balance"""
        
        quest_list = quests.get('quests', [])
        character_list = characters.get('characters', [])
        
        if not quest_list:
            return {'balance_score': 0, 'issues': ['No quests to validate']}
        
        # Analyze quest-to-character level alignment
        avg_char_level = sum(
            char.get('stats', {}).get('level', 1) 
            for char in character_list
        ) / len(character_list) if character_list else 1
        
        quest_balance_issues = []
        difficulty_scores = []
        
        for quest in quest_list:
            # Validate quest level requirements
            quest_level = quest.get('level_requirement', 1)
            level_gap = abs(quest_level - avg_char_level)
            
            if level_gap > self.balance_config['pacing']['max_level_gap']:
                quest_balance_issues.append(
                    f"Quest '{quest.get('title', 'Unknown')}' level {quest_level} too far from character average {avg_char_level:.1f}"
                )
            
            # Validate reward-to-difficulty ratio
            xp_reward = quest.get('rewards', {}).get('experience', 50)
            objective_count = len(quest.get('objectives', []))
            
            expected_xp = objective_count * 25 * quest_level  # Base calculation
            xp_ratio = xp_reward / expected_xp if expected_xp > 0 else 1
            
            difficulty_scores.append(xp_ratio)
            
            if xp_ratio < 0.5:
                quest_balance_issues.append(
                    f"Quest '{quest.get('title', 'Unknown')}' XP reward too low for difficulty"
                )
            elif xp_ratio > 2.0:
                quest_balance_issues.append(
                    f"Quest '{quest.get('title', 'Unknown')}' XP reward too high for difficulty"
                )
        
        # Calculate overall quest balance score
        avg_difficulty_score = sum(difficulty_scores) / len(difficulty_scores) if difficulty_scores else 1
        balance_score = min(avg_difficulty_score, 2.0 - avg_difficulty_score) if avg_difficulty_score <= 2 else 0
        
        return {
            'balance_score': balance_score,
            'average_difficulty_ratio': avg_difficulty_score,
            'quest_level_alignment': avg_char_level,
            'balance_issues': quest_balance_issues,
            'recommended_difficulty_curve': self._generate_difficulty_curve(quest_list),
            'reward_optimization': self._optimize_quest_rewards(quest_list)
        }
    
    def _generate_difficulty_curve(self, quests: List[Dict]) -> List[Dict]:
        """Generate recommended difficulty curve for quests"""
        if not quests:
            return []
        
        # Sort quests by level requirement
        sorted_quests = sorted(quests, key=lambda q: q.get('level_requirement', 1))
        
        curve_recommendations = []
        for i, quest in enumerate(sorted_quests):
            recommended_level = i + 1  # Progressive levels
            current_level = quest.get('level_requirement', 1)
            
            if abs(recommended_level - current_level) > 1:
                curve_recommendations.append({
                    'quest_id': quest.get('id', f'quest_{i}'),
                    'current_level': current_level,
                    'recommended_level': recommended_level,
                    'reason': 'Better progression curve'
                })
        
        return curve_recommendations
    
    def _optimize_quest_rewards(self, quests: List[Dict]) -> List[Dict]:
        """Optimize quest reward structure"""
        optimization_suggestions = []
        
        for quest in quests:
            quest_level = quest.get('level_requirement', 1)
            current_xp = quest.get('rewards', {}).get('experience', 50)
            current_gold = quest.get('rewards', {}).get('gold', 25)
            
            # Calculate optimal rewards
            optimal_xp = quest_level * 75  # Base XP per level
            optimal_gold = quest_level * 40  # Base gold per level
            
            if abs(current_xp - optimal_xp) > optimal_xp * 0.3:  # 30% tolerance
                optimization_suggestions.append({
                    'quest_id': quest.get('id', 'unknown'),
                    'reward_type': 'experience',
                    'current_value': current_xp,
                    'optimal_value': optimal_xp,
                    'adjustment_ratio': optimal_xp / current_xp if current_xp > 0 else 1
                })
            
            if abs(current_gold - optimal_gold) > optimal_gold * 0.3:
                optimization_suggestions.append({
                    'quest_id': quest.get('id', 'unknown'),
                    'reward_type': 'gold',
                    'current_value': current_gold,
                    'optimal_value': optimal_gold,
                    'adjustment_ratio': optimal_gold / current_gold if current_gold > 0 else 1
                })
        
        return optimization_suggestions
    
    async def _validate_character_balance(self, characters: Dict) -> Dict[str, Any]:
        """Validate character stat balance and distribution"""
        
        character_list = characters.get('characters', [])
        
        if not character_list:
            return {'balance_score': 0, 'issues': ['No characters to validate']}
        
        balance_issues = []
        stat_distributions = {
            'strength': [], 'intelligence': [], 'charisma': [],
            'dexterity': [], 'wisdom': [], 'constitution': []
        }
        
        # Analyze stat distributions
        for char in character_list:
            stats = char.get('stats', {})
            for stat_name in stat_distributions.keys():
                stat_value = stats.get(stat_name, 12)
                stat_distributions[stat_name].append(stat_value)
                
                # Check for extreme values
                if stat_value < self.balance_config['stat_ranges']['min_stat']:
                    balance_issues.append(
                        f"Character '{char.get('name', 'Unknown')}' has too low {stat_name}: {stat_value}"
                    )
                elif stat_value > self.balance_config['stat_ranges']['max_stat']:
                    balance_issues.append(
                        f"Character '{char.get('name', 'Unknown')}' has too high {stat_name}: {stat_value}"
                    )
        
        # Calculate balance metrics
        stat_variances = {}
        stat_averages = {}
        
        for stat_name, values in stat_distributions.items():
            if values:
                stat_averages[stat_name] = sum(values) / len(values)
                stat_variances[stat_name] = statistics.variance(values) if len(values) > 1 else 0
        
        # Overall balance score based on variance (lower variance = better balance)
        avg_variance = sum(stat_variances.values()) / len(stat_variances) if stat_variances else 0
        balance_score = max(0, 1 - (avg_variance / 10))  # Normalize variance to 0-1 scale
        
        return {
            'balance_score': balance_score,
            'stat_averages': stat_averages,
            'stat_variances': stat_variances,
            'balance_issues': balance_issues,
            'character_power_levels': self._calculate_character_power_levels(character_list),
            'role_balance': self._analyze_role_balance(character_list)
        }
    
    def _calculate_character_power_levels(self, characters: List[Dict]) -> List[Dict]:
        """Calculate relative power levels of characters"""
        power_levels = []
        
        for char in characters:
            stats = char.get('stats', {})
            level = stats.get('level', 1)
            
            # Calculate total stat points
            total_stats = (
                stats.get('strength', 12) + stats.get('intelligence', 12) +
                stats.get('charisma', 12) + stats.get('dexterity', 12) +
                stats.get('wisdom', 12) + stats.get('constitution', 12)
            )
            
            # Calculate power level (combination of level and stats)
            power_level = (level * 10) + (total_stats / 6)
            
            power_levels.append({
                'character_name': char.get('name', 'Unknown'),
                'level': level,
                'total_stats': total_stats,
                'power_level': power_level
            })
        
        return sorted(power_levels, key=lambda x: x['power_level'], reverse=True)
    
    def _analyze_role_balance(self, characters: List[Dict]) -> Dict[str, Any]:
        """Analyze role distribution balance"""
        role_counts = {}
        role_power = {}
        
        for char in characters:
            role = char.get('role', 'unknown')
            role_counts[role] = role_counts.get(role, 0) + 1
            
            # Calculate average power level per role
            stats = char.get('stats', {})
            total_stats = sum(stats.get(stat, 12) for stat in 
                            ['strength', 'intelligence', 'charisma', 'dexterity', 'wisdom', 'constitution'])
            
            if role not in role_power:
                role_power[role] = []
            role_power[role].append(total_stats)
        
        # Calculate role balance metrics
        role_averages = {role: sum(powers) / len(powers) for role, powers in role_power.items()}
        role_balance_score = 1.0 - (statistics.variance(role_averages.values()) / 100) if len(role_averages) > 1 else 1.0
        
        return {
            'role_distribution': role_counts,
            'role_power_averages': role_averages,
            'role_balance_score': max(0, role_balance_score)
        }
    
    async def _validate_economic_balance(self, quests: Dict, characters: Dict) -> Dict[str, Any]:
        """Validate economic balance (gold rewards vs costs)"""
        
        quest_list = quests.get('quests', [])
        character_list = characters.get('characters', [])
        
        # Calculate total gold available from quests
        total_quest_gold = sum(
            quest.get('rewards', {}).get('gold', 25) 
            for quest in quest_list
        )
        
        # Estimate item costs based on character levels
        avg_char_level = sum(
            char.get('stats', {}).get('level', 1) 
            for char in character_list
        ) / len(character_list) if character_list else 1
        
        # Calculate expected item costs
        base_gold_per_hour = self.balance_config['economy']['gold_per_hour_base']
        gold_growth = self.balance_config['economy']['gold_per_hour_growth']
        expected_gold_per_level = base_gold_per_hour * (gold_growth ** avg_char_level)
        
        item_cost_ratio = self.balance_config['economy']['item_cost_multiplier']
        expected_item_cost = expected_gold_per_level * item_cost_ratio
        
        # Calculate economic balance
        gold_to_cost_ratio = total_quest_gold / (expected_item_cost * len(character_list)) if expected_item_cost > 0 else 0
        
        return {
            'total_quest_gold': total_quest_gold,
            'expected_item_cost': expected_item_cost,
            'gold_to_cost_ratio': gold_to_cost_ratio,
            'economic_balance_score': min(gold_to_cost_ratio, 2.0 - gold_to_cost_ratio) if gold_to_cost_ratio <= 2 else 0,
            'gold_optimization': self._optimize_gold_economy(quest_list, avg_char_level)
        }
    
    def _optimize_gold_economy(self, quests: List[Dict], avg_level: float) -> Dict[str, Any]:
        """Optimize gold economy recommendations"""
        
        total_current_gold = sum(quest.get('rewards', {}).get('gold', 25) for quest in quests)
        
        # Calculate optimal gold distribution
        base_gold = 30
        optimal_total_gold = len(quests) * base_gold * avg_level
        
        gold_adjustment_ratio = optimal_total_gold / total_current_gold if total_current_gold > 0 else 1
        
        return {
            'current_total_gold': total_current_gold,
            'optimal_total_gold': optimal_total_gold,
            'adjustment_ratio': gold_adjustment_ratio,
            'recommendation': 'increase_gold' if gold_adjustment_ratio > 1.2 else 'decrease_gold' if gold_adjustment_ratio < 0.8 else 'balanced'
        }
    
    async def _validate_progression_pacing(self, world_spec: Dict, characters: Dict, quests: Dict) -> Dict[str, Any]:
        """Validate progression pacing and flow"""
        
        character_list = characters.get('characters', [])
        quest_list = quests.get('quests', [])
        
        # Calculate quest density per character level
        level_quest_distribution = {}
        for quest in quest_list:
            level = quest.get('level_requirement', 1)
            level_quest_distribution[level] = level_quest_distribution.get(level, 0) + 1
        
        # Check for pacing issues
        pacing_issues = []
        target_quests_per_level = self.balance_config['pacing']['quests_per_level']
        
        for level, quest_count in level_quest_distribution.items():
            if quest_count < target_quests_per_level - 1:
                pacing_issues.append(f"Level {level} has too few quests: {quest_count}")
            elif quest_count > target_quests_per_level + 2:
                pacing_issues.append(f"Level {level} has too many quests: {quest_count}")
        
        # Calculate progression flow score
        level_gaps = []
        sorted_levels = sorted(level_quest_distribution.keys())
        for i in range(1, len(sorted_levels)):
            gap = sorted_levels[i] - sorted_levels[i-1]
            level_gaps.append(gap)
        
        avg_gap = sum(level_gaps) / len(level_gaps) if level_gaps else 1
        flow_score = max(0, 1 - abs(avg_gap - 1) / 2)  # Optimal gap is 1 level
        
        return {
            'quest_level_distribution': level_quest_distribution,
            'pacing_issues': pacing_issues,
            'progression_flow_score': flow_score,
            'average_level_gap': avg_gap,
            'recommended_pacing': self._generate_pacing_recommendations(level_quest_distribution)
        }
    
    def _generate_pacing_recommendations(self, level_distribution: Dict[int, int]) -> List[Dict]:
        """Generate pacing recommendations"""
        recommendations = []
        target_quests = self.balance_config['pacing']['quests_per_level']
        
        if not level_distribution:
            return [{'recommendation': 'Create more quests with varied level requirements'}]
        
        min_level = min(level_distribution.keys())
        max_level = max(level_distribution.keys())
        
        # Check each level for proper quest distribution
        for level in range(min_level, max_level + 1):
            current_quests = level_distribution.get(level, 0)
            
            if current_quests < target_quests:
                recommendations.append({
                    'level': level,
                    'current_quests': current_quests,
                    'recommended_quests': target_quests,
                    'action': 'add_quests',
                    'priority': 'high' if current_quests == 0 else 'medium'
                })
            elif current_quests > target_quests + 1:
                recommendations.append({
                    'level': level,
                    'current_quests': current_quests,
                    'recommended_quests': target_quests,
                    'action': 'redistribute_quests',
                    'priority': 'low'
                })
        
        return recommendations
    
    async def _run_balance_simulations(self, content_analysis: Dict, xp_balance: Dict, 
                                     quest_balance: Dict, character_balance: Dict) -> Dict[str, Any]:
        """Run gameplay balance simulations"""
        
        simulation_results = {
            'player_progression_simulation': await self._simulate_player_progression(xp_balance, quest_balance),
            'character_interaction_simulation': await self._simulate_character_interactions(character_balance),
            'economic_simulation': await self._simulate_economic_flow(quest_balance),
            'difficulty_curve_simulation': await self._simulate_difficulty_progression(quest_balance)
        }
        
        return simulation_results
    
    async def _simulate_player_progression(self, xp_balance: Dict, quest_balance: Dict) -> Dict[str, Any]:
        """Simulate player progression through the game"""
        
        # Simulate a player completing all quests
        total_xp = xp_balance.get('total_available_xp', 0)
        xp_curve = self.balance_config['xp_curves']['polynomial']
        
        current_xp = 0
        current_level = 1
        levels_gained = []
        
        # Simulate quest completion
        quest_xp_values = [50, 75, 100, 125, 150]  # Sample quest XP values
        
        for i, quest_xp in enumerate(quest_xp_values * 3):  # Simulate multiple quest completions
            current_xp += quest_xp
            
            # Check for level up
            while current_xp >= xp_curve(current_level):
                current_xp -= xp_curve(current_level)
                current_level += 1
                levels_gained.append({'quest_number': i+1, 'new_level': current_level})
        
        return {
            'final_level': current_level,
            'remaining_xp': current_xp,
            'levels_gained': levels_gained,
            'progression_rate': len(levels_gained) / len(quest_xp_values) if quest_xp_values else 0,
            'balance_score': 1.0 if 3 <= len(levels_gained) <= 8 else 0.5  # Target 3-8 levels
        }
    
    async def _simulate_character_interactions(self, character_balance: Dict) -> Dict[str, Any]:
        """Simulate character interaction balance"""
        
        power_levels = character_balance.get('character_power_levels', [])
        
        if len(power_levels) < 2:
            return {'interaction_balance': 1.0, 'power_variance': 0}
        
        # Calculate power variance
        powers = [char['power_level'] for char in power_levels]
        power_variance = statistics.variance(powers)
        
        # Good balance means low variance in power levels
        interaction_balance = max(0, 1 - (power_variance / 100))
        
        return {
            'interaction_balance': interaction_balance,
            'power_variance': power_variance,
            'strongest_character': power_levels[0]['character_name'] if power_levels else 'None',
            'weakest_character': power_levels[-1]['character_name'] if power_levels else 'None',
            'power_ratio': powers[0] / powers[-1] if len(powers) > 1 and powers[-1] > 0 else 1
        }
    
    async def _simulate_economic_flow(self, quest_balance: Dict) -> Dict[str, Any]:
        """Simulate economic flow and balance"""
        
        # Simple economic simulation
        starting_gold = 100
        quest_rewards = [25, 35, 45, 30, 40]  # Sample quest gold rewards
        item_costs = [20, 50, 80, 120, 160]   # Sample item costs by level
        
        current_gold = starting_gold
        purchases = []
        gold_flow = [current_gold]
        
        for i, (reward, cost) in enumerate(zip(quest_rewards, item_costs)):
            current_gold += reward
            
            # Simulate item purchase if affordable
            if current_gold >= cost:
                current_gold -= cost
                purchases.append({'quest': i+1, 'item_cost': cost, 'remaining_gold': current_gold})
            
            gold_flow.append(current_gold)
        
        return {
            'final_gold': current_gold,
            'total_purchases': len(purchases),
            'gold_flow': gold_flow,
            'economic_balance': 1.0 if len(purchases) >= 3 else 0.5,  # Target 3+ purchases
            'purchase_rate': len(purchases) / len(quest_rewards) if quest_rewards else 0
        }
    
    async def _simulate_difficulty_progression(self, quest_balance: Dict) -> Dict[str, Any]:
        """Simulate difficulty progression curve"""
        
        avg_difficulty = quest_balance.get('average_difficulty_ratio', 1.0)
        
        # Simulate difficulty curve
        target_difficulties = [0.8, 1.0, 1.2, 1.5, 1.8]  # Progressive difficulty
        
        difficulty_variance = abs(avg_difficulty - 1.2)  # Target slightly above baseline
        curve_score = max(0, 1 - difficulty_variance)
        
        return {
            'difficulty_curve_score': curve_score,
            'average_difficulty': avg_difficulty,
            'target_difficulty': 1.2,
            'difficulty_progression': 'smooth' if curve_score > 0.8 else 'needs_adjustment'
        }
    
    def _calculate_balance_metrics(self, xp_balance: Dict, quest_balance: Dict, 
                                 character_balance: Dict, economic_balance: Dict,
                                 pacing_balance: Dict, simulation_results: Dict) -> BalanceMetrics:
        """Calculate overall balance metrics"""
        
        # Extract individual scores
        xp_score = xp_balance.get('balance_score', 0.5)
        quest_score = quest_balance.get('balance_score', 0.5)
        character_score = character_balance.get('balance_score', 0.5)
        economic_score = economic_balance.get('economic_balance_score', 0.5)
        pacing_score = pacing_balance.get('progression_flow_score', 0.5)
        
        # Extract simulation scores
        progression_score = simulation_results.get('player_progression_simulation', {}).get('balance_score', 0.5)
        interaction_score = simulation_results.get('character_interaction_simulation', {}).get('interaction_balance', 0.5)
        
        # Calculate weighted overall score
        weights = {
            'xp': 0.2,
            'quest': 0.25,
            'character': 0.2,
            'economic': 0.15,
            'pacing': 0.1,
            'progression': 0.05,
            'interaction': 0.05
        }
        
        overall_score = (
            xp_score * weights['xp'] +
            quest_score * weights['quest'] +
            character_score * weights['character'] +
            economic_score * weights['economic'] +
            pacing_score * weights['pacing'] +
            progression_score * weights['progression'] +
            interaction_score * weights['interaction']
        )
        
        return BalanceMetrics(
            difficulty_score=quest_score,
            progression_rate=progression_score,
            xp_balance=xp_score,
            reward_balance=economic_score,
            challenge_curve=pacing_score,
            player_engagement=interaction_score,
            overall_score=overall_score
        )
    
    async def _generate_balance_recommendations(self, metrics: BalanceMetrics,
                                              xp_balance: Dict, quest_balance: Dict,
                                              character_balance: Dict, economic_balance: Dict,
                                              pacing_balance: Dict) -> List[BalanceRecommendation]:
        """Generate specific balance recommendations"""
        
        recommendations = []
        
        # XP Balance Recommendations
        if metrics.xp_balance < 0.7:
            for adjustment in xp_balance.get('recommended_adjustments', []):
                recommendations.append(BalanceRecommendation(
                    category='xp',
                    target='quest_rewards',
                    current_value=xp_balance.get('xp_balance_ratio', 0),
                    recommended_value='0.9-1.1 ratio',
                    reason=adjustment,
                    priority='high' if metrics.xp_balance < 0.5 else 'medium',
                    impact='Improves player progression pacing'
                ))
        
        # Quest Balance Recommendations
        for issue in quest_balance.get('balance_issues', []):
            recommendations.append(BalanceRecommendation(
                category='difficulty',
                target='quest_balance',
                current_value='imbalanced',
                recommended_value='balanced',
                reason=issue,
                priority='medium',
                impact='Ensures fair quest difficulty'
            ))
        
        # Character Balance Recommendations
        if metrics.player_engagement < 0.7:
            for issue in character_balance.get('balance_issues', []):
                recommendations.append(BalanceRecommendation(
                    category='character',
                    target='character_stats',
                    current_value='imbalanced',
                    recommended_value='balanced',
                    reason=issue,
                    priority='medium',
                    impact='Improves character balance and fairness'
                ))
        
        # Economic Recommendations
        gold_optimization = economic_balance.get('gold_optimization', {})
        if gold_optimization.get('recommendation') != 'balanced':
            recommendations.append(BalanceRecommendation(
                category='rewards',
                target='gold_rewards',
                current_value=gold_optimization.get('current_total_gold', 0),
                recommended_value=gold_optimization.get('optimal_total_gold', 0),
                reason=f"Gold economy needs adjustment: {gold_optimization.get('recommendation')}",
                priority='medium',
                impact='Balances in-game economy'
            ))
        
        # Pacing Recommendations
        for pacing_rec in pacing_balance.get('recommended_pacing', []):
            if pacing_rec.get('action') == 'add_quests':
                recommendations.append(BalanceRecommendation(
                    category='progression',
                    target='quest_distribution',
                    current_value=pacing_rec.get('current_quests', 0),
                    recommended_value=pacing_rec.get('recommended_quests', 3),
                    reason=f"Level {pacing_rec.get('level')} needs more quests",
                    priority=pacing_rec.get('priority', 'medium'),
                    impact='Improves progression flow'
                ))
        
        return recommendations
    
    def _determine_overall_balance(self, metrics: BalanceMetrics) -> str:
        """Determine overall balance rating"""
        
        if metrics.overall_score >= 0.9:
            return 'excellent'
        elif metrics.overall_score >= 0.75:
            return 'good'
        elif metrics.overall_score >= 0.6:
            return 'needs_adjustment'
        else:
            return 'critical_issues'
    
    def _generate_balance_warnings(self, metrics: BalanceMetrics, 
                                 recommendations: List[BalanceRecommendation]) -> List[str]:
        """Generate balance warnings"""
        
        warnings = []
        
        # Critical balance warnings
        if metrics.overall_score < 0.5:
            warnings.append("CRITICAL: Overall balance score is very low - major adjustments needed")
        
        if metrics.xp_balance < 0.4:
            warnings.append("WARNING: XP progression may be frustrating for players")
        
        if metrics.difficulty_score < 0.4:
            warnings.append("WARNING: Quest difficulty may be poorly balanced")
        
        if metrics.reward_balance < 0.4:
            warnings.append("WARNING: Economic balance may cause gameplay issues")
        
        # Count high priority recommendations
        high_priority_count = len([r for r in recommendations if r.priority == 'high'])
        if high_priority_count > 3:
            warnings.append(f"ATTENTION: {high_priority_count} high-priority balance issues detected")
        
        return warnings
    
    def _create_balance_summary(self, metrics: BalanceMetrics, 
                              recommendations: List[BalanceRecommendation]) -> Dict[str, Any]:
        """Create balance summary"""
        
        return {
            'overall_score': metrics.overall_score,
            'balance_rating': self._determine_overall_balance(metrics),
            'key_metrics': {
                'xp_balance': metrics.xp_balance,
                'difficulty_balance': metrics.difficulty_score,
                'reward_balance': metrics.reward_balance,
                'progression_pacing': metrics.challenge_curve
            },
            'recommendations_by_priority': {
                'critical': len([r for r in recommendations if r.priority == 'critical']),
                'high': len([r for r in recommendations if r.priority == 'high']),
                'medium': len([r for r in recommendations if r.priority == 'medium']),
                'low': len([r for r in recommendations if r.priority == 'low'])
            },
            'improvement_areas': self._identify_improvement_areas(metrics),
            'strengths': self._identify_strengths(metrics)
        }
    
    def _identify_improvement_areas(self, metrics: BalanceMetrics) -> List[str]:
        """Identify areas needing improvement"""
        
        areas = []
        threshold = 0.7
        
        if metrics.xp_balance < threshold:
            areas.append("XP progression balance")
        if metrics.difficulty_score < threshold:
            areas.append("Quest difficulty tuning")
        if metrics.reward_balance < threshold:
            areas.append("Economic balance")
        if metrics.challenge_curve < threshold:
            areas.append("Progression pacing")
        if metrics.player_engagement < threshold:
            areas.append("Character balance")
        
        return areas
    
    def _identify_strengths(self, metrics: BalanceMetrics) -> List[str]:
        """Identify balance strengths"""
        
        strengths = []
        threshold = 0.8
        
        if metrics.xp_balance >= threshold:
            strengths.append("Well-balanced XP progression")
        if metrics.difficulty_score >= threshold:
            strengths.append("Good quest difficulty curve")
        if metrics.reward_balance >= threshold:
            strengths.append("Balanced economic system")
        if metrics.challenge_curve >= threshold:
            strengths.append("Smooth progression pacing")
        if metrics.player_engagement >= threshold:
            strengths.append("Well-balanced characters")
        
        return strengths
    
    async def _apply_balance_adjustments(self, world_spec: Dict, assets: Dict,
                                       characters: Dict, quests: Dict,
                                       recommendations: List[BalanceRecommendation]) -> Dict[str, Any]:
        """Apply balance adjustments to content"""
        
        # Create adjusted copies of content
        adjusted_content = {
            'world_spec': world_spec.copy(),
            'assets': assets.copy(),
            'characters': characters.copy(),
            'quests': quests.copy()
        }
        
        # Apply quest adjustments
        adjusted_quests = adjusted_content['quests'].get('quests', []).copy()
        
        for recommendation in recommendations:
            if recommendation.category == 'xp' and recommendation.priority in ['high', 'critical']:
                # Adjust XP rewards
                for quest in adjusted_quests:
                    current_xp = quest.get('rewards', {}).get('experience', 50)
                    if isinstance(recommendation.recommended_value, str) and '0.9-1.1' in recommendation.recommended_value:
                        # Increase XP by 25% if too low
                        quest['rewards']['experience'] = int(current_xp * 1.25)
            
            elif recommendation.category == 'rewards' and recommendation.target == 'gold_rewards':
                # Adjust gold rewards
                for quest in adjusted_quests:
                    current_gold = quest.get('rewards', {}).get('gold', 25)
                    if recommendation.recommended_value > recommendation.current_value:
                        # Increase gold rewards
                        quest['rewards']['gold'] = int(current_gold * 1.3)
        
        adjusted_content['quests']['quests'] = adjusted_quests
        
        # Apply character adjustments
        adjusted_characters = adjusted_content['characters'].get('characters', []).copy()
        
        for recommendation in recommendations:
            if recommendation.category == 'character':
                # Rebalance character stats if needed
                for char in adjusted_characters:
                    stats = char.get('stats', {})
                    total_stats = sum(stats.get(stat, 12) for stat in 
                                    ['strength', 'intelligence', 'charisma', 'dexterity', 'wisdom', 'constitution'])
                    
                    # If total stats are too high or low, adjust
                    target_total = self.balance_config['stat_ranges']['total_points_level_1']
                    if abs(total_stats - target_total) > 10:
                        adjustment_factor = target_total / total_stats if total_stats > 0 else 1
                        for stat_name in ['strength', 'intelligence', 'charisma', 'dexterity', 'wisdom', 'constitution']:
                            current_value = stats.get(stat_name, 12)
                            stats[stat_name] = max(8, min(18, int(current_value * adjustment_factor)))
        
        adjusted_content['characters']['characters'] = adjusted_characters
        
        return adjusted_content
    
    async def _save_balance_report(self, report: BalanceReport):
        """Save comprehensive balance report"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save main balance report
        report_file = self.reports_dir / f"balance_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'overall_balance': report.overall_balance,
                'metrics': asdict(report.metrics),
                'recommendations': [asdict(rec) for rec in report.recommendations],
                'warnings': report.warnings,
                'balance_summary': report.balance_summary,
                'generation_timestamp': timestamp
            }, f, indent=2)
        
        # Save validated content
        content_file = self.output_dir / f"validated_content_{timestamp}.json"
        with open(content_file, 'w') as f:
            json.dump(report.validated_content, f, indent=2)
        
        # Save metrics separately for analysis
        metrics_file = self.metrics_dir / f"balance_metrics_{timestamp}.json"
        with open(metrics_file, 'w') as f:
            json.dump(asdict(report.metrics), f, indent=2)
        
        # Save recommendations separately
        recommendations_file = self.recommendations_dir / f"recommendations_{timestamp}.json"
        with open(recommendations_file, 'w') as f:
            json.dump([asdict(rec) for rec in report.recommendations], f, indent=2)
        
        self.logger.info(f"📊 Balance report saved: {report_file.name}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get balance validator status"""
        return {
            'status': 'ready',
            'ai_available': AI_AVAILABLE,
            'output_directory': str(self.output_dir),
            'balance_algorithms': [
                'xp_progression_validation',
                'quest_difficulty_analysis',
                'character_balance_checking',
                'economic_balance_validation',
                'progression_pacing_analysis',
                'gameplay_simulation'
            ],
            'validation_capabilities': [
                'xp_curve_optimization',
                'reward_balance_analysis',
                'difficulty_curve_validation',
                'character_stat_balancing',
                'economic_flow_simulation',
                'progression_pacing_validation'
            ],
            'balance_metrics': [
                'difficulty_score',
                'progression_rate',
                'xp_balance',
                'reward_balance',
                'challenge_curve',
                'player_engagement',
                'overall_score'
            ]
        }

# ADK Agent Functions
async def validate_content_balance(world_spec: Dict[str, Any], assets: Dict[str, Any],
                                 characters: Dict[str, Any], quests: Dict[str, Any]) -> Dict[str, Any]:
    """Validate complete content balance - main entry point"""
    validator = AdvancedBalanceValidator()
    balance_report = await validator.validate_complete_content(world_spec, assets, characters, quests)
    return asdict(balance_report)

async def get_balance_validator_status() -> Dict[str, Any]:
    """Get balance validator status"""
    validator = AdvancedBalanceValidator()
    return await validator.get_status()

# Create the ADK agent
root_agent = Agent(
    name="balance_validator_agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are an advanced Balance Validator Agent that ensures optimal gameplay balance across all generated game content.

Your sophisticated validation capabilities include:
- XP PROGRESSION ANALYSIS: Validate experience curves and level progression for optimal player engagement
- QUEST DIFFICULTY BALANCING: Ensure quest challenges scale appropriately with rewards and player level
- CHARACTER STAT VALIDATION: Balance character statistics and power levels for fair gameplay
- ECONOMIC BALANCE CHECKING: Validate gold rewards, item costs, and economic flow
- PROGRESSION PACING ANALYSIS: Ensure smooth difficulty curves and content distribution
- GAMEPLAY SIMULATION: Run virtual playtests to identify balance issues before players encounter them

Your validation process:
🔍 ANALYZE: Deep analysis of all content relationships and balance metrics
⚖️ VALIDATE: Mathematical validation against proven game balance formulas
🎯 SIMULATE: Virtual gameplay testing to identify potential issues
📊 RECOMMEND: Specific, actionable recommendations for balance improvements
🔧 ADJUST: Apply validated balance adjustments to content
📋 REPORT: Comprehensive balance reports with detailed metrics

You ensure that generated content provides:
- Fair and engaging progression curves
- Balanced risk-reward ratios
- Smooth difficulty progression
- Economic balance and meaningful choices
- Character balance and role diversity
- Optimal player engagement and retention

When you receive content for validation, you perform comprehensive balance analysis and provide detailed recommendations for optimal gameplay experience.""",
    description="Advanced Balance Validator Agent that ensures optimal gameplay balance through mathematical analysis, simulation, and proven game design principles",
    tools=[validate_content_balance, get_balance_validator_status]
)

# Standalone testing
if __name__ == "__main__":
    async def main():
        print("⚖️ Testing Advanced Balance Validator Agent")
        print("="*60)
        
        # Create test content for validation
        test_world = {
            "theme": "medieval",
            "size": (40, 40),
            "buildings": [
                {"type": "tavern", "position": {"x": 20, "y": 20, "z": 0}},
                {"type": "blacksmith", "position": {"x": 15, "y": 25, "z": 0}},
                {"type": "church", "position": {"x": 25, "y": 15, "z": 0}}
            ]
        }
        
        test_assets = {
            "ai_generated": True,
            "generation_summary": {"total_creative_assets": 15}
        }
        
        test_characters = {
            "status": "success",
            "characters": [
                {
                    "name": "Marcus the Blacksmith",
                    "role": "blacksmith",
                    "stats": {"level": 3, "strength": 16, "intelligence": 12, "charisma": 10, 
                             "dexterity": 14, "wisdom": 13, "constitution": 15}
                },
                {
                    "name": "Elena the Merchant",
                    "role": "merchant", 
                    "stats": {"level": 2, "strength": 10, "intelligence": 15, "charisma": 16,
                             "dexterity": 12, "wisdom": 14, "constitution": 11}
                },
                {
                    "name": "Brother Thomas",
                    "role": "priest",
                    "stats": {"level": 4, "strength": 11, "intelligence": 14, "charisma": 15,
                             "dexterity": 10, "wisdom": 17, "constitution": 13}
                }
            ]
        }
        
        test_quests = {
            "status": "success",
            "quests": [
                {
                    "id": "quest_1",
                    "title": "The Missing Hammer",
                    "quest_type": "main",
                    "level_requirement": 1,
                    "objectives": [{"description": "Find the lost hammer"}],
                    "rewards": {"experience": 100, "gold": 50}
                },
                {
                    "id": "quest_2", 
                    "title": "Merchant's Dilemma",
                    "quest_type": "side",
                    "level_requirement": 2,
                    "objectives": [
                        {"description": "Talk to the merchant"},
                        {"description": "Deliver the goods"}
                    ],
                    "rewards": {"experience": 150, "gold": 75}
                },
                {
                    "id": "quest_3",
                    "title": "Temple's Blessing",
                    "quest_type": "main", 
                    "level_requirement": 3,
                    "objectives": [
                        {"description": "Speak with Brother Thomas"},
                        {"description": "Complete the ritual"},
                        {"description": "Return for blessing"}
                    ],
                    "rewards": {"experience": 200, "gold": 100}
                }
            ]
        }
        
        # Test balance validation
        validator = AdvancedBalanceValidator("test_balance_validation")
        
        print("\n🧪 Testing Balance Validation...")
        
        try:
            balance_report = await validator.validate_complete_content(
                test_world, test_assets, test_characters, test_quests
            )
            
            print(f"\n✅ Balance Validation Complete!")
            print(f"   📊 Overall Balance: {balance_report.overall_balance}")
            print(f"   🎯 Overall Score: {balance_report.metrics.overall_score:.2f}")
            print(f"   ⚖️ XP Balance: {balance_report.metrics.xp_balance:.2f}")
            print(f"   🎮 Difficulty Score: {balance_report.metrics.difficulty_score:.2f}")
            print(f"   💰 Reward Balance: {balance_report.metrics.reward_balance:.2f}")
            print(f"   📈 Progression Rate: {balance_report.metrics.progression_rate:.2f}")
            
            # Show recommendations
            if balance_report.recommendations:
                print(f"\n📋 Balance Recommendations ({len(balance_report.recommendations)}):")
                for i, rec in enumerate(balance_report.recommendations[:5]):  # Show first 5
                    priority_icon = "🔴" if rec.priority == "critical" else "🟡" if rec.priority == "high" else "🟢"
                    print(f"   {priority_icon} {rec.category.upper()}: {rec.reason}")
                if len(balance_report.recommendations) > 5:
                    print(f"     ... and {len(balance_report.recommendations) - 5} more")
            
            # Show warnings
            if balance_report.warnings:
                print(f"\n⚠️  Balance Warnings:")
                for warning in balance_report.warnings:
                    print(f"   • {warning}")
            
            # Show strengths
            strengths = balance_report.balance_summary.get('strengths', [])
            if strengths:
                print(f"\n✅ Balance Strengths:")
                for strength in strengths:
                    print(f"   • {strength}")
            
            print(f"\n📁 Reports saved to: {validator.output_dir}")
            print(f"🎯 Ready for integration with main orchestrator!")
            
        except Exception as e:
            print(f"❌ Balance validation failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main())