import pandas as pd

def standardize_no_column(df: pd.DataFrame, summary: dict):
    """
    Ensures 'no' column starts from 1 and is strictly ascending.
    Runs after duplicates/empty rows removed.
    """
    if "no" not in df.columns:
        df.insert(0, "no", range(1, len(df) + 1))
        summary["no_column_created"] = True
        summary["no_column_reassigned"] = True
        return df

    old_no = df["no"].copy()

    df["no"] = range(1, len(df) + 1)

    changed = (old_no.astype(str) != df["no"].astype(str)).sum()
    summary["no_column_reassigned"] = True
    summary["no_values_changed_count"] = int(changed)

    return df
