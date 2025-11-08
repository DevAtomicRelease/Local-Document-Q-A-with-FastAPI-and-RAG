# backend/app/ingest.py
import hashlib
from pathlib import Path
import mimetypes
from typing import Tuple, List, Dict, Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from .ocr_utils import ocr_image_pil, ocr_pdf, extract_text_from_pdf_with_pymupdf
from .embed_store import add_documents_to_chroma, file_exists
from .config import DOCS_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def compute_file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_file_text(file_path: str) -> List[Dict[str, Any]]:
    """
    Loads text and returns a list of dictionaries: [{"text": str, "page": int}, ...]
    """
    mime, _ = mimetypes.guess_type(file_path)
    ext = Path(file_path).suffix.lower()
    
    if ext in (".txt", ".md"):
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        return [{"text": text, "page": 1}] # Treat as one page
    
    if ext == ".pdf":
        page_data = extract_text_from_pdf_with_pymupdf(file_path)
        # Fallback to OCR if PyMuPDF finds no text
        if not any(p["text"] for p in page_data):
            return ocr_pdf(file_path)
        return page_data
    
    if ext in (".png", ".jpg", ".jpeg", ".tiff"):
        text = ocr_image_pil(file_path)
        return [{"text": text, "page": 1}] # Treat as one page
    
    raise ValueError(f"Unsupported file type: {file_path}")


def chunk_texts(text: str, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)


def ingest_path(file_path: str) -> Tuple[bool, int, str]:
    """
    Ingest one file if not already present.
    Returns (skipped, added_chunks, file_hash)
    """
    file_hash = compute_file_hash(file_path)
    if file_exists(file_hash):
        return True, 0, file_hash

    # This is now a list of {"text": "...", "page": X}
    page_data_list = load_file_text(file_path)
    
    docs = []
    source_name = Path(file_path).name
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    for page_data in page_data_list:
        page_text = page_data["text"]
        page_num = page_data["page"]
        
        # Chunk the text *of this specific page*
        chunks = splitter.split_text(page_text)
        
        for i, chunk in enumerate(chunks):
            docs.append({
                # New ID format is safer
                "id": f"{file_hash}_p{page_num}_{i}", 
                "text": chunk,
                "metadata": {
                    "source": source_name, 
                    "file_hash": file_hash, 
                    "page": page_num, # <-- THE CRITICAL ADDITION
                    "chunk_on_page": i
                },
            })

    added = add_documents_to_chroma(docs)
    return False, added, file_hash


def ingest_folder(folder: str = DOCS_DIR) -> int:
    total = 0
    for p in Path(folder).rglob("*"):
        if p.is_file():
            skipped, added, _ = ingest_path(str(p))
            if not skipped:
                total += added
    return total