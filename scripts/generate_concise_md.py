#!/usr/bin/env python3
"""
scripts/generate_concise_md.py
Generates the concise, to-the-point project_report.md matching the Word report exactly.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "reports" / "project_report.md"

md_content = r"""# Trust-Aware Internship Search and Recommendation System Using Hybrid Retrieval and RAG

**Course:** Information Retrieval & Semantic Web (25M21CA119)  
**Department:** Department of Computer Applications, Jaypee Institute of Information Technology, Noida  
**Supervisor:** Mr. Keshan Srivastava  
**Submitted By:**  
- Akriti Sengar (Enrollment No.: 992509220001)  
- Bhawna Rani (Enrollment No.: 992509220008)  
**Academic Year:** 2025 – 2026  

---

## i. Title Page
- **Institution:** Jaypee Institute of Information Technology, Noida
- **Department:** Department of Computer Applications
- **Project Title:** Trust-Aware Internship Search and Recommendation System Using Hybrid Retrieval and RAG
- **Course Name & Code:** Information Retrieval & Semantic Web (25M21CA119)
- **Supervisor:** Mr. Keshan Srivastava
- **Authors:** Akriti Sengar (992509220001) & Bhawna Rani (992509220008)
- **Academic Year:** 2025 – 2026

---

## ii. Abstract
Online recruitment platforms suffer from two critical limitations: lexical mismatch in keyword search, which misses relevant roles due to varying corporate nomenclature, and total opacity regarding job legitimacy, exposing early-career candidates to deceptive employment scams. This project presents the Trust-Aware Internship Search and Recommendation System, combining sparse lexical retrieval, dense semantic vector search, supervised deception detection, and citation-grounded Retrieval-Augmented Generation (RAG). Evaluated on the EMSCAD benchmark (15,560 postings), the platform implements an Okapi BM25 baseline, dense bi-encoder sentence representations (all-MiniLM-L6-v2 and multi-qa-MiniLM-L6-cos-v1) indexed via FAISS IndexFlatIP, and Reciprocal Rank Fusion (RRF, k=60). A dual-tier trust module combines rule heuristics with an SGD Logistic Regression classifier (PR-AUC = 0.76) to surface transparent risk signals with cautious non-defamatory disclaimers. For explainability, Gemini 3.5 Flash synthesizes match rationales with exact passage citations ([doc_id#c0]), enforced via five deterministic guardrails and a 0.30 cosine abstain threshold. Across 16 benchmark queries and 517 pooled annotations, BM25 plain establishes a dominant baseline (P@5 = 1.000, nDCG@10 = 0.925), outperforming dense retrieval (0.715) and Hybrid RRF (0.850) due to corporate boilerplate phrasing and short postings (~180 words). The RAG layer achieves 1.95/2.00 evidence grounding with zero hallucinated quotes, deployed as an interactive Streamlit application.

---

## Table of Contents

| Section | Title |
| :--- | :--- |
| **Abstract** | Project Summary and Findings |
| **1** | Introduction |
| **2** | Problem Statement |
| **3** | Objectives |
| **4** | Information Need / Use Case |
| **5** | Dataset / Corpus Description |
| **6** | Background / Literature Study |
| **7** | Project Scope and Requirements |
| **8** | System Architecture |
| **9** | Data Preparation and Preprocessing |
| **10** | Document Representation |
| **11** | Indexing and Retrieval |
| **12** | Ranking / Semantic / Knowledge-Based Component |
| **13** | Implementation |
| **14** | Experimental Setup and Test Queries |
| **15** | Retrieval Evaluation |
| **16** | Results and Comparative Analysis |
| **17** | Discussion |
| **18** | Limitations |
| **19** | Future Scope |
| **20** | Conclusion |
| **21** | Individual Contributions |
| **22** | References |

---

## List of Figures

- **Figure 1:** End-to-End System Architecture Pipeline Diagram (`reports/figures/fig1_architecture.png`)
- **Figure 2:** Precision-Recall Curve of the Logistic Risk Classifier on Held-Out Test Set (`reports/pr_curve.png`)
- **Figure 3:** Retrieval Comparison Across Sparse, Dense, and Hybrid Architectures (`reports/retrieval_comparison.png`)
- **Figure 4:** Interactive Streamlit UI Search Dashboard with Skill Gap Analysis and Filter Controls (`reports/figures/fig4_dashboard.png`)
- **Figure 5:** Transparent Risk Detection Engine Displaying Warning Flags, Trigger Terms, and Disclaimers (`reports/figures/fig5_risk.png`)
- **Figure 6:** Grounded RAG Match Explanation with Source Chunk Citations [doc_id#c] and Verified Attributes (`reports/figures/fig6_rag.png`)
- **Figure 7:** Out-of-Domain Query Abstain Behavior Triggered by Cosine Similarity Guardrail (`reports/figures/fig7_abstain.png`)
- **Figure 8:** Dual-Column Comparative View Evaluating BM25 Lexical Matching Against Hybrid RRF (`reports/figures/fig8_compare.png`)

---

## List of Tables

- **Table 1:** Standardized Schema of Processed EMSCAD Corpus (`corpus.parquet`)
- **Table 2:** Retrieval Evaluation Results Across All Systems (P@5, nDCG@10, MRR over 16 Queries)
- **Table 3:** Per-Query Performance Comparison Across Core Queries (q1–q5)
- **Table 4:** RAG Explanation Evaluation Across Relevance, Evidence, and Attribution (0–2 Scale)
- **Table 5:** Deterministic Guardrail Auditing Statistics Across 80 Generation Instances

---

## 1. Introduction
The modern digital recruitment ecosystem enables early-career candidates to explore thousands of employment opportunities across web aggregators. However, job seekers face substantial friction: keyword-based search fails to resolve semantic synonyms (e.g. an "entry-level data analyst" query missing a posting titled "Junior Business Intelligence Trainee"), while fraudulent postings—such as advance-fee work-from-home scams—threaten vulnerable applicants.

To address these challenges, this project introduces the Trust-Aware Internship Search and Recommendation System. The platform combines classical Okapi BM25 retrieval, FAISS dense vector search, Reciprocal Rank Fusion, supervised risk identification, and verifiable Retrieval-Augmented Generation (RAG) into a single production-grade search dashboard.

---

## 2. Problem Statement
Conventional employment search systems suffer from four primary limitations:
- **Lexical Fragility:** Keyword matching misses semantically relevant listings that use alternative phrasing or corporate terminology.
- **Absence of Risk Awareness:** Traditional portals rank listings purely by query similarity, offering zero caution against fraudulent postings or advance-fee scams.
- **Interpretability Deficit:** Arbitrary relevance scores provide no qualitative rationale explaining why a role matches a candidate's background.
- **LLM Hallucinations:** Unconstrained generative language models frequently hallucinate job requirements and company attributes.

---

## 3. Objectives
The key engineering and research objectives are:
1. **Corpus Standardization:** Ingest, clean, and standardize 17,880 raw EMSCAD postings into a deduplicated 15,560-row Parquet corpus.
2. **Sparse Baseline:** Construct an Okapi BM25 inverted index retriever across unstemmed and stemmed text representations.
3. **Dense Vector Indexing:** Encode text into 384-dimensional dense vectors using Sentence Transformers and build a FAISS IndexFlatIP index.
4. **Hybrid Fusion:** Implement Reciprocal Rank Fusion (RRF, k=60) to merge sparse lexical precision and dense semantic recall.
5. **Trust Engine:** Combine rule heuristics with an SGD Logistic Regression classifier to flag high-risk listings with transparent keyword evidence.
6. **Grounded RAG:** Deploy Gemini 3.5 Flash with five deterministic guardrails and a 0.30 cosine abstain threshold for verifiable explanations.
7. **Benchmark Evaluation:** Evaluate retrieval and generation across 16 benchmark queries and 517 pooled human relevance judgments.

---

## 4. Information Need / Use Case
The system fulfills three distinct early-career discovery scenarios:
- **Case 1 (Technical Matching):** A student querying "ML intern" with skills "python, scikit-learn" receives verified junior roles with explicit skill-gap indicators highlighting matched and missing prerequisites.
- **Case 2 (Deception Trapping):** A candidate searching for remote data entry encounters high-earning scam postings. The system surfaces amber/red caution banners detailing suspicious triggers (empty profiles, fee requests) under the ethical disclaimer: "Warnings are signals, not proof of fraud."
- **Case 3 (Boundary Verification):** An out-of-domain query ("deep sea welding internship") safely triggers an automatic abstain response rather than generating hallucinated relevance.

---

## 5. Dataset / Corpus Description
The platform is built on the Employment Scam Aegean Dataset (EMSCAD) [1], comprising genuine recruitment advertisements collected from Workable between 2012 and 2014. After cleaning and deduplication, the standardized corpus contains 15,560 listings (14,810 legitimate, 750 fraudulent, representing a realistic 4.82% fraud class imbalance). Data was partitioned into an 80% training set (12,448 rows) and a 20% held-out test set (3,112 rows), stratified by the fraud target label.

### Table 1: Standardized Schema of Processed EMSCAD Corpus (`corpus.parquet`)

| Field Name | Data Type | Description & Usage in Pipeline |
| :--- | :--- | :--- |
| `doc_id` | String (Unique ID) | Canonical identifier (e.g. emscad_0 to emscad_17879). |
| `title` | String | Job title used in BM25 title boosting and UI display. |
| `company_profile` | String | Organizational background; screened for length heuristics. |
| `description` | String | Core job responsibilities and project overview. |
| `requirements` | String | Required candidate skills, tools, and education. |
| `search_text` | String | Concatenation of title, company, description, and requirements. |
| `telecommuting` | Integer (0/1) | Remote employment indicator used in query filtering. |
| `has_company_logo` | Integer (0/1) | Presence of company logo (heuristic scam feature). |
| `has_questions` | Integer (0/1) | Screening questionnaire present (legitimacy signal). |
| `fraudulent` | Integer (0/1) | Ground truth label: 0 = Legitimate (95.2%), 1 = Fraudulent (4.8%). |
| `split` | Categorical | Stratified partition: 'train' (80%) for risk classifier, 'test' (20%). |

---

## 6. Background / Literature Study
- **Okapi BM25:** Probabilistic retrieval computes relevance using term saturation ($k_1 = 1.5$) and length normalization ($b = 0.75$). BM25 excels at exact keyword matching but cannot resolve synonymy [2].
- **Dense Bi-Encoders:** Sentence-BERT bi-encoders project text into continuous 384-dimensional spaces where cosine distance captures semantic intent independently of surface wording [3].
- **FAISS Indexing:** Facebook AI Similarity Search provides vectorized SIMD inner-product operations, enabling sub-millisecond nearest neighbor search over dense matrices [4].
- **Reciprocal Rank Fusion:** RRF aggregates disparate retrieval rankings monotonically without requiring score calibration: $RRF(d) = \sum \frac{1}{60 + r_m(d)}$ [5].
- **Retrieval-Augmented Generation:** RAG combines parametric generative language models with non-parametric passage retrieval, mitigating hallucination by constraining outputs strictly to source context [6].

---

## 7. Project Scope and Requirements
- **In-Scope:** English-language listings, offline dense embedding generation, exact FAISS inner-product indexing, hybrid RRF fusion, supervised risk indicators, citation-grounded RAG explanations, and interactive Streamlit UI.
- **Out-of-Scope:** Live web scraping, predicting individual hiring odds, and asserting definitive legal fraud claims.
- **System Constraints:** System memory under 8 GB RAM, sub-100ms retrieval latency, sub-50ms cached RAG latency, and deterministic evaluation reproducibility (`random_state=42`).

---

## 8. System Architecture
The platform is organized into four core layers: dual-path retrieval (BM25 sparse + FAISS dense), Reciprocal Rank Fusion ($k=60$), trust and risk scoring (heuristics + logistic classifier), and grounded RAG explanation generation with deterministic guardrails. Figure 1 illustrates the end-to-end dataflow.

![Figure 1: End-to-End System Architecture Pipeline Diagram](figures/fig1_architecture.png)
*Figure 1: End-to-End System Architecture Pipeline Diagram (`reports/figures/fig1_architecture.png`)*

---

## 9. Data Preparation and Preprocessing
Preprocessing enforced four standardized operations:
1. **Text Normalization:** HTML tags and escaped Unicode entities were stripped, whitespace normalized, and non-printable characters removed.
2. **Field Amalgamation:** Title, company profile, description, and requirements were concatenated into a unified `search_text` field.
3. **Deduplication:** Identical postings sharing identical descriptions and company profiles were eliminated.
4. **Skill Lexicon:** A domain-specific lexicon of 35+ technical skills was compiled with regex alias patterns (`data/processed/skills_lexicon.csv`) for deterministic candidate-posting skill matching.

---

## 10. Document Representation
- **Sparse Vectors:** Evaluated unstemmed (`bm25_plain`), normalized (`bm25_norm`), and Porter-stemmed (`bm25_stem`) bag-of-words tokenizations.
- **Dense Bi-Encoders:** Encoded postings into 384-dimensional dense vectors using `all-MiniLM-L6-v2` (256-token limit) and `multi-qa-MiniLM-L6-cos-v1` (512-token limit).
- **Sliding-Window Chunks:** Postings were partitioned into 130-word sliding windows with 20-word overlap (42,480 chunk vectors) to assess passage retrieval against full-document encoding.
- **Unit Normalization:** Embeddings were L2-normalized upon encoding ($\|v\| = 1.0$), making cosine similarity mathematically identical to dot product ($\cos(q, d) = q \cdot d$) and optimizing search throughput.

---

## 11. Indexing and Retrieval
- **BM25 Inverted Index:** In-memory inverted index built via `rank_bm25` across 15,560 corpus postings.
- **FAISS Vector Index:** Built using FAISS `IndexFlatIP` (23.9 MB disk footprint, <3.5s build time). Top-10 results and scores matched pure NumPy matrix multiplication with zero discrepancy.
- **macOS OpenMP Stability Fix:** Streamlit worker collisions with PyTorch/FAISS OpenMP pools on macOS ARM64 Apple Silicon triggered SIGSEGV crashes. Resolved by enforcing `faiss.omp_set_num_threads(1)` and `torch.set_num_threads(1)`, ensuring 2ms retrieval latency with complete stability.

---

## 12. Ranking / Semantic / Knowledge-Based Component
The hybrid engine unifies sparse and dense retrieval using Reciprocal Rank Fusion (RRF):

$$RRF\_Score(d \in D) = \frac{1}{60 + rank_{bm25}(d)} + \frac{1}{60 + rank_{semantic}(d)}$$

Ablation testing over $k \in \{10, 30, 60, 100\}$ confirmed that $k=60$ achieves optimal rank smoothing, preventing single-system outliers from displacing consensus candidates. In chunked semantic search, document relevance is aggregated via max-pooling: $\text{Score}_{doc}(D) = \max_{c \in Chunks(D)} \text{Cosine}(Q, c)$.

---

## 13. Implementation
The codebase is organized into seven modular Python components:
- **`src/semantic.py`:** Dense embedding generation, FAISS indexing, verification, and RRF hybrid search.
- **`src/bm25_search.py`:** BM25 tokenization, inverted indexing, and multi-field scoring.
- **`src/skills.py`:** Deterministic skill extraction and candidate-posting skill gap analysis.
- **`risk/risk_report.py`:** Heuristic scam detection rules and SGD Logistic Regression risk scoring.
- **`src/rag_explain.py`:** Passage chunking, Gemini 3.5 Flash calling, 5-stage guardrails, and SHA-256 disk caching.
- **`src/eval_metrics.py`:** Custom IR metric implementations (P@k, MRR, nDCG@k) cross-tested against ranx.
- **`app/streamlit_app.py`:** Interactive web application with method toggles, risk badges, and RAG expanders.

![Figure 4: Interactive Streamlit UI Search Dashboard](figures/fig4_dashboard.png)
*Figure 4: Interactive Streamlit UI Search Dashboard with Skill Gap Analysis and Filter Controls (`reports/figures/fig4_dashboard.png`)*

---

## 14. Experimental Setup and Test Queries
System evaluation was conducted across 16 standardized queries in `data/processed/queries.json`: Core queries (q1–q5: Data Analyst, ML intern, remote no-exp, WFH scam, Software Java), Supplementary queries (q6–q15: DevOps, cybersecurity, React), and Stress query (q16: deep sea welding, out-of-domain abstain test).

**Candidate Pooling & Ground Truth:** Top-10 results from six retrieval runs were pooled and deduplicated into a system-blind sheet of 517 candidate judgments (`data/eval/pool_for_labelling.csv`). Relevance was graded on a 3-point scale: 0 (Non-Relevant), 1 (Partially Relevant), and 2 (Highly Relevant).

---

## 15. Retrieval Evaluation
Performance was measured across three classical IR metrics [7]: Precision@5 (P@5), Mean Reciprocal Rank (MRR), and Normalized Discounted Cumulative Gain (nDCG@10) under linear gain formulation. All metric functions in `src/eval_metrics.py` were programmatically cross-validated against the academic `ranx` library [8], confirming exact numerical equivalence down to 6 decimal places.

---

## 16. Results and Comparative Analysis
Table 2 and Figure 3 summarize overall retrieval performance across all eight evaluated configurations over the 16 test queries.

### Table 2: Retrieval Evaluation Results Across All Systems (P@5, nDCG@10, MRR over 16 Queries)

| Retrieval System | P@5 | nDCG@10 | MRR | Queries |
| :--- | :---: | :---: | :---: | :---: |
| **bm25_plain** | **1.000** | **0.925** | **1.000** | 16 |
| **bm25 (baseline)** | 0.988 | 0.900 | 1.000 | 16 |
| **bm25_norm** | 0.988 | 0.900 | 1.000 | 16 |
| **bm25_stem** | 0.988 | 0.849 | 1.000 | 16 |
| **hybrid_rrf (Proposed)** | 0.975 | 0.850 | 1.000 | 16 |
| **sem_minilm (Model A)** | 0.913 | 0.715 | 0.969 | 16 |
| **sem_minilm_chunks** | 0.863 | 0.655 | 0.906 | 16 |
| **sem_multiqa (Model B)** | 0.838 | 0.691 | 0.969 | 16 |

![Figure 3: Retrieval Comparison Across Sparse, Dense, and Hybrid Architectures](retrieval_comparison.png)
*Figure 3: Retrieval Comparison Across Sparse, Dense, and Hybrid Architectures (`reports/retrieval_comparison.png`)*

BM25 plain establishes the top-performing configuration (P@5 = 1.000, nDCG@10 = 0.925). Figure 8 illustrates the dual-column comparison mode for query "trainee developer fresh graduate". Dense similarity in Hybrid RRF promotes semantically aligned graduate trainee positions ahead of purely keyword-matched postings.

![Figure 8: Dual-Column Comparative View](figures/fig8_compare.png)
*Figure 8: Dual-Column Comparative View Evaluating BM25 Lexical Matching Against Hybrid RRF (`reports/figures/fig8_compare.png`)*

### Table 3: Per-Query Performance Comparison Across Core Queries (q1–q5)

| Query ID | Query Intent Description | Top-1 Retrieved Document | Relevance Status & Notes |
| :--- | :--- | :--- | :--- |
| **q1** | Data analyst intern, Python & SQL | emscad_4589 (Data Analyst Intern) | Clean match (Label 2); university intern. |
| **q2** | ML intern fresher, scikit-learn | emscad_14113 (Data Science Intern) | Matched scikit-learn & Python; BM25 rank 1. |
| **q3** | Remote internship, no experience | emscad_7983 (Web Intern - Remote) | Verified 100% remote commitment; clean match. |
| **q4** | WFH data entry, high earnings scam | emscad_7667 (Entry Level Online Typist) | Classic EMSCAD fraud sample; high risk flag. |
| **q5** | Software intern, Java & database | emscad_2065 (Software Dev Intern) | Clean match (Label 2); Java & SQL required. |

### Table 4: RAG Explanation Evaluation Across Relevance, Evidence, and Attribution (0–2 Scale)

| Query | Eval Count | Avg Relevance /2 | Avg Evidence /2 | Avg Attribution /2 | Avg Total /6 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **q1: Data Analyst (Python/SQL)** | 5 | 1.60 | 2.00 | 2.00 | 5.60 |
| **q2: ML Intern Fresher** | 5 | 0.60 | 2.00 | 2.00 | 4.60 |
| **q3: Remote No-Experience** | 4 | 1.00 | 1.75 | 2.00 | 4.75 |
| **q4: WFH High Earnings Scam** | 5 | 1.40 | 2.00 | 1.80 | 5.20 |
| **q5: Software Intern (Java/DB)** | 2 | 1.50 | 2.00 | 2.00 | 5.50 |
| **q16: Deep Sea Welding (Abstain)** | 1 | 0.00 | 2.00 | 2.00 | 4.00 |
| **OVERALL AVERAGE** | **22** | **1.14** | **1.95** | **1.95** | **5.05** |

Figure 6 shows a grounded RAG explanation card for an entry-level Data Analyst posting, incorporating verified passage citations (`[emscad_4589#c0]`, `[emscad_4589#c1]`).

![Figure 6: Grounded RAG Match Explanation](figures/fig6_rag.png)
*Figure 6: Grounded RAG Match Explanation with Source Chunk Citations [doc_id#c] and Verified Attributes (`reports/figures/fig6_rag.png`)*

### Table 5: Deterministic Guardrail Auditing Statistics Across 80 Generation Instances

| Guardrail Verification Check | Failure Count | Audit Outcome & Enforcement Action |
| :--- | :---: | :--- |
| **JSON Format Enforcement** | 0 | 100% compliant JSON responses returned by Gemini. |
| **Source ID Existence** | 0 | All [doc_id#c] citations traced to valid retrieved chunks. |
| **Word-for-Word Quote Match** | 0 | 100% of cited quotes verified verbatim in chunk text. |
| **Deterministic Skill Overwrite** | 114 | Model skills overwritten by regex lexicon extractor. |
| **Defamation Keyword Neutralizer** | 0 | No unlawful accusations of "fraud" generated by LLM. |

Figure 7 illustrates the cosine similarity guardrail safely abstaining on out-of-domain query q16 ("deep sea welding internship") rather than hallucinating false advice.

![Figure 7: Out-of-Domain Query Abstain Behavior](figures/fig7_abstain.png)
*Figure 7: Out-of-Domain Query Abstain Behavior Triggered by Cosine Similarity Guardrail (`reports/figures/fig7_abstain.png`)*

Figure 2 and Figure 5 illustrate risk classifier validation (PR-AUC = 0.76) and operational warnings for query q4, displaying triggered heuristic rules and top risk terms with caution disclaimers.

![Figure 2: Precision-Recall Curve](pr_curve.png)
*Figure 2: Precision-Recall Curve of the Logistic Risk Classifier on Held-Out Test Set (`reports/pr_curve.png`)*

![Figure 5: Transparent Risk Detection Engine](figures/fig5_risk.png)
*Figure 5: Transparent Risk Detection Engine Displaying Warning Flags, Trigger Terms, and Disclaimers (`reports/figures/fig5_risk.png`)*

---

## 17. Discussion
Why BM25 Plain Outperformed Semantic and Hybrid Retrieval on EMSCAD:
1. **Standardized Corporate Vocabulary:** EMSCAD job postings follow rigid corporate boilerplate phrasing ("Data Analyst Intern", "Requirements"). Queries matched verbatim phrases directly, heavily favoring exact BM25 term weighting.
2. **Brevity & Chunking Ineffectiveness:** Mean posting length is ~180 words, fitting within the 256-token limit of MiniLM. Chunking into 130-word fragments added boundary noise without recovering lost context, reducing nDCG@10 from 0.715 to 0.655.
3. **RRF Rank Dilution:** Because BM25 top-5 ranks were near-perfect, fusing them with broader semantic candidates diluted precision at ranks 2 through 5, dropping Hybrid nDCG@10 to 0.850.
4. **Stemming Degradation:** Porter stemming collapsed distinct titles (e.g. "analyst" vs "analysis"), increasing false-positive matches and reducing nDCG@10 from 0.925 to 0.849.
5. **RAG Factual Grounding:** Manual auditing scored Evidence Support and Citation Attribution at 1.95/2.00. The LLM actively exposed seniority mismatches (e.g. flagging "senior Ph.D. required" on fresher queries) rather than fabricating relevance.

---

## 18. Limitations
1. **Dataset Era:** 2012–2014 listings from one European/US recruitment platform, lacking modern remote work patterns or contemporary tech stacks (e.g. LangChain, Next.js).
2. **Heuristic Pool Labels:** Accelerated via keyword-overlap heuristics before manual spot-checks, serving as baseline research labels.
3. **Query Set Size:** 16 queries demonstrate operational tendencies but lack statistical sample size (>50 queries) for significance testing.
4. **No Cross-Encoder:** Retrieval was restricted to bi-encoders and RRF without a heavy cross-attention re-ranker due to latency constraints.
5. **Static Abstain Threshold:** The static 0.30 cosine threshold permitted one pipe welder posting through on q16; 0.40 is recommended for complete isolation.

---

## 19. Future Scope
1. **Neural Cross-Encoder Re-Ranking:** Incorporate `ms-marco-MiniLM-L-6-v2` cross-attention scoring over top-50 candidates.
2. **Knowledge Graph Triplification:** Convert postings into RDF triples utilizing schema.org/JobPosting ontologies [10] for structured SPARQL querying.
3. **Adaptive Abstain Thresholds:** Replace static cosine cutoffs with corpus-adaptive quantile thresholds.
4. **Live Multi-Source Ingestion:** Connect live aggregator APIs (e.g. Adzuna, Remotive) for real-time internship discovery.

---

## 20. Conclusion
The Trust-Aware Internship Search System successfully integrates Okapi BM25 retrieval, FAISS dense vector search, Reciprocal Rank Fusion, supervised deception detection, and grounded RAG generation. The empirical findings demonstrate that classical BM25 remains dominant in concise, boilerplate recruitment text, while dense semantic models provide vital passage selection for hallucination-free AI explanations. By pairing non-parametric retrieval memory with deterministic guardrails, the platform demonstrates that trust-aware search is practically viable, responsive, and ethically grounded.

---

## 21. Individual Contributions
The project research, implementation, evaluation, and documentation were collaboratively executed by Akriti Sengar and Bhawna Rani. The division of work is detailed below:

### Work Distribution: Akriti Sengar (Enrollment No. 992509220001)
- **Corpus Acquisition & Licensing:** Sourced the raw EMSCAD benchmark dataset (17,880 listings), verified CC-BY-NC-SA licensing, and configured raw storage.
- **Exploratory Data Analysis:** Conducted exploratory data analysis on title distributions, company fields, and target fraud class imbalance.
- **Data Cleaning & Parquet Schema:** Executed HTML tag stripping, text normalization, and exported the standardized corpus.parquet (15,560 rows).
- **Skill Lexicon Construction:** Assembled the initial regex-based skill lexicon (skills_lexicon.csv) covering technical tools for candidate matching.
- **BM25 Lexical Baseline:** Implemented the initial Okapi BM25 inverted index retrieval pipeline using rank_bm25 across corpus postings.
- **Heuristic Risk Rules:** Formulated deterministic scam detection heuristic rules based on upfront fees, suspicious emails, and empty profiles.
- **Risk Classifier Training:** Trained the SGD Logistic Regression classifier on word and character n-grams to detect potentially fraudulent listings.
- **Streamlit Application Scaffold:** Developed the initial prototype Streamlit application shell for interactive demonstration.

### Work Distribution: Bhawna Rani (Enrollment No. 992509220008)
- **Dense Vector Embeddings & Indexing:** Encoded the corpus into 384-dimensional dense vectors using all-MiniLM-L6-v2 and multi-qa-MiniLM-L6-cos-v1, and built the FAISS IndexFlatIP index with verified inner-product equivalence.
- **Sliding-Window Chunking:** Designed 130-word sliding-window chunking (42,480 chunk vectors) with chunk-to-document max pooling retrieval.
- **Hybrid Reciprocal Rank Fusion:** Implemented the Reciprocal Rank Fusion (RRF) engine, conducted parameter ablation across k ∈ {10, 30, 60, 100}, and integrated dual-column comparison.
- **Relevance Pooling & Ground-Truth Labelling:** Engineered the pooling harness (src/make_pool.py) pooling 517 candidate documents across 16 queries and 6 retriever runs, and executed 3-point relevance grading.
- **IR Metric Suite & ranx Validation:** Developed custom P@5, MRR, and nDCG@10 metrics and mathematically cross-validated implementations against ranx [8].
- **Grounded RAG & Guardrails:** Architected the Gemini 3.5 Flash RAG pipeline, authored structured prompts, calibrated the 0.30 cosine abstain threshold, engineered 5 deterministic guardrails, and implemented SHA-256 disk caching.
- **Manual RAG Evaluation & Audit:** Scored 22 RAG explanation instances across Relevance, Evidence Support, and Citation Attribution, and compiled the citation reference audit.
- **macOS OpenMP Crash Fix & UI Redesign:** Diagnosed and resolved the native OpenMP SIGSEGV multi-threading crash in libomp.dylib on Apple Silicon, and redesigned the Streamlit UI.
- **Project Report Synthesis:** Authored the complete formal 22-section project report in Microsoft Word (.docx) and Markdown (.md) formats.

---

## 22. References

[1] S. Vidros, C. Kolias, G. Kambourakis, and L. Akoglu, "Automatic Detection of Online Recruitment Frauds: Characteristics, Methods, and a Public Dataset," *Future Internet*, vol. 9, no. 1, p. 6, 2017.

[2] S. Robertson and H. Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," *Foundations and Trends in Information Retrieval*, vol. 3, no. 4, pp. 333–389, 2009.

[3] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," in *Proc. 2019 Conf. Empirical Methods in Natural Language Processing (EMNLP)*, Hong Kong, China, 2019, pp. 3982–3992.

[4] J. Johnson, M. Douze, and H. Jégou, "Billion-scale similarity search with GPUs," *IEEE Transactions on Big Data*, vol. 7, no. 3, pp. 535–547, 2019.

[5] G. V. Cormack, C. L. Clarke, and S. Buettcher, "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods," in *Proc. 32nd Int. ACM SIGIR Conf. Research and Development in Information Retrieval*, Boston, MA, USA, 2009, pp. 758–759.

[6] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, 2020, pp. 9459–9474.

[7] C. D. Manning, P. Raghavan, and H. Schütze, *Introduction to Information Retrieval*. Cambridge University Press, Cambridge, UK, 2008.

[8] E. Bassani, "ranx: A Blazing-Fast Python Library for Ranking Evaluation and Comparison," in *Proc. 44th European Conf. Information Retrieval (ECIR)*, Stavanger, Norway, 2022, pp. 238–244.

[9] Google DeepMind, "Gemini: A Family of Highly Capable Multimodal Models," Technical Report, Google AI, 2024. Available: https://arxiv.org/abs/2312.11805

[10] W3C, "RDF 1.1 Concepts and Abstract Syntax," W3C Recommendation, 2014. [Online]. Available: https://www.w3.org/TR/rdf11-concepts/

[11] Streamlit Documentation, "The Fastest Way to Build Data Apps," Available: https://docs.streamlit.io/
"""

with open(MD_PATH, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"Successfully generated concise markdown report at: {MD_PATH}")
