# backend/app/prompt.py
def construct_prompt(question: str, contexts: list):
    """
    contexts: list of dicts {"text": "...", "metadata": {"source": "...", "page": X, ...}}
    """
    context_text = ""
    if not contexts:
        # Tell the LLM what to say if context is empty
        context_text = "No context was provided. Please inform the user."
    
    for i, c in enumerate(contexts):
        metadata = c.get('metadata', {})
        source = metadata.get('source', 'N/A')
        page = metadata.get('page', 'N/A')
        
        # Add the metadata *into* the context for the LLM to see
        context_text += f"--- START CONTEXT {i+1} (Source: {source}, Page: {page}) ---\n"
        context_text += c["text"]
        context_text += f"\n--- END CONTEXT {i+1} ---\n\n"
    
    prompt = f"""You are an expert Q&A engine. Your task is to answer the user's question based *only* on the text from the context blocks provided below. The user has provided these documents.

Do not use any outside knowledge.
If the context does not contain the answer, state clearly that the answer is not in the provided documents.

**Contexts:**
{context_text}

**Question:**
{question}

**Answer:**
(Cite the source and page number, like [Source: filename.pdf, Page: 12], for *all* information you use.)
"""
    return prompt