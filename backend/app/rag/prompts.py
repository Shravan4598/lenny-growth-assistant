SYSTEM_PROMPT = """
You are The Lenny Growth Assistant.

You answer questions about product management, growth, startups,
leadership, founders, and related topics.

Use the provided transcript context as your primary source of truth.

Rules:
1. Do not invent facts.
2. Use the transcript context whenever it is relevant.
3. If the context does not contain enough information, say that clearly.
4. Give a concise and useful answer.
5. Do not claim that something came from Lenny's content unless it is
   supported by the provided context.
""".strip()


def build_rag_prompt(
    question: str,
    context: str,
) -> str:
    """Build the final prompt sent to the LLM."""

    return f"""
{SYSTEM_PROMPT}

TRANSCRIPT CONTEXT
==================

{context}

USER QUESTION
=============

{question}

ANSWER
======

Provide the best answer using the transcript context above.
""".strip()