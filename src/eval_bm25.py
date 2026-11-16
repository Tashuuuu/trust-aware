"""Evaluate BM25 versions. Run: python -m src.eval_bm25"""
import json, os, sys
from src.metrics import evaluate

if not os.path.exists("data/eval/qrels.json"):
    sys.exit("data/eval/qrels.json not found yet. Finish labelling and run `python -m src.make_qrels` first.")
qrels = json.load(open("data/eval/qrels.json"))
os.makedirs("reports", exist_ok=True)
for mode in ["plain", "norm", "stem"]:
    run = json.load(open(f"runs/bm25_{mode}.json"))
    res = evaluate(run, qrels)
    print("\n=== BM25", mode, "===")
    print(res.round(3).to_string(index=False))
    res.to_csv(f"reports/bm25_{mode}_eval.csv", index=False)