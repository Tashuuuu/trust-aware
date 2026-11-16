"""Run: python -m src.checks   (read-only; paste the whole output to Claude)"""
import sys, json, os, subprocess, runpy, traceback
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_fscore_support, confusion_matrix

RAW = "data/raw/fake_job_postings.csv"
CORPUS = "data/processed/corpus.parquet"


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    print((r.stdout + r.stderr).strip()[-3500:])


def section(title):
    def deco(fn):
        print(f"\n{'=' * 10} {title} {'=' * 10}", flush=True)
        try:
            fn()
        except Exception:
            traceback.print_exc()
        return fn
    return deco


@section("1. files exist")
def _():
    need = [RAW, CORPUS, "data/processed/queries.json", "data/processed/skills_lexicon.csv",
            "runs/bm25.json", "runs/bm25_plain.json", "runs/bm25_stem.json",
            "risk/model.joblib", "risk/threshold.json", "risk/probs.parquet",
            "risk/risk_reports.json", "reports/rules_train.csv", "reports/pr_curve.png"]
    for p in need:
        print("OK     " if os.path.exists(p) else "MISSING", p,
              f"{os.path.getsize(p) / 1e6:.1f} MB" if os.path.exists(p) else "")


df = pd.read_parquet(CORPUS)


@section("2. corpus")
def _():
    n_raw = len(pd.read_csv(RAW))
    print("raw rows:", n_raw, "| final rows:", len(df), "| removed:", n_raw - len(df))
    print("doc_id unique:", df.doc_id.is_unique, "| empty search_text:", (df.search_text.str.strip() == "").sum())
    print(df.groupby("split").fraudulent.agg(["count", "sum", "mean"]).round(4))
    print("words per posting:\n", df.search_text.str.split().str.len().describe().round(1))
    tr = set(df[(df.split == "train") & (df.company_profile != "")].company_profile.str.lower())
    te = set(df[(df.split == "test") & (df.company_profile != "")].company_profile.str.lower())
    print("company profiles appearing in BOTH train and test (should be 0):", len(tr & te))
    print("duplicate search_text left (should be 0):", df.search_text.duplicated().sum())
    n_sk = df.skills.map(lambda s: len(s) if s is not None else 0)
    print("skills column filled:", df.skills.notna().mean().round(3), "| postings with >=1 skill:", (n_sk > 0).mean().round(3))
    print("token flags (share of postings):", df[["has_url_token", "has_email_token", "has_phone_token"]].mean().round(3).to_dict())


@section("3. queries and BM25 runs")
def _():
    qs = json.load(open("data/processed/queries.json"))
    print("queries:", len(qs), "| core:", sum(q["set"] == "core" for q in qs))
    for q in qs[:5]:
        print(" ", q["qid"], q["text"])
    run = json.load(open("runs/bm25.json"))
    print("run covers", len(run), "queries; docs per query:", {len(v) for v in run.values()})
    titles = df.set_index("doc_id").title
    for mode in ["plain", "norm", "stem"]:
        r = json.load(open(f"runs/bm25_{mode}.json"))
        for q in qs[:5]:
            top = sorted(r[q["qid"]].items(), key=lambda x: -x[1])[:5]
            print(f"[{mode}] {q['qid']}")
            for d, s in top:
                print(f"   {s:6.2f} | {titles[d][:70]}")


@section("4. tokenizer sanity")
def _():
    from src.bm25_search import tokenize
    for t in ["data analyst internship", "C++ and scikit-learn, Node.js"]:
        print(t, "-> plain:", tokenize(t, "plain"), "| stem:", tokenize(t, "stem"))


@section("5. coverage table")
def _():
    runpy.run_module("src.coverage_check", run_name="__main__")


@section("6. rule precision/recall on TRAIN")
def _():
    sh([sys.executable, "-m", "risk.eval_rules"])


@section("7. classifier (train = out-of-fold, test = held-out)")
def _():
    thr = json.load(open("risk/threshold.json"))["threshold"]
    print("threshold:", round(thr, 4))
    pr = pd.read_parquet("risk/probs.parquet").merge(df[["doc_id", "fraudulent", "split"]], on="doc_id")
    for sp in ["train", "test"]:
        s = pr[pr.split == sp]
        y, p = s.fraudulent.values, s.prob.values
        pred = (p > thr).astype(int)
        P, R, F, _ = precision_recall_fscore_support(y, pred, average="binary", zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
        print(f"{sp}: n={len(s)} fraud={int(y.sum())} PR-AUC={average_precision_score(y, p):.3f} "
              f"precision={P:.3f} recall={R:.3f} F1={F:.3f} false_alarm_rate={fp / (fp + tn):.3f} "
              f"[tn fp fn tp]={tn, fp, fn, tp}")


@section("8. risk reports")
def _():
    rep = json.load(open("risk/risk_reports.json"))
    lv = pd.Series({d: r["level"] for d, r in rep.items()}, name="level")
    print("reports:", len(rep)); print(lv.value_counts(normalize=True).round(3))
    x = df.set_index("doc_id").join(lv)
    print(pd.crosstab(x.level, x.fraudulent))
    for d in [d for d, r in rep.items() if r["level"] == "high"][:2]:
        print(json.dumps(rep[d], indent=1)[:900])


@section("9. unit tests")
def _():
    sh([sys.executable, "-m", "pytest", "-q", "tests"])


@section("10. git hygiene (run `git add .` first)")
def _():
    sh(["git", "status", "--short"])
    files = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.splitlines()
    print("tracked files:", len(files))
    print("tracked files >20 MB:", [(f, round(os.path.getsize(f) / 1e6, 1)) for f in files
                                    if os.path.exists(f) and os.path.getsize(f) > 20e6])
    print("sensitive tracked (should be empty):", [f for f in files if f.endswith(".env") or "kaggle.json" in f])