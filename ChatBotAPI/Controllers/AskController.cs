using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Text.Json;
using ChatBotAPI.Models;
using ChatBotAPI.Data;
using ChatBotAPI.Utils;
using ChatBotAPI.Services;
using System;
using System.Text.Json.Serialization;

namespace ChatBotAPI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class AskController : ControllerBase
    {
        private readonly IPythonBackendService _pythonBackend;
        private readonly ILogger<AskController> _logger;
        private readonly JsonSerializerOptions _jsonOptions;

        public AskController(
            IPythonBackendService pythonBackend,
            ILogger<AskController> logger)
        {
            _pythonBackend = pythonBackend;
            _logger = logger;
            _jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = true
            };
        }

        [HttpPost]
        [Route("Ask")]
        public async Task<ActionResult<ChatbotResponse>> AskAsync([FromBody] UserQuery query)
        {
            try
            {
                // Generate UUID if not provided
                if (query.UserId == Guid.Empty)
                {
                    query.UserId = Guid.NewGuid();
                    _logger.LogInformation($"Generated new UserId: {query.UserId}");
                }

                _logger.LogInformation($"Received question from UserId {query.UserId}: {query.Question}");

                // Create request object matching Python backend's expected format exactly
                var request = new
                {
                    question = query.Question,
                    user_id = query.UserId.ToString("D") // Format as "00000000-0000-0000-0000-000000000000"
                };

                // Log the exact request being sent
                var requestJson = JsonSerializer.Serialize(request, _jsonOptions);
                _logger.LogInformation($"Request payload: {requestJson}");

                var response = await _pythonBackend.PostAsync<ChatbotResponse>("rag/rag_chat", request);

                if (response == null)
                {
                    _logger.LogError($"Invalid response from Python backend for UserId {query.UserId}");
                    return StatusCode(500, "Invalid response from Python backend");
                }

                _logger.LogInformation($"Received response for UserId {query.UserId}: {response.Answer}");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error processing question for UserId {query.UserId}: {ex.Message}");
                return StatusCode(500, new { 
                    message = "An error occurred while processing your question",
                    error = ex.Message,
                    errorType = ex.GetType().Name
                });
            }
        }
    }
} 