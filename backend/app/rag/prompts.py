"""Prompts for RAG generation and agent skills."""


def build_rag_prompt(
    question: str,
    context: str,
    conversation_history: str | None = None,
) -> str:
    """
    Build a grounded RAG prompt.

    Args:
        question: User's question
        context: Retrieved transcript context
        conversation_history: Previous conversation

    Returns:
        Formatted prompt for the LLM
    """

    history_section = ""
    if conversation_history and conversation_history != "No previous conversation.":
        history_section = f"""
Previous Conversation:
{conversation_history}

"""

    return f"""You are the Lenny Growth Assistant, an AI helper specializing in product and growth knowledge.

{history_section}
Transcript Context:
{context}

User Question: {question}

Instructions:
1. Answer the user's question using ONLY the provided transcript context.
2. If the context does not contain relevant information, respond: "I couldn't find enough information in the available Lenny material to answer that question."
3. Be specific and cite sources when relevant.
4. Keep your response concise and actionable.
5. Do NOT make up information or claim transcript content that is not shown above.

Answer:
"""


def build_ship30_prompt(
    topic: str,
    context: str,
    conversation_history: str | None = None,
) -> str:
    """
    Build a Ship 30 plan generation prompt.

    Args:
        topic: The topic or idea for the plan
        context: Retrieved transcript knowledge
        conversation_history: Previous conversation

    Returns:
        Formatted prompt for the LLM
    """

    history_section = ""
    if conversation_history and conversation_history != "No previous conversation.":
        history_section = f"""
Previous Discussion:
{conversation_history}

"""

    return f"""You are a content strategy and execution planning expert specializing in product and growth topics.

Create a structured "Ship 30 for 30" execution plan for the following topic:

Topic: {topic}

{history_section}
Related Knowledge from Lenny's Podcast/Newsletter:
{context}

Generate a comprehensive 30-day plan with the following structure:

For each day (Day 1 through Day 30):
- **Day [N]**
  - **Objective:** What will be accomplished today
  - **Action:** Specific steps to take
  - **Deliverable:** Concrete output (blog post, memo, framework, etc.)

Requirements:
1. Each day should be distinct and build on previous days
2. The plan should be grounded in the provided transcript knowledge
3. Include a strong hook in the early days (Days 1-3)
4. Build toward a climactic or significant deliverable around Day 15
5. Include a strong conclusion/takeaway in the final days (Days 28-30)
6. Use the provided context to make recommendations specific to Lenny's insights
7. Make it actionable and specific

Start the plan immediately with "Day 1" without additional preamble.
"""


def build_artifact_prompt(
    request: str,
    artifact_type: str,
    context: str,
) -> str:
    """
    Build an artifact generation prompt.

    Args:
        request: What the user wants generated
        artifact_type: Type of artifact (markdown, html, etc.)
        context: Retrieved knowledge

    Returns:
        Formatted prompt for the LLM
    """

    format_instructions = ""

    if artifact_type == "html":
        format_instructions = """
Format the output as clean, production-quality HTML/CSS.
Include embedded CSS in a <style> tag.
Make it visually appealing and professional.
Ensure it is self-contained (no external dependencies).
"""

    elif artifact_type == "markdown":
        format_instructions = """
Format the output as well-structured Markdown.
Use clear headings, bullet points, and formatting.
Make it readable and scannable.
"""

    return f"""You are an expert in creating professional documents and frameworks grounded in product and growth expertise.

User Request: {request}

Format: {artifact_type.upper()}
{format_instructions}

Related Knowledge from Lenny's Podcast/Newsletter:
{context}

Generate the requested artifact with the following principles:
1. Professional, clear, and actionable
2. Grounded in the provided knowledge when possible
3. Well-structured with clear hierarchy
4. Specific and practical, not generic
5. Appropriate length for the artifact type (300-2000 words)

Do NOT include explanatory preamble. Output the artifact directly.
"""