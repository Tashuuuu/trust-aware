"""risk_report(doc_id) -> dict ; build all: python -m risk.risk_report"""
import json, joblib
import numpy as np
import pandas as pd
from risk.rules import run_rules
from risk.train_classifier import clf_text

DISCLAIMER = "These are warning signs, not proof of fraud."
_state = {}


def _load():
    if not _state:
        df = pd.read_parquet("data/processed/corpus.parquet").set_index("doc_id", drop=False)
        _state["df"] = df
        _state["model"] = joblib.load("risk/model.joblib")
        _state["thr"] = json.load(open("risk/threshold.json"))["threshold"]
        _state["probs"] = pd.read_parquet("risk/probs.parquet").set_index("doc_id").prob.to_dict()
        tr = pd.read_parquet("risk/probs.parquet").merge(df.reset_index(drop=True)[["doc_id", "fraudulent", "split"]], on="doc_id")
        tr = tr[tr.split == "train"].sort_values("prob", ascending=False).reset_index(drop=True)
        prec = tr.fraudulent.cumsum() / (np.arange(len(tr)) + 1)
        ok = tr.prob[prec >= 0.5]
        _state["thr_high"] = float(ok.min()) if len(ok) else 1.0
    return _state


def top_terms(text: str, n: int = 5) -> list:
    pipe = _load()["model"]
    vec, clf = pipe.named_steps["tfidf"], pipe.named_steps["clf"]
    X = vec.transform([text])
    contrib = X.multiply(clf.coef_[0].reshape(1, -1)).tocsr()
    idx, vals = contrib.indices, contrib.data
    names = vec.get_feature_names_out()
    order = np.argsort(-vals)[:n]
    return [names[idx[i]] for i in order if vals[i] > 0]


def risk_report(doc_id: str) -> dict:
    s = _load()
    row = s["df"].loc[doc_id]
    text = row.search_text + " " + row.company_profile + " " + row.benefits
    prob = s["probs"].get(doc_id)
    if prob is None:                                   # non-EMSCAD document
        prob = float(s["model"].predict_proba([text])[0, 1])
    signals = run_rules(row.search_text, row.company_profile, row.has_email_token, row.has_url_token)

    n_words = len(row.search_text.split())
    n_med = sum(x["severity"] == "medium" for x in signals)
    if n_words < 40:
        level = "insufficient_info"
    elif prob > s["thr_high"]:
        level = "high"
    elif prob > s["thr"] or n_med >= 2 or any(x["severity"] == "high" for x in signals):
        level = "medium"
    else:
        level = "low"
    return {"doc_id": doc_id, "level": level, "classifier_probability": round(float(prob), 3),
            "signals": signals, "top_terms": top_terms(text), "disclaimer": DISCLAIMER}


if __name__ == "__main__":
    import sys, time
    ids = _load()["df"].doc_id.tolist()
    if "--sample" in sys.argv:               # quick timing test
        ids = ids[:300]
    reports, t0 = {}, time.time()
    for i, d in enumerate(ids, 1):
        reports[d] = risk_report(d)
        if i % 500 == 0 or i == len(ids):
            print(f"{i}/{len(ids)} done, {time.time() - t0:.0f}s elapsed", flush=True)
    if "--sample" not in sys.argv:
        json.dump(reports, open("risk/risk_reports.json", "w"))
    print(pd.Series([r["level"] for r in reports.values()]).value_counts())