import os
import pandas as pd

from cleaning_engine.pipeline import run_pipeline
from cleaning_engine.operations.comparison_report import generate_comparison_report
from cleaning_engine.operations.column_name_standardizer import standardize_column_names


DEFAULT_CONFIG = {
    "remove_duplicates": True,
    "remove_empty_rows": True,
    "normalize_nulls": True,
    "trim_text": True,
    "standardize_columns": True,
    "standardize_companies": True,
    "convert_numeric": True,
    "standardize_dates": True,
    "standardize_no": True
}


# -------------------------------------------------
# ✅ Power BI formatter layer (NEW)
# -------------------------------------------------
def make_powerbi_ready(df: pd.DataFrame) -> pd.DataFrame:

    keep_cols = [
        "no",
        "arrival_date",
        "importer_name",
        "importer_country",
        "exporter_name",
        "exporter_country",
        "country_of_origin",
        "product_details_short",
        "usd_fob",
        "usd_cif",
        "gross_weight",
        "net_weight",
        "quantity",
        "package_amount"
    ]

    existing = [c for c in keep_cols if c in df.columns]

    pb_df = df[existing].copy()

    # business-friendly rename
    pb_df = pb_df.rename(columns={
        "product_details_short": "product",
        "usd_fob": "fob_usd",
        "usd_cif": "cif_usd"
    })

    return pb_df


# -------------------------------------------------
# MAIN JOB
# -------------------------------------------------
def run_cleaning_job(input_csv_path: str, output_dir: str = "outputs", config: dict | None = None):

    if config is None:
        config = DEFAULT_CONFIG

    os.makedirs(output_dir, exist_ok=True)

    cleaned_output_path = os.path.join(output_dir, "cleaned_file.csv")
    powerbi_output_path = os.path.join(output_dir, "cleaned_for_powerbi.csv")
    comparison_output_path = os.path.join(output_dir, "comparison_report.csv")

    # -----------------------------
    # READ RAW DATA (robust parser)
    # -----------------------------
    raw_df = pd.read_csv(
        input_csv_path,
        keep_default_na=False,
        engine="python",
        on_bad_lines="warn"
    )

    raw_df_copy = raw_df.copy()

    # -----------------------------
    # RUN PIPELINE
    # -----------------------------
    cleaned_df, summary = run_pipeline(raw_df, config)

    # -----------------------------
    # SAVE FULL CLEANED FILE
    # (engineering / audit version)
    # -----------------------------
    cleaned_df.to_csv(cleaned_output_path, index=False)

    # -----------------------------
    # ✅ POWER BI CURATED FILE
    # -----------------------------
    powerbi_df = make_powerbi_ready(cleaned_df)

    # fill nulls safely for BI tools
    string_cols = powerbi_df.select_dtypes(include=["object", "string"]).columns
    powerbi_df[string_cols] = powerbi_df[string_cols].fillna("NULL")

    powerbi_df.to_csv(powerbi_output_path, index=False)

    # -----------------------------
    # COMPARISON REPORT
    # -----------------------------
    raw_for_compare = standardize_column_names(raw_df_copy.copy())
    cleaned_for_compare = cleaned_df.copy()

    generate_comparison_report(
        raw_df=raw_for_compare,
        cleaned_df=cleaned_for_compare,
        output_path=comparison_output_path
    )

    outputs = {
        "cleaned_file": cleaned_output_path,
        "powerbi_file": powerbi_output_path,
        "comparison_report": comparison_output_path,
    }

    return cleaned_df, summary, outputs
