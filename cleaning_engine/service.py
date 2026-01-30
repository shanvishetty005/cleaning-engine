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


def run_cleaning_job(input_csv_path: str, output_dir: str = "outputs", config: dict | None = None):
    """
    Runs the complete cleaning pipeline and exports:
    - cleaned_file.csv
    - cleaned_for_powerbi.csv
    - comparison_report.csv

    Returns:
        cleaned_df (pd.DataFrame)
        summary (dict)
        outputs (dict): file paths of generated files
    """

    # 1) config handling
    if config is None:
        config = DEFAULT_CONFIG

    # 2) ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    cleaned_output_path = os.path.join(output_dir, "cleaned_file.csv")
    powerbi_output_path = os.path.join(output_dir, "cleaned_for_powerbi.csv")
    comparison_output_path = os.path.join(output_dir, "comparison_report.csv")

    # 3) read raw data
    raw_df = pd.read_csv(input_csv_path, keep_default_na=False)
    raw_df_copy = raw_df.copy()

    # 4) run pipeline
    cleaned_df, summary = run_pipeline(raw_df, config)

    # 5) export cleaned ML output
    cleaned_df.to_csv(cleaned_output_path, index=False)

    # 6) powerbi output (fill NULL safely)
    powerbi_df = cleaned_df.copy()
    string_cols = powerbi_df.select_dtypes(include=["object", "string"]).columns
    powerbi_df[string_cols] = powerbi_df[string_cols].fillna("NULL")
    powerbi_df.to_csv(powerbi_output_path, index=False)

    # 7) comparison report
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
