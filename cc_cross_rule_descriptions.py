# cross_rule_descriptions.py
import pandas as pd
from datetime import datetime

def describe_compound(op, subdescs, extra=None):
    if op == "AND":
        return " and ".join([f"({d})" for d in subdescs])
    if op == "OR":
        return " or ".join([f"({d})" for d in subdescs])
    if op == "NOT":
        return f"not ({subdescs[0]})"
    if op == "IF_THEN":
        antecedent = subdescs[0].replace("must", "is")  # descriptive rewrite
        return f"If {antecedent}, then {subdescs[1]}"
    if op == "IF_THEN_ELSE":
        antecedent = subdescs[0].replace("must", "is")
        return f"If {antecedent}, then {subdescs[1]}, else {subdescs[2]}"
    if op in ("EQUIVALENT", "IFF"):
        return f"{subdescs[0]} if and only if {subdescs[1]}"
    if op == "XOR":
        return f"Exactly one of ({subdescs[0]}) or ({subdescs[1]}) must be true"
    if op == "ONE_OF":
        return "Exactly one of: " + "; ".join(subdescs)
    if op == "AT_LEAST":
        threshold = extra or "N"
        return f"At least {threshold} of the following must be true: " + "; ".join(subdescs)
    return f"Unknown operator '{op}' on clauses: " + "; ".join(subdescs)

def describe_atomic(var_name, var_sheet, op, ref, is_condition=False):
    """
    Returns a human-readable phrase for an atomic clause.
    If `is_condition=True`, uses descriptive ('is') phrasing instead of prescriptive ('must') phrasing.
    """

    ref_text = format_reference(ref)

    # Tone-aware templates
    if is_condition:
        templates = {
            "connected_presence": (
                f"'{var_name}' (sheet '{var_sheet}') has the same blank/non-blank status as {ref_text}"
            ),
            "before": (
                f"'{var_name}' (sheet '{var_sheet}') is before {ref_text}"
            ),
            "after": (
                f"'{var_name}' (sheet '{var_sheet}') is after {ref_text}"
            ),
            "equals": (
                f"'{var_name}' (sheet '{var_sheet}') equals {ref_text}"
            ),
            "is_not_blank": (
                f"'{var_name}' (sheet '{var_sheet}') is filled"
            ),
            "is_blank": (
                f"'{var_name}' (sheet '{var_sheet}') is blank"
            ),
        }
    else:
        templates = {
            "connected_presence": (
                f"'{var_name}' (sheet '{var_sheet}') must match the blank/non-blank status of {ref_text}"
            ),
            "before": (
                f"'{var_name}' (sheet '{var_sheet}') must be before {ref_text}"
            ),
            "after": (
                f"'{var_name}' (sheet '{var_sheet}') must be after {ref_text}"
            ),
            "equals": (
                f"'{var_name}' (sheet '{var_sheet}') must equal {ref_text}"
            ),
            "is_not_blank": (
                f"'{var_name}' (sheet '{var_sheet}') must be filled"
            ),
            "is_blank": (
                f"'{var_name}' (sheet '{var_sheet}') must be blank"
            ),
        }

    return templates.get(
        op,
        f"'{var_name}' (sheet '{var_sheet}') must satisfy '{op}' relative to {ref_text}"
    )


def format_reference(ref):
    """
    Convert a reference (value or variable) into a human-readable string.

    Handles:
        - (sheet, variable) tuples → column references
        - pd.Timestamp / datetime.date → dates
        - numbers → literal values
        - special markers: "__NOT_BLANK__", "__BLANK__"
        - strings → quoted literal values
        - None → empty string
    """
    if ref is None:
        return ""
    elif isinstance(ref, tuple) and len(ref) == 2:
        sheet, var = ref
        return f"'{var}' (sheet '{sheet}')"
    elif isinstance(ref, (pd.Timestamp, datetime)):
        return f"the date {ref.strftime('%Y-%m-%d')}"
    elif isinstance(ref, (int, float)):
        return f"the value {ref}"
    elif isinstance(ref, str):
        r = ref.strip()
        if r == "__NOT_BLANK__":
            return "a non-blank value"
        elif r == "__BLANK__":
            return "a blank value"
        elif r.lower().startswith("20") and len(r) >= 8:
            # likely a date-like literal string
            return f"the date {r}"
        else:
            return f"the value '{r}'"
    else:
        return str(ref)
