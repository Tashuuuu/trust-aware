"""P@5, nDCG@10, MRR. relevant = label >= 1 for P@5 and MRR; nDCG uses graded gains (0/1/2)."""
import math
import pandas as pd


def precision_at_k(ranked, rels, k=5):
    return sum(1 for d in ranked[:k] if rels.get(d, 0) >= 1) / k


def mrr(ranked, rels):
    for i, d in enumerate(ranked, 1):
        if rels.get(d, 0) >= 1:
            return 1.0 / i
    return 0.0


def ndcg_at_k(ranked, rels, k=10):
    dcg = sum((2 ** rels.get(d, 0) - 1) / math.log2(i + 1) for i, d in enumerate(ranked[:k], 1))
    ideal = sorted(rels.values(), reverse=True)[:k]
    idcg = sum((2 ** r - 1) / math.log2(i + 1) for i, r in enumerate(ideal, 1))
    return dcg / idcg if idcg > 0 else 0.0


def evaluate(run: dict, qrels: dict) -> pd.DataFrame:
    rows = []
    for qid, rels in qrels.items():
        if qid not in run:
            continue
        ranked = [d for d, _ in sorted(run[qid].items(), key=lambda x: -x[1])]
        rows.append({"qid": qid,
                     "n_relevant": sum(1 for r in rels.values() if r >= 1),
                     "P@5": precision_at_k(ranked, rels),
                     "nDCG@10": ndcg_at_k(ranked, rels),
                     "MRR": mrr(ranked, rels)})
    df = pd.DataFrame(rows)
    mean = df[["P@5", "nDCG@10", "MRR"]].mean()
    df.loc[len(df)] = {"qid": "MEAN", "n_relevant": None, **mean.to_dict()}
    return df