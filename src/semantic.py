"""
src/semantic.py
Bhawna — B3, B4, B5, B6
Semantic search and hybrid RRF search functions.

Usage:
    from src.semantic import semantic_search, hybrid_search, build_index
"""

import json
import math
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Paths — all relative to project root
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH    = ROOT / "data" / "processed" / "corpus.parquet"
QUERIES_PATH   = ROOT / "data" / "processed" / "queries.json"
INDEX_DIR      = ROOT / "index"
RUNS_DIR       = ROOT / "runs"

# Model names (B3)
MODEL_A = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_B = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"

# Lazy-loaded globals (loaded once; Streamlit will cache the wrapper)
_model = None
_index = None
_doc_ids = None


# ---------------------------------------------------------------------------
# B3 — Embeddings
# ---------------------------------------------------------------------------

def load_corpus():
    """Load corpus.parquet; return DataFrame."""
    import pandas as pd
    df = pd.read_parquet(CORPUS_PATH)
    assert "doc_id" in df.columns, "corpus.parquet missing 'doc_id' column"
    assert "search_text" in df.columns, "corpus.parquet missing 'search_text' column"
    return df


def chunk_text(text: str, words_per_chunk: int = 130, overlap: int = 20) -> list[str]:
    """Split text into overlapping word-chunks (B3, Option 2)."""
    words = str(text).split()
    if not words:
        return [""]
    chunks = []
    step = words_per_chunk - overlap
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + words_per_chunk])
        chunks.append(chunk)
        if start + words_per_chunk >= len(words):
            break
    return chunks or [""]


def embed_corpus(model_name: str = MODEL_A, use_chunks: bool = False, batch_size: int = 64):
    """
    Embed the full corpus and save:
        index/embeddings_<tag>.npy
        index/doc_ids_<tag>.npy
        index/chunk_map_<tag>.json  (only when use_chunks=True)

    Returns (embeddings, doc_ids).
    """
    from sentence_transformers import SentenceTransformer

    tag = _model_tag(model_name, use_chunks)
    emb_path    = INDEX_DIR / f"embeddings_{tag}.npy"
    ids_path    = INDEX_DIR / f"doc_ids_{tag}.npy"
    chunk_path  = INDEX_DIR / f"chunk_map_{tag}.json"

    INDEX_DIR.mkdir(exist_ok=True)

    df = load_corpus()
    print(f"Corpus: {len(df)} rows")

    model = SentenceTransformer(model_name, local_files_only=True)
    print(f"Model: {model_name}  max_seq_length={model.max_seq_length}")

    if use_chunks:
        # Build flat list of (doc_id, chunk_text); store mapping
        texts, chunk_map = [], []
        for _, row in df.iterrows():
            for i, ch in enumerate(chunk_text(row["search_text"])):
                chunk_id = f"{row['doc_id']}#c{i}"
                texts.append(ch)
                chunk_map.append({"chunk_id": chunk_id, "doc_id": row["doc_id"]})
        emb = model.encode(texts, batch_size=batch_size,
                           show_progress_bar=True, normalize_embeddings=True)
        emb = np.asarray(emb, dtype="float32")
        # Save
        np.save(emb_path, emb)
        chunk_ids = [c["chunk_id"] for c in chunk_map]
        np.save(ids_path, np.array(chunk_ids))
        with open(chunk_path, "w") as f:
            json.dump(chunk_map, f)
        print(f"Saved {len(emb)} chunk embeddings → {emb_path}")
        return emb, np.array(chunk_ids)
    else:
        texts   = df["search_text"].fillna("").tolist()
        doc_ids = df["doc_id"].tolist()
        emb = model.encode(texts, batch_size=batch_size,
                           show_progress_bar=True, normalize_embeddings=True)
        emb = np.asarray(emb, dtype="float32")
        assert len(emb) == len(doc_ids), "Embedding count != corpus row count!"
        np.save(emb_path, emb)
        np.save(ids_path, np.array(doc_ids))
        print(f"Saved {len(emb)} doc embeddings → {emb_path}")
        return emb, np.array(doc_ids)


# ---------------------------------------------------------------------------
# B4 — FAISS Index
# ---------------------------------------------------------------------------

