#!/usr/bin/env python3
"""
Character system exporter
Handles export of NPCs, dialogue systems, and character interactions
"""

from typing import Dict, List, Any
from pathlib import Path
import logging

from ..core.data_types import UnityGameObject, UnityComponent

class CharacterExporter:
    """Handles character system export to Unity"""
    
    def __init__(self, scripts_dir: Path, logger: logging.Logger):
        self.scripts_dir = scripts_dir
        self.logger = logger
    
    async def export_character_system(self, characters: Dict[str, Any]) -> List[UnityGameObject]:
        """Export character system"""
        self.logger.info("👥 Exporting character system...")
        
        character_objects = []
        
        if not characters or not characters.get('characters'):
            self.logger.warning("No characters provided")
            return character_objects
        
        # Create NPC management scripts
        await self._create_npc_scripts()
        await self._create_dialogue_system()
        
        # Create character objects
        for char in characters.get('characters', []):
            char_obj = UnityGameObject(
                name=f"NPC_{char.get('name', 'Unknown')}",
                transform={
                    "position": char.get('position', [0, 0, 0]),
                    "rotation": [0, 0, 0, 1],
                    "scale": [1, 1, 1]
                },
                components=[
                    UnityComponent(
                        component_type="NPCController",
                        properties={
                            "characterName": char.get('name', ''),
                            "characterRole": char.get('role', ''),
                            "personality": char.get('personality', {}),
                            "dialogueId": char.get('id', '')
                        }
                    ),
                    UnityComponent(
                        component_type="SphereCollider",
                        properties={"radius": 2.0, "isTrigger": True}
                    )
                ],
                children=[]
            )
            character_objects.append(char_obj)
        
        self.logger.info(f"   ✅ Exported {len(character_objects)} characters")
        return character_objects
    
    async def _create_npc_scripts(self) -> List[str]:
        """Create NPC controller scripts"""
        
        npc_script = '''using UnityEngine;
using System.Collections;

public class NPCController : MonoBehaviour
{
    [Header("Character Info")]
    public string characterName = "";
    public string characterRole = "";
    public string dialogueId = "";
    
    [Header("Interaction")]
    public float interactionRange = 2f;
    public KeyCode interactionKey = KeyCode.E;
    
    private bool playerInRange = false;
    private GameObject player;
    
    void Start()
    {
        player = GameObject.FindGameObjectWithTag("Player");
    }
    
    void Update()
    {
        CheckPlayerInteraction();
    }
    
    void CheckPlayerInteraction()
    {
        if (playerInRange && Input.GetKeyDown(interactionKey))
        {
            StartDialogue();
        }
    }
    
    void OnTriggerEnter(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = true;
            // Show interaction prompt
            Debug.Log($"Press {interactionKey} to talk to {characterName}");
        }
    }
    
    void OnTriggerExit(Collider other)
    {
        if (other.CompareTag("Player"))
        {
            playerInRange = false;
        }
    }
    
    void StartDialogue()
    {
        Debug.Log($"Starting dialogue with {characterName} ({characterRole})");
        
        DialogueSystem dialogueSystem = FindObjectOfType<DialogueSystem>();
        if (dialogueSystem != null)
        {
            dialogueSystem.StartDialogue(dialogueId);
        }
    }
}'''
        
        script_path = self.scripts_dir / "NPCController.cs"
        with open(script_path, 'w') as f:
            f.write(npc_script)
        
        return ["Scripts/NPCController.cs"]
    
    async def _create_dialogue_system(self) -> List[str]:
        """Create dialogue system script"""
        
        dialogue_script = '''using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

public class DialogueSystem : MonoBehaviour
{
    [Header("UI References")]
    public GameObject dialoguePanel;
    public Text speakerNameText;
    public Text dialogueText;
    public Button[] responseButtons;
    
    private Dictionary<string, DialogueData> dialogues = new Dictionary<string, DialogueData>();
    private DialogueData currentDialogue;
    private string currentNodeId;
    
    void Start()
    {
        LoadDialogues();
        if (dialoguePanel != null)
            dialoguePanel.SetActive(false);
    }
    
    void LoadDialogues()
    {
        // In a real implementation, this would load from JSON files
        Debug.Log("Loading dialogue data...");
    }
    
    public void StartDialogue(string dialogueId)
    {
        if (dialogues.ContainsKey(dialogueId))
        {
            currentDialogue = dialogues[dialogueId];
            currentNodeId = "start";
            
            if (dialoguePanel != null)
                dialoguePanel.SetActive(true);
                
            DisplayCurrentNode();
        }
        else
        {
            Debug.Log($"No dialogue found for ID: {dialogueId}");
        }
    }
    
    void DisplayCurrentNode()
    {
        if (currentDialogue == null) return;
        
        // Display dialogue text and options
        if (speakerNameText != null)
            speakerNameText.text = currentDialogue.speakerName;
            
        if (dialogueText != null)
            dialogueText.text = "Hello! I'm here in this generated world.";
    }
    
    public void EndDialogue()
    {
        if (dialoguePanel != null)
            dialoguePanel.SetActive(false);
            
        currentDialogue = null;
        currentNodeId = "";
    }
}

[System.Serializable]
public class DialogueData
{
    public string speakerName;
    public Dictionary<string, DialogueNode> nodes;
}

[System.Serializable]  
public class DialogueNode
{
    public string text;
    public DialogueResponse[] responses;
}

[System.Serializable]
public class DialogueResponse
{
    public string text;
    public string nextNodeId;
    public bool endsDialogue;
}'''
        
        script_path = self.scripts_dir / "DialogueSystem.cs"
        with open(script_path, 'w') as f:
            f.write(dialogue_script)
        
        return ["Scripts/DialogueSystem.cs"]