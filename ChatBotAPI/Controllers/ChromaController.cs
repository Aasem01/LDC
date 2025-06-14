using Microsoft.AspNetCore.Mvc;
using ChatBotAPI.Models;
using ChatBotAPI.Services;
using System.Text.Json;

namespace ChatBotAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ChromaController : ControllerBase
    {
        private readonly IPythonBackendService _pythonBackend;
        private readonly ILogger<ChromaController> _logger;
        private readonly JsonSerializerOptions _jsonOptions;

        public ChromaController(
            IPythonBackendService pythonBackend,
            ILogger<ChromaController> logger)
        {
            _pythonBackend = pythonBackend;
            _logger = logger;
            _jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = true
            };
        }

        [HttpGet("documents")]
        public async Task<ActionResult<DocumentListResponse>> GetAllDocuments()
        {
            try
            {
                var response = await _pythonBackend.GetAsync<DocumentListResponse>("chroma/documents");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting all documents");
                return StatusCode(500, new { message = "Error retrieving documents", error = ex.Message });
            }
        }

        [HttpGet("info")]
        public async Task<ActionResult<ChromaInfoResponse>> GetChromaInfo()
        {
            try
            {
                var response = await _pythonBackend.GetAsync<ChromaInfoResponse>("chroma/info");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting Chroma info");
                return StatusCode(500, new { message = "Error retrieving Chroma info", error = ex.Message });
            }
        }

        [HttpDelete("all")]
        public async Task<ActionResult> DeleteAllDocuments()
        {
            try
            {
                await _pythonBackend.PostAsync<object>("chroma/all", new { });
                return Ok(new { message = "All documents deleted successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting all documents");
                return StatusCode(500, new { message = "Error deleting documents", error = ex.Message });
            }
        }

        [HttpPost("sync")]
        public async Task<ActionResult<ProcessingStats>> SyncDocuments([FromQuery] bool force = false)
        {
            try
            {
                var response = await _pythonBackend.PostAsync<ProcessingStats>("chroma/sync", new { force });
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error syncing documents");
                return StatusCode(500, new { message = "Error syncing documents", error = ex.Message });
            }
        }

        [HttpPost("text")]
        public async Task<ActionResult> AddText([FromBody] DocumentRequest request)
        {
            try
            {
                await _pythonBackend.PostAsync<object>("chroma/text", request);
                return Ok(new { message = "Text added successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error adding text");
                return StatusCode(500, new { message = "Error adding text", error = ex.Message });
            }
        }

        [HttpPost("upload")]
        public async Task<ActionResult<UploadResponse>> UploadDocument(IFormFile file)
        {
            try
            {
                if (file == null || file.Length == 0)
                {
                    return BadRequest(new { message = "No file uploaded" });
                }

                if (!file.FileName.EndsWith(".txt", StringComparison.OrdinalIgnoreCase))
                {
                    return BadRequest(new { message = "Only .txt files are supported" });
                }

                using var content = new MultipartFormDataContent();
                using var fileContent = new StreamContent(file.OpenReadStream());
                content.Add(fileContent, "file", file.FileName);

                var response = await _pythonBackend.PostMultipartAsync<UploadResponse>("chroma/upload", content);
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error uploading document");
                return StatusCode(500, new { message = "Error uploading document", error = ex.Message });
            }
        }

        [HttpDelete("document/{documentId}")]
        public async Task<ActionResult> DeleteDocument(string documentId)
        {
            try
            {
                await _pythonBackend.PostAsync<object>($"chroma/document/{documentId}", new { });
                return Ok(new { message = $"Document {documentId} deleted successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting document {DocumentId}", documentId);
                return StatusCode(500, new { message = "Error deleting document", error = ex.Message });
            }
        }

        [HttpPut("document/{documentId}")]
        public async Task<ActionResult> UpdateDocument(string documentId, [FromBody] DocumentUpdateRequest request)
        {
            try
            {
                await _pythonBackend.PostAsync<object>($"chroma/document/{documentId}", request);
                return Ok(new { message = $"Document {documentId} updated successfully" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error updating document {DocumentId}", documentId);
                return StatusCode(500, new { message = "Error updating document", error = ex.Message });
            }
        }
    }
} 