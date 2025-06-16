using System.Collections.Generic;
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
}