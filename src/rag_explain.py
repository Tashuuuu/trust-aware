"""
src/rag_explain.py
Bhawna — B9, B10: RAG explanation generation with guardrails.

Usage:
    from src.rag_explain import explain
    result = explain("data analyst intern python SQL", ["emscad_101", "emscad_88"])
"""

import hashlib
import json
import os
import re
from pathlib import Path

ROOT        = Path(__file__).resolve().parent.parent
CORPUS_PATH  = ROOT / "data" / "processed" / "corpus.parquet"
PROMPT_PATH  = ROOT / "rag" / "prompts" / "explain_v1.txt"
CACHE_DIR    = ROOT / "rag" / "cache"
ANSWERS_PATH = ROOT / "rag" / "answers.json"

ABSTAIN_THRESHOLD = 0.30   # cosine similarity; update in decisions_bhawna.md after testing
EVIDENCE_CHUNKS   = 2       # top chunks per posting to pass to LLM


# ---------------------------------------------------------------------------
# Evidence selection
# ---------------------------------------------------------------------------

def _get_top_chunks(doc_id: str, query: str,
                    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
                    n: int = EVIDENCE_CHUNKS) -> list[dict]:
    """Return top-n chunks for a posting most similar to the query."""
    from sentence_transformers import SentenceTransformer
    import numpy as np
    import pandas as pd
    from src.semantic import chunk_text

    corpus = pd.read_parquet(CORPUS_PATH).set_index("doc_id")
    if doc_id not in corpus.index:
        return []
    text   = str(corpus.loc[doc_id, "search_text"])
    chunks = chunk_text(text)

    model  = SentenceTransformer(model_name)
    q_vec  = model.encode([query], normalize_embeddings=True).astype("float32")
    c_vecs = model.encode(chunks, normalize_embeddings=True).astype("float32")
    scores = (c_vecs @ q_vec.T).ravel()

    top_idxs = scores.argsort()[::-1][:n]
    return [{"chunk_id": f"{doc_id}#c{i}", "text": chunks[i], "score": float(scores[i])}
            for i in top_idxs]


# ---------------------------------------------------------------------------
# LLM call with caching
# ---------------------------------------------------------------------------

def _cache_path(prompt: str) -> Path:
    h = hashlib.sha256(prompt.encode()).hexdigest()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{h}.json"


def _call_llm(prompt: str) -> str:
    """Call Gemini API (or cached). Returns raw LLM text."""
    cp = _cache_path(prompt)
    if cp.exists():
        with open(cp) as f:
            return json.load(f)["response"]

    # --- Gemini API (Option A) ---
    try:
        import google.generativeai as genai
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in .env")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",   # update if name changes
            generation_config={"temperature": 0, "response_mime_type": "application/json"},
        )
        response = model.generate_content(prompt)
        raw = response.text
    except Exception as e:
        print(f"⚠️  LLM call failed: {e}. Returning insufficient_evidence.")
        raw = json.dumps({"insufficient_evidence": True, "error": str(e)})

    with open(cp, "w") as f:
        json.dump({"prompt_hash": _cache_path(prompt).stem, "response": raw}, f)
    return raw


# ---------------------------------------------------------------------------
# Guardrails (B9, Step 5)
# ---------------------------------------------------------------------------

class GuardrailStats:
    json_fail: int = 0
    bad_source: int = 0
    quote_mismatch: int = 0
    skills_overwritten: int = 0
    defamation_blocked: int = 0

    def report(self):
        print(f"Guardrail failures — JSON:{self.json_fail}  "
              f"bad_source:{self.bad_source}  quote:{self.quote_mismatch}  "
              f"skills_overwrite:{self.skills_overwritten}  "
              f"defamation:{self.defamation_blocked}")


_stats = GuardrailStats()


