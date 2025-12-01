import pandas as pd
import hashlib

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
            raw = row.get(field, None)
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
