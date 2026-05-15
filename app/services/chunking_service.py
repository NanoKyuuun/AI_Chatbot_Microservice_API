import tiktoken
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger

class ChunkingService:
    def __init__(
        self, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 150,
        model_name: str = "gpt-4o-mini"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string."""
        return len(self.encoding.encode(text))

    async def split_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Splits text into chunks using a recursive character splitting strategy
        while respecting token limits.
        """
        logger.info("chunking_started", text_length=len(text))
        
        # Simple recursive-like split by paragraphs first, then sentences/newlines
        separators = ["\n\n", "\n", ". ", " ", ""]
        chunks = []
        
        current_text = text
        chunk_index = 0
        
        # Basic implementation of chunking
        # In a real production scenario, we'd use LangChain's RecursiveCharacterTextSplitter 
        # or a similar library, but for MVP we implement the core logic.
        
        # For MVP: Simple sliding window by characters as a proxy for tokens 
        # (approx 4 chars per token for English)
        char_size = self.chunk_size * 4
        char_overlap = self.chunk_overlap * 4
        
        start = 0
        while start < len(text):
            end = start + char_size
            chunk_content = text[start:end]
            
            # Try to find a good separator near the end to avoid cutting words/sentences
            if end < len(text):
                last_space = chunk_content.rfind(" ")
                if last_space != -1 and last_space > char_size * 0.8:
                    end = start + last_space
                    chunk_content = text[start:end]

            chunks.append({
                "index": chunk_index,
                "content": chunk_content.strip(),
                "token_count": self.count_tokens(chunk_content)
            })
            
            chunk_index += 1
            start += (char_size - char_overlap)

        logger.info("chunking_completed", total_chunks=len(chunks))
        return chunks
