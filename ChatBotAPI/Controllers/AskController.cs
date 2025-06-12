using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Text.Json;
using ChatBotAPI.Models;
using ChatBotAPI.Data;
using ChatBotAPI.Utils;
using System;
using System.Text.Json.Serialization;

namespace ChatBotAPI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class AskController : ControllerBase
    {
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly ILogger<AskController> _logger;
        private readonly JsonSerializerOptions _jsonOptions;

        public AskController(
            IHttpClientFactory httpClientFactory,
            ILogger<AskController> logger)
        {
            _httpClientFactory = httpClientFactory;
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
                    Loggers.AskController.Info($"Generated new UserId: {query.UserId}");
                }

                Loggers.AskController.Info($"Received question from UserId {query.UserId}: {query.Question}");

                var client = _httpClientFactory.CreateClient("PythonBackend");
                Loggers.PythonBackend.Info($"Sending request to Python backend for UserId {query.UserId}: {query.Question}");
                
                // Create request object matching Python backend's expected format exactly
                var request = new
                {
                    question = query.Question,
                    user_id = query.UserId.ToString("D") // Format as "00000000-0000-0000-0000-000000000000"
                };

                // Log the exact request being sent
                var requestJson = JsonSerializer.Serialize(request, _jsonOptions);
                Loggers.PythonBackend.Info($"Request payload: {requestJson}");

                var response = await client.PostAsJsonAsync("/rag/rag_chat", request, _jsonOptions);

                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    var error = $"Python backend returned {response.StatusCode}. Content: {errorContent}";
                    Loggers.PythonBackend.Error($"Error for UserId {query.UserId}: {error}");
                    return StatusCode(500, "Error communicating with Python backend");
                }

                var chatbotResponse = await response.Content.ReadFromJsonAsync<ChatbotResponse>(_jsonOptions);
                if (chatbotResponse == null)
                {
                    Loggers.PythonBackend.Error($"Invalid response from Python backend for UserId {query.UserId}");
                    return StatusCode(500, "Invalid response from Python backend");
                }

                Loggers.AskController.Info($"Received response for UserId {query.UserId}: {chatbotResponse.Answer}");
                return Ok(chatbotResponse);
            }
            catch (Exception ex)
            {
                Loggers.AskController.Error($"Error processing question for UserId {query.UserId}: {ex.Message}");
                return StatusCode(500, "An error occurred while processing your question");
            }
        }
    }
} 