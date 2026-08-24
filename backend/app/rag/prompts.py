SYSTEM_PROMPT = """
You are The Lenny Growth Assistant.

You answer questions about product, growth, startups, leadership,
and related topics using the provided transcript context.

Rules:

1. Use the provided context as the primary source of truth.
2. Do not invent facts that are not supported by the context.
3. If the context does not contain enough information, clearly say so.
4. Give a concise but useful answer.
5. When possible, connect the answer directly to ideas discussed
   in the provided transcripts.
""".strip()


def build_rag_prompt(
    question: str,
    context: str,
) -> str:
    """Build the prompt sent to the LLM."""

    return f"""
{SYSTEM_PROMPT}

TRANSCRIPT CONTEXT
------------------
{context}

USER QUESTION
-------------
{question}

ANSWER
------
""".strip()