"""Per-rule precision / recall. Use TRAIN while designing. Use --test once at the very end.
Run: python -m risk.eval_rules   or   python -m risk.eval_rules --test"""
import sys
import pandas as pd
from risk.rules import run_rules

split = "test" if "--test" in sys.argv else "train"
df = pd.read_parquet("data/processed/corpus.parquet")
df = df[(df.source == "emscad") & (df.split == split)]

fired = df.apply(lambda r: {s["name"] for s in run_rules(r.search_text, r.company_profile,
                                                         r.has_email_token, r.has_url_token)}, axis=1)
names = sorted(set().union(*fired))
n_fraud, n_real = int(df.fraudulent.sum()), int((df.fraudulent == 0).sum())
rows = []
for n in names:
    f = fired.map(lambda s: n in s)
    tp = int((f & (df.fraudulent == 1)).sum()); fp = int((f & (df.fraudulent == 0)).sum())
    rows.append({"rule": n, "fires": tp + fp, "on_fraud": tp, "on_real": fp,
                 "precision": round(tp / (tp + fp), 3) if tp + fp else 0,
                 "recall": round(tp / n_fraud, 3),
                 "real_fire_rate": round(fp / n_real, 3)})
res = pd.DataFrame(rows).sort_values("precision", ascending=False)
print(f"split={split} fraud={n_fraud} real={n_real}")
print(res.to_string(index=False))
res.to_csv(f"reports/rules_{split}.csv", index=False)