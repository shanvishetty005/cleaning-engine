import pandas as pd
import numpy as np

NULL_VALUES = {"", "na", "n/a", "null", "-", ".", "?"}

def normalize_nulls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace common null representations and whitespace-only strings with NaN.
    """

    #  Normalize known null strings (case-insensitive, trimmed)
    df = df.apply(
        lambda col: col.map(
            lambda x: np.nan
            if isinstance(x, str) and x.strip().lower() in NULL_VALUES
            else x
        )
    )

    # Convert whitespace-only strings ("   ") → NaN
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].replace(r"^\s+$", np.nan, regex=True)

    return df
