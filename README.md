# Trust-Aware Internship Search & Recommendation System

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Streamlit-1.42.0-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Retrieval](https://img.shields.io/badge/BM25%20%2B%20FAISS-Dense%20Retrieval-00599C)](https://github.com/facebookresearch/faiss)
[![Generative%20AI](https://img.shields.io/badge/Google%20GenAI-Gemini%203.5%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Tests](https://img.shields.io/badge/Pytest-18%20Passed-brightgreen)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/Dataset-EMSCAD%20(CC--BY--NC--SA)-blue)](https://zenodo.org/record/1045233)

> **Course:** Information Retrieval & Semantic Web (25M21CA119)  
> **Department:** Department of Computer Applications, Jaypee Institute of Information Technology (JIIT), Noida  
> **Supervisor:** Mr. Keshan Srivastava  
> **Authors:** Bhawna Rani (Enrollment No.: 992509220008) & Akriti Sengar (Enrollment No.: 992509220001)

---

## 📌 Overview

The **Trust-Aware Internship Search and Recommendation System** is an end-to-end information retrieval and decision-support platform designed to address two systemic vulnerabilities in digital early-career recruitment:

1. **Vocabulary Mismatch & Lexical Fragility:** Traditional keyword search engines rely exclusively on surface-level term overlaps. When recruiters advertise an internship using alternative corporate nomenclature (e.g., *"Junior Associate"*, *"Graduate Trainee"*, or *"Analytics Apprentice"*), keyword matching produces severe false negatives.
2. **Deception and Scam Blindness:** Conventional job boards rank documents purely on text similarity without evaluating listing legitimacy. Inexperienced applicants querying remote or data entry positions are routinely channeled into predatory advance-fee scams, fake remote jobs, and credential-harvesting schemes.

To resolve these challenges, our platform integrates:
- **Dual-Path Hybrid Retrieval:** Sparse lexical search (Okapi BM25) and dense bi-encoder vector search (`all-MiniLM-L6-v2` via FAISS `IndexFlatIP`).
- **Rank-Based Hybrid Fusion:** Reciprocal Rank Fusion (RRF, $k=60$) combining keyword precision with semantic synonymy without score distortion.
- **Two-Tier Trust Engine:** Deterministic heuristic pattern rules + an SGD Logistic Regression classifier (PR-AUC = 0.76) providing transparent warning signals under the ethical stance: *"Warnings are signals, not proof of fraud."*
- **Citation-Grounded RAG:** Google Gemini 3.5 Flash synthesizes verifiable match explanations with exact passage citations (`[doc_id#c0]`), protected by **five deterministic guardrails** and an objective **$0.30$ cosine abstain gate** to eliminate hallucinations.

---

## 🏗️ System Architecture

```
                                  [ User Query & Profile Skills ]
                                                 │
                   ┌─────────────────────────────┴─────────────────────────────┐
                   ▼                                                           ▼
         [ Sparse Path: BM25 ]                                      [ Dense Path: FAISS ]
       Multi-field tokenization                                    all-MiniLM-L6-v2 (384-d)
         (Title 3x, SearchText)                                     IndexFlatIP Inner Product
                   │                                                           │
                   ▼                                                           ▼
         Top-100 Lexical Ranks                                      Top-100 Semantic Ranks
                   └─────────────────────────────┬─────────────────────────────┘
                                                 ▼
                                     [ Reciprocal Rank Fusion ]
                                        RRF Score, k = 60
                                                 │
                                                 ▼
                                     Top-K Candidate Postings
                                                 │
                   ┌─────────────────────────────┴─────────────────────────────┐
                   ▼                                                           ▼
         [ Risk Engine ]                                             [ Grounded RAG ]
    Tier 1: Heuristic Pattern Rules                            Retrieve Top-2 Passage Chunks
    Tier 2: SGD Logistic Classifier                              Gemini 3.5 Flash Generation
    Flag Amber/Red Caution Badges                               5 Deterministic Guardrails
                                                                 Cosine Abstain Check (<0.30)
                   └─────────────────────────────┬─────────────────────────────┘
                                                 ▼
                             [ Streamlit Interactive User Dashboard ]
                             - Dual-Column Comparison (BM25 vs RRF)
                             - Candidate Skill Gap Analysis
                             - Grounded Match Explanations with Citations
```

---

## ⚡ Quickstart Guide (Local Installation)

Follow these steps to clone and run the application locally on your machine.

### 1. Prerequisites
- **Python:** 3.10, 3.11, or 3.12 (Python 3.12 recommended).
- **RAM:** Minimum 8 GB recommended.
- **OS:** macOS (Apple Silicon / Intel), Linux, or Windows (WSL recommended).

### 2. Clone Repository
```bash
git clone https://github.com/Tashuuuu/trust-aware.git
cd trust-aware
```

### 3. Create & Activate Virtual Environment
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (Command Prompt)
python -m venv .venv
.venv\Scripts\activate.bat
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure API Keys
Copy the template or create a `.env` file in the project root:
```bash
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```
*(Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey). If no key is provided, search, filtering, and risk detection work 100% locally; RAG explanations will load pre-computed benchmark answers or gracefully abstain).*

### 6. Run the Test Suite
Verify that your local environment is correctly configured:
```bash
pytest tests/
```
*Expected result:* **`18 passed in ~13s`**.

### 7. Launch the Interactive Dashboard
```bash
streamlit run app/streamlit_app.py
```
Open your browser and navigate to **`http://localhost:8501`**.

---

## 🧪 Live Demo Walkthrough Scenarios

When evaluating or demonstrating the system, test these four standardized scenarios:

| Scenario | Search Query | User Skills | Method & Options | Expected Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **A. Technical Match & Skill Gap** | `entry-level data analyst internship requiring Python and SQL` | `python, sql` | **Hybrid**, Show AI Explanations ON | Ranks `Data Analyst Intern` (`emscad_4589`) at Rank 1. Shows green matching skill badges and RAG rationale with passage citations (`[emscad_4589#c0]`). |
| **B. Deception Trapping** | `work from home data entry role promising high earnings with no experience` | `data entry` | **BM25**, Show Risk ON | Surfaces high-risk fraudulent postings with dark red warning banners (`Risk: high (model 0.98)`), flags suspicious triggers (empty profile, fees), and displays the caution disclaimer. |
| **C. Anti-Hallucination Abstain Gate** | `deep sea welding internship` | `welding` | **Semantic**, Show AI Explanations ON | Out-of-domain query triggers the 0.30 cosine abstain gate. UI shows: `ℹ️ Explanation Abstained: Insufficient evidence in this posting to match the query above the threshold`. |
| **D. Dual-Column Comparison** | `trainee developer fresh graduate` | *None* | Toggle **Compare BM25 vs Hybrid** ON | Displays synchronized side-by-side comparison. Hybrid RRF elevates semantically aligned postings (`Engineering Graduate Trainee @ Upstream`) above purely keyword-matched postings. |

---

## 📊 Benchmark Evaluation Results

The retrieval pipeline was evaluated across **16 standardized search queries** and **517 pooled human relevance judgments** graded on a 3-point scale ($0 = \text{Non-Relevant}, 1 = \text{Partially Relevant}, 2 = \text{Highly Relevant}$) following the TREC pooling methodology:

| Retrieval System | P@5 | nDCG@10 | MRR | Key Finding |
| :--- | :---: | :---: | :---: | :--- |
| **`bm25_plain` (Unstemmed)** | **1.000** | **0.925** | **1.000** | **Top Performer:** Standardized boilerplate vocabulary heavily favors exact term weighting. |
| **`bm25` (Baseline)** | 0.988 | 0.900 | 1.000 | Robust baseline across all 16 queries. |
| **`bm25_norm` (Lowercased)** | 0.988 | 0.900 | 1.000 | Numerically equivalent to baseline. |
| **`bm25_stem` (Porter Stemming)** | 0.988 | 0.849 | 1.000 | Stemming collapsed distinct terms (*analysis* vs *analyst*), increasing false positives. |
| **`hybrid_rrf` (Proposed Hybrid)** | 0.975 | 0.850 | 1.000 | Preserves high precision at Rank 1; slight rank dilution at ranks 2–5. |
| **`sem_minilm` (Model A, Doc-level)**| 0.913 | 0.715 | 0.969 | Strong semantic recall, but retrieved generic junior developer postings. |
| **`sem_minilm_chunks` (Chunk-level)**| 0.863 | 0.655 | 0.906 | 130-word chunking added boundary noise without recovering lost context. |
| **`sem_multiqa` (Model B)** | 0.838 | 0.691 | 0.969 | Trained on Q&A pairs; less effective for concise keyword intent. |

> **Key Academic Insight:** BM25 plain outperformed dense semantic retrieval because EMSCAD postings are short (average ~180 words) and follow rigid corporate templates. Dense retrieval proved critical not for primary ranking, but for **passage chunk selection** and **grounded RAG explanation synthesis**.

---

## 🛠️ Complete Pipeline Reproduction (Step-by-Step)

If you wish to rebuild the indexes, embeddings, and models from scratch:

```bash
# 1. Preprocess raw EMSCAD data and create standardized Parquet corpus
python -m src.build_corpus

# 2. Extract technical skill lexicon and compile query definitions
python -m src.make_queries
python -m src.skills

# 3. Build Okapi BM25 inverted index
python -m src.bm25_search

# 4. Generate dense vector embeddings and build FAISS IndexFlatIP indexes
python -m src.semantic

# 5. Evaluate heuristic risk rules and train SGD Logistic Regression classifier
python -m risk.eval_rules
python -m risk.train_classifier
python -m risk.risk_report

# 6. Execute pooling harness, format qrels, and run IR evaluation
python -m src.make_pool
python -m src.make_qrels
python -m src.eval_metrics
```

---

## 📁 Repository Structure

```
trust-aware/
├── app/
│   └── streamlit_app.py          # Production Streamlit UI (dual-column, risk, RAG)
├── data/
│   ├── eval/                     # Relevance pooling sheets (517 judged pairs) & qrels.json
│   ├── processed/                # Standardized corpus.parquet (15,560 rows) & queries.json
│   └── raw/                      # Raw EMSCAD source records (CC-BY-NC-SA)
├── docs/                         # Architecture decisions, B-task logs, and coverage reports
├── explanation.md                # 7,500+ word comprehensive viva and technical guide
├── index/                        # FAISS binary indexes, NumPy embeddings, and doc ID arrays
├── rag/
│   ├── answers.json              # Pre-computed guardrail-audited RAG answers
│   ├── cache/                    # SHA-256 hashed disk cache for LLM API calls
│   └── prompts/explain_v1.txt    # Structured prompt template with citation guidelines
├── reports/
│   ├── Trust_Aware_Internship_Search_ProjectReport.docx  # Formal 22-section academic Word report
│   ├── project_report.md         # Full Markdown mirror of formal project report
│   └── figures/                  # High-res 300 DPI architecture diagram & UI screenshots
├── risk/
│   ├── rules.py                  # Deterministic heuristic pattern rules (fees, emails, company)
│   ├── train_classifier.py      # SGD Logistic Regression risk classifier training script
│   └── risk_report.py            # Combined risk scoring engine
├── scripts/
│   ├── build_concise_report.py   # Word report compiler with dot-leader TOC and figures
│   ├── generate_architecture_diagram.py # Matplotlib script generating 300 DPI Figure 1
│   └── generate_concise_md.py    # Markdown report synchronization script
├── src/
│   ├── bm25_search.py            # Okapi BM25 sparse inverted index with 3x title boosting
│   ├── build_corpus.py           # HTML stripping, deduplication, and Parquet exporter
│   ├── eval_metrics.py           # Custom P@k, MRR, nDCG@k suite verified against ranx
│   ├── rag_explain.py            # Gemini 3.5 Flash RAG generator with 5 deterministic guardrails
│   ├── semantic.py               # Dense bi-encoder embeddings, FAISS indexing, and RRF (k=60)
│   └── skills.py                 # Regex skill extraction and profile gap analyzer
├── tests/
│   ├── test_corpus.py            # Corpus integrity and schema validation tests
│   ├── test_pipeline.py          # Dual-path retrieval and RRF verification tests
│   └── test_rules.py             # Heuristic deception rule unit tests
├── requirements.txt              # Pinned Python package dependencies
└── pytest.ini                    # Pytest configuration file
```

---

## 🛡️ Deterministic Guardrails & Safety Architecture

In safety-critical domains like employment search, unconstrained LLM generation creates legal and ethical hazards. Our RAG module (`src/rag_explain.py`) enforces **five deterministic post-processing guardrails**:

1. **Strict JSON Schema:** Forced via Gemini `response_mime_type="application/json"`.
2. **Citation Verification:** Every `[doc_id#c0]` citation is programmatically validated against retrieved chunks.
3. **Word-for-Word Quote Matching:** Quotes generated by the LLM are checked against source passage text; unsupported claims are discarded.
4. **Deterministic Skill Overwrites:** The model's proposed skills are overwritten with ground-truth regex lexicon extractions from `src/skills.py`.
5. **Defamation Neutralization:** Unlawful accusations of *"fraud"* or *"scam"* are intercepted and replaced with standard caution notices.
6. **Cosine Similarity Abstain Gate:** Queries with maximum chunk similarity $< 0.30$ are blocked from LLM inference, returning `insufficient_evidence: true`.

---

## ⚖️ Ethical Considerations & Disclaimers

- **Non-Defamatory Framing:** Automated machine learning models produce statistical warning signals, not legal judgments. The user interface prominently displays:  
  > *"Warnings are signals, not proof of fraud."*
- **Algorithmic Transparency:** Users are shown the specific trigger terms (e.g. *"money, wire transfer, data entry"*) and heuristic rules that raised a posting's risk score.
- **Privacy First:** Profile skills and queries are processed in-memory and are never stored or sold to third-party tracking services.

---

## 👥 Authors & Academic Attribution

This project was developed for **Information Retrieval & Semantic Web (25M21CA119)** at **Jaypee Institute of Information Technology (JIIT), Noida**:

- **Bhawna Rani** (Enrollment No.: `992509220008`): Dense vector embeddings, FAISS vector indexing, Reciprocal Rank Fusion, TREC candidate pooling, IR metric implementation & ranx validation, Gemini 3.5 Flash RAG with 5 guardrails, macOS OpenMP stability engineering, and academic report authorship.
- **Akriti Sengar** (Enrollment No.: `992509220001`): EMSCAD corpus acquisition, exploratory data analysis, data cleaning & Parquet export, skill lexicon construction, BM25 baseline implementation, heuristic risk rules, and initial Streamlit scaffold.
- **Project Supervisor:** Mr. Keshan Srivastava, Department of Computer Applications, JIIT Noida.

### References
- S. Vidros, C. Kolias, G. Kambourakis, and L. Akoglu, *"Automatic Detection of Online Recruitment Frauds: Characteristics, Methods, and a Public Dataset,"* Future Internet, vol. 9, no. 1, p. 6, 2017.
- S. Robertson and H. Zaragoza, *"The Probabilistic Relevance Framework: BM25 and Beyond,"* Foundations and Trends in Information Retrieval, vol. 3, no. 4, pp. 333–389, 2009.
- G. V. Cormack, C. L. Clarke, and S. Buettcher, *"Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,"* in Proc. ACM SIGIR, 2009, pp. 758–759.
- P. Lewis et al., *"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,"* in NeurIPS, vol. 33, 2020, pp. 9459–9474.
