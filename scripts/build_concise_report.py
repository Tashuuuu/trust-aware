#!/usr/bin/env python3
"""
scripts/build_concise_report.py
Generates a streamlined, precise, publication-grade Project Report.
Eliminates verbose filler, wordy exposition, and redundancies while preserving:
- Title page with JIIT logo
- All 8 figures and 5 tables
- Table of Contents, List of Figures, and List of Tables with dot-leader tabs
- IEEE reference syntax [1]-[11]
- Clean single-bullet formatting in Individual Contributions
- Direct, punchy academic writing style (~2,800 words total)
"""

import pathlib
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

DOCX_OUT = REPORTS_DIR / "Trust_Aware_Internship_Search_ProjectReport.docx"
MD_OUT = REPORTS_DIR / "project_report.md"
ORIGINAL_DOCX = REPORTS_DIR / "Trust_Aware_Internship_Search_ProjectReport.docx"

# Image Paths
FIG1_IMG = FIGURES_DIR / "fig1_architecture.png"
FIG2_IMG = REPORTS_DIR / "pr_curve.png"
FIG3_IMG = REPORTS_DIR / "retrieval_comparison.png"
FIG4_IMG = FIGURES_DIR / "fig4_dashboard.png"
FIG5_IMG = FIGURES_DIR / "fig5_risk.png"
FIG6_IMG = FIGURES_DIR / "fig6_rag.png"
FIG7_IMG = FIGURES_DIR / "fig7_abstain.png"
FIG8_IMG = FIGURES_DIR / "fig8_compare.png"

# Color constants
C_BLUE = RGBColor(31, 78, 121)      # #1F4E79
C_SUBBLUE = RGBColor(46, 117, 182)  # #2E75B6
C_GRAY = RGBColor(128, 128, 128)
HEX_HEADER_BG = "1F4E79"
HEX_ROW_ALT = "F9FBFD"


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)


def add_table_row(table, data, is_header=False, bg_hex=None):
    row = table.add_row()
    for i, val in enumerate(data):
        cell = row.cells[i]
        cell.text = str(val)
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (i > 0 and len(data) > 3) else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        for run in p.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            if is_header:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
        if is_header:
            set_cell_background(cell, HEX_HEADER_BG)
        elif bg_hex:
            set_cell_background(cell, bg_hex)
    return row


