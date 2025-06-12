using System;

namespace ChatBotAPI.Models
{
    public class ChatbotResponse
    {
        public string Answer { get; set; } = string.Empty;
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }
} 