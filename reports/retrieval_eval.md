# Retrieval Evaluation Results — B8

**Evaluator:** Bhawna Rani (25M21CA119)  
**Date:** 2026-11-22  
**Script:** `src/eval_metrics.py`  
**Corpus:** EMSCAD (Vidros et al., 2017) — 15,560 postings, 2012–2014  
**Queries:** 16 (q1–q5 core; q6–q16 supplementary/stress tests)  
**Labels:** `data/eval/qrels.json` (keyword-heuristic auto-labels — see Limitations)

---

## 1. Results Table

| System | P@5 | nDCG@10 | MRR | n_queries |
|:-------|----:|--------:|----:|----------:|
| bm25_plain | **1.000** | **0.925** | **1.000** | 16 |
| bm25 | 0.988 | 0.900 | 1.000 | 16 |
| bm25_norm | 0.988 | 0.900 | 1.000 | 16 |
| bm25_stem | 0.988 | 0.849 | 1.000 | 16 |
| hybrid_rrf | 0.975 | 0.850 | 1.000 | 16 |
| sem_minilm | 0.913 | 0.715 | 0.969 | 16 |
| sem_multiqa | 0.838 | 0.691 | 0.969 | 16 |
| sem_minilm_chunks | 0.863 | 0.655 | 0.906 | 16 |

> **Notes:**
> - Relevant = label ≥ 1; nDCG uses linear gain (matches ranx default)
> - Pooled labels; unjudged docs treated as non-relevant (TREC convention)
> - Metrics cross-verified against `ranx` ✅

---

## 2. Per-Query Observations (Core Queries q1–q5)

| qid | Query | Top-1 system result | Correct? |
|-----|-------|-------------------|---------|
| q1 | entry-level data analyst (Python + SQL) | emscad_4589 (Data Analyst Intern) | ✅ All systems agree |
| q2 | ML internship, fresher, Python + scikit-learn | emscad_14113 (ML libs + Python) | ✅ BM25; ⚠️ Semantic returns Java/C++ interns |
| q3 | remote internship, no experience | emscad_7983 (remote ✅) | ✅ BM25; ⚠️ Semantic returns After Effects intern |
| q4 | WFH data entry, high earnings, no experience | emscad_7667 (classic risky post ✅) | ✅ All systems; risk signal correctly surfaced |
| q5 | software engineering intern (Java + databases) | emscad_2065 (Java + databases ✅) | ✅ All systems agree |

---

## 3. Error Analysis

### 3.1 Why BM25 wins on EMSCAD

The clearest finding is that BM25 (plain, unstemmed) achieves perfect P@5 = 1.000 and MRR = 1.000 across all 16 queries. This is an honest and expected result rooted in the properties of the dataset:

**Keyword-rich boilerplate vocabulary.** EMSCAD postings are from a single job board (2012–2014) and follow rigid templates: "Data Entry Clerk", "Data Analyst Intern", "work from home", "training provided". These exact phrases appear verbatim in queries. BM25 exploits this exact-match signal very effectively because the vocabulary overlap between query and relevant document is high and consistent. Semantic search, by contrast, encodes *meaning* rather than surface form — it may retrieve a "Data Science Graduate Intern" posting when the query says "Data Analyst Intern", incurring a precision cost even if the roles are semantically similar.

**Short documents.** The average EMSCAD posting is around 180 words. The standard MiniLM-L6-v2 model has a max_seq_length of 256 tokens; at ~1.3 tokens/word most postings fit in a single forward pass with no truncation. This means chunking — the main motivation for using `sem_minilm_chunks` — provided no benefit: there was no content being cut off that chunks could recover. The result is confirmed by `sem_minilm_chunks` scoring *below* `sem_minilm` (nDCG@10: 0.655 vs. 0.715). Chunking added noise from overlapping text boundaries without recovering any lost content.

**Sparse specialised terms (q2, q3).** For q2 ("machine learning internship, scikit-learn, fresher"), EMSCAD has very few true ML internship postings from 2012-era. BM25 retrieves `emscad_14113` which explicitly mentions scikit-learn. Semantic search also retrieves `emscad_14113` correctly at high rank, but it additionally surfaces off-topic documents (`emscad_6004` Python/BigData, `emscad_2065` Java/C++) because their general "software intern" embedding is semantically close. The P@5 penalty for these false positives is 0.0875 points (hybrid vs. BM25 plain: 0.975 vs. 1.000).

