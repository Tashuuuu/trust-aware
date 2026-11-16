import json, pandas as pd
df = pd.read_parquet("data/processed/corpus.parquet")[["doc_id", "fraudulent", "split"]]
rep = json.load(open("risk/risk_reports.json"))
df["level"] = df.doc_id.map(lambda d: rep[d]["level"])
for sp in ["train", "test"]:
    t = pd.crosstab(df[df.split == sp].level, df[df.split == sp].fraudulent)
    t["fraud_share"] = (t[1] / (t[0] + t[1])).round(3)
    print(sp); print(t)