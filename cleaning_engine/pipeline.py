from cleaning_engine.operations.column_name_standardizer import standardize_column_names
from cleaning_engine.operations.duplicates import remove_duplicates
from cleaning_engine.operations.empty_rows import remove_empty_rows
from cleaning_engine.operations.null_normalization import normalize_nulls
from cleaning_engine.operations.text_cleanup import trim_text
from cleaning_engine.operations.numeric_inference import infer_numeric_columns
from cleaning_engine.operations.date_inference import normalize_date_column

from cleaning_engine.heuristics.date_heuristic import should_convert_to_date

from cleaning_engine.operations.company_standardizer import standardize_company_names
from cleaning_engine.operations.company_preclean import preclean_company_name
from cleaning_engine.operations.company_suffix_cleaner import remove_legal_suffixes

from cleaning_engine.operations.no_standardizer import standardize_no_column


def run_pipeline(df, config):
    summary = {}

    # -------------------------
    # BASIC COLUMN CLEANING
    # -------------------------
    if config.get("standardize_columns"):
        df = standardize_column_names(df)
        summary["columns_standardized"] = True

    if config.get("normalize_nulls"):
        df = normalize_nulls(df)
        summary["nulls_normalized"] = True

    if config.get("trim_text"):
        df = trim_text(df)
        summary["text_trimmed"] = True

    # -------------------------
    # COMPANY NAME STANDARDIZATION
    # -------------------------
    if config.get("standardize_companies") and "importer_name" in df.columns:
        print(">>> COMPANY STANDARDIZER RUNNING")

        df["importer_name_preclean"] = preclean_company_name(
            df["importer_name"]
        )

        df["importer_core_name"] = remove_legal_suffixes(
            df["importer_name_preclean"]
        )

        df = standardize_company_names(
            df=df,
            column_name="importer_core_name",
            master_path="datasets/reference/company_master.csv",
            standardized_col="importer_name_standardized",
            review_flag_col="importer_needs_review",
            review_output_path="datasets/reference/importer_needs_review.csv"
        )

        df["importer_name"] = df["importer_name_standardized"]
        summary["company_standardized"] = True

    # -------------------------
    # DATE STANDARDIZATION (MUST BE BEFORE NUMERIC)
    # -------------------------
    if config.get("standardize_dates"):
        print(">>> DATE STANDARDIZER (HEURISTIC) RUNNING")

        date_cols = []

        for col in df.columns:
            try:
                if should_convert_to_date(df[col]):
                    df[col] = normalize_date_column(df[col])
                    date_cols.append(col)
            except Exception as e:
                print(f"[WARN] Date conversion failed for column '{col}': {e}")

        summary["date_columns_converted"] = date_cols

        if date_cols:
            print("Date columns standardized:", date_cols)
            for c in date_cols:
                print(f"SAMPLE [{c}]:", df[c].head(5).tolist())

    # -------------------------
    # NUMERIC TYPE INFERENCE (AFTER DATES)
    # -------------------------
    if config.get("convert_numeric"):
        df, converted = infer_numeric_columns(df)
        summary["numeric_columns_converted"] = converted

    # -------------------------
    # ROW-LEVEL CLEANUP (LAST)
    # -------------------------
    if config.get("remove_empty_rows"):
        df = remove_empty_rows(df, summary)

    if config.get("remove_duplicates"):
        df = remove_duplicates(df, summary)

    # -------------------------
    # NO COLUMN STANDARDIZATION (FINAL)
    # -------------------------
    if config.get("standardize_no", True):
        df = standardize_no_column(df, summary)

    summary["final_rows"] = len(df)
    summary["final_columns"] = len(df.columns)

    return df, summary
