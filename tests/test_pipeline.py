import pandas as pd
from src.bm25_search import bm25_search, tokenize
from src.skills import extract_skills
from risk.risk_report import risk_report


def test_tokenize_keeps_tech_terms():
    assert tokenize("C++ scikit-learn Node.js", "norm") == ["c++", "scikit-learn", "node.js"]


def test_internship_normalised():
    assert "intern" in tokenize("data analyst internship", "norm")


def test_bm25_returns_k_sorted():
    res = bm25_search("data analyst internship python sql", 5)
    assert len(res) == 5 and res[0][1] >= res[-1][1]


def test_skills():
    assert {"python", "sql"} <= extract_skills("Need Python and SQL, plus scikit-learn")
    assert "java" not in extract_skills("JavaScript developer")


def test_risk_report_format():
    doc = pd.read_parquet("data/processed/corpus.parquet").doc_id.iloc[0]
    r = risk_report(doc)
    assert r["level"] in {"high", "medium", "low", "insufficient_info"}
    assert 0 <= r["classifier_probability"] <= 1 and "disclaimer" in r