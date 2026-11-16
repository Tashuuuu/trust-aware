"""Counts how many postings contain >=3 of the must-have words for each query.
Run: python -m src.coverage_check"""
import pandas as pd

QUERIES = {
    "q1": ["data", "analyst", "python", "sql", "intern"],
    "q2": ["machine learning", "intern", "fresher", "python", "scikit"],
    "q3": ["remote", "intern", "no experience", "entry", "work from home"],
    "q4": ["work from home", "data entry", "earn", "no experience", "weekly"],
    "q5": ["software", "intern", "java", "database", "sql"],
}
MIN_HITS = 3

df = pd.read_parquet("data/processed/corpus.parquet")
low = df.search_text.str.lower()
entry = df.required_experience.str.contains("Internship|Entry", case=False, na=False) | \
        df.title.str.contains("intern", case=False, na=False)

rows = []
for qid, words in QUERIES.items():
    hits = sum(low.str.contains(w.lower(), regex=False).astype(int) for w in words)
    ok = hits >= MIN_HITS
    rows.append({"query": qid, "postings_with_>=3_words": int(ok.sum()),
                 "internship_or_entry_among_them": int((ok & entry).sum()),
                 "fraud_among_them": int(df.loc[ok, "fraudulent"].sum())})
print(pd.DataFrame(rows).to_string(index=False))