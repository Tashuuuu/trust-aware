"""BM25 baseline, three versions: 'plain', 'norm' (internship->intern), 'stem'.
Build + run all queries: python -m src.bm25_search"""
import re, json, joblib, pathlib
from functools import lru_cache
import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

CORPUS = "data/processed/corpus.parquet"
QUERIES = "data/processed/queries.json"
# BASELINE = "stem"
BASELINE = "norm"

TOKEN_RE = re.compile(r"[a-z0-9+#]+(?:[.\-][a-z0-9+#]+)*")
STOP = set(ENGLISH_STOP_WORDS)
NORMALISE = {"internship": "intern", "internships": "intern", "interns": "intern"}
_stemmer = PorterStemmer()


@lru_cache(maxsize=None)
def _stem(w: str) -> str:
    return _stemmer.stem(w)


def tokenize(text: str, mode: str = BASELINE) -> list:
    toks = [t for t in TOKEN_RE.findall(str(text).lower()) if t not in STOP]
    if mode == "norm":
        toks = [NORMALISE.get(t, t) for t in toks]
    elif mode == "stem":
        toks = [_stem(NORMALISE.get(t, t)) if t.isalpha() else t for t in toks]
    return toks


def build_index(mode: str):
    df = pd.read_parquet(CORPUS, columns=["doc_id", "search_text"])
    tokens = [tokenize(t, mode) for t in df.search_text]
    bm25 = BM25Okapi(tokens, k1=1.5, b=0.75)
    pathlib.Path("index").mkdir(exist_ok=True)
    joblib.dump((bm25, df.doc_id.tolist()), f"index/bm25_{mode}.joblib")
    return bm25, df.doc_id.tolist()


_cache = {}


def _get(mode):
    if mode not in _cache:
        p = pathlib.Path(f"index/bm25_{mode}.joblib")
        _cache[mode] = joblib.load(p) if p.exists() else build_index(mode)
    return _cache[mode]


def bm25_search(query: str, k: int = 100, mode: str = BASELINE):
    bm25, doc_ids = _get(mode)
    scores = bm25.get_scores(tokenize(query, mode))
    top = np.argsort(scores)[::-1][:k]
    return [(doc_ids[i], float(scores[i])) for i in top]


def run_all(mode: str, k: int = 100) -> dict:
    qs = json.load(open(QUERIES))
    return {q["qid"]: dict(bm25_search(q["text"], k, mode)) for q in qs}


if __name__ == "__main__":
    # tiny sanity test of the intern/internship problem
    print("plain:", tokenize("data analyst internship", "plain"))
    print("stem :", tokenize("data analyst internship", "stem"))
    for mode in ["plain", "norm", "stem"]:
        build_index(mode)
        run = run_all(mode)
        json.dump(run, open(f"runs/bm25_{mode}.json", "w"))
        print(mode, "run saved:", len(run), "queries")
    json.dump(run_all(BASELINE), open("runs/bm25.json", "w"))
    # show top 5 titles for q1 as a human check
    df = pd.read_parquet(CORPUS, columns=["doc_id", "title"]).set_index("doc_id")
    for d, s in bm25_search("entry-level data analyst internship requiring Python and SQL", 5):
        print(round(s, 2), "|", df.loc[d, "title"])