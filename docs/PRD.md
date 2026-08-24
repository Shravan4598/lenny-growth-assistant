# Product Requirements Document
# The Lenny Growth Assistant

## 1. Executive Summary

The Lenny Growth Assistant is an AI-powered conversational product that helps product managers, founders, growth practitioners, and product teams extract actionable insights from Lenny's Podcast and Newsletter transcript knowledge base.

The product is not intended to act as a general-purpose chatbot. Its primary value is to make a large collection of product and growth knowledge easier to search, interrogate, synthesize, and transform into useful outputs.

The assistant combines:

- Transcript-grounded conversational retrieval
- Multi-turn session context
- Dedicated Ship 30 for 30-style writing
- Markdown artifact generation
- HTML/CSS artifact generation
- Source traceability
- Local Ollama inference
- Optional cloud LLM support

The product will be delivered as a deployable full-stack application with a FastAPI backend, PostgreSQL persistence, a local retrieval layer, and a React frontend.

---

# 2. Customer and Problem Discovery

## 2.1 Primary User

The primary user is a product or growth practitioner who wants to learn from Lenny's corpus but does not have time to manually search, read, and synthesize long transcripts.

Representative users include:

- Product managers
- Growth product managers
- Startup founders
- Product leaders
- Growth practitioners
- Product-focused content creators

## 2.2 Job-to-be-Done

> When I have a product, growth, or strategy problem, I want to quickly find relevant insights from trusted expert conversations and turn them into actionable guidance so that I can make better decisions without manually searching through a large transcript library.

## 2.3 Pain Points

The current workflow has several problems:

### Discovery Cost

Finding the correct episode or transcript requires knowing which conversation may contain the answer.

### Reading Cost

Relevant transcripts can be long, making manual extraction slow.

### Synthesis Cost

Even after finding relevant material, the user must connect insights from multiple conversations.

### Traceability Problem

A summary without sources makes it difficult to distinguish transcript-derived evidence from AI-generated interpretation.

### Output Creation Cost

Users often need to transform research into a strategy document, experiment plan, memo, or piece of writing.

The Lenny Growth Assistant reduces these costs through grounded retrieval and conversational synthesis.

---

# 3. Product Goal

Build a reliable, demo-ready AI application that allows users to ask product and growth questions grounded in Lenny's transcript knowledge base and transform those insights into useful written artifacts.

The application should demonstrate Forward Deployed Engineer capabilities rather than merely maximizing the number of AI features.

---

# 4. Success Metrics

## Primary Product Success Metric

For a representative set of evaluation questions:

> At least 80% of answers should contain one or more relevant retrieved sources and avoid unsupported claims presented as transcript-derived facts.

This metric combines usefulness and grounding.

## Operational Success Metric

For the local Ollama demo:

> A standard grounded response should complete successfully within an acceptable interactive latency target under the development machine's constraints.

The exact latency depends on the selected local model and hardware and will be measured during validation.

## Reliability Metric

> Critical demo flows should complete successfully in a clean end-to-end test environment.

Critical flows:

1. Create session
2. Ask grounded question
3. Retrieve source-backed answer
4. Ask follow-up
5. Generate artifact
6. Render artifact safely

---

# 5. Product Scope

## In Scope

### Grounded Chat

- Product and growth questions
- Retrieval from transcript knowledge
- Source identification
- Multi-turn conversation
- Empty-retrieval limitation behavior

### Sessions

- New chat sessions
- Independent conversation history
- PostgreSQL persistence
- Conversation retrieval

### LLM Providers

- Ollama for the demo
- At least one cloud provider abstraction
- Configuration-based provider switching
- Health and failure handling

### Knowledge Base

- Transcript ingestion
- Cleaning
- Metadata extraction
- Chunking
- Embedding
- Vector indexing
- Retrieval
- Source traceability

### Agent Skills

- Grounded Chat Skill
- Ship 30 for 30 Writing Skill
- Artifact Generation Skill
- Deterministic routing

### Artifacts

- Markdown artifacts
- HTML/CSS artifacts
- In-app artifact viewer
- HTML sanitization and sandbox isolation

### Engineering

- FastAPI
- PostgreSQL
- Docker Compose
- Structured logging
- Automated tests
- Operational documentation

---

# 6. Intentionally Out of Scope

The following are excluded to protect delivery reliability before the deadline.

## Authentication and Multi-Tenant Accounts

The assignment requires session persistence and user metadata but does not explicitly require a complete authentication system.

The implementation will support anonymous or lightweight user metadata rather than building full identity management.

## Production SaaS Billing

No subscription or payment functionality is required for demonstrating the product.

## Full Corpus Continuous Crawling

