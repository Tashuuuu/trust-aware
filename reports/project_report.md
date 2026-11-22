# Trust-Aware Internship Search and Recommendation System Using Hybrid Retrieval and RAG

**Course:** Information Retrieval & Semantic Web (25M21CA119)  
**Department:** Department of Computer Applications, Jaypee Institute of Information Technology, Noida  
**Supervisor:** Mr. Keshan Srivastava  
**Submitted By:**  
- Bhawna Rani (Enrollment No.: 992509220008)  
- Akriti Sengar (Enrollment No.: 992509220001)  
**Academic Year:** 2025 – 2026  

---

## i. Title Page
- **Institution:** Jaypee Institute of Information Technology, Noida
- **Department:** Department of Computer Applications
- **Project Title:** Trust-Aware Internship Search and Recommendation System Using Hybrid Retrieval and RAG
- **Course Name & Code:** Information Retrieval & Semantic Web (25M21CA119)
- **Supervisor:** Mr. Keshan Srivastava
- **Authors:** Bhawna Rani (992509220008) & Akriti Sengar (992509220001)
- **Date of Submission:** November 23, 2026

---

## ii. Abstract
Online employment and internship search platforms serve as crucial entry points for students, recent graduates, and entry-level job seekers navigating early career transitions. However, conventional job search systems suffer from two fundamental deficiencies: (1) lexical fragility in classical keyword retrieval, which fails to capture semantic synonymy and contextual nuance across varying job descriptions, and (2) complete opacity regarding listing legitimacy, leaving vulnerable candidates exposed to deceptive postings, high-risk work-from-home scams, and predatory recruitment schemes. This project designs, implements, and rigorously evaluates the **Trust-Aware Internship Search and Recommendation System**, an end-to-end framework integrating multi-stage information retrieval, supervised risk identification, and grounded Retrieval-Augmented Generation (RAG).

The system operates on the standardized EMSCAD benchmark corpus comprising 15,560 verified employment postings. Retrieval is executed across multiple paradigms: a classical Okapi BM25 sparse baseline, dense bi-encoder semantic retrieval using Sentence Transformers (`all-MiniLM-L6-v2` and `multi-qa-MiniLM-L6-cos-v1`) indexed via FAISS inner product space, and a rank-based Hybrid Reciprocal Rank Fusion (RRF, $k=60$) mechanism. Risk signal assessment is implemented using a transparent multi-tier architecture combining deterministic heuristic rules and a supervised logistic risk classifier, delivering explicit warning indicators under the ethical stance that warnings represent caution signals rather than legal fraud claims. To solve interpretability, a grounded RAG explanation module powered by Gemini 3.5 Flash synthesizes verifiable match justifications accompanied by exact passage citations (`[doc_id#c0]`), enforced through five deterministic guardrails and a calibrated cosine abstain threshold (0.30) to eliminate hallucinations.

Empirical evaluation conducted across 16 standardized search queries and 517 pooled human-annotated documents demonstrates that BM25 plain establishes a dominant baseline (P@5 = 1.000, nDCG@10 = 0.925, MRR = 1.000), outperforming both dense semantic search (P@5 = 0.913, nDCG@10 = 0.715) and Hybrid RRF (P@5 = 0.975, nDCG@10 = 0.850). Error analysis reveals that the rigid boilerplate vocabulary and concise length (~180 words) of EMSCAD job ads heavily reward exact phrase matching while penalizing rank dilution from dense semantic false positives on specialized queries. In generation, manual auditing of 22 RAG instances reveals exceptional factual grounding (Evidence Support = 1.95/2.00, Citation Attribution = 1.95/2.00) with zero hallucinated quotes. The complete architecture is deployed as an interactive Streamlit dashboard.

---

## Table of Contents

