import pandas as pd

KNOWN_FORMATS = [
    "%d-%m-%Y",  # 15-04-2024
    "%d/%m/%Y",  # 15/04/2024
    "%Y-%m-%d",  # 2024-04-15
    "%Y/%m/%d",  # 2024/04/15
    "%m-%d-%Y",  # 04-15-2024
]

def normalize_date_column(series: pd.Series, output_format="%Y-%m-%d"):
    raw = series.astype(str).str.strip()

    # clean junk tokens
    raw = raw.replace(
        ["", "NA", "N/A", "null", "NULL", "None", "nan", "NaN"],
        pd.NA
    )

    # start with all missing
    result = pd.Series(pd.NA, index=raw.index, dtype="object")

    # try each known format and fill missing progressively
    for fmt in KNOWN_FORMATS:
        parsed = pd.to_datetime(raw, errors="coerce", format=fmt)
        result = result.fillna(parsed.dt.strftime(output_format))

    return result