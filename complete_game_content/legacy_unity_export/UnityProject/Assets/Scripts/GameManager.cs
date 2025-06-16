using UnityEngine;
using UnityEngine.SceneManagement;

namespace GeneratedGame
{
    /// <summary>
    /// Main game manager that coordinates all systems
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        [Header("Game State")]
        public bool gameStarted = false;
        public bool gamePaused = false;
        public float gameTime = 0f;
        
        [Header("Managers")]
        public WorldManager worldManager;
        public CharacterManager characterManager;
        public QuestManager questManager;
        public UIManager uiManager;
        
        [Header("Player")]
        public GameObject playerPrefab;
        public GameObject currentPlayer;
        
        [Header("Game Data")]
        public string worldTheme = "spooky";
        public int totalCharacters = 5;
        public int totalQuests = 7;
        
        private static GameManager _instance;
        public static GameManager Instance => _instance;
        
        void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeGame();
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        void Start()
        {
            StartGame();
        }
        
        void Update()
        {
            if (gameStarted && !gamePaused)
            {
                gameTime += Time.deltaTime;
                HandleInput();
            }
        }
        
        void InitializeGame()
        {
            Debug.Log("Initializing Generated Game...");
            
            // Find managers
            if (worldManager == null)
                worldManager = FindObjectOfType<WorldManager>();
                
            if (characterManager == null)
                characterManager = FindObjectOfType<CharacterManager>();
                
            if (questManager == null)
                questManager = FindObjectOfType<QuestManager>();
                
            if (uiManager == null)
                uiManager = FindObjectOfType<UIManager>();
            
            // Initialize all systems
            if (worldManager != null)
                worldManager.Initialize();
                
            if (characterManager != null)
                characterManager.Initialize();
                
            if (questManager != null)
                questManager.Initialize();
                
            if (uiManager != null)
                uiManager.Initialize();
        }
        
        void StartGame()
        {
            Debug.Log($"Starting {worldTheme} adventure with {totalCharacters} characters and {totalQuests} quests!");
            
            // Spawn player
            SpawnPlayer();
            
            gameStarted = true;
            
            // Show welcome message
            if (uiManager != null)
            {
                uiManager.ShowMessage($"Welcome to your generated {worldTheme} world!", 3f);
            }
        }
        
        void SpawnPlayer()
        {
            if (playerPrefab != null && worldManager != null)
            {
                Vector3 spawnPosition = worldManager.GetSpawnPosition();
                currentPlayer = Instantiate(playerPrefab, spawnPosition, Quaternion.identity);
                
                Debug.Log($"Player spawned at {spawnPosition}");
            }
        }
        
        void HandleInput()
        {
            // Handle pause
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                TogglePause();
            }
            
            // Handle quest log
            if (Input.GetKeyDown(KeyCode.Q))
            {
                if (uiManager != null)
                {
                    uiManager.ToggleQuestLog();
                }
            }
            
            // Handle interaction
            if (Input.GetKeyDown(KeyCode.E))
            {
                HandlePlayerInteraction();
            }
        }
        
        void HandlePlayerInteraction()
        {
            if (currentPlayer == null) return;
            
            // Find nearby interactable objects
            Collider[] nearby = Physics.OverlapSphere(currentPlayer.transform.position, 3f);
            
            foreach (var collider in nearby)
            {
                // Check for NPCs
                NPCController npc = collider.GetComponent<NPCController>();
                if (npc != null)
                {
                    npc.OnPlayerInteract();
                    return;
                }
                
                // Check for buildings
                Building building = collider.GetComponent<Building>();
                if (building != null)
                {
                    building.OnPlayerInteract();
                    return;
                }
            }
        }
        
        public void TogglePause()
        {
            gamePaused = !gamePaused;
            Time.timeScale = gamePaused ? 0f : 1f;
            
            if (uiManager != null)
            {
                uiManager.ShowPauseMenu(gamePaused);
            }
        }
        
        public void SaveGame()
        {
            Debug.Log("Saving game...");
            SaveSystem.SaveGame();
        }
        
        public void LoadGame()
        {
            Debug.Log("Loading game...");
            SaveSystem.LoadGame();
        }
        
        public void RestartGame()
        {
            SceneManager.LoadScene(SceneManager.GetActiveScene().name);
        }
        
        public void QuitGame()
        {
            #if UNITY_EDITOR
                UnityEditor.EditorApplication.isPlaying = false;
            #else
                Application.Quit();
            #endif
        }
    }
}