| Section | Title | Page |
| :--- | :--- | :--- |
| **ii** | Abstract | 2 |
| **TOC** | Table of Contents | 3 |
| **LOF** | List of Figures | 4 |
| **LOT** | List of Tables | 4 |
| **iii** | Introduction | 5 |
| **iv** | Problem Statement | 5 |
| **v** | Objectives | 6 |
| **vi** | Information Need / Use Case | 6 |
| **vii** | Dataset / Corpus Description | 7 |
| **viii** | Background / Literature Study | 8 |
| **ix** | Project Scope and Requirements | 9 |
| **x** | System Architecture | 10 |
| **xi** | Data Preparation and Preprocessing | 11 |
| **xii** | Document Representation | 12 |
| **xiii** | Indexing and Retrieval | 12 |
| **xiv** | Ranking / Semantic / Knowledge-Based Component | 13 |
| **xv** | Implementation | 14 |
| **xvi** | Experimental Setup and Test Queries | 15 |
| **xvii** | Retrieval Evaluation | 16 |
| **xviii** | Results and Comparative Analysis | 17 |
| **xix** | Discussion | 20 |
| **xx** | Limitations | 21 |
| **xxi** | Future Scope | 21 |
| **xxii** | Conclusion | 22 |
| **xxiii** | Individual Contributions | 23 |
| | *Work Distribution: Akriti Sengar (992509220001)* | 23 |
| | *Work Distribution: Bhawna Rani (992509220008)* | 23 |
| **xxiv** | References | 24 |

---

## List of Figures

- **Figure 1:** End-to-End System Architecture Pipeline Diagram *(Page 10)*
- **Figure 2:** Precision-Recall Curve of the Logistic Risk Classifier on Held-Out Test Set *(Page 19)*
- **Figure 3:** Retrieval Comparison Across Sparse, Dense, and Hybrid Architectures *(Page 17)*
- **Figure 4:** Interactive Streamlit UI Search Dashboard with Skill Gap Analysis and Filter Controls *(Page 14)*
- **Figure 5:** Transparent Risk Detection Engine Displaying Warning Flags, Trigger Terms, and Disclaimers *(Page 19)*
- **Figure 6:** Grounded RAG Match Explanation with Source Chunk Citations `[doc_id#c]` and Verified Attributes *(Page 18)*
- **Figure 7:** Out-of-Domain Query Abstain Behavior Triggered by Cosine Similarity Guardrail *(Page 18)*
- **Figure 8:** Dual-Column Comparative View Evaluating BM25 Lexical Matching Against Hybrid RRF *(Page 17)*

---

## List of Tables

- **Table 1:** Standardized Schema of Processed EMSCAD Corpus *(Page 7)*
- **Table 2:** Retrieval Evaluation Results Across All Systems (16 Queries) *(Page 17)*
- **Table 3:** Per-Query Performance Comparison Across Core Queries (q1–q5) *(Page 18)*
- **Table 4:** RAG Explanation Evaluation Across Relevance, Evidence, and Attribution (0–2 Scale) *(Page 18)*
- **Table 5:** Deterministic Guardrail Auditing Statistics (80 Instances) *(Page 18)*

---

## iii. Introduction
The modern digital recruitment ecosystem has democratized job hunting, enabling students and early-career professionals to browse thousands of internship and entry-level employment opportunities across diverse web portals. Despite this technological proliferation, navigating recruitment listings remains fraught with cognitive friction, information asymmetry, and substantial security risks. Job seekers, particularly undergraduate students and freshers, frequently struggle to formulate exact keyword queries that match disparate corporate taxonomies. A query for an "entry-level data analyst internship" might miss exceptionally well-matched postings titled "Junior Business Intelligence Trainee" or "Analytics Associate" when evaluated strictly through traditional lexical search engines.

Compounding this discovery challenge is the alarming rise of employment scams, fake job postings, and predatory recruitment operations. Fraudulent actors exploit the eagerness of inexperienced job seekers by advertising fraudulent work-from-home data entry roles, high-paying typist gigs, and fake remote internships designed to harvest personal credentials, advance-fee payments, or uncompensated labor. Conventional search engines and job boards prioritize ranking relevance while treating document content as benign, offering zero warning mechanisms to caution users before they apply or submit confidential resumes.

To resolve these intertwined challenges, this project introduces the **Trust-Aware Internship Search and Recommendation System**. Designed within the intersection of modern Information Retrieval (IR) and Natural Language Processing (NLP), the system establishes a multi-tiered pipeline that unifies classical probabilistic retrieval, dense vector similarity search, supervised risk detection, and verifiable Retrieval-Augmented Generation (RAG).

---

