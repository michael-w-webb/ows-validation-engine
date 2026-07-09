import os
import sys
import pandas as pd
from datetime import datetime
from config import PROJECT_ROOT


# ================================================================
# ===================== ================================================================# ===================== USER CONFIGURABLE =========================

docstring = """
Workbook Definitions, Label Maps, and Schema Metadata
=====================================================

This module contains the authoritative schema specification for all
CareerConneCT “training data” workbooks supported by the validation
pipeline. It encodes:

    • Canonical  names used throughout the pipeline  
    • All known spelling / formatting variants (“label maps”) that appear
      in provider-submitted Excel files  
    • -level metadata describing expected types, requirements, and
      accepted categorical responses  
    • Workbook-level structure (sheet names, starting rows/s, and
      schema for both *simple format* and *four-sheet format*)  
    • Logic template phrases used by natural-language rule descriptions  

These definitions serve as the central contract between:

    1. **WorkbookLoader** – to map raw header text → canonical names  
    2. **NormalizationEngine / Type classes** – to validate, clean,
       and coerce  values into standardized formats  
    3. **CrossRuleEngine** – to interpret variable types and retrieve the
       correct pandas Series for cross-sheet logic evaluation  
    4. **UI or reporting layers** – to generate intelligible messages and
       consistent descriptions of rule expectations  

-----------------------------------------------------------------------
Label Maps (“labels”)
-----------------------------------------------------------------------

Each sheet definition includes a mapping:

    {
        "Canonical Name": ["Variant A", "Variant B", ...]
    }

The workbook loader uses these maps to:

    • Match raw  headers from provider files  
    • Normalize them into predictable, canonical field names  
    • Tolerate typos, punctuation differences, capitalization,
      OWS-specific export labels, and Salesforce-style field names  

These maps are *lossless*: they never drop fields, they only expand the
set of acceptable  headers.

-----------------------------------------------------------------------
Accepted Responses and Types (“accepted_responses_w_types”)
-----------------------------------------------------------------------

Each canonical  has a metadata block describing:

    • type – one of the defined  classes
      (e.g., "dateTime", "categorical", "boolean", "identifier",
      "hourlyWage", "hoursWorked", "stateID7", "CIPCode", "ONETCode")

    • required – whether the field must be present and non-blank

    • accepted_responses – (optional) list of canonical categorical
      values used by categorical normalization and by
      CrossRuleEngine for logical operations

These definitions are consumed by:

    • Base subclasses during normalization  
    • CrossRuleEngine.get_variable() when creating Variable instances  
    • Rule authoring and error-message templates  

-----------------------------------------------------------------------
Workbook Structure (“workbook_definitions”)
-----------------------------------------------------------------------

The outer `workbook_definitions` object organizes schemas by:

    workbook_type → workbook_format → sheet_name → sheet_definition

For example:

    "training data" →
        "simple format" →
            "Report" → {labels, accepted_responses, starting_row, ...}

        "four sheet format" →
            "Personal Information"
            "Training"
            "Credential"
            "Outcomes"

Each sheet definition includes:

    • labels – a full header normalization map  
    • accepted_responses – the  metadata schema  
    • starting_row – where data begins (allows skipping header clutter)  
    • starting_ – permits partial-sheet ingestion  
    • s_used – reserved for restricting the importable subset

This structure makes it easy for the loader to select the correct
parsing logic depending on which workbook format the provider uploaded.

-----------------------------------------------------------------------
Logic Templates and Expectations
-----------------------------------------------------------------------

Two auxiliary dictionaries define natural-language templates used by
`CrossRuleEngine.describe_logic()`:

    • Logic_Templates – maps operator categories to English snippets
      (e.g., “is in the past”, “is blank”, “is {values}”)

    • Logic_Expectations – indicates whether a field is “required” or
      “should be blank” in IF/THEN constructions

These templates ensure that every rule written in clause-tree syntax can
be rendered into a readable English explanation without custom text.

-----------------------------------------------------------------------
Extending or Updating This Module
-----------------------------------------------------------------------

To add new fields or update schemas:

    1. Add new label variants under the correct sheet’s `labels` dict  
    2. Add (or update) a canonical entry under `accepted_responses`
       with its correct type and accepted categorical responses  
    3. If a new sheet or workbook format is added, create a new
       nested dictionary under `workbook_definitions` following the
       established pattern  
    4. If a new variable type is introduced (e.g., NAICSCode),
       ensure that Base+Variable subclasses support the type
       before referencing it here  

All changes propagate automatically through:

    •  mapping  
    • Data normalization  
    • Cross-sheet rule evaluation  
    • Validation reporting  

This module is therefore the **single source of truth** for schema
consistency across every component of the CareerConneCT validation
pipeline.
"""

