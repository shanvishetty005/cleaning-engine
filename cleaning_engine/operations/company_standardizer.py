import pandas as pd
import re

print(">>> COMPANY STANDARDIZER RUNNING")


# ---------------------------------
# Legal suffix noise (for matching only)
# ---------------------------------

LEGAL_SUFFIXES = {
    "LTD", "LIMITED", "PVT", "PRIVATE",
    "INC", "LLC", "GMBH", "AG",
    "SDN", "BHD", "PTE", "PTY",
    "SA", "BV", "NV", "SRL", "SPA"
}


def strip_suffix_noise(name: str) -> str:
    """Remove legal suffix tokens to improve matching"""
    words = name.split()
    return " ".join(w for w in words if w not in LEGAL_SUFFIXES)


# ---------------------------------
# Build brand roots from master file
# ---------------------------------

def build_brand_roots(master_df: pd.DataFrame):
    """
    Build brand root list dynamically from standardized_name column
    Example:
        CLARIANT THAILAND LTD → CLARIANT
    """
    roots = set()

    for val in master_df["standardized_name"]:
        if pd.isna(val):
            continue
        root = str(val).split()[0].upper()
        roots.add(root)

    # longer roots first (better matching)
    return sorted(roots, key=len, reverse=True)


def detect_brand_root_from_master(name: str, brand_roots):
    for root in brand_roots:
        if root in name:
            return root
    return None


# ---------------------------------
# Main Standardizer
# ---------------------------------

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
    Brand collapse is driven by master file — not hardcoded.
    """

    # -----------------------------
    # Load master
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

    brand_roots = build_brand_roots(master_df)

    standardized_values = []
    needs_review = []

    # -----------------------------
    # Row-wise standardization
    # -----------------------------
    for raw in df[column_name]:

        # ---- null safe
        if pd.isna(raw):
            standardized_values.append(raw)
            needs_review.append(False)
            continue

        key = str(raw).upper().strip()

        if key in {"NA", "N/A", "NULL", ""}:
            standardized_values.append(None)
            needs_review.append(False)
            continue

        # -------------------------
        # Step 1 — direct master match
        # -------------------------
        if key in master_map:
            standardized_values.append(master_map[key])
            needs_review.append(False)
            continue

        # -------------------------
        # Step 2 — suffix stripped match
        # -------------------------
        key_no_suffix = strip_suffix_noise(key)

        if key_no_suffix in master_map:
            standardized_values.append(master_map[key_no_suffix])
            needs_review.append(False)
            continue

        # -------------------------
        # Step 3 — brand root collapse
        # -------------------------
        brand = detect_brand_root_from_master(key_no_suffix, brand_roots)

        if brand:
            standardized_values.append(brand)
            needs_review.append(False)
            continue

        # -------------------------
        # Step 4 — fallback → review
        # -------------------------
        standardized_values.append(key)
        needs_review.append(True)

    df[standardized_col] = standardized_values
    df[review_flag_col] = needs_review

    # -----------------------------
    # Export review file
    # -----------------------------
    review_df = (
        df.loc[df[review_flag_col], column_name]
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
