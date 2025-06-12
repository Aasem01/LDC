using Microsoft.AspNetCore.Mvc;
using ChatBotAPI.Services;
using System.Threading.Tasks;
using System.Text.Json;

namespace ChatBotAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TestController : ControllerBase
    {
        private readonly IPythonBackendService _pythonBackend;
        private readonly ILogger<TestController> _logger;

        public TestController(IPythonBackendService pythonBackend, ILogger<TestController> logger)
        {
            _pythonBackend = pythonBackend;
            _logger = logger;
        }

        [HttpGet("test-connection")]
        public async Task<IActionResult> TestConnection()
        {
            try
            {
                _logger.LogInformation("Testing connection to Python backend...");
                
                // Test the RAG endpoint with a simple question
                var testRequest = new
                {
                    question = "What is the company's leave policy?",
                    user_id = Guid.NewGuid()
                };

                _logger.LogInformation("Sending test request: {Request}", 
                    JsonSerializer.Serialize(testRequest));

                // Use the correct endpoint path
                var response = await _pythonBackend.PostAsync<object>("rag/rag_chat", testRequest);
                
                _logger.LogInformation("Successfully connected to Python backend. Response: {Response}", 
                    JsonSerializer.Serialize(response));

                return Ok(new { 
                    status = "success", 
                    message = "Successfully connected to Python backend",
                    request = testRequest,
                    response = response 
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error connecting to Python backend: {Error}", ex.Message);
                return StatusCode(500, new { 
                    status = "error", 
                    message = "Failed to connect to Python backend",
                    error = ex.Message,
                    errorType = ex.GetType().Name,
                    stackTrace = ex.StackTrace
                });
            }
        }
    }
} 