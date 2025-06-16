using UnityEngine;
using UnityEngine.UI;

namespace GeneratedGame
{
    /// <summary>
    /// Manages all UI elements and interactions
    /// </summary>
    public class UIManager : MonoBehaviour
    {
        [Header("UI Panels")]
        public GameObject pauseMenu;
        public GameObject questLogPanel;
        public GameObject dialoguePanel;
        public GameObject messagePanel;
        
        [Header("UI Elements")]
        public Text messageText;
        public Text questCountText;
        public Text gameTimeText;
        
        [Header("Settings")]
        public float messageDuration = 3f;
        
        private bool questLogOpen = false;
        private float messageTimer = 0f;
        
        private static UIManager _instance;
        public static UIManager Instance => _instance;
        
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
            Debug.Log("Initializing UI Manager...");
            
            // Hide all panels initially
            if (pauseMenu != null) pauseMenu.SetActive(false);
            if (questLogPanel != null) questLogPanel.SetActive(false);
            if (dialoguePanel != null) dialoguePanel.SetActive(false);
            if (messagePanel != null) messagePanel.SetActive(false);
        }
        
        void Update()
        {
            UpdateGameTimeDisplay();
            UpdateMessageTimer();
            UpdateQuestDisplay();
        }
        
        void UpdateGameTimeDisplay()
        {
            if (gameTimeText != null && GameManager.Instance != null)
            {
                float gameTime = GameManager.Instance.gameTime;
                int minutes = Mathf.FloorToInt(gameTime / 60f);
                int seconds = Mathf.FloorToInt(gameTime % 60f);
                gameTimeText.text = $"Time: {minutes:00}:{seconds:00}";
            }
        }
        
        void UpdateMessageTimer()
        {
            if (messageTimer > 0f)
            {
                messageTimer -= Time.deltaTime;
                if (messageTimer <= 0f)
                {
                    HideMessage();
                }
            }
        }
        
        void UpdateQuestDisplay()
        {
            if (questCountText != null && QuestManager.Instance != null)
            {
                int activeQuests = QuestManager.Instance.activeQuests.Count;
                int completedQuests = QuestManager.Instance.completedQuests.Count;
                questCountText.text = $"Quests: {activeQuests} Active, {completedQuests} Completed";
            }
        }
        
        public void ShowMessage(string message, float duration = 3f)
        {
            if (messagePanel != null && messageText != null)
            {
                messageText.text = message;
                messagePanel.SetActive(true);
                messageTimer = duration;
            }
        }
        
        public void HideMessage()
        {
            if (messagePanel != null)
            {
                messagePanel.SetActive(false);
            }
            messageTimer = 0f;
        }
        
        public void ShowPauseMenu(bool show)
        {
            if (pauseMenu != null)
            {
                pauseMenu.SetActive(show);
            }
        }
        
        public void ToggleQuestLog()
        {
            questLogOpen = !questLogOpen;
            
            if (questLogPanel != null)
            {
                questLogPanel.SetActive(questLogOpen);
            }
            
            if (questLogOpen)
            {
                UpdateQuestLogContent();
            }
        }
        
        void UpdateQuestLogContent()
        {
            // Update quest log with current quest information
            Debug.Log("Updating quest log content...");
        }
        
        // Button event handlers
        public void OnResumeClicked()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.TogglePause();
            }
        }
        
        public void OnSaveClicked()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.SaveGame();
                ShowMessage("Game Saved!", 2f);
            }
        }
        
        public void OnLoadClicked()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.LoadGame();
            }
        }
        
        public void OnRestartClicked()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.RestartGame();
            }
        }
        
        public void OnQuitClicked()
        {
            if (GameManager.Instance != null)
            {
                GameManager.Instance.QuitGame();
            }
        }
    }
}