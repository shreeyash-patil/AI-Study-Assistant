import fitz
import uuid
import os

def parse_pdf(file_bytes: bytes) -> list[str]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    chunks = []
    
    for page in doc:
        text = page.get_text()
        if text.strip():
            chunks.append(text)
    
    return chunks

def generate_session_id() -> str:
    return str(uuid.uuid4())