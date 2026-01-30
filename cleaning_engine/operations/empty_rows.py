import pandas as pd

def remove_empty_rows(df, summary):
    before = len(df)
    df = df.dropna(how="all")
    removed = before - len(df)

    summary["empty_rows_removed"] = removed
    return df
