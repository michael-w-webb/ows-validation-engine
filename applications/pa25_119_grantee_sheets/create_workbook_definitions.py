import os
import re
import sys
from datetime import datetime
import pandas as pd

# =============================================================================
# Configuration
# =============================================================================

# Default path to the Excel workbook. You can override this by passing a path
# as the first command-line argument:
#   python generate_dicts.py "C:\path\to\data_elements_by_program.xlsm"
DATA_PATH = r"C:\Users\DalyRob\State of Connecticut\OWS HQ - Documents\PA25-119\DataPrep\data_elements_by_program.xlsm"

# Preferred sheet names: tries 'data_elements_table' first, then 'data_element_table'
PREFERRED_SHEETS = ("data_elements_table", "data_element_table")


# =============================================================================
# Helpers
# =============================================================================

def load_table(xlsm_path: str) -> pd.DataFrame:
    """Load the source sheet; prefer 'data_elements_table', then fallback to 'data_element_table'."""
    last_err = None
    for sheet in PREFERRED_SHEETS:
        try:
            return pd.read_excel(xlsm_path, sheet_name=sheet, engine="openpyxl")
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Could not open either sheet {PREFERRED_SHEETS} in '{xlsm_path}': {last_err}")

def clean(val) -> str:
    """Collapse internal whitespace, trim edges, convert NaN to empty string."""
    if pd.isna(val):
        return ""
    return " ".join(str(val).split())

def sanitize_var(token: str) -> str:
    """Convert text into a valid Python identifier (UPPER_SNAKE_CASE)."""
    t = token.upper()
    t = re.sub(r"[^A-Z0-9]", "_", t)
    t = re.sub(r"_+", "_", t)
    t = t.strip("_")
    if re.match(r"^[0-9]", t):
        t = "_" + t
    return t

def dedup_preserve_order(seq):
    """Remove duplicates while preserving original order."""
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

def escape_single_quoted_string(s: str) -> str:
    """Produce a safe single-quoted Python string literal for output."""
    s = s.replace("\\", "\\\\").replace("'", "\\'")
    s = s.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n").replace("\t", "\\t")
    return f"'{s}'"


# =============================================================================
# Core Build Logic
# =============================================================================

def build_dicts(df: pd.DataFrame):
    colmap = {str(c).strip().lower(): c for c in df.columns}

    # Required base columns
    needed = ["user_friendly_name", "type", "accepted_responses"]
    for n in needed:
        if n not in colmap:
            raise ValueError(f"Missing required column: {n}")

    # Data elements column (allow 'data_elements' or 'Data Element')
    de_col = colmap.get("data_elements", colmap.get("data element"))
    if not de_col:
        raise ValueError("Missing data elements column ('data_elements' or 'Data Element').")

    # Optional metadata columns
    section_col       = colmap.get("section")
    programs_col      = colmap.get("programs")
    program_count_col = colmap.get("program_count")
    grouped_col_col   = colmap.get("grouped_col_name")

    ufn_col = colmap["user_friendly_name"]
    type_col = colmap["type"]
    acc_col = colmap["accepted_responses"]

    simple_format_pa25_119_data_labels = {}
    accepted = {}

    for _, row in df.iterrows():
        key = clean(row[ufn_col])
        if not key:
            continue

        # --- simple_format_pa25_119_data_labels list ---
        raw_elems = clean(row[de_col])
        elems = [x.strip() for x in raw_elems.split(";") if x.strip()]
        elems = dedup_preserve_order(elems)

        if key not in simple_format_pa25_119_data_labels:
            simple_format_pa25_119_data_labels[key] = []
        for e in elems:
            if e not in simple_format_pa25_119_data_labels[key]:
                simple_format_pa25_119_data_labels[key].append(e)

        # --- metadata values (strings; empty if missing) ---
        tval = clean(row[type_col])
        aval = clean(row[acc_col])

        section_val  = clean(row[section_col]) if section_col else ""
        programs_val = clean(row[programs_col]) if programs_col else ""
        grouped_val  = clean(row[grouped_col_col]) if grouped_col_col else ""

        # program_count: try to parse as int; else empty string
        program_count_val = ""
        if program_count_col:
            raw_pc = row[program_count_col]
            if not pd.isna(raw_pc):
                try:
                    program_count_val = int(float(raw_pc)) if isinstance(raw_pc, (int, float)) else int(str(raw_pc))
                except Exception:
                    pc_str = clean(raw_pc)
                    program_count_val = pc_str

        # initialize accepted dict entry with all requested fields
        if key not in accepted:
            accepted[key] = {
                'type': tval,
                'Section': section_val,
                'programs': programs_val,
                'program_count': program_count_val,
                'grouped_col_name': grouped_val,
            }
        else:
            # type: prefer non-empty if not already set
            if tval and not accepted[key].get('type'):
                accepted[key]['type'] = tval
            # always (re)apply extra fields (sheet is aggregated, so one row per key anyway)
            accepted[key]['Section'] = section_val
            accepted[key]['programs'] = programs_val
            accepted[key]['program_count'] = program_count_val
            accepted[key]['grouped_col_name'] = grouped_val

        # --- accepted_responses: unquoted variable tokens list ---
        # --- accepted_responses ---
        # If type is 'categorical', accepted_responses should be a single UNQUOTED token (not a list),
        # e.g., EMPLOYMENT_STATUS_MAPPING. For other types, keep a list of tokens.
        if aval:
            raw_tokens = [x.strip() for x in aval.split(";") if x.strip()]
            raw_tokens = dedup_preserve_order(raw_tokens)

            tnorm = tval.strip().lower()
            if tnorm == "categorical":
                # For categorical: take the FIRST token, sanitize to a valid identifier, and store as string.
                # If multiple tokens provided, we choose the first one.
                tok = sanitize_var(raw_tokens[0]) if raw_tokens else ""
                if tok:
                    accepted[key]['accepted_responses'] = tok  # single token string (UNQUOTED in writer)
            else:
                # For non-categorical: produce a list of sanitized tokens.
                toks = [sanitize_var(x) for x in raw_tokens if x]
                toks = [t for t in toks if t]
                accepted[key]['accepted_responses'] = toks

    return simple_format_pa25_119_data_labels, accepted


