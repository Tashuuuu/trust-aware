"""Train the fraud-warning classifier on TRAIN only; evaluate on TEST once.
Run: python -m risk.train_classifier"""
from sklearn.model_selection import StratifiedGroupKFold
import hashlib
import json, joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import (average_precision_score, precision_recall_fscore_support,
                             confusion_matrix, precision_recall_curve)

RS = 42


def make_pipe():
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_features=50000,
                                  sublinear_tf=True, stop_words="english")),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=RS)),
    ])


def clf_text(df):
    return df.search_text + " " + df.company_profile + " " + df.benefits


if __name__ == "__main__":
    df = pd.read_parquet("data/processed/corpus.parquet")
    df = df[df.source == "emscad"].copy()
    df["clf_text"] = clf_text(df)
    tr, te = df[df.split == "train"], df[df.split == "test"]
    print("train:", len(tr), "fraud", int(tr.fraudulent.sum()), "| test:", len(te), "fraud", int(te.fraudulent.sum()))

    pipe = make_pipe()
    grp = tr.company_profile.map(lambda s: hashlib.md5(s.lower().encode()).hexdigest() if s else "")
    grp = grp.where(grp != "", tr.doc_id)
    cv = StratifiedGroupKFold(5, shuffle=True, random_state=RS)
    oof = cross_val_predict(pipe, tr.clf_text, tr.fraudulent, cv=cv, groups=grp,
                            method="predict_proba", n_jobs=-1)[:, 1]
    print("CV average precision (PR-AUC):", round(average_precision_score(tr.fraudulent, oof), 3))

    # 2) threshold from TRAIN real postings: 95th percentile -> ~5% false alarms
    thr = float(np.quantile(oof[tr.fraudulent.values == 0], 0.95))
    print("alert threshold:", round(thr, 3))

    # 3) final model on all train, evaluate on test ONCE
    pipe.fit(tr.clf_text, tr.fraudulent)
    p_test = pipe.predict_proba(te.clf_text)[:, 1]
    pred = (p_test > thr).astype(int)
    y = te.fraudulent.values
    pr, rc, f1, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y, pred).ravel()
    far = fp / (fp + tn)
    print(f"TEST precision={pr:.3f} recall={rc:.3f} F1={f1:.3f} false_alarm_rate={far:.3f}")
    print("confusion [tn fp fn tp]:", tn, fp, fn, tp, "| test PR-AUC:",
          round(average_precision_score(y, p_test), 3))

    p, r, _ = precision_recall_curve(y, p_test)
    plt.plot(r, p); plt.xlabel("recall"); plt.ylabel("precision"); plt.title("PR curve (test)")
    plt.savefig("reports/pr_curve.png", dpi=150)

    # 4) save everything the app needs
    joblib.dump(pipe, "risk/model.joblib")
    json.dump({"threshold": thr}, open("risk/threshold.json", "w"))
    probs = pd.concat([pd.DataFrame({"doc_id": tr.doc_id.values, "prob": oof}),
                       pd.DataFrame({"doc_id": te.doc_id.values, "prob": p_test})])
    probs.to_parquet("risk/probs.parquet", index=False)

    # 5) error analysis helpers: read these by hand
    te = te.assign(p=p_test, pred=pred)
    print("\n--- 10 false positives ---")
    print(te[(te.pred == 1) & (te.fraudulent == 0)].sort_values("p", ascending=False).head(10)[["doc_id", "title", "p"]].to_string())
    print("\n--- 10 false negatives ---")
    print(te[(te.pred == 0) & (te.fraudulent == 1)].sort_values("p").head(10)[["doc_id", "title", "p"]].to_string())