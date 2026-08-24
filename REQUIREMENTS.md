# The Lenny Growth Assistant — Requirement Traceability Matrix

> **Purpose:** This document maps assignment requirements to implementation,
> testing, and documentation. A requirement is not considered complete until
> implementation, verification, and relevant documentation are complete.

## Status Legend

- `PLANNED` — Not yet implemented
- `IN PROGRESS` — Implementation has started
- `IMPLEMENTED` — Code exists but verification may be incomplete
- `VERIFIED` — Implementation and tests/manual verification pass
- `BLOCKED` — Cannot proceed without an external dependency or decision
- `DEFERRED` — Intentionally postponed with justification

## Priority Legend

- **P0** — Explicit assignment requirement / submission blocker
- **P1** — Important quality, reliability, or evaluator-impacting requirement
- **P2** — Nice-to-have; implement only after P0/P1 completion

---

# 1. Forward Deployment Discovery

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-001 | Define primary user | P0 | `docs/PRD.md` | PRD review | `docs/PRD.md` | PLANNED |
| R-002 | Define job-to-be-done | P0 | `docs/PRD.md` | PRD review | `docs/PRD.md` | PLANNED |
| R-003 | Define pain point removed | P0 | `docs/PRD.md` | PRD review | `docs/PRD.md` | PLANNED |
| R-004 | Define measurable success metric | P0 | `docs/PRD.md` | Metric is measurable | `docs/PRD.md` | PLANNED |
| R-005 | Document assumptions | P0 | `docs/PRD.md` | Assumption review | `docs/PRD.md` | PLANNED |
| R-006 | Define included scope | P0 | `docs/PRD.md` | Scope review | `docs/PRD.md` | PLANNED |
| R-007 | Define out-of-scope items | P0 | `docs/PRD.md` | Scope review | `docs/PRD.md` | PLANNED |
| R-008 | Document scope rationale | P0 | `docs/PRD.md` | Product review | `docs/PRD.md` | PLANNED |
| R-009 | Document hallucination risk | P0 | Grounding policy | Empty retrieval tests | `docs/PRD.md`, `docs/architecture.md` | PLANNED |
| R-010 | Document latency trade-off | P0 | LLM/retrieval design | Manual verification | `docs/PRD.md`, `docs/architecture.md` | PLANNED |
| R-011 | Document cost trade-off | P0 | Provider abstraction | Configuration review | `docs/PRD.md` | PLANNED |
| R-012 | Document local model quality trade-off | P0 | Ollama configuration | Model evaluation | `docs/PRD.md`, `README.md` | PLANNED |
| R-013 | Document data leakage risk | P0 | Provider/security design | Security review | `docs/architecture.md` | PLANNED |
| R-014 | Document unsafe artifact rendering risk | P0 | Sanitizer + iframe isolation | Security tests | `docs/architecture.md` | PLANNED |

---

# 2. FastAPI Backend and API Contracts

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-020 | Use FastAPI | P0 | `backend/app/main.py` | Application startup | `README.md` | PLANNED |
| R-021 | REST API | P0 | `backend/app/api/routes/` | API tests | `docs/architecture.md` | PLANNED |
| R-022 | Clear request contracts | P0 | `backend/app/api/schemas/` | Validation tests | `docs/architecture.md` | PLANNED |
| R-023 | Clear response contracts | P0 | Pydantic response models | API tests | `docs/architecture.md` | PLANNED |
| R-024 | Pydantic validation | P0 | `api/schemas/` | Invalid request tests | `README.md` | PLANNED |
| R-025 | Structured error responses | P0 | `core/exceptions.py` | Error response tests | `docs/architecture.md` | PLANNED |
| R-026 | Health endpoint | P0 | `api/routes/health.py` | `test_health.py` | `README.md` | PLANNED |
| R-027 | Create session endpoint | P0 | `api/routes/sessions.py` | `test_sessions.py` | `docs/architecture.md` | PLANNED |
| R-028 | Send chat message endpoint | P0 | `api/routes/chat.py` | `test_chat.py` | `docs/architecture.md` | PLANNED |
| R-029 | Retrieve conversation history | P0 | `api/routes/sessions.py` | `test_sessions.py` | `docs/architecture.md` | PLANNED |
| R-030 | Generate artifact endpoint | P0 | `api/routes/artifacts.py` | Artifact API tests | `docs/architecture.md` | PLANNED |
| R-031 | Frontend decoupled from internals | P1 | API service layer | Contract review | `docs/architecture.md` | PLANNED |

