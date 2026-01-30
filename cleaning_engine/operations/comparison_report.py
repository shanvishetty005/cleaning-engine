import pandas as pd


def generate_comparison_report(
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    output_path: str
):
    """
    Generates a detailed comparison report between raw and cleaned data.
    - Cell-level changes
    - Row removal detection
    """

    report_rows = []

    raw_len = len(raw_df)
    clean_len = len(cleaned_df)
    min_rows = min(raw_len, clean_len)

    common_columns = raw_df.columns.intersection(cleaned_df.columns)

    # -----------------------------
    # CELL-LEVEL COMPARISON
    # -----------------------------
    for row_idx in range(min_rows):
        for col in common_columns:
            raw_val = raw_df.iloc[row_idx][col]
            clean_val = cleaned_df.iloc[row_idx][col]

            # Normalize only for comparison
            raw_norm = None if pd.isna(raw_val) else str(raw_val).strip()
            clean_norm = None if pd.isna(clean_val) else str(clean_val).strip()

            if raw_norm != clean_norm:
                report_rows.append({
                    "row_number": row_idx + 1,
                    "column_name": col,
                    "raw_value": raw_val,
                    "cleaned_value": clean_val,
                    "change_type": "value_changed"
                })

    # -----------------------------
    # ROW REMOVAL TRACKING
    # -----------------------------
    if raw_len > clean_len:
        for row_idx in range(clean_len, raw_len):
            report_rows.append({
                "row_number": row_idx + 1,
                "column_name": "__ROW__",
                "raw_value": "ROW_PRESENT",
                "cleaned_value": "ROW_REMOVED",
                "change_type": "row_removed"
            })

    # -----------------------------
    # EXPORT
    # -----------------------------
    report_df = pd.DataFrame(report_rows)

    report_df.to_csv(output_path, index=False)
