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
# ✅ Power BI formatter layer (UPDATED)
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

        # product
        "product_details_short",

        # values
        "usd_fob",
        "usd_cif",

        # weights + UNITS ✅
        "gross_weight",
        "gross_weight_unit",
        "net_weight",
        "net_weight_unit",

        # quantity + UNITS ✅
        "quantity",
        "quantity_unit",

        # packages + UNITS ✅
        "package_amount",
        "packages_unit"
    ]

    existing = [c for c in keep_cols if c in df.columns]
    pb_df = df[existing].copy()

    # -------------------------
    # Business friendly rename
    # -------------------------
    pb_df = pb_df.rename(columns={
        "product_details_short": "product",
        "usd_fob": "fob_usd",
        "usd_cif": "cif_usd"
    })

    # -------------------------
    # Time features (PowerBI loves this)
    # -------------------------
    if "arrival_date" in pb_df.columns:
        pb_df["arrival_date"] = pd.to_datetime(pb_df["arrival_date"], errors="coerce")
        pb_df["year"] = pb_df["arrival_date"].dt.year
        pb_df["month"] = pb_df["arrival_date"].dt.month

    # -------------------------
    # Derived metrics
    # -------------------------
    if "cif_usd" in pb_df.columns and "net_weight" in pb_df.columns:
        pb_df["value_per_kg"] = pb_df["cif_usd"] / pb_df["net_weight"].replace(0, pd.NA)

    if "cif_usd" in pb_df.columns and "quantity" in pb_df.columns:
        pb_df["value_per_unit"] = pb_df["cif_usd"] / pb_df["quantity"].replace(0, pd.NA)

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
    # Engineering / ML / audit version
    # -----------------------------
    cleaned_df.to_csv(cleaned_output_path, index=False)

    # -----------------------------
    # ✅ POWER BI CURATED FILE
    # -----------------------------
    powerbi_df = make_powerbi_ready(cleaned_df)

    # Fill nulls safely for BI tools
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