---

# 3. Agent Architecture and Skills

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-040 | Use approved agent framework | P0 | `backend/app/agents/` | Integration verification | `docs/architecture.md` | PLANNED |
| R-041 | Meaningful agent SDK integration | P0 | Agent orchestration adapter | Agent integration test | `docs/architecture.md` | PLANNED |
| R-042 | Grounded Chat Skill | P0 | `agents/grounded_chat.py` | Routing/skill tests | `docs/architecture.md` | PLANNED |
| R-043 | Ship 30 Skill | P0 | `agents/ship30_skill.py` | Routing/structure tests | `docs/architecture.md` | PLANNED |
| R-044 | Artifact Generation Skill | P0 | `agents/artifact_skill.py` | Routing/artifact tests | `docs/architecture.md` | PLANNED |
| R-045 | Sensible skill routing | P0 | `agents/router.py` | `test_routing.py` | `docs/architecture.md` | PLANNED |
| R-046 | Avoid unnecessary routing complexity | P1 | Deterministic intent classifier | Routing tests | `docs/architecture.md` | PLANNED |
| R-047 | Clear skill boundaries | P0 | Agent module structure | Architecture review | `docs/architecture.md` | PLANNED |

---

# 4. Sessions and PostgreSQL Persistence

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-060 | Use PostgreSQL | P0 | `db/session.py` | DB integration test | `README.md` | PLANNED |
| R-061 | Persist session IDs | P0 | `db/models.py` | Persistence test | `docs/architecture.md` | PLANNED |
| R-062 | Persist conversation messages | P0 | `db/models.py` | Message persistence test | `docs/architecture.md` | PLANNED |
| R-063 | Persist timestamps | P0 | `db/models.py` | DB verification | `docs/architecture.md` | PLANNED |
| R-064 | Persist user metadata | P0 | `db/models.py` | Persistence test | `docs/architecture.md` | PLANNED |
| R-065 | New chat creates independent session | P0 | Session service | `test_persistence.py` | `README.md` | PLANNED |
| R-066 | Prevent cross-session context leakage | P0 | Conversation service | Session isolation test | `docs/architecture.md` | PLANNED |
| R-067 | Conversation history retrievable | P0 | Repository/service | `test_sessions.py` | `README.md` | PLANNED |
| R-068 | Graceful database failure handling | P0 | Exception/service layer | Failure test | `docs/architecture.md` | PLANNED |
| R-069 | Use clean repository architecture | P1 | `db/repositories/` | Code review | `docs/architecture.md` | PLANNED |
| R-070 | Database migrations | P1 | Alembic | Migration verification | `README.md` | PLANNED |

---

# 5. LLM Provider Configuration

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-080 | LLM provider abstraction | P0 | `llm/base.py` | Provider tests | `docs/architecture.md` | PLANNED |
| R-081 | Mandatory Ollama provider | P0 | `llm/ollama.py` | Ollama mock/integration test | `README.md` | PLANNED |
| R-082 | Demo runs using Ollama | P0 | `.env` configuration | Demo verification | `README.md` | PLANNED |
| R-083 | Lightweight local model | P0 | Configuration default | Manual machine verification | `README.md` | PLANNED |
| R-084 | Cloud LLM provider | P0 | `llm/cloud.py` | Mock provider test | `README.md` | PLANNED |
| R-085 | Provider switch through configuration | P0 | `llm/factory.py` | Factory tests | `docs/architecture.md` | PLANNED |
| R-086 | No code change required to switch provider | P0 | Environment config | Configuration test | `README.md` | PLANNED |
| R-087 | Active provider/model visible | P0 | Config API + frontend | UI verification | `docs/design.md` | PLANNED |
| R-088 | Ollama installation documented | P0 | Setup documentation | Manual setup test | `README.md` | PLANNED |
| R-089 | Ollama model pull command documented | P0 | Setup documentation | Manual setup test | `README.md` | PLANNED |
| R-090 | Ollama health check | P0 | `llm/ollama.py` | Health failure test | `README.md` | PLANNED |
| R-091 | Ollama unavailable behavior | P0 | Provider exceptions | Failure test | `README.md` | PLANNED |
| R-092 | Document cloud fallback behavior | P0 | Provider configuration | Configuration test | `README.md` | PLANNED |
| R-093 | No silent model fallback | P0 | Provider factory | Failure/config test | `docs/architecture.md` | PLANNED |