The ingestion pipeline will support repeatable updates, but a production-grade distributed crawler is unnecessary for the demo.

## Advanced Hybrid Search

BM25, reranking, and hybrid retrieval can improve quality but are not required for the first working system.

The initial system prioritizes reliable semantic retrieval with preserved metadata.

## Real-Time Collaboration

Collaborative editing is outside the assignment scope.

## Arbitrary JavaScript Execution

HTML artifacts will not be treated as executable applications.

Scripts and dangerous browser behavior will be restricted.

## Complex Autonomous Multi-Agent Workflows

The product has only three clear skill categories. Deterministic routing is easier to test and explain than an unnecessarily complex agent graph.

---

# 7. Key User Flows

## Flow 1: Grounded Question

1. User opens a new chat.
2. User asks a product or growth question.
3. Backend retrieves relevant transcript chunks.
4. Retrieval quality is evaluated.
5. Grounded Chat Skill generates an answer.
6. Sources are returned.
7. Frontend displays answer and sources.

## Flow 2: Follow-Up Question

1. User continues the same conversation.
2. Backend loads only that session's relevant history.
3. Current question is processed with conversation context.
4. Retrieval is performed again.
5. Answer and sources are returned.
6. No context from other sessions is used.

## Flow 3: Ship 30 Writing

1. User requests a Ship 30 for 30-style essay.
2. Router selects Ship 30 Skill.
3. Relevant transcript evidence is retrieved.
4. Skill creates an internal outline.
5. Essay is generated.
6. Structure and approximate word count are validated.
7. Grounded source references are returned.

## Flow 4: Artifact Generation

1. User requests a strategy document, plan, memo, Markdown artifact, or HTML/CSS artifact.
2. Router selects Artifact Skill.
3. Relevant conversation context and evidence are assembled.
4. Artifact is generated.
5. HTML is validated and sanitized when applicable.
6. Artifact is persisted.
7. Artifact Viewer renders it beside the chat.

---

# 8. Functional Requirements

## 8.1 Chat

The assistant must:

- Accept user questions.
- Retrieve relevant transcript knowledge.
- Generate grounded answers.
- Support follow-up questions.
- Return source information.
- Avoid presenting unsupported information as transcript fact.

## 8.2 Sessions

The application must:

- Create independent sessions.
- Persist messages.
- Retrieve history.
- Prevent cross-session context leakage.

## 8.3 Knowledge Retrieval

The ingestion pipeline must:

1. Load transcripts.
2. Clean transcript content.
3. Extract metadata.
4. Split content into chunks.
5. Generate embeddings.
6. Build or update the vector index.
7. Retrieve relevant chunks.
8. Preserve source metadata.

## 8.4 Ship 30 Skill

The skill must:

- Be implemented as a dedicated reusable component.
- Retrieve transcript evidence.
- Generate approximately 1,250 words.
- Include a strong hook.
- Follow a clear narrative progression.
- Use headings and bullets.
- Use selective bold emphasis.
- End with a useful takeaway.
- Avoid unsupported transcript claims.

## 8.5 Artifact Generation

The application must support:

- Markdown artifacts
- HTML/CSS artifacts

Artifacts should use relevant conversation context and retrieved knowledge when appropriate.

---

# 9. Assumptions

## Assumption 1: Representative Transcript Dataset

The submitted demo will initially use a representative subset of the available transcript corpus.

### Why

A small, curated dataset allows the ingestion and retrieval pipeline to be tested before scaling to the complete repository.

### Risk

A small corpus may reduce answer coverage.

### Mitigation

The ingestion pipeline will remain reusable for additional transcripts.

---

## Assumption 2: PostgreSQL Is the System of Record

PostgreSQL will store application entities including sessions, messages, users, and artifacts.

A local vector index may be used separately for semantic retrieval.

### Why

This satisfies the persistence requirement while avoiding unnecessary vector database complexity.

---

## Assumption 3: FAISS Is Sufficient for the Demo

A local FAISS index will be used for vector similarity retrieval.

### Why

It is lightweight, reproducible, and suitable for a local demo corpus.

### Trade-Off

The system will not initially support distributed vector search or advanced database-native filtering.

---

## Assumption 4: Ollama Runs on the Host

Ollama will run on the evaluator's host machine rather than being required as a Docker service.

### Why

This reduces container resource pressure and keeps the local model workflow familiar.

### Implication

Docker networking to the host Ollama service must be documented.

---

## Assumption 5: Deterministic Routing Is Sufficient

Intent routing will classify requests into:

- Grounded chat
- Ship 30
- Artifact generation

### Why

The skills are clearly distinguishable and deterministic routing improves reliability and testability.

