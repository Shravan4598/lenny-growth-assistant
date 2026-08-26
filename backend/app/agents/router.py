"""Deterministic intent routing for agent skills."""

import structlog


logger = structlog.get_logger(__name__)


def determine_skill(prompt: str) -> str:
    """
    Route a user prompt to the appropriate agent skill.

    Routing is deterministic based on keywords and patterns.

    Returns:
        str: One of:
            - "grounded_chat"
            - "ship30"
            - "artifact"
    """

    prompt_lower = prompt.lower().strip()

    # ==========================================================
    # Ship 30 for 30
    # ==========================================================

    ship30_keywords = [
        "ship 30",
        "ship 30 for 30",
        "ship30",
        "ship30 essay",
        "ship 30 essay",
        "30-day plan",
        "30 day plan",
        "30 days writing",
        "shipping",
        "written plan",
        "content plan",
        "content strategy",
    ]

    if any(
        keyword in prompt_lower
        for keyword in ship30_keywords
    ):
        logger.info(
            "routing_decision",
            skill="ship30",
            reason="ship30_keyword_matched",
        )

        return "ship30"

    # ==========================================================
    # Artifact Generation
    # ==========================================================

    artifact_keywords = [
        "create a memo",
        "write a memo",
        "create a document",
        "generate document",
        "create template",
        "html artifact",
        "markdown document",
        "create html",
        "create design",
        "create framework",
        "strategic plan",
        "project plan",
    ]

    if any(
        keyword in prompt_lower
        for keyword in artifact_keywords
    ):
        logger.info(
            "routing_decision",
            skill="artifact",
            reason="artifact_keyword_matched",
        )

        return "artifact"

    # ==========================================================
    # Default Grounded Chat
    # ==========================================================

    logger.info(
        "routing_decision",
        skill="grounded_chat",
        reason="default",
    )

    return "grounded_chat"