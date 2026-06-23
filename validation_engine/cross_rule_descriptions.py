# cross_rule_descriptions.py
import pandas as pd
from datetime import datetime

def describe_compound(op, subdescs, extra=None):

    """
    Construct a natural-language description for a compound logical clause.

    This function combines already-rendered subclause descriptions into a
    single human-readable logical expression.

    Unlike ``describe_logic()``, this function does not recurse through
    clause trees directly. Instead, it operates on pre-rendered textual
    fragments representing descendant clauses.

    Supported operators include:

        - AND
        - OR
        - NOT
        - IF_THEN
        - IF_THEN_ELSE
        - EQUIVALENT / IFF
        - XOR
        - ONE_OF
        - AT_LEAST

    Overview
    --------
    Compound logical operators combine multiple subclauses into larger
    logical expressions.

    Example:

    >>> describe_compound(
    ...     "AND",
    ...     [
    ...         "'Completed Date' must be filled",
    ...         "'Employment Status' must be filled"
    ...     ]
    ... )

    Produces:

        "('Completed Date' must be filled) and
        ('Employment Status' must be filled)"

    Conditional Tone Rewriting
    --------------------------
    Conditional operators such as ``IF_THEN`` and ``IF_THEN_ELSE`` soften
    the antecedent phrasing by rewriting:

        "must"

    to:

        "is"

    This produces more natural conditional language.

    Example:

        "If 'Completed Date' is filled, then
        'Employment Status' must be filled"

    rather than:

        "If 'Completed Date' must be filled..."

    Parameters
    ----------
    op : str
        Compound logical operator name.

    subdescs : list[str]
        Pre-rendered natural-language descriptions of subclauses.

    extra : int | None, optional
        Additional operator metadata used by certain operators such as
        ``AT_LEAST``.

    Returns
    -------
    str
        Human-readable logical description.

    Notes
    -----
    Unknown operators fall back to a defensive generic rendering rather
    than raising exceptions. This behavior helps preserve debuggability
    during rule-authoring or grammar-extension workflows.
    """

    if op == "AND":
        return " and ".join([f"({d})" for d in subdescs])
    if op == "OR":
        return " or ".join([f"({d})" for d in subdescs])
    if op == "IF_THEN":
        antecedent = subdescs[0].replace("must", "is")  # descriptive rewrite
        return f"If {antecedent}, then {subdescs[1]}"
    if op == "IF_THEN_ELSE":
        antecedent = subdescs[0].replace("must", "is")
        return f"If {antecedent}, then {subdescs[1]}, else {subdescs[2]}"
    if op =="NOT":
        return f"{subdescs}"
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

def describe_atomic(var_name, var_sheet, op, ref, is_condition=False, is_negated = False):
    """
    Construct a natural-language description for a single atomic clause.

    This is used for leaf nodes in a clause tree. It interprets operators
    such as `is_blank`, `before`, or `connected_presence`, and chooses
    tone-appropriate phrasing depending on whether the clause appears
    in a conditional antecedent.

    Args:
        var_name (str):
            Column name being referenced.
        var_sheet (str):
            Sheet where the column resides.
        op (str):
            Atomic operator applied to the variable
            (e.g., "is_blank", "before", "equals").
        ref (Any):
            Reference value or (sheet, column) tuple to compare against.
            Passed through `format_reference()`.
        is_condition (bool):
            If True, phrasing uses descriptive rather than prescriptive tone
            (e.g., "is filled" instead of "must be filled").

    Returns:
        str:
            A human-readable description of the atomic requirement.
    """
    negation = ""
    if is_negated:
        negation = "*not*"
    ref_text = format_reference(ref)

    # Tone-aware templates
    if is_condition:
        templates = {
            "connected_presence": (
               f"'{var_name}' (sheet '{var_sheet}') is {negation} blank or non-blank in the same way as {ref_text}"
            ),
            "before": (
                f"'{var_name}' (sheet '{var_sheet}') is {negation} before {ref_text}"
            ),
            "after": (
                f"'{var_name}' (sheet '{var_sheet}') is {negation} after {ref_text}"
            ),
            "equals": (
                f"'{var_name}' (sheet '{var_sheet}') is {negation} equal to {ref_text}"
            ),
            "is_not_blank": (
                f"'{var_name}' (sheet '{var_sheet}') is {negation} filled"
            ),
            "is_blank": (
                f"'{var_name}' (sheet '{var_sheet}') is {negation} blank"
            ),
            "in": (
                f"'{var_name}' (sheet '{var_sheet}') is {negation} one of {ref_text}"
            )
        }
    else:
        templates = {
            "connected_presence": (
                f"'{var_name}' (sheet '{var_sheet}') must {negation} match the blank/non-blank status of {ref_text}"
            ),
            "before": (
                f"'{var_name}' (sheet '{var_sheet}') must {negation} be before {ref_text}"
            ),
            "after": (
                f"'{var_name}' (sheet '{var_sheet}') must {negation} be after {ref_text}"
            ),
            "equals": (
                f"'{var_name}' (sheet '{var_sheet}') must {negation} equal {ref_text}"
            ),
            "is_not_blank": (
                f"'{var_name}' (sheet '{var_sheet}') must {negation} be filled"
            ),
            "is_blank": (
                f"'{var_name}' (sheet '{var_sheet}') must {negation} be blank"
            ),
            "in": (
                f"'{var_name}' (sheet '{var_sheet}') must {negation} be one of {ref_text}"
            )
        }

    return templates.get(
        op,
        f"'{var_name}' (sheet '{var_sheet}') must {negation} satisfy '{op}' relative to {ref_text}"
    )


def format_reference(ref):
    """
    Format a comparison reference into a human-readable English phrase.

    This function standardizes the various ways references can appear in
    cross-sheet rules, including literal values, dates, or references to
    other variables.

    Supports:
        • (sheet, column) tuples → "'Column' (sheet 'Sheet')"
        • pandas / datetime date types → "the date YYYY-MM-DD"
        • numbers → "the value X"
        • "__BLANK__" and "__NOT_BLANK__" indicators
        • Strings that appear date-like → "the date YYYY-MM-DD"
        • All other types → stringified

    Args:
        ref (Any):
            The comparison target or special marker.

    Returns:
        str:
            A formatted reference string suitable for inclusion in
            natural-language rule descriptions.
    """
    if ref is None:
        return ""
    elif isinstance(ref, list):
        return ", ".join([format_reference(r) for r in ref])
    elif isinstance(ref, tuple) and len(ref) == 2:
        sheet, var = ref
        return f"'{var}' (sheet '{sheet}')"
    elif isinstance(ref, (pd.Timestamp, datetime)):
        return f"the date {ref.strftime('%Y-%m-%d')}"
    elif isinstance(ref, (int, float)):
        return f"{ref}"
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
            return f"'{r}'"
    else:
        return str(ref)