def build_index(model_name: str = MODEL_A, use_chunks: bool = False):
    """Build a FAISS IndexFlatIP and save it to disk."""
    import faiss

    tag       = _model_tag(model_name, use_chunks)
    emb_path  = INDEX_DIR / f"embeddings_{tag}.npy"
    idx_path  = INDEX_DIR / f"faiss_{tag}.index"

    if not emb_path.exists():
        raise FileNotFoundError(
            f"Embeddings not found: {emb_path}. Run embed_corpus() first."
        )

    emb = np.load(emb_path)
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(emb)
    faiss.write_index(index, str(idx_path))
    print(f"FAISS index built ({emb.shape[0]} vectors, dim={emb.shape[1]}) → {idx_path}")
    return index


def _load_index(model_name: str = MODEL_A, use_chunks: bool = False):
    """Load FAISS index + doc_ids (lazy, cached per tag)."""
    import faiss
    faiss.omp_set_num_threads(1)

    tag      = _model_tag(model_name, use_chunks)
    idx_path = INDEX_DIR / f"faiss_{tag}.index"
    ids_path = INDEX_DIR / f"doc_ids_{tag}.npy"

    # Cache per tag so switching models works correctly
    if not hasattr(_load_index, "_cache"):
        _load_index._cache = {}
    if tag not in _load_index._cache:
        import torch
        torch.set_num_threads(1)
        from sentence_transformers import SentenceTransformer
        _load_index._cache[tag] = (
            SentenceTransformer(model_name, local_files_only=True),
            faiss.read_index(str(idx_path)),
            np.load(ids_path, allow_pickle=True),
        )
    return _load_index._cache[tag]


def verify_faiss(query: str, model_name: str = MODEL_A, use_chunks: bool = False, top_k: int = 10):
    """
    B4 correctness check: compare FAISS top-k against NumPy brute force.
    Call once after building index; results should match exactly.
    """
    model, index, doc_ids = _load_index(model_name, use_chunks)
    q_vec = model.encode([query], normalize_embeddings=True).astype("float32")

    # FAISS result
    scores_faiss, idxs_faiss = index.search(q_vec, top_k)
    faiss_top = [(doc_ids[i], float(s)) for i, s in zip(idxs_faiss[0], scores_faiss[0])]

    # NumPy brute force
    tag     = _model_tag(model_name, use_chunks)
    emb     = np.load(INDEX_DIR / f"embeddings_{tag}.npy")
    dot     = emb @ q_vec.T  # (N, 1)
    np_idxs = np.argsort(-dot[:, 0])[:top_k]
    np_top  = [(doc_ids[i], float(dot[i, 0])) for i in np_idxs]

    faiss_ids = [x[0] for x in faiss_top]
    np_ids    = [x[0] for x in np_top]
    if faiss_ids == np_ids:
        print("✅  FAISS matches NumPy brute force — index is correct.")
    else:
        print("❌  MISMATCH between FAISS and NumPy!")
        print("FAISS:", faiss_ids)
        print("NumPy:", np_ids)
    return faiss_top, np_top


# ---------------------------------------------------------------------------
# B5 — semantic_search  (the public API)
# ---------------------------------------------------------------------------

def semantic_search(query: str, k: int = 100,
                    model_name: str = MODEL_A,
                    use_chunks: bool = False) -> list[tuple[str, float]]:
    """
    Return top-k (doc_id, score) pairs for the query.
    Scores are cosine similarities in [0, 1] (vectors are normalised).
    """
    model, index, doc_ids = _load_index(model_name, use_chunks)
    q_vec = model.encode([query], normalize_embeddings=True).astype("float32")
    scores, idxs = index.search(q_vec, k if not use_chunks else k * 3)
    results = [(str(doc_ids[i]), float(s)) for i, s in zip(idxs[0], scores[0])]

    if use_chunks:
        # Keep best chunk score per doc_id
        best: dict[str, float] = {}
        for chunk_id, score in results:
            doc_id = chunk_id.split("#")[0]
            if score > best.get(doc_id, -1):
                best[doc_id] = score
        results = sorted(best.items(), key=lambda x: x[1], reverse=True)[:k]

    return results


