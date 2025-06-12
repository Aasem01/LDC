using System;
using System.Text.Json.Serialization;

namespace ChatBotAPI.Models
{
    public class ChatbotResponse
    {
        [JsonPropertyName("answer")]
        public string Answer { get; set; } = string.Empty;

        [JsonPropertyName("source_documents")]
        public List<Dictionary<string, object>> SourceDocuments { get; set; } = new();

        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    }
} 