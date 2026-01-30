import pandas as pd

def remove_duplicates(df, summary):
    before = len(df)

    df = df.drop_duplicates(keep="first")

    summary["duplicates_removed"] = before - len(df)
    return df