def save_run(results_per_query: dict[str, list[tuple[str, float]]], path: str | Path):
    """Save run in the shared {qid: {doc_id: score}} format."""
    run = {qid: {doc_id: score for doc_id, score in hits}
           for qid, hits in results_per_query.items()}
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(run, f, indent=2)
    print(f"Run saved → {path}")


def run_all_queries(model_name: str = MODEL_A, use_chunks: bool = False, k: int = 100):
    """Run semantic search for all queries and save run file (B5)."""
    with open(QUERIES_PATH) as f:
        queries = json.load(f)
    tag = _model_tag(model_name, use_chunks)
    results = {}
    for q in queries:
        hits = semantic_search(q["text"], k=k, model_name=model_name, use_chunks=use_chunks)
        results[q["qid"]] = hits
        print(f"  {q['qid']}: top result = {hits[0] if hits else 'none'}")
    save_run(results, RUNS_DIR / f"sem_{tag}.json")
    return results


# ---------------------------------------------------------------------------
# B6 — Hybrid ranking with RRF
# ---------------------------------------------------------------------------

def rrf(rankings: list[list[str]], k: int = 60, top_n: int = 100) -> list[tuple[str, float]]:
    """
    Reciprocal Rank Fusion (hand-implemented as per B6 requirement).
    rankings: list of ranked doc_id lists (best first).
    Returns [(doc_id, rrf_score), ...] sorted descending.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]


def hybrid_search(query: str, k: int = 100,
                  sem_model: str = MODEL_A,
                  use_chunks: bool = False,
                  rrf_k: int = 60,
                  bm25_run_path: str | Path | None = None) -> list[tuple[str, float]]:
    """
    Hybrid search: RRF fusion of BM25 + semantic (B6).
    Returns list of (doc_id, rrf_score).

    bm25_run_path: path to Akriti's BM25 run JSON. If None, tries runs/bm25.json.
    """
    bm25_path = Path(bm25_run_path) if bm25_run_path else RUNS_DIR / "bm25.json"

    # --- Semantic ranking ---
    sem_results = semantic_search(query, k=k, model_name=sem_model, use_chunks=use_chunks)
    sem_ranking = [str(doc_id) for doc_id, _ in sem_results]

    # --- BM25 ranking (cached run for known qids; live call for arbitrary queries) ---
    bm25_ranking: list[str] = []
    qid = _query_to_qid(query)
    if qid and bm25_path.exists():
        # Known query — use pre-computed run file (fast, deterministic)
        with open(bm25_path) as f:
            bm25_run = json.load(f)
        if qid in bm25_run:
            bm25_ranking = [str(d) for d in sorted(bm25_run[qid], key=lambda d: bm25_run[qid][d], reverse=True)]
    else:
        # Arbitrary/live query — call Akriti's live BM25 function
        try:
            from src.bm25_search import bm25_search as _bm25_live  # type: ignore
            bm25_ranking = [str(doc_id) for doc_id, _ in _bm25_live(query, k)]
        except Exception as exc:
            print(f"⚠️  BM25 live search failed ({exc}). Using semantic-only fallback.")
            return sem_results

    return rrf([bm25_ranking, sem_ranking], k=rrf_k, top_n=k)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _model_tag(model_name: str, use_chunks: bool) -> str:
    """Short tag used in filenames."""
    if "minilm" in model_name.lower() and "multi" not in model_name.lower():
        tag = "minilm"
    elif "multi-qa" in model_name.lower() or "multiqa" in model_name.lower():
        tag = "multiqa"
    elif "mpnet" in model_name.lower():
        tag = "mpnet"
    else:
        tag = model_name.split("/")[-1]
    return tag + ("_chunks" if use_chunks else "")


def _query_to_qid(query_text: str) -> str | None:
    """Find the qid for an exact query text from queries.json."""
    with open(QUERIES_PATH) as f:
        queries = json.load(f)
    for q in queries:
        if q["text"].strip().lower() == query_text.strip().lower():
            return q["qid"]
    return None


# ---------------------------------------------------------------------------
# CLI entry-point for quick tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "data analyst intern python SQL"
    print(f"Query: {query}")
    print("Top 5 semantic results:")
    for doc_id, score in semantic_search(query, k=5):
        print(f"  {doc_id}: {score:.4f}")
