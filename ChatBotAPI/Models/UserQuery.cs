using System;

namespace ChatBotAPI.Models
{
    public class UserQuery
    {
        public string Question { get; set; } = string.Empty;
        public string UserId { get; set; } = string.Empty;
    }
} 