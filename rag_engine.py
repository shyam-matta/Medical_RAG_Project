"""
RAG Engine - Medical Information Assistant
Handles document loading, chunking, embedding, and retrieval.
"""

import os
import re
import math
from typing import List, Dict, Tuple


# ── Simple TF-IDF + cosine similarity retriever (zero heavy dependencies) ──

def load_documents(docs_dir: str) -> List[Dict]:
    """Load all .txt documents from the documents directory."""
    documents = []
    for filename in os.listdir(docs_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(docs_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
            # Extract source name from first line
            first_line = content.split("\n")[0]
            source = first_line.replace("DOCUMENT:", "").strip() if "DOCUMENT:" in first_line else filename
            documents.append({
                "filename": filename,
                "source": source,
                "content": content,
            })
    print(f"[RAG] Loaded {len(documents)} documents from '{docs_dir}'")
    return documents


def chunk_document(doc: Dict, chunk_size: int = 300, overlap: int = 50) -> List[Dict]:
    """Split a document into overlapping word-level chunks."""
    words = doc["content"].split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_text = " ".join(words[start:end])
        chunks.append({
            "chunk_id": f"{doc['filename']}::{len(chunks)}",
            "source": doc["source"],
            "filename": doc["filename"],
            "text": chunk_text,
        })
        if end == len(words):
            break
        start += chunk_size - overlap
    return chunks


def build_knowledge_base(docs_dir: str) -> List[Dict]:
    """Load documents and split them into chunks."""
    documents = load_documents(docs_dir)
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    print(f"[RAG] Knowledge base built: {len(all_chunks)} chunks from {len(documents)} documents")
    return all_chunks


# ── TF-IDF Vectorizer ──

def tokenize(text: str) -> List[str]:
    """Lowercase and tokenize text into words."""
    return re.findall(r'\b[a-z]{2,}\b', text.lower())


def build_tfidf_index(chunks: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Build a TF-IDF index over chunks.
    Returns (enriched_chunks_with_tf, idf_dict)
    """
    N = len(chunks)
    # Compute term frequency for each chunk
    for chunk in chunks:
        tokens = tokenize(chunk["text"])
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        # Normalize
        total = sum(tf.values()) or 1
        chunk["tf"] = {t: v / total for t, v in tf.items()}
        chunk["tokens_set"] = set(tf.keys())

    # Compute IDF
    df = {}
    for chunk in chunks:
        for term in chunk["tokens_set"]:
            df[term] = df.get(term, 0) + 1

    idf = {term: math.log((N + 1) / (count + 1)) + 1 for term, count in df.items()}
    return chunks, idf


def tfidf_vector(tf: Dict, idf: Dict) -> Dict:
    """Compute TF-IDF weighted vector from a TF dict and IDF dict."""
    return {term: tf_val * idf.get(term, 1.0) for term, tf_val in tf.items()}


def cosine_similarity(vec_a: Dict, vec_b: Dict) -> float:
    """Compute cosine similarity between two sparse TF-IDF vectors."""
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0.0
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def keyword_overlap_ratio(query_tokens: List[str], chunk_text: str) -> float:
    """
    Fraction of meaningful query tokens (len >= 4) that appear in the chunk.
    Acts as a second-pass guard to filter false positives from TF-IDF.
    """
    # Only consider words of length >= 4 as meaningful content words
    meaningful = [t for t in query_tokens if len(t) >= 4]
    if not meaningful:
        return 0.0
    chunk_lower = chunk_text.lower()
    matched = sum(1 for t in meaningful if t in chunk_lower)
    return matched / len(meaningful)


def retrieve(query: str, chunks: List[Dict], idf: Dict, top_k: int = 3,
             min_score: float = 0.15, min_overlap: float = 0.25) -> List[Dict]:
    """
    Retrieve the top_k most relevant chunks for a query.

    Two-stage filter:
      1. TF-IDF cosine similarity >= min_score
      2. Keyword overlap ratio  >= min_overlap

    Returns empty list if no chunk passes both filters (out-of-scope question).
    """
    query_tokens = tokenize(query)
    query_tf = {}
    for t in query_tokens:
        query_tf[t] = query_tf.get(t, 0) + 1
    total = sum(query_tf.values()) or 1
    query_tf = {t: v / total for t, v in query_tf.items()}
    query_vec = tfidf_vector(query_tf, idf)

    scores = []
    for chunk in chunks:
        chunk_vec = tfidf_vector(chunk["tf"], idf)
        score = cosine_similarity(query_vec, chunk_vec)
        overlap = keyword_overlap_ratio(query_tokens, chunk["text"])
        scores.append((score, overlap, chunk))

    # Sort by TF-IDF score descending
    scores.sort(key=lambda x: x[0], reverse=True)

    # Apply both filters
    top = [
        (score, chunk)
        for score, overlap, chunk in scores[:top_k]
        if score >= min_score and overlap >= min_overlap
    ]
    return top


# ── Answer Generation (template-based, grounded) ──

def generate_answer(query: str, retrieved: List[Tuple[float, Dict]]) -> Dict:
    """
    Generate a grounded answer from retrieved chunks.
    Returns dict with answer text and sources.
    """
    DISCLAIMER = (
        "\n\n⚠️  DISCLAIMER: This information is for general educational purposes only. "
        "It does not constitute medical advice, diagnosis, or treatment recommendations. "
        "Always consult a qualified healthcare provider for personal medical guidance."
    )

    if not retrieved:
        return {
            "answer": (
                "I'm sorry, I couldn't find relevant information in my knowledge base to answer your question.\n\n"
                "My knowledge base currently covers: Diabetes, Hypertension, Common Cold, "
                "Nutrition, Mental Health, and Exercise & Physical Health.\n\n"
                "Please try rephrasing your question, or ask about one of those topics."
                + DISCLAIMER
            ),
            "sources": [],
            "found": False,
        }

    # Build context from top chunks (deduplicate by source)
    seen_sources = []
    context_parts = []
    source_list = []

    for score, chunk in retrieved:
        if chunk["source"] not in seen_sources:
            seen_sources.append(chunk["source"])
        context_parts.append(chunk["text"])
        if chunk["source"] not in source_list:
            source_list.append(chunk["source"])

    context = "\n\n---\n\n".join(context_parts)

    # Template-based answer construction
    answer = (
        f"Based on the information in my medical knowledge base, here is what I found regarding your question:\n\n"
        f"{context}"
        f"{DISCLAIMER}"
    )

    return {
        "answer": answer,
        "sources": source_list,
        "found": True,
        "scores": [round(s, 4) for s, _ in retrieved],
    }
