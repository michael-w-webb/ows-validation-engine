import pandas as pd
from config import OUTPUT_DIRECTORY

df = pd.read_csv(OUTPUT_DIRECTORY / "find_value_all_sheets_report.csv")

# ---------------------------
# 1. Filter to target column
# ---------------------------
target_col = "Employment Status at exit"

df_col = df[df["column_name"] == target_col].copy()

# Clean blanks
df_col["value_of_interest"] = (
    df_col["value_of_interest"]
    .astype(str)
    .str.strip()
    .replace("", pd.NA)
)

df_col = df_col.dropna(subset=["value_of_interest"])

# ---------------------------
# 2. Sort quarters properly
# ---------------------------
# Convert PY3_Q2 → numeric sort key
def quarter_key(q):
    py, qtr = q.split("_")
    return int(py.replace("PY", "")) * 10 + int(qtr.replace("Q", ""))

df_col["quarter_order"] = df_col["quarter"].apply(quarter_key)

df_col = df_col.sort_values(
    ["participant_id", "quarter_order"]
)

# ---------------------------
# 3. Detect transitions
# ---------------------------
results = []

for (org, pid), group in df_col.groupby(["org", "participant_id"]):
    group = group.reset_index(drop=True)

    for i in range(1, len(group)):
        prev_val = group.loc[i-1, "value_of_interest"]
        curr_val = group.loc[i, "value_of_interest"]

        if (
            prev_val.lower() != "unemployed"
            and curr_val.lower() == "unemployed"
        ):
            results.append({
                "org": org,
                "participant_id": pid,
                "original_value": prev_val,
                "original_first_quarter": group.loc[
                    group["value_of_interest"] == prev_val,
                    "quarter"
                ].iloc[0],
                "new_value": curr_val,
                "new_first_quarter": group.loc[
                    group["value_of_interest"] == "unemployed",
                    "quarter"
                ].iloc[0]
            })

transitions = pd.DataFrame(results)

# ---------------------------
# 4. Org-level summary
# ---------------------------
summary = (
    transitions
    .groupby(["org", "original_value"])
    .size()
    .reset_index(name="count")
)

print(summary)

from pathlib import Path

# Detailed transition records
transitions_path = OUTPUT_DIRECTORY / "employment_status_transitions_to_unemployed.csv"
transitions.to_csv(transitions_path, index=False)

# Org-level summary
summary_path = OUTPUT_DIRECTORY / "employment_status_transition_summary.csv"
summary.to_csv(summary_path, index=False)

print(f"Detailed transitions written to: {transitions_path}")
print(f"Summary written to: {summary_path}")