## iv. Problem Statement
Conventional employment search architectures and academic IR baselines suffer from four core technical and functional limitations:
1. **Lexical Brittleness and Vocabulary Mismatch:** Keyword-based inverted index retrieval algorithms (such as TF-IDF and BM25) rely exclusively on surface-level term overlaps. When recruiters employ non-standard nomenclature, lexical retrieval suffers from severe false negatives and low recall.
2. **Absence of Deception and Risk Awareness:** Commercial job boards rank documents strictly on text-query similarity with zero safety layer to detect deceptive signals, such as advance fee collection or unrealistic compensation.
3. **Interpretability Deficit:** Traditional search systems return ranked title lists and arbitrary similarity scores that provide no actionable semantic reasoning explaining why a role fits a candidate's profile.
4. **Hallucination Vulnerability in Generative LLMs:** While LLMs can synthesize explanations, ungrounded conversational agents frequently hallucinate requirements or invent fictitious company details.

---

## v. Objectives
1. **Corpus Curation and Standardization:** Ingest, clean, and standardize the raw EMSCAD dataset into a high-integrity benchmark corpus of 15,560 verified postings.
2. **Classical Baseline Implementation:** Build an Okapi BM25 sparse inverted index retrieval engine across unstemmed, normalized, and Porter-stemmed token representations.
3. **Dense Semantic Vector Indexing:** Formulate dense bi-encoder sentence representations using Sentence Transformers (`all-MiniLM-L6-v2` and `multi-qa-MiniLM-L6-cos-v1`) and construct exact inner-product vector indexes using FAISS.
4. **Hybrid Rank Fusion Architecture:** Implement and calibrate a Reciprocal Rank Fusion (RRF) algorithm to combine disparate sparse and dense rank lists without score calibration biases.
5. **Transparent Trust-Aware Risk Detection:** Engineer a dual-tier safety module incorporating deterministic heuristic pattern rules alongside a supervised machine learning risk classifier.
6. **Grounded RAG Explanations with Guardrails:** Deploy a Gemini 3.5 Flash explanation generator with five deterministic guardrails (citation verification, exact quote checking, deterministic skill overwrites, defamation neutralization, and cosine abstain filtering).
7. **Empirical Evaluation and Error Analysis:** Conduct systematic multi-system IR benchmarking across 16 standardized queries and 517 pooled human annotations using Precision@5, MRR, and nDCG@10, validated against standard IR libraries (`ranx`).

---

## vi. Information Need / Use Case
- **Target Persona:** Computer Science undergraduate / fresher seeking entry-level technical internships.
- **Case A: Legitimate Specialized Technical Discovery:** An undergraduate candidate searches \"entry-level data analyst internship requiring Python and SQL\" alongside personal profile skills `{{python, sql}}`. The candidate requires postings that strictly match internship-level responsibilities, specify technical requirements, highlight profile skill overlap, and verify that the hiring organization is legitimate.
- **Case B: Vulnerable Deception and Scam Trapping:** An inexperienced candidate searches \"work-from-home data entry role promising high earnings with no experience\". The system must retrieve matching postings, immediately flag severe warning signals (e.g. \"guarantees up to six-figure salary\"), and explain via RAG that the earnings claims exhibit established high-risk fraud characteristics.
- **Case C: Out-of-Domain Boundary Verification:** A candidate searches for an intentionally unrepresented query: \"deep sea welding internship\". The system triggers an abstain mechanism, returning \"insufficient evidence\" to preserve user trust.

---

## vii. Dataset/Corpus Description
The primary dataset utilized is the **Employment Scam Aegean Dataset (EMSCAD)** (Vidros et al., 2017). After cleaning and deduplication, the finalized corpus consists of **15,560 postings** stored in Apache Parquet format. Exactly 751 postings (4.82%) are labeled fraudulent.

