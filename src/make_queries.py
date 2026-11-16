import json
core = {
    "q1": "entry-level data analyst internship requiring Python and SQL",
    "q2": "machine learning internship for a fresher with Python and scikit-learn",
    "q3": "remote internship with no prior work experience required",
    "q4": "work-from-home data entry role promising high earnings with no experience",
    "q5": "software engineering internship requiring Java and database skills",
}
extra = [
    "data science internship Python pandas",
    "web developer internship JavaScript React",
    "customer support work from home no experience",
    "digital marketing intern social media",
    "finance analyst entry level Excel",
    "quality assurance tester fresher",
    "content writer internship remote",
    "NLP internship",
    "database administrator junior SQL",
    "earn money from home registration fee",
    "deep sea welding internship",
]
qs = [{"qid": k, "text": v, "set": "core"} for k, v in core.items()]
qs += [{"qid": f"q{6+i}", "text": t, "set": "extra"} for i, t in enumerate(extra)]
json.dump(qs, open("data/processed/queries.json", "w"), indent=2)
print(len(qs), "queries saved")