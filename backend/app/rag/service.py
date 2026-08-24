from app.llm.base import LLMProvider
from app.rag.models import ChatResponse, SourceResponse
from app.rag.prompts import build_rag_prompt
from app.retrieval.models import RetrievedChunk
from app.retrieval.service import RetrievalService


class RAGService:
    """Retrieval-Augmented Generation service."""

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
    ) -> ChatResponse:
        """Retrieve relevant context and generate an answer."""

        question = question.strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        retrieved_chunks = self.retrieval_service.retrieve(
            query=question,
            top_k=top_k,
        )

        context = self._build_context(
            retrieved_chunks,
        )

        prompt = build_rag_prompt(
            question=question,
            context=context,
        )

        result = await self.llm_provider.generate(
            prompt,
            temperature=0.2,
            max_tokens=None,
        )

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

        return ChatResponse(
            provider=result.provider,
            model=result.model,
            response=result.content,
            sources=sources,
        )

    @staticmethod
    def _build_context(
        retrieved_chunks: list[RetrievedChunk],
    ) -> str:
        """Convert retrieved chunks into LLM context."""

        if not retrieved_chunks:
            return "No relevant transcript context was found."

        sections: list[str] = []

        for index, item in enumerate(
            retrieved_chunks,
            start=1,
        ):
            chunk = item.chunk

            section = f"""
SOURCE {index}

Title: {chunk.title}
Guest: {chunk.guest or "Unknown"}
Date: {chunk.date or "Unknown"}
URL: {chunk.source_url or "N/A"}

Transcript:
{chunk.text}
""".strip()

            sections.append(section)

        return "\n\n".join(sections)