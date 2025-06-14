using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using ChatBotAPI.Models;
using ChatBotAPI.Services;
using System.Text.Json;

namespace ChatBotAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class InteractionsController : ControllerBase
    {
        private readonly IPythonBackendService _pythonBackend;
        private readonly ILogger<InteractionsController> _logger;
        private readonly JsonSerializerOptions _jsonOptions;

        public InteractionsController(
            IPythonBackendService pythonBackend,
            ILogger<InteractionsController> logger)
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
        public async Task<ActionResult<InteractionResponse>> CreateInteraction(InteractionCreate interaction)
        {
            try
            {
                _logger.LogInformation($"Creating interaction for user {interaction.UserId}");

                // Create request object matching Python backend's expected format
                var request = new
                {
                    user_id = interaction.UserId,
                    query = interaction.Query,
                    answer = interaction.Answer,
                    timestamp = interaction.Timestamp,
                    source_documents = interaction.SourceDocuments.Select(d => new
                    {
                        document_type = d.Metadata.DocumentType,
                        source = d.Metadata.Source
                    }).ToList()
                };

                // Log the exact request being sent
                var requestJson = JsonSerializer.Serialize(request, _jsonOptions);
                _logger.LogInformation($"Request payload: {requestJson}");

                var response = await _pythonBackend.PostAsync<InteractionResponse>("sqlite/interactions", request);

                if (response == null)
                {
                    _logger.LogError($"Invalid response from Python backend for user {interaction.UserId}");
                    return StatusCode(500, "Invalid response from Python backend");
                }

                _logger.LogInformation($"Created interaction for user {interaction.UserId}");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error creating interaction for user {interaction.UserId}: {ex.Message}");
                return StatusCode(500, new { 
                    message = "An error occurred while creating the interaction",
                    error = ex.Message,
                    errorType = ex.GetType().Name
                });
            }
        }

        [HttpGet("{interactionId}")]
        public async Task<ActionResult<InteractionResponse>> GetInteraction(int interactionId)
        {
            try
            {
                _logger.LogInformation($"Getting interaction {interactionId}");

                var response = await _pythonBackend.GetAsync<InteractionResponse>($"sqlite/interactions/{interactionId}");

                if (response == null)
                {
                    _logger.LogWarning($"Interaction {interactionId} not found");
                    return NotFound(new { message = "Interaction not found" });
                }

                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error getting interaction {interactionId}: {ex.Message}");
                return StatusCode(500, new { 
                    message = "An error occurred while getting the interaction",
                    error = ex.Message,
                    errorType = ex.GetType().Name
                });
            }
        }

        [HttpGet("user/{userId}")]
        public async Task<ActionResult<InteractionList>> GetUserInteractions(string userId)
        {
            try
            {
                _logger.LogInformation($"Getting interactions for user {userId}");

                var response = await _pythonBackend.GetAsync<InteractionList>($"sqlite/interactions/user/{userId}");

                if (response == null)
                {
                    _logger.LogWarning($"No interactions found for user {userId}");
                    return Ok(new InteractionList { interactions = new List<InteractionResponse>(), total = 0 });
                }

                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error getting interactions for user {userId}: {ex.Message}");
                return StatusCode(500, new { 
                    message = "An error occurred while getting user interactions",
                    error = ex.Message,
                    errorType = ex.GetType().Name
                });
            }
        }

        [HttpGet]
        public async Task<ActionResult<InteractionList>> GetAllInteractions()
        {
            try
            {
                _logger.LogInformation("Getting all interactions");

                var response = await _pythonBackend.GetAsync<InteractionList>("sqlite/interactions");

                if (response == null)
                {
                    _logger.LogWarning("No interactions found");
                    return Ok(new InteractionList { interactions = new List<InteractionResponse>(), total = 0 });
                }

                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error getting all interactions: {ex.Message}");
                return StatusCode(500, new { 
                    message = "An error occurred while getting all interactions",
                    error = ex.Message,
                    errorType = ex.GetType().Name
                });
            }
        }

        [HttpDelete("user/{userId}")]
        public async Task<ActionResult> DeleteUserData(string userId)
        {
            try
            {
                _logger.LogInformation($"Deleting interactions for user {userId}");

                var response = await _pythonBackend.DeleteAsync<object>($"sqlite/interactions/user/{userId}");

                return Ok(new { message = $"Successfully deleted interactions for user {userId}" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error deleting interactions for user {userId}: {ex.Message}");
                return StatusCode(500, new { 
                    message = "An error occurred while deleting user interactions",
                    error = ex.Message,
                    errorType = ex.GetType().Name
                });
            }
        }
    }
} 