---

# 6. Knowledge Base and Ingestion

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-100 | Use Lenny transcript repository | P0 | `retrieval/ingest.py` | Ingestion test | `README.md` | PLANNED |
| R-101 | Transcript loader | P0 | `retrieval/loader.py` | Loader tests | `docs/architecture.md` | PLANNED |
| R-102 | Transcript cleaning | P0 | `retrieval/cleaner.py` | Cleaner tests | `docs/architecture.md` | PLANNED |
| R-103 | Metadata extraction | P0 | `retrieval/metadata.py` | Metadata tests | `docs/architecture.md` | PLANNED |
| R-104 | Chunk transcripts | P0 | `retrieval/chunker.py` | Chunking tests | `docs/architecture.md` | PLANNED |
| R-105 | Define chunk size and overlap | P0 | Chunker configuration | Chunking verification | `README.md` | PLANNED |
| R-106 | Generate embeddings | P0 | `retrieval/embeddings.py` | Embedding mock/test | `docs/architecture.md` | PLANNED |
| R-107 | Index embeddings | P0 | `retrieval/vector_store.py` | Retrieval test | `docs/architecture.md` | PLANNED |
| R-108 | Implement retrieval | P0 | `retrieval/retriever.py` | `test_retrieval.py` | `docs/architecture.md` | PLANNED |
| R-109 | Preserve transcript ID | P0 | Chunk metadata | Metadata test | `docs/architecture.md` | PLANNED |
| R-110 | Preserve title | P0 | Chunk metadata | Metadata test | `docs/architecture.md` | PLANNED |
| R-111 | Preserve guest/date when available | P0 | Chunk metadata | Metadata test | `docs/architecture.md` | PLANNED |
| R-112 | Preserve source URL | P0 | Chunk metadata | Metadata test | `docs/architecture.md` | PLANNED |
| R-113 | Preserve chunk ID | P0 | Chunk metadata | Metadata test | `docs/architecture.md` | PLANNED |
| R-114 | Document transcript selection | P0 | Ingestion configuration | Manual review | `README.md` | PLANNED |
| R-115 | Document refresh/update strategy | P0 | Ingestion script | Refresh verification | `README.md`, `docs/architecture.md` | PLANNED |
| R-116 | Preserve source traceability | P0 | Source schema/service | Retrieval tests | `docs/architecture.md` | PLANNED |

---

# 7. Grounded Conversational Assistant

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-120 | Answer product questions | P0 | Grounded chat skill | Integration test | README demo | PLANNED |
| R-121 | Answer growth questions | P0 | Grounded chat skill | Integration test | README demo | PLANNED |
| R-122 | Use transcript knowledge | P0 | Retrieval + prompt assembly | Retrieval test | `docs/architecture.md` | PLANNED |
| R-123 | Handle follow-up questions | P0 | Session context service | Multi-turn test | `docs/architecture.md` | PLANNED |
| R-124 | Preserve session context | P0 | Conversation history service | Session test | `docs/architecture.md` | PLANNED |
| R-125 | Display sources | P0 | Source response schema | API/UI test | `docs/design.md` | PLANNED |
| R-126 | Do not claim unsupported facts | P0 | Grounding prompt/policy | Empty retrieval test | `docs/architecture.md` | PLANNED |
| R-127 | Empty retrieval logic | P0 | Retrieval threshold | `test_retrieval.py` | `docs/architecture.md` | PLANNED |
| R-128 | Limitation response for weak retrieval | P0 | Grounded chat service | Empty retrieval test | README | PLANNED |

