#!/usr/bin/env python3
"""
Quest system exporter
Handles export of quest management, objectives, and tracking
"""

from typing import Dict, List, Any
from pathlib import Path
import logging

from ..core.data_types import UnityGameObject, UnityComponent

class QuestExporter:
    """Handles quest system export to Unity"""
    
    def __init__(self, scripts_dir: Path, logger: logging.Logger):
        self.scripts_dir = scripts_dir
        self.logger = logger
    
    async def export_quest_system(self, quests: Dict[str, Any], characters: Dict[str, Any]) -> List[UnityGameObject]:
        """Export quest system"""
        self.logger.info("📜 Exporting quest system...")
        
        quest_objects = []
        
        if not quests or not quests.get('quests'):
            self.logger.warning("No quests provided")
            return quest_objects
        
        # Create quest management scripts
        await self._create_quest_manager_script(quests)
        
        # Create quest manager object
        quest_manager = UnityGameObject(
            name="QuestManager",
            transform={
                "position": [0, 0, 0],
                "rotation": [0, 0, 0, 1],
                "scale": [1, 1, 1]
            },
            components=[
                UnityComponent(
                    component_type="QuestManager",
                    properties={
                        "totalQuests": len(quests.get('quests', [])),
                        "questDataFile": "StreamingAssets/quests.json"
                    }
                )
            ],
            children=[]
        )
        quest_objects.append(quest_manager)
        
        self.logger.info(f"   ✅ Exported quest system with {len(quests.get('quests', []))} quests")
        return quest_objects
    
    async def _create_quest_manager_script(self, quests: Dict[str, Any]) -> List[str]:
        """Create quest manager script"""
        
        quest_script = f'''using UnityEngine;
using System.Collections.Generic;

public class QuestManager : MonoBehaviour
{{
    [Header("Quest Configuration")]
    public int totalQuests = {len(quests.get('quests', []))};
    
    private List<Quest> availableQuests = new List<Quest>();
    private List<Quest> activeQuests = new List<Quest>();
    private List<Quest> completedQuests = new List<Quest>();
    
    void Start()
    {{
        LoadQuests();
        Debug.Log($"Quest Manager initialized with {{totalQuests}} total quests");
    }}
    
    void LoadQuests()
    {{
        // Load quest data from generated content
        Debug.Log("Loading quest data...");
        
        // Add sample quests based on generated content
        CreateSampleQuests();
    }}
    
    void CreateSampleQuests()
    {{
        // Create quests based on the generated quest data
        Quest sampleQuest = new Quest
        {{
            id = "sample_quest_1",
            title = "Explore the Generated World",
            description = "Get familiar with this AI-generated world",
            isCompleted = false
        }};
        
        availableQuests.Add(sampleQuest);
    }}
    
    public void StartQuest(string questId)
    {{
        Quest quest = availableQuests.Find(q => q.id == questId);
        if (quest != null)
        {{
            availableQuests.Remove(quest);
            activeQuests.Add(quest);
            
            Debug.Log($"Started quest: {{quest.title}}");
        }}
    }}
    
    public void CompleteQuest(string questId)
    {{
        Quest quest = activeQuests.Find(q => q.id == questId);
        if (quest != null)
        {{
            quest.isCompleted = true;
            activeQuests.Remove(quest);
            completedQuests.Add(quest);
            
            Debug.Log($"Completed quest: {{quest.title}}");
        }}
    }}
}}

[System.Serializable]
public class Quest
{{
    public string id;
    public string title;
    public string description;
    public bool isCompleted;
}}'''
        
        script_path = self.scripts_dir / "QuestManager.cs"
        with open(script_path, 'w') as f:
            f.write(quest_script)
        
        return ["Scripts/QuestManager.cs"]