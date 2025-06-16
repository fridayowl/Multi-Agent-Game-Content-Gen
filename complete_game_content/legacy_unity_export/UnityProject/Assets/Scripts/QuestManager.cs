using System.Collections.Generic;
using UnityEngine;

namespace GeneratedGame
{
    /// <summary>
    /// Manages all quests and quest progression
    /// </summary>
    public class QuestManager : MonoBehaviour
    {
        [Header("Quest Configuration")]
        public int totalQuests = 7;
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
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }
        }
        
        public void Initialize()
        {
            Debug.Log("Initializing Quest Manager...");
            InitializeQuests();
        }
        
        void InitializeQuests()
        {
            // Initialize all quests from generated data

            // Quest: The Village Crisis
            {
                Quest quest = new Quest();
                quest.questId = "main_quest_1_sir_dara";
                quest.title = "The Village Crisis";
                quest.description = "Sir Dara needs help resolving a crisis that threatens the village.";
                quest.giverNPC = "Sir Dara";
                quest.objectiveCount = 4;
                quest.experienceReward = 100;
                quest.goldReward = 50;
                availableQuests.Add(quest);
            }
            // Quest: Ancient Secrets
            {
                Quest quest = new Quest();
                quest.questId = "main_quest_2_sir_edwin";
                quest.title = "Ancient Secrets";
                quest.description = "Sir Edwin has discovered something that could change everything.";
                quest.giverNPC = "Sir Edwin";
                quest.objectiveCount = 4;
                quest.experienceReward = 200;
                quest.goldReward = 100;
                availableQuests.Add(quest);
            }
            // Quest: Personal Favor
            {
                Quest quest = new Quest();
                quest.questId = "side_quest_1_sir_dara";
                quest.title = "Personal Favor";
                quest.description = "Sir Dara needs help with a personal matter.";
                quest.giverNPC = "Sir Dara";
                quest.objectiveCount = 3;
                quest.experienceReward = 50;
                quest.goldReward = 25;
                availableQuests.Add(quest);
            }
            // Quest: Personal Favor
            {
                Quest quest = new Quest();
                quest.questId = "side_quest_2_sir_edwin";
                quest.title = "Personal Favor";
                quest.description = "Sir Edwin needs help with a personal matter.";
                quest.giverNPC = "Sir Edwin";
                quest.objectiveCount = 3;
                quest.experienceReward = 50;
                quest.goldReward = 25;
                availableQuests.Add(quest);
            }
            // Quest: Personal Favor
            {
                Quest quest = new Quest();
                quest.questId = "side_quest_3_lady_fiona";
                quest.title = "Personal Favor";
                quest.description = "Lady Fiona needs help with a personal matter.";
                quest.giverNPC = "Lady Fiona";
                quest.objectiveCount = 3;
                quest.experienceReward = 50;
                quest.goldReward = 25;
                availableQuests.Add(quest);
            }
            
            Debug.Log($"Initialized {availableQuests.Count} available quests");
        }
        
        public void StartQuest(string questId)
        {
            Quest questToStart = availableQuests.Find(q => q.questId == questId);
            if (questToStart != null)
            {
                availableQuests.Remove(questToStart);
                activeQuests.Add(questToStart);
                questToStart.StartQuest();
                
                Debug.Log($"Started quest: {questToStart.title}");
                ShowQuestNotification($"Quest Started: {questToStart.title}", Color.yellow);
            }
        }
        
        public void CompleteQuest(string questId)
        {
            Quest questToComplete = activeQuests.Find(q => q.questId == questId);
            if (questToComplete != null)
            {
                activeQuests.Remove(questToComplete);
                completedQuests.Add(questToComplete);
                questToComplete.CompleteQuest();
                
                Debug.Log($"Completed quest: {questToComplete.title}");
                ShowQuestNotification($"Quest Completed: {questToComplete.title}", Color.green);
                
                // Give rewards
                GiveQuestRewards(questToComplete);
            }
        }
        
        public void UpdateQuestProgress(string questId, string objectiveId)
        {
            Quest quest = activeQuests.Find(q => q.questId == questId);
            if (quest != null)
            {
                quest.UpdateObjective(objectiveId);
                
                if (quest.IsCompleted())
                {
                    CompleteQuest(questId);
                }
            }
        }
        
        void GiveQuestRewards(Quest quest)
        {
            // Implement reward system
            Debug.Log($"Giving rewards for quest: {quest.title}");
            
            // Add experience, gold, items, etc.
            if (quest.experienceReward > 0)
            {
                // Give experience
                Debug.Log($"Gained {quest.experienceReward} experience!");
            }
            
            if (quest.goldReward > 0)
            {
                // Give gold
                Debug.Log($"Gained {quest.goldReward} gold!");
            }
        }
        
        void ShowQuestNotification(string message, Color color)
        {
            Debug.Log($"Quest Notification: {message}");
            
            if (questNotificationUI != null)
            {
                // Show UI notification
                questNotificationUI.SetActive(true);
                // Set notification text and color
            }
        }
        
        public Quest GetQuestById(string questId)
        {
            // Search in all quest lists
            Quest quest = availableQuests.Find(q => q.questId == questId);
            if (quest != null) return quest;
            
            quest = activeQuests.Find(q => q.questId == questId);
            if (quest != null) return quest;
            
            quest = completedQuests.Find(q => q.questId == questId);
            return quest;
        }
        
        public bool IsQuestCompleted(string questId)
        {
            return completedQuests.Exists(q => q.questId == questId);
        }
        
        public bool IsQuestActive(string questId)
        {
            return activeQuests.Exists(q => q.questId == questId);
        }
    }
}