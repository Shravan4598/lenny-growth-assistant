# Lenny Growth Assistant

A Retrieval-Augmented Generation (RAG) assistant built around Lenny's newsletter and podcast knowledge base.

The application combines semantic retrieval, FAISS vector search, PostgreSQL-backed conversation persistence, and a local Ollama language model to answer product and growth questions using retrieved source material.

## Features

- Lenny transcript ingestion
- Transcript cleaning and chunking
- Sentence Transformer embeddings
- FAISS vector similarity search
- Retrieval-Augmented Generation (RAG)
- Local Ollama LLM integration
- PostgreSQL persistence
- Chat sessions
- Conversation history
- Follow-up question support
- Source metadata returned with responses
- Unsupported-question fallback
- Health and readiness endpoints
- Docker Compose deployment
- Alembic database migrations
- Configurable retrieval parameters
- Automated tests

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
                           │  qwen2.5:1.5b   │
                           └─────────────────┘
```

---

## Project Structure

```text
lenny-growth-assistant/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── chat.py
│   │   │   │   ├── health.py
│   │   │   │   ├── llm.py
│   │   │   │   └── sessions.py
│   │   │   ├── schemas/
│   │   │   │   ├── chat.py
│   │   │   │   └── sessions.py
│   │   │   └── services/
│   │   │       └── session_service.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── llm/
│   │   ├── rag/
│   │   ├── retrieval/
│   │   └── main.py
│   ├── alembic/
│   ├── alembic.ini
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
├── data/
│   ├── raw/
│   ├── external/
│   └── processed/
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── LICENSE
├── README.md
└── REQUIREMENTS.md
```

---

## Technology Stack

| Component            | Technology             |
| --------------------- | ----------------------- |
| Backend               | FastAPI                 |
| Language              | Python 3.12+             |
| Database              | PostgreSQL               |
| ORM / Database Layer  | SQLAlchemy / Psycopg     |
| Migrations            | Alembic                  |
| Embeddings            | Sentence Transformers    |
| Embedding Model       | all-MiniLM-L6-v2         |
| Vector Search         | FAISS                    |
| LLM Runtime           | Ollama                   |
| Default LLM           | qwen2.5:1.5b             |
| Containerization      | Docker                   |
| Orchestration         | Docker Compose           |
| Testing               | Pytest                   |

---

# Requirements

Before running the project, install or configure the following:

- Python 3.12+
- Docker Desktop
- Docker Compose
- Ollama
- `qwen2.5:1.5b` Ollama model

Verify the installations:

```powershell
python --version
docker --version
docker compose version
ollama --version
```

---

# Ollama Setup

The project uses Ollama as the local LLM provider. Make sure Ollama is running before starting the application.

Pull the configured model:

```powershell
ollama pull qwen2.5:1.5b
```

Verify that it is available:

```powershell
ollama list
```

You should see:

```text
qwen2.5:1.5b
```

You can test Ollama directly:

```powershell
$body = @{
    model = "qwen2.5:1.5b"
    prompt = "Explain product-market fit in three sentences."
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

Create a `.env` file in the project root using `.env.example` as a template.

Example configuration:

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
OLLAMA_MODEL=qwen2.5:1.5b

RETRIEVAL_INDEX_PATH=data/processed/lenny.faiss
EMBEDDING_MODEL=all-MiniLM-L6-v2

RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.40
```

## Important Docker Networking Note

When the backend runs inside Docker and Ollama runs on the host machine, use:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Do not use:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

Inside the backend container, `localhost` refers to the container itself, not the host machine.

---

# Quick Start

## 1. Pull the Ollama model

```powershell
ollama pull qwen2.5:1.5b
```

## 2. Configure environment variables

Create `.env` from `.env.example` and configure the required values.

## 3. Build and start the services

From the project root:

```powershell
docker compose up -d --build
```

## 4. Check container status

```powershell
docker compose ps
```

Expected services:

```text
lenny-growth-backend
lenny-growth-postgres
```

Both services should become healthy.

## 5. Check application health

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

Expected response:

```json
{
  "status": "ok",
  "application": "The Lenny Growth Assistant",
  "environment": "development"
}
```

## 6. Check application readiness

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health/ready" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

Expected response:

```json
{
  "status": "ok",
  "application": "The Lenny Growth Assistant",
  "environment": "development",
  "database": "available",
  "llm_provider": "ollama",
  "model": "qwen2.5:1.5b"
}
```

## 7. Open API documentation

```text
http://localhost:8000/docs
```

## 8. Create a session

```powershell
$body = @{
    title = "Product Strategy Chat"
} | ConvertTo-Json -Compress

$session = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$session | ConvertTo-Json -Depth 10
```

Save the returned session ID:

```powershell
$sessionId = $session.id
```

## 9. Send a question

```powershell
$body = @{
    session_id = $sessionId
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

# API

The API base URL is:

```text
http://localhost:8000/api/v1
```

Interactive documentation is available at:

```text
http://localhost:8000/docs
```

ReDoc documentation:

```text
http://localhost:8000/redoc
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

---

## Health Check

### GET /health

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health" `
    -Method Get
```

The endpoint returns a successful response indicating that the API is running.

---

## Readiness Check

### GET /health/ready

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health/ready" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

The readiness check verifies:

- Application availability
- Database availability
- Configured LLM provider
- Active model

---

## LLM Status

### GET /api/v1/llm/status

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/llm/status" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

Example response:

```json
{
  "provider": "ollama",
  "model": "qwen2.5:1.5b",
  "healthy": true,
  "detail": "Ollama service and configured model are available."
}
```

---

## Direct LLM Generation

### POST /api/v1/llm/generate

```powershell
$body = @{
    prompt = "Explain product-market fit in one paragraph."
    temperature = 0.2
    max_tokens = 200
} | ConvertTo-Json -Compress

Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/llm/generate" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body |
    ConvertTo-Json -Depth 10
```

---

# Chat Sessions

## Create a Session

### POST /api/v1/sessions

```powershell
$body = @{
    title = "Product Strategy Chat"
} | ConvertTo-Json -Compress

$session = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$session | ConvertTo-Json -Depth 10
```

Save the returned `session_id`. It is required when sending chat messages.

```powershell
$sessionId = $session.id
```

---

## List Sessions

### GET /api/v1/sessions

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

---

## Get Session History

### GET /api/v1/sessions/{session_id}

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions/$sessionId" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

The response includes the persisted conversation history.

---

# RAG Chat

### POST /api/v1/chat

```powershell
$body = @{
    prompt = "What is product-market fit?"
    top_k = 3
    session_id = $sessionId
} | ConvertTo-Json -Compress

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response | ConvertTo-Json -Depth 10
```

The response contains:

- Active LLM provider
- Active model
- Generated answer
- Retrieved source metadata
- Retrieval scores

---

# RAG Pipeline

The request flow is:

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
        (includes conversation context)
                       │
                       ▼
                    Ollama
                       │
                       ▼
               Generated Answer
                       │
                       ▼
         Persist Conversation to PostgreSQL
                       │
                       ▼
             Return Answer and Sources
```

The application is designed to answer using retrieved knowledge rather than relying exclusively on the LLM's general knowledge.

When the retrieved evidence is insufficient, the assistant returns an explicit fallback instead of fabricating an answer.

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
qwen2.5:1.5b
```

### Retrieval Configuration

```env
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.40
```

`RETRIEVAL_TOP_K` controls how many relevant chunks are retrieved.

`RETRIEVAL_MIN_SCORE` defines the minimum similarity threshold used during retrieval.

---

# Knowledge Base Processing

The retrieval pipeline processes source material as follows:

```text
Raw Lenny Content
       │
       ▼
Content Loading
       │
       ▼
Text Cleaning
       │
       ▼
Chunking
       │
       ▼
Embedding Generation
       │
       ▼
FAISS Index Creation
       │
       ▼
Semantic Retrieval
```

Processed retrieval artifacts are stored under:

```text
data/processed/
```

The configured index path is:

```text
data/processed/lenny.faiss
```

---

# Database

PostgreSQL runs as a Docker service.

Default configuration:

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

The application uses Alembic for schema migrations.

## Database Tables

Current tables include:

```text
users
sessions
messages
artifacts
alembic_version
```

## Inspect Database Tables

```powershell
docker compose exec postgres `
    psql -U postgres -d lenny_growth -c "\dt"
```

## Open a PostgreSQL Shell

```powershell
docker compose exec postgres `
    psql -U postgres -d lenny_growth
```

Useful commands:

```sql
\dt
\d sessions
\d messages
\q
```

---

# Database Migrations

Check the current migration:

```powershell
docker compose exec backend alembic current
```

View migration history:

```powershell
docker compose exec backend alembic history
```

Apply migrations:

```powershell
docker compose exec backend alembic upgrade head
```

The backend startup process also applies migrations before starting the application.

---

# Testing

The project includes automated tests for core components and application behavior.

Run tests locally:

```powershell
cd backend
pytest -q
cd ..
```

Current verified result:

```text
11 passed
```

Note: `pytest` is included in the development environment and may not be installed in the production Docker image.

---

# Docker Operations

## Start

```powershell
docker compose up -d --build
```

## Check status

```powershell
docker compose ps
```

## View backend logs

```powershell
docker compose logs backend --tail=100
```

## Follow backend logs

```powershell
docker compose logs -f backend
```

## Restart backend

```powershell
docker compose restart backend
```

## Inspect all logs

```powershell
docker compose logs --tail=200
```

## Stop services

```powershell
docker compose down
```

## Remove services and database volume

```powershell
docker compose down -v
```

Warning: removing the volume deletes the PostgreSQL data stored in Docker.

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

---

# Troubleshooting

## Backend is not running

Check:

```powershell
docker compose ps
```

Then inspect:

```powershell
docker compose logs backend --tail=200
```

---

## PostgreSQL is unavailable

Check:

```powershell
docker compose logs postgres --tail=200
```

Restart services:

```powershell
docker compose restart
```

---

## Ollama connection error

Check available models:

```powershell
ollama list
```

Check the Ollama API:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:11434/api/tags" `
    -Method Get
```

If the configured model is missing:

```powershell
ollama pull qwen2.5:1.5b
```

For Dockerized backend communication with Ollama running on the host, verify `.env` contains:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

## Check backend can reach Ollama

```powershell
docker compose exec backend `
    python -c "import urllib.request; print(urllib.request.urlopen('http://host.docker.internal:11434/api/tags').read().decode())"
```

If this succeeds, the Docker container can reach Ollama running on the host machine.

---

## FAISS Index Not Found

Check the processed data directory:

```powershell
Get-ChildItem .\data\processed\
```

The configured index is:

```text
data/processed/lenny.faiss
```

If the index does not exist, run the project's ingestion/indexing process before testing RAG queries.

---

# Final Verification Checklist

Before submission, verify:

```text
[ ] docker compose config
[ ] docker compose up -d --build
[ ] docker compose ps
[ ] GET /health
[ ] GET /health/ready
[ ] GET /api/v1/llm/status
[ ] POST /api/v1/llm/generate
[ ] POST /api/v1/sessions
[ ] POST /api/v1/chat
[ ] GET /api/v1/sessions
[ ] GET /api/v1/sessions/{session_id}
[ ] Unsupported-question fallback
[ ] pytest -q
[ ] git status
```

---

# Project Goal

The goal of the Lenny Growth Assistant is to provide a conversational interface for answering product and growth questions using retrieved knowledge from Lenny's newsletter and podcast content.

Instead of sending a question directly to a language model, the application retrieves relevant transcript chunks, adds them to a grounded prompt, and generates a response based on that retrieved context.

This architecture provides a foundation for:

- Source-grounded answers
- Semantic knowledge retrieval
- Conversation persistence
- Follow-up questions
- Explicit handling of insufficient evidence

---

# License

This project was developed as part of a technical assignment and is intended for evaluation and educational purposes.