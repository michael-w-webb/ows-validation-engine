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