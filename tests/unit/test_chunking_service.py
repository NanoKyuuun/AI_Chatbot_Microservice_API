import pytest
from app.services.chunking_service import ChunkingService

@pytest.fixture
def chunking_service():
    return ChunkingService(chunk_size=10, chunk_overlap=2)

def test_count_tokens(chunking_service):
    text = "Hello world"
    # tiktoken encoding for gpt-4o-mini usually gives 2 tokens for "Hello world"
    tokens = chunking_service.count_tokens(text)
    assert tokens > 0

@pytest.mark.asyncio
async def test_split_text_short(chunking_service):
    text = "Short text"
    chunks = await chunking_service.split_text(text)
    assert len(chunks) == 1
    assert chunks[0]["content"] == text
    assert chunks[0]["index"] == 0

@pytest.mark.asyncio
async def test_split_text_long():
    # Use a smaller chunk size to force splitting
    service = ChunkingService(chunk_size=5, chunk_overlap=1)
    # Approx 4 chars per token, so 5 tokens ~ 20 chars
    text = "This is a very long text that should be split into multiple chunks because it exceeds the chunk size limit."
    chunks = await service.split_text(text)
    assert len(chunks) > 1
    assert chunks[0]["index"] == 0
    assert chunks[1]["index"] == 1
