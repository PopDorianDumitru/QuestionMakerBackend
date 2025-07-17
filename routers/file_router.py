from fastapi import APIRouter, UploadFile, File
from docling.document_converter import DocumentConverter
from pathlib import Path
import tempfile
from docling.datamodel.base_models import InputFormat
from services.file_converter import convert_docx, convert_pdf, convert_pptx

# Create a new router for file transformation
file_router = APIRouter()

converter = DocumentConverter(
    allowed_formats=[InputFormat.PPTX, InputFormat.PDF, InputFormat.DOCX, InputFormat.ASCIIDOC],
)

@file_router.post("/transform/{format}")
async def transform_file(file: UploadFile = File(...), format: str = ""):
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = Path(tmp.name)
    result = converter.convert(tmp_path)
    converted_result = None
    if format == "docx":
        converted_result = convert_docx(result)
    elif format == "pdf":
        converted_result = convert_pdf(result)
    elif format == "pptx":
        converted_result = convert_pptx(result)
    else:
        return {"error": "Invalid format"}
    return {"document": converted_result}

