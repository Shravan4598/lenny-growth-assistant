from app.core.exceptions import AppError
from app.llm.base import LLMProvider
from app.api.schemas.chat import ChatResponse, SourceResponse
from app.rag.prompts import build_rag_prompt
from app.retrieval.models import RetrievedChunk
from app.retrieval.service import RetrievalService


class RAGService:
    """Retrieval-Augmented Generation service."""

    MAX_CHUNK_CHARS = 800

    # 80 was too restrictive for useful grounded answers.
    MAX_OUTPUT_TOKENS = 300

    MAX_HISTORY_CHARS = 2000

    NO_CONTEXT_RESPONSE = (
        "I couldn't find enough information in the available "
        "Lenny material to answer that question."
    )

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_provider: LLMProvider,
    ) -> None:
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider

    async def answer(
        self,
        question: str,
        top_k: int = 5,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> ChatResponse:
        """
        Retrieve relevant Lenny knowledge and generate a grounded answer.
        """

        question = question.strip()

        if not question:
            raise AppError(
                status_code=400,
                code="INVALID_QUESTION",
                message="Question cannot be empty.",
            )

        # ---------------------------------------------------------
        # 1. Normalize conversation history
        # ---------------------------------------------------------

        history_text = self._format_conversation_history(
            conversation_history
        )

        # ---------------------------------------------------------
        # 2. Build conversation-aware retrieval query
        # ---------------------------------------------------------

        retrieval_query = self._build_retrieval_query(
            question=question,
            conversation_history=history_text,
        )

        # ---------------------------------------------------------
        # 3. Retrieve relevant transcript chunks
        # ---------------------------------------------------------

        retrieved_chunks = self.retrieval_service.retrieve(
            query=retrieval_query,
            top_k=top_k,
        )

        # ---------------------------------------------------------
        # 4. No relevant context
        # ---------------------------------------------------------

        if not retrieved_chunks:
            return ChatResponse(
                provider=self.llm_provider.provider_name,
                model=self.llm_provider.model_name,
                response=self.NO_CONTEXT_RESPONSE,
                sources=[],
            )

        # ---------------------------------------------------------
        # 5. Build bounded transcript context
        # ---------------------------------------------------------

        context = self._build_context(
            retrieved_chunks,
        )

        # ---------------------------------------------------------
        # 6. Build grounded prompt
        # ---------------------------------------------------------

        prompt = build_rag_prompt(
            question=question,
            context=context,
            conversation_history=history_text,
        )

        # ---------------------------------------------------------
        # 7. Generate answer
        # ---------------------------------------------------------

        result = await self.llm_provider.generate(
            prompt,
            temperature=0.2,
            max_tokens=self.MAX_OUTPUT_TOKENS,
        )

        # ---------------------------------------------------------
        # 8. Convert retrieved chunks into API sources
        # ---------------------------------------------------------

        sources = [
            SourceResponse(
                chunk_id=item.chunk.chunk_id,
                title=item.chunk.title,
                guest=item.chunk.guest,
                date=item.chunk.date,
                source_url=item.chunk.source_url,
                score=item.score,
            )
            for item in retrieved_chunks
        ]

        # ---------------------------------------------------------
        # 9. Return response
        # ---------------------------------------------------------

        return ChatResponse(
            provider=result.provider,
            model=result.model,
            response=result.content,
            sources=sources,
        )

    @staticmethod
    def _format_conversation_history(
        conversation_history: list[dict[str, str]] | None,
    ) -> str:
        """Convert structured conversation history into prompt text."""

        if not conversation_history:
            return "No previous conversation."

        lines: list[str] = []

        for message in conversation_history:
            role = message.get("role", "").strip()
            content = message.get("content", "").strip()

            if not content:
                continue

            if role not in {"user", "assistant"}:
                continue

            lines.append(
                f"{role.capitalize()}: {content}"
            )

        if not lines:
            return "No previous conversation."

        return "\n".join(lines)

    @classmethod
    def _build_retrieval_query(
        cls,
        question: str,
        conversation_history: str,
    ) -> str:
        """Build a retrieval-friendly query using recent conversation."""

        question = question.strip()

        if not conversation_history:
            return question

        history = conversation_history.strip()

        if not history:
            return question

        if history.lower() == "no previous conversation.":
            return question

        if len(history) > cls.MAX_HISTORY_CHARS:
            history = history[-cls.MAX_HISTORY_CHARS:]

        return (
            "Recent conversation:\n"
            f"{history}\n\n"
            "Current user question:\n"
            f"{question}"
        )

    @classmethod
    def _build_context(
        cls,
        retrieved_chunks: list[RetrievedChunk],
    ) -> str:
        """Convert retrieved chunks into bounded LLM context."""

        if not retrieved_chunks:
            return "No relevant transcript context was found."

        sections: list[str] = []

        for index, item in enumerate(
            retrieved_chunks,
            start=1,
        ):
            chunk = item.chunk

            chunk_text = chunk.text.strip()

            if len(chunk_text) > cls.MAX_CHUNK_CHARS:
                chunk_text = (
                    chunk_text[:cls.MAX_CHUNK_CHARS]
                    + "\n[Transcript truncated]"
                )

            section = f"""
SOURCE {index}

Title: {chunk.title}
Guest: {chunk.guest or "Unknown"}
Date: {chunk.date or "Unknown"}
URL: {chunk.source_url or "N/A"}

Transcript:

{chunk_text}
""".strip()

            sections.append(section)

        return "\n\n".join(sections)