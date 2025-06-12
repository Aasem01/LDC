using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Text.Json;
using ChatBotAPI.Models;
using ChatBotAPI.Data;
using ChatBotAPI.Utils;

namespace ChatBotAPI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class AskController : ControllerBase
    {
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly ILogger<AskController> _logger;

        public AskController(
            IHttpClientFactory httpClientFactory,
            ILogger<AskController> logger)
        {
            _httpClientFactory = httpClientFactory;
            _logger = logger;
        }

        [HttpPost]
        [Route("Ask")]
        public async Task<ActionResult<ChatbotResponse>> AskAsync([FromBody] UserQuery query)
        {
            try
            {
                Loggers.AskController.Info($"Received question: {query.Question}");

                var client = _httpClientFactory.CreateClient("PythonBackend");
                Loggers.PythonBackend.Info($"Sending request to Python backend: {query.Question}");
                
                var response = await client.PostAsJsonAsync("/rag/rag_chat", query);

                if (!response.IsSuccessStatusCode)
                {
                    var error = $"Python backend returned {response.StatusCode}";
                    Loggers.PythonBackend.Error(error);
                    return StatusCode(500, "Error communicating with Python backend");
                }

                var chatbotResponse = await response.Content.ReadFromJsonAsync<ChatbotResponse>();
                if (chatbotResponse == null)
                {
                    Loggers.PythonBackend.Error("Invalid response from Python backend");
                    return StatusCode(500, "Invalid response from Python backend");
                }

                Loggers.AskController.Info($"Received response: {chatbotResponse.Answer}");
                return Ok(chatbotResponse);
            }
            catch (Exception ex)
            {
                Loggers.AskController.Error($"Error processing question: {ex.Message}");
                return StatusCode(500, "An error occurred while processing your question");
            }
        }
    }
} 