# =============================================================================
# Output Writer
# =============================================================================

def write_output(path, labels, accepted):
    lines = []
    lines.append("# Auto-generated dictionaries")
    lines.append(f"# Generated: {datetime.now()}")
    lines.append("")

    # -----------------------
    # data_labels
    # -----------------------
    lines.append("simple_format_pa25_119_data_labels = {")
    for key in sorted(labels.keys()):
        lines.append(f"    {escape_single_quoted_string(key)}: [")
        for item in labels[key]:
            lines.append(f"        {escape_single_quoted_string(item)},")
        lines.append("    ],")
    lines.append("}\n")

    # -----------------------
    # simple_format_pa25_119_data_accepted_responses_w_types
    # -----------------------
    lines.append("simple_format_pa25_119_data_accepted_responses_w_types = {")
    for key in sorted(accepted.keys()):
        meta = accepted[key]
        lines.append(f"    {escape_single_quoted_string(key)}: {{")
        # type (string)
        lines.append(f"        'type': {escape_single_quoted_string(meta.get('type', ''))},")
        # Section (string)
        lines.append(f"        'Section': {escape_single_quoted_string(meta.get('Section', ''))},")
        # programs (string; semicolon-delimited as-is)
        lines.append(f"        'programs': {escape_single_quoted_string(meta.get('programs', ''))},")
        # grouped_col_name (string)
        lines.append(f"        'grouped_col_name': {escape_single_quoted_string(meta.get('grouped_col_name', ''))},")
        # program_count (emit int if numeric; else quoted string)
        pc = meta.get('program_count', '')
        if isinstance(pc, int):
            lines.append(f"        'program_count': {pc},")
        else:
            lines.append(f"        'program_count': {escape_single_quoted_string(str(pc))},")
        # accepted_responses list (UNQUOTED variable tokens)
        # accepted_responses: emit either a single UNQUOTED token (categorical) or a list of tokens
        if 'accepted_responses' in meta and meta['accepted_responses']:
            ar = meta['accepted_responses']
            if isinstance(ar, (list, tuple)):
                lines.append("        'accepted_responses': [")
                for tok in ar:
                    lines.append(f"            {tok},")  # UNQUOTED tokens
                lines.append("        ],")
            elif isinstance(ar, str):
                # Single token (categorical), emit UNQUOTED
                lines.append(f"        'accepted_responses': {ar}")
        
        # ✅ Close this entry's dict
        lines.append("    },")


    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# =============================================================================
# Main
# =============================================================================

def main():
    global DATA_PATH
    if len(sys.argv) > 1:
        DATA_PATH = sys.argv[1]

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(DATA_PATH)

    df = load_table(DATA_PATH)
    labels, accepted = build_dicts(df)

    out_path = os.path.join(os.path.dirname(DATA_PATH), "data_element_table_dicts.py")
    write_output(out_path, labels, accepted)

    print("Successfully wrote:", out_path)


if __name__ == "__main__":
    main()