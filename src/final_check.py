"""Run: python -m src.final_check
Prints PASS/FAIL per check and writes docs/results_summary.md (numbers for your report)."""
import json, os, subprocess, sys, traceback
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_fscore_support, confusion_matrix

LINES, RESULTS = [], []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LINES.append(s)


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    return (r.stdout + r.stderr).strip(), r.returncode


def check(name, fn):
    out(f"\n## {name}")
    try:
        ok = fn()
        RESULTS.append((name, ok is not False))
    except Exception:
        out(traceback.format_exc())
        RESULTS.append((name, False))


CORPUS = "data/processed/corpus.parquet"


def files():
    need = ["data/raw/fake_job_postings.csv", CORPUS, "data/processed/queries.json",
            "data/processed/skills_lexicon.csv", "runs/bm25.json", "runs/bm25_plain.json",
            "runs/bm25_norm.json", "runs/bm25_stem.json", "risk/model.joblib", "risk/threshold.json",
            "risk/probs.parquet", "risk/risk_reports.json", "reports/pr_curve.png",
            "README.md", "requirements.txt", "pytest.ini"]
    miss = [p for p in need if not os.path.exists(p)]
    out("missing:", miss or "none")
    return not miss


def corpus():
    df = pd.read_parquet(CORPUS)
    n_raw = len(pd.read_csv("data/raw/fake_job_postings.csv"))
    out(f"raw rows {n_raw} -> final {len(df)} (removed {n_raw - len(df)})")
    sp = df.groupby("split").fraudulent.agg(["count", "sum", "mean"]).round(4)
    out(sp.to_string())
    tr = set(df[(df.split == "train") & (df.company_profile != "")].company_profile.str.lower())
    te = set(df[(df.split == "test") & (df.company_profile != "")].company_profile.str.lower())
    out("shared company profiles train/test:", len(tr & te), "| duplicate search_text:", df.search_text.duplicated().sum())
    out("postings with >=1 skill:", round((df.skills.map(lambda s: len(s) if s is not None else 0) > 0).mean(), 3))
    return df.doc_id.is_unique and not (tr & te) and not df.search_text.duplicated().any() \
        and abs(sp["mean"].iloc[0] - sp["mean"].iloc[1]) < 0.005


def baseline():
    from src import bm25_search as b
    a = json.load(open("runs/bm25.json"))
    n = json.load(open("runs/bm25_norm.json"))
    out("BASELINE in code:", b.BASELINE, "| runs/bm25.json equals norm run:", a == n)
    return b.BASELINE == "norm" and a == n


def bm25_view():
    df = pd.read_parquet(CORPUS).set_index("doc_id")
    qs = json.load(open("data/processed/queries.json"))
    run = json.load(open("runs/bm25.json"))
    for q in qs[:5]:
        out(f"{q['qid']}: {q['text']}")
        for d, s in sorted(run[q["qid"]].items(), key=lambda x: -x[1])[:5]:
            out(f"   {s:6.2f} | {df.loc[d, 'title'][:70]}")


def rules():
    from risk.rules import TEXT_RULES
    sev = {r.name: r.severity for r in TEXT_RULES}
    out("severities:", sev)
    txt, _ = sh([sys.executable, "-m", "risk.eval_rules"])
    out(txt)
    return sev["chat_app_contact"] == "low" and sev["scam_job_type"] == "low"


def classifier():
    df = pd.read_parquet(CORPUS)
    thr = json.load(open("risk/threshold.json"))["threshold"]
    pr = pd.read_parquet("risk/probs.parquet").merge(df[["doc_id", "fraudulent", "split"]], on="doc_id")
    far_test = None
    for sp in ["train", "test"]:
        s = pr[pr.split == sp]
        y, p = s.fraudulent.values, s.prob.values
        pred = (p > thr).astype(int)
        P, R, F, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
        tn, fp, fn, tp = [int(v) for v in confusion_matrix(y, pred, labels=[0, 1]).ravel()]
        far = fp / (fp + tn)
        out(f"{sp}: n={len(s)} fraud={int(y.sum())} PR-AUC={average_precision_score(y, p):.3f} "
            f"precision={P:.3f} recall={R:.3f} F1={F:.3f} false_alarm_rate={far:.3f} tn/fp/fn/tp={tn}/{fp}/{fn}/{tp}")
        if sp == "test":
            far_test = far
    out("threshold:", round(thr, 4))
    return far_test < 0.10


def levels():
    df = pd.read_parquet(CORPUS)[["doc_id", "fraudulent", "split"]]
    rep = json.load(open("risk/risk_reports.json"))
    df["level"] = df.doc_id.map(lambda d: rep[d]["level"])
    base = df[df.split == "test"].fraudulent.mean()
    share = None
    for sp in ["train", "test"]:
        t = pd.crosstab(df[df.split == sp].level, df[df.split == sp].fraudulent)
        t["fraud_share"] = (t[1] / (t[0] + t[1])).round(3)
        out(sp + ":\n" + t.to_string())
        if sp == "test":
            share = t.loc["high", "fraud_share"] if "high" in t.index else 0
    out(f"test base rate {base:.3f}; high-level fraud share on test {share}")
    return share > 3 * base


def unit_tests():
    txt, rc = sh([sys.executable, "-m", "pytest", "-q", "tests"])
    out(txt[-1500:])
    return rc == 0


def app():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file("../app/streamlit_app.py", default_timeout=240).run()
    out("exceptions:", [e.value for e in at.exception], "| result cards rendered:", len(at.subheader))
    return not at.exception and len(at.subheader) > 0


def repo():
    req = open("requirements.txt").read().lower()
    need = ["pandas", "scikit-learn", "rank-bm25", "streamlit", "pyarrow", "nltk", "beautifulsoup4"]
    out("requirements missing:", [n for n in need if n not in req] or "none")
    files_ = sh(["git", "ls-files"])[0].splitlines()
    big = [(f, round(os.path.getsize(f) / 1e6, 1)) for f in files_ if os.path.exists(f) and os.path.getsize(f) > 20e6]
    bad = [f for f in files_ if f.endswith(".env") or "kaggle.json" in f]
    out("tracked files:", len(files_), "| >20MB:", big, "| sensitive:", bad)
    out("git status (first 15):\n" + "\n".join(sh(["git", "status", "--short"])[0].splitlines()[:15]))
    return not big and not bad and all(n in req for n in need)


for name, fn in [("1 files exist", files), ("2 corpus", corpus), ("3 BM25 baseline = norm", baseline),
                 ("4 BM25 top-5 (norm)", bm25_view), ("5 rules + severities", rules),
                 ("6 classifier", classifier), ("7 risk levels on train/test", levels),
                 ("8 unit tests", unit_tests), ("9 app smoke test", app), ("10 repo hygiene", repo)]:
    check(name, fn)

out("\n## SUMMARY")
for n, ok in RESULTS:
    out(("PASS  " if ok else "FAIL  ") + n)
os.makedirs("docs", exist_ok=True)
open("docs/results_summary.md", "w", encoding="utf-8").write("# Results summary (auto-generated)\n\n```\n" + "\n".join(LINES) + "\n```\n")