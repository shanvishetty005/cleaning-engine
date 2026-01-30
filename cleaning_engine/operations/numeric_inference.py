import pandas as pd
import re
from cleaning_engine.heuristics.numeric_heuristic import should_convert_to_numeric

# Keeps only digits, decimal point and minus sign
NUMERIC_CLEAN_REGEX = re.compile(r"[^0-9\.\-]")

NULL_TOKENS = {"", "NA", "N/A", "NULL", "NONE", "NAN", "not_a_number", "not_a_numeric"}


def clean_numeric_value(x):
    """
    Cleans a single numeric value by removing:
    - currency symbols (₹, $, etc.)
    - commas
    - units stuck to numbers (kg, lb)
    - random symbols (#$_+- etc.)
    Keeps:
    - digits
    - one decimal point
    - negative sign
    """
    if pd.isna(x):
        return pd.NA

    s = str(x).strip()

    if s.upper() in NULL_TOKENS:
        return pd.NA

    # Remove commas first
    s = s.replace(",", "")

    # Remove all non-numeric chars except dot and minus
    s = NUMERIC_CLEAN_REGEX.sub("", s)

    # Handle cases where cleaning makes it invalid
    if s in {"", "-", ".", "-.", ".-"}:
        return pd.NA

    return s


def infer_numeric_columns(df: pd.DataFrame):
    """
    Convert numeric-looking columns safely.
    - Removes prefixes/suffixes like ₹, $, kg, commas, random symbols
    - Invalid values → 0 (as per your system requirement)
    - Uses heuristic-based conversion
    """
    converted_cols = []

    for col in df.columns:
        series = df[col]

        # Skip datetime columns
        if pd.api.types.is_datetime64_any_dtype(series):
            continue

        if should_convert_to_numeric(series):

            cleaned = series.apply(clean_numeric_value)

            numeric = pd.to_numeric(cleaned, errors="coerce")

            # Convert only if meaningful
            if numeric.notna().mean() >= 0.2:
                # CORE: NaN → 0
                df[col] = numeric.fillna(0)
                converted_cols.append(col)

    return df, converted_cols
