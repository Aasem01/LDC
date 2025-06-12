# LDC Technical Assessment - RAG Chatbot System

A Retrieval-Augmented Generation (RAG) based chatbot system that provides intelligent responses to queries about company policies and HR-related information.

## Overview

This project implements a RAG-based chatbot system using FastAPI, LangChain, and ChromaDB. The system processes HR policy documents and provides intelligent responses to user queries by combining retrieval-based and generative AI approaches.

## Features

- Document processing and embedding generation
- Vector storage using ChromaDB
- RAG-based question answering
- RESTful API endpoints
- Automatic document processing on startup
- CORS support
- Comprehensive logging

## Prerequisites

- Python 3.9 or higher
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd LDC_task
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
LDC_task/
├── app/
│   ├── api/            # API routes and endpoints
│   ├── core/           # Core configuration
│   ├── models/         # Data models
│   ├── services/       # Business logic services
│   └── utils/          # Utility functions
├── data/
│   └── raw/           # Raw document storage
├── logs/              # Application logs
├── main.py           # Application entry point
├── requirements.txt  # Project dependencies
└── run.bat          # Windows startup script
```

## Usage

1. Place your HR policy documents in the `data/raw` directory (supported format: .txt)

2. Start the application:
```bash
# Using Python directly
python main.py

# Or using the provided batch script (Windows)
run.bat
```

3. Access the API documentation at `http://localhost:9000/docs`

## API Endpoints

- `/rag/rag_chat`: Process user queries and return AI-generated responses
- `/chroma/`: ChromaDB management endpoints

## Dependencies

Key dependencies include:
- FastAPI: Web framework
- LangChain: RAG implementation
- ChromaDB: Vector database
- Transformers: Embedding models
- OpenAI: Language model integration

## Configuration

The application can be configured through environment variables or the settings module in `app/core/config.py`.

## Logging

Logs are stored in the `logs` directory and include:
- API request logs
- Document processing logs
- System startup and shutdown events
