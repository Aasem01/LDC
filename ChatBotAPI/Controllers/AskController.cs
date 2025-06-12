using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Text.Json;
using ChatBotAPI.Models;
using ChatBotAPI.Data;

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
        public async Task<IActionResult> Ask([FromBody] UserQuery query)
        {
            try
            {
                var client = _httpClientFactory.CreateClient("PythonBackend");
                var response = await client.PostAsJsonAsync("/rag/rag_chat", query);

                if (!response.IsSuccessStatusCode)
                {
                    _logger.LogError($"Python backend returned {response.StatusCode}");
                    return StatusCode(500, "Error communicating with Python backend");
                }

                var chatbotResponse = await response.Content.ReadFromJsonAsync<ChatbotResponse>();
                if (chatbotResponse == null)
                {
                    return StatusCode(500, "Invalid response from Python backend");
                }

                return Ok(chatbotResponse);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing question");
                return StatusCode(500, "An error occurred while processing your question");
            }
        }
    }
} 