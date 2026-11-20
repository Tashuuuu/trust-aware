# Bhawna — Design Decisions Log

> Record every technical decision here as you work. This feeds your report and viva.

---

## B3 — Embeddings

| Item | Value |
|------|-------|
| Model A | `sentence-transformers/all-MiniLM-L6-v2` |
| Model B | `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` |
| `max_seq_length` (MiniLM-L6) | _TODO: fill after B0 test_ |
| `max_seq_length` (multi-qa) | _TODO: fill after B0 test_ |
| Corpus size | _TODO: fill after loading corpus.parquet_ |
| Embedding date | _TODO_ |
| Time to embed full corpus (Model A) | _TODO_ |
| Time to embed full corpus (Model B) | _TODO_ |
| Chunking: words per chunk | 130 (midpoint of 120–150) |
| Chunking: overlap | 20 words |
| Text truncation vs chunks | _TODO: decision after B5 sanity check_ |

---

## B4 — FAISS Index

| Item | Value |
|------|-------|
| Index type | `IndexFlatIP` (exact cosine, via inner product on normalised vectors) |
| Why exact? | ~18k vectors; exact search is fast enough. Approximate needed only at millions. |
| Verified against NumPy brute force? | _TODO_ |

---

## B5 — Semantic Runs

| Observation | Query | Detail |
|-------------|-------|--------|
| _TODO_ | q1 | |
| _TODO_ | q2 | |

---

## B6 — Hybrid / RRF

| Item | Value |
|------|-------|
| `k` chosen | 60 (default; see ablation) |
| Candidate depth | 100 per system |
| Best semantic variant (chosen before looking at test numbers) | _TODO_ |
| Ablation: k ∈ {10, 30, 60, 100} winner | _TODO_ |

---

## B9 — RAG

| Item | Value |
|------|-------|
| LLM model | _TODO_ |
| Model date used | _TODO_ |
| Temperature | 0 |
| Abstain threshold (cosine similarity) | _TODO_ |
| Why that threshold? | _TODO_ |
| Prompt version | explain_v1.txt |
| Cache location | `rag/cache/<hash>.json` |
