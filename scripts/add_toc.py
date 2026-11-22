#!/usr/bin/env python3
"""
scripts/add_toc.py
Adds a professional Table of Contents, List of Figures, and List of Tables
to reports/Trust_Aware_Internship_Search_ProjectReport.docx and reports/tw_report.docx.
Uses right-aligned dot-leader tab stops matching IEEE / NextWatch formatting.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER, WD_ALIGN_PARAGRAPH

DOCX_PATH = "reports/Trust_Aware_Internship_Search_ProjectReport.docx"
doc = docx.Document(DOCX_PATH)

# Find Introduction paragraph
intro_idx = None
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == "Introduction":
        intro_idx = i
        break

if intro_idx is None:
    raise ValueError("Introduction heading not found in document!")

intro_para = doc.paragraphs[intro_idx]

# Helper to add a TOC heading
def add_toc_heading(target_para, title):
    p = target_para.insert_paragraph_before()
    p.style = "Body"
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(title)
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = RGBColor(31, 78, 121)
    return p

# Helper to add a dot-leader TOC line
def add_toc_line(target_para, title, page_num, is_bold=False, indent_spaces=0):
    p = target_para.insert_paragraph_before()
    p.style = "Body"
    p.paragraph_format.space_before = Pt(1.5)
    p.paragraph_format.space_after = Pt(2.0)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    
    prefix = "    " * indent_spaces
    r_title = p.add_run(prefix + title)
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(11)
    r_title.font.bold = is_bold
    
    r_page = p.add_run(f"\t{page_num}")
    r_page.font.name = "Times New Roman"
    r_page.font.size = Pt(11)
    r_page.font.bold = is_bold
    return p

def add_page_break(target_para):
    p = target_para.insert_paragraph_before()
    p.style = "Body"
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run()
    r.add_break(docx.enum.text.WD_BREAK.PAGE)
    return p

# 1. Page break after Abstract (before TOC)
add_page_break(intro_para)

# 2. TABLE OF CONTENTS
add_toc_heading(intro_para, "Table of Contents")

toc_entries = [
    ("Abstract", "2", False, 0),
    ("Table of Contents", "3", False, 0),
    ("List of Figures", "4", False, 0),
    ("List of Tables", "4", False, 0),
    ("1. Introduction", "5", True, 0),
    ("2. Problem Statement", "5", True, 0),
    ("3. Objectives", "6", True, 0),
    ("4. Information Need / Use Case", "6", True, 0),
    ("5. Dataset / Corpus Description", "7", True, 0),
    ("6. Background / Literature Study", "8", True, 0),
    ("7. Project Scope and Requirements", "9", True, 0),
    ("8. System Architecture", "10", True, 0),
    ("9. Data Preparation and Preprocessing", "11", True, 0),
    ("10. Document Representation", "12", True, 0),
    ("11. Indexing and Retrieval", "12", True, 0),
    ("12. Ranking / Semantic / Knowledge-Based Component", "13", True, 0),
    ("13. Implementation", "14", True, 0),
    ("14. Experimental Setup and Test Queries", "15", True, 0),
    ("15. Retrieval Evaluation", "16", True, 0),
    ("16. Results and Comparative Analysis", "17", True, 0),
    ("17. Discussion", "20", True, 0),
    ("18. Limitations", "21", True, 0),
    ("19. Future Scope", "21", True, 0),
    ("20. Conclusion", "22", True, 0),
    ("21. Individual Contributions", "23", True, 0),
    ("Work Distribution: Akriti Sengar (992509220001)", "23", False, 1),
    ("Work Distribution: Bhawna Rani (992509220008)", "23", False, 1),
    ("22. References", "24", True, 0)
]

for title, page_num, is_bold, indent in toc_entries:
    add_toc_line(intro_para, title, page_num, is_bold=is_bold, indent_spaces=indent)

# 3. Page break after TOC (before List of Figures & Tables)
add_page_break(intro_para)

# 4. LIST OF FIGURES
add_toc_heading(intro_para, "List of Figures")

figures = [
    ("Figure 1: End-to-End System Architecture Pipeline Diagram", "10"),
    ("Figure 2: Precision-Recall Curve of the Logistic Risk Classifier on Held-Out Test Set", "19"),
    ("Figure 3: Retrieval Comparison Across Sparse, Dense, and Hybrid Architectures", "17"),
    ("Figure 4: Interactive Streamlit UI Search Dashboard with Skill Gap Analysis and Filter Controls", "14"),
    ("Figure 5: Transparent Risk Detection Engine Displaying Warning Flags, Trigger Terms, and Disclaimers", "19"),
    ("Figure 6: Grounded RAG Match Explanation with Source Chunk Citations [doc_id#c] and Verified Attributes", "18"),
    ("Figure 7: Out-of-Domain Query Abstain Behavior Triggered by Cosine Similarity Guardrail", "18"),
    ("Figure 8: Dual-Column Comparative View Evaluating BM25 Lexical Matching Against Hybrid RRF", "17")
]

for fig_title, page_num in figures:
    add_toc_line(intro_para, fig_title, page_num, is_bold=False)

# 5. LIST OF TABLES
add_toc_heading(intro_para, "List of Tables")

tables = [
    ("Table 1: Standardized Schema of Processed EMSCAD Corpus", "7"),
    ("Table 2: Retrieval Evaluation Results Across All Systems (16 Queries)", "17"),
    ("Table 3: Per-Query Performance Comparison Across Core Queries (q1–q5)", "18"),
    ("Table 4: RAG Explanation Evaluation Across Relevance, Evidence, and Attribution (0–2 Scale)", "18"),
    ("Table 5: Deterministic Guardrail Auditing Statistics (80 Instances)", "18")
]

for tbl_title, page_num in tables:
    add_toc_line(intro_para, tbl_title, page_num, is_bold=False)

# 6. Page break before Introduction
add_page_break(intro_para)

doc.save(DOCX_PATH)
doc.save("reports/tw_report.docx")
print(f"Successfully added Table of Contents, List of Figures, and List of Tables to {DOCX_PATH}")
