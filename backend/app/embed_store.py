# backend/app/embed_store.py
import os
import uuid
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from typing import List, Dict, Any

from .config import CHROMA_DIR, LLM_BASE_URL, LLM_API_KEY, EMBED_MODEL

try:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
except Exception:
    from chromadb.config import Settings
    client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=CHROMA_DIR))


embed_function = OpenAIEmbeddingFunction(
    api_key=LLM_API_KEY,
    api_base=LLM_BASE_URL,
    model_name=EMBED_MODEL
)

def get_collection(name: str = "rag_docs"):
    try:
        return client.get_or_create_collection(
            name, 
            embedding_function=embed_function
        )
    except Exception as e:
        print(f"Error getting/creating collection (retrying): {e}")
        try:
            return client.get_collection(name, embedding_function=embed_function)
        except Exception:
            return client.create_collection(name, embedding_function=embed_function)


def file_exists(file_hash: str, collection_name: str = "rag_docs") -> bool:
    col = get_collection(collection_name)
    res = col.get(where={"file_hash": file_hash}, limit=1)
    return len(res.get("ids", [])) > 0


def add_documents_to_chroma(docs: List[Dict[str, Any]], collection_name: str = "rag_docs") -> int:
    # docs: [{"text": str, "metadata": dict, "id": str}, ..]
    if not docs:
        return 0

    col = get_collection(collection_name)

    texts = [d["text"] for d in docs]
    metadatas = [d["metadata"] for d in docs]
    ids = [d["id"] for d in docs]  
   
    col.add(documents=texts, metadatas=metadatas, ids=ids)
    try:
        client.persist()
    except Exception:
        pass
    return len(texts)