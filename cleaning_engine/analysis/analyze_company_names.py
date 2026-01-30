import os
import pandas as pd
from cleaning_engine.operations.company_preclean import preclean_company_name
from cleaning_engine.operations.company_suffix_cleaner import remove_legal_suffixes

os.makedirs("datasets/reference", exist_ok=True)

df = pd.read_csv("datasets/cleaned/cleaned_file.csv")

df["importer_name_preclean"] = preclean_company_name(df["importer_name"])

# STEP 1: Pre-clean analysis
unique_preclean = (
    df["importer_name_preclean"]
    .dropna()
    .sort_values()
    .unique()
)

print(f"Unique importer names (after pre-clean): {len(unique_preclean)}")
for name in unique_preclean[:50]:
    print(name)

pd.DataFrame({"preclean_name": unique_preclean}) \
    .to_csv("datasets/reference/importer_preclean_values.csv", index=False)

# STEP 2: Legal suffix removal
df["importer_core_name"] = remove_legal_suffixes(
    df["importer_name_preclean"]
)

invalid_values = {"", "NAN"}

unique_core = (
    df["importer_core_name"]
    .dropna()
    .astype(str)
    .str.strip()
    .loc[~df["importer_core_name"].isin(invalid_values)]
    .sort_values()
    .unique()
)

print(f"\nUnique importer names (after suffix removal): {len(unique_core)}")
for name in unique_core:
    print(name)

pd.DataFrame({"core_name": unique_core}) \
    .to_csv("datasets/reference/importer_core_names.csv", index=False)
