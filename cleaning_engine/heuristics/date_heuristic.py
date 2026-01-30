import pandas as pd
import re

# Accept common date formats safely
DATE_REGEX = re.compile(
    r"""
    ^
    (
        \d{4}[-/]\d{1,2}[-/]\d{1,2} |   # YYYY-MM-DD or YYYY/MM/DD
        \d{1,2}[-/]\d{1,2}[-/]\d{4}     # DD-MM-YYYY or DD/MM/YYYY
    )
    $
    """,
    re.VERBOSE
)

def should_convert_to_date(series: pd.Series) -> bool:
    """
    Decide whether a column should be treated as a date column.
    Ignores NULL / NA / junk values safely.
    """

    # Normalize values
    cleaned = (
        series.dropna()
        .astype(str)
        .str.strip()
        .str.upper()
    )

    if cleaned.empty:
        return False

    # Remove obvious non-date tokens
    cleaned = cleaned[~cleaned.isin({"NA", "N/A", "NULL", ""})]

    if cleaned.empty:
        return False

    # Regex-based detection (CRITICAL FIX)
    matches = cleaned.apply(lambda x: bool(DATE_REGEX.match(x)))

    # Convert only if enough values look like dates
    return matches.mean() >= 0.2
