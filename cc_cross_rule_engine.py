import operator
from functools import reduce
import pandas as pd

from cc_cross_rule_descriptions import * 
from cc_cross_rule_classes import BaseVariable, NumericVariable, DateVariable, CategoricalVariable
from cc_column_label_list import workbook_definitions


class CrossRuleEngine:


    """
    ============================================================
    🧩 CrossRuleEngine — Unified Cross-Sheet Logic Evaluator
    ============================================================

    The CrossRuleEngine evaluates logical dependencies across multiple
    worksheets within a normalized workbook. It supports both
    cross-sheet and multi-column validation using a single recursive
    logical grammar (the “clause tree” model).

    ─────────────────────────────────────────────────────────────
    🔹 Overview
    ─────────────────────────────────────────────────────────────
    The engine replaces legacy rule categories (e.g. “conditionally
    required,” “connected presence”) with a single clause structure that
    can express any logical or conditional relationship between columns.

    Each rule is defined as a nested dictionary (“clause tree”) using
    logical operators (AND, OR, NOT, etc.) and conditional modifiers
    (IF_THEN, IF_THEN_ELSE, etc.). The recursion allows arbitrarily deep
    combinations of conditions.

    ─────────────────────────────────────────────────────────────
    🔹 Clause Tree Structure
    ─────────────────────────────────────────────────────────────
    • Simple relational clause:
        {"var": ("Training", "Completed Date"), "op": "is_not_blank"}

    • Compound logical clause:
        {"AND": [
            {"var": ("Training", "Completed Date"), "op": "is_not_blank"},
            {"var": ("Outcomes", "Employment Status"), "op": "is_not_blank"}
        ]}

    • Conditional clause:
        {"IF_THEN": [
            {"var": ("Training", "Completed Date"), "op": "is_not_blank"},
            {"var": ("Outcomes", "Employment Status"), "op": "is_not_blank"}
        ]}

    Clause trees can nest indefinitely:
        {
            "AND": [
                {"IF_THEN": [
                    {"var": ("Training", "Completed Date"), "op": "is_not_blank"},
                    {"var": ("Outcomes", "Employment Status"), "op": "is_not_blank"}
                ]},
                {"NOT": [
                    {"var": ("Outcomes", "Withdrawal Reason"), "op": "is_not_blank"}
                ]}
            ]
        }

    ─────────────────────────────────────────────────────────────
    🔹 Variable References
    ─────────────────────────────────────────────────────────────
    Each variable reference is a tuple:
        (sheet_name, column_name)

    Examples:
        ("Training", "Completed Date")
        ("Outcomes", "Employment Status")

    When used with “var_ref”, the engine performs column-to-column
    comparisons across sheets rather than static value checks.

    ─────────────────────────────────────────────────────────────
    🔹 Evaluation Process
    ─────────────────────────────────────────────────────────────
    1️⃣  Leaf nodes containing "var" are evaluated using the correct
        Variable subclass (DateVariable, CategoricalVariable, etc.)
        and return a pandas.Series[bool].

    2️⃣  Compound nodes (AND, IF_THEN, etc.) recursively evaluate their
        subclauses, combine Boolean results via the `combine()` method,
        and return a Boolean mask of valid rows.

    3️⃣  Rows that evaluate False are treated as violations.

    ─────────────────────────────────────────────────────────────
    🔹 Supported Operators
    ─────────────────────────────────────────────────────────────
    Logical / Conditional modifiers supported in `combine()`:

        Operator         Arity    Meaning
        ----------------------------------------------------------
        AND              n        All clauses must be True
        OR               n        At least one clause must be True
        NOT              1        Negates the clause
        IF_THEN          2        If first clause True → second must be True
        IF_THEN_ELSE     3        If first True → second; else → third
        EQUIVALENT/IFF   2        Clauses must share same Boolean value
        XOR              2        Exactly one clause True
        ONE_OF           n        Exactly one of n clauses True
        AT_LEAST         n+1      At least k of n clauses True (last arg = k)

    All masks are re-indexed to align DataFrame lengths safely.

    ─────────────────────────────────────────────────────────────
    🔹 Output Format
    ─────────────────────────────────────────────────────────────
    Each rule produces a DataFrame of violations matching the
    normalization-error schema:

        file | sheet | row_number | column | rule | raw_value | normalized

    • `file`: workbook name
    • `sheet`: sheet of primary variable
    • `row_number`: row index (1-based)
    • `column`: variable name
    • `rule`: human-readable description
    • `raw_value`: left blank for cross-rules
    • `normalized`: normalized value from the source sheet

    This ensures cross-rule violations can be concatenated directly
    with standard normalization errors.

    ─────────────────────────────────────────────────────────────
    🔹 Human-Readable Descriptions
    ─────────────────────────────────────────────────────────────
    The `describe_logic()` method walks any clause tree recursively
    and builds a natural-language explanation.

    Example:
        {"IF_THEN": [
            {"var": ("Training", "Completed Date"), "op": "is_not_blank"},
            {"var": ("Outcomes", "Employment Status"), "op": "is_not_blank"}
        ]}

    ➜ “If ‘Completed Date’ (Training) is filled, then
       ‘Employment Status’ (Outcomes) must also be filled.”

    Compound example:
        {"AND": [
            {"IF_THEN": [...]},
            {"NOT": [{"var": ("Outcomes", "Withdrawal Reason"), "op": "is_not_blank"}]}
        ]}

    ➜ “(If ‘Completed Date’ (Training) is filled, then
       ‘Employment Status’ (Outcomes) must also be filled) and
       (not (‘Withdrawal Reason’ (Outcomes) is filled)).”

    ─────────────────────────────────────────────────────────────
    🔹 Rule Expansion
    ─────────────────────────────────────────────────────────────
    For authoring convenience, rules can include multiple references
    using the `var_refs` key:
        {
            "rule_name": "Program Entry → Status dependencies",
            "logic": {
                "var": ("Training", "Date of Program Entry"),
                "op": "connected_presence",
                "var_refs": [
                    ("Personal Information", "Low Income Status"),
                    ("Personal Information", "Single Parent Status")
                ]
            }
        }

    The engine’s `expand_rules()` method automatically generates one
    atomic rule for each reference pair.

    ─────────────────────────────────────────────────────────────
    🔹 Summary
    ─────────────────────────────────────────────────────────────
    • Unified recursive framework replaces legacy rule types.
    • Clause grammar supports arbitrary nesting and combinations.
    • Descriptions generated automatically from rule logic.
    • Output schema aligns with normalization validation results.

    This design makes the CrossRuleEngine extensible, debuggable, and
    suitable for future UI-driven rule builders or schema generators.
    """

    def __init__(self, workbook_type, workbook_format, dfs_by_sheet, normalization_schema, file):
        self.workbook_type = workbook_type          # e.g. "training data (workbook type)"
        self.workbook_format = workbook_format      # e.g. "four sheet format" or "simple format (workbook format)"
        self.dfs = dfs_by_sheet                     # normalized DataFrames by sheet
        self.schema = normalization_schema          # e.g. cc_column_label_list
        self.file = file                            # file name reference (for error reporting)

    # ============================================================
    # 🔹 Variable retrieval
    # ============================================================
    def get_variable(self, var_name, sheet_key):
        """Instantiate the appropriate Variable subclass from the nested schema."""
        
        if self.workbook_format == "simple format":

            sheet_key = "Report"
        
        try:
            # Navigate the nested schema hierarchy
            sheet_def = (
                self.schema[self.workbook_type][self.workbook_format][sheet_key]
            )
        except KeyError:
            raise KeyError(
                f"Sheet '{sheet_key}' not found under "
                f"'{self.workbook_type}' → '{self.workbook_format}'."
            )

        col_meta = sheet_def["accepted_responses"].get(var_name)
        if not col_meta:
            raise KeyError(
                f"Variable '{var_name}' not found in accepted_responses for sheet '{sheet_key}'."
            )

        dtype = col_meta.get("type", "string").lower()
        accepted = col_meta.get("accepted_responses", [])

        cls_map = {
            "numeric": NumericVariable,
            "hourlywage": NumericVariable,
            "datetime": DateVariable,
            "categorical": CategoricalVariable,
            "filespecificcategorical": CategoricalVariable,
            "identifier": BaseVariable,
        }

        cls_ref = cls_map.get(dtype, BaseVariable)

        df = self.dfs.get(sheet_key)
        if df is None:
            raise KeyError(f"DataFrame for sheet '{sheet_key}' not found in dfs_by_sheet.")
        if var_name not in df.columns:
            raise KeyError(f"'{var_name}' not found in DataFrame for sheet '{sheet_key}'.")

        # Instantiate variable object
        series = df[var_name]
        var_obj = cls_ref(var_name, sheet_key, series, self.dfs, self.schema)
        var_obj.engine = self
        var_obj.accepted_responses = accepted
        var_obj.meta = col_meta
        return var_obj

    # ============================================================
    # 🔹 Logic combination and evaluation
    # ============================================================
    def combine(self, masks, logic_op):
        op = logic_op.upper()
        if op == "AND": return reduce(operator.and_, masks) ## arity n
        if op == "OR": return reduce(operator.or_, masks) ## arity n
        if op == "NOT": return ~masks[0] ## arity 1
        if op == "IF_THEN": a, b = masks; return ~a | b ## arity 2
        if op == "IF_THEN_ELSE": a, b, c = masks; return (~a | b) & (a | c) ## arity 3 
        if op == "EQUIVALENT" or op == "IFF": a, b = masks; return (a & b) | (~a & ~b) ## arity 2 
        if op == "XOR": a, b = masks; return a ^ b ## arity 2
        if op == "ONE_OF": return reduce(operator.xor, masks)
        if op == "AT_LEAST": n, min_required = masks[:-1], int(masks[-1]); return sum(n) >= min_required
        raise ValueError(f"Unknown logic operator: {op}")


    def evaluate_logic(self, logic_dict):
        """
        Recursively evaluate a nested logic dictionary like:
        {"AND": [{"var": "X", ...}, {"OR": [...]}, ...]}
        or a single condition like:
        {"var": "Training End Date", "op": "before", "compare_to": "Quarter End Date"}
        """

        # --- Base case: single condition ---
        if "var" in logic_dict:
            var_sheet, var_name = logic_dict["var"]
            var = self.get_variable(var_name, var_sheet)

            condition = logic_dict.copy()
            if "compare_to" in condition:
                ref_sheet, ref_name = condition["compare_to"]
                ref_var = self.get_variable(ref_name, ref_sheet)
                condition["value"] = ref_var.series
                condition["comparison_type"] = "column"
            else:
                condition["comparison_type"] = "value"

            return var.evaluate(condition)

        # --- Compound logic ---
        for logic_op, subclauses in logic_dict.items():
            masks = [self.evaluate_logic(sub) for sub in subclauses]
            return self.combine(masks, logic_op.upper())

    def describe_logic(self, logic_dict, is_condition=False):
        """
        Recursively describe a logic tree in natural language.
        `is_condition=True` softens phrasing for antecedents
        (e.g. "is filled" instead of "must be filled").
        """

        # --- Base case: atomic clause ---
        if "var" in logic_dict:
            (var_sheet, var_name) = logic_dict["var"]
            op = logic_dict.get("op", "").lower()
            ref = logic_dict.get("compare_to")
            value = logic_dict.get("value")
            ref_text = ""
            if value:
                ref_text = value
            if ref:
                ref_sheet, ref_name = ref
                ref_text = f"'{ref_name}' (sheet '{ref_sheet}')"
            return describe_atomic(var_name, var_sheet, op, ref_text, is_condition=is_condition)

        # --- Compound clause ---
        for op, subclauses in logic_dict.items():
            op_upper = op.upper()

            # Handle conditional operators with tone-aware recursion
            if op_upper == "IF_THEN":
                antecedent_desc = self.describe_logic(subclauses[0], is_condition=True)
                consequent_desc = self.describe_logic(subclauses[1], is_condition=False)
                subdescs = [antecedent_desc, consequent_desc]

            elif op_upper == "IF_THEN_ELSE":
                antecedent_desc = self.describe_logic(subclauses[0], is_condition=True)
                then_desc = self.describe_logic(subclauses[1], is_condition=False)
                else_desc = self.describe_logic(subclauses[2], is_condition=False)
                subdescs = [antecedent_desc, then_desc, else_desc]

            else:
                # Regular recursion for other operators (AND, OR, etc.)
                subdescs = [self.describe_logic(sub, is_condition=is_condition) for sub in subclauses]

            extra = None
            if op_upper == "AT_LEAST":
                *subdescs, extra = subdescs  # last one is threshold

            return describe_compound(op_upper, subdescs, extra)


    def _find_primary_var(self, logic):
        """Recursively find the first (sheet, column) tuple in a logic tree."""
        if not isinstance(logic, dict):
            return None

        if "var" in logic and isinstance(logic["var"], tuple):
            return logic["var"]

        for v in logic.values():
            if isinstance(v, list):
                for sub in v:
                    found = self._find_primary_var(sub)
                    if found:
                        return found
            elif isinstance(v, dict):
                found = self._find_primary_var(v)
                if found:
                    return found

        return None


    # ============================================================
    # 🔹 Rule-level evaluation (conditional + relational)
    # ============================================================

    def evaluate_rule(self, rule):
        """
        Evaluate a complete rule definition using the unified clause/modifier syntax.
        
        Each rule is a single logical tree (supports AND, OR, NOT, IF_THEN, IF_THEN_ELSE, etc.).
        A violation occurs wherever the logical expression evaluates to False.
        """

        rule_name = rule.get("rule_name", "Unnamed Rule")
        logic = rule.get("logic", rule)  # entire clause tree

        # 1️⃣ Evaluate recursively — returns Boolean mask
        mask_valid = self.evaluate_logic(logic)
        violations = ~mask_valid

        # 2️⃣ Derive the primary variable reference for reporting
        main_ref = self._find_primary_var(logic)
        if isinstance(main_ref, tuple):
            main_sheet, main_col = main_ref
        else:
            main_sheet, main_col = ("<unknown>", "<unknown>")

        df = self.dfs.get(main_sheet, next(iter(self.dfs.values())))

        rule_text = self.describe_logic(logic)

        # 4️⃣ Produce unified, normalization-compatible output
        out = pd.DataFrame({
            "file": self.file or "",
            "sheet": main_sheet,
            "row_number": (
                df.loc[violations, "row_number"].values
                if "row_number" in df else None
            ),
            "column": main_col,
            "rule": rule_text,
            "raw_value": "",
            "normalized": (
                df.loc[violations, main_col].astype(str).fillna("").values
                if main_col in df.columns else ""
            ),
            "id_key": (
                df.loc[violations, "id_key"].values
                if "id_key" in df.columns else None
            )

        })

        #out["rule_name"] = rule_name  # keep internal rule label (optional)
        return out

    # ============================================================
    # 🔹 Rule expansion + batch execution
    # ============================================================

    def expand_rules(self, rules):
        """
        Expand any list of variables appearing anywhere within a clause tree into
        multiple atomic rules. Works recursively — supports arbitrary nesting.

        Example input:
            {
                "rule_name": "Program Entry → Status dependencies",
                "logic": {
                    "AND": [
                        {
                            "var": ("Training", "Date of Program Entry"),
                            "op": "connected_presence",
                            "compare_to": [
                                ("Personal Information", "Low Income Status"),
                                ("Personal Information", "Single Parent Status")
                            ]
                        },
                        {"var": ("Training", "Enrollment Date"), "op": "is_not_blank"}
                    ]
                }
            }
        """

        def expand_node(node):
            if not isinstance(node, dict):
                return [node]

            expanded_variants = []

            # Step 1️⃣ — Detect expansion keys dynamically
            # If any key has a list of variable tuples, expand those
            if "var" in node and isinstance(node["var"], list):
                variants = []
                for var_entry in node["var"]:
                    new_node = node.copy()
                    new_node["var"] = var_entry
                    variants.append(new_node)
                return variants

            if "compare_to" in node and isinstance(node["compare_to"], list):
                variants = []
                for ref_entry in node["compare_to"]:
                    new_node = node.copy()
                    new_node["compare_to"] = ref_entry
                    variants.append(new_node)
                return variants

            # Step 2️⃣ — Handle compound logic (AND, OR, IF_THEN, etc.)
            for k, v in node.items():
                if isinstance(v, list) and all(isinstance(x, dict) for x in v):
                    sub_expanded = [expand_node(sub) for sub in v]
                    from itertools import product
                    combos = product(*sub_expanded)
                    return [{k: list(combo)} for combo in combos]

            # Step 3️⃣ — Default: no expansion
            return [node]


        expanded_rules = []
        for rule in rules:
            base_logic = rule.get("logic", rule)
            rule_name = rule.get("rule_name", "Unnamed Rule")

            # Expand recursively and flatten
            expanded_variants = expand_node(base_logic)
            for i, logic_variant in enumerate(expanded_variants, start=1):
                expanded_rules.append({
                    **rule,
                    "rule_name": f"{rule_name} (variant {i})" if len(expanded_variants) > 1 else rule_name,
                    "logic": logic_variant
                })

        return expanded_rules


    # def expand_rules(self, rules):
    #     """Expand multi-reference rules into individual atomic rules."""
    #     expanded = []
    #     for rule in rules:
    #         logic = rule.get("logic", {})
    #         if "var_refs" in logic:  # cluster syntax
    #             for ref_sheet, ref_var in logic["var_refs"]:
    #                 new_rule = {
    #                     **rule,
    #                     "rule_name": f"{rule['rule_name']} ↔ {ref_var}",
    #                     "logic": {
    #                         "var": logic["var"],
    #                         "op": logic["op"],
    #                         "var_ref": ref_var,
    #                         "sheet_ref": ref_sheet,
    #                     },
    #                 }
    #                 expanded.append(new_rule)
    #         else:
    #             expanded.append(rule)
    #     return expanded

    def run_all_rules(self, rules):
        """Run a list of rules and aggregate violations."""
        all_violations = []
        for rule in self.expand_rules(rules): ## expand rules accounts for rules that are grouped for ease of interpretation in cross_rule_sets
            result = self.evaluate_rule(rule) ## evaluate rule breaks them out based on whether they are relational ("if/logic") or conditional ("if-then")
            if not result.empty:
                all_violations.append(result)
        return pd.concat(all_violations, ignore_index=True) if all_violations else pd.DataFrame()
