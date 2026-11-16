"""Skill lexicon + extraction.
Run once to build lexicon and fill the corpus: python -m src.skills"""
import re, pathlib
import pandas as pd

LEX_PATH = pathlib.Path("data/processed/skills_lexicon.csv")
CORPUS = "data/processed/corpus.parquet"

DEFAULT = {
    "python": ["python"], "sql": ["sql"], "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"], "mongodb": ["mongodb"],
    "java": ["java"], "javascript": ["javascript"], "typescript": ["typescript"],
    "c++": ["c++"], "c#": ["c#"], "php": ["php"], "ruby": ["ruby"], "html": ["html"], "css": ["css"],
    "react": ["react", "reactjs", "react.js"], "node.js": ["node.js", "nodejs"],
    "angular": ["angular"], ".net": [".net", "dotnet"], "django": ["django"], "flask": ["flask"],
    "excel": ["excel", "ms excel", "microsoft excel"], "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"], "pandas": ["pandas"], "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "tensorflow": ["tensorflow"], "pytorch": ["pytorch"], "keras": ["keras"],
    "machine learning": ["machine learning", "ml"], "deep learning": ["deep learning"],
    "nlp": ["nlp", "natural language processing"], "computer vision": ["computer vision"],
    "statistics": ["statistics", "statistical"], "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization", "data visualisation"],
    "data entry": ["data entry"], "git": ["git", "github"], "docker": ["docker"],
    "kubernetes": ["kubernetes"], "aws": ["aws", "amazon web services"], "azure": ["azure"],
    "gcp": ["gcp", "google cloud"], "linux": ["linux"], "spark": ["spark", "pyspark"],
    "hadoop": ["hadoop"], "rest api": ["rest api", "restful"], "agile": ["agile", "scrum"],
    "communication": ["communication skills", "communication"],
    "teamwork": ["teamwork", "team player"], "problem solving": ["problem solving", "problem-solving"],
    "seo": ["seo"], "social media": ["social media"], "content writing": ["content writing"],
    "customer service": ["customer service", "customer support"],
    "testing": ["manual testing", "qa testing", "software testing"], "selenium": ["selenium"],
    "photoshop": ["photoshop"], "accounting": ["accounting", "tally"],
    "typing": ["typing speed", "typing"],
}


def ensure_lexicon():
    if not LEX_PATH.exists():
        pd.DataFrame({"skill": list(DEFAULT), "aliases": ["|".join(v) for v in DEFAULT.values()]}) \
            .to_csv(LEX_PATH, index=False)


def _load():
    ensure_lexicon()
    lex = pd.read_csv(LEX_PATH)
    alias2skill = {}
    for _, r in lex.iterrows():
        for a in str(r.aliases).split("|"):
            alias2skill[a.strip().lower()] = r.skill
    aliases = sorted(alias2skill, key=len, reverse=True)       # longest first
    pat = re.compile(r"(?<![a-z0-9+#])(" + "|".join(re.escape(a) for a in aliases) + r")(?![a-z0-9+#])")
    return alias2skill, pat


_ALIAS2SKILL, _PAT = _load()


def extract_skills(text: str) -> set:
    return {_ALIAS2SKILL[m.group(1)] for m in _PAT.finditer(str(text).lower())}


def match_skills(user_skills: set, posting_skills: set) -> dict:
    return {"matched": sorted(user_skills & posting_skills),
            "missing": sorted(user_skills - posting_skills),
            "extra_in_posting": sorted(posting_skills - user_skills)}


if __name__ == "__main__":
    df = pd.read_parquet(CORPUS)
    df["skills"] = df.search_text.map(lambda t: sorted(extract_skills(t)))
    df.to_parquet(CORPUS, index=False)
    print("postings with >=1 skill:", (df.skills.str.len() > 0).mean().round(3))
    print(df.skills.explode().value_counts().head(20))
    # eyeball check: look at 30 random postings and judge correctness yourself
    for _, r in df.sample(30, random_state=42).iterrows():
        print("\n", r.doc_id, "|", r.title[:70], "\n  skills:", r.skills)