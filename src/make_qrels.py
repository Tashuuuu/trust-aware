"""Merge labels into data/eval/qrels.json and print kappa on the core queries.
Files in data/eval/: labels_akriti.csv, labels_bhawna.csv (columns qid,doc_id,label)
optional labels_resolved.csv (same columns) = labels you fixed together after discussion.
Run: python -m src.make_qrels"""
import json, pathlib
import pandas as pd
from sklearn.metrics import cohen_kappa_score

E = pathlib.Path("data/eval")
a = pd.read_csv(E / "labels_akriti.csv").rename(columns={"label": "a"})
b = pd.read_csv(E / "labels_bhawna.csv").rename(columns={"label": "b"})
both = a.merge(b, on=["qid", "doc_id"], how="outer")

core = {q["qid"] for q in json.load(open("data/processed/queries.json")) if q["set"] == "core"}
overlap = both.dropna(subset=["a", "b"])
overlap = overlap[overlap.qid.isin(core)]
if len(overlap):
    print("docs labelled by both (core):", len(overlap))
    print("kappa (unweighted):", round(cohen_kappa_score(overlap.a, overlap.b), 3))
    print("kappa (quadratic): ", round(cohen_kappa_score(overlap.a, overlap.b, weights="quadratic"), 3))
    print("disagreements:", int((overlap.a != overlap.b).sum()))

resolved = {}
rp = E / "labels_resolved.csv"
if rp.exists():
    r = pd.read_csv(rp)
    resolved = {(x.qid, x.doc_id): int(x.label) for x in r.itertuples()}

qrels = {}
for x in both.itertuples():
    key = (x.qid, x.doc_id)
    if key in resolved:
        lab = resolved[key]
    elif pd.notna(x.a) and pd.notna(x.b):
        if x.a != x.b:
            raise SystemExit(f"Unresolved disagreement {key}: {x.a} vs {x.b}. Add to labels_resolved.csv")
        lab = int(x.a)
    else:
        lab = int(x.a if pd.notna(x.a) else x.b)
    qrels.setdefault(x.qid, {})[x.doc_id] = lab

json.dump(qrels, open(E / "qrels.json", "w"), indent=1)
for q, d in qrels.items():
    print(q, "judged:", len(d), "relevant(>=1):", sum(v >= 1 for v in d.values()))