---

## Assumption 6: HTML Is Untrusted

Generated HTML/CSS will never be treated as trusted application code.

It will be sanitized and rendered in an isolated iframe with restricted capabilities.

---

# 10. Risks and Trade-Offs

## 10.1 Hallucination

### Risk

The model may produce plausible information not present in retrieved transcripts.

### Mitigation

- Retrieval threshold
- Explicit grounding instructions
- Source metadata
- Empty-retrieval limitation response
- Tests for unsupported-context behavior

### Remaining Limitation

A model can still misinterpret retrieved content. Source citations improve traceability but do not guarantee perfect factual interpretation.

---

## 10.2 Local Model Quality

### Risk

A lightweight local model may produce lower-quality reasoning or writing than a large cloud model.

### Mitigation

- Select a practical 3B-class model.
- Keep prompts structured.
- Limit retrieved context to relevant chunks.
- Allow optional cloud configuration.

### Trade-Off

Lower model size improves local feasibility but may reduce response quality.

---

## 10.3 Latency

### Risk

Local inference can be slower than cloud inference.

### Mitigation

- Use a lightweight model.
- Limit retrieval context.
- Use bounded history.
- Configure timeouts.
- Log request duration.

---

## 10.4 Cost

### Risk

Cloud LLM usage can introduce variable costs.

### Mitigation

The submitted demo defaults to Ollama.

Cloud providers remain optional and configuration-driven.

---

## 10.5 Data Leakage

### Risk

Conversation content or retrieved transcripts may be sent to an external cloud provider when cloud mode is selected.

### Mitigation

- Local Ollama as the demo default.
- Explicit provider configuration.
- No silent cloud fallback.
- Documentation of provider behavior.

---

## 10.6 Unsafe Artifact Rendering

### Risk

Generated HTML can contain scripts, malicious URLs, or browser abuse attempts.

### Mitigation

- Validate and sanitize generated HTML.
- Remove scripts.
- Remove inline event handlers.
- Restrict dangerous URL schemes.
- Render through a sandboxed iframe.

### Remaining Limitation

Browser sandboxing and sanitization reduce risk but do not constitute a guarantee against every browser or parser vulnerability.

---

# 11. Acceptance Criteria

The project is acceptable when:

- FastAPI starts successfully.
- PostgreSQL persistence works.
- Sessions remain isolated.
- Ollama works for the demo.
- A cloud provider is available through configuration.
- Transcripts can be ingested.
- Retrieval preserves metadata.
- Grounded answers display sources.
- Empty retrieval does not trigger fabricated transcript claims.
- The three skills work independently.
- Ship 30 generation follows the required structure.
- Markdown and HTML/CSS artifacts render inside the application.
- Generated HTML is restricted.
- Docker startup is reproducible.
- Automated tests pass.
- Required documentation is complete.

---

# 12. Implementation Plan

## Phase 1: Requirement Traceability

Create and maintain `REQUIREMENTS.md`.

## Phase 2: Discovery Documentation

Create:

- `docs/PRD.md`
- `docs/architecture.md`
- `docs/design.md`

## Phase 3: Technical Foundation

Implement:

- Configuration
- FastAPI
- Health endpoint
- Logging
- PostgreSQL
- Migrations
- Docker Compose

## Phase 4: Knowledge Base

Implement:

- Transcript loader
- Cleaner
- Metadata extraction
- Chunking
- Embeddings
- Vector index
- Retrieval

## Phase 5: LLM Providers

Implement:

- Provider abstraction
- Ollama provider
- Cloud provider
- Health and timeout behavior

## Phase 6: Agent Skills

Implement:

- Approved agent SDK integration
- Grounded Chat Skill
- Ship 30 Skill
- Artifact Skill
- Router

## Phase 7: Sessions and Chat

Implement API routes and persistence.

## Phase 8: Frontend

Implement the chat and artifact workspace.

## Phase 9: Security and Resilience

Test failure behavior and artifact isolation.

## Phase 10: Automated Tests

Run and fix the complete test suite.

## Phase 11: Documentation and Handoff

Complete README, troubleshooting, manual test plan, and genuine implementation transcripts.

## Phase 12: Demo Preparation

Prepare and rehearse a concise demonstration.

---

# 13. Product Principles

The implementation will prioritize:

1. **Grounded usefulness over impressive hallucination**
2. **Reliability over unnecessary agent complexity**
3. **Clarity over visual decoration**
4. **Local reproducibility over infrastructure sophistication**
5. **Security awareness over unrestricted artifact execution**
6. **Explicit trade-offs over hidden assumptions**

These principles guide implementation decisions throughout the project.