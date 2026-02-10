import pandas as pd
import re


# -----------------------------
# Filters
# -----------------------------

DROP_EXACT = {
    "NA", "NA+", "N A", "N/A",
    "INDIVIDUALS OR ORGANIZATIONS DO NOT HAVE TAX CODE",
    "CA NHAN TO CHUC KHONG CO MA SO THUE",
    "CHINA",
    "VIETNAM",
    "INDONESIA"
}

DROP_KEYWORDS = [
    "BRANCH",
    "CHI NHANH",
    "PLANT",
    "ROAD",
    "KM",
    "WAREHOUSE",
    "SITE",
    "UNIT",
    "FACTORY"
]


# -----------------------------
# Core Relevance Filter
# -----------------------------

def is_irrelevant_company(name: str) -> bool:

    if not name or not isinstance(name, str):
        return True

    n = name.strip().upper()

    # ---------------------
    # exact junk values
    # ---------------------
    if n in DROP_EXACT:
        return True

    # ---------------------
    # numeric / code rows
    # 30504 / 1250-COM-1 / EXP 907 H
    # ---------------------
    if re.fullmatch(r"[0-9\-/\sA-Z]*", n) and not re.search(r"[A-Z]{3,}", n):
        return True

    # ---------------------
    # mostly digits
    # ---------------------
    digit_ratio = sum(c.isdigit() for c in n) / max(len(n), 1)
    if digit_ratio > 0.6:
        return True

    # ---------------------
    # masked / corrupted names
    # XXMARXXRGAXXC type
    # ---------------------
    if n.count("XX") >= 2:
        return True

    # ---------------------
    # sole proprietor patterns
    # ---------------------
    if n.startswith(("ИП ", "SP ", "IP ")):
        return True

    # ---------------------
    # branch / site indicators
    # ---------------------
    if any(k in n for k in DROP_KEYWORDS):
        return True

    # ---------------------
    # NON-LATIN heavy strings (Cyrillic / Vietnamese etc.)
    # require at least 40% latin letters
    # ---------------------
    latin_letters = len(re.findall(r"[A-Z]", n))
    latin_ratio = latin_letters / max(len(n), 1)

    if latin_ratio < 0.4:
        return True

    # ---------------------
    # too short after clean
    # ---------------------
    if len(n) < 3:
        return True

    return False


# -----------------------------
# Main Preclean Function
# -----------------------------

def preclean_company_name(series: pd.Series) -> pd.Series:
    """
    Pre-clean company names:
    - Uppercase
    - Remove punctuation
    - Remove standalone numbers
    - Normalize spaces
    - Remove irrelevant companies
    """

    cleaned = (
        series
        .astype(str)
        .str.upper()
        .str.replace(r"[^\w\s]", " ", regex=True)
        .str.replace(r"\b\d+\b", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # mark irrelevant
    mask_irrelevant = cleaned.apply(is_irrelevant_company)

    # set junk → NA (pipeline will drop rows)
    cleaned[mask_irrelevant] = pd.NA

    return cleaned
