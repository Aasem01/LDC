using System.Net.Http.Headers;
using System.Text.Json;
using ChatBotAPI.Models;
using Microsoft.Extensions.Options;

namespace ChatBotAPI.Services
{
    public interface IPythonBackendService
    {
        Task<T?> PostAsync<T>(string endpoint, object data);
        Task<T?> GetAsync<T>(string endpoint);
        Task<T?> PostMultipartAsync<T>(string endpoint, MultipartFormDataContent content);
    }

    public class PythonBackendService : IPythonBackendService
    {
        private readonly HttpClient _httpClient;
        private readonly PythonBackendSettings _settings;
        private readonly ILogger<PythonBackendService> _logger;

        public PythonBackendService(
            HttpClient httpClient,
            IOptions<PythonBackendSettings> settings,
            ILogger<PythonBackendService> logger)
        {
            _httpClient = httpClient;
            _settings = settings.Value;
            _logger = logger;

            // Configure HttpClient
            var baseUrl = _settings.BaseUrl.TrimEnd('/');
            _httpClient.BaseAddress = new Uri(baseUrl);
            _logger.LogInformation("Setting base URL to: {BaseUrl}", baseUrl);

            _httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
            
            // Clear any existing headers to avoid duplicates
            _httpClient.DefaultRequestHeaders.Remove("X-API-Key");
            _httpClient.DefaultRequestHeaders.Remove("Origin");
            
            // Add API key header
            _httpClient.DefaultRequestHeaders.Add("X-API-Key", _settings.ApiKey);
            
            // Add Origin header to match allowed origins
            _httpClient.DefaultRequestHeaders.Add("Origin", "http://localhost:7000");
            
            _logger.LogInformation("PythonBackendService initialized with API key: {ApiKey}", 
                _settings.ApiKey.Substring(0, 10) + "..."); // Log only first 10 chars for security
        }

        private string GetFullUrl(string endpoint)
        {
            // Ensure endpoint starts with a forward slash
            endpoint = endpoint.StartsWith("/") ? endpoint : "/" + endpoint;
            var fullUrl = $"{_httpClient.BaseAddress}{endpoint}";
            _logger.LogDebug("Full URL: {FullUrl}", fullUrl);
            return fullUrl;
        }

        public async Task<T?> PostAsync<T>(string endpoint, object data)
        {
            try
            {
                var fullUrl = GetFullUrl(endpoint);
                _logger.LogDebug("Making POST request to {FullUrl} with API key: {ApiKey}", 
                    fullUrl, 
                    _httpClient.DefaultRequestHeaders.GetValues("X-API-Key").FirstOrDefault()?.Substring(0, 10) + "...");

                var json = JsonSerializer.Serialize(data);
                var content = new StringContent(json, System.Text.Encoding.UTF8, "application/json");
                
                _logger.LogDebug("Request payload: {Payload}", json);
                
                var response = await _httpClient.PostAsync(endpoint, content);
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("Error response from Python backend: {StatusCode} - {Content}", 
                        response.StatusCode, errorContent);
                    response.EnsureSuccessStatusCode();
                }
                
                var responseContent = await response.Content.ReadAsStringAsync();
                _logger.LogDebug("Response content: {Content}", responseContent);
                
                return JsonSerializer.Deserialize<T>(responseContent);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error making POST request to Python backend: {Endpoint}", endpoint);
                throw;
            }
        }

        public async Task<T?> PostMultipartAsync<T>(string endpoint, MultipartFormDataContent content)
        {
            try
            {
                var fullUrl = GetFullUrl(endpoint);
                _logger.LogDebug("Making multipart POST request to {FullUrl}", fullUrl);
                
                var response = await _httpClient.PostAsync(endpoint, content);
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("Error response from Python backend: {StatusCode} - {Content}", 
                        response.StatusCode, errorContent);
                    response.EnsureSuccessStatusCode();
                }
                
                var responseContent = await response.Content.ReadAsStringAsync();
                _logger.LogDebug("Response content: {Content}", responseContent);
                
                return JsonSerializer.Deserialize<T>(responseContent);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error making multipart POST request to Python backend: {Endpoint}", endpoint);
                throw;
            }
        }

        public async Task<T?> GetAsync<T>(string endpoint)
        {
            try
            {
                var fullUrl = GetFullUrl(endpoint);
                _logger.LogDebug("Making GET request to {FullUrl} with API key: {ApiKey}", 
                    fullUrl, 
                    _httpClient.DefaultRequestHeaders.GetValues("X-API-Key").FirstOrDefault()?.Substring(0, 10) + "...");

                var response = await _httpClient.GetAsync(endpoint);
                
                if (!response.IsSuccessStatusCode)
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    _logger.LogError("Error response from Python backend: {StatusCode} - {Content}", 
                        response.StatusCode, errorContent);
                    response.EnsureSuccessStatusCode();
                }
                
                var responseContent = await response.Content.ReadAsStringAsync();
                _logger.LogDebug("Response content: {Content}", responseContent);
                
                return JsonSerializer.Deserialize<T>(responseContent);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error making GET request to Python backend: {Endpoint}", endpoint);
                throw;
            }
        }
    }
} 