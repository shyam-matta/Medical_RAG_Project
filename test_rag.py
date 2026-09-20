"""
Automated test script for the Medical RAG pipeline.
Runs without user input - safe to execute in CI or terminal.
"""
import os
from rag_engine import build_knowledge_base, build_tfidf_index, retrieve, generate_answer

DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")

def main():
    print("=" * 60)
    print("  Medical RAG Assistant - Full Pipeline Test")
    print("=" * 60)

    # ── Step 1: Build knowledge base ──
    chunks = build_knowledge_base(DOCS_DIR)
    chunks, idf = build_tfidf_index(chunks)
    print(f"\nChunks indexed: {len(chunks)}\n")

    # ── Step 2: In-scope & out-of-scope questions ──
    test_cases = [
        ("What are the symptoms of diabetes?",                True),
        ("What is normal blood pressure?",                    True),
        ("How do I treat a common cold at home?",             True),
        ("What are macronutrients?",                          True),
        ("How does exercise help mental health?",             True),
        ("What weekly exercise is recommended?",              True),
        ("Tell me about rocket science",                      False),  # out of scope
        ("Who won the football world cup?",                   False),  # out of scope
    ]

    print("--- RAG Retrieval Tests ---")
    all_passed = True
    for question, expect_found in test_cases:
        retrieved = retrieve(question, chunks, idf, top_k=3, min_score=0.05)
        result = generate_answer(question, retrieved)
        found = result["found"]
        status = "PASS" if found == expect_found else "FAIL"
        if status == "FAIL":
            all_passed = False
        srcs = ", ".join(result["sources"]) if result["sources"] else "none"
        print(f"  [{status}] {question[:50]:<50}  found={found}  sources=[{srcs}]")

    # ── Step 3: Source display ──
    print("\n--- Source & Score Display ---")
    q = "What are the symptoms of type 2 diabetes?"
    retrieved = retrieve(q, chunks, idf, top_k=3)
    result = generate_answer(q, retrieved)
    print(f"  Query  : {q}")
    print(f"  Sources: {result['sources']}")
    print(f"  Scores : {result['scores']}")
    print(f"  Snippet: {result['answer'][:180]}...")

    # ── Step 4: Hallucination guard ──
    print("\n--- Hallucination / Out-of-Scope Guard ---")
    oos = "What is the GDP of France in 2024?"
    r2 = generate_answer(oos, retrieve(oos, chunks, idf, top_k=3, min_score=0.05))
    print(f"  Query : {oos}")
    print(f"  Found : {r2['found']}  (expected False)")
    print(f"  Reply : {r2['answer'][:160]}...")

    # ── Step 5: Disclaimer present ──
    print("\n--- Disclaimer Check ---")
    q3 = "What foods should I eat for good health?"
    r3 = generate_answer(q3, retrieve(q3, chunks, idf, top_k=3, min_score=0.05))
    has_disclaimer = "DISCLAIMER" in r3["answer"]
    print(f"  Disclaimer present in answer: {has_disclaimer}  (expected True)")
    if not has_disclaimer:
        all_passed = False

    # ── Summary ──
    print("\n" + "=" * 60)
    if all_passed:
        print("  ALL TESTS PASSED - Project is working correctly! ✅")
    else:
        print("  SOME TESTS FAILED - Check output above ❌")
    print("=" * 60)


if __name__ == "__main__":
    main()
