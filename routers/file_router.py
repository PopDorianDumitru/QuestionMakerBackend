from typing import Optional
from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from docling.document_converter import DocumentConverter
from pathlib import Path
import tempfile
from docling.datamodel.base_models import InputFormat
from services.file_converter import convert_docx, convert_pdf, convert_pptx
import os
from services.firebase_service import service
# Create a new router for file transformation
file_router = APIRouter()

converter = DocumentConverter(
    allowed_formats=[InputFormat.PPTX, InputFormat.PDF, InputFormat.DOCX, InputFormat.ASCIIDOC],
)

@file_router.post("/transform/{format}")
async def transform_file(file: UploadFile = File(...), format: str = "", authorization: Optional[str] = Header(None)):
    await service.turnOffFreeTrial(authorization)
    await service.canCreateQuiz(authorization)
    
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = Path(tmp.name)
    converted_result = None
    if format == "docx":
        converted_result = convert_docx(tmp_path)
    elif format == "pdf":
        converted_result = convert_pdf(tmp_path)
    elif format == "pptx":
        result = converter.convert(tmp_path)
        converted_result = convert_pptx(result)
    else:
        os.remove(tmp_path)
        return {"error": "Invalid format"}
    os.remove(tmp_path)
    return {"document": converted_result}

