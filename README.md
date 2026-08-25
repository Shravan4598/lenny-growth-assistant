# Lenny Growth Assistant

A Retrieval-Augmented Generation (RAG) assistant built around Lenny's newsletter and podcast knowledge base.

The application provides a FastAPI backend that combines transcript retrieval, semantic search, conversation history, PostgreSQL persistence, and a local Ollama LLM.

## Features

* Lenny transcript ingestion
* Transcript cleaning and chunking
* Sentence Transformer embeddings
* FAISS vector similarity search
* Retrieval-Augmented Generation (RAG)
* Local Ollama LLM integration
* PostgreSQL persistence
* Chat sessions
* Conversation history
* Health and readiness endpoints
* Docker Compose deployment
* Alembic database migrations
* Configurable retrieval parameters

---

## Architecture

```text
                         ┌─────────────────────┐
                         │       Client        │
                         │  PowerShell / UI    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │      REST API       │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
      │    Session    │     │      RAG      │     │    Health     │
      │    Service    │     │    Service    │     │   Endpoints   │
      └───────┬───────┘     └───────┬───────┘     └───────────────┘
              │                     │
              ▼                     ▼
      ┌───────────────┐     ┌───────────────┐
      │  PostgreSQL   │     │     FAISS     │
      │   Database    │     │  Vector Index │
      └───────────────┘     └───────┬───────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │     Ollama      │
                           │   qwen2.5:3b    │
                           └─────────────────┘
```

---

## Project Structure

```text
lenny-growth-assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── chat.py
│   │   │   │   ├── health.py
│   │   │   │   ├── llm.py
│   │   │   │   └── sessions.py
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   └── sessions.py
│   │   │   │
│   │   │   └── services/
│   │   │       └── session_service.py
│   │   │
│   │   ├── core/
│   │   ├── db/
│   │   ├── llm/
│   │   ├── rag/
│   │   └── retrieval/
│   │
│   ├── alembic/
│   ├── alembic.ini
│   ├── Dockerfile
│   └── requirements.txt
│
├── data/
│   ├── external/
│   └── processed/
│
├── docker-compose.yml
├── .env
├── .env.example
└── README.md
```

---

# Requirements

Before running the project, install or configure the following:

* Python 3.12+
* Docker Desktop
* Docker Compose
* Ollama
* `qwen2.5:3b` Ollama model

### Verify Python

```powershell
python --version
```

Expected:

```text
Python 3.12.x
```

### Verify Docker

```powershell
docker --version
docker compose version
```

### Verify Ollama

```powershell
ollama --version
```

---

# Ollama Setup

The application uses Ollama as the local LLM provider.

Make sure Ollama is running before starting the application.

Pull the required model:

```powershell
ollama pull qwen2.5:3b
```

Verify that the model is available:

```powershell
ollama list
```

You should see:

```text
qwen2.5:3b
```

You can also test Ollama directly:

```powershell
$body = @{
    model = "qwen2.5:3b"
    prompt = "Explain product-market fit in 3 sentences."
    stream = $false
} | ConvertTo-Json -Compress

Invoke-RestMethod `
    -Uri "http://localhost:11434/api/generate" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

---

# Environment Variables

Create a `.env` file in the project root.

You can use `.env.example` as the template.

```env
APP_NAME=The Lenny Growth Assistant
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
API_PREFIX=/api/v1

DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/lenny_growth

LLM_PROVIDER=ollama
LLM_TIMEOUT_SECONDS=180

OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b

RETRIEVAL_INDEX_PATH=data/processed/lenny.faiss
EMBEDDING_MODEL=all-MiniLM-L6-v2
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.25
```

### Important

When the backend runs inside Docker and Ollama runs on the Windows host, use:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Do **not** use:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

inside the Dockerized backend because `localhost` refers to the backend container itself.

---

# Start the Application

Open PowerShell in the project root:

```powershell
cd C:\Users\shrav\Desktop\lenny-growth-assistant
```

Start the application:

```powershell
docker compose up -d --build
```

Check container status:

```powershell
docker compose ps
```

Expected services should include the backend and PostgreSQL containers.

---

# View Backend Logs

To view the latest backend logs:

```powershell
docker compose logs backend --tail=100
```

To follow logs continuously:

```powershell
docker compose logs -f backend
```

Press `Ctrl+C` to stop following the logs.

