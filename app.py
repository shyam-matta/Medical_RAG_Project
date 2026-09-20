"""
Medical Information RAG Assistant - Flask Web App
"""
import os
from flask import Flask, render_template, request, jsonify
from rag_engine import build_knowledge_base, build_tfidf_index, retrieve, generate_answer

app = Flask(__name__)

# ── Build knowledge base once at startup ──
DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")
print("[RAG] Loading knowledge base...")
chunks = build_knowledge_base(DOCS_DIR)
chunks, idf = build_tfidf_index(chunks)
print(f"[RAG] Ready — {len(chunks)} chunks indexed.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    retrieved = retrieve(question, chunks, idf, top_k=3)
    result = generate_answer(question, retrieved)

    return jsonify({
        "found":   result["found"],
        "answer":  result["answer"],
        "sources": result["sources"],
        "scores":  result.get("scores", []),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
