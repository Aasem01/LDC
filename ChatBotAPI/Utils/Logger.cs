using System;
using System.IO;
using Microsoft.Extensions.Logging;

namespace ChatBotAPI.Utils
{
    public class Logger
    {
        private readonly ILogger _logger;
        private readonly string _logDirectory;

        public Logger(string name)
        {
            _logDirectory = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "logs");
            Directory.CreateDirectory(_logDirectory);

            var loggerFactory = LoggerFactory.Create(builder =>
            {
                builder
                    .AddConsole()
                    .AddFile(Path.Combine(_logDirectory, $"{name}_{DateTime.Now:yyyyMMdd_HHmmss}.log"));
            });

            _logger = loggerFactory.CreateLogger(name);
        }

        public void Debug(string message) => _logger.LogDebug(message);
        public void Info(string message) => _logger.LogInformation(message);
        public void Warning(string message) => _logger.LogWarning(message);
        public void Error(string message) => _logger.LogError(message);
        public void Critical(string message) => _logger.LogCritical(message);
    }

    // Static logger instances for different components
    public static class Loggers
    {
        public static readonly Logger Api = new("api");
        public static readonly Logger AskController = new("ask_controller");
        public static readonly Logger PythonBackend = new("python_backend");
    }
} 