---

# Stop the Application

Stop the containers:

```powershell
docker compose down
```

To stop the containers and remove the PostgreSQL volume as well:

```powershell
docker compose down -v
```

> Warning: removing the volume deletes the PostgreSQL data stored in that Docker volume.

---

# Health Check

The backend exposes a health endpoint.

Run:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health" `
    -Method Get
```

The endpoint should return a successful response indicating that the API is running.

---

# Readiness Check

The readiness endpoint checks whether the application dependencies are available.

Run:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health/ready" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

A successful response should look similar to:

```json
{
  "status": "ok",
  "application": "The Lenny Growth Assistant",
  "environment": "development",
  "database": "available",
  "llm_provider": "ollama",
  "model": "qwen2.5:3b"
}
```

---

# API

The API base URL is:

```text
http://localhost:8000/api/v1
```

## Create a Session

Create a new conversation session:

```powershell
$body = @{
    title = "Product Strategy Chat"
    user_metadata = @{
        role = "product_manager"
    }
} | ConvertTo-Json -Compress

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body |
    ConvertTo-Json -Depth 10
```

Save the returned `session_id`. It is required when sending chat messages.

---

## List Sessions

Retrieve existing sessions:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

---

## Chat

Send a question to the RAG assistant.

Replace `YOUR_SESSION_ID` with the ID returned when creating a session.

```powershell
$body = @{
    session_id = "YOUR_SESSION_ID"
    prompt = "What is product-market fit?"
    top_k = 3
} | ConvertTo-Json -Compress

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body |
    ConvertTo-Json -Depth 10
```

The request performs the following operations:

```text
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
Search FAISS Index
      │
      ▼
Retrieve Relevant Chunks
      │
      ▼
Build RAG Prompt
      │
      ▼
Send Prompt to Ollama
      │
      ▼
Generate Answer
      │
      ▼
Store Conversation
```

---

## Get Conversation History

Retrieve the conversation associated with a session:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions/YOUR_SESSION_ID" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

---

# Database

PostgreSQL runs as a Docker service.

### Database Configuration

```text
Host:     postgres
Port:     5432
Database: lenny_growth
User:     postgres
```

The application connects using:

```text
postgresql+psycopg://postgres:postgres@postgres:5432/lenny_growth
```

---

# Database Tables

The application uses PostgreSQL for persistent application data.

Current tables include:

```text
users
sessions
messages
artifacts
alembic_version
```

---

# Inspect Database Tables

Run:

```powershell
docker compose exec postgres `
    psql -U postgres -d lenny_growth -c "\dt"
```

---

# Inspect Database

Open a PostgreSQL shell:

```powershell
docker compose exec postgres `
    psql -U postgres -d lenny_growth
```

Inside PostgreSQL, useful commands include:

```sql
\dt
```

List tables.

```sql
\d sessions
```

Describe the `sessions` table.

```sql
\d messages
```

Describe the `messages` table.

Exit PostgreSQL:

```sql
\q
```

---

# Database Migrations

The project uses Alembic for database migrations.

Check the current migration:

```powershell
docker compose exec backend alembic current
```

View migration history:

```powershell
docker compose exec backend alembic history
```

Run pending migrations:

```powershell
docker compose exec backend alembic upgrade head
```

---

# RAG Pipeline

The RAG pipeline is responsible for retrieving relevant information from Lenny's knowledge base before generating an answer.

```text
                  User Question
                       │
                       ▼
              Query Embedding
                       │
                       ▼
              FAISS Similarity
                    Search
                       │
                       ▼
            Relevant Transcript
                  Chunks
                       │
                       ▼
             Prompt Construction
                       │
                       ▼
                    Ollama
                       │
                       ▼
               Generated Answer
```

## Components

### Embedding Model

```text
all-MiniLM-L6-v2
```

The embedding model converts the user's question and transcript chunks into numerical vectors.

### Vector Store

```text
FAISS
```

FAISS performs similarity search over the transcript embeddings.

### Large Language Model

```text
Ollama
```

### Model

```text
qwen2.5:3b
```

### Retrieval Configuration

```env
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.25
```

`RETRIEVAL_TOP_K` controls how many relevant chunks are retrieved.

`RETRIEVAL_MIN_SCORE` defines the minimum similarity threshold used during retrieval.

---

# Transcript Processing

The knowledge base follows a preprocessing pipeline:

```text
Raw Lenny Transcripts
        │
        ▼