def build_doc():
    # Load original document to preserve cover page runs, styles, relationships, and images exactly
    doc = docx.Document(str(ORIGINAL_DOCX))

    # Remove all elements after the 14th paragraph (P0 to P13) except sectPr
    body = doc._body._body
    children = list(body)
    for child in children[14:]:
        if not child.tag.endswith("sectPr"):
            body.remove(child)

    # Standardize margins to 1.0 inch and ensure centered page numbers
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        
        footer = sec.footer
        p_foot = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Helper text formatting functions
    def add_p(text, bold_prefix="", space_before=0, space_after=5, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(12)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        return p

    def add_h1(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = C_BLUE
        return p

    def add_h2(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Times New Roman"
        r.font.size = Pt(13.5)
        r.font.bold = True
        r.font.color.rgb = C_SUBBLUE
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Times New Roman"
            rb.font.size = Pt(12)
            rb.font.bold = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        return p

    def add_caption(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.italic = True
        r.font.bold = True
        r.font.color.rgb = RGBColor(60, 60, 60)
        return p

    def add_img(img_path, width=Inches(5.8), caption=""):
        if img_path.exists():
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(2)
            p.add_run().add_picture(str(img_path), width=width)
            if caption:
                add_caption(caption)

    def add_toc_line(title, page_num, is_bold=False, indent=0):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1.5)
        p.paragraph_format.space_after = Pt(2.0)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        prefix = "    " * indent
        r1 = p.add_run(prefix + title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.font.bold = is_bold
        r2 = p.add_run(f"\t{page_num}")
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(11)
        r2.font.bold = is_bold

    # -------------------------------------------------------------
    # ABSTRACT
    # -------------------------------------------------------------
    add_h1("Abstract")
    add_p("Online recruitment platforms suffer from two critical limitations: lexical mismatch in keyword search, which misses relevant roles due to varying corporate nomenclature, and total opacity regarding job legitimacy, exposing early-career candidates to deceptive employment scams. This project presents the Trust-Aware Internship Search and Recommendation System, combining sparse lexical retrieval, dense semantic vector search, supervised deception detection, and citation-grounded Retrieval-Augmented Generation (RAG). Evaluated on the EMSCAD benchmark (15,560 postings), the platform implements an Okapi BM25 baseline, dense bi-encoder sentence representations (all-MiniLM-L6-v2 and multi-qa-MiniLM-L6-cos-v1) indexed via FAISS IndexFlatIP, and Reciprocal Rank Fusion (RRF, k=60). A dual-tier trust module combines rule heuristics with an SGD Logistic Regression classifier (PR-AUC = 0.76) to surface transparent risk signals with cautious non-defamatory disclaimers. For explainability, Gemini 3.5 Flash synthesizes match rationales with exact passage citations ([doc_id#c0]), enforced via five deterministic guardrails and a 0.30 cosine abstain threshold. Across 16 benchmark queries and 517 pooled annotations, BM25 plain establishes a dominant baseline (P@5 = 1.000, nDCG@10 = 0.925), outperforming dense retrieval (0.715) and Hybrid RRF (0.850) due to corporate boilerplate phrasing and short postings (~180 words). The RAG layer achieves 1.95/2.00 evidence grounding with zero hallucinated quotes, deployed as an interactive Streamlit application.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # TABLE OF CONTENTS
    # -------------------------------------------------------------
    add_h1("Table of Contents")
    toc_items = [
        ("Abstract", "2", False, 0),
        ("Table of Contents", "3", False, 0),
        ("List of Figures", "4", False, 0),
        ("List of Tables", "4", False, 0),
        ("1. Introduction", "5", True, 0),
        ("2. Problem Statement", "5", True, 0),
        ("3. Objectives", "5", True, 0),
        ("4. Information Need / Use Case", "6", True, 0),
        ("5. Dataset / Corpus Description", "6", True, 0),
        ("6. Background / Literature Study", "7", True, 0),
        ("7. Project Scope and Requirements", "8", True, 0),
        ("8. System Architecture", "9", True, 0),
        ("9. Data Preparation and Preprocessing", "10", True, 0),
        ("10. Document Representation", "10", True, 0),
        ("11. Indexing and Retrieval", "11", True, 0),
        ("12. Ranking / Semantic / Knowledge-Based Component", "11", True, 0),
        ("13. Implementation", "12", True, 0),
        ("14. Experimental Setup and Test Queries", "13", True, 0),
        ("15. Retrieval Evaluation", "14", True, 0),
        ("16. Results and Comparative Analysis", "14", True, 0),
        ("17. Discussion", "17", True, 0),
        ("18. Limitations", "18", True, 0),
        ("19. Future Scope", "18", True, 0),
        ("20. Conclusion", "18", True, 0),
        ("21. Individual Contributions", "19", True, 0),
        ("Work Distribution: Akriti Sengar (992509220001)", "19", False, 1),
        ("Work Distribution: Bhawna Rani (992509220008)", "19", False, 1),
        ("22. References", "20", True, 0),
    ]
    for title, pnum, bold, indent in toc_items:
        add_toc_line(title, pnum, is_bold=bold, indent=indent)

    doc.add_page_break()

    # -------------------------------------------------------------
    # LIST OF FIGURES & LIST OF TABLES
    # -------------------------------------------------------------
    add_h1("List of Figures")
    fig_items = [
        ("Figure 1: End-to-End System Architecture Pipeline Diagram", "9"),
        ("Figure 2: Precision-Recall Curve of the Logistic Risk Classifier on Held-Out Test Set", "16"),
        ("Figure 3: Retrieval Comparison Across Sparse, Dense, and Hybrid Architectures", "15"),
        ("Figure 4: Interactive Streamlit UI Search Dashboard with Skill Gap Analysis and Filter Controls", "12"),
        ("Figure 5: Transparent Risk Detection Engine Displaying Warning Flags, Trigger Terms, and Disclaimers", "16"),
        ("Figure 6: Grounded RAG Match Explanation with Source Chunk Citations [doc_id#c] and Verified Attributes", "15"),
        ("Figure 7: Out-of-Domain Query Abstain Behavior Triggered by Cosine Similarity Guardrail", "16"),
        ("Figure 8: Dual-Column Comparative View Evaluating BM25 Lexical Matching Against Hybrid RRF", "15"),
    ]
    for title, pnum in fig_items:
        add_toc_line(title, pnum)

    add_h1("List of Tables")
    tbl_items = [
        ("Table 1: Standardized Schema of Processed EMSCAD Corpus", "6"),
        ("Table 2: Retrieval Evaluation Results Across All Systems (16 Queries)", "14"),
        ("Table 3: Per-Query Performance Comparison Across Core Queries (q1–q5)", "15"),
        ("Table 4: RAG Explanation Evaluation Across Relevance, Evidence, and Attribution (0–2 Scale)", "15"),
        ("Table 5: Deterministic Guardrail Auditing Statistics (80 Instances)", "16"),
    ]
    for title, pnum in tbl_items:
        add_toc_line(title, pnum)

    doc.add_page_break()

    # -------------------------------------------------------------
    # 1. INTRODUCTION
    # -------------------------------------------------------------
    add_h1("Introduction")
    add_p("The modern digital recruitment ecosystem enables early-career candidates to explore thousands of employment opportunities across web aggregators. However, job seekers face substantial friction: keyword-based search fails to resolve semantic synonyms (e.g. an 'entry-level data analyst' query missing a posting titled 'Junior Business Intelligence Trainee'), while fraudulent postings—such as advance-fee work-from-home scams—threaten vulnerable applicants.")
    add_p("To address these challenges, this project introduces the Trust-Aware Internship Search and Recommendation System. The platform combines classical Okapi BM25 retrieval, FAISS dense vector search, Reciprocal Rank Fusion, supervised risk identification, and verifiable Retrieval-Augmented Generation (RAG) into a single production-grade search dashboard.")

    # -------------------------------------------------------------
    # 2. PROBLEM STATEMENT
    # -------------------------------------------------------------
    add_h1("Problem Statement")
    add_p("Conventional employment search systems suffer from four primary limitations:")
    add_bullet("Keyword matching misses semantically relevant listings that use alternative phrasing or corporate terminology.", bold_prefix="Lexical Fragility: ")
    add_bullet("Traditional portals rank listings purely by query similarity, offering zero caution against fraudulent postings or advance-fee scams.", bold_prefix="Absence of Risk Awareness: ")
    add_bullet("Arbitrary relevance scores provide no qualitative rationale explaining why a role matches a candidate's background.", bold_prefix="Interpretability Deficit: ")
    add_bullet("Unconstrained generative language models frequently hallucinate job requirements and company attributes.", bold_prefix="LLM Hallucinations: ")

    # -------------------------------------------------------------
    # 3. OBJECTIVES
    # -------------------------------------------------------------
    add_h1("Objectives")
    add_p("The key engineering and research objectives are:")
    add_bullet("Ingest, clean, and standardize 17,880 raw EMSCAD postings into a deduplicated 15,560-row Parquet corpus.", bold_prefix="1. Corpus Standardization: ")
    add_bullet("Construct an Okapi BM25 inverted index retriever across unstemmed and stemmed text representations.", bold_prefix="2. Sparse Baseline: ")
    add_bullet("Encode text into 384-dimensional dense vectors using Sentence Transformers and build a FAISS IndexFlatIP index.", bold_prefix="3. Dense Vector Indexing: ")
    add_bullet("Implement Reciprocal Rank Fusion (RRF, k=60) to merge sparse lexical precision and dense semantic recall.", bold_prefix="4. Hybrid Fusion: ")
    add_bullet("Combine rule heuristics with an SGD Logistic Regression classifier to flag high-risk listings with transparent keyword evidence.", bold_prefix="5. Trust Engine: ")
    add_bullet("Deploy Gemini 3.5 Flash with five deterministic guardrails and a 0.30 cosine abstain threshold for verifiable explanations.", bold_prefix="6. Grounded RAG: ")
    add_bullet("Evaluate retrieval and generation across 16 benchmark queries and 517 pooled human relevance judgments.", bold_prefix="7. Benchmark Evaluation: ")

    # -------------------------------------------------------------
    # 4. INFORMATION NEED / USE CASE
    # -------------------------------------------------------------
    add_h1("Information Need / Use Case")
    add_p("The system fulfills three distinct early-career discovery scenarios:")
    add_bullet("A student querying 'ML intern' with skills 'python, scikit-learn' receives verified junior roles with explicit skill-gap indicators highlighting matched and missing prerequisites.", bold_prefix="Case 1 (Technical Matching): ")
    add_bullet("A candidate searching for remote data entry encounters high-earning scam postings. The system surfaces amber/red caution banners detailing suspicious triggers (empty profiles, fee requests) under the ethical disclaimer: 'Warnings are signals, not proof of fraud.'", bold_prefix="Case 2 (Deception Trapping): ")
    add_bullet("An out-of-domain query ('deep sea welding internship') safely triggers an automatic abstain response rather than generating hallucinated relevance.", bold_prefix="Case 3 (Boundary Verification): ")

    # -------------------------------------------------------------
    # 5. DATASET / CORPUS DESCRIPTION
    # -------------------------------------------------------------
    add_h1("Dataset/Corpus Description")
    add_p("The platform is built on the Employment Scam Aegean Dataset (EMSCAD) [1], comprising genuine recruitment advertisements collected from Workable between 2012 and 2014. After cleaning and deduplication, the standardized corpus contains 15,560 listings (14,810 legitimate, 750 fraudulent, representing a realistic 4.82% fraud class imbalance). Data was partitioned into an 80% training set (12,448 rows) and a 20% held-out test set (3,112 rows), stratified by the fraud target label.")

    # Table 1: Corpus Schema
    add_caption("Table 1: Standardized Schema of Processed EMSCAD Corpus (corpus.parquet)")
    t1 = doc.add_table(rows=0, cols=3)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_table_row(t1, ["Field Name", "Data Type", "Description & Usage in Pipeline"], is_header=True)
    t1_data = [
        ["doc_id", "String (Unique ID)", "Canonical identifier (e.g. emscad_0 to emscad_17879)."],
        ["title", "String", "Job title used in BM25 title boosting and UI display."],
        ["company_profile", "String", "Organizational background; screened for length heuristics."],
        ["description", "String", "Core job responsibilities and project overview."],
        ["requirements", "String", "Required candidate skills, tools, and education."],
        ["search_text", "String", "Concatenation of title, company, description, and requirements."],
        ["telecommuting", "Integer (0/1)", "Remote employment indicator used in query filtering."],
        ["has_company_logo", "Integer (0/1)", "Presence of company logo (heuristic scam feature)."],
        ["has_questions", "Integer (0/1)", "Screening questionnaire present (legitimacy signal)."],
        ["fraudulent", "Integer (0/1)", "Ground truth label: 0 = Legitimate (95.2%), 1 = Fraudulent (4.8%)."],
        ["split", "Categorical", "Stratified partition: 'train' (80%) for risk classifier, 'test' (20%)."]
    ]
    for row in t1_data:
        add_table_row(t1, row)

    # -------------------------------------------------------------
    # 6. BACKGROUND / LITERATURE STUDY
    # -------------------------------------------------------------
    add_h1("Background / Literature Study")
    add_bullet("Probabilistic retrieval computes relevance using term saturation (k1 = 1.5) and length normalization (b = 0.75). BM25 excels at exact keyword matching but cannot resolve synonymy [2].", bold_prefix="Okapi BM25: ")
    add_bullet("Sentence-BERT bi-encoders project text into continuous 384-dimensional spaces where cosine distance captures semantic intent independently of surface wording [3].", bold_prefix="Dense Bi-Encoders: ")
    add_bullet("Facebook AI Similarity Search provides vectorized SIMD inner-product operations, enabling sub-millisecond nearest neighbor search over dense matrices [4].", bold_prefix="FAISS Indexing: ")
    add_bullet("RRF aggregates disparate retrieval rankings monotonically without requiring score calibration: RRF(d) = Σ 1 / (60 + r_m(d)) [5].", bold_prefix="Reciprocal Rank Fusion: ")
    add_bullet("RAG combines parametric generative language models with non-parametric passage retrieval, mitigating hallucination by constraining outputs strictly to source context [6].", bold_prefix="Retrieval-Augmented Generation: ")

    # -------------------------------------------------------------
    # 7. PROJECT SCOPE AND REQUIREMENTS
    # -------------------------------------------------------------
    add_h1("Project Scope and Requirements")
    add_bullet("English-language listings, offline dense embedding generation, exact FAISS inner-product indexing, hybrid RRF fusion, supervised risk indicators, citation-grounded RAG explanations, and interactive Streamlit UI.", bold_prefix="In-Scope: ")
    add_bullet("Live web scraping, predicting individual hiring odds, and asserting definitive legal fraud claims.", bold_prefix="Out-of-Scope: ")
    add_bullet("System memory under 8 GB RAM, sub-100ms retrieval latency, sub-50ms cached RAG latency, and deterministic evaluation reproducibility (random_state=42).", bold_prefix="System Constraints: ")

    # -------------------------------------------------------------
    # 8. SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    add_h1("System Architecture")
    add_p("The platform is organized into four core layers: dual-path retrieval (BM25 sparse + FAISS dense), Reciprocal Rank Fusion (k=60), trust and risk scoring (heuristics + logistic classifier), and grounded RAG explanation generation with deterministic guardrails. Figure 1 illustrates the end-to-end dataflow.")
    add_img(FIG1_IMG, width=Inches(6.2), caption="Figure 1: End-to-End System Architecture Pipeline Diagram (reports/figures/fig1_architecture.png)")

    # -------------------------------------------------------------
    # 9. DATA PREPARATION AND PREPROCESSING
    # -------------------------------------------------------------
    add_h1("Data Preparation and Preprocessing")
    add_p("Preprocessing enforced four standardized operations:")
    add_bullet("HTML tags and escaped Unicode entities were stripped, whitespace normalized, and non-printable characters removed.", bold_prefix="1. Text Normalization: ")
    add_bullet("Title, company profile, description, and requirements were concatenated into a unified search_text field.", bold_prefix="2. Field Amalgamation: ")
    add_bullet("Identical postings sharing identical descriptions and company profiles were eliminated.", bold_prefix="3. Deduplication: ")
    add_bullet("A domain-specific lexicon of 35+ technical skills was compiled with regex alias patterns (data/processed/skills_lexicon.csv) for deterministic candidate-posting skill matching.", bold_prefix="4. Skill Lexicon: ")

    # -------------------------------------------------------------
    # 10. DOCUMENT REPRESENTATION
    # -------------------------------------------------------------
    add_h1("Document Representation")
    add_bullet("Evaluated unstemmed (bm25_plain), normalized (bm25_norm), and Porter-stemmed (bm25_stem) bag-of-words tokenizations.", bold_prefix="Sparse Vectors: ")
    add_bullet("Encoded postings into 384-dimensional dense vectors using all-MiniLM-L6-v2 (256-token limit) and multi-qa-MiniLM-L6-cos-v1 (512-token limit).", bold_prefix="Dense Bi-Encoders: ")
    add_bullet("Postings were partitioned into 130-word sliding windows with 20-word overlap (42,480 chunk vectors) to assess passage retrieval against full-document encoding.", bold_prefix="Sliding-Window Chunks: ")
    add_bullet("Embeddings were L2-normalized upon encoding (||v|| = 1.0), making cosine similarity mathematically identical to dot product (cos(q, d) = q · d) and optimizing search throughput.", bold_prefix="Unit Normalization: ")

    # -------------------------------------------------------------
    # 11. INDEXING AND RETRIEVAL
    # -------------------------------------------------------------
    add_h1("Indexing and Retrieval")
    add_bullet("In-memory inverted index built via rank_bm25 across 15,560 corpus postings.", bold_prefix="BM25 Inverted Index: ")
    add_bullet("Built using FAISS IndexFlatIP (23.9 MB disk footprint, <3.5s build time). Top-10 results and scores matched pure NumPy matrix multiplication with zero discrepancy.", bold_prefix="FAISS Vector Index: ")
    add_bullet("Streamlit worker collisions with PyTorch/FAISS OpenMP pools on macOS ARM64 Apple Silicon triggered SIGSEGV crashes. Resolved by enforcing faiss.omp_set_num_threads(1) and torch.set_num_threads(1), ensuring 2ms retrieval latency with complete stability.", bold_prefix="macOS OpenMP Stability Fix: ")

    # -------------------------------------------------------------
    # 12. RANKING / SEMANTIC / KNOWLEDGE-BASED COMPONENT
    # -------------------------------------------------------------
    add_h1("Ranking / Semantic / Knowledge-Based Component")
    add_p("The hybrid engine unifies sparse and dense retrieval using Reciprocal Rank Fusion (RRF):")
    add_p("RRF_Score(d ∈ D) = [ 1 / (60 + rank_bm25(d)) ] + [ 1 / (60 + rank_semantic(d)) ]", align=WD_ALIGN_PARAGRAPH.CENTER)
    add_p("Ablation testing over k ∈ {10, 30, 60, 100} confirmed that k=60 achieves optimal rank smoothing, preventing single-system outliers from displacing consensus candidates. In chunked semantic search, document relevance is aggregated via max-pooling: Score_doc(D) = max_{c ∈ Chunks(D)} Cosine(Q, c).")

    # -------------------------------------------------------------
    # 13. IMPLEMENTATION
    # -------------------------------------------------------------
    add_h1("Implementation")
    add_p("The codebase is organized into seven modular Python components:")
    add_bullet("Dense embedding generation, FAISS indexing, verification, and RRF hybrid search.", bold_prefix="src/semantic.py: ")
    add_bullet("BM25 tokenization, inverted indexing, and multi-field scoring.", bold_prefix="src/bm25_search.py: ")
    add_bullet("Deterministic skill extraction and candidate-posting skill gap analysis.", bold_prefix="src/skills.py: ")
    add_bullet("Heuristic scam detection rules and SGD Logistic Regression risk scoring.", bold_prefix="risk/risk_report.py: ")
    add_bullet("Passage chunking, Gemini 3.5 Flash calling, 5-stage guardrails, and SHA-256 disk caching.", bold_prefix="src/rag_explain.py: ")
    add_bullet("Custom IR metric implementations (P@k, MRR, nDCG@k) cross-tested against ranx.", bold_prefix="src/eval_metrics.py: ")
    add_bullet("Interactive web application with method toggles, risk badges, and RAG expanders.", bold_prefix="app/streamlit_app.py: ")
    add_img(FIG4_IMG, width=Inches(5.8), caption="Figure 4: Interactive Streamlit UI Search Dashboard with Skill Gap Analysis and Filter Controls (reports/figures/fig4_dashboard.png)")

    # -------------------------------------------------------------
    # 14. EXPERIMENTAL SETUP AND TEST QUERIES
    # -------------------------------------------------------------
    add_h1("Experimental Setup and Test Queries")
    add_p("System evaluation was conducted across 16 standardized queries in data/processed/queries.json: Core queries (q1–q5: Data Analyst, ML intern, remote no-exp, WFH scam, Software Java), Supplementary queries (q6–q15: DevOps, cybersecurity, React), and Stress query (q16: deep sea welding, out-of-domain abstain test).")
    add_p("Candidate Pooling & Ground Truth: Top-10 results from six retrieval runs were pooled and deduplicated into a system-blind sheet of 517 candidate judgments (data/eval/pool_for_labelling.csv). Relevance was graded on a 3-point scale: 0 (Non-Relevant), 1 (Partially Relevant), and 2 (Highly Relevant).")

    # -------------------------------------------------------------
    # 15. RETRIEVAL EVALUATION
    # -------------------------------------------------------------
    add_h1("Retrieval Evaluation")
    add_p("Performance was measured across three classical IR metrics [7]: Precision@5 (P@5), Mean Reciprocal Rank (MRR), and Normalized Discounted Cumulative Gain (nDCG@10) under linear gain formulation. All metric functions in src/eval_metrics.py were programmatically cross-validated against the academic ranx library [8], confirming exact numerical equivalence down to 6 decimal places.")

    # -------------------------------------------------------------
    # 16. RESULTS AND COMPARATIVE ANALYSIS
    # -------------------------------------------------------------
    add_h1("Results and Comparative Analysis")
    add_p("Table 2 and Figure 3 summarize overall retrieval performance across all eight evaluated configurations over the 16 test queries.")

    # Table 2: Retrieval Evaluation Results
    add_caption("Table 2: Retrieval Evaluation Results Across All Systems (P@5, nDCG@10, MRR over 16 Queries)")
    t2 = doc.add_table(rows=0, cols=5)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_table_row(t2, ["Retrieval System", "P@5", "nDCG@10", "MRR", "Queries"], is_header=True)
    t2_data = [
        ["bm25_plain", "1.000", "0.925", "1.000", "16"],
        ["bm25 (baseline)", "0.988", "0.900", "1.000", "16"],
        ["bm25_norm", "0.988", "0.900", "1.000", "16"],
        ["bm25_stem", "0.988", "0.849", "1.000", "16"],
        ["hybrid_rrf (Proposed)", "0.975", "0.850", "1.000", "16"],
        ["sem_minilm (Model A)", "0.913", "0.715", "0.969", "16"],
        ["sem_minilm_chunks", "0.863", "0.655", "0.906", "16"],
        ["sem_multiqa (Model B)", "0.838", "0.691", "0.969", "16"]
    ]
    for row in t2_data:
        add_table_row(t2, row)

    add_img(FIG3_IMG, width=Inches(5.5), caption="Figure 3: Retrieval Comparison Across Sparse, Dense, and Hybrid Architectures (reports/retrieval_comparison.png)")

    add_p("BM25 plain establishes the top-performing configuration (P@5 = 1.000, nDCG@10 = 0.925). Figure 8 illustrates the dual-column comparison mode for query 'trainee developer fresh graduate'. Dense similarity in Hybrid RRF promotes semantically aligned graduate trainee positions ahead of purely keyword-matched postings.")
    add_img(FIG8_IMG, width=Inches(5.8), caption="Figure 8: Dual-Column Comparative View Evaluating BM25 Lexical Matching Against Hybrid RRF (reports/figures/fig8_compare.png)")

    # Table 3: Per-Query Breakdown
    add_caption("Table 3: Per-Query Performance Comparison Across Core Queries (q1–q5)")
    t3 = doc.add_table(rows=0, cols=4)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_table_row(t3, ["Query ID", "Query Intent Description", "Top-1 Retrieved Document", "Relevance Status & Notes"], is_header=True)
    t3_data = [
        ["q1", "Data analyst intern, Python & SQL", "emscad_4589 (Data Analyst Intern)", "Clean match (Label 2); university intern."],
        ["q2", "ML intern fresher, scikit-learn", "emscad_14113 (Data Science Intern)", "Matched scikit-learn & Python; BM25 rank 1."],
        ["q3", "Remote internship, no experience", "emscad_7983 (Web Intern - Remote)", "Verified 100% remote commitment; clean match."],
        ["q4", "WFH data entry, high earnings scam", "emscad_7667 (Entry Level Online Typist)", "Classic EMSCAD fraud sample; high risk flag."],
        ["q5", "Software intern, Java & database", "emscad_2065 (Software Dev Intern)", "Clean match (Label 2); Java & SQL required."]
    ]
    for row in t3_data:
        add_table_row(t3, row)

    # Table 4: RAG Evaluation Table
    add_caption("Table 4: RAG Explanation Evaluation Across Relevance, Evidence, and Attribution (0–2 Scale)")
    t4 = doc.add_table(rows=0, cols=6)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_table_row(t4, ["Query", "Eval Count", "Avg Relevance /2", "Avg Evidence /2", "Avg Attribution /2", "Avg Total /6"], is_header=True)
    t4_data = [
        ["q1: Data Analyst (Python/SQL)", "5", "1.60", "2.00", "2.00", "5.60"],
        ["q2: ML Intern Fresher", "5", "0.60", "2.00", "2.00", "4.60"],
        ["q3: Remote No-Experience", "4", "1.00", "1.75", "2.00", "4.75"],
        ["q4: WFH High Earnings Scam", "5", "1.40", "2.00", "1.80", "5.20"],
        ["q5: Software Intern (Java/DB)", "2", "1.50", "2.00", "2.00", "5.50"],
        ["q16: Deep Sea Welding (Abstain)", "1", "0.00", "2.00", "2.00", "4.00"],
        ["OVERALL AVERAGE", "22", "1.14", "1.95", "1.95", "5.05"]
    ]
    for row in t4_data:
        add_table_row(t4, row, bg_hex="F2F2F2" if row[0] == "OVERALL AVERAGE" else None)

    add_p("Figure 6 shows a grounded RAG explanation card for an entry-level Data Analyst posting, incorporating verified passage citations ([emscad_4589#c0], [emscad_4589#c1]).")
    add_img(FIG6_IMG, width=Inches(5.8), caption="Figure 6: Grounded RAG Match Explanation with Source Chunk Citations [doc_id#c] and Verified Attributes (reports/figures/fig6_rag.png)")

    # Table 5: Guardrail Stats
    add_caption("Table 5: Deterministic Guardrail Auditing Statistics Across 80 Generation Instances")
    t5 = doc.add_table(rows=0, cols=3)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_table_row(t5, ["Guardrail Verification Check", "Failure Count", "Audit Outcome & Enforcement Action"], is_header=True)
    t5_data = [
        ["JSON Format Enforcement", "0", "100% compliant JSON responses returned by Gemini."],
        ["Source ID Existence", "0", "All [doc_id#c] citations traced to valid retrieved chunks."],
        ["Word-for-Word Quote Match", "0", "100% of cited quotes verified verbatim in chunk text."],
        ["Deterministic Skill Overwrite", "114", "Model skills overwritten by regex lexicon extractor."],
        ["Defamation Keyword Neutralizer", "0", "No unlawful accusations of 'fraud' generated by LLM."]
    ]
    for row in t5_data:
        add_table_row(t5, row)

    add_p("Figure 7 illustrates the cosine similarity guardrail safely abstaining on out-of-domain query q16 ('deep sea welding internship') rather than hallucinating false advice.")
    add_img(FIG7_IMG, width=Inches(5.8), caption="Figure 7: Out-of-Domain Query Abstain Behavior Triggered by Cosine Similarity Guardrail (reports/figures/fig7_abstain.png)")

    add_p("Figure 2 and Figure 5 illustrate risk classifier validation (PR-AUC = 0.76) and operational warnings for query q4, displaying triggered heuristic rules and top risk terms with caution disclaimers.")
    add_img(FIG2_IMG, width=Inches(4.5), caption="Figure 2: Precision-Recall Curve of the Logistic Risk Classifier on Held-Out Test Set (reports/pr_curve.png)")
    add_img(FIG5_IMG, width=Inches(5.8), caption="Figure 5: Transparent Risk Detection Engine Displaying Warning Flags, Trigger Terms, and Disclaimers (reports/figures/fig5_risk.png)")

    # -------------------------------------------------------------
    # 17. DISCUSSION
    # -------------------------------------------------------------
    add_h1("Discussion")
    add_p("Why BM25 Plain Outperformed Semantic and Hybrid Retrieval on EMSCAD:")
    add_bullet("EMSCAD job postings follow rigid corporate boilerplate phrasing ('Data Analyst Intern', 'Requirements'). Queries matched verbatim phrases directly, heavily favoring exact BM25 term weighting.", bold_prefix="1. Standardized Corporate Vocabulary: ")
    add_bullet("Mean posting length is ~180 words, fitting within the 256-token limit of MiniLM. Chunking into 130-word fragments added boundary noise without recovering lost context, reducing nDCG@10 from 0.715 to 0.655.", bold_prefix="2. Brevity & Chunking Ineffectiveness: ")
    add_bullet("Because BM25 top-5 ranks were near-perfect, fusing them with broader semantic candidates diluted precision at ranks 2 through 5, dropping Hybrid nDCG@10 to 0.850.", bold_prefix="3. RRF Rank Dilution: ")
    add_bullet("Porter stemming collapsed distinct titles (e.g. 'analyst' vs 'analysis'), increasing false-positive matches and reducing nDCG@10 from 0.925 to 0.849.", bold_prefix="4. Stemming Degradation: ")
    add_bullet("Manual auditing scored Evidence Support and Citation Attribution at 1.95/2.00. The LLM actively exposed seniority mismatches (e.g. flagging 'senior Ph.D. required' on fresher queries) rather than fabricating relevance.", bold_prefix="5. RAG Factual Grounding: ")

    # -------------------------------------------------------------
    # 18. LIMITATIONS
    # -------------------------------------------------------------
    add_h1("Limitations")
    add_bullet("2012–2014 listings from one European/US recruitment platform, lacking modern remote work patterns or contemporary tech stacks (e.g. LangChain, Next.js).", bold_prefix="1. Dataset Era: ")
    add_bullet("Accelerated via keyword-overlap heuristics before manual spot-checks, serving as baseline research labels.", bold_prefix="2. Heuristic Pool Labels: ")
    add_bullet("16 queries demonstrate operational tendencies but lack statistical sample size (>50 queries) for significance testing.", bold_prefix="3. Query Set Size: ")
    add_bullet("Retrieval was restricted to bi-encoders and RRF without a heavy cross-attention re-ranker due to latency constraints.", bold_prefix="4. No Cross-Encoder: ")
    add_bullet("The static 0.30 cosine threshold permitted one pipe welder posting through on q16; 0.40 is recommended for complete isolation.", bold_prefix="5. Static Abstain Threshold: ")

    # -------------------------------------------------------------
    # 19. FUTURE SCOPE
    # -------------------------------------------------------------
    add_h1("Future Scope")
    add_bullet("Incorporate ms-marco-MiniLM-L-6-v2 cross-attention scoring over top-50 candidates.", bold_prefix="1. Neural Cross-Encoder Re-Ranking: ")
    add_bullet("Convert postings into RDF triples utilizing schema.org/JobPosting ontologies [10] for structured SPARQL querying.", bold_prefix="2. Knowledge Graph Triplification: ")
    add_bullet("Replace static cosine cutoffs with corpus-adaptive quantile thresholds.", bold_prefix="3. Adaptive Abstain Thresholds: ")
    add_bullet("Connect live aggregator APIs (e.g. Adzuna, Remotive) for real-time internship discovery.", bold_prefix="4. Live Multi-Source Ingestion: ")

    # -------------------------------------------------------------
    # 20. CONCLUSION
    # -------------------------------------------------------------
    add_h1("Conclusion")
    add_p("The Trust-Aware Internship Search System successfully integrates Okapi BM25 retrieval, FAISS dense vector search, Reciprocal Rank Fusion, supervised deception detection, and grounded RAG generation. The empirical findings demonstrate that classical BM25 remains dominant in concise, boilerplate recruitment text, while dense semantic models provide vital passage selection for hallucination-free AI explanations. By pairing non-parametric retrieval memory with deterministic guardrails, the platform demonstrates that trust-aware search is practically viable, responsive, and ethically grounded.")

    # -------------------------------------------------------------
    # 21. INDIVIDUAL CONTRIBUTIONS
    # -------------------------------------------------------------
    add_h1("Individual Contributions")
    add_p("The project research, implementation, evaluation, and documentation were collaboratively executed by Akriti Sengar and Bhawna Rani. The division of work is detailed below:")

    add_h2("Work Distribution: Akriti Sengar (Enrollment No. 992509220001)")
    add_bullet("Sourced the raw EMSCAD benchmark dataset (17,880 listings), verified CC-BY-NC-SA licensing, and configured raw storage.", bold_prefix="Corpus Acquisition & Licensing: ")
    add_bullet("Conducted exploratory data analysis on title distributions, company fields, and target fraud class imbalance.", bold_prefix="Exploratory Data Analysis: ")
    add_bullet("Executed HTML tag stripping, text normalization, and exported the standardized corpus.parquet (15,560 rows).", bold_prefix="Data Cleaning & Parquet Schema: ")
    add_bullet("Assembled the initial regex-based skill lexicon (skills_lexicon.csv) covering technical tools for candidate matching.", bold_prefix="Skill Lexicon Construction: ")
    add_bullet("Implemented the initial Okapi BM25 inverted index retrieval pipeline using rank_bm25 across corpus postings.", bold_prefix="BM25 Lexical Baseline: ")
    add_bullet("Formulated deterministic scam detection heuristic rules based on upfront fees, suspicious emails, and empty profiles.", bold_prefix="Heuristic Risk Rules: ")
    add_bullet("Trained the SGD Logistic Regression classifier on word and character n-grams to detect potentially fraudulent listings.", bold_prefix="Risk Classifier Training: ")
    add_bullet("Developed the initial prototype Streamlit application shell for interactive demonstration.", bold_prefix="Streamlit Application Scaffold: ")

    add_h2("Work Distribution: Bhawna Rani (Enrollment No. 992509220008)")
    add_bullet("Encoded the corpus into 384-dimensional dense vectors using all-MiniLM-L6-v2 and multi-qa-MiniLM-L6-cos-v1, and built the FAISS IndexFlatIP index with verified inner-product equivalence.", bold_prefix="Dense Vector Embeddings & Indexing: ")
    add_bullet("Designed 130-word sliding-window chunking (42,480 chunk vectors) with chunk-to-document max pooling retrieval.", bold_prefix="Sliding-Window Chunking: ")
    add_bullet("Implemented the Reciprocal Rank Fusion (RRF) engine, conducted parameter ablation across k ∈ {10, 30, 60, 100}, and integrated dual-column comparison.", bold_prefix="Hybrid Reciprocal Rank Fusion: ")
    add_bullet("Engineered the pooling harness (src/make_pool.py) pooling 517 candidate documents across 16 queries and 6 retriever runs, and executed 3-point relevance grading.", bold_prefix="Relevance Pooling & Ground-Truth Labelling: ")
    add_bullet("Developed custom P@5, MRR, and nDCG@10 metrics and mathematically cross-validated implementations against ranx [8].", bold_prefix="IR Metric Suite & ranx Validation: ")
    add_bullet("Architected the Gemini 3.5 Flash RAG pipeline, authored structured prompts, calibrated the 0.30 cosine abstain threshold, engineered 5 deterministic guardrails, and implemented SHA-256 disk caching.", bold_prefix="Grounded RAG & Guardrails: ")
    add_bullet("Scored 22 RAG explanation instances across Relevance, Evidence Support, and Citation Attribution, and compiled the citation reference audit.", bold_prefix="Manual RAG Evaluation & Audit: ")
    add_bullet("Diagnosed and resolved the native OpenMP SIGSEGV multi-threading crash in libomp.dylib on Apple Silicon, and redesigned the Streamlit UI.", bold_prefix="macOS OpenMP Crash Fix & UI Redesign: ")
    add_bullet("Authored the complete formal 22-section project report in Microsoft Word (.docx) and Markdown (.md) formats.", bold_prefix="Project Report Synthesis: ")

    # -------------------------------------------------------------
    # 22. REFERENCES
    # -------------------------------------------------------------
    add_h1("References")
    ieee_refs = [
        "[1]\tS. Vidros, C. Kolias, G. Kambourakis, and L. Akoglu, \"Automatic Detection of Online Recruitment Frauds: Characteristics, Methods, and a Public Dataset,\" Future Internet, vol. 9, no. 1, p. 6, 2017.",
        "[2]\tS. Robertson and H. Zaragoza, \"The Probabilistic Relevance Framework: BM25 and Beyond,\" Foundations and Trends in Information Retrieval, vol. 3, no. 4, pp. 333–389, 2009.",
        "[3]\tN. Reimers and I. Gurevych, \"Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,\" in Proc. 2019 Conf. Empirical Methods in Natural Language Processing (EMNLP), Hong Kong, China, 2019, pp. 3982–3992.",
        "[4]\tJ. Johnson, M. Douze, and H. Jégou, \"Billion-scale similarity search with GPUs,\" IEEE Transactions on Big Data, vol. 7, no. 3, pp. 535–547, 2019.",
        "[5]\tG. V. Cormack, C. L. Clarke, and S. Buettcher, \"Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,\" in Proc. 32nd Int. ACM SIGIR Conf. Research and Development in Information Retrieval, Boston, MA, USA, 2009, pp. 758–759.",
        "[6]\tP. Lewis et al., \"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, 2020, pp. 9459–9474.",
        "[7]\tC. D. Manning, P. Raghavan, and H. Schütze, Introduction to Information Retrieval. Cambridge University Press, Cambridge, UK, 2008.",
        "[8]\tE. Bassani, \"ranx: A Blazing-Fast Python Library for Ranking Evaluation and Comparison,\" in Proc. 44th European Conf. Information Retrieval (ECIR), Stavanger, Norway, 2022, pp. 238–244.",
        "[9]\tGoogle DeepMind, \"Gemini: A Family of Highly Capable Multimodal Models,\" Technical Report, Google AI, 2024. Available: https://arxiv.org/abs/2312.11805",
        "[10]\tW3C, \"RDF 1.1 Concepts and Abstract Syntax,\" W3C Recommendation, 2014. [Online]. Available: https://www.w3.org/TR/rdf11-concepts/",
        "[11]\tStreamlit Documentation, \"The Fastest Way to Build Data Apps,\" Available: https://docs.streamlit.io/"
    ]
    for ref_str in ieee_refs:
        p = doc.add_paragraph()
        p.text = ref_str
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)

    doc.save(str(DOCX_OUT))
    print(f"Successfully generated concise report at: {DOCX_OUT}")


if __name__ == "__main__":
    build_doc()
