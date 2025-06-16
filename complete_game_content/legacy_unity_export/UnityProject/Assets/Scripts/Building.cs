using UnityEngine;

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
}