# backend/app/ocr_utils.py
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import tempfile
import os
from typing import List, Dict, Any

def ocr_image_pil(image_path, lang='eng') -> str:
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang=lang)
    return text

def ocr_pdf(pdf_path, lang='eng') -> List[Dict[str, Any]]:
    pages = convert_from_path(pdf_path)
    page_data = []
    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page, lang=lang)
        if text.strip():
            page_data.append({"text": text, "page": i + 1})
    return page_data

def extract_text_from_pdf_with_pymupdf(pdf_path) -> List[Dict[str, Any]]:
    doc = fitz.open(pdf_path)
    page_data = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        if text.strip():
            page_data.append({"text": text, "page": i + 1}) 
    doc.close()
    return page_data