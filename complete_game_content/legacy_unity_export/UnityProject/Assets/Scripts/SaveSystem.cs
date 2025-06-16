using System.IO;
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
}