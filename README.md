# LDC Technical Assessment - HR Policy Chatbot System

A comprehensive chatbot system that provides intelligent responses to HR policy queries using RAG (Retrieval-Augmented Generation) technology. The system consists of a Python-based RAG backend and a .NET-based API service.

## System Architecture

The project is divided into two main components:

1. **Python RAG Backend** (`/`): Handles document processing, embeddings, and RAG-based question answering
2. **.NET ChatBot API** (`/ChatBotAPI`): Provides a RESTful interface and manages chat interactions

## Features

### Python RAG Backend
- Document processing and embedding generation
- Vector storage using ChromaDB
- RAG-based question answering
- Automatic document processing
- Comprehensive logging

### .NET ChatBot API
- RESTful API endpoints
- Integration with Python RAG backend
- Swagger/OpenAPI documentation
- Structured logging
- Error handling

## Prerequisites

- Python 3.9 or higher
- .NET 9.0 SDK
- Virtual environment (recommended for Python)
- Python RAG backend service running on port 9000

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd LDC_task
```

### 2. Python Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. .NET API Setup
```bash
cd ChatBotAPI
dotnet restore
```

## Project Structure

```
LDC_task/
├── app/                    # Python backend application
│   ├── api/               # API routes
│   ├── core/              # Core configuration
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── ChatBotAPI/            # .NET API service
│   ├── Controllers/       # API endpoints
│   ├── Models/            # Data models
│   ├── Utils/             # Utility classes
│   └── Program.cs         # Entry point
├── data/
│   └── raw/              # HR policy documents
├── logs/                  # Application logs
├── main.py               # Python backend entry point
└── requirements.txt      # Python dependencies
```

## Running the Application

### Option 1: Using run_all.bat (Recommended for Windows)
The easiest way to start both services is using the provided batch script:

```bash
# From the root directory
run_all.bat
```

This script will:
1. Start the Python backend service
2. Wait for 5 seconds to ensure the backend is ready
3. Start the .NET API service
4. Open both services in separate command windows

The services will be available at:
- Python Backend: `http://localhost:9000`
- .NET API: `http://localhost:7000`

To stop the services, press Ctrl+C in each command window.

### Option 2: Manual Start

#### 1. Start the Python Backend
```bash
# From the root directory
python main.py
```
The backend will be available at `http://localhost:9000`

#### 2. Start the .NET API
```bash
# From the ChatBotAPI directory
dotnet run
```
The API will be available at `https://localhost:7000`

### 3. Access the Documentation
- Python Backend: `http://localhost:9000/docs`
- .NET API: `https://localhost:7000/swagger`

## API Endpoints

### Python Backend
- `POST /rag/rag_chat`: Process queries and return AI-generated responses
- `GET /chroma/`: ChromaDB management endpoints

### .NET API
- `POST /Ask/Ask`: Send chat messages

## Configuration

### Python Backend
Configuration is managed through environment variables and settings in `app/core/config.py`

### .NET API
Configuration is managed through `appsettings.json` in the ChatBotAPI directory

## Logging

Both components implement comprehensive logging:

### Python Backend
- Logs are stored in the `logs` directory
- Includes API requests, document processing, and system events

### .NET API
- Uses Serilog for structured logging
- Logs are written to files in the `Logs` directory
- Includes daily logs and error-specific logs

## Error Handling

Both components implement robust error handling:
- Structured error responses
- Detailed logging of exceptions
- HTTP status codes following REST conventions