import pandas as pd
import re

def preclean_company_name(series: pd.Series) -> pd.Series:
    """
    Pre-clean company names:
    - Uppercase
    - Remove punctuation
    - Remove standalone numbers
    - Normalize spaces
    """
    return (
        series
        .astype(str)
        .str.upper()
        .str.replace(r"[^\w\s]", " ", regex=True)
        .str.replace(r"\b\d+\b", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