### Table 1: EMSCAD Corpus Characteristics and Preprocessed Feature Schema
| Field Name | Data Type | Operational Description & Usage |
| :--- | :--- | :--- |
| `doc_id` | String (PK) | Unique document identifier (e.g. `emscad_4589`) mapped across all indexes. |
| `title` | String | Cleaned job title (e.g. 'Data Analyst Intern'). |
| `company_profile` | String | Background overview of the hiring company (used in search text). |
| `search_text` | String (Text) | Concatenation of title, company profile, description, and requirements. |
| `location` | String | Geographical placement (Country, State, City). |
| `employment_type` | Categorical | Employment classification (Full-time, Part-time, Internship, Contract). |
| `required_experience`| Categorical | Seniority level (Entry level, Internship, Mid-Senior, Executive). |
| `skills` | Array<String> | Extracted skills using deterministic regex lexicon matching. |
| `fraudulent` | Integer (0/1) | Ground truth label: 0 = Legitimate (95.2%), 1 = Fraudulent (4.8%). |
| `split` | Categorical | Stratified partition: 'train' (80%) for risk classifier, 'test' (20%). |

---

## viii. Background / Literature Study
- **Okapi BM25:** Probabilistic relevance framework (Robertson & Zaragoza, 2009) incorporating term frequency saturation and document length normalization.
- **Dense Bi-Encoders:** Sentence-BERT architectures (Reimers & Gurevych, 2019) projecting queries and documents into continuous 384-dimensional spaces where cosine similarity measures conceptual alignment.
- **FAISS Vector Indexing:** Fast inner-product vector indexing (Johnson et al., 2019) enabling sub-millisecond retrieval.
- **Reciprocal Rank Fusion (RRF):** Cormack, Clarke & Buettcher (SIGIR 2009) established rank-based fusion:
  $$RRF\\_Score(d) = \\sum_{m \\in M} \\frac{{1}}{{k + r_m(d)}}$$
- **Retrieval-Augmented Generation (RAG):** Lewis et al. (NeurIPS 2020) demonstrated combining retrieval memory with generative language models.

---