---

# 8. Ship 30 for 30 Writing Skill

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-140 | Dedicated Ship 30 skill architecture | P0 | `agents/ship30_skill.py` | Skill test | `docs/architecture.md` | PLANNED |
| R-141 | Study provided Ship 30 guide | P0 | Skill principles document | Manual review | `docs/PRD.md` / skill docs | PLANNED |
| R-142 | Extract reusable writing principles | P0 | Templates/rules/validator | Structure tests | `docs/architecture.md` | PLANNED |
| R-143 | Avoid one giant ad-hoc prompt | P0 | Modular skill pipeline | Code review | `docs/architecture.md` | PLANNED |
| R-144 | Approximately 1,250 words | P0 | Word-count validator | Output test | README | PLANNED |
| R-145 | Strong hook | P0 | Essay validator/template | Manual/output test | Skill docs | PLANNED |
| R-146 | Narrative progression | P0 | Outline generation | Output test | Skill docs | PLANNED |
| R-147 | Skimmable structure | P0 | Markdown structure rules | Output test | Skill docs | PLANNED |
| R-148 | Headings | P0 | Structure validator | Output test | Skill docs | PLANNED |
| R-149 | Bullets | P0 | Structure validator | Output test | Skill docs | PLANNED |
| R-150 | Selective bold emphasis | P0 | Structure validator | Output test | Skill docs | PLANNED |
| R-151 | Specific useful takeaway | P0 | Final section validator | Output test | Skill docs | PLANNED |
| R-152 | Ground transcript claims | P0 | Evidence retrieval | Grounding review | `docs/architecture.md` | PLANNED |
| R-153 | Outline before essay | P1 | Internal skill pipeline | Skill test | `docs/architecture.md` | PLANNED |
| R-154 | Validate grounding and structure | P0 | Ship30 validator | Unit test | `docs/architecture.md` | PLANNED |

---

# 9. Artifact Generation

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-160 | Generate Markdown artifacts | P0 | Artifact skill | Artifact tests | README | PLANNED |
| R-161 | Generate HTML/CSS artifacts | P0 | Artifact skill | Artifact tests | README | PLANNED |
| R-162 | Generate complete self-contained HTML | P0 | HTML generator rules | Validation test | `docs/architecture.md` | PLANNED |
| R-163 | Use conversation context | P0 | Context assembler | Integration test | `docs/architecture.md` | PLANNED |
| R-164 | Use retrieved knowledge where relevant | P0 | Artifact evidence service | Grounding test | `docs/architecture.md` | PLANNED |
| R-165 | Detect artifact type | P1 | Router/request schema | Routing test | `docs/architecture.md` | PLANNED |
| R-166 | Persist generated artifacts | P1 | Artifact repository | Persistence test | `docs/architecture.md` | PLANNED |

---

# 10. Artifact Viewer and Security

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-180 | Render artifacts in application | P0 | Frontend ArtifactViewer | UI test | `docs/design.md` | PLANNED |
| R-181 | Render Markdown | P0 | Markdown renderer | UI test | `docs/design.md` | PLANNED |
| R-182 | Render HTML/CSS preview | P0 | Sandboxed iframe | UI/security test | `docs/design.md` | PLANNED |
| R-183 | Do not display unsafe raw HTML directly | P0 | Sanitizer/iframe | Security test | `docs/architecture.md` | PLANNED |
| R-184 | Treat generated HTML as untrusted | P0 | Security policy | Security review | `docs/architecture.md` | PLANNED |
| R-185 | Sanitize or validate generated HTML | P0 | Artifact sanitizer | Sanitization tests | `docs/architecture.md` | PLANNED |
| R-186 | Use sandboxed iframe | P0 | Frontend viewer | Manual security verification | `docs/architecture.md` | PLANNED |
| R-187 | Restrict scripts | P0 | Sanitizer + sandbox | Security tests | `docs/architecture.md` | PLANNED |
| R-188 | Restrict inline event handlers | P0 | Sanitizer | Security tests | `docs/architecture.md` | PLANNED |
| R-189 | Restrict dangerous URLs/navigation | P0 | URL sanitizer + iframe policy | Security tests | `docs/architecture.md` | PLANNED |
| R-190 | Document permitted behavior | P0 | Security documentation | Review | `docs/architecture.md` | PLANNED |
| R-191 | Document blocked behavior | P0 | Security documentation | Review | `docs/architecture.md` | PLANNED |
| R-192 | Document limitations | P0 | Security documentation | Review | `docs/architecture.md` | PLANNED |

