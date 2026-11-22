# Bhawna — Study Notes: 6 Core Ideas

> Reference: B1 in the task plan. Written after completing B3–B11 on the EMSCAD dataset.

---

## 1. Embedding

An **embedding** converts a piece of text into a list of numbers (a vector) so that texts with similar meaning end up close together in that number-space. For example, "trainee" and "intern" will have vectors that are very similar even though they share no letters. Models like `all-MiniLM-L6-v2` learn these vectors by training on millions of sentence pairs using a contrastive objective — pairs of sentences that mean the same thing are pushed together, and pairs that don't are pushed apart. The key idea is that *semantic meaning* is captured, not just word overlap.

**Example from EMSCAD:** The query "entry-level data analyst internship requiring Python and SQL" retrieved `emscad_4589` (title: "Data Analyst Intern") as the top result. The word "entry-level" does not appear anywhere in that posting, but the embedding captured the internship+analyst+Python meaning and placed both vectors close in the 384-dimensional space. BM25 would have scored this posting lower for the missing "entry-level" term; embedding search was better here because it understood synonymy.

The model we used (`all-MiniLM-L6-v2`) outputs 384-dimensional vectors. We also tested `multi-qa-MiniLM-L6-cos-v1` (also 384-d, trained on Q&A pairs) and found MiniLM-L6-v2 performed slightly better on our data.

---

## 2. Cosine Similarity

Cosine similarity measures the **angle** between two vectors, not their magnitude. If two vectors point in the same direction (angle = 0°), cosine similarity = 1 — they mean the same thing. If they are perpendicular (90°), similarity = 0.

The formula is:

```
cos(A, B) = (A · B) / (|A| × |B|)
```

In plain words: take the dot product of the two vectors, then divide by both their lengths to cancel out magnitude. The result is always between −1 and 1 for text embeddings.

When vectors are **normalised to unit length** (|A| = |B| = 1), the denominator becomes 1×1 = 1, so cosine similarity equals the raw dot product. This is why we use `normalize_embeddings=True` before saving to the FAISS index and use `IndexFlatIP` (inner product): the inner product *is* cosine similarity when vectors are normalised. This saves a division at query time — a useful trick for speed at scale.

**In our system:** The abstain threshold for RAG was set at cosine similarity = 0.30. Any posting with max chunk similarity below 0.30 to the query was considered too different to explain, and the system returned `insufficient_evidence = True` instead of generating an answer.

---

## 3. FAISS

FAISS (Facebook AI Similarity Search) is a library from Meta that finds the closest vectors to a query vector very quickly. It is especially designed for large-scale nearest-neighbour search in high-dimensional spaces.

For our ~15,560 postings, we used `IndexFlatIP` — a "flat" (exact, brute-force) index that checks every vector in the database. This gives guaranteed correct results with no approximation, and it is fast enough for 15k vectors (search takes <100 ms on a laptop CPU). We verified correctness by comparing FAISS top-10 results against NumPy brute-force dot products for every model — they matched exactly after fixing a per-tag cache bug.

For millions of vectors, exact search becomes too slow. That's when you would switch to approximate indexes like **IVF** (inverted file index — clusters vectors into buckets and only searches nearby buckets) or **HNSW** (hierarchical navigable small world graph — builds a graph of nearest neighbours for fast traversal). We don't need those here, but it's worth knowing for the viva.

**Index build time:** ~3 seconds per index on MacBook CPU (the embedding step takes much longer — ~4 min for 15,560 doc-level vectors).

---

## 4. Reciprocal Rank Fusion (RRF)

RRF combines two or more ranked lists by using **rank positions**, not raw scores. The formula is:

```
score(doc) = Σ  1 / (k + rank_in_list_i)
```

where `k = 60` is a smoothing constant from the original paper (Cormack & Clarke, 2009). We fuse BM25 ranks and semantic ranks.