def _check_and_fix(answer: dict, evidence_chunks: list[dict],
                   matched_skills: list[str], missing_skills: list[str]) -> dict:
    """Apply all guardrail checks. Returns (possibly fixed) answer dict."""
    chunk_map = {c["chunk_id"]: c["text"] for c in evidence_chunks}
    valid_ids  = set(chunk_map)

    # Check 2: source ids exist
    for eq in answer.get("evidence_quotes", []):
        if eq.get("source") not in valid_ids:
            answer["_guardrail_bad_source"] = True
            _stats.bad_source += 1

    # Check 3: quotes match cited chunks (word-for-word after normalising)
    for eq in answer.get("evidence_quotes", []):
        src = eq.get("source", "")
        quote = re.sub(r"\s+", " ", eq.get("quote", "")).strip().lower()
        if src in chunk_map:
            chunk_norm = re.sub(r"\s+", " ", chunk_map[src]).lower()
            if quote and quote not in chunk_norm:
                eq["_unsupported"] = True
                _stats.quote_mismatch += 1

    # Check 4: overwrite skills with computed versions
    if answer.get("matched_skills") != matched_skills:
        answer["matched_skills"] = matched_skills
        _stats.skills_overwritten += 1
    if answer.get("missing_skills") != missing_skills:
        answer["missing_skills"] = missing_skills
        _stats.skills_overwritten += 1

    # Check 5: block defamation
    BAD_WORDS = ["scam", "fraudster", "is fake", "is a fraud", "is fraudulent"]
    text_to_check = (answer.get("why_relevant", "") + " " + answer.get("warning_notes", "")).lower()
    for w in BAD_WORDS:
        if w in text_to_check:
            answer["_defamation_blocked"] = True
            answer["warning_notes"] = (
                "Warning: this posting shows signals that may indicate risk. "
                "This is a warning only; it is not proof of fraud."
            )
            _stats.defamation_blocked += 1
            break

    return answer


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def explain(query: str, doc_ids: list[str],
            model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> dict:
    """
    B9 public function.
    Returns {doc_id: answer_dict} for each doc_id.
    """
    import pandas as pd
    from src.skills import extract_skills   # Akriti's function

    try:
        risk_reports = json.loads((ROOT / "risk" / "risk_reports.json").read_text())
    except Exception:
        risk_reports = {}

    prompt_template = PROMPT_PATH.read_text()
    corpus = pd.read_parquet(CORPUS_PATH).set_index("doc_id")

    results = {}
    for doc_id in doc_ids:
        # -- Evidence selection --
        chunks = _get_top_chunks(doc_id, query, model_name=model_name)
        if not chunks or chunks[0]["score"] < ABSTAIN_THRESHOLD:
            results[doc_id] = {
                "doc_id": doc_id,
                "insufficient_evidence": True,
                "why_relevant": "",
                "matched_skills": [],
                "missing_skills": [],
                "warning_notes": "",
                "evidence_quotes": [],
            }
            continue

        # -- Computed skills --
        text = str(corpus.loc[doc_id, "search_text"]) if doc_id in corpus.index else ""
        query_skills  = extract_skills(query)
        posting_skills = extract_skills(text)
        matched = sorted(set(query_skills) & set(posting_skills))
        missing = sorted(set(query_skills) - set(posting_skills))

        # -- Risk evidence --
        risk_ev = risk_reports.get(doc_id, {}).get("evidence", "No risk signals detected.")

        # -- Build prompt --
        evidence_passages = "\n\n".join(
            f"[{c['chunk_id']}]\n{c['text']}" for c in chunks
        )
        prompt = (prompt_template
                  .replace("{{query}}", query)
                  .replace("{{doc_id}}", doc_id)
                  .replace("{{matched_skills}}", json.dumps(matched))
                  .replace("{{missing_skills}}", json.dumps(missing))
                  .replace("{{risk_evidence}}", str(risk_ev))
                  .replace("{{evidence_passages}}", evidence_passages))

        # -- LLM call + JSON parse --
        raw = _call_llm(prompt)
        try:
            answer = json.loads(raw)
        except json.JSONDecodeError:
            # Retry once
            raw2 = _call_llm(prompt + "\n\nRemember: return ONLY valid JSON.")
            try:
                answer = json.loads(raw2)
            except json.JSONDecodeError:
                _stats.json_fail += 1
                answer = {"doc_id": doc_id, "insufficient_evidence": True,
                          "_parse_failed": True}

        # -- Guardrails --
        answer = _check_and_fix(answer, chunks, matched, missing)
        # Attach chunk texts for the app
        answer["_chunk_texts"] = {c["chunk_id"]: c["text"] for c in chunks}
        results[doc_id] = answer

    return results


def run_all_and_save():
    """Generate and cache RAG answers for all queries × top-5 results (B9)."""
    import json as _json
    from src.semantic import hybrid_search
    from pathlib import Path as _Path

    queries_path = ROOT / "data" / "processed" / "queries.json"
    with open(queries_path) as f:
        queries = _json.load(f)

    all_answers = {}
    for q in queries:
        print(f"\n--- {q['qid']}: {q['text']}")
        top5 = [doc_id for doc_id, _ in hybrid_search(q["text"], k=5)]
        answers = explain(q["text"], top5)
        all_answers[q["qid"]] = {"query": q["text"], "answers": answers}

    ANSWERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ANSWERS_PATH, "w") as f:
        _json.dump(all_answers, f, indent=2)
    print(f"\nAll answers saved → {ANSWERS_PATH}")
    _stats.report()


if __name__ == "__main__":
    # Quick test: abstain query
    result = explain("deep sea welding internship", ["emscad_101"])
    print(json.dumps(result, indent=2))
