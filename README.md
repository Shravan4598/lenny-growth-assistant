# Lenny Growth Assistant

A production-style Retrieval-Augmented Generation (RAG) assistant built around Lenny's Newsletter and Podcast knowledge base.

The application combines transcript ingestion, semantic embeddings, FAISS vector search, PostgreSQL-backed conversation persistence, a local Ollama LLM, and a React frontend to answer product and growth questions using retrieved source material.

---

## Demo

[![Watch the demo](https://img.youtube.com/vi/grZyoM4tT84/maxresdefault.jpg)](https://youtu.be/grZyoM4tT84)

🎥 **Video walkthrough:** [https://youtu.be/grZyoM4tT84](https://youtu.be/grZyoM4tT84)

---

## Features

- Lenny Podcast and Newsletter knowledge ingestion
- Transcript cleaning and chunking
- Sentence Transformer embeddings
- FAISS vector similarity search
- Retrieval-Augmented Generation (RAG)
- Local Ollama LLM integration
- PostgreSQL persistence
- Chat session management
- Persistent conversation history
- Follow-up question support
- Source metadata and retrieval scores
- Grounded/unsupported-question fallback
- Agent execution and event tracking
- Health and readiness endpoints
- LLM status and direct generation endpoints
- REST API with FastAPI
- React + Vite frontend
- Artifact viewer with Markdown rendering and sanitization
- Docker Compose deployment
- Alembic database migrations
- Configurable retrieval parameters
- Automated tests

---

## Architecture

```text
                           ┌──────────────────────┐
                           │       React UI        │
                           │    Vite Frontend     │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │       FastAPI        │
                           │      REST API        │
                           └──────────┬───────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
                ▼                     ▼                     ▼
        ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
        │    Sessions   │     │      RAG      │     │    Agent      │
        │    Service    │     │    Service    │     │   Execution   │
        └───────┬───────┘     └───────┬───────┘     └───────┬───────┘
                │                     │                     │
                ▼                     ▼                     ▼
        ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
        │  PostgreSQL   │     │     FAISS     │     │ Agent Events  │
        │   Database    │     │ Vector Index  │     │   Tracking    │
        └───────────────┘     └───────┬───────┘     └───────────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │     Ollama      │
                             │  qwen2.5:1.5b   │
                             └─────────────────┘
```

### RAG Request Flow

```text
User Question
      │
      ▼
Query Embedding
      │
      ▼
FAISS Similarity Search
      │
      ▼
Relevant Lenny Transcript Chunks
      │
      ▼
Prompt Construction
+ Conversation History
      │
      ▼
Ollama LLM
      │
      ▼
Grounded Answer
      │
      ├──────────────► Source Metadata
      │
      ▼
Persist Conversation
      │
      ▼
Return Response
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
│   │   │   │   ├── agent.py
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
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   └── ArtifactViewer.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── package.json
│   └── ...
│
├── data/
│   ├── raw/
│   ├── external/
│   └── processed/
│
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

| Component | Technology |
|---|---|
| Backend | FastAPI |
| Language | Python 3.12+ |
| Database | PostgreSQL |
| ORM / Database Layer | SQLAlchemy / Psycopg |
| Migrations | Alembic |
| Embeddings | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| Vector Search | FAISS |
| LLM Runtime | Ollama |
| Default LLM | qwen2.5:1.5b |
| Frontend | React 18 + TypeScript |
| Frontend Build Tool | Vite |
| HTTP Client | Axios |
| Markdown Rendering | Marked |
| HTML Sanitization | DOMPurify |
| Containerization | Docker |
| Orchestration | Docker Compose |
| Testing | Pytest |

---

# Requirements

Before running the project, install/configure:

- Python 3.12+
- Docker Desktop
- Docker Compose
- Node.js/npm
- Ollama
- `qwen2.5:1.5b` Ollama model

Verify the installations:

```powershell
python --version
docker --version
docker compose version
node --version
npm --version
ollama --version
```

---

# Ollama Setup

The project uses Ollama as the local LLM provider.

Pull the configured model:

```powershell
ollama pull qwen2.5:1.5b
```

Verify:

```powershell
ollama list
```

You should see:

```text
qwen2.5:1.5b
```

Test Ollama directly:

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

Create a `.env` file in the project root using `.env.example` as the template.

Example:

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

LENNY_REPOSITORY_PATH=data/external/lennys-newsletterpodcastdata
LENNY_CONTENT_TYPES=["podcasts","newsletters"]
```

## Important Docker Networking Note

When the backend runs inside Docker and Ollama runs on the host machine:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Do not use:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

Inside the backend container, `localhost` refers to the container itself.

---

# Quick Start

## 1. Start Ollama

```powershell
ollama pull qwen2.5:1.5b
```

Make sure Ollama is running.

## 2. Configure `.env`

Create `.env` from `.env.example`.

## 3. Build and start the backend services

From the project root:

```powershell
docker compose up -d --build
```

## 4. Check container status

```powershell
docker compose ps
```

Expected core services include:

```text
lenny-growth-backend
lenny-growth-postgres
```

## 5. Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

The Vite development server will display its local URL in the terminal, normally:

```text
http://localhost:5173
```

## 6. Check API health

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

## 7. Open API documentation

```text
http://localhost:8000/docs
```

---

# API

Base URL:

```text
http://localhost:8000/api/v1
```

Interactive Swagger documentation:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

---

# Health Check

### GET `/health`

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

Expected:

```json
{
  "status": "ok",
  "application": "The Lenny Growth Assistant",
  "environment": "development"
}
```

---

# Readiness Check

### GET `/health/ready`

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/health/ready" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

The readiness check verifies application availability, database availability, configured LLM provider, and active model.

---

# LLM Status

### GET `/api/v1/llm/status`

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/llm/status" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

Example:

```json
{
  "provider": "ollama",
  "model": "qwen2.5:1.5b",
  "healthy": true,
  "detail": "Ollama service and configured model are available."
}
```

---

# Direct LLM Generation

### POST `/api/v1/llm/generate`

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

### POST `/api/v1/sessions`

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

$sessionId = $session.id
```

A session ID is used to persist conversation history.

## List Sessions

### GET `/api/v1/sessions`

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions" `
    -Method Get |
    ConvertTo-Json -Depth 10
```

## Get Session History

### GET `/api/v1/sessions/{session_id}`

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/sessions/$sessionId" `
    -Method Get |
    ConvertTo-Json -Depth 20
```

---

# RAG Chat

### POST `/api/v1/chat`

```powershell
$body = @{
    session_id = $sessionId
    prompt = "What is product-market fit?"
    top_k = 3
} | ConvertTo-Json -Compress

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response | ConvertTo-Json -Depth 20
```

The response contains:

- Active LLM provider
- Active model
- Generated answer
- Retrieved source metadata
- Retrieval scores

Example source information:

```json
{
  "chunk_id": "podcasts-matt-macinnis-chunk-0022",
  "title": "10 contrarian leadership truths every leader needs to hear | Matt MacInnis (Rippling)",
  "guest": "Matt MacInnis",
  "date": "2025-12-28",
  "score": 0.6053
}
```

---

# Agent Execution

The project also exposes an agent execution flow that records execution state and events.

### POST `/api/v1/agent/run`

```powershell
$agentBody = @{
    session_id = $sessionId
    prompt = "What is product-market fit? Explain it using insights from Lenny's Podcast and Newsletter."
} | ConvertTo-Json -Compress

$agentRun = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agent/run" `
    -Method Post `
    -ContentType "application/json" `
    -Body $agentBody

$agentRun | ConvertTo-Json -Depth 20
```

Example successful response:

```json
{
  "response": "...",
  "artifact_id": null,
  "run_id": "9c72fc13-ed52-464b-b1bb-158a80fdf599",
  "skill": "grounded_chat",
  "status": "completed"
}
```

## Agent Events

### GET `/api/v1/agent/runs/{run_id}/events`

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/agent/runs/$runId/events" `
    -Method Get |
    ConvertTo-Json -Depth 20
```

A successful run records events such as:

```text
agent_started
planning
retrieval_started
retrieval_completed
llm_completed
agent_completed
```

This provides observability into the agent execution lifecycle.

---

# Conversation Persistence

When `session_id` is supplied to `/api/v1/chat`, the application:

1. Validates the session.
2. Loads previous messages.
3. Uses recent conversation history as context.
4. Saves the current user message.
5. Runs retrieval and generation.
6. Saves the assistant response and source metadata.
7. Updates session activity.
8. Returns the grounded answer.

Follow-up questions therefore retain conversational context.

Example:

```text
User:
What is product-market fit?

Assistant:
...

User:
What did Matt MacInnis say about knowing when you have it?

Assistant:
...
```

The second question can use the previous conversation together with newly retrieved evidence.

---

# Knowledge Base and RAG Pipeline

The knowledge pipeline is:

```text
Lenny Podcast / Newsletter Data
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
        FAISS Index
             │
             ▼
      Semantic Retrieval
             │
             ▼
      Grounded Generation
```

Processed retrieval artifacts are stored under:

```text
data/processed/
```

Configured index:

```text
data/processed/lenny.faiss
```

The current FAISS index has been verified to load successfully and contains:

```text
2339 vectors
384 dimensions
```

---

# Retrieval Configuration

```env
RETRIEVAL_TOP_K=5
RETRIEVAL_MIN_SCORE=0.40
```

`RETRIEVAL_TOP_K` controls how many candidate chunks are retrieved.

`RETRIEVAL_MIN_SCORE` controls the minimum similarity threshold accepted by retrieval.

For individual chat requests, `top_k` can be overridden:

```json
{
  "prompt": "What is product-market fit?",
  "top_k": 3
}
```

---

# Grounded Responses and Fallback

The assistant is designed to answer from retrieved Lenny knowledge rather than relying exclusively on the LLM's general knowledge.

The RAG service:

```text
Question
   │
   ▼
Retrieve evidence
   │
   ├── Sufficient evidence ──► Grounded answer
   │
   └── Insufficient evidence ─► Explicit fallback
```

This reduces unsupported or fabricated answers.

---

# Frontend

The frontend is implemented with:

- React
- TypeScript
- Vite
- Axios
- Marked
- DOMPurify
- Tailwind CSS

The main UI contains:

```text
┌──────────────────────────────────────────────────────────────┐
│                  Lenny Growth Assistant                      │
├─────────────────────────────┬────────────────────────────────┤
│                             │                                │
│       Chat Interface        │       Artifact Viewer          │
│                             │                                │
│  User messages              │       Generated artifact       │
│  Assistant responses        │       rendered as Markdown     │
│  Loading state               │       and sanitized            │
│                             │                                │
├─────────────────────────────┴────────────────────────────────┤
│                     Message Input                            │
└──────────────────────────────────────────────────────────────┘
```

Run the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Build for production:

```powershell
npm run build
```

The artifact viewer converts Markdown to HTML and sanitizes the generated content with DOMPurify before rendering it inside a sandboxed iframe.

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

Connection string:

```text
postgresql+psycopg://postgres:postgres@postgres:5432/lenny_growth
```

## Database Tables

The application currently uses tables including:

```text
users
sessions
messages
artifacts
agent_runs
agent_events
alembic_version
```

## Inspect Tables

```powershell
docker compose exec postgres `
    psql -U postgres -d lenny_growth -c "\dt"
```

## Inspect Sessions

```powershell
docker compose exec postgres `
    psql -U postgres -d lenny_growth `
    -c "SELECT id, title, created_at, updated_at FROM sessions ORDER BY created_at DESC LIMIT 10;"
```

## Inspect Messages

```powershell
docker compose exec postgres `
    psql -U postgres -d lenny_growth `
    -c "SELECT id, session_id, role, LEFT(content,150) AS content_preview, created_at FROM messages ORDER BY created_at DESC LIMIT 10;"
```

## Inspect Agent Runs

```powershell
docker compose exec postgres `
    psql -U postgres -d lenny_growth `
    -c "SELECT id, session_id, skill, status, created_at, completed_at FROM agent_runs ORDER BY created_at DESC LIMIT 10;"
```

## Inspect Agent Events

```powershell
docker compose exec postgres `
    psql -U postgres -d lenny_growth `
    -c "SELECT id, run_id, event_type, timestamp FROM agent_events ORDER BY timestamp DESC LIMIT 20;"
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

Run the backend tests:

```powershell
cd backend
pytest -q
cd ..
```

The project includes tests covering core application behavior, retrieval, configuration, database behavior, and API functionality.

---

# Verified Integration Tests

The following flows have been manually verified successfully:

### Session creation

```text
POST /api/v1/sessions
Status: successful
```

### Agent execution

```text
POST /api/v1/agent/run
Status: completed
Skill: grounded_chat
Provider: ollama
Model: qwen2.5:1.5b
```

### Agent observability

Verified event sequence:

```text
agent_started
planning
retrieval_started
retrieval_completed
llm_completed
agent_completed
```

### RAG chat

```text
POST /api/v1/chat
Status: successful
Provider: ollama
Model: qwen2.5:1.5b
Sources returned: yes
```

### Conversation persistence

Verified that user and assistant messages are persisted in PostgreSQL and follow-up questions can use the same session.

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

## Backend logs

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

> Warning: removing the Docker volume deletes PostgreSQL data stored in that volume.

---

# Troubleshooting

## Backend is not running

Check:

```powershell
docker compose ps
```

Then:

```powershell
docker compose logs backend --tail=200
```

---

## PostgreSQL is unavailable

Check:

```powershell
docker compose logs postgres --tail=200
```

Restart:

```powershell
docker compose restart
```

---

## Ollama connection error

Check:

```powershell
ollama list
```

Test:

```powershell
Invoke-RestMethod `
    -Uri "http://localhost:11434/api/tags" `
    -Method Get
```

If the model is missing:

```powershell
ollama pull qwen2.5:1.5b
```

For the Dockerized backend, verify:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

Check Docker-to-host connectivity:

```powershell
docker compose exec backend `
    python -c "import urllib.request; print(urllib.request.urlopen('http://host.docker.internal:11434/api/tags').read().decode())"
```

---

## FAISS Index Not Found

Check:

```powershell
Get-ChildItem .\data\processed\
```

Expected:

```text
data/processed/lenny.faiss
```

If missing, run the project's ingestion/indexing process before testing RAG queries.

---

# Final Verification Checklist

Before submission:

```text
[ ] docker compose config
[ ] docker compose up -d --build
[ ] docker compose ps

[ ] GET /health
[ ] GET /health/ready
[ ] GET /api/v1/llm/status
[ ] POST /api/v1/llm/generate

[ ] POST /api/v1/sessions
[ ] GET /api/v1/sessions
[ ] GET /api/v1/sessions/{session_id}

[ ] POST /api/v1/chat
[ ] Follow-up question using the same session
[ ] Conversation persistence in PostgreSQL

[ ] POST /api/v1/agent/run
[ ] GET /api/v1/agent/runs/{run_id}/events

[ ] Unsupported-question fallback
[ ] FAISS index loads correctly
[ ] pytest -q

[ ] npm install
[ ] npm run build
[ ] Frontend chat flow

[ ] git status
```

---

# Project Goal

The goal of the Lenny Growth Assistant is to provide a conversational interface for answering product and growth questions using retrieved knowledge from Lenny's Newsletter and Podcast content.

Instead of sending a question directly to a language model, the application:

1. Receives the user's question.
2. Generates an embedding for the query.
3. Searches the FAISS vector index.
4. Retrieves relevant Lenny content.
5. Combines retrieved evidence with conversation history.
6. Generates a grounded answer using Ollama.
7. Persists the conversation in PostgreSQL.
8. Returns the answer together with source metadata.
9. Records agent execution events when the agent endpoint is used.

This architecture provides a foundation for:

- Source-grounded answers
- Semantic knowledge retrieval
- Persistent conversations
- Follow-up questions
- Agent observability
- Explicit insufficient-evidence handling
- Local/private LLM inference
- Extensible product and growth intelligence workflows

---

# License

This project was developed as part of a technical assignment and is intended for evaluation and educational purposes.