---

# 11. Frontend

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-200 | Main chat interface | P0 | `frontend/src/components/Chat/` | Manual UI test | `docs/design.md` | PLANNED |
| R-201 | User messages | P0 | Chat components | UI test | `docs/design.md` | PLANNED |
| R-202 | Assistant messages | P0 | Chat components | UI test | `docs/design.md` | PLANNED |
| R-203 | Loading state | P0 | Chat state | UI test | `docs/design.md` | PLANNED |
| R-204 | Error state | P0 | Error components | UI test | `docs/design.md` | PLANNED |
| R-205 | Empty state | P0 | Empty state component | UI test | `docs/design.md` | PLANNED |
| R-206 | New Chat control | P0 | Session controls | UI/API test | `docs/design.md` | PLANNED |
| R-207 | Independent sessions | P0 | Session state | Session isolation test | `docs/design.md` | PLANNED |
| R-208 | Session switching | P1 | Session sidebar | UI test | `docs/design.md` | PLANNED |
| R-209 | Display transcript title | P0 | Sources component | UI test | `docs/design.md` | PLANNED |
| R-210 | Display source identifier | P0 | Sources component | UI test | `docs/design.md` | PLANNED |
| R-211 | Display source URL when available | P0 | Sources component | UI test | `docs/design.md` | PLANNED |
| R-212 | Display active provider/model | P0 | Model indicator | UI test | `docs/design.md` | PLANNED |
| R-213 | Desktop layout | P0 | Responsive layout | Manual UI test | `docs/design.md` | PLANNED |
| R-214 | Tablet behavior | P1 | Responsive CSS | Manual UI test | `docs/design.md` | PLANNED |
| R-215 | Mobile behavior | P1 | Responsive CSS | Manual UI test | `docs/design.md` | PLANNED |
| R-216 | Keyboard navigation | P1 | Accessible components | Manual accessibility test | `docs/design.md` | PLANNED |
| R-217 | Focus states | P1 | CSS/accessibility | Manual test | `docs/design.md` | PLANNED |
| R-218 | Semantic labels | P1 | ARIA/HTML semantics | Accessibility review | `docs/design.md` | PLANNED |
| R-219 | Reasonable color contrast | P1 | Design system | Manual test | `docs/design.md` | PLANNED |

---

# 12. Deployment

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-220 | Reproducible startup | P0 | Docker Compose + Makefile | Clean startup test | README | PLANNED |
| R-221 | Prefer Docker Compose | P0 | `docker-compose.yml` | `docker compose up` | README | PLANNED |
| R-222 | Frontend service | P0 | Frontend Dockerfile | Compose verification | README | PLANNED |
| R-223 | Backend service | P0 | Backend Dockerfile | Compose verification | README | PLANNED |
| R-224 | PostgreSQL service | P0 | Compose configuration | Compose verification | README | PLANNED |
| R-225 | Document Ollama host/container strategy | P0 | Compose/docs | Manual setup test | README | PLANNED |
| R-226 | Document Docker networking for host Ollama | P0 | Compose/docs | Connection verification | README | PLANNED |
| R-227 | Provide `.env.example` | P0 | `.env.example` | Config review | README | PLANNED |
| R-228 | No secrets committed | P0 | `.gitignore` + config policy | Secret scan/manual review | README | PLANNED |