The reason we use ranks instead of scores is that BM25 scores (term frequency sums) and cosine similarity scores (0 to 1) are on completely different scales — adding them directly would bias the result toward whichever system has larger raw numbers. By converting to rank positions first, both systems contribute equally regardless of their score scale. With `k = 60`, a document at rank 1 gets score ≈ 0.0164 and a document at rank 100 gets ≈ 0.0062 — so top-ranked documents from either list get a meaningful boost, but very low-ranked documents contribute very little.

**Ablation result (B6):** We tested k ∈ {10, 30, 60, 100}. The top-5 retrieved doc_ids were identical for k = 60 and k = 100 on all 5 core queries. k = 10 caused some re-ordering at positions 4–5 for q2 and q3. We chose k = 60 as it matches the original paper's recommendation and is the most commonly used default.

**Key finding:** Hybrid RRF did not beat BM25 on EMSCAD (nDCG@10: 0.850 vs. 0.925). This is expected — EMSCAD postings use rigid keyword templates, so BM25's exact-match signal is very strong. Hybrid would likely win on a dataset with more vocabulary variation.

---

## 5. Evaluation Metrics

- **Precision@5 (P@5):** Of the top 5 returned results, how many are relevant? Simple and intuitive — directly reflects what a user sees on the first page.

- **MRR (Mean Reciprocal Rank):** 1 ÷ rank of the *first* relevant result, averaged over queries. Good for tasks where the user just wants one good answer (e.g., "find me any suitable internship"). If the first relevant result is at rank 1, MRR = 1. At rank 2, MRR = 0.5. At rank 3, MRR = 0.33.

- **nDCG@10 (Normalised Discounted Cumulative Gain):** Rewards putting *highly* relevant results (label 2) higher than partially relevant (label 1). Uses log discounting: a result at rank 1 is worth twice a result at rank 3. The "N" means it's divided by the ideal DCG (perfect ranking), so the value is always 0–1.

**Our B8 results:**

| System | P@5 | nDCG@10 | MRR |
|--------|-----|---------|-----|
| bm25_plain | **1.000** | **0.925** | **1.000** |
| hybrid_rrf | 0.975 | 0.850 | 1.000 |
| sem_minilm | 0.913 | 0.715 | 0.969 |
| sem_minilm_chunks | 0.863 | 0.655 | 0.906 |
| sem_multiqa | 0.838 | 0.691 | 0.969 |

BM25 wins across the board. This is an honest result — EMSCAD job postings are keyword-rich templates where exact-match retrieval dominates. Semantic search adds value in explanation generation (B9), not necessarily in ranking.

---

## 6. RAG (Retrieval-Augmented Generation)

RAG works in two steps:
1. **Retrieve** the most relevant document chunks from the FAISS index (using cosine similarity to find the top-2 most relevant chunks per posting).
2. **Generate** — pass those chunks to a language model (Gemini 3.5 Flash) and ask it to answer *only from those chunks*, with citations like `[emscad_4589#c0]`.

The benefit is that the LLM uses fresh, specific information from the actual job posting rather than relying on what it was trained on. This is what makes the explanations trustworthy and grounded — every claim traces back to a chunk of text the user can verify.

**The key risks and how we handled them:**
- **Hallucination** (LLM invents quotes): We check every quote in the answer against the actual chunk text. If a quote doesn't appear in the cited chunk, we flag it with `_unsupported: true`.
- **Off-topic answers**: We refuse to generate an explanation if the top chunk cosine similarity < 0.30 (`insufficient_evidence = true`). This abstain mechanism fired for 58 of 80 answer attempts — mostly the stress query q16 "deep sea welding internship".
- **Defamation**: We replace any answer containing words like "scam" or "is a fraud" with a standard warning: "this posting shows signals that may indicate risk."

**B10 guardrail results:** JSON parse failures: 0. Bad citations: 0. Quote mismatches: 0. Skills overwritten (expected): 114. Defamation blocked: 0. The RAG layer was clean — the LLM consistently grounded its answers in the retrieved chunks and cited sources correctly (average attribution score: 1.95/2.0).
