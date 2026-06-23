import operator
from functools import reduce
import pandas as pd
import json

from validation_engine.cross_rule_descriptions import * 
from validation_engine.cross_rule_classes import BaseVariable, NumericVariable, DateVariable, CategoricalVariable

from validation_engine.column_names import (
    find_column,
    find_columns,
    get_value,
)

class CrossRuleEngine:
    """
    Recursive engine for evaluating cross-sheet validation rules against
    normalized workbook data.

    Rules are defined as nested clause trees composed of:

        - atomic conditions
        - logical operators
        - conditional operators
        - recursively nested subclauses

    Variables are referenced using:

        (sheet_name, column_name)

    tuples and resolved dynamically against the merged validation
    dataframe produced by the ValidationEngine.

    Example
    -------
    Atomic clause:

    >>> {
    ...     "var": ("Training", "Completed Date"),
    ...     "op": "is_not_blank"
    ... }

    Compound clause:

    >>> {
    ...     "IF_THEN": [
    ...         {
    ...             "var": ("Training", "Completed Date"),
    ...             "op": "is_not_blank"
    ...         },
    ...         {
    ...             "var": ("Outcomes", "Employment Status"),
    ...             "op": "is_not_blank"
    ...         }
    ...     ]
    ... }

    Evaluation Pipeline
    -------------------
    Rule execution proceeds in five stages:

        1. normalize clause-tree structure
        2. expand grouped rule definitions
        3. resolve schema-aware variables
        4. recursively evaluate Boolean masks
        5. generate validation violations

    Data Model
    ----------
    The engine operates on a row-aligned dataframe in which workbook
    sheets have already been merged together.

    Sheet provenance is preserved using the delimiter:

        _|_|_

    Example column:

        Employment Status_normalized_|_|_Outcomes

    Responsibilities
    ----------------
    The engine is responsible for:

        - recursive rule evaluation
        - logical mask combination
        - schema-aware variable resolution
        - grouped rule expansion
        - natural-language rule descriptions
        - validation violation generation

    Notes
    -----
    The engine assumes workbook data has already been normalized and
    merged by the ValidationEngine before cross-rule execution begins.
    """
    def __init__(self, workbook_type, workbook_format, normalized_single_sheet, normalization_schema, file):

        """
        Initialize the cross-rule evaluation engine.

        Parameters
        ----------
        workbook_type : str
            Logical workbook category used for schema lookup.

        workbook_format : str
            Workbook layout definition used within the schema hierarchy.

        normalized_single_sheet : pandas.DataFrame
            Unified normalized dataframe containing merged workbook sheets.

        normalization_schema : dict
            Nested workbook schema containing variable metadata and
            accepted response definitions.

        file : str
            File identifier used in validation output and error reporting.

        Notes
        -----
        The engine operates on a merged dataframe representation in which
        sheet provenance is encoded directly into column names using the
        delimiter:

            _|_|_
        """
        self.workbook_type = workbook_type          # e.g. "training data (workbook type)"
        self.workbook_format = workbook_format      # e.g. "four sheet format" or "simple format (workbook format)"
        self.single_sheet_df = normalized_single_sheet                   # normalized DataFrames by sheet
        self.schema = normalization_schema          # e.g. cc_column_label_list
        self.file = file

    def _collect_vars(self, logic):

        """
        Recursively collect all variable references used in a clause tree.

        Variable references are extracted from:

            - "var"
            - "compare_to"

        fields appearing anywhere within the nested logic structure.

        Parameters
        ----------
        logic : dict
            Recursive clause-tree structure.

        Returns
        -------
        set[tuple[str, str]]
            Deduplicated set of:

                (sheet_name, column_name)

            references used by the rule.

        Notes
        -----
        This method performs structural traversal only. It does not resolve
        dataframe columns or evaluate logic.
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
        Extract contextual variable values for violated rows.

        For each referenced variable, values are pulled from the merged
        dataframe for rows where the supplied violation mask is True.

        Parameters
        ----------
        vars_used : set[tuple[str, str]]
            Set of logical variable references in the form:

                (sheet_name, column_name)

        violation_mask : pandas.Series[bool]
            Boolean mask identifying rows that violated the rule.

        Returns
        -------
        pandas.DataFrame
            Snapshot dataframe containing one column per referenced
            variable and one row per violated record.

        Notes
        -----
        Variable references that cannot be resolved are skipped silently.
        Snapshot values are primarily used for debugging, explainability,
        and audit output.
        """ 
        snapshots = []

        for (sheet, col) in vars_used:
            df = self.single_sheet_df
            try:
                series = self._resolve_series(df, col, sheet)
            except KeyError:
                continue

            values = (
                series.loc[violation_mask]
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

    def _resolve_series(self, df, var_name, sheet_key):
        """
        Resolve a logical variable reference to a dataframe column.

        Resolution prefers normalized columns before falling back to raw columns.
        Ambiguous matches are treated as structural errors.
        """

        base = var_name.replace("_normalized", "")

        # Prefer normalized column for this sheet.
        try:
            col = find_column(
                df.columns,
                base=base,
                sheet=sheet_key,
                normalized=True
            )
            return df[col]

        except KeyError:
            # No normalized match; try raw below.
            pass

        except ValueError as e:
            raise ValueError(
                "Ambiguous normalized column reference in cross-rule resolution.\n"
                f"var_name={var_name!r}, sheet_key={sheet_key!r}\n\n"
                f"{e}"
            ) from e

        # Fall back to raw column for this sheet.
        try:
            col = find_column(
                df.columns,
                base=base,
                sheet=sheet_key,
                normalized=False
            )
            return df[col]

        except KeyError as e:
            raise KeyError(
                "Column not found in cross-rule resolution.\n"
                f"var_name={var_name!r}, sheet_key={sheet_key!r}, base={base!r}"
            ) from e

        except ValueError as e:
            raise ValueError(
                "Ambiguous raw column reference in cross-rule resolution.\n"
                f"var_name={var_name!r}, sheet_key={sheet_key!r}\n\n"
                f"{e}"
            ) from e
    # ============================================================
    # 🔹 Variable retrieval
    # ============================================================
    def get_variable(self, var_name, sheet_key):
        """
        Resolve and instantiate a schema-aware Variable object.

        This method:

            - retrieves variable metadata from the normalization schema
            - resolves the associated dataframe column
            - selects the appropriate Variable subclass
            - attaches runtime metadata used during evaluation

        Supported subclasses include:

            - NumericVariable
            - DateVariable
            - CategoricalVariable
            - BaseVariable

        Parameters
        ----------
        var_name : str
            Logical variable name.

        sheet_key : str
            Logical sheet reference associated with the variable.

        Returns
        -------
        BaseVariable
            Initialized Variable subclass instance.

        Raises
        ------
        KeyError
            If the variable definition, schema entry, or dataframe column
            cannot be resolved.

        Notes
        -----
        Simple-format workbooks internally normalize all sheet references
        to:

            "Report"
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
        
        series = self._resolve_series(df, var_name, sheet_key)
        
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
        Combine Boolean masks using a logical operator.

        Parameters
        ----------
        masks : list[pandas.Series[bool]]
            Boolean masks produced by recursive subclause evaluation.

        logic_op : str
            Logical operator name.

        Returns
        -------
        pandas.Series[bool]
            Combined Boolean evaluation mask.

        Supported Operators
        -------------------
        AND
            All clauses must evaluate True.

        OR
            At least one clause must evaluate True.

        NOT
            Negates a single clause.

        IF_THEN
            Conditional implication.

        IF_THEN_ELSE
            Conditional branching.

        EQUIVALENT / IFF
            Clauses must share the same truth value.

        XOR / ONE_OF
            Exactly one clause must evaluate True.

        AT_LEAST
            At least N clauses must evaluate True.

        Raises
        ------
        ValueError
            If an unsupported logical operator is encountered.

        Notes
        -----
        All masks are assumed to be index-aligned to the merged validation
        dataframe.
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
        Recursively evaluate a clause-tree logical expression.

        Atomic clauses are evaluated using schema-aware Variable objects.
        Compound clauses recursively evaluate descendant clauses and combine
        their Boolean masks using logical operators.

        Parameters
        ----------
        logic_dict : dict
            Recursive clause-tree structure describing the rule logic.

        Returns
        -------
        pandas.Series[bool]
            Boolean mask where:

                True  -> row satisfies rule
                False -> row violates rule

        Notes
        -----
        This method forms the core recursive evaluation layer of the
        CrossRuleEngine.
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
        Generate a human-readable description for a clause tree.

        Atomic clauses are rendered using `describe_atomic()`.
        Compound clauses are rendered recursively using
        `describe_compound()`.

        Parameters
        ----------
        logic_dict : dict
            Recursive clause-tree structure.

        is_condition : bool, default False
            If True, descriptive phrasing is used for conditional
            antecedents.

        Returns
        -------
        str
            Natural-language description of the logical expression.
        """
         
        logic_dict = self.normalize_logic(logic_dict)

        # --- Base case: atomic clause ---
        if "var" in logic_dict:
            (var_sheet, var_name) = logic_dict["var"]
            op = logic_dict.get("op", "").lower()

            # Determine reference for description
            if "language_substitute" in logic_dict:
                ref = logic_dict["language_substitute"]
            elif "values" in logic_dict:
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
                subdescs = self.describe_logic(subclauses[0], is_condition = is_condition, is_negated = True)
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

        """
        Validate and canonicalize a recursive clause-tree structure.

        Compound operators are normalized into a consistent internal form
        so downstream evaluation logic can assume predictable structure.

        Canonicalization behavior includes:

            - uppercasing logical operators
            - enforcing operator arity
            - recursively normalizing subclauses
            - wrapping single compound subclauses in lists

        Atomic clauses containing ``"var"`` are passed through unchanged.

        Parameters
        ----------
        logic : dict
            Recursive clause-tree structure.

        Returns
        -------
        dict
            Normalized logic tree suitable for evaluation.

        Raises
        ------
        ValueError
            If the logic structure is invalid or violates operator arity
            requirements.

        Notes
        -----
        This method validates structure only. It does not resolve variables
        or evaluate rule logic.
        """

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
        Evaluate a single cross-rule definition and generate violations.

        Parameters
        ----------
        rule : dict
            Rule definition containing:

                - rule_name
                - logic

        Returns
        -------
        pandas.DataFrame
            Validation violations generated by the rule.

        Notes
        -----
        Violations are returned using the standard validation schema and
        include contextual snapshots of referenced variable values.
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

        row_col = find_column(
            df.columns,
            base=f"row_number_{main_sheet}",
            normalized=False
        )

        row_values = df.loc[violations, row_col].values if row_col else None

        # 4️⃣ Produce unified, normalization-compatible output
        out = pd.DataFrame({
            "file": self.file or "",
            "sheet": main_sheet,
            "row_number": row_values,
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
        Expand grouped rule definitions into atomic rule variants.

        Rules containing lists in:

            - "var"
            - "compare_to"

        are expanded into multiple concrete rule definitions before
        evaluation.

        Parameters
        ----------
        rules : list[dict]
            Rule definitions.

        Returns
        -------
        list[dict]
            Expanded atomic rule definitions.

        Notes
        -----
        Expansion improves rule authoring ergonomics while preserving
        granular violation reporting.
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

    def run_all_rules(self, rules):
        
        """
        Evaluate a collection of cross-rule definitions.

        Rules are first expanded into atomic variants and then evaluated
        individually. Violations produced by each rule are concatenated
        into a single validation dataframe.

        Parameters
        ----------
        rules : list[dict]
            Cross-rule definitions.

        Returns
        -------
        pandas.DataFrame
            Combined validation violations generated across all rules.

            Returns an empty dataframe with the standard validation schema
            if no violations are detected.

        Notes
        -----
        Rules producing no violations are omitted from the final output.
        """
        all_violations = []
        for rule in self.expand_rules(rules): ## expand rules accounts for rules that are grouped for ease of interpretation in cross_rule_sets
            result = self.evaluate_rule(rule) ## evaluate rule breaks them out based on whether they are relational ("if/logic") or conditional ("if-then")
            if not result.empty:
                all_violations.append(result)
        return pd.concat(all_violations, ignore_index=True) if all_violations else pd.DataFrame()
