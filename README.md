# Trust-Aware Internship Search (IR & Semantic Web, 25M21CA119)

Search and rank job postings with BM25, show matching/missing skills, and show transparent
warning signs (rules + classifier). Warnings are signals, not proof of fraud.
Data: fixed EMSCAD corpus (Vidros et al., 2017, Future Internet 9(1):6), 2012-2014, one platform,
mostly English/US. No live scraping.

## Install
python -m venv .venv ; activate it ; pip install -r requirements.txt
Python version used: 3.12

## Data
Download `fake_job_postings.csv` from Kaggle (shivamb/real-or-fake-fake-jobposting-prediction)
into `data/raw/`. Check the licence shown on the Kaggle page.

## Run in order
python -m src.build_corpus
python -m src.make_queries
python -m src.coverage_check
python -m src.skills
python -m src.bm25_search
python -m risk.eval_rules
python -m risk.train_classifier
python -m risk.risk_report          # ~15 min for all postings
python -m src.final_check
streamlit run app/streamlit_app.py

After labelling (data/eval/labels_*.csv): python -m src.make_qrels ; python -m src.eval_bm25

## Folders
data/raw (never edited) | data/processed (corpus, queries, skills) | runs | risk | src | app | tests | docs | reports

## Limits
Old data, one platform, English only. Risk output is a warning only. Rule and classifier results
are for EMSCAD and are not validated on current postings.