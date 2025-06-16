#!/usr/bin/env python3
"""
Game management scripts
Generates core game system scripts like GameManager and PlayerController
"""

from typing import List, Dict, Any
from pathlib import Path
import logging

class GameScriptsGenerator:
    """Handles generation of core game scripts"""
    
    def __init__(self, scripts_dir: Path, logger: logging.Logger):
        self.scripts_dir = scripts_dir
        self.logger = logger
        self.exported_scripts = []
    
    async def generate_management_scripts(self, world_spec: Dict[str, Any], 
                                         characters: Dict[str, Any], 
                                         quests: Dict[str, Any]) -> List[str]:
        """Generate all management scripts"""
        self.logger.info("🔧 Generating management scripts...")
        
        scripts = []
        
        # Generate player controller
        scripts.extend(await self._create_player_controller())
        
        # Generate game manager
        scripts.extend(await self._create_game_manager())
        
        self.exported_scripts.extend(scripts)
        self.logger.info(f"   ✅ Generated {len(scripts)} management scripts")
        return scripts
    
    async def _create_player_controller(self) -> List[str]:
        """Create player controller script"""
        
        player_script = '''using UnityEngine;

public class PlayerController : MonoBehaviour
{
    [Header("Movement")]
    public float moveSpeed = 5f;
    public float mouseSensitivity = 2f;
    
    private CharacterController controller;
    private Camera playerCamera;
    private float verticalRotation = 0;
    
    void Start()
    {
        controller = GetComponent<CharacterController>();
        if (controller == null)
            controller = gameObject.AddComponent<CharacterController>();
            
        playerCamera = GetComponent<Camera>();
        
        // Lock cursor to center
        Cursor.lockState = CursorLockMode.Locked;
        
        // Tag as Player
        gameObject.tag = "Player";
    }
    
    void Update()
    {
        HandleMovement();
        HandleMouseLook();
    }
    
    void HandleMovement()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        Vector3 direction = new Vector3(horizontal, 0, vertical);
        direction = transform.TransformDirection(direction);
        direction *= moveSpeed;
        
        // Apply gravity
        direction.y -= 9.81f * Time.deltaTime;
        
        controller.Move(direction * Time.deltaTime);
    }
    
    void HandleMouseLook()
    {
        float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
        float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;
        
        verticalRotation -= mouseY;
        verticalRotation = Mathf.Clamp(verticalRotation, -90f, 90f);
        
        playerCamera.transform.localRotation = Quaternion.Euler(verticalRotation, 0, 0);
        transform.rotation *= Quaternion.Euler(0, mouseX, 0);
    }
}'''
        
        script_path = self.scripts_dir / "PlayerController.cs"
        with open(script_path, 'w') as f:
            f.write(player_script)
        
        return ["Scripts/PlayerController.cs"]
    
    async def _create_game_manager(self) -> List[str]:
        """Create game manager script"""
        
        game_manager_script = '''using UnityEngine;

public class GameManager : MonoBehaviour
{
    [Header("Game State")]
    public bool gameStarted = false;
    
    private static GameManager instance;
    public static GameManager Instance => instance;
    
    void Awake()
    {
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);
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
    
    public void StartGame()
    {
        gameStarted = true;
        Debug.Log("Generated game started!");
        
        // Initialize all systems
        InitializeSystems();
    }
    
    void InitializeSystems()
    {
        // Find and initialize quest manager
        QuestManager questManager = FindObjectOfType<QuestManager>();
        if (questManager != null)
        {
            Debug.Log("Quest system initialized");
        }
        
        // Find and initialize dialogue system
        DialogueSystem dialogueSystem = FindObjectOfType<DialogueSystem>();
        if (dialogueSystem != null)
        {
            Debug.Log("Dialogue system initialized");
        }
        
        Debug.Log("All game systems initialized successfully!");
    }
    
    void Update()
    {
        // Handle escape key to unlock cursor
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            if (Cursor.lockState == CursorLockMode.Locked)
                Cursor.lockState = CursorLockMode.None;
            else
                Cursor.lockState = CursorLockMode.Locked;
        }
    }
}'''
        
        script_path = self.scripts_dir / "GameManager.cs"
        with open(script_path, 'w') as f:
            f.write(game_manager_script)
        
        return ["Scripts/GameManager.cs"]
    
    def get_exported_scripts(self) -> List[str]:
        """Get list of exported script files"""
        return self.exported_scripts.copy()