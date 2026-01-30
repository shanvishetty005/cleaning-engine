import re
import pandas as pd

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names to snake_case safely.
    """
    new_columns = []
    for col in df.columns:
        col = col.strip()
        col = col.lower()
        col = re.sub(r"[^\w\s]", "", col)
        col = re.sub(r"\s+", "_", col)
        new_columns.append(col)

    df.columns = new_columns
    return df
