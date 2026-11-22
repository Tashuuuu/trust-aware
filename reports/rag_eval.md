# RAG Evaluation Report (B10)

> **Task:** Manually assess RAG answers for relevance, evidence support and source attribution.
> **Sample:** All real LLM answers for q1–q5 core queries + q16 (abstain test) = 22 answers.

---

## Scoring Rubric

| Criterion | 0 | 1 | 2 |
|-----------|---|---|---|
| **Relevance** | Explanation wrong / misleading | Partly correct | Correctly explains why posting matches query |
| **Evidence Support** | Most claims unsupported by cited text | Some claims unsupported | Every claim backed by cited chunk |
| **Attribution** | Citation IDs point to wrong posting/chunk | Some IDs wrong | All citation IDs correct |

---

## Summary Table

> Fill in after scoring all rows in `reports/rag_eval_sheet.csv`

| Query | n answers | Avg Relevance | Avg Evidence | Avg Attribution |
|-------|-----------|---------------|--------------|-----------------|
| q1 — data analyst intern | 5 | _TODO_ | _TODO_ | _TODO_ |
| q2 — ML intern fresher | 5 | _TODO_ | _TODO_ | _TODO_ |
| q3 — remote, no experience | 4 | _TODO_ | _TODO_ | _TODO_ |
| q4 — WFH data entry risky | 5 | _TODO_ | _TODO_ | _TODO_ |
| q5 — software eng Java | 2 | _TODO_ | _TODO_ | _TODO_ |
| q16 — deep sea welding (abstain) | 1* | _TODO_ | _TODO_ | _TODO_ |
| **Overall** | **22** | **_TODO_** | **_TODO_** | **_TODO_** |

*q16 answer should be `insufficient_evidence: true` — count as pass if abstained correctly.

---

## Automatic Guardrail Check Results

| Check | Failures | % failure rate |
|-------|----------|----------------|
| JSON parse fail | 0 | 0% |
| Bad source ID | 0 | 0% |
| Quote mismatch | 0 | 0% |
| Skills overwritten by code | 114 | — (expected behaviour) |
| Defamation blocked | 0 | 0% |

> [!NOTE]
> `skills_overwrite = 114` is not a failure — it means the guardrail correctly replaced the LLM's skill suggestions with the code-computed values every time, as designed.

---

## Abstain Test Result

| Query | Expected | Got |
|-------|----------|-----|
| q16 — "deep sea welding internship" | `insufficient_evidence: true` | ✅ All 5 postings abstained |

The abstain threshold (cosine similarity < 0.30) correctly identified that none of the top-5 retrieved postings were genuinely relevant to this query, returning `insufficient_evidence` instead of hallucinating an explanation.

---

## Failure Examples

> Fill in 3 real failure cases after scoring (required for the report).

### Failure 1
- **Query / doc_id:** _TODO_
- **Criterion failed:** _TODO_
- **What went wrong:** _TODO_
- **Example:** _TODO_

### Failure 2
- **Query / doc_id:** _TODO_
- **Criterion failed:** _TODO_
- **What went wrong:** _TODO_

### Failure 3
- **Query / doc_id:** _TODO_
- **Criterion failed:** _TODO_
- **What went wrong:** _TODO_

---

## Limitations

- Sample is small (22 answers from one student); results show a tendency, not proof.
- Labels from a single annotator; no kappa computed for RAG eval (Akriti scored 10 overlapping answers — _TODO: add kappa_).
- The LLM (gemini-3.5-flash, temperature=0) may still paraphrase rather than quote exactly; quote-check guardrail catches word-for-word mismatches but not close paraphrases.
- Abstain threshold (0.30) chosen on a small test set; a different threshold may change the abstain rate.
- RAG does **not prevent hallucination** — it reduces it. We measured how often it still occurred on this small sample.