# Required column names in the Excel file:
raw_column_name = "Data Element"                     # raw messy values
canon_column_name = "col_name_v0"                    # canonical / normalized values
type_column = "type"                            # type (text, number, categorical, etc.)
accepted_responses_column = "accepted_responses"     # accepted values
multiCategorical_grouped_column = "multiCategorical_grouped_col_name"                 # optional grouping column for multiCategorical columns

# Optional additional metadata columns to aggregate
other_cols_of_interest = [
    "Program",
    "Category",
]

# Excel file to read
DATA_PATH = r"C:\Users\DalyRob\State of Connecticut\OWS HQ - Documents\PA25-119\DataPrep\data_elements_by_program.xlsm"
SHEET_NAME = "data_elements_by_program"

# Output location of the generated Python dictionary file
OUTPUT_PY_PATH = PROJECT_ROOT / "applications" / "pa25_119_grantee_sheets"
OUTPUT_FILENAME = "workbook_definitions.py"

# Names of dictionaries to generate (configurable)
DICT_NAME_LABELS = "simple_format_pa25_119_data_labels"
DICT_NAME_ACCEPTED = "simple_format_pa25_119_data_accepted_responses_w_types"


# ================================================================
# ====================== HELPER FUNCTIONS =========================
# ================================================================

def clean(val):
    """Convert NaN → empty string, trim whitespace, collapse internal spaces."""
    if pd.isna(val):
        return ""
    return " ".join(str(val).split())


def unique_sorted(values):
    """Deduplicate, clean, remove empty strings, sort alphabetically."""
    cleaned = [clean(v) for v in values if clean(v)]
    return sorted(set(cleaned))


