"""
src/make_pool.py
Bhawna — B7: Build the pooling sheet for relevance labelling.

Usage:
    python src/make_pool.py

Output:
    data/eval/pool_for_labelling.csv
"""

import json
import random
from pathlib import Path

import pandas as pd

ROOT        = Path(__file__).resolve().parent.parent
RUNS_DIR    = ROOT / "runs"
QUERIES_PATH = ROOT / "data" / "processed" / "queries.json"
CORPUS_PATH  = ROOT / "data" / "processed" / "corpus.parquet"
EVAL_DIR     = ROOT / "data" / "eval"

POOL_DEPTH = 10   # top-N per system per query to include in pool
RANDOM_SEED = 42


def load_run(path: Path) -> dict[str, dict[str, float]]:
    """Load a run JSON: {qid: {doc_id: score}}."""
    with open(path) as f:
        return json.load(f)


def build_pool():
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    # Load queries
    with open(QUERIES_PATH) as f:
        queries = json.load(f)
    qid_to_text = {q["qid"]: q["text"] for q in queries}

    # Discover run files  — add sem and hybrid runs once generated
    run_files = list(RUNS_DIR.glob("*.json"))
    if not run_files:
        print("No run files found in runs/. Run BM25 and semantic first.")
        return

    runs: dict[str, dict[str, dict[str, float]]] = {}
    for rp in run_files:
        runs[rp.stem] = load_run(rp)

    # Load corpus for titles + search_text
    corpus = pd.read_parquet(CORPUS_PATH)
    corpus = corpus.set_index("doc_id")

    pool_rows = []
    for qid, query_text in qid_to_text.items():
        pooled: set[str] = set()
        for system_name, run in runs.items():
            if qid not in run:
                continue
            ranked = sorted(run[qid], key=lambda d: run[qid][d], reverse=True)
            pooled.update(ranked[:POOL_DEPTH])

        for doc_id in pooled:
            if doc_id not in corpus.index:
                continue
            row = corpus.loc[doc_id]
            pool_rows.append({
                "qid":         qid,
                "query":       query_text,
                "doc_id":      doc_id,
                "title":       row.get("title", ""),
                "search_text": str(row.get("search_text", ""))[:1500],
                "full_text":   row.get("search_text", ""),
                "label":       "",   # to be filled by annotator
            })

    # Shuffle rows to hide which system retrieved them
    random.seed(RANDOM_SEED)
    random.shuffle(pool_rows)

    df_pool = pd.DataFrame(pool_rows)
    out_path = EVAL_DIR / "pool_for_labelling.csv"
    df_pool.to_csv(out_path, index=False)
    print(f"Pool saved → {out_path}  ({len(df_pool)} rows, {len(qid_to_text)} queries)")
    return df_pool


if __name__ == "__main__":
    build_pool()
