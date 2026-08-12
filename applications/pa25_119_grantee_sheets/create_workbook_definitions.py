import os
import sys
import pandas as pd
from datetime import datetime
from config import PROJECT_ROOT

# ================================================================
# ===================== USER CONFIGURABLE =========================
# ================================================================

docstring = """
Workbook Definitions, Label Maps, and Schema Metadata
=====================================================

This module contains the authoritative schema specification for all
PA25-119 workbooks supported by the validation pipeline. It encodes:

    • Canonical names used throughout the pipeline
    • All known spelling / formatting variants (“label maps”) found in
      provider-submitted Excel files
    • Field-level metadata describing expected types, requirements, and
      accepted categorical responses
    • Workbook-level structure for both “simple format” and
      “four-sheet format”
    • Logic template phrases used in natural-language rule descriptions

These definitions serve as the central contract between:

    1. WorkbookLoader – maps raw headers → canonical names
    2. NormalizationEngine / Type classes – validates and coerces values
    3. CrossRuleEngine – interprets variable types and resolves Series
    4. UI/reporting layers – generate intelligible rule messages

-----------------------------------------------------------------------
Label Maps (“labels”)
-----------------------------------------------------------------------

Each sheet definition includes:

    {
        "Canonical Name": ["Variant A", "Variant B", ...]
    }

The loader uses these maps to match raw headers, normalize text, and
tolerate typos/punctuation/casing differences and OWS/Salesforce labels.

-----------------------------------------------------------------------
Accepted Responses and Types (“accepted_responses_w_types”)
-----------------------------------------------------------------------

Each canonical field has:

    • type – one of the normalization types
    • required – whether nonblank is required
    • accepted_responses – categorical response set (if applicable)

-----------------------------------------------------------------------
Workbook Structure (“workbook_definitions”)
-----------------------------------------------------------------------

Organized by:

    workbook_type → workbook_format → sheet → definition

-----------------------------------------------------------------------
Logic Templates and Expectations
-----------------------------------------------------------------------

Used by CrossRuleEngine.describe_logic().

-----------------------------------------------------------------------
Extending This Module
-----------------------------------------------------------------------

To add/update fields:

    1. Add label variants
    2. Add metadata entry for the canonical field
    3. Add sheet/workbook formats as needed
    4. Add new types only after normalization support exists

This module is the **single source of truth** for schema consistency.
"""

raw_column_name = "Data Element"
canon_column_name = "canonical_name"
type_column = "type"
accepted_responses_column = "accepted_responses"
concept_class = "concept_class"

other_cols_of_interest = [
    "Program",
    "PIRL Category",
]

DATA_PATH = r"C:\Users\DalyRob\State of Connecticut\OWS HQ - Documents\PA25-119\DataPrep\data_elements_by_program.xlsm"
SHEET_NAME = "data_elements_by_program"

OUTPUT_PY_PATH = PROJECT_ROOT / "applications" / "pa25_119_grantee_sheets"
OUTPUT_FILENAME = "workbook_definitions.py"

DICT_NAME_LABELS = "simple_format_pa25_119_data_labels"
DICT_NAME_ACCEPTED = "simple_format_pa25_119_data_accepted_responses_w_types"

# ================================================================
# ====================== HELPER FUNCTIONS =========================
# ================================================================

def clean(val):
    if pd.isna(val):
        return ""
    return " ".join(str(val).split())

def unique_sorted(values):
    cleaned = [clean(v) for v in values if clean(v)]
    return sorted(set(cleaned))

def load_excel():
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
            raise ValueError(f"Column '{col}' listed in other_cols_of_interest is missing.")

    if concept_class not in df.columns:
        raise ValueError(f"Column '{concept_class}' is missing from the Excel file.")

    return df

# ================================================================
# ======================== BUILD DICT #1 ==========================
# ================================================================

