using System;
using System.ComponentModel.DataAnnotations;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace ChatBotAPI.Models
{
    public class Interaction
    {
        [Key]
        public int Id { get; set; }
        
        [Required]
        public string UserId { get; set; } = string.Empty;
        
        [Required]
        public string DocumentId { get; set; } = string.Empty;
        
        [Required]
        public string Query { get; set; } = string.Empty;
        
        [Required]
        public string Response { get; set; } = string.Empty;
        
        public DateTime Timestamp { get; set; }
        
        [Required]
        public string Metadata { get; set; } = string.Empty;
    }

    public class DocumentMetadata
    {
        [JsonPropertyName("content_type")]
        public string ContentType { get; set; } = string.Empty;

        [JsonPropertyName("source")]
        public string Source { get; set; } = string.Empty;

        [JsonPropertyName("created_at")]
        public string CreatedAt { get; set; } = string.Empty;

        [JsonPropertyName("updated_at")]
        public string UpdatedAt { get; set; } = string.Empty;

        [JsonPropertyName("document_type")]
        public string DocumentType { get; set; } = string.Empty;

        [JsonPropertyName("file_modified_at")]
        public string FileModifiedAt { get; set; } = string.Empty;
    }

    public class SourceDocument
    {
        [JsonPropertyName("content")]
        public string Content { get; set; } = string.Empty;

        [JsonPropertyName("metadata")]
        public DocumentMetadata Metadata { get; set; } = new DocumentMetadata();
    }

    public class InteractionCreate
    {
        [Required]
        [JsonPropertyName("userId")]
        public string UserId { get; set; } = string.Empty;

        [Required]
        [JsonPropertyName("query")]
        public string Query { get; set; } = string.Empty;

        [Required]
        [JsonPropertyName("answer")]
        public string Answer { get; set; } = string.Empty;

        [Required]
        [JsonPropertyName("timestamp")]
        public string Timestamp { get; set; } = string.Empty;

        [Required]
        [JsonPropertyName("source_documents")]
        public List<SourceDocument> SourceDocuments { get; set; } = new List<SourceDocument>();
    }

    public class InteractionResponse
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("user_id")]
        public string UserId { get; set; } = string.Empty;

        [JsonPropertyName("query")]
        public string Query { get; set; } = string.Empty;

        [JsonPropertyName("answer")]
        public string Answer { get; set; } = string.Empty;

        [JsonPropertyName("timestamp")]
        public string Timestamp { get; set; } = string.Empty;

        [JsonPropertyName("document_types")]
        public List<string> DocumentTypes { get; set; } = new List<string>();

        [JsonPropertyName("sources")]
        public List<string> Sources { get; set; } = new List<string>();

        [JsonPropertyName("created_at")]
        public string CreatedAt { get; set; } = string.Empty;

        [JsonPropertyName("updated_at")]
        public string UpdatedAt { get; set; } = string.Empty;
    }

    public class InteractionList
    {
        [JsonPropertyName("interactions")]
        public List<InteractionResponse> interactions { get; set; } = new List<InteractionResponse>();

        [JsonPropertyName("total")]
        public int total { get; set; }
    }
} 