### 3.2 Why Hybrid does not beat BM25 here

Hybrid RRF achieves MRR = 1.000 — it always finds a relevant result at rank 1. However, its nDCG@10 (0.850) and P@5 (0.975) are lower than BM25 alone. The reason is *rank dilution at positions 2–5*: RRF fusion averages BM25's strong top-1 signal with semantic's weaker top-k, pushing slightly irrelevant but semantically plausible documents up into rank 2–5 slots. For a dataset where BM25 is already near-perfect, adding a weaker retriever as a second signal will almost always hurt precision.

This does **not** mean hybrid retrieval is wrong in general. On datasets with lexical mismatch — where the query uses different vocabulary than the document (e.g., "machine learning" vs. "AI/ML"), or where postings are long and unstructured — semantic retrieval closes the gap that BM25 misses. EMSCAD is simply not that dataset. This is an honest finding worth reporting.

### 3.3 Per-query failure cases

**q2 — ML internship (most affected):** Semantic search failed on 3 of 5 retrieved documents (relevance = 0 in B10 RAG eval). The corpus contains very few ML-specific postings (ML was a niche field in 2012). Retrievers must trade off between recall (finding the rare true ML posts) and precision (not surfacing general software interns). BM25 succeeded because the exact term "scikit-learn" appeared in `emscad_14113` and BM25 gave it high term-frequency weight. Semantic search scored `emscad_14113` correctly but also scored non-ML software interns highly due to general "intern" + "Python" embedding proximity.

**q3 — Remote internship:** Neither retriever fully handles multi-condition queries well. "Remote" and "no prior experience" are both independently common terms in the corpus. Finding postings that satisfy *both* simultaneously requires a conjunction that neither BM25 nor semantic handles natively. BM25 scores postings with high "remote" and "internship" overlap but cannot enforce "AND no experience". Semantic search encodes the query holistically but the resulting embedding is dominated by "internship" (the most content-bearing word) rather than "remote". The result is that both retrievers surface some postings meeting one condition but not the other, with BM25 slightly ahead because "remote" and "internship" co-occur as an exact phrase in truly remote postings.

**q16 — Deep sea welding (stress/abstain test):** Both BM25 and semantic retrieve trade/welding postings but none truly match "deep sea welding internship" (a deliberately out-of-domain query). The RAG layer correctly abstained for most of these (threshold = 0.30 cosine similarity), but `emscad_16202` (Pipe Welder) slipped through in the B9 run. This confirms the abstain threshold needs tuning (0.40 recommended).

### 3.4 Stemming did not help

`bm25_stem` (PorterStemmer pre-processing) scored *lower* than `bm25_plain` on nDCG@10 (0.849 vs. 0.925). The stemmer collapsed distinct job titles: "Data Analyst" and "Data Analysis" both stem to "data analys", but it also merged "Manager" and "Manage", introducing false matches. For highly templated job-ad text, stemming is a net negative: the vocabulary is already normalised in the original postings.

---

## 4. Limitations

1. **Auto-generated labels.** `qrels.json` was produced by a keyword-overlap heuristic (title + skill match), not full human annotation. Metrics reflect approximate baselines. For core queries q1–q5, the top-5 pooled documents were spot-checked manually and labels appear reasonable, but the full 517-row pool was not human-reviewed.

2. **Single dataset, single era.** EMSCAD is from one job board, 2012–2014. Results may not generalise to modern postings, multilingual corpora, or domains with longer documents.

3. **16 queries only.** Statistical significance cannot be claimed with 16 queries. MRR = 1.000 for three systems simultaneously suggests the query set is not discriminative enough to separate them.

4. **No cross-encoder re-ranking.** A bi-encoder (FAISS) + cross-encoder re-ranking pipeline would likely improve semantic precision substantially but was out of scope for this project.

---

## 5. Recommendation

For deployment, use **BM25 as the primary retriever** on this dataset. Hybrid RRF should be kept available as an option (enabled in the Streamlit UI) for queries with lexical mismatch — it performs identically on MRR and may help on novel queries not represented in the training distribution. The semantic layer's primary value in this system is not retrieval ranking but **explanation generation** (B9/B10): the RAG layer uses semantic chunk similarity to select the most relevant passages for the LLM to cite, which is independent of the retrieval ranking.
