# RAG Evaluation Report — B10

**Evaluator:** Bhawna Rani (25M21CA119)  
**Date:** 2026-11-22  
**Model:** `gemini-3.5-flash` via `google-genai` SDK  
**Prompt template:** `rag/prompts/explain_v1.txt`  
**Answers file:** `rag/answers.json`  
**Eval sheet:** `reports/rag_eval_sheet.csv`  
**Citation reference:** `reports/rag_citation_reference.md`

---

## 1. Scoring Rubric

Each of the 22 non-abstained answers was scored on three dimensions (0–2 each):

| Dimension | 0 | 1 | 2 |
|-----------|---|---|---|
| **Relevance** | Answer is for a completely different role/skill | Partial match — some criteria met but significant mismatch noted | Fully or mostly relevant to the query |
| **Evidence Support** | No grounded quotes; LLM hallucinated | At least one quote but insufficient to fully support the claim | Quotes from retrieved chunks directly support all major claims |
| **Attribution** | Citations wrong or missing | Minor citation issue (chunk-id mismatch or sparse quote) | All `[doc_id#chunk]` citations correct and traceable |

Maximum score per answer = 6 (2+2+2).

---

## 2. Per-Query Summary

| Query | n | Avg Relevance /2 | Avg Evidence /2 | Avg Attribution /2 | Avg Total /6 |
|-------|---|-----------------|-----------------|-------------------|--------------|
| q1 — entry-level data analyst (Python + SQL) | 5 | 1.60 | 2.00 | 2.00 | 5.60 |
| q2 — ML intern fresher (Python + scikit-learn) | 5 | 0.60 | 2.00 | 2.00 | 4.60 |
| q3 — remote internship, no experience | 4 | 1.00 | 1.75 | 2.00 | 4.75 |
| q4 — WFH data entry, high earnings, no experience | 5 | 1.40 | 2.00 | 1.80 | 5.20 |
| q5 — software engineering intern (Java + databases) | 2 | 1.50 | 2.00 | 2.00 | 5.50 |
| q16 — deep sea welding internship (abstain test) | 1 | 0.00 | 2.00 | 2.00 | 4.00 |
| **OVERALL** | **22** | **1.14** | **1.95** | **1.95** | **5.05** |

---

## 3. Row-Level Scores

| # | qid | doc_id | Rel | Ev | Attr | Notes |
|---|-----|--------|-----|----|----|-------|
| 1 | q1 | emscad_4589 | 2 | 2 | 2 | Clean. Intern + Python matched. SQL correctly noted as missing. |
| 2 | q1 | emscad_9633 | 2 | 2 | 2 | Near-duplicate of emscad_4589 (same agency, Greece). Clean match. |
| 3 | q1 | emscad_4444 | 2 | 2 | 2 | SQL matched, Python missing. Only c0 used but quote is present. Correct. |
| 4 | q1 | emscad_1952 | 1 | 2 | 2 | 4–10yr experience mismatch correctly flagged but still called a match. |
| 5 | q1 | emscad_4834 | 1 | 2 | 2 | 6–8 week project, not a real internship. SQL/Python peripheral. LLM honest. |
| 6 | q2 | emscad_17326 | 1 | 2 | 2 | ML intern but PhD-level, not fresher. LLM correctly flags mismatch. |
| 7 | q2 | emscad_6004 | 0 | 2 | 2 | Python internship but no ML/scikit-learn. `why_relevant` still calls it relevant — LLM inconsistency. |
| 8 | q2 | emscad_2065 | 0 | 2 | 2 | Java/C++, no ML, no Python, no scikit-learn. LLM honest. Retrieval failure. |
| 9 | q2 | emscad_14113 | 2 | 2 | 2 | Best ML match: Python + scikit-learn + ML. Accepts academic/side-project experience. |
| 10 | q2 | emscad_16067 | 0 | 2 | 2 | Distributed systems intern, no ML/Python/scikit-learn. Retrieval failure. |
| 11 | q3 | emscad_1754 | 1 | 2 | 2 | No-experience ✅ but in-person Athens, not remote. LLM flags it. |
| 12 | q3 | emscad_7983 | 2 | 2 | 2 | Remote ✅ + internship ✅. No-experience not explicit but noted by LLM. |
| 13 | q3 | emscad_3860 | 0 | 2 | 2 | Requires After Effects experience, not remote. Mismatch correctly identified. |
| 14 | q3 | emscad_12568 | 1 | 1 | 2 | Unpaid internship ✅ but no remote/no-experience evidence. Sparse chunk, only 1 quote. |
| 15 | q4 | emscad_17552 | 1 | 2 | 1 | Data entry ✅ but requires experience. c0/c1 citation order inconsistency — minor attribution issue. |
| 16 | q4 | emscad_7667 | 2 | 2 | 2 | WFH ✅ data entry ✅ high earnings ✅ training provided ✅. Classic risky post. Clean. |
| 17 | q4 | emscad_2931 | 1 | 2 | 2 | Data entry ✅ but requires experience and not WFH. LLM honest. |
| 18 | q4 | emscad_7658 | 2 | 2 | 2 | Near-duplicate of emscad_7667. WFH ✅ entry-level ✅ high earnings ✅. |
| 19 | q4 | emscad_3136 | 1 | 2 | 2 | High earnings ✅ but Sales role, not data entry. LLM correctly notes mismatch. |
| 20 | q5 | emscad_2065 | 2 | 2 | 2 | Software internship ✅ Java ✅ databases ✅. Clean match. |
| 21 | q5 | emscad_2915 | 1 | 2 | 2 | Java ✅ database ✅ but Field Engineer, not internship. LLM correctly flags. |
| 22 | q16 | emscad_16202 | 0 | 2 | 2 | Pipe Welder — not deep sea, not an internship. LLM answered instead of abstaining. **Abstain failure.** |

