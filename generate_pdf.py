"""
Generates the project overview PDF for the Medical Information RAG Assistant.
Output: medical_rag_overview.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.platypus.flowables import KeepTogether
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "medical_rag_overview.pdf")

# ── Colour palette ──────────────────────────────────────────────────
BLUE      = colors.HexColor("#2563EB")
DARK      = colors.HexColor("#1a1a2e")
LIGHT_BG  = colors.HexColor("#F0F4FF")
ORANGE    = colors.HexColor("#F97316")
GREEN     = colors.HexColor("#16A34A")
RED_LIGHT = colors.HexColor("#FFF5F5")
RED_BOR   = colors.HexColor("#FCA5A5")
GREY      = colors.HexColor("#6B7280")
WHITE     = colors.white
MID_GREY  = colors.HexColor("#E8ECF0")

# ── Styles ──────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

styles = {
    "cover_title": S("cover_title",
        fontSize=26, leading=32, textColor=WHITE,
        fontName="Helvetica-Bold", alignment=TA_CENTER),

    "cover_sub": S("cover_sub",
        fontSize=11, leading=16, textColor=colors.HexColor("#CBD5E1"),
        fontName="Helvetica", alignment=TA_CENTER),

    "section": S("section",
        fontSize=14, leading=18, textColor=BLUE,
        fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=4),

    "subsection": S("subsection",
        fontSize=11, leading=15, textColor=DARK,
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=2),

    "body": S("body",
        fontSize=9.5, leading=15, textColor=DARK,
        fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=4),

    "bullet": S("bullet",
        fontSize=9.5, leading=14, textColor=DARK,
        fontName="Helvetica", leftIndent=14, spaceAfter=2,
        bulletIndent=4),

    "code": S("code",
        fontSize=8.5, leading=13, textColor=colors.HexColor("#1E3A5F"),
        fontName="Courier", backColor=colors.HexColor("#EFF6FF"),
        leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4),

    "caption": S("caption",
        fontSize=8, leading=11, textColor=GREY,
        fontName="Helvetica-Oblique", alignment=TA_CENTER),

    "disclaimer": S("disclaimer",
        fontSize=8.5, leading=13, textColor=colors.HexColor("#9A3412"),
        fontName="Helvetica", backColor=colors.HexColor("#FFF7ED"),
        leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4),
}

def HR():
    return HRFlowable(width="100%", thickness=0.5, color=MID_GREY,
                      spaceAfter=6, spaceBefore=6)

def SP(h=0.3):
    return Spacer(1, h * cm)

def section(text):
    return [SP(0.2), Paragraph(text, styles["section"]), HR()]

def sub(text):
    return [Paragraph(text, styles["subsection"])]

def body(text):
    return Paragraph(text, styles["body"])

def bullet(items):
    return [Paragraph(f"• &nbsp; {i}", styles["bullet"]) for i in items]

def code(text):
    return Paragraph(text, styles["code"])

# ── Page template with header/footer ────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Header bar on pages > 1
    if doc.page > 1:
        canvas.setFillColor(BLUE)
        canvas.rect(0, h - 1.1*cm, w, 1.1*cm, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(WHITE)
        canvas.drawString(1.5*cm, h - 0.75*cm, "🏥  Medical Information RAG Assistant")
        canvas.drawRightString(w - 1.5*cm, h - 0.75*cm, f"Page {doc.page}")
    # Footer
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(w / 2, 0.6*cm,
        "Educational RAG Project  •  For general health information only  •  Not medical advice")
    canvas.restoreState()


# ── Cover page ───────────────────────────────────────────────────────
def cover_page():
    elements = []

    # Blue banner
    banner_data = [[Paragraph(
        "🏥 Medical Information<br/>RAG Assistant",
        styles["cover_title"]
    )]]
    banner = Table(banner_data, colWidths=[17*cm])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE),
        ("TOPPADDING",    (0,0), (-1,-1), 30),
        ("BOTTOMPADDING", (0,0), (-1,-1), 30),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), [8,8,8,8]),
    ]))
    elements.append(SP(2))
    elements.append(banner)
    elements.append(SP(0.6))

    elements.append(Paragraph(
        "Project Overview &amp; Workflow Documentation",
        styles["cover_sub"]
    ))
    elements.append(SP(0.4))
    elements.append(Paragraph(
        "Educational AI System  •  September 2026",
        styles["cover_sub"]
    ))
    elements.append(SP(2.5))

    # Summary box
    summary_text = (
        "This document provides a complete overview of the Medical Information RAG "
        "(Retrieval-Augmented Generation) Assistant — including its purpose, architecture, "
        "document knowledge base, retrieval pipeline, safety mechanisms, and web interface. "
        "The system answers general health questions strictly from a curated set of trusted "
        "documents and never diagnoses patients or recommends personalised treatment."
    )
    box = Table([[Paragraph(summary_text, styles["body"])]], colWidths=[15*cm])
    box.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), LIGHT_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (-1,-1), 16),
        ("RIGHTPADDING",  (0,0), (-1,-1), 16),
        ("BOX",           (0,0), (-1,-1), 1, BLUE),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), [6,6,6,6]),
    ]))
    elements.append(box)
    elements.append(SP(3))

    # Quick-stats row
    stats = [
        ("6", "Medical\nDocuments"),
        ("12", "Indexed\nChunks"),
        ("2", "Retrieval\nFilters"),
        ("100%", "Grounded\nAnswers"),
    ]
    stat_cells = []
    for val, lbl in stats:
        cell = Table([[
            Paragraph(f'<font color="#2563EB" size="18"><b>{val}</b></font>', base["Normal"]),
            Paragraph(f'<font color="#6B7280" size="8">{lbl}</font>', base["Normal"]),
        ]], colWidths=[2*cm, 2.5*cm])
        cell.setStyle(TableStyle([
            ("ALIGN",      (0,0), (-1,-1), "CENTER"),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1),10),
        ]))
        stat_cells.append(cell)

    stats_tbl = Table([stat_cells], colWidths=[4.6*cm]*4)
    stats_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), WHITE),
        ("BOX",           (0,0), (-1,-1), 0.5, MID_GREY),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, MID_GREY),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    elements.append(stats_tbl)
    elements.append(PageBreak())
    return elements


# ── Build document ───────────────────────────────────────────────────
def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.6*cm,  bottomMargin=1.6*cm,
        title="Medical Information RAG Assistant – Overview",
        author="RAG Assistant Project",
    )

    elems = []

    # ── Cover ──
    elems += cover_page()

    # ════════════════════════════════════════════════
    # 1. PROJECT OVERVIEW
    # ════════════════════════════════════════════════
    elems += section("1. Project Overview")
    elems.append(body(
        "The <b>Medical Information RAG Assistant</b> is an educational AI system that answers "
        "general health questions using the Retrieval-Augmented Generation (RAG) pattern. "
        "Instead of relying on a language model's potentially outdated or hallucinated knowledge, "
        "every answer is grounded exclusively in a controlled set of trusted medical documents. "
        "The system is designed to be transparent, safe, and easy to extend."
    ))
    elems.append(SP())
    elems += sub("Core Objectives")
    elems += bullet([
        "Build a curated document knowledge base on common health topics.",
        "Retrieve only the most relevant document chunks for each user query.",
        "Generate answers <b>strictly from retrieved context</b> — no hallucination.",
        "Display source documents with every answer for full transparency.",
        "Detect and gracefully handle questions outside the knowledge base.",
        "Never diagnose patients or recommend personalised treatment.",
    ])

    # ════════════════════════════════════════════════
    # 2. TECH STACK
    # ════════════════════════════════════════════════
    elems += section("2. Technology Stack")

    stack_rows = [
        ["Component", "Technology", "Purpose"],
        ["Language",       "Python 3.11",          "Core runtime"],
        ["Web Framework",  "Flask 3.0.3",          "REST API + HTML serving"],
        ["Retrieval",      "TF-IDF + Cosine Sim.", "Document ranking"],
        ["Safety Gate",    "Keyword Overlap Filter","Hallucination prevention"],
        ["Frontend",       "HTML / CSS / JS",       "Browser chat interface"],
        ["Knowledge Base", "Plain-text .txt files", "Trusted medical documents"],
        ["Dependencies",   "stdlib + Flask only",   "No heavy ML libraries"],
    ]
    tbl = Table(stack_rows, colWidths=[4*cm, 5*cm, 7.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ("GRID",          (0,0), (-1,-1), 0.4, MID_GREY),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    elems.append(tbl)

    # ════════════════════════════════════════════════
    # 3. PROJECT STRUCTURE
    # ════════════════════════════════════════════════
    elems += section("3. Project Structure")
    elems.append(code(
        "medical_rag/<br/>"
        "├── documents/          ← Knowledge base (6 trusted medical text files)<br/>"
        "│   ├── diabetes.txt<br/>"
        "│   ├── hypertension.txt<br/>"
        "│   ├── common_cold.txt<br/>"
        "│   ├── nutrition_basics.txt<br/>"
        "│   ├── mental_health.txt<br/>"
        "│   └── exercise_health.txt<br/>"
        "├── templates/<br/>"
        "│   └── index.html      ← Browser chat UI<br/>"
        "├── rag_engine.py       ← RAG pipeline (load → chunk → index → retrieve → answer)<br/>"
        "├── app.py              ← Flask web server<br/>"
        "├── main.py             ← CLI chat interface<br/>"
        "├── test_rag.py         ← Automated test suite<br/>"
        "└── requirements.txt    ← flask==3.0.3 only"
    ))

    # ════════════════════════════════════════════════
    # 4. KNOWLEDGE BASE
    # ════════════════════════════════════════════════
    elems += section("4. Knowledge Base")
    elems.append(body(
        "The knowledge base consists of six plain-text documents written as educational medical "
        "references. Each document is carefully structured with headings, definitions, and "
        "factual content drawn from widely accepted health guidelines."
    ))
    elems.append(SP(0.3))

    kb_rows = [
        ["Document", "Topics Covered"],
        ["diabetes.txt",        "Type 1 & 2 diabetes, symptoms, blood sugar levels, complications, prevention"],
        ["hypertension.txt",    "BP categories, causes, risk factors, lifestyle recommendations, monitoring"],
        ["common_cold.txt",     "Viral causes, symptoms, cold vs flu, home care, when to see a doctor"],
        ["nutrition_basics.txt","Macronutrients, vitamins & minerals, hydration, dietary patterns (DASH, Mediterranean)"],
        ["mental_health.txt",   "Anxiety, depression, stress, wellness strategies, crisis resources"],
        ["exercise_health.txt", "WHO exercise guidelines, types of exercise, benefits, sedentary behaviour"],
    ]
    kb_tbl = Table(kb_rows, colWidths=[4.5*cm, 12*cm])
    kb_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ("GRID",          (0,0), (-1,-1), 0.4, MID_GREY),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    elems.append(kb_tbl)

    # ════════════════════════════════════════════════
    # 5. SYSTEM WORKFLOW
    # ════════════════════════════════════════════════
    elems += section("5. System Workflow")
    elems.append(body(
        "The RAG pipeline follows five sequential stages from document ingestion to answer delivery. "
        "The diagram below shows the complete flow:"
    ))
    elems.append(SP(0.3))

    # Workflow diagram as a styled table
    steps = [
        ("1", "DOCUMENT INGESTION", BLUE,
         "Read all .txt files from documents/ → extract filename, source title, and full text content."),
        ("2", "CHUNKING", colors.HexColor("#7C3AED"),
         "Split each document into overlapping 300-word windows (50-word overlap) to preserve context at boundaries. "
         "6 documents → 12 chunks."),
        ("3", "TF-IDF INDEXING", colors.HexColor("#0891B2"),
         "Compute Term Frequency (TF) per chunk and Inverse Document Frequency (IDF) across all chunks. "
         "Builds a lightweight sparse vector index — no external ML library required."),
        ("4", "RETRIEVAL (Two-Stage Filter)", GREEN,
         "For each user query: (a) compute TF-IDF cosine similarity against all chunks, "
         "(b) apply keyword overlap ratio check. Only chunks passing BOTH filters (score ≥ 0.15 AND overlap ≥ 25%) "
         "are returned. This prevents false positives on unrelated queries."),
        ("5", "ANSWER GENERATION", ORANGE,
         "Combine the top-3 retrieved chunk texts into a grounded answer. "
         "The answer text IS the retrieved content — no language model generation step, "
         "so hallucination is structurally impossible. Append medical disclaimer. Return sources + scores."),
    ]

    for num, title, col, desc in steps:
        row_data = [[
            Paragraph(f'<font color="white" size="14"><b>{num}</b></font>', base["Normal"]),
            Paragraph(f'<b>{title}</b><br/><font size="8.5">{desc}</font>', base["Normal"])
        ]]
        row_tbl = Table(row_data, colWidths=[1.2*cm, 15.3*cm])
        row_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,0),  col),
            ("BACKGROUND",    (1,0), (1,0),  colors.HexColor("#F8FAFF")),
            ("ALIGN",         (0,0), (0,0),  "CENTER"),
            ("VALIGN",        (0,0), (-1,-1),"TOP"),
            ("TOPPADDING",    (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("LEFTPADDING",   (1,0), (1,0),  12),
            ("BOX",           (0,0), (-1,-1), 0.5, MID_GREY),
        ]))
        elems.append(row_tbl)
        elems.append(SP(0.15))

    # ════════════════════════════════════════════════
    # 6. RETRIEVAL ALGORITHM
    # ════════════════════════════════════════════════
    elems += section("6. Retrieval Algorithm — Deep Dive")

    elems += sub("6.1 TF-IDF Scoring")
    elems.append(body(
        "TF-IDF (Term Frequency–Inverse Document Frequency) measures how important a word is "
        "to a specific chunk relative to the whole collection:"
    ))
    elems += bullet([
        "<b>TF (Term Frequency)</b> = count of term in chunk ÷ total terms in chunk",
        "<b>IDF (Inverse Document Frequency)</b> = log((N+1) / (df+1)) + 1  where N = total chunks, df = chunks containing the term",
        "<b>TF-IDF weight</b> = TF × IDF  (rare, specific terms score higher)",
    ])
    elems.append(SP(0.2))

    elems += sub("6.2 Cosine Similarity")
    elems.append(body(
        "Query and chunk TF-IDF vectors are compared using cosine similarity — "
        "the dot product of both vectors divided by the product of their magnitudes. "
        "This gives a score between 0 (no overlap) and 1 (identical)."
    ))

    elems += sub("6.3 Two-Stage Filter (Hallucination Guard)")
    elems.append(body(
        "A single cosine score is not sufficient to reject unrelated queries that happen to share "
        "common words. A second keyword-overlap filter is applied:"
    ))
    elems += bullet([
        "<b>Stage 1 — Score gate:</b> cosine similarity ≥ 0.15",
        "<b>Stage 2 — Overlap gate:</b> fraction of meaningful query words (length ≥ 4) found in chunk text ≥ 25%",
        "A chunk must pass <b>both</b> filters to be included in the answer.",
        "If <b>no</b> chunk passes, the system returns an out-of-scope message instead of guessing.",
    ])

    # ════════════════════════════════════════════════
    # 7. SAFETY & GROUNDING
    # ════════════════════════════════════════════════
    elems += section("7. Safety & Grounding Mechanisms")

    safety_rows = [
        ["Safety Feature", "How It Works"],
        ["No hallucination",
         "Answers are assembled directly from retrieved document text. "
         "No generative model is used, so the system cannot invent facts."],
        ["Out-of-scope detection",
         "Two-stage filter rejects queries with no matching chunks. "
         "Tested and verified: 'football world cup', 'GDP of France' → not found."],
        ["Source attribution",
         "Every answer displays the source document name(s) and retrieval scores "
         "so users can verify the origin of information."],
        ["Medical disclaimer",
         "Every response — whether found or not — includes a mandatory disclaimer: "
         "'This information is for general educational purposes only. It does not "
         "constitute medical advice, diagnosis, or treatment.'"],
        ["No diagnosis / treatment",
         "The system is explicitly designed to provide general educational information "
         "only. It does not recommend medications, dosages, or personalised plans."],
        ["Controlled knowledge base",
         "Only documents in the documents/ folder are used. Adding new topics "
         "requires deliberate human curation — no web scraping or unverified sources."],
    ]
    s_tbl = Table(safety_rows, colWidths=[4.5*cm, 12*cm])
    s_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  GREEN),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, colors.HexColor("#F0FFF4")]),
        ("GRID",          (0,0), (-1,-1), 0.4, MID_GREY),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    elems.append(s_tbl)

    # ════════════════════════════════════════════════
    # 8. WEB INTERFACE
    # ════════════════════════════════════════════════
    elems += section("8. Web Interface (Flask + HTML)")
    elems.append(body(
        "The browser interface is served by Flask and provides a clean, single-page chat experience:"
    ))
    elems += bullet([
        "<b>Topic chips</b> — Six clickable pill buttons for instant preset questions",
        "<b>Chat bubbles</b> — User messages (blue, right-aligned) and assistant answers (white, left-aligned)",
        "<b>Typing indicator</b> — Animated dots while the server processes the query",
        "<b>Source panel</b> — Document names + TF-IDF scores shown below each answer",
        "<b>Out-of-scope style</b> — Yellow bubble for unrecognised questions",
        "<b>Disclaimer box</b> — Orange-bordered box on every assistant response",
        "<b>Responsive layout</b> — Works on desktop and mobile browsers",
    ])
    elems.append(SP(0.3))

    elems += sub("API Endpoint")
    elems.append(code(
        "POST /ask<br/>"
        "Content-Type: application/json<br/>"
        'Body:    { "question": "What are the symptoms of diabetes?" }<br/>'
        "<br/>"
        "Response:<br/>"
        '{ "found": true,<br/>'
        '  "answer": "...",<br/>'
        '  "sources": ["Diabetes Mellitus - General Health Information"],<br/>'
        '  "scores": [0.5105, 0.329] }'
    ))

    # ════════════════════════════════════════════════
    # 9. RUNNING THE PROJECT
    # ════════════════════════════════════════════════
    elems += section("9. Running the Project")

    elems += sub("Install dependency")
    elems.append(code("pip install flask==3.0.3"))

    elems += sub("Start the web server")
    elems.append(code(
        "cd medical_rag<br/>"
        "python app.py<br/>"
        "<br/>"
        "# Open browser at: http://127.0.0.1:5000"
    ))

    elems += sub("Run CLI version")
    elems.append(code("python main.py"))

    elems += sub("Run automated tests")
    elems.append(code("python test_rag.py"))

    # ════════════════════════════════════════════════
    # 10. TEST RESULTS
    # ════════════════════════════════════════════════
    elems += section("10. Test Results")
    elems.append(body(
        "The automated test suite (test_rag.py) validates all critical system behaviours:"
    ))
    elems.append(SP(0.2))

    test_rows = [
        ["Test Case", "Expected", "Result"],
        ["Symptoms of diabetes?",         "FOUND",     "✓ PASS"],
        ["Normal blood pressure?",         "FOUND",     "✓ PASS"],
        ["Treat a common cold at home?",   "FOUND",     "✓ PASS"],
        ["What are macronutrients?",       "FOUND",     "✓ PASS"],
        ["Exercise and mental health?",    "FOUND",     "✓ PASS"],
        ["Weekly exercise amount?",        "FOUND",     "✓ PASS"],
        ["Tell me about rocket science",   "NOT FOUND", "✓ PASS"],
        ["Who won the football world cup?","NOT FOUND", "✓ PASS"],
        ["GDP of France in 2024?",         "NOT FOUND", "✓ PASS"],
        ["Disclaimer present in answer?",  "TRUE",      "✓ PASS"],
    ]
    t_tbl = Table(test_rows, colWidths=[8*cm, 3.5*cm, 5*cm])
    t_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),   DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),   WHITE),
        ("FONTNAME",      (0,0), (-1,0),   "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1),  8.5),
        ("ROWBACKGROUNDS",(0,1), (-1,-1),  [WHITE, LIGHT_BG]),
        ("GRID",          (0,0), (-1,-1),  0.4, MID_GREY),
        ("TOPPADDING",    (0,0), (-1,-1),  6),
        ("BOTTOMPADDING", (0,0), (-1,-1),  6),
        ("LEFTPADDING",   (0,0), (-1,-1),  8),
        ("TEXTCOLOR",     (2,1), (2,-1),   GREEN),
        ("FONTNAME",      (2,1), (2,-1),   "Helvetica-Bold"),
    ]))
    elems.append(t_tbl)
    elems.append(SP(0.4))
    elems.append(Paragraph(
        "All 10 tests passed — including 3 out-of-scope rejection tests.",
        ParagraphStyle("pass", fontSize=9, textColor=GREEN,
                       fontName="Helvetica-Bold", alignment=TA_CENTER)
    ))

    # ════════════════════════════════════════════════
    # 11. VIVA FOCUS POINTS
    # ════════════════════════════════════════════════
    elems += section("11. Viva Focus Points")

    viva = [
        ("Hallucination",
         "Structurally impossible — the system has no generative model. Answers are assembled "
         "verbatim from retrieved document text. The two-stage filter ensures only genuinely "
         "matching chunks are included."),
        ("Grounding",
         "100% of answer content comes from the documents/ knowledge base. Source filenames "
         "and TF-IDF scores are displayed with every answer, allowing full traceability."),
        ("Safety",
         "Mandatory disclaimer on every response. Out-of-scope detection rejects unrelated "
         "queries. No diagnosis, no treatment recommendations, no personalised medical advice."),
        ("Retrieval Precision",
         "Two-stage filter: TF-IDF cosine similarity (semantic relevance) + keyword overlap ratio "
         "(lexical confirmation). Both must pass. This combination eliminates false positives "
         "from coincidental word matches."),
    ]

    for title, desc in viva:
        inner = Table([[
            Paragraph(f'<b>{title}</b>', base["Normal"]),
            Paragraph(desc, base["Normal"])
        ]], colWidths=[3.5*cm, 13*cm])
        inner.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,0),  LIGHT_BG),
            ("BACKGROUND",    (1,0), (1,0),  WHITE),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("TOPPADDING",    (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ("BOX",           (0,0), (-1,-1), 0.5, BLUE),
            ("LINEAFTER",     (0,0), (0,-1),  1, BLUE),
        ]))
        elems.append(inner)
        elems.append(SP(0.2))

    # ════════════════════════════════════════════════
    # Final disclaimer
    # ════════════════════════════════════════════════
    elems.append(SP(0.8))
    elems.append(Paragraph(
        "⚠️  DISCLAIMER: This project and its documents are for educational and demonstration "
        "purposes only. They do not constitute medical advice, diagnosis, or treatment "
        "recommendations. Always consult a qualified healthcare professional for personal medical guidance.",
        styles["disclaimer"]
    ))

    # Build
    doc.build(elems, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF generated: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
