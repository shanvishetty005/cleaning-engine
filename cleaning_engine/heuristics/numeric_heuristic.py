import pandas as pd

def should_convert_to_numeric(series: pd.Series) -> bool:
    """
    Convert column if it looks numeric after cleaning.
    Designed for sparse enterprise datasets.
    """
    non_null = series.dropna().astype(str)

    if non_null.empty:
        return False

    # Remove commas and spaces
    cleaned = non_null.str.replace(",", "", regex=False).str.strip()

    # Attempt numeric coercion
    parsed = pd.to_numeric(cleaned, errors="coerce")

    # If at least 20% of total rows become numeric → convert
    return parsed.notna().mean() >= 0.2
