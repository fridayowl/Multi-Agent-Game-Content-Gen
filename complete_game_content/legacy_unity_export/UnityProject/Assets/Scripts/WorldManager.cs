using System.Collections.Generic;
using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Main world manager for generated game content
    /// Manages world state, buildings, and global systems
    /// </summary>
    public class WorldManager : MonoBehaviour
    {
        [Header("World Configuration")]
        public string worldTheme = "spooky";
        public Vector2 worldSize = new Vector2(40, 40);
        
        [Header("World Objects")]
        public List<GameObject> buildings = new List<GameObject>();
        public List<GameObject> naturalFeatures = new List<GameObject>();
        public List<GameObject> paths = new List<GameObject>();
        
        [Header("Systems")]
        public CharacterManager characterManager;
        public QuestManager questManager;
        
        private static WorldManager _instance;
        public static WorldManager Instance => _instance;
        
        void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeWorld();
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        void InitializeWorld()
        {
            Debug.Log($"Initializing {worldTheme} world of size {worldSize}");
            
            // Find and register all world objects
            RegisterWorldObjects();
            
            // Initialize systems
            if (characterManager != null)
                characterManager.Initialize();
                
            if (questManager != null)
                questManager.Initialize();
        }
        
        void RegisterWorldObjects()
        {
            // Find buildings
            GameObject[] buildingObjects = GameObject.FindGameObjectsWithTag("Building");
            buildings.AddRange(buildingObjects);
            
            // Find natural features
            GameObject[] featureObjects = GameObject.FindGameObjectsWithTag("NaturalFeature");
            naturalFeatures.AddRange(featureObjects);
            
            Debug.Log($"Registered {buildings.Count} buildings, {naturalFeatures.Count} features");
        }
        
        public GameObject FindBuildingByType(string buildingType)
        {
            foreach (var building in buildings)
            {
                var buildingComponent = building.GetComponent<Building>();
                if (buildingComponent != null && buildingComponent.buildingType == buildingType)
                {
                    return building;
                }
            }
            return null;
        }
        
        public Vector3 GetSpawnPosition()
        {
            // Return a safe spawn position
            return new Vector3(worldSize.x * 0.1f, 0, worldSize.y * 0.1f);
        }
        
        public void Initialize()
        {
            InitializeWorld();
        }
    }
}