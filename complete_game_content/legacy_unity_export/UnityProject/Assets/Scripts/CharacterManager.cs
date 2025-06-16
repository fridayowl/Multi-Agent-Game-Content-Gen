using System.Collections.Generic;
using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Manages all NPCs and character interactions
    /// </summary>
    public class CharacterManager : MonoBehaviour
    {
        [Header("Characters")]
        public List<NPCController> npcs = new List<NPCController>();
        
        [Header("Dialogue System")]
        public GameObject dialogueUI;
        public bool isDialogueActive = false;
        
        private static CharacterManager _instance;
        public static CharacterManager Instance => _instance;
        
        void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        public void Initialize()
        {
            Debug.Log("Initializing Character Manager...");
            
            // Find all NPCs in scene
            RegisterNPCs();
            
            // Setup relationships
            SetupRelationships();
        }
        
        void RegisterNPCs()
        {
            NPCController[] foundNPCs = FindObjectsOfType<NPCController>();
            npcs.AddRange(foundNPCs);
            
            Debug.Log($"Registered {npcs.Count} NPCs");
        }
        
        void SetupRelationships()
        {
            // Setup NPC relationships based on generated data
            foreach (var npc in npcs)
            {
                npc.InitializeRelationships();
            }
        }
        
        public NPCController FindNPCByName(string npcName)
        {
            foreach (var npc in npcs)
            {
                if (npc.characterName == npcName)
                {
                    return npc;
                }
            }
            return null;
        }
        
        public void StartDialogue(NPCController npc)
        {
            if (isDialogueActive) return;
            
            isDialogueActive = true;
            Debug.Log($"Starting dialogue with {npc.characterName}");
            
            // Implement dialogue system
            if (dialogueUI != null)
            {
                dialogueUI.SetActive(true);
                // Setup dialogue content
            }
        }
        
        public void EndDialogue()
        {
            isDialogueActive = false;
            
            if (dialogueUI != null)
            {
                dialogueUI.SetActive(false);
            }
        }
    }
}