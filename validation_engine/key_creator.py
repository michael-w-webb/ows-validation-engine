"""
KeyCreator Module
=================

Provides a flexible, schema-agnostic key generation utility used to create 
deterministic identifiers for participant records, workbook rows, 
and entity matching across datasets.

The :class:`KeyCreator` class supports:

- **Composite key creation** from arbitrary fields
- **Optional normalization** of individual components via user-supplied functions
- **Required field enforcement**, with automatic invalidation when requirements fail
- **Hashed or unhashed keys**, depending on debugging or privacy needs
- **Attach-to-DataFrame API** for generating key columns at scale

Typical Use Cases
-----------------
This module is used throughout the validation engine to generate
stable row-level identifiers such as:

- ``sheet-level linking keys`` (e.g., First Name + Last Name)
- ``participant identity keys`` for database lookup
- ``hashed canonical IDs`` used for cross-dataset entity resolution

The class accepts any schema and is not tied to CareerConneCT, GJC,
or specific column conventions.

Example
-------

.. code-block:: python

    from key_creator import KeyCreator
    from utils import strict_alphabetic_normalize

    kc = KeyCreator(
        key_fields=["First Name", "Last Name", "DOB"],
        normalizers={"First Name": strict_alphabetic_normalize},
        required_fields=["First Name", "Last Name"],
        return_unhashed=False
    )

    df["id_key"] = df.apply(kc.create_key_from_row, axis=1)


Contents
--------
- KeyCreator  -- main class for composite/hashing logic

Dependencies
------------
- pandas
- hashlib

"""

import pandas as pd
import hashlib
import warnings

from validation_engine.column_names import (
    find_columns
)

class KeyCreator:
    """
    Generic, schema-agnostic key generator.

    - key_fields: list[str]
    - normalizers: dict[field -> fn(value)]
    - required_fields: list[str]
    - return_unhashed: if True, return the composite string instead of a hashed ID
    """
    

    def __init__(
        self,
        key_fields,
        normalizers=None,
        required_fields=None,
        hash_length=16,
        sep="|",
        hash_fn="sha256",
        return_unhashed=False,
    ):
        self.key_fields = key_fields
        self.normalizers = normalizers or {}
        self.required_fields = required_fields or key_fields
        self.hash_length = hash_length
        self.sep = sep
        self.hash_fn = hash_fn
        self.return_unhashed = return_unhashed

    # --------------------------
    # Hash utility
    # --------------------------
    def _hash(self, text):
        if self.hash_fn == "sha1":
            h = hashlib.sha1()
        elif self.hash_fn == "blake2":
            h = hashlib.blake2b()
        else:
            h = hashlib.sha256()

        h.update(text.encode())
        return h.hexdigest()[:self.hash_length]

    # --------------------------
    # Normalize one value
    # --------------------------
    def _apply_normalizer(self, field, value):
        if field in self.normalizers:
            return self.normalizers[field](value)
        return value

    # --------------------------
    # Create a key for a single row
    # --------------------------
    def create_key_from_row(self, row):
        parts = []

        for field in self.key_fields:
            raw = self._resolve_field(row, field)
            normed = self._apply_normalizer(field, raw)

            if field in self.required_fields and (pd.isna(normed) or normed in (None, "")):
                return None

            parts.append("" if normed is None else str(normed).strip())

        composite = self.sep.join(parts)

        if self.return_unhashed:
            return composite

        return self._hash(composite)

    # --------------------------
    # Add key column to DataFrame
    # --------------------------
    def add_key_column(self, df, key_col="id_key"):
        df[key_col] = df.apply(self.create_key_from_row, axis=1)
        df[f"{key_col}_invalid"] = df[key_col].isna()
        return df
    
    
    def _resolve_field(self, row, field):
        """
        Resolve a logical field from a row.

        Preference order:

        1. Normalized values
        2. Raw values

        Within each group:
        1. First non-null value
        2. Otherwise first matching column
        """

        base = field.replace(
            "_normalized",
            ""
        )

        norm_candidates = find_columns(
            row.index,
            base=base,
            normalized=True
        )

        if len(norm_candidates) > 1:

            values = {
                row.get(col)
                for col in norm_candidates
                if pd.notna(row.get(col))
                and row.get(col) != ""
            }

            if len(values) > 1:

                warnings.warn(
                    f"Multiple normalized values found for '{base}' "
                    f"with conflicting values: {values}"
                )

        raw_candidates = find_columns(
            row.index,
            base=base,
            normalized=False
        )

        candidates = (
            norm_candidates
            if norm_candidates
            else raw_candidates
        )

        if not candidates:
            return None

        for col in candidates:

            value = row.get(col)

            if pd.notna(value) and value not in ("", None):
                return value

        return row.get(candidates[0])