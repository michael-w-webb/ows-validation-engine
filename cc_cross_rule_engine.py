import operator
from functools import reduce
import pandas as pd
import json

from cc_cross_rule_descriptions import * 
from cc_cross_rule_classes import BaseVariable, NumericVariable, DateVariable, CategoricalVariable

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

    def __init__(self, workbook_type, workbook_format, normalized_single_sheet, normalization_schema, file):
        
        """
        Initialize a CrossRuleEngine.

        Args:
            workbook_type (str):
                Logical grouping of the workbook, e.g., "Training Data".
            workbook_format (str):
                Structural format of the workbook
                (e.g. "simple format", "four sheet format").
            dfs_by_sheet (dict[str, pd.DataFrame]):
                Normalized DataFrames indexed by sheet name.
            normalization_schema (dict):
                Schema specifying accepted responses, variable types,
                and metadata for each column in each sheet.
            file (str):
                Identifier used in error reporting (typically filename).
        """
        
        self.workbook_type = workbook_type          # e.g. "training data (workbook type)"
        self.workbook_format = workbook_format      # e.g. "four sheet format" or "simple format (workbook format)"
        self.single_sheet_df = normalized_single_sheet                   # normalized DataFrames by sheet
        self.schema = normalization_schema          # e.g. cc_column_label_list
        self.file = file                            # file name reference (for error reporting)

    def _collect_vars(self, logic):
        """
        Recursively collect all (sheet, column) variable references
        appearing anywhere in a clause tree.
        """
        vars_found = set()

        if isinstance(logic, dict):
            if "var" in logic:
                v = logic["var"]
                if isinstance(v, tuple):
                    vars_found.add(v)
                elif isinstance(v, list):
                    for vv in v:
                        vars_found.add(vv)

            if "compare_to" in logic:
                ref = logic["compare_to"]
                if isinstance(ref, tuple):
                    vars_found.add(ref)
                elif isinstance(ref, list):
                    for rr in ref:
                        vars_found.add(rr)

            for value in logic.values():
                if isinstance(value, (list, dict)):
                    for sub in (value if isinstance(value, list) else [value]):
                        vars_found |= self._collect_vars(sub)

        return vars_found

    def _snapshot_values(self, vars_used, violation_mask):
        """
        Build a per-row snapshot of all relevant variable values
        for rows where the rule is violated.
        """
        snapshots = []

        for (sheet, col) in vars_used:
            df = self.single_sheet_df
            if df is None or col not in df.columns:
                continue

            values = (
                df.loc[violation_mask, col]
                .astype(str)
                .fillna("")
                .values
            )

            snapshots.append(
                pd.Series(
                    values,
                    name=f"(Sheet){sheet}::(Column){col}"
                )
            )

        if snapshots:
            return pd.concat(snapshots, axis=1)
        else:
            return pd.DataFrame(index=violation_mask[violation_mask].index)

    # ============================================================
    # 🔹 Variable retrieval
    # ============================================================
    def get_variable(self, var_name, sheet_key):
        """
        Retrieve and instantiate the appropriate Variable subclass for a
        given (sheet, column) reference.

        This method:
            • Navigates the normalization schema to retrieve metadata  
            • Identifies the correct Variable subclass  
            • Extracts the Series from the workbook  
            • Attaches schema metadata and file context  

        Args:
            var_name (str):
                Column name to retrieve.
            sheet_key (str):
                Sheet containing the column.

        Returns:
            BaseVariable:
                An instantiated Variable subclass (NumericVariable,
                DateVariable, CategoricalVariable, etc.).

        Raises:
            KeyError:
                If the sheet, column, or schema metadata is missing.
        """
        
        #### specifying 'report' here because it is the value used in the 
        #### simple format workbook definitions but isn't necessarily the 
        #### value that is going to be used elsewhere. 

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

        df = self.single_sheet_df
        if df is None:
            raise KeyError(f"DataFrame for sheet '{sheet_key}' not found in dfs_by_sheet.")
        if var_name not in df.columns:
            raise KeyError(f"'{var_name}' not found in DataFrame for sheet '{sheet_key}'.")

        # Instantiate variable object
        series = df[var_name]
        var_obj = cls_ref(var_name, sheet_key, series, self.single_sheet_df, self.schema)
        var_obj.engine = self
        var_obj.accepted_responses = accepted
        var_obj.meta = col_meta
        return var_obj
    


    # ============================================================
    # 🔹 Logic combination and evaluation
    # ============================================================
    def combine(self, masks, logic_op):

        """
        Combine a list of boolean masks using a specified logical operator.

        Supports all operators in the clause grammar:
            AND, OR, NOT, IF_THEN, IF_THEN_ELSE,
            EQUIVALENT/IFF, XOR, ONE_OF, AT_LEAST.

        Args:
            masks (list[pd.Series[bool]]):
                Boolean masks produced by sub-clauses.
            logic_op (str):
                Logical operator name (case-insensitive).

        Returns:
            pd.Series[bool]:
                Combined boolean mask.

        Raises:
            ValueError:
                If an unknown operator is encountered.
        """

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
        Recursively evaluate a clause tree.

        Behavior:
            • Atomic clauses ("var": ...) evaluate via Variable.evaluate().
            • Compound clauses recursively compute sub-masks and merge
            them using ``combine()``.

        Args:
            logic_dict (dict):
                A nested clause tree representing a logical expression.

        Returns:
            pd.Series[bool]:
                Boolean mask indicating whether each row satisfies the clause.
        """

        logic_dict = self.normalize_logic(logic_dict)

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

            # Normalize single clause → list
            if isinstance(subclauses, dict):
                subclauses = [subclauses]

            # Defensive: reject nonsense early
            if not isinstance(subclauses, list):
                raise TypeError(
                    f"{logic_op} expects dict or list, got {type(subclauses)}"
                )

            masks = [self.evaluate_logic(sub) for sub in subclauses]
            return self.combine(masks, logic_op.upper())

    def describe_logic(self, logic_dict, is_condition=False, is_negated = False):
        
        """
        Generate a human-readable natural-language description of a clause tree.

        Used for producing interpretable validation error messages.

        Args:
            logic_dict (dict):
                Logic tree corresponding to a rule.
            is_condition (bool):
                If True, phrasing is softened to reflect antecedent logic
                ("is filled" vs. "must be filled").

        Returns:
            str:
                Human-readable description of the rule logic.
        """
        logic_dict = self.normalize_logic(logic_dict)

        # --- Base case: atomic clause ---
        if "var" in logic_dict:
            (var_sheet, var_name) = logic_dict["var"]
            op = logic_dict.get("op", "").lower()

            # Determine reference for description
            if "values" in logic_dict:
                ref = logic_dict["values"]
            elif "value" in logic_dict:
                ref = logic_dict["value"]
            elif "compare_to" in logic_dict:
                ref = logic_dict["compare_to"]
            else:
                ref = None

            ref_text = format_reference(ref)

            return describe_atomic(
                var_name,
                var_sheet,
                op,
                ref_text,
                is_condition=is_condition, 
                is_negated = is_negated
            )

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

            elif op_upper == "NOT":
                subdescs = self.describe_logic(subclauses[0], is_negated = True)
            else:
                # Regular recursion for other operators (AND, OR, etc.)
                subdescs = [self.describe_logic(sub, is_condition=is_condition) for sub in subclauses]

            extra = None
            if op_upper == "AT_LEAST":
                *subdescs, extra = subdescs  # last one is threshold

            return describe_compound(op_upper, subdescs, extra)


    def _find_primary_var(self, logic):
        """
        Locate the first (sheet, column) reference appearing in a logic tree.

        This determines which sheet/column anchors the rule's error output.

        Args:
            logic (dict):
                A clause tree (possibly nested).

        Returns:
            tuple[str, str] | None:
                (sheet_name, column_name) or None if not found.
        """
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

    

    def normalize_logic(self, logic):

        COMPOUND_OPS = {"AND", "OR", "NOT", "IF_THEN", "IF_THEN_ELSE", "AT_LEAST"}

        if not isinstance(logic, dict):
            raise TypeError(f"Logic must be dict, got {type(logic)}")

        # Atomic clause
        if "var" in logic:
            return logic

        if len(logic) != 1:
            raise ValueError(f"Compound clause must have exactly one operator: {logic}")

        op, subclauses = next(iter(logic.items()))
        op_upper = op.upper()

        if op_upper not in COMPOUND_OPS:
            raise ValueError(f"Unknown logic operator: {op}")

        # Normalize to list
        if isinstance(subclauses, dict):
            subclauses = [subclauses]

        if not isinstance(subclauses, list):
            raise TypeError(f"{op_upper} expects dict or list")

        # Arity checks
        if op_upper == "NOT" and len(subclauses) != 1:
            raise ValueError("NOT expects exactly 1 clause")

        if op_upper == "IF_THEN" and len(subclauses) != 2:
            raise ValueError("IF_THEN expects exactly 2 clauses")

        if op_upper == "IF_THEN_ELSE" and len(subclauses) != 3:
            raise ValueError("IF_THEN_ELSE expects exactly 3 clauses")

        # Recurse
        return {
            op_upper: [self.normalize_logic(sub) for sub in subclauses]
        }
    # ============================================================
    # 🔹 Rule-level evaluation (conditional + relational)
    # ============================================================

    def evaluate_rule(self, rule):
        """
        Evaluate a single rule definition.

        Steps:
            1. Evaluate the rule's clause tree to a boolean mask.
            2. Identify rows where the rule is violated (mask == False).
            3. Determine the rule's primary variable for error context.
            4. Produce a DataFrame conforming to the validation error schema.

        Args:
            rule (dict):
                A rule definition containing:
                    • "rule_name"
                    • "logic" (nested clause tree)

        Returns:
            pd.DataFrame:
                Violations with metadata for file, sheet, row_number,
                column, rule description, normalized value, and id_key.
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

        df = self.single_sheet_df

        rule_text = self.describe_logic(logic)

        vars_used = self._collect_vars(logic)
        context_df = self._snapshot_values(vars_used, violations)
        context_text_series = context_df.apply(
            lambda row: json.dumps(row.to_dict(), ensure_ascii=False),
            axis=1
        )

        if self.workbook_format == "simple format":
            main_sheet = "Report"

        # 4️⃣ Produce unified, normalization-compatible output
        out = pd.DataFrame({
            "file": self.file or "",
            "sheet": main_sheet,
            "row_number": (
                df.loc[violations, f"row_number_{main_sheet}"].values
                if f"row_number_{main_sheet}" in df else None
            ),
            "column": main_col,
            "rule": rule_text,
            "raw_value": "Not Applicable.",
            "normalized": context_text_series.values,
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
        Expand rules that contain lists of variables or compare-to
        references into multiple atomic rule variants.

        This supports authoring syntactic sugar such as:
            • Multiple "var" references
            • Multiple "compare_to" references
            • Nested logical constructs with variable lists

        Args:
            rules (list[dict]):
                List of rule definitions (each containing "logic").

        Returns:
            list[dict]:
                Fully expanded rules, one per atomic pair of references.
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
        """
        Execute a list of rules (expanding them first) and aggregate violations.

        Args:
            rules (list[dict]):
                Rules to evaluate.

        Returns:
            pd.DataFrame:
                Concatenated violation results for all rules.
                Empty DataFrame if no violations occur.
        """
        all_violations = []
        for rule in self.expand_rules(rules): ## expand rules accounts for rules that are grouped for ease of interpretation in cross_rule_sets
            result = self.evaluate_rule(rule) ## evaluate rule breaks them out based on whether they are relational ("if/logic") or conditional ("if-then")
            if not result.empty:
                all_violations.append(result)
        return pd.concat(all_violations, ignore_index=True) if all_violations else pd.DataFrame()
