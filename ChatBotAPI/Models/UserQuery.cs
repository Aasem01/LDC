using System;

namespace ChatBotAPI.Models
{
    public class UserQuery
    {
        public string Question { get; set; } = string.Empty;
        public Guid UserId { get; set; }
    }
} 