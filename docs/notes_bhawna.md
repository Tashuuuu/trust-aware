# Bhawna — Study Notes: 6 Core Ideas

> Write 5–6 lines per idea **in your own words** before the viva.
> Reference: B1 in your task plan.

---

## 1. Embedding

An **embedding** converts a piece of text into a list of numbers (a vector) so that texts with similar meaning end up close together in that number-space. For example, "trainee" and "intern" will have vectors that are very similar. Models like `all-MiniLM-L6-v2` learn these vectors by training on millions of sentence pairs. The key idea is that *semantic meaning* is captured, not just word overlap. This is what makes embedding search different from keyword search like BM25.

> _TODO: add your own example from the EMSCAD data._

---

## 2. Cosine Similarity

Cosine similarity measures the **angle** between two vectors, not their magnitude. If two vectors point in the same direction (angle = 0°), cosine similarity = 1 (identical meaning). When vectors are **normalised** to unit length (length = 1), the cosine similarity equals the dot product (inner product). This is why FAISS `IndexFlatIP` (inner product) gives exact cosine results when the vectors are pre-normalised with `normalize_embeddings=True`.

> _TODO: write the formula cos(A,B) = A·B / (|A||B|) in your own words._

---

## 3. FAISS

FAISS (Facebook AI Similarity Search) is a library from Meta that finds the closest vectors to a query vector very quickly. For ~18,000 postings a "flat" (exact) index (`IndexFlatIP`) is fast enough and gives guaranteed correct results. For millions of vectors, approximate indexes like IVF or HNSW are used to trade a little accuracy for much faster speed. We do not need that here, but it is worth knowing for the viva.

> _TODO: note the time taken to build your index (B4) here._

---

## 4. Reciprocal Rank Fusion (RRF)

RRF combines two or more ranked lists by using **rank positions**, not raw scores. The formula is:

```
score(doc) = Σ  1 / (k + rank_in_list_i)
```

where `k = 60` is a smoothing constant (default from the original paper). The reason we use ranks instead of scores is that BM25 scores and cosine scores are on completely different scales — adding them directly would bias the result. With `k = 60`, documents ranked near the top of either list get a big boost, but very low-ranked documents contribute very little.

> _TODO: add your ablation result for k ∈ {10, 30, 60, 100} here (B6)._

---

## 5. Evaluation Metrics

- **Precision@5 (P@5):** Of the top 5 returned results, how many are relevant? Simple and intuitive.
- **MRR (Mean Reciprocal Rank):** 1 ÷ rank of the *first* relevant result, averaged over queries. Good for tasks where the user just wants one good answer.
- **nDCG@10 (Normalised Discounted Cumulative Gain):** Rewards putting *highly* relevant results (label 2) higher than partly relevant (label 1). Uses log discounting: a result at rank 1 is worth twice a result at rank 3. The "N" means it is divided by the ideal DCG so the value is 0–1.

> _TODO: fill in your P@5, nDCG@10, MRR numbers from B8._

---

## 6. RAG (Retrieval-Augmented Generation)

RAG works in two steps: (1) **retrieve** the most relevant documents from your index, then (2) **give them to a language model** and ask it to answer *only from those documents*, with citations. The benefit is that the model can use fresh, specific information rather than relying on what it was trained on. The key risk is **hallucination** — the model may still invent facts. To reduce this, we check every quote in the answer against the actual retrieved text and refuse answers where evidence is weak (`insufficient_evidence = true`).

> _TODO: record how many guardrail failures you saw in B10 here._