---

# 13. Observability

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-240 | Structured logs | P0 | `core/logging.py` | Log verification | `docs/architecture.md` | PLANNED |
| R-241 | Application startup log | P1 | Application lifecycle | Manual verification | README | PLANNED |
| R-242 | Configuration validation log | P1 | Config service | Config test | `docs/architecture.md` | PLANNED |
| R-243 | Database connection log | P1 | DB lifecycle | DB test | `docs/architecture.md` | PLANNED |
| R-244 | Session creation log | P1 | Session service | Log verification | `docs/architecture.md` | PLANNED |
| R-245 | Message processing log | P1 | Chat service | Log verification | `docs/architecture.md` | PLANNED |
| R-246 | Agent routing log | P1 | Router | Log verification | `docs/architecture.md` | PLANNED |
| R-247 | LLM provider selection log | P1 | Provider factory | Log verification | `docs/architecture.md` | PLANNED |
| R-248 | LLM duration log | P1 | Provider wrapper | Log verification | `docs/architecture.md` | PLANNED |
| R-249 | Retrieval duration log | P1 | Retriever | Log verification | `docs/architecture.md` | PLANNED |
| R-250 | Retrieved chunk count log | P1 | Retriever | Log verification | `docs/architecture.md` | PLANNED |
| R-251 | Empty retrieval log | P1 | Retriever | Log verification | `docs/architecture.md` | PLANNED |
| R-252 | Artifact generation log | P1 | Artifact service | Log verification | `docs/architecture.md` | PLANNED |
| R-253 | Artifact sanitization log | P1 | Artifact sanitizer | Log verification | `docs/architecture.md` | PLANNED |
| R-254 | Error logging without secrets | P0 | Exception middleware | Log review | `docs/architecture.md` | PLANNED |
| R-255 | Request/correlation IDs | P2 | Request middleware | Integration test | `docs/architecture.md` | PLANNED |

---

# 14. Resilience and Failure Handling

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-260 | Missing API key error | P0 | Provider/config validation | Failure test | README | PLANNED |
| R-261 | Ollama unavailable detection | P0 | Ollama health check | Failure test | README | PLANNED |
| R-262 | Useful Ollama unavailable response | P0 | Provider exception mapping | API test | README | PLANNED |
| R-263 | Model timeout handling | P0 | Provider timeout | Timeout test | `docs/architecture.md` | PLANNED |
| R-264 | Empty retrieval without hallucination | P0 | Grounded response policy | Retrieval/chat test | `docs/architecture.md` | PLANNED |
| R-265 | Controlled database error | P0 | Exception layer | DB failure test | `docs/architecture.md` | PLANNED |
| R-266 | Server-side technical logging | P0 | Logging middleware | Error test | `docs/architecture.md` | PLANNED |
| R-267 | Invalid artifact handling | P0 | Artifact validator | Artifact security test | `docs/architecture.md` | PLANNED |

---

# 15. Required Documentation

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-280 | Complete README | P0 | `README.md` | Documentation review | `README.md` | PLANNED |
| R-281 | Project overview | P0 | README | Review | README | PLANNED |
| R-282 | Architecture overview | P0 | README | Review | README | PLANNED |
| R-283 | Features | P0 | README | Review | README | PLANNED |
| R-284 | Prerequisites | P0 | README | Clean setup verification | README | PLANNED |
| R-285 | Installation instructions | P0 | README | Clean setup verification | README | PLANNED |
| R-286 | Environment variables | P0 | README | Config verification | README | PLANNED |
| R-287 | Ollama setup | P0 | README | Manual setup | README | PLANNED |
| R-288 | Cloud LLM setup | P0 | README | Config verification | README | PLANNED |
| R-289 | Database setup | P0 | README | Startup verification | README | PLANNED |
| R-290 | Ingestion instructions | P0 | README | Manual ingestion | README | PLANNED |
| R-291 | Docker startup | P0 | README | Compose test | README | PLANNED |
| R-292 | Local development startup | P0 | README | Manual test | README | PLANNED |
| R-293 | Testing instructions | P0 | README | Test execution | README | PLANNED |
| R-294 | Troubleshooting | P0 | README | Review | README | PLANNED |
| R-295 | Known limitations | P0 | README | Review | README | PLANNED |
| R-296 | Extension guidance | P0 | README | Review | README | PLANNED |
| R-297 | Complete PRD | P0 | `docs/PRD.md` | Documentation review | `docs/PRD.md` | PLANNED |
| R-298 | Complete design documentation | P0 | `docs/design.md` | Documentation review | `docs/design.md` | PLANNED |
| R-299 | Complete architecture documentation | P0 | `docs/architecture.md` | Documentation review | `docs/architecture.md` | PLANNED |

