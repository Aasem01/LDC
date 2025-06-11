# LDC Technical Assessment – AI Engineer Task  
**Author:** Aasem Said
**Project Type:** Retrieval-Augmented Generation (RAG) Chatbot System  
**Stack:** .NET Web API, Python FastAPI, LangChain, ChromaDB, SQLite/SQL Server  

---

## 📌 Objective  
This project implements a RAG-based chatbot capable of answering user questions based on a provided document corpus. The solution integrates a .NET Web API, a Python backend using LangChain, and a SQL database to store user-chatbot interactions.

---

## 📅 5-Days Implementation Plan

### Day 1 – Python RAG Core Setup  
**Goal:** Develop the knowledge base and retrieval pipeline using LangChain.

**Tasks:**  
- Load `.txt` documents using `LangChain`.  
- Split text.  
- Generate embeddings (OpenAI or local model).  
- Store vectors in ChromaDB with persistence.  
- Scaffold FastAPI with a `/query` POST route.  
- Test document retrieval.

**Focus Areas (not mentioned yet):** Chunk size tuning, persistence path setup, offline readiness.

---

### Day 2 – LangChain + FastAPI Completion  
**Goal:** Complete RAG integration with FastAPI and enable full response generation.

**Tasks:**  
- Implement `RetrievalQA` or `ConversationalRetrievalChain` with memory.  
- Integrate LLM (OpenAI or Ollama) for response generation.  
- Finalize FastAPI route to handle incoming questions.  
- Return JSON response (including optional document metadata).  
- Add request validation and CORS headers.  
- Perform end-to-end test of the RAG pipeline.

**Focus Areas:** Prompt tuning, context management, memory persistence.

---

### Day 3 – .NET Web API & SQL Integration  
(i am not sure of my choices in this section, i might change them while i am implementing the task)

**Goal:** Connect .NET frontend to Python backend and SQL database.

**Tasks:**  
- Scaffold .NET Web API project (Minimal API or MVC).  
- Create async POST endpoint for user input.  
- Use `HttpClient` to communicate with Python FastAPI.  
- Return chatbot response to user.  
- Build local SQL DB (`UserQueries`, `ChatbotResponses`).  
- Log user input and response into database.

**Focus Areas:** Asynchronous logic, schema design, clean data contracts.

---

### Day 4 – Logging, Error Handling & Final Testing  
**Goal:** Harden the application and test under real conditions.

**Tasks:**  
- Finalize DB logging (link queries and responses via foreign key).  
- Implement structured logging (file/console) in both services.  
- Add error handling for common failure cases.  
- Perform QA with sample user queries.  
- (Optional) Add helper DB reset and testing scripts.

**Focus Areas:** Fault tolerance, test coverage, traceability.

---

### Day 5 – Buffer / Enhancement Day  


**Tasks:**
1- re-visit the code and enhance it with refactoring and cleaning.  


---

## 🛠️ Tech Stack  
| Component           | Technology              |
|--------------------|--------------------------|
| Document Embedding | LangChain + Sentence Transformers / OpenAI |
| Vector Store       | ChromaDB                 |
| Backend Service    | Python FastAPI           |
| Retrieval Pipeline | LangChain  |
| Frontend API       | .NET Web API (.NET 7+)   |
| Database           | SQLite or SQL Server     |

---

## 📂 Deliverables  
- Python FastAPI backend with RAG implementation  
- .NET Web API gateway with SQL logging  
- SQL schema (`.sql` file or EF Core models)  
- README documentation  
- Optional: Docker setup and helper scripts  

---
