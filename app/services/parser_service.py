import os
from typing import BinaryIO, List, Dict, Any
import fitz  # PyMuPDF
from docx import Document as DocxDocument
import pandas as pd
from bs4 import BeautifulSoup
import markdown
from app.core.logging import logger
from app.core.errors import AppError
from fastapi import status

class ParserService:
    @staticmethod
    async def parse_file(file_path: str, file_type: str) -> str:
        """
        Main entry point to parse a file based on its type.
        Returns the extracted text.
        """
        logger.info("parsing_file_started", path=file_path, type=file_type)
        
        try:
            if file_type == "pdf":
                return await ParserService._parse_pdf(file_path)
            elif file_type == "docx":
                return await ParserService._parse_docx(file_path)
            elif file_type in ["xlsx", "xls"]:
                return await ParserService._parse_excel(file_path)
            elif file_type == "csv":
                return await ParserService._parse_csv(file_path)
            elif file_type in ["txt", "md"]:
                return await ParserService._parse_text(file_path)
            elif file_type == "html":
                return await ParserService._parse_html(file_path)
            else:
                logger.error("unsupported_file_type", type=file_type)
                raise AppError(
                    code="UNSUPPORTED_FILE_TYPE",
                    message=f"File type {file_type} is not supported",
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
                )
        except Exception as e:
            logger.exception("parsing_failed", path=file_path, error=str(e))
            if isinstance(e, AppError):
                raise e
            raise AppError(
                code="PARSING_FAILED",
                message=f"Failed to parse {file_type} file",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @staticmethod
    async def _parse_pdf(file_path: str) -> str:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    @staticmethod
    async def _parse_docx(file_path: str) -> str:
        doc = DocxDocument(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    @staticmethod
    async def _parse_excel(file_path: str) -> str:
        df_dict = pd.read_excel(file_path, sheet_name=None)
        output = []
        for sheet_name, df in df_dict.items():
            output.append(f"Sheet: {sheet_name}")
            output.append(df.to_string(index=False))
        return "\n\n".join(output)

    @staticmethod
    async def _parse_csv(file_path: str) -> str:
        df = pd.read_csv(file_path)
        return df.to_string(index=False)

    @staticmethod
    async def _parse_text(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @staticmethod
    async def _parse_html(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator="\n")
