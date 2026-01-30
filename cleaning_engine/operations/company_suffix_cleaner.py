import pandas as pd
import re

LEGAL_SUFFIXES = [
    "PRIVATE LIMITED", "PVT LTD", "PVT",
    "LIMITED", "LTD",
    "S A", "S R L", "S A C", "S A S",
    "LLC", "INC", "CORP", "CORPORATION",
    "LTDA", "FZCO"
]

def remove_legal_suffixes(series: pd.Series) -> pd.Series:
    s = series.copy()

    for suffix in LEGAL_SUFFIXES:
        pattern = r"\b" + re.escape(suffix) + r"\b"
        s = s.str.replace(pattern, "", regex=True)

    return (
        s.str.replace(r"\s+", " ", regex=True)
         .str.strip()
    )
