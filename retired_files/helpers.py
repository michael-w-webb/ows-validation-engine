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


