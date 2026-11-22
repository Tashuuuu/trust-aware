#!/usr/bin/env python3
"""
scripts/update_tw_report.py
Applies requested formatting fixes to reports/tw_report.docx:
1. Fixes double bullets in Individual Contributions (removes literal '• ' and bolds titles before colon).
2. Removes empty bullet paragraph P225.
3. Updates in-text citation syntax to IEEE style [1], [2], etc.
4. Rewrites the References section to standard IEEE numbered format [1] - [11] with hanging indents.
"""

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

DOCX_IN = "reports/tw_report.docx"
DOCX_OUT = "reports/Trust_Aware_Internship_Search_ProjectReport.docx"

doc = docx.Document(DOCX_IN)

# -----------------------------------------------------------------------------
# 1. FIX DOUBLE BULLETS IN INDIVIDUAL CONTRIBUTIONS
# -----------------------------------------------------------------------------
# Find the start of Individual Contributions
contrib_idx = None
for i, p in enumerate(doc.paragraphs):
    if "individual contributions" in p.text.lower():
        contrib_idx = i
        break

print(f"Individual Contributions found at paragraph {contrib_idx}")

# Fix paragraphs under contributions
for p in doc.paragraphs[contrib_idx:]:
    if "references" in p.text.lower() and len(p.text.strip()) < 20:
        break # reached references
    
    txt = p.text.strip()
    if p.style.name == "List Bullet":
        if not txt:
            # Empty bullet paragraph (P225) - clear runs and change style to Body
            p.style = "Body"
            p.text = ""
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            continue
        
        # Remove literal bullet if present
        clean_text = txt
        if clean_text.startswith("•"):
            clean_text = clean_text.lstrip("•").strip()
        
        # Parse title before colon and description after colon
        if ":" in clean_text:
            title, desc = clean_text.split(":", 1)
            title = title.strip() + ":"
            desc = desc # keep leading space
        else:
            title = ""
            desc = clean_text
        
        # Clear existing runs
        p.text = ""
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        if title:
            r_title = p.add_run(title)
            r_title.font.name = "Times New Roman"
            r_title.font.size = Pt(12)
            r_title.font.bold = True
        
        r_desc = p.add_run(desc)
        r_desc.font.name = "Times New Roman"
        r_desc.font.size = Pt(12)
        r_desc.font.bold = False

# -----------------------------------------------------------------------------
# 2. UPDATE IN-TEXT CITATIONS TO IEEE STYLE [1], [2], ETC.
# -----------------------------------------------------------------------------
replacements = [
    ("(Vidros et al., 2017)", "[1]"),
    ("Robertson and Zaragoza (2009)", "Robertson and Zaragoza [2]"),
    ("(Reimers & Gurevych, 2019)", "[3]"),
    ("(Johnson et al., 2019)", "[4]"),
    ("Cormack, Clarke, and Buettcher (SIGIR 2009)", "Cormack, Clarke, and Buettcher [5]"),
    ("Lewis et al. (NeurIPS 2020)", "Lewis et al. [6]"),
    ("standard academic ranx library, verifying", "standard academic ranx library [8], verifying"),
    ("schema.org/JobPosting ontologies, enabling", "schema.org/JobPosting ontologies [10], enabling")
]

for p in doc.paragraphs:
    # Only replace in body paragraphs before References
    if "references" in p.text.lower() and len(p.text.strip()) < 20:
        break
    for target, rep in replacements:
        if target in p.text:
            # Replace in full paragraph text while preserving runs
            full_txt = p.text
            new_txt = full_txt.replace(target, rep)
            # Rebuild runs cleanly
            # Check if paragraph had bold prefix
            first_run_bold = p.runs[0].bold if p.runs else False
            p.text = new_txt
            p.runs[0].font.name = "Times New Roman"
            p.runs[0].font.size = Pt(12)
            print(f"Replaced citation: '{target}' -> '{rep}'")

# -----------------------------------------------------------------------------
# 3. REWRITE REFERENCES SECTION IN IEEE NUMBERED FORMAT [1] - [11]
# -----------------------------------------------------------------------------
ref_idx = None
for i, p in enumerate(doc.paragraphs):
    if p.text.strip().lower() == "references":
        ref_idx = i
        break

print(f"References heading found at paragraph {ref_idx}")

# Format References heading
p_ref_head = doc.paragraphs[ref_idx]
p_ref_head.style = "Body"
p_ref_head.text = "References"
p_ref_head.paragraph_format.space_before = Pt(16)
p_ref_head.paragraph_format.space_after = Pt(8)
r_rh = p_ref_head.runs[0]
r_rh.font.name = "Times New Roman"
r_rh.font.size = Pt(16)
r_rh.font.bold = True
r_rh.font.color.rgb = RGBColor(31, 78, 121)

ieee_references = [
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

# Update existing reference paragraphs (P238 - P247)
existing_ref_paras = doc.paragraphs[ref_idx + 1:]

for i, ref_text in enumerate(ieee_references):
    if i < len(existing_ref_paras):
        p = existing_ref_paras[i]
    else:
        p = doc.add_paragraph()
    
    p.style = "Body"
    p.text = ref_text
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.first_line_indent = Inches(-0.4)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    for r in p.runs:
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)

# Save output
doc.save(DOCX_OUT)
doc.save("reports/tw_report.docx")
print(f"Successfully saved updated reports to {DOCX_OUT} and reports/tw_report.docx")
