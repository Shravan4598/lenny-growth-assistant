# Architecture
# The Lenny Growth Assistant

## 1. Architecture Overview

The system is designed as a modular full-stack application.

```text
┌──────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                  React + Vite + TypeScript                   │
│                                                              │
│   Sessions │ Chat │ Sources │ Model Indicator │ Artifacts    │
└─────────────────────────────┬────────────────────────────────┘
                              │ HTTPS / REST
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                         FastAPI                              │
│                                                              │
│  API Routes → Services → Agent Router → Skills               │
│                                      │                       │
│                         ┌────────────┼────────────┐          │
│                         ▼            ▼            ▼          │
│                   Grounded Chat    Ship 30     Artifact      │
└───────────────┬──────────────────────┬───────────────────────┘
                │                      │
                ▼                      ▼
       ┌─────────────────┐    ┌─────────────────────┐
       │ Retrieval Layer │    │ LLM Provider Layer  │
       │                 │    │                     │
       │ Embeddings      │    │ Base Provider       │
       │ FAISS           │    │ ├─ Ollama           │
       │ Metadata        │    │ └─ Cloud            │
       └─────────────────┘    └─────────────────────┘
                │                      │
                ▼                      ▼
       Transcript Corpus          Model Inference

                │
                ▼
       ┌─────────────────┐
       │ PostgreSQL      │
       │                 │
       │ Users           │
       │ Sessions        │
       │ Messages        │
       │ Artifacts       │
       └─────────────────┘