def load_excel():
    """Load the Excel sheet and validate required columns exist."""
    df = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME, engine="openpyxl")

    missing = [
        c for c in [
            raw_column_name,
            canon_column_name,
            type_column,
            accepted_responses_column
        ] if c not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    for col in other_cols_of_interest:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' listed in other_cols_of_interest is missing from the Excel file.")

    return df


# ================================================================
# ======================== BUILD DICT #1 ==========================
# ================================================================

def build_raw_to_canonical(df):
    """Dictionary #1: canonical_value → sorted list of raw values."""
    mapping = {}

    for _, row in df.iterrows():
        raw_val = clean(row[raw_column_name])
        canon_val = clean(row[canon_column_name])

        if not canon_val:
            continue

        if canon_val not in mapping:
            mapping[canon_val] = []

        if raw_val:
            mapping[canon_val].append(raw_val)

    # Dedup & alphabetical sort
    for k in mapping:
        mapping[k] = sorted(set(mapping[k]))

    return mapping


# ================================================================
# ======================== BUILD DICT #2 ==========================
# ================================================================

def build_metadata(df):
    """Dictionary #2: canonical_value → metadata."""
    metadata = {}

    for _, row in df.iterrows():
        canon_val = clean(row[canon_column_name])
        if not canon_val:
            continue

        if canon_val not in metadata:
            metadata[canon_val] = {
                "type": "",
                "accepted_responses": None,
            }
            for col in other_cols_of_interest:
                metadata[canon_val][col] = []

        # type
        dtype = clean(row[type_column])
        if dtype and not metadata[canon_val]["type"]:
            metadata[canon_val]["type"] = dtype

        # accepted_responses
        ar = clean(row[accepted_responses_column])
        if ar:
            tokens = [t.strip() for t in ar.split(";") if t.strip()]
            if tokens:
                if metadata[canon_val]["accepted_responses"] is None:
                    metadata[canon_val]["accepted_responses"] = []
                metadata[canon_val]["accepted_responses"].extend(tokens)
       
        # grouped columns --- for multiCategorical types, collect all unique raw values (Data Elements) for the same group. This will be used in processing multicateogrical columns to loop through multiple Data Elements in a single sheet that should be consolidated and one hot encoded
        if dtype == "multiCategorical":
            grouped_col_val = clean(row[multiCategorical_grouped_column])
            if grouped_col_val:
                columns = df[(df[multiCategorical_grouped_column] == grouped_col_val) & (df[raw_column_name] != canon_val)][raw_column_name].unique()  # do not include the canonical value itself in the list of columns
                metadata[canon_val]["columns"] = columns.tolist()

        # other metadata fields
        for col in other_cols_of_interest:
            val = clean(row[col])
            if val:
                metadata[canon_val][col].append(val)

    # Final formatting
    for canon, meta in metadata.items():

        # accepted_responses formatting (UNQUOTED)
        vals = meta["accepted_responses"]
        if not vals:
            meta["accepted_responses"] = None
        else:
            uniq = unique_sorted(vals)
            if len(uniq) == 1:
                meta["accepted_responses"] = uniq[0]  # single unquoted token
            else:
                meta["accepted_responses"] = uniq     # list of unquoted tokens

        # other metadata fields formatting
        for col in other_cols_of_interest:
            vals = unique_sorted(meta[col])
            meta[col] = ";".join(vals) if vals else ""

    return metadata


# ================================================================
# ======================== WRITER FUNCTION ========================
# ================================================================

def write_output(raw_map, metadata):
    """Write a pretty-formatted Python file containing both dictionaries, 
    including an import line referencing all mapping dictionaries used inside accepted_responses."""
    
    OUTPUT_PY_PATH.mkdir(parents=True, exist_ok=True)
    full_path = OUTPUT_PY_PATH / OUTPUT_FILENAME

    # ---------------------------------------------
    # 1. Collect all tokens used in accepted_responses
    # ---------------------------------------------
    used_mappings = set()

    for canon, meta in metadata.items():
        ar = meta.get("accepted_responses")
        if not ar:
            continue

        # Single token
        if isinstance(ar, str):
            used_mappings.add(ar)

        # List of tokens
        elif isinstance(ar, list):
            for token in ar:
                used_mappings.add(token)

    # Convert to sorted list for stable output
    used_mappings = sorted(used_mappings)

    # ---------------------------------------------
    # 2. Write output file
    # ---------------------------------------------
    lines = []

    # Auto-generated 
    lines.append("# Auto-generated dictionary file")
    lines.append(f"# Generated: {datetime.now()}")
    lines.append("")

    lines.append('"""')
    lines.append(docstring)
    lines.append('"""')

    # NEW: import line at the top
    if used_mappings:
        csv_list = ", ".join(used_mappings)
        lines.append(f"from applications.pa25_119_grantee_sheets.workbook_definition_dictionaries import {csv_list}")
        lines.append("")

    lines.append("")

    # ------------------------------
    # 1. Dictionary: labels
    # ------------------------------
    lines.append(f"{DICT_NAME_LABELS} = {{")
    for canon in sorted(raw_map.keys()):
        lines.append(f"    {repr(canon)}: [")
        for raw in raw_map[canon]:
            lines.append(f"        {repr(raw)},")
        lines.append("    ],")
    lines.append("}")
    lines.append("")
    lines.append("")

    # ------------------------------
    # 2. Dictionary: accepted responses w/ metadata
    # ------------------------------
    lines.append(f"{DICT_NAME_ACCEPTED} = {{")
    for canon in sorted(metadata.keys()):
        meta = metadata[canon]

        lines.append(f"    {repr(canon)}: {{")
        lines.append(f"        'type': {repr(meta['type'])},")

        # accepted_responses (UNQUOTED)
        ar = meta["accepted_responses"]
        if ar is None:
            lines.append("        'accepted_responses': None,")
        elif isinstance(ar, str):
            lines.append(f"        'accepted_responses': {ar},")
        else:
            lines.append("        'accepted_responses': [")
            for item in ar:
                lines.append(f"            {item},")
            lines.append("        ],")

        # add list of columns that apply to the multiCategorical canonical column if they are present
        if "columns" in meta and meta["columns"]:
            lines.append(f"        'columns': {repr(meta['columns'])},")

        # additional metadata
        for col in other_cols_of_interest:
            lines.append(f"        '{col}': {repr(meta[col])},")

        lines.append("    },")
    lines.append("}")
    lines.append("")
    lines.append("")

    # ------------------------------
    # 3. Workbook Definitions
    # ------------------------------
    lines.append("workbook_definitions = {")
    lines.append("    'pa25_119 data': {")
    lines.append("        'simple format': {")
    lines.append("            'Report': {")
    lines.append(f"                'labels': {DICT_NAME_LABELS},")
    lines.append(f"                'accepted_responses': {DICT_NAME_ACCEPTED},")
    lines.append("                's_used': None,")
    lines.append("                'starting_row': 0,")
    lines.append("                'sheet_name': 'Report',")
    lines.append("                'starting_': 0,")
    lines.append("            }")
    lines.append("        }")
    lines.append("    }")
    lines.append("}")
    lines.append("")

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nWrote output file:\n{full_path}\n")


# ================================================================
# ============================= MAIN ==============================
# ================================================================

def main():
    df = load_excel()
    raw_map = build_raw_to_canonical(df)
    metadata = build_metadata(df)
    write_output(raw_map, metadata)


if __name__ == "__main__":
    main()