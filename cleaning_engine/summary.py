def print_summary(summary: dict):
    print("\nCLEANING SUMMARY")
    print("-" * 30)
    for key, value in summary.items():
        print(f"{key}: {value}")
