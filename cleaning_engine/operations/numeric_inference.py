import pandas as pd
import re
from cleaning_engine.heuristics.numeric_heuristic import should_convert_to_numeric


NULL_TOKENS = {
    "", "NA", "N/A", "NULL", "NONE", "NAN",
    "not_a_number", "not_a_numeric"
}


# -----------------------------------
# Numeric Cleaner
# -----------------------------------

def clean_numeric_value(x):
    """
    Strong numeric cleaner

    Handles:
    $434 → 434
    ₹12,400 → 12400
    USD -23870.13 → -23870.13
    --233 → -233
    12kg → 12
    garbage → NA
    """

    if pd.isna(x):
        return pd.NA

    s = str(x).strip()

    if s.upper() in NULL_TOKENS:
        return pd.NA

    # remove commas
    s = s.replace(",", "")

    # detect negativity by odd minus count
    minus_count = s.count("-")
    is_negative = minus_count % 2 == 1

    # keep only digits and dots
    s = re.sub(r"[^0-9.]", "", s)

    # fix multiple dots
    if s.count(".") > 1:
        first, *rest = s.split(".")
        s = first + "." + "".join(rest)

    if s == "" or s == ".":
        return pd.NA

    if is_negative:
        s = "-" + s

    return s


# -----------------------------------
# Sign Consistency Fixer
# -----------------------------------

def _align_sign(df, a, b):
    if a in df.columns and b in df.columns:
        mask = (df[a] < 0) & (df[b] > 0)
        df.loc[mask, b] = -df.loc[mask, b]

        mask = (df[a] > 0) & (df[b] < 0)
        df.loc[mask, b] = -df.loc[mask, b]


# -----------------------------------
# Main Numeric Conversion Engine
# -----------------------------------

def infer_numeric_columns(df: pd.DataFrame):

    converted_cols = []

    for col in df.columns:
        series = df[col]

        # skip datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            continue

        if should_convert_to_numeric(series):

            cleaned = series.apply(clean_numeric_value)
            numeric = pd.to_numeric(cleaned, errors="coerce")

            # convert only if meaningful
            if numeric.notna().mean() >= 0.2:
                df[col] = numeric.fillna(0)
                converted_cols.append(col)

    # -----------------------------------
    # Cross-field sign consistency
    # -----------------------------------

    _align_sign(df, "fob_value", "usd_fob")
    _align_sign(df, "cif_value", "usd_cif")

    # -----------------------------------
    # Physical columns must be non-negative
    # -----------------------------------

    NON_NEGATIVE_COLS = [
        "gross_weight",
        "net_weight",
        "quantity",
        "package_amount"
    ]

    for col in NON_NEGATIVE_COLS:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].abs()

    return df, converted_cols
