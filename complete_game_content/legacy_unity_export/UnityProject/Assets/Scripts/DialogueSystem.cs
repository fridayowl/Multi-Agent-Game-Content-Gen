using System.Collections.Generic;
using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Handles dialogue interactions and conversation trees
    /// </summary>
    public class DialogueSystem : MonoBehaviour
    {
        [Header("Dialogue UI")]
        public GameObject dialoguePanel;
        public UnityEngine.UI.Text npcNameText;
        public UnityEngine.UI.Text dialogueText;
        public UnityEngine.UI.Button[] responseButtons;
        
        [Header("Current Dialogue")]
        public NPCController currentNPC;
        public DialogueNode currentNode;
        
        private static DialogueSystem _instance;
        public static DialogueSystem Instance => _instance;
        
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
        
        public void StartDialogue(NPCController npc)
        {
            currentNPC = npc;
            
            if (dialoguePanel != null)
            {
                dialoguePanel.SetActive(true);
            }
            
            if (npcNameText != null)
            {
                npcNameText.text = npc.characterName;
            }
            
            // Show greeting
            ShowDialogue(npc.GetGreeting());
        }
        
        public void EndDialogue()
        {
            if (currentNPC != null)
            {
                string farewell = currentNPC.GetFarewell();
                ShowDialogue(farewell);
            }
            
            if (dialoguePanel != null)
            {
                dialoguePanel.SetActive(false);
            }
            
            currentNPC = null;
            currentNode = null;
        }
        
        void ShowDialogue(string text)
        {
            if (dialogueText != null)
            {
                dialogueText.text = text;
            }
            
            // Setup response buttons
            SetupResponseButtons();
        }
        
        void SetupResponseButtons()
        {
            // Hide all buttons first
            foreach (var button in responseButtons)
            {
                if (button != null)
                {
                    button.gameObject.SetActive(false);
                }
            }
            
            // Show basic responses
            if (responseButtons.Length > 0 && responseButtons[0] != null)
            {
                responseButtons[0].gameObject.SetActive(true);
                responseButtons[0].GetComponentInChildren<UnityEngine.UI.Text>().text = "Continue";
                responseButtons[0].onClick.RemoveAllListeners();
                responseButtons[0].onClick.AddListener(() => OnResponseSelected(0));
            }
            
            if (responseButtons.Length > 1 && responseButtons[1] != null)
            {
                responseButtons[1].gameObject.SetActive(true);
                responseButtons[1].GetComponentInChildren<UnityEngine.UI.Text>().text = "Goodbye";
                responseButtons[1].onClick.RemoveAllListeners();
                responseButtons[1].onClick.AddListener(() => EndDialogue());
            }
        }
        
        public void OnResponseSelected(int responseIndex)
        {
            Debug.Log($"Selected response: {responseIndex}");
            
            // Handle response logic
            if (responseIndex == 0)
            {
                // Continue conversation
                if (currentNPC != null)
                {
                    ShowDialogue($"That's interesting! I'm {currentNPC.characterRole} here in town.");
                }
            }
        }
    }
    
    [System.Serializable]
    public class DialogueNode
    {
        public string nodeId;
        public string text;
        public List<DialogueResponse> responses;
    }
    
    [System.Serializable]
    public class DialogueResponse
    {
        public string text;
        public string nextNodeId;
        public bool endsDialogue;
    }
}