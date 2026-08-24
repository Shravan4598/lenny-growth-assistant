
---

### File: `docs/design.md`

**Purpose:** UI/UX and interaction design specification.

```markdown id="rm4o6h"
# Design Specification
# The Lenny Growth Assistant

## 1. Design Goal

The interface should make it easy for a user to:

1. Start a new conversation.
2. Ask a product or growth question.
3. Understand the answer.
4. Inspect sources.
5. Continue the conversation.
6. Generate a reusable artifact.
7. View the artifact without leaving the application.

The design principle is:

> Clarity over visual complexity. Reliability over animation.

---

# 2. Information Architecture

```text
Application
│
├── Session Sidebar
│   ├── New Chat
│   └── Session List
│
├── Chat Workspace
│   ├── Empty State
│   ├── Conversation
│   ├── Sources
│   ├── Loading State
│   ├── Error State
│   └── Message Composer
│
└── Artifact Viewer
    ├── Empty State
    ├── Markdown Renderer
    └── HTML Sandbox Preview