---

# 16. Agent Transcripts

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-310 | Create `agent_transcripts/` | P0 | Directory | File review | README | PLANNED |
| R-311 | Record task planning | P0 | Actual implementation logs | Review | Transcript files | PLANNED |
| R-312 | Record meaningful implementation attempts | P0 | Actual logs | Review | Transcript files | PLANNED |
| R-313 | Record relevant failures | P0 | Actual failures only | Review | Transcript files | PLANNED |
| R-314 | Record debugging and corrections | P0 | Actual logs | Review | Transcript files | PLANNED |
| R-315 | Remove secrets | P0 | Transcript sanitization | Secret review | README | PLANNED |
| R-316 | Do not fabricate failures | P0 | Process policy | Review | README | PLANNED |

---

# 17. Automated Testing

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-320 | Automated test suite | P0 | `backend/tests/` | `pytest` | README | PLANNED |
| R-321 | Health endpoint test | P0 | `test_health.py` | Pytest | README | PLANNED |
| R-322 | Session creation test | P0 | `test_sessions.py` | Pytest | README | PLANNED |
| R-323 | Chat validation test | P0 | `test_chat.py` | Pytest | README | PLANNED |
| R-324 | Error response test | P0 | API tests | Pytest | README | PLANNED |
| R-325 | Relevant retrieval test | P0 | `test_retrieval.py` | Pytest | README | PLANNED |
| R-326 | Empty retrieval test | P0 | `test_retrieval.py` | Pytest | README | PLANNED |
| R-327 | Metadata preservation test | P0 | `test_retrieval.py` | Pytest | README | PLANNED |
| R-328 | Grounded routing test | P0 | `test_routing.py` | Pytest | README | PLANNED |
| R-329 | Ship 30 routing test | P0 | `test_routing.py` | Pytest | README | PLANNED |
| R-330 | Artifact routing test | P0 | `test_routing.py` | Pytest | README | PLANNED |
| R-331 | Session persistence test | P0 | `test_persistence.py` | Pytest | README | PLANNED |
| R-332 | Message persistence test | P0 | `test_persistence.py` | Pytest | README | PLANNED |
| R-333 | Session isolation test | P0 | `test_persistence.py` | Pytest | README | PLANNED |
| R-334 | Avoid expensive real cloud calls in tests | P0 | Provider mocks | Test configuration review | README | PLANNED |
| R-335 | Manual UI test plan | P0 | `docs/manual_test_plan.md` | Manual execution | README | PLANNED |

---

# 18. Demo Preparation

| ID | Requirement | Priority | Implementation | Test / Verification | Documentation | Status |
|---|---|---:|---|---|---|---|
| R-340 | Explain customer problem | P0 | Demo script | Demo rehearsal | README/demo notes | PLANNED |
| R-341 | Demonstrate grounded question | P0 | Chat UI | Demo rehearsal | Demo notes | PLANNED |
| R-342 | Demonstrate source citations | P0 | Sources UI | Demo rehearsal | Demo notes | PLANNED |
| R-343 | Demonstrate follow-up conversation | P0 | Session context | Demo rehearsal | Demo notes | PLANNED |
| R-344 | Demonstrate Ollama | P0 | Model indicator | Demo rehearsal | Demo notes | PLANNED |
| R-345 | Demonstrate Ship 30 or artifact generation | P0 | Skill/artifact UI | Demo rehearsal | Demo notes | PLANNED |
| R-346 | Demonstrate Artifact Viewer | P0 | Frontend viewer | Demo rehearsal | Demo notes | PLANNED |
| R-347 | Explain technical trade-off | P0 | Demo script | Demo rehearsal | Demo notes | PLANNED |
| R-348 | Keep demo approximately 2–3 minutes | P1 | Demo script | Timed rehearsal | Demo notes | PLANNED |

