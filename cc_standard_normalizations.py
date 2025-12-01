import re
import pandas as pd

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