def build_raw_to_canonical(df):
    mapping = {}

    for _, row in df.iterrows():
        raw_val = clean(row[raw_column_name])
        canon_val = clean(row[canon_column_name])

        if not canon_val:
            continue

        mapping.setdefault(canon_val, [])

        if raw_val:
            mapping[canon_val].append(raw_val)

    for k in mapping:
        mapping[k] = sorted(set(mapping[k]))

    return mapping

# ================================================================
# ======================== BUILD DICT #2 ==========================
# ================================================================

def build_metadata(df):
    metadata = {}

    for _, row in df.iterrows():
        canon_val = clean(row[canon_column_name])
        if not canon_val:
            continue

        if canon_val not in metadata:
            metadata[canon_val] = {
                "type": "",
                "accepted_responses": None,
                "concept_class": "",
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

        # concept_class (correct handling)
        concept_val = clean(row[concept_class])
        if concept_val:
            metadata[canon_val]["concept_class"] = concept_val

        # other metadata
        for col in other_cols_of_interest:
            val = clean(row[col])
            if val:
                metadata[canon_val][col].append(val)

    # finalize formatting
    for canon, meta in metadata.items():

        vals = meta["accepted_responses"]
        if not vals:
            meta["accepted_responses"] = None
        else:
            uniq = unique_sorted(vals)
            if len(uniq) == 1:
                meta["accepted_responses"] = uniq[0]
            else:
                meta["accepted_responses"] = uniq

        for col in other_cols_of_interest:
            meta[col] = ";".join(unique_sorted(meta[col])) if meta[col] else ""

    return metadata

# ================================================================
# ======================== WRITER FUNCTION ========================
# ================================================================

def write_output(raw_map, metadata):
    OUTPUT_PY_PATH.mkdir(parents=True, exist_ok=True)
    full_path = OUTPUT_PY_PATH / OUTPUT_FILENAME

    used_mappings = set()

    for canon, meta in metadata.items():
        ar = meta.get("accepted_responses")
        if not ar:
            continue
        if isinstance(ar, str):
            used_mappings.add(ar)
        elif isinstance(ar, list):
            used_mappings.update(ar)

    used_mappings = sorted(used_mappings)

    lines = []
    lines.append("# Auto-generated dictionary file")
    lines.append(f"# Generated: {datetime.now()}")
    lines.append("")
    lines.append('"""')
    lines.append(docstring)
    lines.append('"""')

    if used_mappings:
        csv_list = ", ".join(used_mappings)
        lines.append(
            f"from applications.pa25_119_grantee_sheets.workbook_definition_dictionaries import {csv_list}"
        )
    lines.append("")
    lines.append("")

    lines.append(f"{DICT_NAME_LABELS} = {{")
    for canon in sorted(raw_map.keys()):
        lines.append(f"    {repr(canon)}: [")
        for raw in raw_map[canon]:
            lines.append(f"        {repr(raw)},")
        lines.append("    ],")
    lines.append("}")
    lines.append("")
    lines.append("")

    lines.append(f"{DICT_NAME_ACCEPTED} = {{")
    for canon in sorted(metadata.keys()):
        meta = metadata[canon]
        lines.append(f"    {repr(canon)}: {{")
        lines.append(f"        'type': {repr(meta['type'])},")
        lines.append(f"        'concept_class': {repr(meta['concept_class'])},")

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

        for col in other_cols_of_interest:
            lines.append(f"        '{col}': {repr(meta[col])},")

        lines.append("    },")
    lines.append("}")
    lines.append("")
    lines.append("")

    lines.append("workbook_definitions = {")
    lines.append("    'pa25_119 data': {")
    lines.append("        'simple format': {")
    lines.append("            'Report': {")
    lines.append(f"                'labels': {DICT_NAME_LABELS},")
    lines.append(f"                'accepted_responses': {DICT_NAME_ACCEPTED},")
    lines.append("                's_used': None,")
    lines.append("                'starting_row': 0,")
    lines.append("                'sheet_name': 'Report',")
    lines.append("                'starting_col': 0,")
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