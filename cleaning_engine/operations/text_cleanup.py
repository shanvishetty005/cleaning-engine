import pandas as pd

def trim_text(df: pd.DataFrame) -> pd.DataFrame:
    
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)          # prevents errors on NaN
                .str.strip()          # trims spaces
                .replace("nan", pd.NA)  # converts back to real NULL
            )
    return df
