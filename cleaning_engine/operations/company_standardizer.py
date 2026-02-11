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

BAD_NAME_TOKENS = {"", "NA", "N/A", "NULL", "NONE", "NAN"}


# ---------------------------------
# Helpers
# ---------------------------------

def normalize_key(x: str) -> str:
    """Safe normalize for matching"""
    if pd.isna(x):
        return ""

    s = str(x).upper().strip()

    if s in BAD_NAME_TOKENS:
        return ""

    # collapse spaces
    s = re.sub(r"\s+", " ", s)

    return s


def strip_suffix_noise(name: str) -> str:
    """Remove legal suffix tokens to improve matching"""
    words = name.split()
    return " ".join(w for w in words if w not in LEGAL_SUFFIXES)


# ---------------------------------
# Build brand roots from master file
# ---------------------------------

def build_brand_roots(master_df: pd.DataFrame):
    roots = set()

    for val in master_df["standardized_name"]:
        key = normalize_key(val)
        if not key:
            continue

        root = key.split()[0]
        if len(root) >= 3:
            roots.add(root)

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

    # -----------------------------
    # Load master
    # -----------------------------
    master_df = pd.read_csv(master_path)

    master_df["core_name"] = master_df["core_name"].apply(normalize_key)
    master_df["standardized_name"] = master_df["standardized_name"].apply(normalize_key)

    master_df = master_df[
        (master_df["core_name"] != "") &
        (master_df["standardized_name"] != "")
    ]

    master_map = dict(
        zip(master_df["core_name"], master_df["standardized_name"])
    )

    # also allow suffix-stripped keys in map
    master_map_suffix = {
        strip_suffix_noise(k): v
        for k, v in master_map.items()
    }

    brand_roots = build_brand_roots(master_df)

    standardized_values = []
    needs_review = []

    # -----------------------------
    # Row-wise standardization
    # -----------------------------
    for raw in df[column_name]:

        key = normalize_key(raw)

        if key == "":
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

        if key_no_suffix in master_map_suffix:
            standardized_values.append(master_map_suffix[key_no_suffix])
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
    # Export clean review file
    # -----------------------------
    review_df = (
        df.loc[df[review_flag_col], standardized_col]
        .dropna()
        .astype(str)
        .map(normalize_key)
        .loc[lambda s: s.str.len() >= 3]
        .drop_duplicates()
        .sort_values()
        .to_frame(name="unmapped_core_name")
    )

    if not review_df.empty:
        review_df.to_csv(review_output_path, index=False)

    return df
