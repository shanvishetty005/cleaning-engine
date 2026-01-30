from cleaning_engine.service import run_cleaning_job

if __name__ == "__main__":
    input_path = "datasets/raw/raw_file.csv"
    cleaned_df, summary, outputs = run_cleaning_job(input_path, output_dir="datasets/cleaned")

    print("\n✅ CLEANING SUMMARY")
    for k, v in summary.items():
        print(f"{k}: {v}")

    print("\nFiles generated:")
    print(f"- Cleaned file (ML): {outputs['cleaned_file']}")
    print(f"- Cleaned file (Power BI): {outputs['powerbi_file']}")
    print(f"- Comparison report: {outputs['comparison_report']}")
