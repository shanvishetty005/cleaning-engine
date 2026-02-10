import pandas as pd
import re
from pathlib import Path


INPUT_PATH = "datasets/reference/importer_needs_review.csv"
OUTPUT_PATH = "datasets/reference/company_master_additions.csv"


# -------------------------
# Heuristic brand reducer
# -------------------------
def suggest_standardized_name(core: str) -> str:
    if not isinstance(core, str):
        return core

    name = core.upper().strip()

    # remove country words
    COUNTRY_WORDS = [
        "INDIA", "INDONESIA", "MALAYSIA", "PHILIPPINES",
        "THAILAND", "VIETNAM", "BRAZIL", "MEXICO",
        "TANZANIA", "RUSSIA", "UAE"
    ]

    words = name.split()
    words = [w for w in words if w not in COUNTRY_WORDS]

    name = " ".join(words)

    # collapse long legal phrases
    name = re.sub(r"\bCOMPANY\b", "", name)
    name = re.sub(r"\bLABORATORIES\b", "LABS", name)
    name = re.sub(r"\bLAB SOLUTIONS\b", "LABS", name)

    name = re.sub(r"\s+", " ", name).strip()

    # brand heuristics
    BRAND_RULES = {
        "MAC NELS": "MAC NELS",
        "MERCK": "MERCK",
        "SIGMA ALDRICH": "SIGMA-ALDRICH",
        "PROCTER": "PROCTER & GAMBLE",
        "UNILEVER": "UNILEVER",
        "CLARIANT": "CLARIANT",
        "DKSH": "DKSH",
        "MEGASETIA": "MEGASETIA AGUNG",
        "KYROVET": "KYROVET LABORATORIES",
        "MOLECULES ANALYTICAL": "MOLECULES ANALYTICAL",
        "HOMEPRO": "HOMEPRO",
        "QUIMICA ISA": "QUIMICA ISA",
        "KEDS": "KEDS",
        "ALNAIM": "ALNAIM DRUG",
        "BAJA": "BAJA FUR",
        "NEW DAY": "NEW DAY INTERNATIONAL",
    }

    for key, std in BRAND_RULES.items():
        if key in name:
            return std

    # fallback → first 2 words
    return " ".join(name.split()[:2])


# -------------------------
# Build master additions
# -------------------------
def build_master_additions():
    df = pd.read_csv(INPUT_PATH)

    if "unmapped_core_name" not in df.columns:
        raise ValueError("unmapped_core_name column missing")

    core_names = (
        df["unmapped_core_name"]
        .dropna()
        .astype(str)
        .str.upper()
        .str.strip()
        .unique()
    )

    rows = []

    for core in core_names:
        std = suggest_standardized_name(core)

        rows.append({
            "core_name": core,
            "standardized_name": std
        })

    out_df = pd.DataFrame(rows).sort_values("core_name")

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUTPUT_PATH, index=False)

    print("✅ Master additions file created:")
    print(OUTPUT_PATH)
    print(f"Rows: {len(out_df)}")


if __name__ == "__main__":
    build_master_additions()
