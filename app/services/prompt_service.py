from typing import List, Dict, Any, Optional
from app.schemas.search import SearchResult

class PromptService:
    DEFAULT_SYSTEM_PROMPT = (
        "Anda adalah asisten AI yang menjawab berdasarkan konteks yang diberikan sistem.\n"
        "Gunakan hanya informasi yang tersedia dalam konteks jika pertanyaan berkaitan dengan dokumen.\n"
        "Jika konteks tidak cukup, katakan bahwa informasi tidak ditemukan dalam dokumen.\n"
        "Jangan membuat sumber palsu.\n"
        "Jawab dengan bahasa yang jelas, ringkas, dan sesuai kebutuhan pengguna.\n"
        "Sertakan sumber jika tersedia."
    )

    CONTEXT_TEMPLATE = (
        "Berikut konteks yang relevan dari dokumen:\n\n"
        "{chunks_content}"
    )

    CHUNK_TEMPLATE = (
        "[Source {index}]\n"
        "Document: {title}\n"
        "Page: {page_number}\n"
        "Content:\n"
        "{content}\n"
    )

    @staticmethod
    def format_context(search_results: List[SearchResult]) -> str:
        """
        Format list of search results into a context string.
        """
        if not search_results:
            return "Tidak ada konteks yang relevan ditemukan dalam dokumen."
            
        chunks_text = []
        for i, res in enumerate(search_results, 1):
            chunk_text = PromptService.CHUNK_TEMPLATE.format(
                index=i,
                title=res.title or "Unknown",
                page_number=res.page_number or "N/A",
                content=res.content or ""
            )
            chunks_text.append(chunk_text)
            
        return PromptService.CONTEXT_TEMPLATE.format(
            chunks_content="\n".join(chunks_text)
        )

    @staticmethod
    def build_messages(
        user_query: str,
        context_str: Optional[str] = None,
        system_prompt: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        Assemble the messages for the LLM call.
        """
        messages = []
        
        # 1. System message
        messages.append({
            "role": "system",
            "content": system_prompt or PromptService.DEFAULT_SYSTEM_PROMPT
        })
        
        # 2. Add chat history if any (could be limited later)
        if chat_history:
            messages.extend(chat_history)
            
        # 3. Add Context and User Query
        content = ""
        if context_str:
            content += context_str + "\n\n"
            
        content += f"Pertanyaan pengguna:\n{user_query}"
        
        messages.append({
            "role": "user",
            "content": content
        })
        
        return messages
