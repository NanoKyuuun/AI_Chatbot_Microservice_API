import pytest
from app.services.prompt_service import PromptService
from app.schemas.search import SearchResult

def test_format_context_empty():
    result = PromptService.format_context([])
    assert "Tidak ada konteks" in result

def test_format_context_with_results():
    results = [
        SearchResult(
            chunk_uuid="1",
            document_uuid="doc1",
            title="Doc 1",
            content="Content 1",
            page_number=1,
            score=0.9
        )
    ]
    result = PromptService.format_context(results)
    assert "[Source 1]" in result
    assert "Doc 1" in result
    assert "Content 1" in result

def test_build_messages_basic():
    query = "Apa itu AI?"
    messages = PromptService.build_messages(query)
    
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert query in messages[1]["content"]

def test_build_messages_with_context():
    query = "Apa itu AI?"
    context = "AI adalah kecerdasan buatan."
    messages = PromptService.build_messages(query, context_str=context)
    
    assert len(messages) == 2
    assert context in messages[1]["content"]
    assert query in messages[1]["content"]

def test_build_messages_with_history():
    query = "Lanjutkan."
    history = [
        {"role": "user", "content": "Halo"},
        {"role": "assistant", "content": "Hai, ada yang bisa dibantu?"}
    ]
    messages = PromptService.build_messages(query, chat_history=history)
    
    # System + History (2) + User = 4
    assert len(messages) == 4
    assert messages[1]["content"] == "Halo"
    assert messages[2]["content"] == "Hai, ada yang bisa dibantu?"
    assert query in messages[3]["content"]
