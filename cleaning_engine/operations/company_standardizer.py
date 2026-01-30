import pandas as pd

print(">>> COMPANY STANDARDIZER RUNNING")


def standardize_company_names(
    df: pd.DataFrame,
    column_name: str,
    master_path: str,
    standardized_col: str,
    review_flag_col: str,
    review_output_path: str
) -> pd.DataFrame:
    """
    Standardize company names using a master file.
    Unknown companies are flagged and exported for review.
    """

    # -----------------------------
    # Load & normalize master
    # -----------------------------
    master_df = pd.read_csv(master_path)

    master_df["core_name"] = (
        master_df["core_name"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    master_df["standardized_name"] = (
        master_df["standardized_name"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    master_map = dict(
        zip(master_df["core_name"], master_df["standardized_name"])
    )

    standardized_values = []
    needs_review = []

    # -----------------------------
    # Row-wise standardization
    # -----------------------------
    for raw in df[column_name]:

        # Skip NA / NULL-like safely
        if pd.isna(raw):
            standardized_values.append(raw)
            needs_review.append(False)
            continue

        key = str(raw).upper().strip()

        if key in {"NA", "N/A", "NULL", ""}:
            standardized_values.append(None)
            needs_review.append(False)
            continue

        if key in master_map:
            standardized_values.append(master_map[key])
            needs_review.append(False)
        else:
            standardized_values.append(key)
            needs_review.append(True)

    df[standardized_col] = standardized_values
    df[review_flag_col] = needs_review

    # -----------------------------
    # Generate separate review file
    # -----------------------------
    review_df = (
        df.loc[df[review_flag_col], column_name]   # Series
        .dropna()
        .astype(str)
        .str.upper()
        .drop_duplicates()
        .sort_values()
        .to_frame(name="unmapped_core_name")
    )

    if not review_df.empty:
        review_df.to_csv(review_output_path, index=False)

    return df