---

## 4. Failure Analysis

### 4.1 Relevance failures (score = 0) — Retrieval is to blame

Three answers for **q2** (machine learning internship) scored relevance=0:
- `emscad_6004` — Python internship retrieved despite no ML, no scikit-learn.
- `emscad_2065` — Java/C++ internship retrieved; zero overlap with query intent.
- `emscad_16067` — Distributed systems internship; completely off-topic.

**Root cause:** BM25 and semantic retrieval both struggle when the corpus has very few true ML internship postings (the EMSCAD dataset is 2012-era and ML roles were rare). The retrieved documents share surface-level keyword overlap ("intern", "software") but fail on the specialisation. This is an honest retrieval limitation, not a RAG generation failure — the LLM correctly acknowledged the mismatches in its `warning_notes` and `missing_skills` fields.

For **q3** (remote, no experience):
- `emscad_3860` — After Effects experience required; not remote.

For **q16** (deep sea welding abstain test):
- `emscad_16202` — Retrieval found a Pipe Welder posting. The LLM generated an explanation instead of abstaining. This is an **abstain failure**: the cosine similarity threshold (0.30) was not tight enough to filter out tangentially related trades postings. This is an important limitation to flag.

### 4.2 Evidence failure (score < 2) — Sparse retrieved chunk

- `emscad_12568` (Row 14, q3): The chunk was extremely sparse (single sentence: "has an opening for an unpaid internship (for a school credit)."). Only one quote was available; the LLM said "does not specify" for both remote and no-experience conditions. Evidence score = 1.

### 4.3 Attribution issue

- `emscad_17552` (Row 15, q4): The evidence quotes cited chunks in order c1, c0 (reverse of the chunk list). The factual content was correct but the citation ordering was inconsistent with the chunk presentation. Attribution = 1.

### 4.4 LLM inconsistency (not scored separately)

- `emscad_6004` (Row 7, q2): The `why_relevant` field still said "relevant as a Python graduate internship" even though `missing_skills` correctly listed `machine learning, scikit-learn` and `warning_notes` flagged the mismatch. The LLM was not fully consistent between its own fields in this case.

---

## 5. Key Observations

1. **Evidence and Attribution are strong.** Average scores of 1.95/2.00 for both show that the RAG prompt is reliably grounding answers in retrieved chunks and citing sources correctly. No hallucinated facts were detected across all 22 answers.

2. **Relevance is the bottleneck.** Average relevance = 1.14/2.00. This is not a failure of the generation layer — the LLM consistently identified and disclosed mismatches. The bottleneck is retrieval quality: the top-k documents returned by hybrid RRF include off-topic postings for specialised queries (q2, q3).

3. **The abstain threshold needs tuning.** The q16 Pipe Welder case passed the 0.30 threshold and produced an answer. A tighter threshold (e.g., 0.40) or a secondary LLM-based out-of-scope check would prevent this.

4. **q4 (risk query) works well.** The system correctly surfaced two classic EMSCAD scam/risky postings (`emscad_7667`, `emscad_7658`) with accurate warning notes about unrealistic earnings promises. This validates the trust-aware aspect of the pipeline.

5. **Labels are auto-generated.** `labels_bhawna.csv` and `qrels.json` were generated using a keyword heuristic, not full human annotation. The B8 retrieval metrics should be interpreted as approximate baselines. This is acknowledged as a limitation.

---

## 6. Conclusion

The RAG explanation layer performs reliably on evidence grounding and citation attribution but is constrained by upstream retrieval for specialised, rare-skill queries. The system demonstrates honest behaviour — it discloses mismatches rather than fabricating relevance — which is the core design goal of a trust-aware system.

**Recommended next steps:**
- Tune the abstain cosine threshold to ≥ 0.40 for out-of-domain queries.
- For deployment, add a secondary LLM relevance check before generating explanations.
- Human re-labelling of `qrels.json` for core queries q1–q5 is strongly recommended before citing B8 metrics in a paper.
