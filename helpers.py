# helpers.py
import pandas as pd

def cross_errors_df(df, colnames, masks, file=None, sheet=None, pairs = None,
                    row_offset=1, column_error_index=None):
    frames = []

    for rule, mask in masks.items():
        idx = df.index[mask.fillna(False)]
        if len(idx) == 0:
            continue

        # Filter out rows that already errored at column level
        if column_error_index:
            bad_rows = set()
            for pair in pairs:
                bad_rows |= column_error_index.get(pair, set())
            idx = [i for i in idx if i not in bad_rows]

        if not len(idx):
            continue

        raw_values = (
            df.loc[idx, colnames]
              .astype("string")
              .fillna("")
              .apply(lambda row: " | ".join([f"{col}: {row[col]}" for col in row.index]),
                     axis=1)
              .values
        )

        frames.append(pd.DataFrame({
            "file": file,
            "sheet": sheet,
            "row_number": df.loc[idx, "row_number"].values,
            "column": ", ".join(colnames),
            "rule": rule,
            "raw_value": raw_values,
            "normalized": None,
        }, index=idx))

    return pd.concat(frames) if frames else pd.DataFrame(
        columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
    )



def normalize_full_name(df, first_col="First Name", last_col="Last Name"):
    """
    Build a normalized 'full_name' column from first/last name fields.
    
    - Lowercases names
    - Strips leading/trailing whitespace
    - Collapses multiple spaces to a single space
    - Drops rows where first name is 'nan' or full name == 'nan nan'
    - Drops rows where full name has no letters
    
    Returns:
        DataFrame with an added 'full_name' column
    """
    df = df.copy()

    # Normalize first and last names separately
    df[first_col] = (
        df[first_col].astype(str).fillna("")
        .str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
    )
    df[last_col] = (
        df[last_col].astype(str).fillna("")
        .str.lower().str.strip().str.replace(r"\s+", " ", regex=True)
    )

    # Drop rows where first name is exactly "nan"
    df = df[df[first_col] != "nan"]

    # Build normalized full name
    df["_full_name"] = (df[last_col] + " " + df[first_col]).str.strip()
    df["_full_name"] = df["full_name"].str.replace(r"\s+", " ", regex=True)

    # Drop invalids
    df = df[df["_full_name"].str.contains(r"[a-z]", na=False)]
    df = df[df["_full_name"] != "nan nan"]

    return df
