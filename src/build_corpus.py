"""Build data/processed/corpus.parquet from the raw EMSCAD csv.
Run: python -m src.build_corpus"""
import re, html, hashlib, warnings
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.model_selection import StratifiedGroupKFold

warnings.filterwarnings("ignore")          # BeautifulSoup warns on text that looks like a URL

RAW = "data/raw/fake_job_postings.csv"
OUT = "data/processed/corpus.parquet"
MIN_WORDS = 20

TEXT_COLS = ["title", "location", "department", "salary_range", "company_profile",
             "description", "requirements", "benefits", "employment_type",
             "required_experience", "required_education", "industry", "function"]

URL_RE = re.compile(r"#URL_\w+#")
EMAIL_RE = re.compile(r"#EMAIL_\w+#")
PHONE_RE = re.compile(r"#PHONE_\w+#")


def clean_text(s: str) -> str:
    s = html.unescape(str(s))                         # &amp; -> &
    s = URL_RE.sub(" [URL] ", s)                      # hide random hash from search
    s = EMAIL_RE.sub(" [EMAIL] ", s)
    s = PHONE_RE.sub(" [PHONE] ", s)
    s = BeautifulSoup(s, "lxml").get_text(" ")        # strip HTML tags
    s = re.sub(r"\s+", " ", s).strip()                # collapse whitespace
    return s


def main():
    df = pd.read_csv(RAW)
    n_raw = len(df)
    print("raw rows:", n_raw)

    for c in TEXT_COLS:
        df[c] = df[c].fillna("").astype(str)

    # 1) flags BEFORE cleaning (cleaning removes the tokens)
    raw_all = df.description + " " + df.requirements + " " + df.company_profile + " " + df.benefits
    df["has_url_token"] = raw_all.str.contains(URL_RE).astype(int)
    df["has_email_token"] = raw_all.str.contains(EMAIL_RE).astype(int)
    df["has_phone_token"] = raw_all.str.contains(PHONE_RE).astype(int)

    # 2) clean text columns
    for c in ["title", "description", "requirements", "company_profile", "benefits"]:
        df[c] = df[c].map(clean_text)

    # 3) search_text = title + description + requirements
    df["search_text"] = df.title + ". " + df.description + " Requirements: " + df.requirements
    df["search_text"] = df.search_text.str.strip()

    # 4) drop near-empty documents
    n_words = df.search_text.str.split().str.len()
    short = n_words < MIN_WORDS
    print("dropped (too short):", short.sum(), "| of which fraud:", df.loc[short, "fraudulent"].sum())
    df = df[~short].copy()

    # 5) deduplicate BEFORE splitting
    key = (df.title + df.description + df.requirements).str.lower().str.replace(r"\s+", "", regex=True)
    df["dedup_key"] = key.map(lambda s: hashlib.md5(s.encode("utf-8")).hexdigest())
    dup = df.duplicated(subset="dedup_key", keep="first")
    print("dropped (duplicates):", dup.sum(), "| of which fraud:", df.loc[dup, "fraudulent"].sum())
    df = df[~dup].copy()

    # 6) ids and source info
    df["doc_id"] = "emscad_" + df.job_id.astype(str)
    df["source"] = "emscad"
    df["snapshot_date"] = ""
    df["url"] = ""
    df = df.reset_index(drop=True)

    # 7) train/test split, stratified, same company never on both sides
    group = df.company_profile.map(lambda s: hashlib.md5(s.lower().encode()).hexdigest() if s else "")
    group = group.where(group != "", df.doc_id)       # empty profile -> its own group
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    train_idx, test_idx = next(sgkf.split(df, df.fraudulent, groups=group))
    df["split"] = "train"
    df.loc[test_idx, "split"] = "test"

    df["skills"] = None                               # filled in Block 5

    cols = ["doc_id", "source", "snapshot_date", "url", "title", "search_text",
            "company_profile", "benefits", "location", "employment_type",
            "required_experience", "skills", "fraudulent", "split",
            "has_url_token", "has_email_token", "has_phone_token",
            "telecommuting", "has_company_logo", "has_questions"]
    out = df[cols]
    out.to_parquet(OUT, index=False)

    # 8) summary numbers for docs/decisions.md
    print("final rows:", len(out), "(started with", n_raw, ")")
    print(out.groupby("split").fraudulent.agg(["count", "sum", "mean"]))


if __name__ == "__main__":
    main()