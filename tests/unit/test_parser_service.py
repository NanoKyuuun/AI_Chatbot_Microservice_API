import pytest
from unittest.mock import MagicMock, patch
from app.services.parser_service import ParserService
from app.core.errors import AppError

@pytest.mark.asyncio
async def test_parse_text(tmp_path):
    # Create a temporary text file
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.txt"
    content = "Hello World"
    p.write_text(content)
    
    result = await ParserService._parse_text(str(p))
    assert result == content

@pytest.mark.asyncio
async def test_parse_file_unsupported():
    with pytest.raises(AppError) as excinfo:
        await ParserService.parse_file("test.unknown", "unknown")
    assert excinfo.value.code == "UNSUPPORTED_FILE_TYPE"

@pytest.mark.asyncio
@patch("app.services.parser_service.fitz.open")
async def test_parse_pdf_mock(mock_fitz_open):
    # Mock fitz document and page
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "PDF Content"
    mock_doc.__iter__.return_value = [mock_page]
    mock_doc.__enter__.return_value = mock_doc
    mock_fitz_open.return_value = mock_doc
    
    result = await ParserService._parse_pdf("dummy.pdf")
    assert result == "PDF Content"
    mock_fitz_open.assert_called_once_with("dummy.pdf")

@pytest.mark.asyncio
@patch("app.services.parser_service.DocxDocument")
async def test_parse_docx_mock(mock_docx_doc):
    # Mock docx paragraphs
    mock_para = MagicMock()
    mock_para.text = "Docx Content"
    mock_doc = MagicMock()
    mock_doc.paragraphs = [mock_para]
    mock_docx_doc.return_value = mock_doc
    
    result = await ParserService._parse_docx("dummy.docx")
    assert result == "Docx Content"
    mock_docx_doc.assert_called_once_with("dummy.docx")
