#!/usr/bin/env python3
"""
scripts/generate_architecture_diagram.py
Generates a publication-grade, professional system architecture diagram
for the Trust-Aware Internship Search System.
Saved to reports/figures/fig1_architecture.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "reports" / "figures" / "fig1_architecture.png"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def draw_architecture():
    fig = plt.figure(figsize=(16, 10), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Color palette - Academic & Professional
    c_bg = "#F8F9FA"
    c_user = "#E3F2FD"      # Soft blue
    c_user_border = "#1976D2"
    c_data = "#E8F5E9"      # Soft green
    c_data_border = "#388E3C"
    c_retrieval = "#EDE7F6" # Soft purple
    c_retrieval_border = "#512DA8"
    c_risk = "#FFEBEE"      # Soft red
    c_risk_border = "#D32F2F"
    c_rag = "#FFF8E1"       # Soft amber
    c_rag_border = "#F57C00"
    c_ui = "#ECEFF1"        # Soft slate
    c_ui_border = "#455A64"

    fig.patch.set_facecolor("#FFFFFF")

    # Title
    ax.text(8.0, 9.6, "Trust-Aware Internship Search System: End-to-End Architecture",
            fontsize=18, fontweight="bold", ha="center", va="center", color="#1A237E", family="sans-serif")
    ax.text(8.0, 9.25, "Multi-Stage Hybrid Retrieval (BM25 + FAISS RRF), Trust Scoring & Grounded RAG with Deterministic Guardrails",
            fontsize=11, fontstyle="italic", ha="center", va="center", color="#424242", family="sans-serif")

    # Helper function for rounded boxes
    def draw_box(x, y, w, h, bg_color, border_color, title, subtitle="", items=None, title_color="#000000"):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12,rounding_size=0.15",
                                     facecolor=bg_color, edgecolor=border_color, linewidth=1.5, zorder=2)
        ax.add_patch(box)
        
        # Header line
        title_y = y + h - 0.28
        ax.text(x + w / 2, title_y, title, fontsize=10.5, fontweight="bold", ha="center", va="center", color=title_color, zorder=3)
        if subtitle:
            ax.text(x + w / 2, title_y - 0.24, subtitle, fontsize=8.5, fontstyle="italic", ha="center", va="center", color="#555555", zorder=3)
        
        if items:
            item_y = title_y - (0.48 if subtitle else 0.32)
            for it in items:
                ax.text(x + 0.15, item_y, f"• {it}", fontsize=8.2, ha="left", va="center", color="#212121", zorder=3)
                item_y -= 0.26

    # Helper function for connecting arrows
    def draw_arrow(x1, y1, x2, y2, label="", color="#37474F", ls="-", lw=1.5, rad=0.0):
        connectionstyle = f"arc3,rad={rad}" if rad != 0 else "arc3"
        arrow = patches.FancyArrowPatch((x1, y1), (x2, y2),
                                        arrowstyle="-|>,head_length=5,head_width=3.5",
                                        connectionstyle=connectionstyle,
                                        color=color, linewidth=lw, linestyle=ls, zorder=4)
        ax.add_patch(arrow)
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(mx, my + 0.12, label, fontsize=7.5, fontweight="bold", ha="center", va="bottom",
                    color=color, bbox=dict(boxstyle="square,pad=0.1", fc="#FFFFFF", ec="none", alpha=0.85), zorder=5)

    # -------------------------------------------------------------
    # SECTION 1: USER INPUT & QUERY DISPATCH (Top Left: x=0.6, y=6.4)
    # -------------------------------------------------------------
    draw_box(0.6, 6.2, 3.4, 2.5, c_user, c_user_border,
             "1. User Query & Constraints", "Streamlit Client Input",
             [
                 "Search Query (e.g., 'ML intern')",
                 "Candidate Skills ('python, sql')",
                 "Method Selector (BM25 / Hybrid)",
                 "Toggles: Risk Flags & RAG Explanations",
                 "Candidate Depth Slider (k = 5..20)"
             ],
             title_color=c_user_border)

    # -------------------------------------------------------------
    # SECTION 2: DATA PREPARATION & CORPUS (Bottom Left: x=0.6, y=1.0)
    # -------------------------------------------------------------
    draw_box(0.6, 1.0, 3.4, 4.4, c_data, c_data_border,
             "2. Corpus Preprocessing & Indexing", "Offline Ingestion Pipeline",
             [
                 "EMSCAD Corpus (15,560 Job Ads)",
                 "Cleaning: HTML Strip, Lowercase, Regex",
                 "Tokenization: Whitespace & Alphanum",
                 "Sliding-Window Chunking:",
                 "  130-word chunks, 20-word overlap",
                 "  Yields 42,480 passage chunks",
                 "Dense Embeddings Generation:",
                 "  all-MiniLM-L6-v2 (384-dim)",
                 "  L2-Normalized: ||v|| = 1.0",
                 "FAISS IndexFlatIP (23.9 MB)",
                 "Okapi BM25 Inverted Index"
             ],
             title_color=c_data_border)

    # -------------------------------------------------------------
    # SECTION 3: DUAL-PATH HYBRID RETRIEVAL (Middle Column: x=4.8)
    # -------------------------------------------------------------
    # Sparse BM25 Box
    draw_box(4.8, 6.5, 3.6, 2.2, c_retrieval, c_retrieval_border,
             "3A. Sparse Lexical Search", "Okapi BM25 Inverted Index",
             [
                 "Exact lexical keyword matching",
                 "Term Frequency & Inverse Doc Freq",
                 "Evaluated variants: plain, norm, stem",
                 "Retrieves top-N candidate doc IDs",
                 "Dominant baseline: P@5 = 1.000"
             ],
             title_color=c_retrieval_border)

    # Dense Semantic Box
    draw_box(4.8, 3.6, 3.6, 2.4, c_retrieval, c_retrieval_border,
             "3B. Dense Semantic Search", "FAISS Inner Product (Cosine)",
             [
                 "Query encoding via all-MiniLM-L6",
                 "Cosine inner product: cos(q, d) = q·d",
                 "FAISS IndexFlatIP exact vector search",
                 "Chunk-to-doc max pooling:",
                 "  Score(D) = max Cosine(Q, c)",
                 "Retrieves top-N candidate doc IDs"
             ],
             title_color=c_retrieval_border)

    # Reciprocal Rank Fusion Box
    draw_box(4.8, 1.0, 3.6, 2.0, c_retrieval, c_retrieval_border,
             "3C. Reciprocal Rank Fusion (RRF)", "Rank-Based Fusion (k = 60)",
             [
                 "Score-invariant rank aggregation:",
                 "  RRF(d) = 1/(k+r_bm25) + 1/(k+r_sem)",
                 "Ablation validated: k=60 balances lists",
                 "Merges sparse precision & dense recall",
                 "Outputs consolidated Top-K documents"
             ],
             title_color=c_retrieval_border)

    # -------------------------------------------------------------
    # SECTION 4: TRUST & RISK ASSESSMENT ENGINE (Top Right: x=9.3, y=5.5)
    # -------------------------------------------------------------
    draw_box(9.3, 5.2, 3.4, 3.5, c_risk, c_risk_border,
             "4. Trust & Risk Assessment Engine", "Dual Heuristic + ML Classifier",
             [
                 "Rule 1: Money / upfront fee requests",
                 "Rule 2: Suspicious / personal email domain",
                 "Rule 3: Vague / empty company profile",
                 "Rule 4: High pay without experience",
                 "SGD Logistic Regression Classifier:",
                 "  Trained on TF-IDF word & char n-grams",
                 "  PR-AUC = 0.76 (Test set evaluation)",
                 "Ensemble Risk Level: Low / Med / High",
                 "N-gram evidence highlight in UI",
                 "Ethical Stance: Caution signals, not fraud"
             ],
             title_color=c_risk_border)

    # -------------------------------------------------------------
    # SECTION 5: GROUNDED RAG EXPLANATIONS (Bottom Right: x=9.3, y=1.0)
    # -------------------------------------------------------------
    draw_box(9.3, 1.0, 3.4, 3.7, c_rag, c_rag_border,
             "5. Grounded RAG & Guardrails", "Gemini 3.5 Flash + Deterministic Checks",
             [
                 "Passage Extraction: Top-k 130w chunks",
                 "Cosine Abstain Filter (Threshold < 0.30):",
                 "  Blocks out-of-domain hallucinations",
                 "5 Deterministic Guardrails:",
                 "  1. Strict JSON format enforcement",
                 "  2. Citation existence check [doc_id#c]",
                 "  3. Word-for-word quote verification",
                 "  4. Regex skill gap overwrite (114 hits)",
                 "  5. Defamation neutralizer ('fraud' filter)",
                 "SHA-256 persistent disk cache (0 duplicate API)"
             ],
             title_color=c_rag_border)

    # -------------------------------------------------------------
    # SECTION 6: INTERACTIVE DASHBOARD (Far Right: x=13.2, y=1.0)
    # -------------------------------------------------------------
    draw_box(13.2, 1.0, 2.3, 7.7, c_ui, c_ui_border,
             "6. User Interface", "Streamlit Presentation",
             [
                 "Ranked Job Cards",
                 "Skill Gap Engine:",
                 " • Matched Skills (Green)",
                 " • Missing Skills (Amber)",
                 "Full Posting Expander",
                 "--------------------",
                 "Trust Layer Display:",
                 " • Risk Level Banner",
                 " • Heuristic Trigger List",
                 " • Top Risk Keywords",
                 " • Disclaimer Notice",
                 "--------------------",
                 "RAG Explanation Card:",
                 " • Match Justification",
                 " • Chunk Citations",
                 " • Anti-hallucination",
                 "   abstain notice",
                 "--------------------",
                 "Dual-Column Mode:",
                 " • BM25 vs Hybrid Side-by-Side"
             ],
             title_color=c_ui_border)

    # -------------------------------------------------------------
    # ARROWS & DATAFLOWS
    # -------------------------------------------------------------
    # Query to BM25 & Semantic
    draw_arrow(4.0, 7.6, 4.8, 7.6, label="Terms", color="#1976D2")
    draw_arrow(4.0, 7.1, 4.8, 4.8, label="Dense Vector", color="#1976D2", rad=-0.15)

    # Preprocessed data to indexes
    draw_arrow(4.0, 2.5, 4.8, 2.0, label="Corpus & Chunks", color="#388E3C")
    draw_arrow(2.3, 5.4, 4.8, 7.1, label="BM25 Postings", color="#388E3C", rad=0.25)
    draw_arrow(2.3, 5.4, 4.8, 4.2, label="FAISS Index", color="#388E3C", rad=0.1)

    # BM25 & Semantic to RRF
    draw_arrow(6.6, 6.5, 6.6, 3.0, label="Ranks (BM25)", color="#512DA8")
    draw_arrow(6.6, 3.6, 6.6, 3.0, label="Ranks (Dense)", color="#512DA8")

    # RRF to UI and downstream engines
    draw_arrow(8.4, 2.0, 13.2, 2.0, label="Top-K Ranked Docs", color="#512DA8", lw=2)

    # Candidates to Risk Engine
    draw_arrow(8.4, 2.3, 9.3, 6.5, label="Posting Text", color="#D32F2F", rad=0.2)

    # Candidates to RAG Engine
    draw_arrow(8.4, 1.8, 9.3, 2.8, label="Top Chunks", color="#F57C00")

    # Risk Engine to UI
    draw_arrow(12.7, 6.8, 13.2, 6.8, label="Risk Signals", color="#D32F2F")

    # RAG Engine to UI
    draw_arrow(12.7, 2.8, 13.2, 3.5, label="Grounded RAG", color="#F57C00")

    # Save diagram
    plt.tight_layout()
    plt.savefig(OUT_PATH, format="png", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Successfully generated architecture diagram at: {OUT_PATH}")


if __name__ == "__main__":
    draw_architecture()