---

# 19. Final Acceptance Gate

The project cannot be marked complete until all P0 requirements are `VERIFIED`.

## Backend

- [ ] FastAPI starts successfully.
- [ ] Health endpoint works.
- [ ] Request validation works.
- [ ] Structured errors exist.

## Database

- [ ] PostgreSQL persists sessions.
- [ ] Messages persist.
- [ ] Sessions are isolated.
- [ ] Database failures are handled.

## LLM

- [ ] Ollama works locally.
- [ ] Local model is used for demo.
- [ ] Cloud provider integration exists.
- [ ] Provider switching requires no code modification.
- [ ] Active provider/model is visible or clearly configurable.

## Knowledge Base

- [ ] Transcripts can be ingested.
- [ ] Metadata is preserved.
- [ ] Retrieval works.
- [ ] Answers are grounded.
- [ ] Sources are displayed.
- [ ] Empty retrieval does not cause hallucinated transcript claims.

## Agent Skills

- [ ] Grounded Chat Skill works.
- [ ] Ship 30 Skill works.
- [ ] Artifact Skill works.
- [ ] Routing is tested.
- [ ] Approved agent framework is integrated meaningfully.

## Ship 30

- [ ] Dedicated skill architecture exists.
- [ ] Output is approximately 1,250 words.
- [ ] Strong hook exists.
- [ ] Narrative progression exists.
- [ ] Headings are present.
- [ ] Bullets are present.
- [ ] Selective bold emphasis is present.
- [ ] Specific takeaway is present.
- [ ] Claims are grounded.

## Artifacts

- [ ] Markdown artifact works.
- [ ] HTML/CSS artifact works.
- [ ] Artifact Viewer works.
- [ ] Artifacts render inside the application.
- [ ] HTML is sanitized or isolated.
- [ ] Security strategy is documented.

## Deployment

- [ ] Reproducible startup exists.
- [ ] `.env.example` exists.
- [ ] No secrets are committed.
- [ ] Ollama setup is documented.
- [ ] Troubleshooting is documented.

## Quality

- [ ] Structured logs exist.
- [ ] Important failures are handled.
- [ ] Automated tests exist.
- [ ] Manual UI test plan exists.
- [ ] README is complete.
- [ ] PRD is complete.
- [ ] Design documentation is complete.
- [ ] Architecture documentation is complete.
- [ ] Agent transcripts/logs are included.

---

# Final Evaluator Review

Before submission, score the implementation from 1–10:

| Dimension | Score | Evidence |
|---|---:|---|
| Customer & Product Judgment | /10 | PRD, scope decisions, assumptions |
| Technical Execution | /10 | Working backend/frontend/database |
| Agentic Architecture & Grounding | /10 | Skills, routing, retrieval, sources |
| Deployment & Operability | /10 | Docker, configuration, resilience |
| Code Quality | /10 | Structure, tests, maintainability |
| UI/UX Quality | /10 | Chat, sources, artifacts, responsiveness |
| Communication | /10 | Documentation and demo |

## Submission Blockers

The project must not be submitted with:

- Any P0 requirement still `PLANNED`, `BLOCKED`, or unverified.
- A fake or unused agent SDK dependency.
- Ollama not working for the submitted demo.
- Unsupported transcript claims presented as facts.
- Session context leaking across sessions.
- Unsafe HTML rendered directly without a documented mitigation.
- Missing source traceability.
- Missing setup instructions or unreproducible startup.
- Missing automated tests.