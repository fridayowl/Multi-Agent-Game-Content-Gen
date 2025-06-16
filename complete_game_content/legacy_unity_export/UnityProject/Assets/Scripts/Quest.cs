using System.Collections.Generic;
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
}