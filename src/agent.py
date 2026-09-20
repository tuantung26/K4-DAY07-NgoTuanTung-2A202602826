from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        if self.store.get_collection_size() == 0:
            return "Không tìm thấy tài liệu phù hợp trong cơ sở tri thức."

        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy tài liệu phù hợp trong cơ sở tri thức."

        context_parts: list[str] = []
        for i, r in enumerate(results, start=1):
            source = r.get("metadata", {}).get("source", r.get("id", f"doc_{i}"))
            context_parts.append(f"[{i}] (Nguồn: {source}):\n{r.get('content', '')}")
        context_str = "\n\n".join(context_parts)

        prompt = (
            f"Dưới đây là các đoạn thông tin ngữ cảnh được truy xuất:\n\n"
            f"{context_str}\n\n"
            f"Câu hỏi: {question}\n\n"
            f"Hãy trả lời câu hỏi chỉ dựa trên các ngữ cảnh trên và trích dẫn nguồn [1], [2], ... tương ứng."
        )
        return self.llm_fn(prompt)
