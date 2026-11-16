import pandas as pd

def test_corpus():
    df = pd.read_parquet("data/processed/corpus.parquet")
    assert df.doc_id.is_unique
    assert (df.search_text.str.split().str.len() >= 20).all()
    assert set(df.split.unique()) <= {"train", "test"}
    print("fraud rows:", df.fraudulent.sum())