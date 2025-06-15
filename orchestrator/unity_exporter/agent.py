#!/usr/bin/env python3
"""
COMPLETE UNITY CODE EXPORTER AGENT v2.0
Converts multi-agent pipeline output into Unity-ready packages
Final step in the game content generation pipeline
"""

import asyncio
import json
import os
import shutil
import zipfile
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import logging
from datetime import datetime
import textwrap

# Google ADK imports
from google.adk.agents import Agent

@dataclass
class UnityComponent:
    """Unity component definition"""
    component_type: str
    properties: Dict[str, Any]
    script_path: Optional[str] = None

@dataclass
class UnityGameObject:
    """Unity GameObject definition"""
    name: str
    transform: Dict[str, Any]
    components: List[UnityComponent]
    children: List['UnityGameObject']
    prefab_path: Optional[str] = None

@dataclass
class UnityScene:
    """Unity scene definition"""
    name: str
    game_objects: List[UnityGameObject]
    settings: Dict[str, Any]

@dataclass
class ExportManifest:
    """Complete export package manifest"""
    project_name: str
    unity_version: str
    export_timestamp: str
    content_summary: Dict[str, Any]
    file_structure: Dict[str, str]
    import_instructions: List[str]
    scene_files: List[str]
    script_files: List[str]
    prefab_files: List[str]
    asset_files: List[str]

