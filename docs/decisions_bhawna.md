# Bhawna — Design Decisions Log

> Records every technical decision made during B3–B11. This feeds the report and viva.

---

## B3 — Embeddings

| Item | Value |
|------|-------|
| Model A | `sentence-transformers/all-MiniLM-L6-v2` |
| Model B | `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` |
| `max_seq_length` (MiniLM-L6-v2) | 256 tokens |
| `max_seq_length` (multi-qa-MiniLM-L6-cos-v1) | 512 tokens |
| Corpus size | 15,560 documents |
| Embedding date | 2026-11-20 |
| Time to embed full corpus (Model A, doc-level) | ~4 min on MacBook CPU |
| Time to embed full corpus (Model A, chunks) | ~11 min (42,480 chunk vectors) |
| Time to embed full corpus (Model B, doc-level) | ~4 min on MacBook CPU |
| Chunking: words per chunk | 130 (midpoint of 120–150 word range) |
| Chunking: overlap | 20 words (≈15%, prevents boundary losses) |
| Why 130 words? | MiniLM max_seq_length = 256 tokens; 130 words ≈ 170 tokens, well within limit with ~40% headroom for subword expansion |
| Text truncation vs chunks | Chunks chosen as the semantic variant (minilm_chunks). However, B5 results showed chunks did **not** improve scores vs. doc-level (see B6 notes). This is a valid finding: EMSCAD postings are short (average ~180 words), so truncation was not a real problem. |
| `normalize_embeddings=True`? | Yes. Required for `IndexFlatIP` to compute cosine similarity via inner product. |
| `batch_size` | 64 (default; memory-safe on 8 GB MBP) |
| `random_state` | 42 (where applicable) |

---

## B4 — FAISS Index

| Item | Value |
|------|-------|
| Index type | `IndexFlatIP` (exact inner product = cosine on normalised vectors) |
| Why exact? | 15,560 vectors; exact search is fast enough (<100 ms). Approximate (HNSW/IVF) needed only at millions of vectors. |
| Dimension | 384 (both MiniLM variants) |
| Verified against NumPy brute force? | Yes ✅ — top-10 results identical for all three indexes after fixing a per-tag cache bug (module-level global reused Model A's index for Model B; fixed with `_load_index._cache[tag]` dict). |
| Indexes saved | `faiss_minilm.index`, `faiss_minilm_chunks.index`, `faiss_multiqa.index` |

---

## B5 — Semantic Runs

| Observation | Query | Detail |
|-------------|-------|--------|
| Top result correct | q1 | emscad_4589 (Data Analyst Intern) — expected first. |
| Chunks didn't beat doc-level | q1–q5 | `sem_minilm_chunks` retrieved the same top-5 doc_ids as `sem_minilm` for all 5 core queries. EMSCAD postings are short; chunking added overhead without gain. |
| Multi-QA slightly worse | q2–q3 | `sem_multiqa` underperformed `sem_minilm` on specialised queries (ML intern, remote internship). MiniLM-L6-v2 trained on more diverse corpora; multi-qa trained on Q&A pairs which suits longer queries. |
| Weak on keyword-heavy queries | q4 (data entry) | Semantic search retrieved fewer exact phrase matches than BM25 for "data entry" and "work-from-home". Expected: job postings use highly repetitive boilerplate vocabulary. |

---

## B6 — Hybrid / RRF

| Item | Value |
|------|-------|
| `k` chosen | 60 (standard default from Cormack & Clarke, 2009) |
| Candidate depth per system | 100 |
| Semantic variant used | `sem_minilm_chunks` (chosen **before** looking at nDCG numbers, as designed) |
| Ablation: k ∈ {10, 30, 60, 100} winner | k = 60 and k = 100 tied on top-5 doc_ids for all 5 core queries. k = 60 chosen as it matches the original RRF paper default. |
| Fusion formula | `score(d) = Σ 1/(k + rank_i(d))` over BM25 and semantic rankings |
| BM25 source | `runs/bm25.json` (Akriti's pre-computed run, 16 queries) |
| Result | Hybrid ranks all correctly known relevant docs at rank ≤ 2, but nDCG@10 (0.850) is **lower** than BM25 (0.900). See retrieval_eval.md for analysis. |

---

## B8 — Evaluation Metrics

| Item | Value |
|------|-------|
| Metrics computed | P@5, nDCG@10, MRR |
| nDCG gain type | Linear (matches ranx default) |
| Labels | Auto-generated keyword heuristic (`src/make_pool.py`). Not full human annotation. See limitation note. |
| Relevant threshold | label ≥ 1 (binary; label 2 = highly relevant) |
| Unjudged docs | Treated as non-relevant (standard TREC convention) |
| Library cross-check | Scores verified against `ranx` ✅ |
| **Key finding** | BM25 (plain) beats hybrid on this dataset. This is **honest and expected**: EMSCAD is a 2012-era job board with keyword-rich, boilerplate postings. Semantic adds diversity but hurts precision at top ranks. |

**Limitation note:** `labels_bhawna.csv` / `qrels.json` used a keyword heuristic (title/skill overlap), not human annotation. Metrics should be treated as approximate baselines. Full human review of q1–q5 is recommended before citing these numbers in a published paper.

---

## B9 — RAG

| Item | Value |
|------|-------|
| LLM model | `gemini-3.5-flash` |
| SDK | `google-genai` (new SDK, `from google import genai`) |
| Model used date | 2026-11-20 |
| Temperature | 0 (deterministic; important for reproducibility) |
| Response format | `application/json` (enforced via `response_mime_type`) |
| Abstain threshold | 0.30 cosine similarity |
| Why 0.30? | Chosen as a conservative lower bound: postings below 0.30 similarity to the query are almost certainly off-topic. Set low to avoid false abstains for borderline-relevant posts. Post-hoc analysis (B10 q16 failure) suggests 0.40 would be more appropriate. |
| Prompt version | `explain_v1.txt` |
| Cache | `rag/cache/<sha256>.json` (gitignored) |
| Evidence chunks per doc | 2 (top-2 chunks by cosine similarity to query) |
| Total answers generated | 80 (22 real LLM, 58 abstained) |
| Guardrail results | JSON fail: 0 · bad_source: 0 · quote_mismatch: 0 · skills_overwrite: 114 · defamation: 0 |

---

## B11 — Streamlit Integration

| Item | Value |
|------|-------|
| Import fix | Akriti's placeholder `src.hybrid` → `src.semantic`; `rag.explain` → `src.rag_explain` |
| Explain adapter | `explain()` returns `{doc_id: answer_dict}`; app-level adapter flattens to one markdown string per search |
| Live BM25 fallback | For arbitrary queries not in `bm25.json`, calls `bm25_search(query, k)` live (requires `rank_bm25` + `nltk`) |
| np.str_ fix | All doc_ids cast to `str` at source in `semantic_search()` and both BM25 paths |
| Model loading | Lazy, cached per tag — model loads once per Streamlit session |
