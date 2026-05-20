import pandas as pd
import re

#pa25-119 race columns
race_columns = [
    "Race Ethnicity",
    "211 American Indian / Alaska Native\n(WIOA)",
    "Race1",
    "Race2",
    "Race3",
    "Race4",
    "Race (CWP)",
    "Race - Self-Identify",
    "What is your race? Select one or more:",
    "Race",
    "212 Asian (WIOA)",
    "213 Black / African American (WIOA)",
    "214 Native Hawaiian / Other Pacific Islander\n(WIOA)",
    "215 White (WIOA)"
]


def consolidate_race_ethnicity(
    df,
    race_columns=None,
    ethnicity_columns=None
):
    """
    Consolidate inconsistent race and ethnicity fields into standardized
    Census-compliant classifications, with optional explicit column control.

    ---------------------------------------------------------------------
    PURPOSE
    ---------------------------------------------------------------------
    This function was designed to harmonize race and ethnicity data coming 
    from multiple external data systems, each with their own format, field 
    names, and coding systems (WIOA booleans, multi-select, free text, etc.).

    The function produces two standardized columns:
        • race_consolidated
        • ethnicity_consolidated

    ---------------------------------------------------------------------
    COLUMN SELECTION (IMPORTANT)
    ---------------------------------------------------------------------
    You can allow automatic detection OR explicitly pass in the columns.

    1) AUTOMATIC MODE (default)
        If race_columns is None:
            All columns containing "race" (case-insensitive) 
            except those containing "ethnicity" will be used.
        
        If ethnicity_columns is None:
            All columns containing "ethnicity", "hispanic", or "latino"
            (case-insensitive) will be used.

    2) EXPLICIT MODE
        If you supply:
            race_columns=[...your exact list...]
            ethnicity_columns=[...your exact list...]

        ONLY those columns will be processed.

        This is recommended when you have a known and stable schema
        or want to prevent unintended columns from being picked up.

    Any columns you pass in that are not present in the dataframe are ignored
    and a warning is printed.

    ---------------------------------------------------------------------
    RACE CONSOLIDATION LOGIC (STRICT CENSUS STANDARDS)
    ---------------------------------------------------------------------
    Boolean WIOA fields:
        • 1 → mapped race (inferred from column name)
        • 0 → ignored
        • 9 → "Unknown"
        • any other number → "Unknown"

    Text values:
        Mapped to census categories:
            • White
            • Black or African American
            • American Indian or Alaska Native
            • Asian
            • Native Hawaiian or Other Pacific Islander
            • Some Other Race
            • Multiracial

        Free-text "self-identify" content is appended as-is.

    Final output:
        • Values deduplicated
        • Order preserved
        • Items combined using "; "
        • If empty → "Unknown"

    ---------------------------------------------------------------------
    ETHNICITY CONSOLIDATION LOGIC
    ---------------------------------------------------------------------
    • Hispanic/Latino/Spanish indicators → "Hispanic or Latino"
    • Explicit non-Hispanic indicators → "Not Hispanic or Latino"
    • Hispanic overrides non-Hispanic if both appear
    • If nothing found → "Unknown"

    ---------------------------------------------------------------------
    RETURNS
    ---------------------------------------------------------------------
    The input dataframe, with two additional columns:
        df["race_consolidated"]
        df["ethnicity_consolidated"]
    """

    # ------------------------------
    # Census vocabulary normalization
    # ------------------------------
    census_race_map = {
        "american indian": "American Indian or Alaska Native",
        "alaska native": "American Indian or Alaska Native",
        "native american": "American Indian or Alaska Native",
        "asian": "Asian",
        "black": "Black or African American",
        "african american": "Black or African American",
        "hawaiian": "Native Hawaiian or Other Pacific Islander",
        "pacific islander": "Native Hawaiian or Other Pacific Islander",
        "white": "White",
        "multiracial": "Multiracial",
        "multi-racial": "Multiracial",
        "two or more races": "Multiracial",
        "other": "Some Other Race",
        "prefer to self-identify": "Some Other Race"
    }

    # ----------------------------------------------
    # Determine which columns to use (auto vs manual)
    # ----------------------------------------------
    if race_columns is None:
        race_cols = [
            c for c in df.columns
            if "race" in c.lower() and "ethnicity" not in c.lower()
        ]
    else:
        race_cols = [c for c in race_columns if c in df.columns]
        missing = set(race_columns) - set(race_cols)
        if missing:
            print(f"Warning: These race columns were not found in the dataframe: {missing}")

    if ethnicity_columns is None:
        eth_cols = [
            c for c in df.columns
            if any(x in c.lower() for x in ["ethnicity", "hispanic", "latino"])
        ]
    else:
        eth_cols = [c for c in ethnicity_columns if c in df.columns]
        missing = set(ethnicity_columns) - set(eth_cols)
        if missing:
            print(f"Warning: These ethnicity columns were not found in the dataframe: {missing}")

    # -------------------------
    # Normalization functions
    # -------------------------
    def normalize_race_text(value):
        """Normalize text race values to strict Census categories."""
        if pd.isna(value):
            return None
        v = str(value).strip().lower()
        for keyword, mapped in census_race_map.items():
            if keyword in v:
                return mapped
        return str(value).strip()

    # -------------------------
    # Row-wise race extraction
    # -------------------------
    def extract_race_from_row(row):
        found = []

        for col in race_cols:
            val = row[col]
            if pd.isna(val):
                continue

            # Numeric WIOA logic
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                col_lower = col.lower()

                if val == 1:
                    for keyword, mapped in census_race_map.items():
                        if keyword in col_lower:
                            found.append(mapped)
                            break
                elif val == 9:
                    found.append("Unknown")

                # Ignore 0
                continue

            # Text logic
            if isinstance(val, str):
                normalized = normalize_race_text(val)
                found.append(normalized)

        # Cleanup
        found = [f for f in found if f and f.lower() != "no"]

        if not found:
            return "Unknown"

        # Deduplicate
        seen = set()
        unique = []
        for f in found:
            if f not in seen:
                seen.add(f)
                unique.append(f)

        return "; ".join(unique)

    # ------------------------------
    # Row-wise ethnicity extraction
    # ------------------------------
    def extract_ethnicity_from_row(row):
        found_hisp = False
        found_nonhisp = False

        for col in eth_cols:
            val = row[col]
            if pd.isna(val):
                continue

            v = str(val).lower()

            if any(x in v for x in ["hisp", "latino", "latin", "spanish"]):
                found_hisp = True

            if any(x in v for x in ["non-hisp", "not hisp"]):
                found_nonhisp = True

        if found_hisp:
            return "Hispanic or Latino"
        if found_nonhisp:
            return "Not Hispanic or Latino"
        return "Unknown"

    # ---------------------------------------
    # Apply transformations to the dataframe
    # ---------------------------------------
    df["race_consolidated"] = df.apply(extract_race_from_row, axis=1)
    df["ethnicity_consolidated"] = df.apply(extract_ethnicity_from_row, axis=1)

