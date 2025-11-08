# Local-Document-Q-A-with-FastAPI-and-RAG
This project is a complete, 100% local RAG (Retrieval-Augmented Generation) backend. It's a FastAPI server that ingests your private documents (PDFs, images, text files) and uses a locally-hosted LLM via LM Studio to answer questions about them.
The entire system is designed for privacy and offline use, ensuring none of your data ever leaves your machine.

## Core Features
- FastAPI Backend: A high-performance, asynchronous web server with interactive API docs.
- Local-First AI: Uses LM Studio to serve both the LLM (e.g., Llama 3.1 8B) and the embedding model (nomic-embed-text).
- Multi-Modal Ingestion: Can read .pdf, .png, .jpg, .jpeg, .txt, and .md files.
- Smart PDF & Image Handling: Uses PyMuPDF for fast digital text extraction and falls back to Tesseract-OCR for scanned images or PDFs.
- Page-Aware Storage: Chunks are saved with page number metadata ({"page": 5, ...}), allowing for precise answers and citations.
- Idempotent Uploads: Uses a file_hash to prevent processing and storing the same file multiple times.
- Query Filtering: The API supports querying your entire document library or filtering to a single, specific file.

## Tech Stack
- Python 3.10+
- FastAPI: For the web server and API.
- ChromaDB: As the local, persistent vector store.
- LM Studio: As the server for both the embedding model and the LLM.
- Pytesseract: The OCR engine for images and scanned PDFs.
- PyMuPDF (fitz): For high-speed digital PDF text extraction.
- Langchain (text-splitters): For document chunking.

## How It Works
The system is built on two main workflows: Ingestion and Querying.
  - Ingestion (/upload_and_query):
    - A file is uploaded to the FastAPI server.
    - ingest.py calculates the file's hash to check for duplicates.
    - ocr_utils.py extracts text and page numbers from the file (using Tesseract if it's an image).
    - The text is split into chunks, each retaining its page and file_hash metadata.
    - embed_store.py sends these chunks to the LM Studio embeddings endpoint (nomic-embed-text).
    - The resulting vectors and metadata are stored in the chroma_db directory.

Querying (/upload_and_query or /query):
  - The user's text question is sent to the LM Studio embeddings endpoint to get a query vector.
  - If using /upload_and_query, a where filter ({"file_hash": "..."}) is applied to the search.
  - ChromaDB finds the TOP_K (e.g., 4) most relevant text chunks.
  - prompt.py constructs a detailed prompt, injecting the retrieved chunks as "Context."
  - llm_router.py sends this final prompt to the LM Studio chat endpoint (llama-3.1-8b).
  - The LLM generates an answer based only on the provided context, which is then sent back to the user.

🏁 Getting Started
1. Prerequisites
You must have these three things installed:
- Python 3.10+
- LM Studio: Download and install it from lmstudio.ai.
- Tesseract-OCR: This is required for reading images and scanned PDFs.

## Create requirements: 
fastapi
uvicorn[standard]
chromadb
openai
langchain-text-splitters
pytesseract
PyMuPDF
pdf2image
python-dotenv
requests

## To start the FastAPI Server

In your terminal (with the virtual environment activated), run the following command from the project's root directory:
`python -m uvicorn backend.app.qa_api:app --reload --reload-dir backend`
You should see a confirmation that Uvicorn is running on http://127.0.0.1:8000.

### Use the API

You're all set! Open your browser and go to the interactive API documentation:
`http://127.0.0.1:8000/docs`
From here, you can use the two main endpoints:
- /upload_and_query: Upload a file and ask a question about that specific file.
- /query: Ask a question against all documents you have ever uploaded.

Author 
DevAtomicRelease
