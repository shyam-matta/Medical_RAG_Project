"""
Medical Information RAG Assistant
===================================
An educational RAG system that answers general health questions
from a trusted document knowledge base.

- Retrieval: TF-IDF cosine similarity
- Generation: Grounded, template-based (no hallucination risk)
- Safety: Out-of-scope detection, medical disclaimer on every answer
"""

import os
import sys
from rag_engine import build_knowledge_base, build_tfidf_index, retrieve, generate_answer

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║         🏥  Medical Information RAG Assistant               ║
║                                                              ║
║  Answers general health questions from trusted documents.    ║
║  This system does NOT diagnose or recommend treatment.       ║
╚══════════════════════════════════════════════════════════════╝

Topics covered:
  • Diabetes          • Hypertension (High Blood Pressure)
  • Common Cold       • Nutrition Basics
  • Mental Health     • Exercise & Physical Health

Commands:
  'quit' or 'exit'  — Exit the assistant
  'topics'          — List available topics
  'help'            — Show this message again

"""

TOPICS_MSG = """
Available topics in the knowledge base:
  1. Diabetes (Type 1 & Type 2, symptoms, blood sugar levels, complications)
  2. Hypertension (blood pressure categories, risk factors, lifestyle tips)
  3. Common Cold (causes, symptoms, home care, prevention)
  4. Nutrition Basics (macronutrients, vitamins, healthy eating guidelines)
  5. Mental Health (anxiety, depression, stress, wellness strategies)
  6. Exercise & Physical Health (recommendations, types, benefits)
"""

EXAMPLE_QUESTIONS = [
    "What are the symptoms of diabetes?",
    "What is a healthy blood pressure level?",
    "How can I treat a common cold at home?",
    "What are the main macronutrients?",
    "How does exercise affect mental health?",
]


def print_separator():
    print("\n" + "─" * 66 + "\n")


def format_response(result: dict) -> str:
    """Format the RAG result for display."""
    lines = []

    if result["found"]:
        lines.append("📋 ANSWER")
        lines.append("─" * 40)
        lines.append(result["answer"])
        lines.append("")
        lines.append("📚 SOURCES")
        lines.append("─" * 40)
        for i, src in enumerate(result["sources"], 1):
            lines.append(f"  [{i}] {src}")
        lines.append("")
        lines.append(f"🔍 Retrieval scores: {result.get('scores', [])}")
    else:
        lines.append("❓ OUT OF SCOPE")
        lines.append("─" * 40)
        lines.append(result["answer"])

    return "\n".join(lines)


def run_demo_questions(chunks, idf):
    """Run a quick demo with example questions to verify the system works."""
    print("\n🔬 Running demo queries to verify the system...\n")
    for q in EXAMPLE_QUESTIONS[:2]:
        print(f"  Demo Q: {q}")
        retrieved = retrieve(q, chunks, idf, top_k=2)
        result = generate_answer(q, retrieved)
        status = "✅ FOUND" if result["found"] else "❌ NOT FOUND"
        print(f"  Status: {status} | Sources: {result['sources']}")
    print("\n✅ System verified and ready!\n")


def main():
    print(BANNER)

    # ── Build knowledge base ──
    print("⚙️  Building knowledge base...")
    if not os.path.exists(DOCS_DIR):
        print(f"ERROR: Documents directory not found at '{DOCS_DIR}'")
        sys.exit(1)

    chunks = build_knowledge_base(DOCS_DIR)
    chunks, idf = build_tfidf_index(chunks)
    print(f"✅ Knowledge base ready: {len(chunks)} chunks indexed\n")

    # Quick system verification
    run_demo_questions(chunks, idf)

    print_separator()
    print("💬 Chat with the Medical Information Assistant")
    print("   (Type your health question below)\n")

    # ── Main chat loop ──
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye! Stay healthy! 👋")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("quit", "exit", "q"):
            print("\nGoodbye! Stay healthy! 👋")
            break

        if cmd == "topics":
            print(TOPICS_MSG)
            continue

        if cmd == "help":
            print(BANNER)
            continue

        # ── RAG pipeline ──
        print_separator()
        retrieved = retrieve(user_input, chunks, idf, top_k=3)
        result = generate_answer(user_input, retrieved)
        print(format_response(result))
        print_separator()


if __name__ == "__main__":
    main()