class UnityCodeExporter:
    """
    COMPLETE UNITY CODE EXPORTER AGENT
    - Converts multi-agent pipeline output to Unity packages
    - Generates C# scripts for NPCs, quests, and world systems
    - Creates prefabs, scenes, and import-ready packages
    - Provides complete Unity project setup
    """
    
    def __init__(self, output_dir: str = "unity_export"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Unity project structure
        self.unity_project_dir = self.output_dir / "UnityProject"
        self.assets_dir = self.unity_project_dir / "Assets"
        self.scripts_dir = self.assets_dir / "Scripts"
        self.prefabs_dir = self.assets_dir / "Prefabs"
        self.scenes_dir = self.assets_dir / "Scenes"
        self.models_dir = self.assets_dir / "Models"
        self.textures_dir = self.assets_dir / "Textures"
        self.materials_dir = self.assets_dir / "Materials"
        
        # Create directory structure
        for directory in [self.assets_dir, self.scripts_dir, self.prefabs_dir, 
                         self.scenes_dir, self.models_dir, self.textures_dir, self.materials_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Export tracking
        self.exported_scripts = []
        self.exported_prefabs = []
        self.exported_scenes = []
        self.exported_assets = []
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def export_complete_package(self, world_spec: Dict[str, Any], 
                                    assets: Dict[str, Any], 
                                    characters: Dict[str, Any], 
                                    quests: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export complete Unity package from all pipeline components
        """
        self.logger.info("🚀 Starting Unity package export...")
        
        project_name = f"GeneratedGame_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Step 1: Create Unity project structure
            await self._create_project_structure(project_name)
            
            # Step 2: Export world system
            world_objects = await self._export_world_system(world_spec)
            
            # Step 3: Export character system
            character_objects = await self._export_character_system(characters)
            
            # Step 4: Export quest system
            quest_objects = await self._export_quest_system(quests, characters)
            
            # Step 5: Export assets
            asset_objects = await self._export_asset_system(assets)
            
            # Step 6: Create main scene
            main_scene = await self._create_main_scene(world_objects, character_objects, 
                                                     quest_objects, asset_objects)
            
            # Step 7: Generate management scripts
            await self._generate_management_scripts(world_spec, characters, quests)
            
            # Step 8: Create Unity package
            package_path = await self._create_unity_package(project_name)
            
            # Step 9: Generate documentation
            docs = await self._generate_documentation(world_spec, characters, quests, assets)
            
            export_manifest = ExportManifest(
                project_name=project_name,
                unity_version="2022.3 LTS",
                export_timestamp=datetime.now().isoformat(),
                content_summary=self._create_content_summary(world_spec, characters, quests, assets),
                file_structure=self._create_file_structure_map(),
                import_instructions=self._create_import_instructions(),
                scene_files=self.exported_scenes,
                script_files=self.exported_scripts,
                prefab_files=self.exported_prefabs,
                asset_files=self.exported_assets
            )
            
            # Save manifest
            manifest_path = self.output_dir / "export_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(asdict(export_manifest), f, indent=2)
            
            self.logger.info(f"✅ Unity package export complete!")
            self.logger.info(f"   📦 Package: {package_path}")
            self.logger.info(f"   📄 Scripts: {len(self.exported_scripts)}")
            self.logger.info(f"   🎮 Prefabs: {len(self.exported_prefabs)}")
            self.logger.info(f"   🌍 Scenes: {len(self.exported_scenes)}")
            
            return {
                'status': 'success',
                'project_name': project_name,
                'package_path': str(package_path),
                'manifest': asdict(export_manifest),
                'output_directory': str(self.output_dir),
                'unity_project_path': str(self.unity_project_dir),
                'import_ready': True,
                'file_counts': {
                    'scripts': len(self.exported_scripts),
                    'prefabs': len(self.exported_prefabs),
                    'scenes': len(self.exported_scenes),
                    'assets': len(self.exported_assets)
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Unity export failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'partial_export': True,
                'output_directory': str(self.output_dir)
            }
    
    async def _create_project_structure(self, project_name: str):
        """Create Unity project structure"""
        self.logger.info("📁 Creating Unity project structure...")
        
        # Create ProjectSettings
        project_settings_dir = self.unity_project_dir / "ProjectSettings"
        project_settings_dir.mkdir(exist_ok=True)
        
        # Create basic ProjectSettings files
        await self._create_project_settings_files(project_settings_dir, project_name)
        
        # Create Packages manifest
        packages_dir = self.unity_project_dir / "Packages"
        packages_dir.mkdir(exist_ok=True)
        
        await self._create_packages_manifest(packages_dir)
        
        self.logger.info("   ✅ Project structure created")
    
    async def _create_project_settings_files(self, settings_dir: Path, project_name: str):
        """Create essential Unity project settings files"""
        
        # ProjectSettings.asset (simplified)
        project_settings = f'''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 24
  productGUID: {self._generate_guid()}
  companyName: GeneratedGame
  productName: {project_name}
  defaultCursor: {{fileID: 0}}
  cursorHotspot: {{x: 0, y: 0}}
  m_SplashScreenBackgroundColor: {{r: 0.13725491, g: 0.12156863, b: 0.1254902, a: 1}}
  m_ShowUnitySplashScreen: 1
'''
        
        with open(settings_dir / "ProjectSettings.asset", 'w') as f:
            f.write(project_settings)
        
        # ProjectVersion.txt
        project_version = "m_EditorVersion: 2022.3.10f1\nm_EditorVersionWithRevision: 2022.3.10f1 (ff3792e53c62)"
        
        with open(settings_dir / "ProjectVersion.txt", 'w') as f:
            f.write(project_version)
    
    async def _create_packages_manifest(self, packages_dir: Path):
        """Create Unity packages manifest"""
        
        manifest = {
            "dependencies": {
                "com.unity.collab-proxy": "2.0.5",
                "com.unity.ide.rider": "3.0.24",
                "com.unity.ide.visualstudio": "2.0.18",
                "com.unity.test-framework": "1.1.33",
                "com.unity.textmeshpro": "3.0.6",
                "com.unity.ugui": "1.0.0",
                "com.unity.modules.ai": "1.0.0",
                "com.unity.modules.animation": "1.0.0",
                "com.unity.modules.audio": "1.0.0",
                "com.unity.modules.imgui": "1.0.0",
                "com.unity.modules.physics": "1.0.0",
                "com.unity.modules.ui": "1.0.0"
            }
        }
        
        with open(packages_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
    
    async def _export_world_system(self, world_spec: Dict[str, Any]) -> List[UnityGameObject]:
        """Export world system as Unity GameObjects"""
        self.logger.info("🌍 Exporting world system...")
        
        world_objects = []
        
        # Create world manager script
        await self._create_world_manager_script(world_spec)
        
        # Create terrain
        terrain_object = await self._create_terrain_object(world_spec)
        world_objects.append(terrain_object)
        
        # Create buildings
        buildings = world_spec.get('buildings', [])
        for i, building in enumerate(buildings):
            building_object = await self._create_building_object(building, i)
            world_objects.append(building_object)
        
        # Create natural features
        features = world_spec.get('natural_features', [])
        for i, feature in enumerate(features):
            feature_object = await self._create_feature_object(feature, i)
            world_objects.append(feature_object)
        
        self.logger.info(f"   ✅ Exported {len(world_objects)} world objects")
        return world_objects
    
    async def _create_world_manager_script(self, world_spec: Dict[str, Any]):
        """Create WorldManager script"""
        
        script_content = f'''using System.Collections.Generic;
using UnityEngine;

namespace GeneratedGame
{{
    /// <summary>
    /// Main world manager for generated game content
    /// Manages world state, buildings, and global systems
    /// </summary>
    public class WorldManager : MonoBehaviour
    {{
        [Header("World Configuration")]
        public string worldTheme = "{world_spec.get('theme', 'medieval')}";
        public Vector2 worldSize = new Vector2({world_spec.get('size', [40, 40])[0]}, {world_spec.get('size', [40, 40])[1]});
        
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
        {{
            if (_instance == null)
            {{
                _instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeWorld();
            }}
            else
            {{
                Destroy(gameObject);
            }}
        }}
        
        void InitializeWorld()
        {{
            Debug.Log($"Initializing {{worldTheme}} world of size {{worldSize}}");
            
            // Find and register all world objects
            RegisterWorldObjects();
            
            // Initialize systems
            if (characterManager != null)
                characterManager.Initialize();
                
            if (questManager != null)
                questManager.Initialize();
        }}
        
        void RegisterWorldObjects()
        {{
            // Find buildings
            GameObject[] buildingObjects = GameObject.FindGameObjectsWithTag("Building");
            buildings.AddRange(buildingObjects);
            
            // Find natural features
            GameObject[] featureObjects = GameObject.FindGameObjectsWithTag("NaturalFeature");
            naturalFeatures.AddRange(featureObjects);
            
            Debug.Log($"Registered {{buildings.Count}} buildings, {{naturalFeatures.Count}} features");
        }}
        
        public GameObject FindBuildingByType(string buildingType)
        {{
            foreach (var building in buildings)
            {{
                var buildingComponent = building.GetComponent<Building>();
                if (buildingComponent != null && buildingComponent.buildingType == buildingType)
                {{
                    return building;
                }}
            }}
            return null;
        }}
        
        public Vector3 GetSpawnPosition()
        {{
            // Return a safe spawn position
            return new Vector3(worldSize.x * 0.1f, 0, worldSize.y * 0.1f);
        }}
        
        public void Initialize()
        {{
            InitializeWorld();
        }}
    }}
}}'''
        
        script_path = self.scripts_dir / "WorldManager.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/WorldManager.cs")
    
    async def _create_terrain_object(self, world_spec: Dict[str, Any]) -> UnityGameObject:
        """Create terrain GameObject"""
        
        size = world_spec.get('size', [40, 40])
        
        return UnityGameObject(
            name="Terrain",
            transform={
                "position": [0, 0, 0],
                "rotation": [0, 0, 0, 1],
                "scale": [1, 1, 1]
            },
            components=[
                UnityComponent(
                    component_type="MeshRenderer",
                    properties={
                        "materials": ["Materials/TerrainMaterial"]
                    }
                ),
                UnityComponent(
                    component_type="MeshFilter",
                    properties={
                        "mesh": "Plane"
                    }
                ),
                UnityComponent(
                    component_type="BoxCollider",
                    properties={
                        "size": [size[0], 1, size[1]]
                    }
                )
            ],
            children=[]
        )
    
    async def _create_building_object(self, building: Dict[str, Any], index: int) -> UnityGameObject:
        """Create building GameObject"""
        
        position = building.get('position', {'x': 0, 'y': 0, 'z': 0})
        building_type = building.get('type', 'house')
        
        # Create Building component script
        await self._create_building_script()
        
        return UnityGameObject(
            name=f"{building_type.title()}_{index}",
            transform={
                "position": [position['x'], position['y'], position['z']],
                "rotation": [0, building.get('rotation', 0), 0, 1],
                "scale": [building.get('scale', 1), building.get('scale', 1), building.get('scale', 1)]
            },
            components=[
                UnityComponent(
                    component_type="MeshRenderer",
                    properties={
                        "materials": [f"Materials/{building_type}_Material"]
                    }
                ),
                UnityComponent(
                    component_type="MeshFilter",
                    properties={
                        "mesh": "Cube"
                    }
                ),
                UnityComponent(
                    component_type="BoxCollider",
                    properties={
                        "isTrigger": False,
                        "size": [1, 1, 1]
                    }
                ),
                UnityComponent(
                    component_type="Building",
                    properties={
                        "buildingType": building_type,
                        "buildingId": building.get('id', f'{building_type}_{index}'),
                        "importance": building.get('properties', {}).get('importance', 'normal')
                    },
                    script_path="Scripts/Building.cs"
                )
            ],
            children=[]
        )
    
    async def _create_building_script(self):
        """Create Building component script"""
        
        if "Scripts/Building.cs" in self.exported_scripts:
            return  # Already created
        
        script_content = '''using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Building component for generated structures
    /// </summary>
    public class Building : MonoBehaviour
    {
        [Header("Building Info")]
        public string buildingType = "house";
        public string buildingId = "";
        public string importance = "normal";
        
        [Header("Interaction")]
        public bool isInteractable = true;
        public float interactionRange = 3.0f;
        
        private void Start()
        {
            // Register with WorldManager
            if (WorldManager.Instance != null)
            {
                WorldManager.Instance.buildings.Add(gameObject);
            }
            
            // Set appropriate tag
            gameObject.tag = "Building";
        }
        
        public void OnPlayerInteract()
        {
            Debug.Log($"Player interacted with {buildingType}: {buildingId}");
            
            // Handle building-specific interactions
            switch (buildingType.ToLower())
            {
                case "tavern":
                    OpenTavernMenu();
                    break;
                case "shop":
                    OpenShopMenu();
                    break;
                case "blacksmith":
                    OpenBlacksmithMenu();
                    break;
                default:
                    ShowBuildingInfo();
                    break;
            }
        }
        
        private void OpenTavernMenu()
        {
            Debug.Log("Opening tavern menu...");
        }
        
        private void OpenShopMenu()
        {
            Debug.Log("Opening shop menu...");
        }
        
        private void OpenBlacksmithMenu()
        {
            Debug.Log("Opening blacksmith menu...");
        }
        
        private void ShowBuildingInfo()
        {
            Debug.Log($"This is a {buildingType}");
        }
        
        private void OnDrawGizmosSelected()
        {
            // Draw interaction range
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, interactionRange);
        }
    }
}'''
        
        script_path = self.scripts_dir / "Building.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/Building.cs")
    
    async def _create_feature_object(self, feature: Dict[str, Any], index: int) -> UnityGameObject:
        """Create natural feature GameObject"""
        
        position = feature.get('position', {'x': 0, 'y': 0, 'z': 0})
        feature_type = feature.get('type', 'tree')
        
        return UnityGameObject(
            name=f"{feature_type.title()}_{index}",
            transform={
                "position": [position['x'], position['y'], position['z']],
                "rotation": [0, feature.get('rotation', 0), 0, 1],
                "scale": [feature.get('scale', 1), feature.get('scale', 1), feature.get('scale', 1)]
            },
            components=[
                UnityComponent(
                    component_type="MeshRenderer",
                    properties={
                        "materials": [f"Materials/{feature_type}_Material"]
                    }
                ),
                UnityComponent(
                    component_type="MeshFilter",
                    properties={
                        "mesh": "Cylinder" if feature_type in ['tree', 'oak_tree'] else "Sphere"
                    }
                ),
                UnityComponent(
                    component_type="CapsuleCollider",
                    properties={
                        "isTrigger": False,
                        "radius": 0.5,
                        "height": 2.0
                    }
                )
            ],
            children=[]
        )
    
    async def _export_character_system(self, characters: Dict[str, Any]) -> List[UnityGameObject]:
        """Export character system"""
        self.logger.info("👥 Exporting character system...")
        
        character_objects = []
        
        # Create character manager script
        await self._create_character_manager_script(characters)
        
        # Create NPC script
        await self._create_npc_script()
        
        # Create character objects
        character_list = characters.get('characters', [])
        for i, character in enumerate(character_list):
            char_object = await self._create_character_object(character, i)
            character_objects.append(char_object)
        
        self.logger.info(f"   ✅ Exported {len(character_objects)} characters")
        return character_objects
    
    async def _create_character_manager_script(self, characters: Dict[str, Any]):
        """Create CharacterManager script"""
        
        script_content = f'''using System.Collections.Generic;
using UnityEngine;

namespace GeneratedGame
{{
    /// <summary>
    /// Manages all NPCs and character interactions
    /// </summary>
    public class CharacterManager : MonoBehaviour
    {{
        [Header("Characters")]
        public List<NPCController> npcs = new List<NPCController>();
        
        [Header("Dialogue System")]
        public GameObject dialogueUI;
        public bool isDialogueActive = false;
        
        private static CharacterManager _instance;
        public static CharacterManager Instance => _instance;
        
        void Awake()
        {{
            if (_instance == null)
            {{
                _instance = this;
            }}
            else
            {{
                Destroy(gameObject);
            }}
        }}
        
        public void Initialize()
        {{
            Debug.Log("Initializing Character Manager...");
            
            // Find all NPCs in scene
            RegisterNPCs();
            
            // Setup relationships
            SetupRelationships();
        }}
        
        void RegisterNPCs()
        {{
            NPCController[] foundNPCs = FindObjectsOfType<NPCController>();
            npcs.AddRange(foundNPCs);
            
            Debug.Log($"Registered {{npcs.Count}} NPCs");
        }}
        
        void SetupRelationships()
        {{
            // Setup NPC relationships based on generated data
            foreach (var npc in npcs)
            {{
                npc.InitializeRelationships();
            }}
        }}
        
        public NPCController FindNPCByName(string npcName)
        {{
            foreach (var npc in npcs)
            {{
                if (npc.characterName == npcName)
                {{
                    return npc;
                }}
            }}
            return null;
        }}
        
        public void StartDialogue(NPCController npc)
        {{
            if (isDialogueActive) return;
            
            isDialogueActive = true;
            Debug.Log($"Starting dialogue with {{npc.characterName}}");
            
            // Implement dialogue system
            if (dialogueUI != null)
            {{
                dialogueUI.SetActive(true);
                // Setup dialogue content
            }}
        }}
        
        public void EndDialogue()
        {{
            isDialogueActive = false;
            
            if (dialogueUI != null)
            {{
                dialogueUI.SetActive(false);
            }}
        }}
    }}
}}'''
        
        script_path = self.scripts_dir / "CharacterManager.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/CharacterManager.cs")
    
    async def _create_npc_script(self):
        """Create NPC controller script"""
        
        script_content = '''using System.Collections.Generic;
using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Controls individual NPC behavior and interactions
    /// </summary>
    public class NPCController : MonoBehaviour
    {
        [Header("Character Info")]
        public string characterName = "";
        public string characterRole = "";
        public int characterAge = 30;
        public string characterLocation = "";
        
        [Header("Personality")]
        public string primaryTrait = "";
        public string secondaryTrait = "";
        public string motivation = "";
        public string fear = "";
        public string secret = "";
        
        [Header("Stats")]
        public int level = 1;
        public int health = 100;
        public int strength = 10;
        public int intelligence = 10;
        public int charisma = 10;
        
        [Header("Behavior")]
        public float walkSpeed = 2.0f;
        public float interactionRange = 3.0f;
        public Transform[] patrolPoints;
        public bool isMoving = false;
        
        [Header("Dialogue")]
        public List<string> greetings = new List<string>();
        public List<string> farewells = new List<string>();
        
        private int currentPatrolIndex = 0;
        private bool playerInRange = false;
        
        void Start()
        {
            // Register with CharacterManager
            if (CharacterManager.Instance != null)
            {
                CharacterManager.Instance.npcs.Add(this);
            }
            
            // Start patrol behavior
            if (patrolPoints.Length > 0)
            {
                StartPatrol();
            }
        }
        
        void Update()
        {
            HandleMovement();
            CheckPlayerInteraction();
        }
        
        void HandleMovement()
        {
            if (patrolPoints.Length == 0 || !isMoving) return;
            
            Transform target = patrolPoints[currentPatrolIndex];
            Vector3 direction = (target.position - transform.position).normalized;
            
            transform.position += direction * walkSpeed * Time.deltaTime;
            transform.LookAt(target.position);
            
            if (Vector3.Distance(transform.position, target.position) < 0.5f)
            {
                currentPatrolIndex = (currentPatrolIndex + 1) % patrolPoints.Length;
            }
        }
        
        void CheckPlayerInteraction()
        {
            GameObject player = GameObject.FindGameObjectWithTag("Player");
            if (player == null) return;
            
            float distance = Vector3.Distance(transform.position, player.transform.position);
            bool wasInRange = playerInRange;
            playerInRange = distance <= interactionRange;
            
            if (playerInRange && !wasInRange)
            {
                OnPlayerEnterRange();
            }
            else if (!playerInRange && wasInRange)
            {
                OnPlayerExitRange();
            }
        }
        
        void OnPlayerEnterRange()
        {
            Debug.Log($"{characterName} notices the player");
            // Show interaction prompt
        }
        
        void OnPlayerExitRange()
        {
            Debug.Log($"{characterName} returns to normal behavior");
        }
        
        public void OnPlayerInteract()
        {
            Debug.Log($"Player interacts with {characterName}");
            
            // Stop movement during conversation
            bool wasMoving = isMoving;
            isMoving = false;
            
            // Face the player
            GameObject player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
            {
                Vector3 direction = (player.transform.position - transform.position).normalized;
                transform.rotation = Quaternion.LookRotation(direction);
            }
            
            // Start dialogue
            if (CharacterManager.Instance != null)
            {
                CharacterManager.Instance.StartDialogue(this);
            }
        }
        
        public void InitializeRelationships()
        {
            // Initialize character relationships based on generated data
            Debug.Log($"Initializing relationships for {characterName}");
        }
        
        void StartPatrol()
        {
            isMoving = true;
        }
        
        public void StopPatrol()
        {
            isMoving = false;
        }
        
        public string GetGreeting()
        {
            if (greetings.Count > 0)
            {
                return greetings[Random.Range(0, greetings.Count)];
            }
            return $"Hello! I'm {characterName}.";
        }
        
        public string GetFarewell()
        {
            if (farewells.Count > 0)
            {
                return farewells[Random.Range(0, farewells.Count)];
            }
            return "Goodbye!";
        }
        
        private void OnDrawGizmosSelected()
        {
            // Draw interaction range
            Gizmos.color = Color.green;
            Gizmos.DrawWireSphere(transform.position, interactionRange);
            
            // Draw patrol path
            if (patrolPoints.Length > 1)
            {
                Gizmos.color = Color.blue;
                for (int i = 0; i < patrolPoints.Length; i++)
                {
                    Vector3 current = patrolPoints[i].position;
                    Vector3 next = patrolPoints[(i + 1) % patrolPoints.Length].position;
                    Gizmos.DrawLine(current, next);
                }
            }
        }
    }
}'''
        
        script_path = self.scripts_dir / "NPCController.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/NPCController.cs")
    
    async def _create_character_object(self, character: Dict[str, Any], index: int) -> UnityGameObject:
        """Create character GameObject"""
        
        # Get character data
        char_name = character.get('name', f'Character_{index}')
        char_role = character.get('role', 'villager')
        char_age = character.get('age', 30)
        char_location = character.get('location', 'town_square')
        
        personality = character.get('personality', {})
        stats = character.get('stats', {})
        
        # Find spawn position based on location
        spawn_pos = self._get_character_spawn_position(char_location, index)
        
        return UnityGameObject(
            name=f"NPC_{char_name.replace(' ', '_')}",
            transform={
                "position": spawn_pos,
                "rotation": [0, 0, 0, 1],
                "scale": [1, 1, 1]
            },
            components=[
                UnityComponent(
                    component_type="CapsuleCollider",
                    properties={
                        "isTrigger": False,
                        "radius": 0.5,
                        "height": 2.0
                    }
                ),
                UnityComponent(
                    component_type="Rigidbody",
                    properties={
                        "mass": 1.0,
                        "drag": 1.0,
                        "angularDrag": 0.05,
                        "useGravity": True,
                        "isKinematic": False
                    }
                ),
                UnityComponent(
                    component_type="MeshRenderer",
                    properties={
                        "materials": [f"Materials/Character_{char_role}_Material"]
                    }
                ),
                UnityComponent(
                    component_type="MeshFilter",
                    properties={
                        "mesh": "Capsule"
                    }
                ),
                UnityComponent(
                    component_type="NPCController",
                    properties={
                        "characterName": char_name,
                        "characterRole": char_role,
                        "characterAge": char_age,
                        "characterLocation": char_location,
                        "primaryTrait": personality.get('primary_trait', 'friendly'),
                        "secondaryTrait": personality.get('secondary_trait', 'helpful'),
                        "motivation": personality.get('motivation', 'help others'),
                        "fear": personality.get('fear', 'being alone'),
                        "secret": personality.get('secret', 'has a mysterious past'),
                        "level": stats.get('level', 1),
                        "health": stats.get('health', 100),
                        "strength": stats.get('strength', 10),
                        "intelligence": stats.get('intelligence', 10),
                        "charisma": stats.get('charisma', 10)
                    },
                    script_path="Scripts/NPCController.cs"
                )
            ],
            children=[]
        )
    
    def _get_character_spawn_position(self, location: str, index: int) -> List[float]:
        """Get spawn position for character based on location"""
        
        # Base positions for different location types
        location_positions = {
            "tavern": [20, 0, 20],
            "blacksmith": [15, 0, 25],
            "church": [25, 0, 15],
            "shop": [18, 0, 22],
            "house": [12, 0, 18],
            "town_square": [20, 0, 18],
            "market": [20, 0, 25]
        }
        
        base_pos = location_positions.get(location, [20, 0, 18])
        
        # Add slight offset to prevent NPCs spawning in same spot
        offset_x = (index % 3 - 1) * 2  # -2, 0, 2
        offset_z = (index // 3 % 3 - 1) * 2
        
        return [base_pos[0] + offset_x, base_pos[1], base_pos[2] + offset_z]
    
    async def _export_quest_system(self, quests: Dict[str, Any], characters: Dict[str, Any]) -> List[UnityGameObject]:
        """Export quest system"""
        self.logger.info("📜 Exporting quest system...")
        
        quest_objects = []
        
        # Create quest manager script
        await self._create_quest_manager_script(quests)
        
        # Create quest scripts
        await self._create_quest_script()
        await self._create_dialogue_system_script()
        
        # Create quest manager object
        quest_manager_object = UnityGameObject(
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
                        "autoSave": True
                    },
                    script_path="Scripts/QuestManager.cs"
                )
            ],
            children=[]
        )
        
        quest_objects.append(quest_manager_object)
        
        self.logger.info(f"   ✅ Exported quest system with {len(quests.get('quests', []))} quests")
        return quest_objects
    
    async def _create_quest_manager_script(self, quests: Dict[str, Any]):
        """Create QuestManager script"""
        
        quest_list = quests.get('quests', [])
        
        script_content = f'''using System.Collections.Generic;
using UnityEngine;

namespace GeneratedGame
{{
    /// <summary>
    /// Manages all quests and quest progression
    /// </summary>
    public class QuestManager : MonoBehaviour
    {{
        [Header("Quest Configuration")]
        public int totalQuests = {len(quest_list)};
        public bool autoSave = true;
        
        [Header("Quest Lists")]
        public List<Quest> availableQuests = new List<Quest>();
        public List<Quest> activeQuests = new List<Quest>();
        public List<Quest> completedQuests = new List<Quest>();
        
        [Header("UI")]
        public GameObject questLogUI;
        public GameObject questNotificationUI;
        
        private static QuestManager _instance;
        public static QuestManager Instance => _instance;
        
        void Awake()
        {{
            if (_instance == null)
            {{
                _instance = this;
                DontDestroyOnLoad(gameObject);
            }}
            else
            {{
                Destroy(gameObject);
            }}
        }}
        
        public void Initialize()
        {{
            Debug.Log("Initializing Quest Manager...");
            InitializeQuests();
        }}
        
        void InitializeQuests()
        {{
            // Initialize all quests from generated data
{self._generate_quest_initialization_code(quest_list)}
            
            Debug.Log($"Initialized {{availableQuests.Count}} available quests");
        }}
        
        public void StartQuest(string questId)
        {{
            Quest questToStart = availableQuests.Find(q => q.questId == questId);
            if (questToStart != null)
            {{
                availableQuests.Remove(questToStart);
                activeQuests.Add(questToStart);
                questToStart.StartQuest();
                
                Debug.Log($"Started quest: {{questToStart.title}}");
                ShowQuestNotification($"Quest Started: {{questToStart.title}}", Color.yellow);
            }}
        }}
        
        public void CompleteQuest(string questId)
        {{
            Quest questToComplete = activeQuests.Find(q => q.questId == questId);
            if (questToComplete != null)
            {{
                activeQuests.Remove(questToComplete);
                completedQuests.Add(questToComplete);
                questToComplete.CompleteQuest();
                
                Debug.Log($"Completed quest: {{questToComplete.title}}");
                ShowQuestNotification($"Quest Completed: {{questToComplete.title}}", Color.green);
                
                // Give rewards
                GiveQuestRewards(questToComplete);
            }}
        }}
        
        public void UpdateQuestProgress(string questId, string objectiveId)
        {{
            Quest quest = activeQuests.Find(q => q.questId == questId);
            if (quest != null)
            {{
                quest.UpdateObjective(objectiveId);
                
                if (quest.IsCompleted())
                {{
                    CompleteQuest(questId);
                }}
            }}
        }}
        
        void GiveQuestRewards(Quest quest)
        {{
            // Implement reward system
            Debug.Log($"Giving rewards for quest: {{quest.title}}");
            
            // Add experience, gold, items, etc.
            if (quest.experienceReward > 0)
            {{
                // Give experience
                Debug.Log($"Gained {{quest.experienceReward}} experience!");
            }}
            
            if (quest.goldReward > 0)
            {{
                // Give gold
                Debug.Log($"Gained {{quest.goldReward}} gold!");
            }}
        }}
        
        void ShowQuestNotification(string message, Color color)
        {{
            Debug.Log($"Quest Notification: {{message}}");
            
            if (questNotificationUI != null)
            {{
                // Show UI notification
                questNotificationUI.SetActive(true);
                // Set notification text and color
            }}
        }}
        
        public Quest GetQuestById(string questId)
        {{
            // Search in all quest lists
            Quest quest = availableQuests.Find(q => q.questId == questId);
            if (quest != null) return quest;
            
            quest = activeQuests.Find(q => q.questId == questId);
            if (quest != null) return quest;
            
            quest = completedQuests.Find(q => q.questId == questId);
            return quest;
        }}
        
        public bool IsQuestCompleted(string questId)
        {{
            return completedQuests.Exists(q => q.questId == questId);
        }}
        
        public bool IsQuestActive(string questId)
        {{
            return activeQuests.Exists(q => q.questId == questId);
        }}
    }}
}}'''
        
        script_path = self.scripts_dir / "QuestManager.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/QuestManager.cs")
    
    def _generate_quest_initialization_code(self, quest_list: List[Dict]) -> str:
        """Generate quest initialization code"""
        
        init_code = ""
        for quest in quest_list[:5]:  # Limit to first 5 quests for readability
            quest_id = quest.get('id', 'unknown_quest')
            title = quest.get('title', 'Unknown Quest')
            description = quest.get('description', 'No description')
            giver_npc = quest.get('giver_npc', 'Unknown NPC')
            
            objectives = quest.get('objectives', [])
            obj_count = len(objectives)
            
            rewards = quest.get('rewards', {})
            exp_reward = rewards.get('experience', 0)
            gold_reward = rewards.get('gold', 0)
            
            init_code += f'''
            // Quest: {title}
            {{
                Quest quest = new Quest();
                quest.questId = "{quest_id}";
                quest.title = "{title}";
                quest.description = "{description}";
                quest.giverNPC = "{giver_npc}";
                quest.objectiveCount = {obj_count};
                quest.experienceReward = {exp_reward};
                quest.goldReward = {gold_reward};
                availableQuests.Add(quest);
            }}'''
        
        return init_code
    
    async def _create_quest_script(self):
        """Create Quest class script"""
        
        script_content = '''using System.Collections.Generic;
using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Individual quest data and logic
    /// </summary>
    [System.Serializable]
    public class Quest
    {
        [Header("Quest Info")]
        public string questId = "";
        public string title = "";
        public string description = "";
        public string giverNPC = "";
        
        [Header("Objectives")]
        public int objectiveCount = 0;
        public List<string> objectives = new List<string>();
        public List<bool> objectiveCompleted = new List<bool>();
        
        [Header("Rewards")]
        public int experienceReward = 0;
        public int goldReward = 0;
        public List<string> itemRewards = new List<string>();
        
        [Header("State")]
        public bool isActive = false;
        public bool isCompleted = false;
        
        public void StartQuest()
        {
            isActive = true;
            Debug.Log($"Started quest: {title}");
        }
        
        public void CompleteQuest()
        {
            isActive = false;
            isCompleted = true;
            Debug.Log($"Completed quest: {title}");
        }
        
        public void UpdateObjective(string objectiveId)
        {
            // Find and update objective
            for (int i = 0; i < objectives.Count; i++)
            {
                if (objectives[i].Contains(objectiveId))
                {
                    objectiveCompleted[i] = true;
                    Debug.Log($"Objective completed: {objectives[i]}");
                    break;
                }
            }
        }
        
        public bool IsCompleted()
        {
            if (objectiveCompleted.Count == 0) return false;
            
            foreach (bool completed in objectiveCompleted)
            {
                if (!completed) return false;
            }
            return true;
        }
        
        public float GetProgress()
        {
            if (objectiveCompleted.Count == 0) return 0f;
            
            int completed = 0;
            foreach (bool obj in objectiveCompleted)
            {
                if (obj) completed++;
            }
            
            return (float)completed / objectiveCompleted.Count;
        }
    }
}'''
        
        script_path = self.scripts_dir / "Quest.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/Quest.cs")
    
    async def _create_dialogue_system_script(self):
        """Create dialogue system script"""
        
        script_content = '''using System.Collections.Generic;
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
}'''
        
        script_path = self.scripts_dir / "DialogueSystem.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/DialogueSystem.cs")
    
    async def _export_asset_system(self, assets: Dict[str, Any]) -> List[UnityGameObject]:
        """Export asset system"""
        self.logger.info("🎨 Exporting asset system...")
        
        asset_objects = []
        
        # Copy asset files if they exist
        if assets and assets.get('output_directory'):
            await self._copy_asset_files(assets)
        
        # Create asset manager
        asset_manager_object = UnityGameObject(
            name="AssetManager",
            transform={
                "position": [0, 0, 0],
                "rotation": [0, 0, 0, 1],
                "scale": [1, 1, 1]
            },
            components=[
                UnityComponent(
                    component_type="AssetManager",
                    properties={
                        "assetCount": assets.get('generation_summary', {}).get('total_creative_assets', 0)
                    }
                )
            ],
            children=[]
        )
        
        asset_objects.append(asset_manager_object)
        
        self.logger.info(f"   ✅ Exported asset system")
        return asset_objects
    
    async def _copy_asset_files(self, assets: Dict[str, Any]):
        """Copy asset files to Unity project"""
        
        asset_source_dir = Path(assets.get('output_directory', ''))
        
        if not asset_source_dir.exists():
            self.logger.warning(f"Asset source directory not found: {asset_source_dir}")
            return
        
        # Copy models
        models_source = asset_source_dir / "models"
        if models_source.exists():
            for model_file in models_source.glob("*.obj"):
                shutil.copy2(model_file, self.models_dir)
                self.exported_assets.append(f"Models/{model_file.name}")
        
        # Copy textures
        textures_source = asset_source_dir / "ai_textures"
        if textures_source.exists():
            for texture_file in textures_source.glob("*.png"):
                shutil.copy2(texture_file, self.textures_dir)
                self.exported_assets.append(f"Textures/{texture_file.name}")
        
        self.logger.info(f"   📁 Copied {len(self.exported_assets)} asset files")
    
    async def _create_main_scene(self, world_objects: List[UnityGameObject], 
                                character_objects: List[UnityGameObject],
                                quest_objects: List[UnityGameObject],
                                asset_objects: List[UnityGameObject]) -> UnityScene:
        """Create main Unity scene"""
        
        self.logger.info("🎬 Creating main Unity scene...")
        
        all_objects = []
        
        # Add world objects
        all_objects.extend(world_objects)
        
        # Add character objects
        all_objects.extend(character_objects)
        
        # Add quest objects
        all_objects.extend(quest_objects)
        
        # Add asset objects
        all_objects.extend(asset_objects)
        
        # Add lighting
        lighting_object = UnityGameObject(
            name="Directional Light",
            transform={
                "position": [0, 10, 0],
                "rotation": [50, -30, 0, 1],
                "scale": [1, 1, 1]
            },
            components=[
                UnityComponent(
                    component_type="Light",
                    properties={
                        "type": "Directional",
                        "color": [1, 0.95, 0.8, 1],
                        "intensity": 1.0,
                        "shadows": "Soft"
                    }
                )
            ],
            children=[]
        )
        all_objects.append(lighting_object)
        
        # Add camera
        camera_object = UnityGameObject(
            name="Main Camera",
            transform={
                "position": [0, 5, -10],
                "rotation": [15, 0, 0, 1],
                "scale": [1, 1, 1]
            },
            components=[
                UnityComponent(
                    component_type="Camera",
                    properties={
                        "clearFlags": "Skybox",
                        "fieldOfView": 60,
                        "nearClipPlane": 0.3,
                        "farClipPlane": 1000
                    }
                ),
                UnityComponent(
                    component_type="AudioListener",
                    properties={}
                )
            ],
            children=[]
        )
        all_objects.append(camera_object)
        
        main_scene = UnityScene(
            name="GeneratedGameScene",
            game_objects=all_objects,
            settings={
                "ambientLight": [0.2, 0.2, 0.3, 1],
                "skybox": "Default-Skybox",
                "fog": True,
                "fogColor": [0.5, 0.5, 0.7, 1],
                "fogMode": "Linear",
                "fogStartDistance": 20,
                "fogEndDistance": 200
            }
        )
        
        # Save scene file
        await self._save_unity_scene(main_scene)
        
        self.logger.info(f"   ✅ Created scene with {len(all_objects)} objects")
        return main_scene
    
    async def _save_unity_scene(self, scene: UnityScene):
        """Save Unity scene file in proper YAML format"""
        
        scene_content = f'''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!29 &1
OcclusionCullingSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_OcclusionBakeSettings:
    smallestOccluder: 5
    smallestHole: 0.25
    backfaceThreshold: 100
  m_SceneGUID: 00000000000000000000000000000000
  m_OcclusionCullingData: {{fileID: 0}}
--- !u!104 &2
RenderSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 9
  m_Fog: {str(scene.settings.get('fog', True)).lower()}
  m_FogColor: {{r: {scene.settings.get('fogColor', [0.5, 0.5, 0.7, 1])[0]}, g: {scene.settings.get('fogColor', [0.5, 0.5, 0.7, 1])[1]}, b: {scene.settings.get('fogColor', [0.5, 0.5, 0.7, 1])[2]}, a: {scene.settings.get('fogColor', [0.5, 0.5, 0.7, 1])[3]}}}
  m_FogMode: 1
  m_FogDensity: 0.01
  m_LinearFogStart: {scene.settings.get('fogStartDistance', 20)}
  m_LinearFogEnd: {scene.settings.get('fogEndDistance', 200)}
  m_AmbientSkyColor: {{r: {scene.settings.get('ambientLight', [0.2, 0.2, 0.3, 1])[0]}, g: {scene.settings.get('ambientLight', [0.2, 0.2, 0.3, 1])[1]}, b: {scene.settings.get('ambientLight', [0.2, 0.2, 0.3, 1])[2]}, a: {scene.settings.get('ambientLight', [0.2, 0.2, 0.3, 1])[3]}}}
  m_AmbientEquatorColor: {{r: 0.114, g: 0.125, b: 0.133, a: 1}}
  m_AmbientGroundColor: {{r: 0.047, g: 0.043, b: 0.035, a: 1}}
  m_AmbientIntensity: 1
  m_AmbientMode: 0
  m_SubtractiveShadowColor: {{r: 0.42, g: 0.478, b: 0.627, a: 1}}
  m_SkyboxMaterial: {{fileID: 10304, guid: 0000000000000000f000000000000000, type: 0}}
  m_HaloStrength: 0.5
  m_FlareStrength: 1
  m_FlareFadeSpeed: 3
  m_HaloTexture: {{fileID: 0}}
  m_SpotCookie: {{fileID: 10001, guid: 0000000000000000e000000000000000, type: 0}}
  m_DefaultReflectionMode: 0
  m_DefaultReflectionResolution: 128
  m_ReflectionBounces: 1
  m_ReflectionIntensity: 1
  m_CustomReflection: {{fileID: 0}}
  m_Sun: {{fileID: 0}}
  m_IndirectSpecularColor: {{r: 0.44657898, g: 0.4964133, b: 0.5748178, a: 1}}
  m_UseRadianceAmbientProbe: 0
--- !u!157 &3
LightmapSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 12
  m_GIWorkflowMode: 1
  m_GISettings:
    serializedVersion: 2
    m_BounceScale: 1
    m_IndirectOutputScale: 1
    m_AlbedoBoost: 1
    m_EnvironmentLightingMode: 0
    m_EnableBakedLightmaps: 1
    m_EnableRealtimeLightmaps: 0
--- !u!196 &4
NavMeshSettings:
  serializedVersion: 2
  m_ObjectHideFlags: 0
  m_BuildSettings:
    serializedVersion: 2
    agentTypeID: 0
    agentRadius: 0.5
    agentHeight: 2
    agentSlope: 45
    agentClimb: 0.4
    ledgeDropHeight: 0
    maxJumpAcrossDistance: 0
    minRegionArea: 2
    manualCellSize: 0
    cellSize: 0.16666667
    manualTileSize: 0
    tileSize: 256
    accuratePlacement: 0
    maxJobWorkers: 0
    preserveTilesOutsideBounds: 0
    debug:
      m_Flags: 0
  m_NavMeshData: {{fileID: 0}}
'''

        # Add GameObjects to scene
        object_id = 5
        for game_object in scene.game_objects[:10]:  # Limit for demo
            scene_content += f'''--- !u!1 &{object_id}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {object_id + 100}}}
  m_Layer: 0
  m_Name: {game_object.name}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{object_id + 100}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {object_id}}}
  m_LocalRotation: {{x: {game_object.transform['rotation'][0]}, y: {game_object.transform['rotation'][1]}, z: {game_object.transform['rotation'][2]}, w: {game_object.transform['rotation'][3]}}}
  m_LocalPosition: {{x: {game_object.transform['position'][0]}, y: {game_object.transform['position'][1]}, z: {game_object.transform['position'][2]}}}
  m_LocalScale: {{x: {game_object.transform['scale'][0]}, y: {game_object.transform['scale'][1]}, z: {game_object.transform['scale'][2]}}}
  m_Children: []
  m_Father: {{fileID: 0}}
  m_RootOrder: {object_id - 5}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
'''
            object_id += 200  # Space for components

        scene_path = self.scenes_dir / f"{scene.name}.unity"
        with open(scene_path, 'w') as f:
            f.write(scene_content)
        
        self.exported_scenes.append(f"Scenes/{scene.name}.unity")
    
    async def _generate_management_scripts(self, world_spec: Dict[str, Any], 
                                         characters: Dict[str, Any], 
                                         quests: Dict[str, Any]):
        """Generate additional management scripts"""
        
        self.logger.info("⚙️ Generating management scripts...")
        
        # Create Game Manager
        await self._create_game_manager_script(world_spec, characters, quests)
        
        # Create Player Controller
        await self._create_player_controller_script()
        
        # Create UI Manager
        await self._create_ui_manager_script()
        
        # Create Save System
        await self._create_save_system_script()
        
        self.logger.info("   ✅ Generated management scripts")
    
    async def _create_game_manager_script(self, world_spec: Dict[str, Any], 
                                        characters: Dict[str, Any], 
                                        quests: Dict[str, Any]):
        """Create main GameManager script"""
        
        script_content = f'''using UnityEngine;
using UnityEngine.SceneManagement;

namespace GeneratedGame
{{
    /// <summary>
    /// Main game manager that coordinates all systems
    /// </summary>
    public class GameManager : MonoBehaviour
    {{
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
        public string worldTheme = "{world_spec.get('theme', 'medieval')}";
        public int totalCharacters = {len(characters.get('characters', []))};
        public int totalQuests = {len(quests.get('quests', []))};
        
        private static GameManager _instance;
        public static GameManager Instance => _instance;
        
        void Awake()
        {{
            if (_instance == null)
            {{
                _instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeGame();
            }}
            else
            {{
                Destroy(gameObject);
            }}
        }}
        
        void Start()
        {{
            StartGame();
        }}
        
        void Update()
        {{
            if (gameStarted && !gamePaused)
            {{
                gameTime += Time.deltaTime;
                HandleInput();
            }}
        }}
        
        void InitializeGame()
        {{
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
        }}
        
        void StartGame()
        {{
            Debug.Log($"Starting {{worldTheme}} adventure with {{totalCharacters}} characters and {{totalQuests}} quests!");
            
            // Spawn player
            SpawnPlayer();
            
            gameStarted = true;
            
            // Show welcome message
            if (uiManager != null)
            {{
                uiManager.ShowMessage($"Welcome to your generated {{worldTheme}} world!", 3f);
            }}
        }}
        
        void SpawnPlayer()
        {{
            if (playerPrefab != null && worldManager != null)
            {{
                Vector3 spawnPosition = worldManager.GetSpawnPosition();
                currentPlayer = Instantiate(playerPrefab, spawnPosition, Quaternion.identity);
                
                Debug.Log($"Player spawned at {{spawnPosition}}");
            }}
        }}
        
        void HandleInput()
        {{
            // Handle pause
            if (Input.GetKeyDown(KeyCode.Escape))
            {{
                TogglePause();
            }}
            
            // Handle quest log
            if (Input.GetKeyDown(KeyCode.Q))
            {{
                if (uiManager != null)
                {{
                    uiManager.ToggleQuestLog();
                }}
            }}
            
            // Handle interaction
            if (Input.GetKeyDown(KeyCode.E))
            {{
                HandlePlayerInteraction();
            }}
        }}
        
        void HandlePlayerInteraction()
        {{
            if (currentPlayer == null) return;
            
            // Find nearby interactable objects
            Collider[] nearby = Physics.OverlapSphere(currentPlayer.transform.position, 3f);
            
            foreach (var collider in nearby)
            {{
                // Check for NPCs
                NPCController npc = collider.GetComponent<NPCController>();
                if (npc != null)
                {{
                    npc.OnPlayerInteract();
                    return;
                }}
                
                // Check for buildings
                Building building = collider.GetComponent<Building>();
                if (building != null)
                {{
                    building.OnPlayerInteract();
                    return;
                }}
            }}
        }}
        
        public void TogglePause()
        {{
            gamePaused = !gamePaused;
            Time.timeScale = gamePaused ? 0f : 1f;
            
            if (uiManager != null)
            {{
                uiManager.ShowPauseMenu(gamePaused);
            }}
        }}
        
        public void SaveGame()
        {{
            Debug.Log("Saving game...");
            SaveSystem.SaveGame();
        }}
        
        public void LoadGame()
        {{
            Debug.Log("Loading game...");
            SaveSystem.LoadGame();
        }}
        
        public void RestartGame()
        {{
            SceneManager.LoadScene(SceneManager.GetActiveScene().name);
        }}
        
        public void QuitGame()
        {{
            #if UNITY_EDITOR
                UnityEditor.EditorApplication.isPlaying = false;
            #else
                Application.Quit();
            #endif
        }}
    }}
}}'''
        
        script_path = self.scripts_dir / "GameManager.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/GameManager.cs")
    
    async def _create_player_controller_script(self):
        """Create PlayerController script"""
        
        script_content = '''using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Basic player movement and interaction controller
    /// </summary>
    public class PlayerController : MonoBehaviour
    {
        [Header("Movement")]
        public float moveSpeed = 5f;
        public float rotationSpeed = 720f;
        public float jumpForce = 5f;
        
        [Header("Camera")]
        public Transform cameraFollow;
        public float cameraDistance = 10f;
        public float cameraHeight = 5f;
        
        [Header("Ground Check")]
        public LayerMask groundMask = 1;
        public float groundCheckDistance = 0.1f;
        
        private Rigidbody rb;
        private bool isGrounded;
        private Vector3 moveDirection;
        
        void Start()
        {
            rb = GetComponent<Rigidbody>();
            
            // Setup camera if not assigned
            if (cameraFollow == null)
            {
                GameObject mainCam = Camera.main?.gameObject;
                if (mainCam != null)
                {
                    cameraFollow = mainCam.transform;
                }
            }
            
            // Tag as player
            gameObject.tag = "Player";
        }
        
        void Update()
        {
            HandleInput();
            CheckGrounded();
            UpdateCamera();
        }
        
        void FixedUpdate()
        {
            HandleMovement();
        }
        
        void HandleInput()
        {
            // Get movement input
            float horizontal = Input.GetAxis("Horizontal");
            float vertical = Input.GetAxis("Vertical");
            
            moveDirection = new Vector3(horizontal, 0, vertical).normalized;
            
            // Jump input
            if (Input.GetButtonDown("Jump") && isGrounded)
            {
                Jump();
            }
        }
        
        void HandleMovement()
        {
            if (moveDirection.magnitude > 0.1f)
            {
                // Move the player
                Vector3 movement = moveDirection * moveSpeed * Time.fixedDeltaTime;
                rb.MovePosition(transform.position + movement);
                
                // Rotate towards movement direction
                Quaternion targetRotation = Quaternion.LookRotation(moveDirection);
                transform.rotation = Quaternion.RotateTowards(
                    transform.rotation, 
                    targetRotation, 
                    rotationSpeed * Time.fixedDeltaTime
                );
            }
        }
        
        void Jump()
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        }
        
        void CheckGrounded()
        {
            RaycastHit hit;
            isGrounded = Physics.Raycast(
                transform.position, 
                Vector3.down, 
                out hit, 
                groundCheckDistance + 0.1f, 
                groundMask
            );
        }
        
        void UpdateCamera()
        {
            if (cameraFollow == null) return;
            
            // Position camera behind and above player
            Vector3 targetPosition = transform.position - transform.forward * cameraDistance + Vector3.up * cameraHeight;
            cameraFollow.position = Vector3.Lerp(cameraFollow.position, targetPosition, Time.deltaTime * 2f);
            
            // Look at player
            cameraFollow.LookAt(transform.position + Vector3.up * 1.5f);
        }
        
        private void OnDrawGizmosSelected()
        {
            // Draw ground check ray
            Gizmos.color = isGrounded ? Color.green : Color.red;
            Gizmos.DrawRay(transform.position, Vector3.down * (groundCheckDistance + 0.1f));
        }
    }
}'''
        
        script_path = self.scripts_dir / "PlayerController.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/PlayerController.cs")
    
    async def _create_ui_manager_script(self):
        """Create UIManager script"""
        
        script_content = '''using UnityEngine;
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
}'''
        
        script_path = self.scripts_dir / "UIManager.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/UIManager.cs")
    
    async def _create_save_system_script(self):
        """Create SaveSystem script"""
        
        script_content = '''using System.IO;
using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Handles game save and load functionality
    /// </summary>
    public static class SaveSystem
    {
        private static string savePath = Application.persistentDataPath + "/savegame.json";
        
        [System.Serializable]
        public class SaveData
        {
            public float gameTime;
            public Vector3 playerPosition;
            public string[] completedQuests;
            public string[] activeQuests;
            public int playerLevel;
            public int playerExperience;
            public int playerGold;
        }
        
        public static void SaveGame()
        {
            try
            {
                SaveData saveData = new SaveData();
                
                // Gather data from game managers
                if (GameManager.Instance != null)
                {
                    saveData.gameTime = GameManager.Instance.gameTime;
                    
                    if (GameManager.Instance.currentPlayer != null)
                    {
                        saveData.playerPosition = GameManager.Instance.currentPlayer.transform.position;
                    }
                }
                
                if (QuestManager.Instance != null)
                {
                    saveData.completedQuests = new string[QuestManager.Instance.completedQuests.Count];
                    for (int i = 0; i < QuestManager.Instance.completedQuests.Count; i++)
                    {
                        saveData.completedQuests[i] = QuestManager.Instance.completedQuests[i].questId;
                    }
                    
                    saveData.activeQuests = new string[QuestManager.Instance.activeQuests.Count];
                    for (int i = 0; i < QuestManager.Instance.activeQuests.Count; i++)
                    {
                        saveData.activeQuests[i] = QuestManager.Instance.activeQuests[i].questId;
                    }
                }
                
                // Convert to JSON and save
                string jsonData = JsonUtility.ToJson(saveData, true);
                File.WriteAllText(savePath, jsonData);
                
                Debug.Log($"Game saved to: {savePath}");
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Failed to save game: {e.Message}");
            }
        }
        
        public static bool LoadGame()
        {
            try
            {
                if (!File.Exists(savePath))
                {
                    Debug.LogWarning("No save file found");
                    return false;
                }
                
                string jsonData = File.ReadAllText(savePath);
                SaveData saveData = JsonUtility.FromJson<SaveData>(jsonData);
                
                // Apply loaded data
                if (GameManager.Instance != null)
                {
                    GameManager.Instance.gameTime = saveData.gameTime;
                    
                    if (GameManager.Instance.currentPlayer != null)
                    {
                        GameManager.Instance.currentPlayer.transform.position = saveData.playerPosition;
                    }
                }
                
                if (QuestManager.Instance != null)
                {
                    // Restore quest states
                    foreach (string questId in saveData.completedQuests)
                    {
                        QuestManager.Instance.CompleteQuest(questId);
                    }
                    
                    foreach (string questId in saveData.activeQuests)
                    {
                        QuestManager.Instance.StartQuest(questId);
                    }
                }
                
                Debug.Log("Game loaded successfully");
                return true;
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Failed to load game: {e.Message}");
                return false;
            }
        }
        
        public static bool SaveExists()
        {
            return File.Exists(savePath);
        }
        
        public static void DeleteSave()
        {
            try
            {
                if (File.Exists(savePath))
                {
                    File.Delete(savePath);
                    Debug.Log("Save file deleted");
                }
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Failed to delete save file: {e.Message}");
            }
        }
    }
}'''
        
        script_path = self.scripts_dir / "SaveSystem.cs"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        self.exported_scripts.append("Scripts/SaveSystem.cs")
    
    async def _create_unity_package(self, project_name: str) -> Path:
        """Create Unity package file"""
        
        self.logger.info("📦 Creating Unity package...")
        
        package_path = self.output_dir / f"{project_name}.unitypackage"
        
        # Create a zip file with Unity package structure
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as package_zip:
            
            # Add all files from the Unity project
            for root, dirs, files in os.walk(self.unity_project_dir):
                for file in files:
                    file_path = Path(root) / file
                    arc_path = file_path.relative_to(self.unity_project_dir)
                    package_zip.write(file_path, arc_path)
        
        self.logger.info(f"   ✅ Package created: {package_path.name}")
        return package_path
    
    async def _generate_documentation(self, world_spec: Dict[str, Any], 
                                    characters: Dict[str, Any], 
                                    quests: Dict[str, Any], 
                                    assets: Dict[str, Any]) -> str:
        """Generate comprehensive documentation"""
        
        self.logger.info("📝 Generating documentation...")
        
        documentation = f'''# Generated Game Unity Package Documentation

## Project Overview
This Unity package contains a complete game generated by the Multi-Agent Game Content Pipeline.

### World Information
- **Theme**: {world_spec.get('theme', 'Unknown')}
- **Size**: {world_spec.get('size', [0, 0])}
- **Buildings**: {len(world_spec.get('buildings', []))}
- **Natural Features**: {len(world_spec.get('natural_features', []))}

### Characters
- **Total NPCs**: {len(characters.get('characters', []))}
- **Unique Personalities**: Generated with AI
- **Dialogue Systems**: Interactive conversation trees

### Quest System
- **Total Quests**: {len(quests.get('quests', []))}
- **Quest Types**: Main storylines and side quests
- **Interconnected**: Quests reference each other and NPCs

## Installation Instructions

1. **Import Package**
   - Open Unity 2022.3 LTS or newer
   - Go to Assets > Import Package > Custom Package
   - Select the .unitypackage file
   - Import all assets

2. **Open Scene**
   - Navigate to Assets/Scenes/
   - Open "GeneratedGameScene"

3. **Setup Player**
   - The scene includes a basic player controller
   - Press Play to start exploring

## Controls

- **WASD**: Move player
- **E**: Interact with NPCs and buildings
- **Q**: Open quest log
- **Esc**: Pause menu

## System Architecture

### Core Scripts
- **GameManager**: Main game coordinator
- **WorldManager**: Handles world objects and systems
- **CharacterManager**: Manages all NPCs
- **QuestManager**: Quest progression and tracking
- **UIManager**: User interface coordination

### NPC System
- **NPCController**: Individual NPC behavior
- **DialogueSystem**: Conversation handling

### Quest System
- **Quest**: Individual quest definitions
- **Objective tracking**: Automatic progress monitoring

## File Structure
```
Assets/
├── Scenes/
│   └── GeneratedGameScene.unity
├── Scripts/
│   ├── GameManager.cs
│   ├── WorldManager.cs
│   ├── CharacterManager.cs
│   ├── QuestManager.cs
│   ├── UIManager.cs
│   ├── NPCController.cs
│   ├── Building.cs
│   ├── Quest.cs
│   ├── DialogueSystem.cs
│   ├── PlayerController.cs
│   └── SaveSystem.cs
├── Models/
├── Textures/
├── Materials/
└── Prefabs/
```

## Troubleshooting

### Common Issues

**NPCs not moving**
- Check patrol points are assigned
- Verify NPCController script is enabled

**Quests not starting**
- Verify QuestManager is in scene
- Check NPC dialogue is set up

**UI not responding**
- Check UIManager references
- Verify Canvas and EventSystem exist

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
        
        # Save documentation
        docs_path = self.output_dir / "README.md"
        with open(docs_path, 'w') as f:
            f.write(documentation)
        
        self.logger.info(f"   ✅ Documentation saved: {docs_path.name}")
        return documentation
    
    def _create_content_summary(self, world_spec: Dict[str, Any], 
                               characters: Dict[str, Any], 
                               quests: Dict[str, Any], 
                               assets: Dict[str, Any]) -> Dict[str, Any]:
        """Create content summary for manifest"""
        
        return {
            "world": {
                "theme": world_spec.get('theme', 'unknown'),
                "size": world_spec.get('size', [0, 0]),
                "buildings": len(world_spec.get('buildings', [])),
                "natural_features": len(world_spec.get('natural_features', []))
            },
            "characters": {
                "total_npcs": len(characters.get('characters', [])),
                "total_relationships": characters.get('generation_summary', {}).get('total_relationships', 0)
            },
            "quests": {
                "total_quests": len(quests.get('quests', [])),
                "main_quests": len([q for q in quests.get('quests', []) if q.get('quest_type') == 'main']),
                "side_quests": len([q for q in quests.get('quests', []) if q.get('quest_type') == 'side'])
            },
            "assets": {
                "total_assets": assets.get('generation_summary', {}).get('total_creative_assets', 0),
                "ai_generated": assets.get('ai_generated', False)
            }
        }
    
    def _create_file_structure_map(self) -> Dict[str, str]:
        """Create file structure mapping"""
        
        return {
            "Scripts/": "C# scripts for game logic and systems",
            "Scenes/": "Unity scene files ready to play",
            "Models/": "3D model files (.obj, .fbx)",
            "Textures/": "AI-generated texture files (.png)",
            "Materials/": "Unity material definitions",
            "Prefabs/": "Reusable Unity prefabs",
            "ProjectSettings/": "Unity project configuration",
            "Packages/": "Unity package dependencies"
        }
    
    def _create_import_instructions(self) -> List[str]:
        """Create import instructions"""
        
        return [
            "1. Open Unity 2022.3 LTS or newer",
            "2. Create new 3D project or open existing project",
            "3. Go to Assets > Import Package > Custom Package",
            "4. Select the .unitypackage file from this export",
            "5. Import all assets when prompted",
            "6. Open Assets/Scenes/GeneratedGameScene.unity",
            "7. Press Play to start exploring the generated world",
            "8. Use WASD to move, E to interact, Q for quest log",
            "9. Interact with NPCs to start conversations and quests",
            "10. Customize scripts and assets as needed for your project"
        ]
    
    def _generate_guid(self) -> str:
        """Generate a Unity-style GUID"""
        import random
        import string
        
    def _generate_guid(self) -> str:
        """Generate a Unity-style GUID"""
        import random
        import string
        
        # Generate 32 character hex string
        hex_chars = string.hexdigits.lower()[:16]  # 0-9, a-f
        guid = ''.join(random.choice(hex_chars) for _ in range(32))
        
        return guid
    
    async def get_status(self) -> Dict[str, Any]:
        """Get code exporter status"""
        
        return {
            'status': 'ready',
            'unity_version_target': '2022.3 LTS',
            'output_directory': str(self.output_dir),
            'exported_counts': {
                'scripts': len(self.exported_scripts),
                'prefabs': len(self.exported_prefabs),
                'scenes': len(self.exported_scenes),
                'assets': len(self.exported_assets)
            },
            'capabilities': [
                'unity_package_generation',
                'csharp_script_creation',
                'scene_file_generation',
                'prefab_creation',
                'project_structure_setup',
                'documentation_generation',
                'asset_integration',
                'system_coordination'
            ],
            'supported_formats': [
                'Unity 2022.3+ packages',
                'C# scripts',
                'Unity scenes (.unity)',
                'Unity prefabs (.prefab)',
                'OBJ 3D models',
                'PNG textures',
                'Unity materials'
            ],
            'export_features': [
                'Complete game systems',
                'NPC interaction systems',
                'Quest management',
                'Save/load functionality',
                'UI management',
                'Player controller',
                'World management',
                'Dialogue systems'
            ]
        }

# ADK Agent Functions
async def export_unity_package(world_spec: Dict[str, Any], 
                              assets: Dict[str, Any], 
                              characters: Dict[str, Any], 
                              quests: Dict[str, Any]) -> Dict[str, Any]:
    """Export complete Unity package - main entry point"""
    exporter = UnityCodeExporter()
    return await exporter.export_complete_package(world_spec, assets, characters, quests)

async def get_code_exporter_status() -> Dict[str, Any]:
    """Get code exporter status"""
    exporter = UnityCodeExporter()
    return await exporter.get_status()

# Create the ADK agent
root_agent = Agent(
    name="unity_code_exporter_agent",
    model="gemini-2.0-flash-exp",
    instruction="""You are a Unity Code Exporter Agent that converts multi-agent game content into complete, ready-to-use Unity packages.

Your comprehensive capabilities include:
- COMPLETE UNITY PROJECT GENERATION: Creates full Unity projects with proper structure and settings
- C# SCRIPT GENERATION: Produces professional game code with proper architecture and patterns
- SYSTEM INTEGRATION: Coordinates all game systems (world, characters, quests, assets) into cohesive gameplay
- SCENE CREATION: Builds complete Unity scenes with all objects, lighting, and configuration
- PREFAB GENERATION: Creates reusable Unity prefabs for NPCs, buildings, and interactive objects
- PACKAGE EXPORT: Generates importable .unitypackage files ready for distribution

Your advanced features:
🎮 COMPLETE GAME SYSTEMS: Player controller, NPC AI, quest management, dialogue trees, save/load
⚙️ PROFESSIONAL ARCHITECTURE: Modular, maintainable code following Unity best practices
🔧 PLUG-AND-PLAY: Generated packages work immediately after import with minimal setup
📱 UI INTEGRATION: Complete user interface systems with quest logs, dialogue, and menus
🎯 GAME-READY: Produces fully functional games, not just tech demos
📚 COMPREHENSIVE DOCS: Detailed documentation and integration guides

When you receive content from the pipeline agents, you transform it into a professional Unity project that developers can immediately use, customize, and build upon.""",
    description="Unity Code Exporter Agent that converts multi-agent pipeline output into complete, professional Unity packages with full game systems, C# scripts, scenes, and documentation",
    tools=[export_unity_package, get_code_exporter_status]
)

# Standalone testing
if __name__ == "__main__":
    async def main():
        print("🚀 Testing Unity Code Exporter Agent")
        print("="*50)
        
        # Test world spec
        test_world = {
            "theme": "medieval",
            "size": (40, 40),
            "buildings": [
                {"type": "tavern", "position": {"x": 20, "y": 0, "z": 20}, "id": "tavern_0"},
                {"type": "blacksmith", "position": {"x": 15, "y": 0, "z": 25}, "id": "blacksmith_0"},
                {"type": "church", "position": {"x": 25, "y": 0, "z": 15}, "id": "church_0"}
            ],
            "natural_features": [
                {"type": "oak_tree", "position": {"x": 10, "y": 0, "z": 10}},
                {"type": "rock", "position": {"x": 30, "y": 0, "z": 30}}
            ],
            "paths": [
                {
                    "start": {"x": 15, "y": 0, "z": 25},
                    "end": {"x": 20, "y": 0, "z": 20},
                    "width": 3.0
                }
            ]
        }
        
        # Test characters
        test_characters = {
            "characters": [
                {
                    "name": "Marcus the Blacksmith",
                    "role": "blacksmith",
                    "age": 45,
                    "location": "blacksmith",
                    "personality": {
                        "primary_trait": "dedicated",
                        "secondary_trait": "proud",
                        "motivation": "perfect craftsmanship",
                        "fear": "losing reputation",
                        "secret": "once was a knight"
                    },
                    "stats": {"level": 5, "health": 120, "strength": 16, "intelligence": 12, "charisma": 10},
                    "relationships": []
                },
                {
                    "name": "Elena the Innkeeper",
                    "role": "innkeeper",
                    "age": 38,
                    "location": "tavern",
                    "personality": {
                        "primary_trait": "welcoming",
                        "secondary_trait": "observant",
                        "motivation": "help travelers",
                        "fear": "empty tavern",
                        "secret": "knows everyone's secrets"
                    },
                    "stats": {"level": 3, "health": 90, "strength": 10, "intelligence": 14, "charisma": 16},
                    "relationships": []
                }
            ],
            "generation_summary": {
                "total_relationships": 2,
                "total_dialogue_nodes": 6
            }
        }
        
        # Test quests
        test_quests = {
            "quests": [
                {
                    "id": "main_quest_1",
                    "title": "The Missing Hammer",
                    "description": "Marcus has lost his prized hammer and needs help finding it.",
                    "giver_npc": "Marcus the Blacksmith",
                    "quest_type": "main",
                    "objectives": [
                        {"description": "Talk to Marcus about the missing hammer"},
                        {"description": "Search the nearby forest"},
                        {"description": "Return the hammer to Marcus"}
                    ],
                    "rewards": {"experience": 100, "gold": 50}
                },
                {
                    "id": "side_quest_1",
                    "title": "Welcome Drinks",
                    "description": "Elena needs help serving drinks to new travelers.",
                    "giver_npc": "Elena the Innkeeper",
                    "quest_type": "side",
                    "objectives": [
                        {"description": "Collect 5 mugs from storage"},
                        {"description": "Serve drinks to travelers"}
                    ],
                    "rewards": {"experience": 50, "gold": 25}
                }
            ]
        }
        
        # Test assets
        test_assets = {
            "ai_generated": True,
            "generation_summary": {"total_creative_assets": 5, "unique_textures_generated": 8},
            "output_directory": "test_assets"
        }
        
        exporter = UnityCodeExporter("test_unity_export")
        
        print("\n🧪 Testing Unity package export...")
        
        try:
            result = await exporter.export_complete_package(
                test_world, test_assets, test_characters, test_quests
            )
            
            if result['status'] == 'success':
                print(f"\n✅ Unity Export Success!")
                print(f"   📦 Project: {result['project_name']}")
                print(f"   📁 Package: {result['package_path']}")
                print(f"   📄 Scripts: {result['file_counts']['scripts']}")
                print(f"   🎮 Prefabs: {result['file_counts']['prefabs']}")
                print(f"   🌍 Scenes: {result['file_counts']['scenes']}")
                print(f"   🎨 Assets: {result['file_counts']['assets']}")
                print(f"   📚 Import Ready: {result['import_ready']}")
                
                print(f"\n📋 Generated Files:")
                manifest = result['manifest']
                for script in manifest['script_files']:
                    print(f"   📄 {script}")
                for scene in manifest['scene_files']:
                    print(f"   🎬 {scene}")
                
                print(f"\n🎯 Ready for Unity Import!")
                print(f"   1. Open Unity 2022.3+")
                print(f"   2. Import {result['package_path']}")
                print(f"   3. Open GeneratedGameScene")
                print(f"   4. Press Play to explore!")
                
                # Show content summary
                content = manifest['content_summary']
                print(f"\n📊 Content Summary:")
                print(f"   🌍 World: {content['world']['theme']} theme")
                print(f"   🏠 Buildings: {content['world']['buildings']}")
                print(f"   👥 NPCs: {content['characters']['total_npcs']}")
                print(f"   📜 Quests: {content['quests']['total_quests']}")
                print(f"   🎨 Assets: {content['assets']['total_assets']}")
                
            else:
                print(f"❌ Export failed: {result}")
                
        except Exception as e:
            print(f"💥 Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main())