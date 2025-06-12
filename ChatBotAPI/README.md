# ChatBot API

A .NET-based API service that serves as an intermediary between the frontend and the Python RAG backend. This API provides a structured interface for handling chat interactions and managing conversation history.

## Overview

The ChatBot API is built using ASP.NET Core and provides a RESTful interface for chat interactions. It communicates with a Python-based RAG backend service to process queries and generate responses about company policies and HR-related information.

## Features

- RESTful API endpoints for chat interactions
- Integration with Python RAG backend
- Swagger/OpenAPI documentation
- HTTPS support
- Structured logging with Serilog
- Entity Framework Core for data access

## Prerequisites

- .NET 9.0 SDK
- Python RAG backend service running on port 9000

## Project Structure

```
ChatBotAPI/
├── Controllers/        # API endpoints
├── Data/              # Database context and configurations
├── Models/            # Data models and DTOs
├── Utils/             # Utility classes and helpers
├── Properties/        # Project properties
├── Program.cs         # Application entry point
└── appsettings.json   # Application configuration
```

## Configuration

The application can be configured through `appsettings.json`:

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Your_SQL_Server_Connection_String"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

## API Endpoints

The API provides the following endpoints:

- `POST /api/chat`: Send a chat message and receive a response
- `GET /api/chat/history`: Retrieve chat history
- `DELETE /api/chat/history`: Clear chat history

## Dependencies

Key NuGet packages:
- Microsoft.AspNetCore.OpenApi
- Microsoft.EntityFrameworkCore
- Microsoft.EntityFrameworkCore.SqlServer
- Serilog.Extensions.Logging.File
- Swashbuckle.AspNetCore

## Development Setup

1. Clone the repository and navigate to the ChatBotAPI directory:
```bash
cd ChatBotAPI
```

2. Restore dependencies:
```bash
dotnet restore
```

3. Update the connection string in `appsettings.json` to point to your SQL Server instance

4. Run the application:
```bash
dotnet run
```

5. Access the Swagger documentation at `https://localhost:7000/swagger`

## Integration with Python Backend

The API communicates with the Python RAG backend service running on `http://localhost:9000`. Ensure the Python service is running before starting the ChatBot API.

## Logging

The application uses Serilog for structured logging. Logs are written to files in the `Logs` directory with the following format:
- `log-{date}.txt`: Daily log files
- `error-{date}.txt`: Error-specific log files

## Error Handling

The API implements global error handling with:
- Structured error responses
- Detailed logging of exceptions
- HTTP status codes following REST conventions