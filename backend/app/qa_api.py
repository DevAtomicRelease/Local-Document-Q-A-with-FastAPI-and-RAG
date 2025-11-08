# backend/app/qa_api.py 
from pathlib import Path
import tempfile
import json # Import json for pretty printing

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import RedirectResponse, Response

from .embed_store import get_collection
from .config import TOP_K
from .prompt import construct_prompt
from .ingest import ingest_path
from .llm_router import llama_generate  

app = FastAPI()
collection = None

@app.on_event("startup")
def ensure_collection():
    global collection
    collection = get_collection("rag_docs")


async def _get_query_response(question: str, file_hash: str | None = None) -> dict:
    # Build a "where" filter if a hash is provided
    query_filter = {}
    if file_hash:
        query_filter = {"file_hash": file_hash}
        print(f"\n[DEBUG] Querying with FILTER: {query_filter}")
    else:
        print("\n[DEBUG] Querying ALL documents (no filter).")

    results = collection.query(
        query_texts=[question],
        n_results=TOP_K,
        where=query_filter,  # <-- THE CRITICAL FILTER
        include=["documents", "metadatas"],
    )
    
    print("="*50)
    print("[DEBUG] RETRIEVED RESULTS FROM CHROMA:")
    print(json.dumps(results, indent=2))
    print("="*50)
    
    docs = [
        {"text": t, "metadata": m}
        for t, m in zip(results["documents"][0], results["metadatas"][0])
    ]
    
    prompt = construct_prompt(question, docs)
    
    # --- START NEW DEBUGGING ---
    print("[DEBUG] PROMPT BEING SENT TO LLM:")
    print(prompt)
    print("="*50)
    # --- END NEW DEBUGGING ---

    answer = llama_generate(prompt)
    return {"answer": answer, "sources": [d["metadata"] for d in docs]}


@app.post("/upload_and_query")
async def upload_and_query(file: UploadFile = File(...), question: str = Form(...)):
    tmp = Path(tempfile.gettempdir()) / file.filename
    file_hash = "" # Initialize
    try:
        with open(tmp, "wb") as f:
            f.write(await file.read())

        # 1. Get the file_hash from the ingest function
        skipped, added, file_hash_result = ingest_path(str(tmp))
        file_hash = file_hash_result
        
        if skipped:
            print(f"[ingest] SKIP (already present): {file.filename} ({file_hash})")
        else:
            print(f"[ingest] ADDED {added} chunks from {file.filename}")
    
    finally:
        # Add cleanup to remove the temp file
        if tmp.exists():
            tmp.unlink()


    return await _get_query_response(question, file_hash=file_hash)


@app.post("/query")
async def query(q: str = Form(...)):
    return await _get_query_response(q, file_hash=None)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)