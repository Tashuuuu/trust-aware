"""Run: streamlit run app/streamlit_app.py"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from src.bm25_search import bm25_search
from src.skills import extract_skills, match_skills
from risk.risk_report import risk_report

# Bhawna's parts: adjust these import paths to her real module names
try:
    from src.hybrid import hybrid_search, semantic_search
except Exception:
    hybrid_search = semantic_search = None
try:
    from rag.explain import explain
except Exception:
    explain = None

st.set_page_config(page_title="Trust-Aware Internship Search", layout="wide")


@st.cache_data
def load_corpus():
    return pd.read_parquet(ROOT / "data/processed/corpus.parquet").set_index("doc_id", drop=False)


@st.cache_data
def cached_risk(doc_id):
    return risk_report(doc_id)


corpus = load_corpus()
st.title("Trust-Aware Internship Search")
st.caption("Warnings are signals, not proof of fraud.")

methods = ["BM25"] + (["Semantic", "Hybrid"] if hybrid_search else [])
with st.sidebar:
    query = st.text_input("Search", "entry-level data analyst internship requiring Python and SQL")
    skills_in = st.text_input("Your skills (comma-separated)", "python, sql")
    k = st.slider("Results", 3, 10, 5)
    method = st.selectbox("Method", methods)
    show_risk = st.toggle("Show risk", True)
    compare = st.toggle("Compare BM25 vs Hybrid", False, disabled=hybrid_search is None)


def search(m, q, k):
    if m == "BM25":
        return bm25_search(q, k)
    return (semantic_search if m == "Semantic" else hybrid_search)(q, k)


def render(results, user_skills, key):
    for rank, (doc_id, score) in enumerate(results, 1):
        r = corpus.loc[doc_id]
        with st.container(border=True):
            st.subheader(f"{rank}. {r.title}")
            st.caption(f"source: {r.source} {r.snapshot_date} | score {score:.2f} | {doc_id}")
            if r.url:
                st.markdown(f"[original posting]({r.url})")
            ms = match_skills(user_skills, set(r.skills) if r.skills is not None else set())
            if ms["matched"]:
                st.markdown("Matching: " + " ".join(f":green[{s}]" for s in ms["matched"]))
            if ms["missing"]:
                st.markdown("Missing: " + " ".join(f":orange[{s}]" for s in ms["missing"]))
            if show_risk:
                rep = cached_risk(doc_id)
                msg = f"Risk: {rep['level']} (model {rep['classifier_probability']:.2f})"
                {"high": st.error, "medium": st.warning}.get(rep["level"], st.success)(msg)
                for sg in rep["signals"]:
                    st.write(f"- **{sg['name']}** ({sg['severity']}): {sg['evidence']}")
                if rep["top_terms"]:
                    st.caption("Words that raised the model score: " + ", ".join(rep["top_terms"]))
                st.caption(rep["disclaimer"])
            with st.expander("Show full posting text"):
                st.write(r.search_text)


if st.button("Search") or query:
    user_skills = {s.strip().lower() for s in skills_in.split(",") if s.strip()}
    user_skills |= extract_skills(query)
    if compare and hybrid_search:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### BM25"); render(search("BM25", query, k), user_skills, "a")
        with c2:
            st.markdown("### Hybrid"); render(search("Hybrid", query, k), user_skills, "b")
    else:
        res = search(method, query, k)
        if explain:
            try:
                ans = explain(query, [d for d, _ in res])
                st.info(ans.get("answer", ans) if isinstance(ans, dict) else ans)
            except Exception as e:
                st.caption(f"Explanation unavailable: {e}")
        render(res, user_skills, "main")

st.divider()
st.caption("Data: EMSCAD (Vidros et al., 2017), 2012–2014, one platform, mostly English/US. "
           "No live scraping. Risk output = warning signs only.")