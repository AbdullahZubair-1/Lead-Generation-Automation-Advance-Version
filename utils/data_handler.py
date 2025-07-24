import pandas as pd
import io

def clean_and_export_data(df):
    # Convert unhashable columns (like lists) to strings for deduplication
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df[col] = df[col].apply(str)
    df = df.drop_duplicates()
    csv = df.to_csv(index=False)
    return io.BytesIO(csv.encode('utf-8')) 