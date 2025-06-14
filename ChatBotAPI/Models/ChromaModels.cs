using System.Text.Json.Serialization;

namespace ChatBotAPI.Models
{
    public class DocumentRequest
    {
        [JsonPropertyName("content")]
        public string Content { get; set; } = string.Empty;

        [JsonPropertyName("metadata")]
        public Dictionary<string, object>? Metadata { get; set; }
    }

    public class DocumentUpdateRequest
    {
        [JsonPropertyName("content")]
        public string Content { get; set; } = string.Empty;

        [JsonPropertyName("metadata")]
        public Dictionary<string, object>? Metadata { get; set; }
    }

    public class DocumentListResponse
    {
        [JsonPropertyName("documents")]
        public List<Document> Documents { get; set; } = new();
    }

    public class Document
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;

        [JsonPropertyName("content")]
        public string Content { get; set; } = string.Empty;

        [JsonPropertyName("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    public class UploadResponse
    {
        [JsonPropertyName("message")]
        public string Message { get; set; } = string.Empty;

        [JsonPropertyName("document_count")]
        public int DocumentCount { get; set; }

        [JsonPropertyName("processed_count")]
        public int ProcessedCount { get; set; }

        [JsonPropertyName("skipped_count")]
        public int SkippedCount { get; set; }

        [JsonPropertyName("filename")]
        public string Filename { get; set; } = string.Empty;

        [JsonPropertyName("status")]
        public string Status { get; set; } = string.Empty;
    }

    public class ChromaInfoResponse
    {
        [JsonPropertyName("collection_count")]
        public int CollectionCount { get; set; }

        [JsonPropertyName("document_count")]
        public int DocumentCount { get; set; }

        [JsonPropertyName("embedding_dimension")]
        public int EmbeddingDimension { get; set; }
    }

    public class ProcessingStats
    {
        [JsonPropertyName("total_files")]
        public int TotalFiles { get; set; }

        [JsonPropertyName("processed_files")]
        public int ProcessedFiles { get; set; }

        [JsonPropertyName("skipped_files")]
        public int SkippedFiles { get; set; }

        [JsonPropertyName("error_files")]
        public int ErrorFiles { get; set; }
    }
} 