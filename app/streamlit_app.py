"""Run: streamlit run app/streamlit_app.py"""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from src.bm25_search import bm25_search
from src.skills import extract_skills, match_skills
from risk.risk_report import risk_report

# Bhawna's parts — B5/B6/B9
try:
    from src.semantic import hybrid_search, semantic_search
    _semantic_ok = True
except Exception as _e:
    hybrid_search = semantic_search = None
    _semantic_ok = False

try:
    from src.rag_explain import explain
except Exception as _e2:
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
    show_rag = st.toggle("Show AI explanations (RAG)", True, disabled=explain is None)
    compare = st.toggle("Compare BM25 vs Hybrid", False, disabled=hybrid_search is None)


def search(m, q, k):
    if m == "BM25":
        return bm25_search(q, k)
    return (semantic_search if m == "Semantic" else hybrid_search)(q, k)


def render(results, user_skills, key, explanations=None):
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

            # Clean per-posting RAG explanation
            if show_rag and explanations and doc_id in explanations:
                exp = explanations[doc_id]
                if not exp.get("insufficient_evidence"):
                    why = exp.get("why_relevant", "")
                    warn = exp.get("warning_notes", "")
                    with st.expander("🤖 AI Match Explanation (RAG)", expanded=True):
                        if why:
                            st.markdown(why)
                        if warn:
                            st.caption(f"⚠️ **Note:** {warn}")

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

    def get_explanations(docs):
        if show_rag and explain:
            try:
                return explain(query, docs)
            except Exception as e:
                st.caption(f"Explanation unavailable: {e}")
        return None

    if compare and hybrid_search:
        res_bm25 = search("BM25", query, k)
        res_hybrid = search("Hybrid", query, k)
        exp_bm25 = get_explanations([d for d, _ in res_bm25])
        exp_hybrid = get_explanations([d for d, _ in res_hybrid])
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### BM25"); render(res_bm25, user_skills, "a", exp_bm25)
        with c2:
            st.markdown("### Hybrid"); render(res_hybrid, user_skills, "b", exp_hybrid)
    else:
        res = search(method, query, k)
        exps = get_explanations([d for d, _ in res])
        render(res, user_skills, "main", exps)

st.divider()
st.caption("Data: EMSCAD (Vidros et al., 2017), 2012–2014, one platform, mostly English/US. "
           "No live scraping. Risk output = warning signs only.")