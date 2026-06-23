"""
Lightweight normalization helpers for strict identity-style matching.

This module provides highly conservative normalization utilities used in
contexts where approximate or permissive matching is undesirable. The
functions are primarily intended for deterministic identity resolution,
record linkage, and participant-key generation workflows.

Normalization behavior prioritizes:
    • removal of spreadsheet/export artifacts
    • rejection of placeholder or junk values
    • canonical lowercase representations
    • stable comparison-friendly outputs

The helpers intentionally return `None` for ambiguous, malformed, or
insufficiently informative values rather than attempting aggressive
recovery or fuzzy interpretation.

Functions:
    strict_alphabetic_normalize:
        Normalize alphabetic identity-style fields such as names.

    strict_date_normalize:
        Normalize date-like values into ISO date strings (`YYYY-MM-DD`).
"""

import re
import pandas as pd
import datetime as dt

def strict_alphabetic_normalize(value):
    """
    Normalize a value to strictly alphabetic lowercase text.
    Returns None if the value is invalid, empty, or non-alphabetic.
    """

    if pd.isna(value):
        return None

    # Convert to clean string
    s = str(value)
    s = s.replace('\xa0', ' ').replace('Â', '').strip().lower()

    # Reject obvious junk tokens
    if s in (
        "", "-", ".", "none", "null", "nan", "n/a",
        "#n/a", "#value!", "#ref!", "#name?"
    ):
        return None

    # Remove Excel numeric suffixes like ".0"
    s = re.sub(r"\.0$", "", s)

    # Keep only alphabetic + hyphen/apostrophe
    s = re.sub(r"[^a-z\'-]", "", s)

    # Reject short or empty results
    if len(s) < 1:  # adjust to <2 if you want more strictness
        return None

    return s

def strict_date_normalize(value):
    """
    Normalize a value to ISO date format (YYYY-MM-DD).
    Returns None if the value is invalid or cannot be parsed as a date.
    """

    if pd.isna(value):
        return None

    # Handle pandas Timestamp / datetime / date
    if isinstance(value, (pd.Timestamp, dt.datetime, dt.date)):
        return value.date().isoformat()

    s = str(value).strip()

    # Clean common Excel artifacts
    s = s.replace('\xa0', ' ').replace('Â', '')

    # Reject obvious junk tokens
    if s.lower() in (
        "", "-", ".", "none", "null", "nan", "n/a",
        "#n/a", "#value!", "#ref!", "#name?"
    ):
        return None

    # Remove trailing Excel numeric artifacts
    s = re.sub(r"\.0$", "", s)

    try:
        parsed = pd.to_datetime(s, errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date().isoformat()
    except Exception:
        return None