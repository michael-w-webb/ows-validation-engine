import pandas as pd

class BaseVariable:
    """
    Parent (base) class for all variable types.

    Provides universal predicates (is_blank, equals, etc.)
    and a common evaluate() interface that subclasses extend.

    Each Variable operates only on its own column (Series) and the
    pre-processed `condition` dict provided by the CrossRuleEngine.
    The engine handles:
        - Resolving `var_ref` → injecting referenced Series into condition["value"]
        - Selecting the correct subclass for variable type
        - Passing the appropriate DataFrame context
    """
    def __init__(self, name, sheet, series, dfs_by_sheet=None, normalization_schema=None):
        self.name = name
        self.sheet = sheet
        self.series = series
        self.dfs_by_sheet = dfs_by_sheet
        self.normalization_schema = normalization_schema

    # ------------------------------------------------------------
    # ✅ Universal predicates
    # ------------------------------------------------------------
    
    def is_blank(self):
        """Return a Boolean mask where the value is missing or empty."""
        s = self.series
        return s.isna() | (s.astype(str).str.strip() == "")

    def is_not_blank(self):
        """Inverse of is_blank()."""
        return ~self.is_blank()

    def equals(self, value):
        """Return a Boolean mask where the value equals `value`."""
        return self.series == value

    def in_list(self, values):
        """Return True where the value is one of `values`."""
        return self.series.isin(values)

    def not_in_list(self, values):
        """Return True where the value is *not* one of `values`."""
        return ~self.series.isin(values)

    # ------------------------------------------------------------
    # ⚙️ Default evaluation logic
    # ------------------------------------------------------------
    def evaluate(self, condition: dict):
        """
        Generic evaluation dispatcher. Subclasses override or extend this.
        The condition dict should include:
            - op: the operation (e.g. 'equals', 'in', 'is_blank')
            - value(s): supporting arguments depending on op

        Notes:
        - The engine guarantees that `value` (if present) has already been
          resolved (either a scalar, list, or Series).
        - Subclasses can safely assume consistent structure.
        """
        op = condition.get("op")

        if op == "connected_presence":
            ref_series = condition.get("value")
            if ref_series is None or not isinstance(ref_series, pd.Series):
                raise ValueError(
                    f"connected_presence requires a resolved reference Series for '{self.name}'."
                )

            # Normalize blanks in both variables
            x_blank = self.series.isna() | (self.series.astype(str).str.strip() == "")
            y_blank = ref_series.isna() | (ref_series.astype(str).str.strip() == "")

            # True if both blank or both not blank
            return (x_blank & y_blank) | (~x_blank & ~y_blank)

        if op == "equals":
            return self.equals(condition["value"])
        elif op == "in":
            return self.in_list(condition["values"])
        elif op == "not_in":
            return self.not_in_list(condition["values"])
        elif op == "is_blank":
            return self.is_blank()
        elif op == "is_not_blank":
            return self.is_not_blank()
        else:
            raise ValueError(f"Unsupported operation '{op}' for variable '{self.name}'")


# ------------------------------------------------------------
# 🔢 Numeric Variable
# ------------------------------------------------------------
class NumericVariable(BaseVariable):
    def evaluate(self, condition):
        op = condition.get("op")
        if op == "between":
            lo, hi = condition["range"]
            return (self.series >= lo) & (self.series <= hi)
        elif op == "gt":
            return self.series > condition["value"]
        elif op == "lt":
            return self.series < condition["value"]
        else:
            return super().evaluate(condition)


# ------------------------------------------------------------
# 📅 Date Variable
# ------------------------------------------------------------
class DateVariable(BaseVariable):
    def evaluate(self, condition):
        """
        Handles date comparisons. Supports both literal and Series-based
        comparisons, depending on whether the engine passed a static date
        or another column’s Series in `condition["value"]`.
        """
        op = condition.get("op")
        s = pd.to_datetime(self.series, errors="coerce")
        value = condition.get("value")

        # Normalize: if value is not a Series, convert to Timestamp
        if not isinstance(value, pd.Series):
            if value is not None:
                value = pd.Timestamp(value)

        # perform operation
        if op == "before":
            return s < value
        elif op == "after":
            return s > value
        elif op == "between":
            lo, hi = [pd.Timestamp(d) for d in condition["range"]]
            return (s >= lo) & (s <= hi)
        else:
            return super().evaluate(condition)

# ------------------------------------------------------------
# 🧩 Categorical Variable
# ------------------------------------------------------------
class CategoricalVariable(BaseVariable):
    def evaluate(self, condition):
        op = condition.get("op")
        if op == "in":
            return self.in_list(condition["values"])
        elif op == "not_in":
            return self.not_in_list(condition["values"])
        else:
            return super().evaluate(condition)