Transcript Cleaning
        │
        ▼
Text Chunking
        │
        ▼
Embedding Generation
        │
        ▼
FAISS Index
        │
        ▼
Ready for Retrieval
```

Processed retrieval artifacts are stored under:

```text
data/processed/
```

The configured FAISS index path is:

```text
data/processed/lenny.faiss
```

---

# API Documentation

When the backend is running, FastAPI provides interactive API documentation.

### Swagger UI

Open:

```text
http://localhost:8000/docs
```

### ReDoc

Open:

```text
http://localhost:8000/redoc
```

These interfaces can be used to inspect and test the API endpoints without PowerShell.

---

# Troubleshooting

## Backend container is not running

Check:

```powershell
docker compose ps
```

Then inspect the logs:

```powershell
docker compose logs backend --tail=200
```

---

## PostgreSQL is unavailable

Check PostgreSQL logs:

```powershell
docker compose logs postgres --tail=200
```

Restart the services:

```powershell
docker compose restart
```

---

## Ollama connection error

First check whether Ollama is running:

```powershell
ollama list
```

Then test the Ollama API:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:11434/api/tags" `
    -Method Get
```

Make sure the required model exists:

```powershell
ollama list
```

If it is missing:

```powershell
ollama pull qwen2.5:3b
```

If the backend is running inside Docker, verify that `.env` contains:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

---

## Check backend can reach Ollama

Run:

```powershell
docker compose exec backend `
    python -c "import urllib.request; print(urllib.request.urlopen('http://host.docker.internal:11434/api/tags').read().decode())"
```

If this succeeds, the Docker container can reach Ollama running on the host machine.

---

## FAISS index not found

Check whether the index exists:

```powershell
Get-ChildItem .\data\processed\
```

The configured path is:

```text
data/processed/lenny.faiss
```

If the index has not been generated yet, run the project's transcript ingestion/indexing process before testing RAG queries.

---

# Development

To rebuild the backend after making code changes:

```powershell
docker compose up -d --build
```

To restart only the backend:

```powershell
docker compose restart backend
```

To inspect all logs:

```powershell
docker compose logs --tail=200
```

---

# Quick Start

For a clean setup, the basic workflow is:

### 1. Start Ollama

Make sure Ollama is running.

### 2. Pull the model

```powershell
ollama pull qwen2.5:3b
```

### 3. Configure environment variables

Create `.env`:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b
```

### 4. Start Docker services

```powershell
docker compose up -d --build
```

### 5. Check containers

```powershell
docker compose ps
```

### 6. Check readiness

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health/ready" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

### 7. Open API documentation

```text
http://localhost:8000/docs
```

### 8. Create a session

```powershell
$body = @{
    title = "Product Strategy Chat"
    user_metadata = @{
        role = "product_manager"
    }
} | ConvertTo-Json -Compress

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response | ConvertTo-Json -Depth 10
```

### 9. Send a question

Use the returned `session_id`:

```powershell
$body = @{
    session_id = "YOUR_SESSION_ID"
    prompt = "What is product-market fit?"
    top_k = 3
} | ConvertTo-Json -Compress

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body |
    ConvertTo-Json -Depth 10
```

---

# Technology Stack

| Component            | Technology            |
| -------------------- | --------------------- |
| Backend              | FastAPI               |
| Language             | Python 3.12+          |
| Database             | PostgreSQL            |
| ORM / Database Layer | SQLAlchemy / Psycopg  |
| Migrations           | Alembic               |
| Embeddings           | Sentence Transformers |
| Embedding Model      | `all-MiniLM-L6-v2`    |
| Vector Search        | FAISS                 |
| LLM Runtime          | Ollama                |
| LLM                  | `qwen2.5:3b`          |
| Containerization     | Docker                |
| Orchestration        | Docker Compose        |

---

# Project Goal

The goal of the Lenny Growth Assistant is to provide a conversational interface for answering product and growth questions using information retrieved from Lenny's transcript knowledge base.

Instead of relying only on the language model's general knowledge, the application retrieves relevant transcript chunks and provides them as context to the LLM.

This architecture helps produce answers that are grounded in the project's source material.

---

# License

This project is developed as part of a technical assignment and is intended for evaluation and educational purposes.