## ix. Project Scope and Requirements
- **In-Scope:** English-language postings, offline vector embeddings, exact vector indexing, RRF fusion, supervised risk indicators with transparent term attribution, grounded RAG explanations, interactive Streamlit UI.
- **Out-of-Scope:** Live web scraping, predicting individual hiring probability, asserting definitive legal fraud (\"warnings are signals, not proof of fraud\").
- **System Constraints:** Memory < 8 GB RAM, sub-second query latency (<100 ms retrieval, <50 ms cached RAG), fully reproducible seed configuration (`random_state=42`).

---

## x. System Architecture

The Trust-Aware Internship Search System is structured as a multi-stage modular pipeline comprising four core operational layers: Retrieval, Trust/Risk Scoring, Explanation Generation, and Interface Presentation.

![Figure 1: End-to-End System Architecture Pipeline Diagram](figures/fig1_architecture.png)  
*Figure 1: End-to-End System Architecture Pipeline Diagram.*

---

## xi. Data Preparation and Preprocessing
1. **HTML Stripping & Text Normalization:** Stripped HTML tags, decoded entities, and normalized whitespace.
2. **Field Amalgamation:** Created `search_text` by concatenating title, company profile, description, and requirements.
3. **Deduplication:** Merged duplicate listings sharing identical requirements and company profiles.
4. **Stratified Splitting:** 80% train (12,448) and 20% test (3,112), preserving 4.82% fraud proportion.
5. **Skill Lexicon:** Built regex alias mapping for 35+ core skills (`data/processed/skills_lexicon.csv`).

---

## xii. Document Representation
- **Sparse Representation:** Unstemmed, normalized, and Porter-stemmed token vectors.
- **Dense Vector Representation:**
  - `all-MiniLM-L6-v2` (Model A, 384-d, 256 tokens)
  - `multi-qa-MiniLM-L6-cos-v1` (Model B, 384-d, 512 tokens)
- **Document vs Chunk Representation:**
  - Full document vectors (15,560 × 384)
  - Chunked vectors: 130 words with 20-word overlap (42,480 × 384)
- **L2 Vector Normalization:** Normalizing embeddings ensures dot product equals cosine similarity.

---

## xiii. Indexing and Retrieval
- **Sparse Index:** Inverted index with `rank_bm25` ($k_1=1.5, b=0.75$).
- **Dense Vector Index:** FAISS `IndexFlatIP` (exact cosine inner product).
- **Correctness Verification:** Tested FAISS top-10 against NumPy brute force matrix multiplication (`emb @ q_vec.T`), confirming 100% agreement.
- **macOS Apple Silicon Multi-Threading Fix:** Resolved `libomp.dylib` OpenMP crash in Streamlit by setting single-threaded mode (`faiss.omp_set_num_threads(1)`, `torch.set_num_threads(1)`).

---

## xiv. Ranking / Semantic / Knowledge-Based Component
- **Reciprocal Rank Fusion (RRF):** Fuses BM25 and Semantic rank lists:
  $$RRF\\_Score(d) = \\frac{{1}}{{60 + rank_{{bm25}}(d)}} + \\frac{{1}}{{60 + rank_{{sem}}(d)}}$$
- **Ablation on Smoothing Constant $k$:** Evaluated $k \\in \\{{10, 30, 60, 100\\}}$. $k=60$ balances high rank bonuses without letting single-system outliers dominate.
- **Chunk Max Pooling:** $Score(D) = \\max_{{c \\in Chunks(D)}} \\text{{Cosine}}(Q, c)$.

---

## xv. Implementation
- `src/semantic.py`: Vector embeddings, FAISS indexing, semantic search, hybrid RRF.
- `src/bm25_search.py`: BM25 tokenization, stemming, scoring.
- `src/skills.py`: Skill extraction and gap analysis.
- `risk/risk_report.py`: Heuristic rules + logistic classifier evaluation.
- `src/rag_explain.py`: Passage chunking, Gemini API calling, 5-stage guardrails, disk caching.
- `src/eval_metrics.py`: Custom P@k, nDCG@k, MRR implementations cross-tested with `ranx`.
- `app/streamlit_app.py`: Interactive web UI.

![Figure 4: Interactive Streamlit UI Search Dashboard with Skill Gap Analysis and Filter Controls](figures/fig4_dashboard.png)  
*Figure 4: Interactive Streamlit UI Search Dashboard with Skill Gap Analysis and Filter Controls.*

---

## xvi. Experimental Setup and Test Queries
- **16 Standardized Queries:**
  - Core queries (q1–q5): Data analyst, ML intern, remote no-exp, WFH data entry scam, software engineering Java.
  - Supplementary queries (q6–q15): Cybersecurity, DevOps, web dev, marketing analytics.
  - Stress query (q16): \"deep sea welding internship\" (out-of-domain abstain test).
- **Pooling Methodology:** Top-10 results from 6 systems pooled and deduplicated into 517 evaluation rows (`data/eval/pool_for_labelling.csv`).
- **Graded Relevance Labels:** 0 = Non-Relevant, 1 = Partially Relevant, 2 = Highly Relevant.

---

## xvii. Retrieval Evaluation
- **Metrics:** Precision@5, Mean Reciprocal Rank (MRR), Normalized Discounted Cumulative Gain (nDCG@10) with linear gain.
- **Validation:** Cross-checked hand implementations against `ranx`.

---

## xviii. Results and Comparative Analysis

### Table 2: Retrieval Evaluation Results Across All Systems (16 Queries)
| Retrieval System | P@5 | nDCG@10 | MRR | Queries |
| :--- | :--- | :--- | :--- | :--- |
| **bm25_plain** | **1.000** | **0.925** | **1.000** | 16 |
| **bm25 (baseline)** | 0.988 | 0.900 | 1.000 | 16 |
| **bm25_norm** | 0.988 | 0.900 | 1.000 | 16 |
| **bm25_stem** | 0.988 | 0.849 | 1.000 | 16 |
| **hybrid_rrf (Proposed)** | 0.975 | 0.850 | 1.000 | 16 |
| **sem_minilm (Model A)** | 0.913 | 0.715 | 0.969 | 16 |
| **sem_minilm_chunks** | 0.863 | 0.655 | 0.906 | 16 |
| **sem_multiqa (Model B)** | 0.838 | 0.691 | 0.969 | 16 |

![Retrieval Evaluation Comparison](retrieval_comparison.png)  
*Figure 3: Retrieval Evaluation Comparison Across Systems (P@5, nDCG@10, MRR).*

![Figure 8: Dual-Column Comparative View Evaluating BM25 Lexical Matching Against Hybrid RRF](figures/fig8_compare.png)  
*Figure 8: Dual-Column Comparative View Evaluating BM25 Lexical Matching Against Hybrid RRF.*

### Table 3: Per-Query Performance Comparison Across Core Queries (q1–q5)
| Query ID | Query Intent Description | Top-1 Retrieved Document | Relevance Status & Notes |
| :--- | :--- | :--- | :--- |
| `q1` | Data analyst intern, Python & SQL | `emscad_4589` (Data Analyst Intern) | Clean match (Label 2); university intern. |
| `q2` | ML intern fresher, scikit-learn | `emscad_14113` (Data Science Intern) | Matched scikit-learn & Python; BM25 rank 1. |
| `q3` | Remote internship, no experience | `emscad_7983` (Web Intern - Remote) | Verified 100% remote commitment; clean match. |
| `q4` | WFH data entry, high earnings scam | `emscad_7667` (Entry Level Online Typist) | Classic EMSCAD fraud sample; high risk flag. |
| `q5` | Software intern, Java & database | `emscad_2065` (Software Dev Intern) | Clean match (Label 2); Java & SQL required. |

### Table 4: RAG Explanation Evaluation Across Relevance, Evidence, and Attribution (0–2 Scale)
| Query | Eval Count | Avg Relevance /2 | Avg Evidence /2 | Avg Attribution /2 | Avg Total /6 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `q1`: Data Analyst (Python/SQL) | 5 | 1.60 | 2.00 | 2.00 | 5.60 |
| `q2`: ML Intern Fresher | 5 | 0.60 | 2.00 | 2.00 | 4.60 |
| `q3`: Remote No-Experience | 4 | 1.00 | 1.75 | 2.00 | 4.75 |
| `q4`: WFH High Earnings Scam | 5 | 1.40 | 2.00 | 1.80 | 5.20 |
| `q5`: Software Intern (Java/DB) | 2 | 1.50 | 2.00 | 2.00 | 5.50 |
| `q16`: Deep Sea Welding (Abstain) | 1 | 0.00 | 2.00 | 2.00 | 4.00 |
| **OVERALL AVERAGE** | **22** | **1.14** | **1.95** | **1.95** | **5.05** |

![Figure 6: Grounded RAG Match Explanation with Source Chunk Citations](figures/fig6_rag.png)  
*Figure 6: Grounded RAG Match Explanation with Source Chunk Citations [doc_id#c] and Verified Attributes.*

### Table 5: Deterministic Guardrail Auditing Statistics (80 Instances)
| Guardrail Verification Check | Failure Count | Audit Outcome & Enforcement Action |
| :--- | :--- | :--- |
| JSON Format Enforcement | 0 | 100% compliant JSON responses returned by Gemini. |
| Source ID Existence | 0 | All `[doc_id#c]` citations traced to valid retrieved chunks. |
| Word-for-Word Quote Match | 0 | 100% of cited quotes verified verbatim in chunk text. |
| Deterministic Skill Overwrite | 114 | Model skills overwritten by regex lexicon extractor. |
| Defamation Keyword Neutralizer | 0 | No unlawful accusations of 'fraud' generated by LLM. |

![Figure 7: Out-of-Domain Query Abstain Behavior Triggered by Cosine Similarity Guardrail](figures/fig7_abstain.png)  
*Figure 7: Out-of-Domain Query Abstain Behavior Triggered by Cosine Similarity Guardrail.*

![Risk Classifier Precision-Recall Curve](pr_curve.png)  
*Figure 2: Precision-Recall Curve of the Logistic Risk Classifier on Held-Out Test Set.*

![Figure 5: Transparent Risk Detection Engine Displaying Warning Flags, Trigger Terms, and Disclaimers](figures/fig5_risk.png)  
*Figure 5: Transparent Risk Detection Engine Displaying Warning Flags, Trigger Terms, and Disclaimers.*

---

## xix. Discussion
- **Why BM25 Outperformed Semantic & Hybrid Retrieval on EMSCAD:**
  1. *Rigid Template Phrasing:* EMSCAD job postings follow strict corporate boilerplate language. BM25 directly exploits exact keyword overlap.
  2. *Document Brevity:* Average posting length is ~180 words, comfortably fitting within the 256 token limit of MiniLM. Overlapping chunks added boundary noise without recovering un-embedded text.
  3. *RRF Rank Dilution:* Blending near-perfect BM25 top-5 ranks with semantic search's slightly looser top-5 diluted overall precision.
  4. *Stemming Degradation:* Conflated distinct job titles ("analyst" vs "analysis"), harming nDCG.
- **RAG Honesty:** The LLM consistently exposed seniority and skill gaps rather than hallucinating false relevance.

---

## xx. Limitations
1. **Dataset Era & Bias:** 2012–2014 listings from one platform; US/Europe centric.
2. **Heuristic Pool Labels:** Baseline labels created via keyword heuristic; human review of all 517 rows recommended for published work.
3. **Query Set Size:** 16 queries demonstrate tendencies, not statistical significance.
4. **No Cross-Encoder:** Lacks a 2nd-stage neural cross-attention re-ranker.
5. **Abstain Threshold:** 0.30 cosine threshold let one pipe welder job through for q16 (0.40 recommended).

---

## xxi. Future Scope
1. **Cross-Encoder Re-Ranking:** Re-rank top-50 candidates with `ms-marco-MiniLM-L-6-v2`.
2. **Semantic Web (RDF / SPARQL):** Triplify postings with `schema.org/JobPosting` ontologies and enable SPARQL knowledge-graph queries.
3. **Adaptive Abstain Thresholds:** Dynamic quantile-based abstain filtering.
4. **Modern Live Aggregation:** Integrate live APIs (Adzuna, Remotive) for real-time postings.

---

## xxii. Conclusion
This project demonstrates that combining classical BM25 retrieval, FAISS dense vector search, Reciprocal Rank Fusion, supervised risk identification, and grounded RAG establishes an explainable, trust-aware search framework. The empirical results show that classical keyword retrieval remains exceptionally potent on domain-specific boilerplate text, while dense semantic models provide critical passage selection for grounded, hallucination-free AI explanations.

---

## xxiii. Individual Contributions
The technical research, implementation, evaluation benchmarking, and report preparation for this project were collaboratively executed by Bhawna Rani and Akriti Sengar. Table 6 provides the complete breakdown of responsibilities and technical deliverables across all system modules, followed by detailed individual contribution summaries.

### Table 6: Project Work Distribution and Responsibilities Matrix

| Project Module / Component | Team Member Responsible | Key Tasks & Technical Deliverables |
| :--- | :--- | :--- |
| **Repository & Environment Setup** | Akriti Sengar & Bhawna Rani | Git configuration, Python venv, dependencies setup. |
| **Corpus Acquisition & Exploration** | Akriti Sengar | Raw EMSCAD download, licensing check, EDA notebook. |
| **Data Cleaning & Corpus Schema** | Akriti Sengar | HTML tag stripping, deduplication, `corpus.parquet`. |
| **Skill Lexicon & Pattern Matching** | Akriti Sengar | Regex-based technical skills lexicon compilation. |
| **BM25 Lexical Retrieval Baseline** | Akriti Sengar | Okapi BM25 implementation across corpus postings. |
| **Trust & Risk Rules Formulation** | Akriti Sengar | Scam heuristics (fees, contact info, empty profiles). |
| **Supervised Risk Classifier Training** | Akriti Sengar | SGD Logistic Regression model on n-gram features. |
| **Initial Streamlit Dashboard Shell** | Akriti Sengar | Initial Streamlit interface layout and search controls. |
| **Dense Vector Representation & Encoding** | Bhawna Rani | MiniLM and Multi-QA dense embeddings (doc & chunks). |
| **FAISS Vector Indexing & Verification** | Bhawna Rani | FAISS `IndexFlatIP` build, inner product verification. |
| **Sliding-Window Chunk Mapping** | Bhawna Rani | 130-word chunking pipeline, max pooling aggregation. |
| **Reciprocal Rank Fusion (RRF) Engine** | Bhawna Rani | RRF algorithm implementation and smoothing k-ablation. |
| **Relevance Pool Construction & Labelling** | Bhawna Rani | `make_pool.py` script, 517 pooled candidate annotations. |
| **Information Retrieval Evaluation Suite** | Bhawna Rani | P@5, MRR, nDCG@10 metrics + automated `ranx` validation. |
| **Generative RAG Explanation Pipeline** | Bhawna Rani | Gemini 3.5 Flash RAG module, passage retrieval, prompt. |
| **Deterministic Guardrails & Caching** | Bhawna Rani | 5 guardrails, cosine abstain filter, SHA-256 disk cache. |
| **Manual RAG Evaluation & Audit** | Bhawna Rani | Scored 22 RAG instances on 3 criteria, citation audit. |
| **macOS OpenMP Crash Fix & UI Overhaul** | Bhawna Rani | Resolved libomp segfault, full Streamlit UI redesign. |
| **Project Report Synthesis & Verification** | Bhawna Rani | Authored comprehensive 24-section formal project report. |

### 1. Work Distribution: Bhawna Rani (Enrollment No. 992509220008)
- **Dense Vector Embeddings & Indexing:** Generated 384-dimensional dense semantic vectors across the entire corpus using `all-MiniLM-L6-v2` and `multi-qa-MiniLM-L6-cos-v1`. Engineered FAISS `IndexFlatIP` vector indexing with cosine inner product equivalence and automated verification.
- **Sliding-Window Chunking & Max Pooling:** Designed 130-word sliding-window chunking (42,480 chunk vectors) with chunk-to-document max pooling retrieval.
- **Hybrid Reciprocal Rank Fusion:** Implemented the score-invariant Reciprocal Rank Fusion (RRF) engine, conducted parameter ablation across $k \in \{10, 30, 60, 100\}$, and integrated dual-column comparative retrieval.
- **Relevance Pooling & Ground-Truth Annotation:** Engineered the candidate pooling harness (`src/make_pool.py`) pooling 517 candidate documents across 16 queries and 6 retriever runs, and performed relevance grading on a 3-point scale across all 517 rows.
- **IR Metric Suite & ranx Cross-Validation:** Developed custom implementations for Precision@5, Mean Reciprocal Rank (MRR), and nDCG@10, mathematically cross-validating them against the academic `ranx` library.
- **Grounded RAG Pipeline & Deterministic Guardrails:** Architected the generative RAG explanation engine using Gemini 3.5 Flash, authored structured prompts, calibrated the cosine abstain threshold (0.30), engineered 5 deterministic guardrails (format, source ID, quote match, skill overwrite, defamation filter), and implemented SHA-256 disk caching.
- **RAG Manual Evaluation & Citation Audit:** Conducted manual qualitative evaluation of 22 non-abstained RAG explanation cards across Relevance, Evidence Support, and Citation Attribution, and compiled the citation reference audit.
- **Low-Level macOS ARM64 Debugging & UI Redesign:** Diagnosed and resolved the native OpenMP SIGSEGV multi-threading crash in `libomp.dylib` on Apple Silicon, and redesigned the interactive Streamlit dashboard.
- **Project Report Synthesis:** Authored the complete formal 24-section project report in Microsoft Word (`.docx`) and Markdown (`.md`) formats, adhering strictly to institutional guidelines.

### 2. Work Distribution: Akriti Sengar (Enrollment No. 992509220001)
- **Corpus Acquisition & Licensing Verification:** Sourced the EMSCAD benchmark dataset (17,880 listings), verified CC-BY-NC-SA licensing, and set up the raw data storage.
- **Exploratory Data Analysis:** Conducted initial exploratory data analysis on job title distributions, company profiles, requirements fields, and class imbalance (`notebooks/01_eda.ipynb`).
- **Data Preprocessing & Parquet Schema:** Executed HTML tag stripping, text normalization, missing-field handling, and exported the standardized cleaned corpus (`corpus.parquet`, 15,560 rows).
- **Skill Lexicon Construction:** Assembled the initial regex-based skill lexicon (`skills_lexicon.csv`) covering technical skills and tools for candidate matching.
- **BM25 Lexical Retrieval Baseline:** Implemented the initial Okapi BM25 inverted index retrieval pipeline using `rank_bm25` across corpus postings.
- **Heuristic Risk Rule Formulation:** Formulated deterministic scam detection heuristic rules based on common fraudulent job characteristics (unsolicited fees, suspicious contact emails, empty company profiles).
- **Supervised Risk Classifier Training:** Trained the SGD Logistic Regression classifier on word and character n-grams to identify potentially fraudulent job postings.
- **Streamlit Application Scaffold:** Developed the initial prototype Streamlit application shell for interactive demonstration.

---

## xxiv. References
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
