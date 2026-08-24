SYSTEM_PROMPT = """
You are The Lenny Growth Assistant.

Answer the user's question using ONLY the transcript context.

Rules:
- Do not invent facts.
- If the context is insufficient, say:
  "The transcript context does not contain enough information to answer this."
- Do not attribute statements to Lenny or a guest unless supported
  by the context.
- Be concise and directly answer the question.
- Prefer specific examples from the context.
""".strip()


def build_rag_prompt(
    question: str,
    context: str,
) -> str:
    """Build the final prompt sent to the LLM."""

    return f"""
{SYSTEM_PROMPT}

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
""".strip()