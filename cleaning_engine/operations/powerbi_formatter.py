import pandas as pd


POWERBI_COLUMNS = [
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

    # weights + units
    "gross_weight",
    "gross_weight_unit",
    "net_weight",
    "net_weight_unit",

    # quantity + packages
    "quantity",
    "quantity_unit",
    "package_amount",
    "packages_unit",
]


def build_powerbi_dataset(df: pd.DataFrame) -> pd.DataFrame:

    out = df.copy()

    # -------------------
    # Keep only useful cols
    # -------------------
    cols = [c for c in POWERBI_COLUMNS if c in out.columns]
    out = out[cols]

    # -------------------
    # Add time features
    # -------------------
    if "arrival_date" in out.columns:
        out["arrival_date"] = pd.to_datetime(out["arrival_date"], errors="coerce")
        out["year"] = out["arrival_date"].dt.year
        out["month"] = out["arrival_date"].dt.month

    # -------------------
    # Add derived metrics
    # -------------------
    if "usd_cif" in out.columns and "net_weight" in out.columns:
        out["value_per_kg"] = out["usd_cif"] / out["net_weight"].replace(0, pd.NA)

    if "usd_cif" in out.columns and "quantity" in out.columns:
        out["value_per_unit"] = out["usd_cif"] / out["quantity"].replace(0, pd.NA)

    return out
