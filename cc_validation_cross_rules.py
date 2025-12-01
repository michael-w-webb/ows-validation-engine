import pandas as pd
from helpers import cross_errors_df



### Conditional presence rule requires column y to be present or absent in accordance with whether column x is present or absent 
###  set for this one is "CONNECTED_PRESENCE_RULES"

def connected_presence(dfs_by_sheet, sheet_x: str, col_x: str,
                       sheet_y: str, col_y: str,
                       file=None, row_offset: int = 1, column_error_index = None):
    """
    Cross rule: col_x in sheet_x and col_y in sheet_y must both be present or both be blank.
    """
    df_x = dfs_by_sheet[sheet_x]
    df_y = dfs_by_sheet[sheet_y]
    print(df_x.columns)
    print(len(df_x))
    print(sheet_x)
    print(sheet_y)
    # Align on id_key
    merged = pd.merge(df_x[["id_key", col_x]], df_y[["id_key", col_y, "row_number"]], on="id_key", how="outer")

    x_present = merged[col_x].astype("string").str.strip().replace("", pd.NA).notna()
    y_present = merged[col_y].astype("string").str.strip().replace("", pd.NA).notna()

    mask = x_present ^ y_present

    return cross_errors_df(
        merged,
        [col_x, col_y],
        {f"Connected presence violation: '{col_x}' ({sheet_x}) and '{col_y}' ({sheet_y}) must both be present or both be blank": mask},
        file=file,
        sheet=f"{sheet_x} <-> {sheet_y}",
        pairs= [(sheet_x,col_x),(sheet_y,col_y)],
        row_offset=row_offset,
        column_error_index=column_error_index
    )

# #### Conditionally blank, if col x is blank then col y must be blank (the negative half of conditional presence)
# #### set for this one is CONDITIONALLY_BLANK_RULES

# def conditionally_blank(dfs_by_sheet, sheet_x: str, col_x: str,
#                         sheet_y: str, col_y: str,
#                         file=None, row_offset: int = 1, column_error_index = None):
#     """
#     Cross rule: If col_x (sheet_x) is blank, then col_y (sheet_y) must also be blank.
#     """

#     df_x = dfs_by_sheet[sheet_x]
#     df_y = dfs_by_sheet[sheet_y]

#     # Align by id_key so the same participant is compared
#     merged = pd.merge(df_x[["id_key", col_x]], df_y[["id_key", col_y, "row_number"]],
#                       on="id_key", how="outer")

#     x_blank = merged[col_x].astype("string").str.strip().replace("", pd.NA).isna()
#     y_present = merged[col_y].astype("string").str.strip().replace("", pd.NA).notna()

#     mask = x_blank & y_present

#     return cross_errors_df(
#         merged,
#         [col_x, col_y],
#         {f"Conditionally blank violation: If '{col_x}' ({sheet_x}) is blank, "
#          f"'{col_y}' ({sheet_y}) must also be blank": mask},
#         file=file,
#         sheet=f"{sheet_x} <-> {sheet_y}",
#         pairs= [(sheet_x,col_x),(sheet_y,col_y)],
#         row_offset=row_offset,
#         column_error_index=column_error_index
#     )


# ### col y must be blank unless col x is a speciif cvalue 
# ### this is basically conditionally blank but instead of whether x is blank/not blank it is whether x is set to a specific value
# ### Set for this one is "CONDITIONALLY_ALLOWED_RULES"

# def conditionally_allowed(dfs_by_sheet, sheet_x: str, col_x: str,
#                           sheet_y: str, col_y: str, trigger_values: list[str],
#                           file=None, row_offset: int = 1, column_error_index = None):
#     df_x = dfs_by_sheet[sheet_x]
#     df_y = dfs_by_sheet[sheet_y]

#     merged = pd.merge(df_x[["id_key", col_x]], df_y[["id_key", col_y, "row_number"]], on="id_key", how="outer")

#     x_trigger = merged[col_x].astype("string").str.strip().str.casefold().isin(
#         [v.casefold() for v in trigger_values]
#     )
#     y_present = merged[col_y].astype("string").str.strip().replace("", pd.NA).notna()

#     mask = ~x_trigger & y_present

#     return cross_errors_df(
#         merged,
#         [col_x, col_y],
#         {f"Conditionally allowed violation: '{col_y}' ({sheet_y}) must be blank unless '{col_x}' ({sheet_x}) is {trigger_values}": mask},
#         file=file,
#         sheet=f"{sheet_x} <-> {sheet_y}",
#         pairs= [(sheet_x,col_x),(sheet_y,col_y)],
#         row_offset=row_offset,
#         column_error_index=column_error_index
#     )


def conditionally_blank_unless(
    dfs_by_sheet,
    if_pair: tuple[str, str],              # e.g. ("Participant Database", "Exit Status")
    then_pairs: list[tuple[str, str]],     # e.g. [("Employment", "Job Title"), ("Employment", "Employment Type")]
    trigger_values: list[str],             # e.g. ["__NOT_BLANK__"] or ["employed", "hired"]
    file=None, row_offset: int = 1, column_error_index=None,
):
    """
    Cross rule:
    Each column in 'then_pairs' must be BLANK unless the condition column (if_pair)
    meets a trigger condition defined by trigger_values.

    Logic summary:
      - "__NOT_BLANK__" in trigger_values → X is considered "allowed" when it is not blank
      - otherwise → X is allowed only when its value (case-insensitive) is in trigger_values
      - Violation = (X does NOT meet trigger condition) AND (Y is filled)
    """

    import pandas as pd

    # --- Parse the controlling column (if_pair) ---
    if not if_pair or len(if_pair) != 2:
        raise ValueError("if_pair must be a (sheet, column) tuple defining the trigger column.")

    sheet_x, col_x = if_pair
    df_x = dfs_by_sheet[sheet_x]
    base = df_x[["id_key", col_x]].copy()

    # --- Normalize X and trigger logic ---
    trigger_values_norm = [v.casefold().strip() for v in trigger_values or []]
    x_str = base[col_x].astype("string").str.strip()
    x_blank = x_str.replace("", pd.NA).isna()

    # default: no trigger condition met
    x_trigger = pd.Series(False, index=base.index)

    # Allow any nonblank X if "__NOT_BLANK__" included
    if "__NOT_BLANK__" in trigger_values:
        x_trigger = x_trigger | (~x_blank)

    # Allow specific values if present in trigger_values
    if trigger_values:
        x_trigger = x_trigger | x_str.str.casefold().isin(trigger_values_norm)

    # Create human-readable description
    if "__NOT_BLANK__" in trigger_values and len(trigger_values) == 1:
        trigger_desc = "not blank"
    else:
        vals = [v for v in trigger_values if v != "__NOT_BLANK__"]
        trigger_desc = ", ".join(vals) if vals else "not blank"

    all_violations = []

    # --- Apply to each dependent column ---
    for sheet_y, col_y in then_pairs:
        df_y = dfs_by_sheet[sheet_y]

        merged = base.merge(df_y[["id_key", col_y, "row_number"]], on="id_key", how="left")

        y_str = merged[col_y].astype("string").str.strip()
        y_present = y_str.replace("", pd.NA).notna()

        # Violation: Y is filled but X does NOT meet trigger
        violation_mask = (~x_trigger.reindex(merged.index, fill_value=False)) & y_present

        message = (
            f"Conditionally allowed violation: '{col_y}' ({sheet_y}) must be blank unless "
            f"'{col_x}' ({sheet_x}) is {trigger_desc}."
        )

        errs = cross_errors_df(
            merged,
            [col_x, col_y],
            {message: violation_mask},
            file=file,
            sheet=f"{sheet_x} <-> {sheet_y}",
            pairs=[(sheet_x, col_x), (sheet_y, col_y)],
            row_offset=row_offset,
            column_error_index=column_error_index,
        )

        if not errs.empty:
            all_violations.append(errs)

    # --- Combine all results ---
    return (
        pd.concat(all_violations)
        if all_violations
        else pd.DataFrame(columns=["file", "sheet", "row_number", "column", "rule", "raw_value", "normalized"])
    )


def conditionally_required(
    dfs_by_sheet,
    if_pairs: list[tuple[str, str]],
    then_pairs: list[tuple[str, str]],
    trigger_values: list[str] = None,
    file=None, row_offset: int = 1, column_error_index=None
):
    """
    For each THEN column:
        If IF condition(s) are met (nonblank or trigger match),
        the THEN column must NOT be blank.
    """

    errors = []

    # --- Build merged base only once for the IF pairs ---
    sheet0, col0 = if_pairs[0]
    merged_base = dfs_by_sheet[sheet0][["id_key", col0]]

    for sheet, col in if_pairs[1:]:
        merged_base = merged_base.merge(
            dfs_by_sheet[sheet][["id_key", col]], on="id_key", how="outer"
        )

    def is_present(series):
        return series.astype("string").str.strip().replace("", pd.NA).notna()

    def matches_trigger(series, triggers):
        cleaned = series.astype("string").str.strip().str.casefold()
        return cleaned.isin([t.casefold() for t in triggers])

    # Build IF-condition mask once
    if trigger_values:
        if_condition = pd.Series(False, index=merged_base.index)
        for _, col in if_pairs:
            if_condition |= matches_trigger(merged_base[col], trigger_values)
        trigger_desc = f"equal to one of {trigger_values}"
    else:
        if_condition = pd.Series(True, index=merged_base.index)
        for _, col in if_pairs:
            if_condition &= is_present(merged_base[col])
        trigger_desc = "not blank"

    # --- Evaluate each THEN pair separately ---
    for sheet, col in then_pairs:
        df_then = dfs_by_sheet[sheet][["id_key", col, "row_number"]]
        merged = merged_base.merge(df_then, on="id_key", how="left")

        y_blank = merged[col].astype("string").str.strip().replace("", pd.NA).isna() 
        y_blank = y_blank.reindex(if_condition.index, fill_value=False)
        violation_mask = if_condition & y_blank

        if_cols = [f"'{c}' ({s})" for s, c in if_pairs]
        message = (
            f"Conditionally required violation: If all of {', '.join(if_cols)} are {trigger_desc}, "
            f"then '{col}' ({sheet}) must also not be blank."
        )

        errs = cross_errors_df(
            merged,
            [c for _, c in if_pairs] + [col],
            {message: violation_mask},
            file=file,
            sheet=f"{' <-> '.join([s for s, _ in if_pairs])} <-> {sheet}",
            pairs=if_pairs + [(sheet, col)],
            row_offset=row_offset,
            column_error_index=column_error_index,
        )

        if not errs.empty:
            errors.append(errs)

    return pd.concat(errors) if errors else pd.DataFrame(
        columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
    )

def conditionally_required_by_date_comparison(
    dfs_by_sheet,
    if_pairs: list[tuple[str, str]],      # e.g. [("Program_Enrollment", "Training End Date"), ("Reference Dates", "Quarter End Date")] or [("Program_Enrollment", "Training End Date"), ("Reference", "2025-09-30")]
    then_pairs: list[tuple[str, str]],    # e.g. [("Program_Enrollment", "Training Completion Status"), ("Employment", "Employment Status")]
    relation: str = "after",              # "before" or "after"
    allowed_values: list[str] = None,     # [] or None means must not be blank
    reference_date: str = None,           # optional static date (used if 2nd pair is literal)
    file=None, row_offset: int = 1, column_error_index=None,
):
    """
    Cross rule: If date1 and date2 (from if_pairs) satisfy a temporal relation
    (e.g., date1 is before date2, or before a fixed reference date),
    then each column in then_pairs must either be blank or one of a list of allowed values.

    Supports both:
      - Comparing two date columns from sheets
      - Comparing a date column to a fixed reference date
    """

    if len(if_pairs) < 1:
        raise ValueError("if_pairs must contain at least one (sheet, column) pair for date comparison.")

    # --- Extract first date column ---
    sheet_date1, col_date1 = if_pairs[0]
    df1 = dfs_by_sheet[sheet_date1]
    base = df1[["id_key", col_date1]].copy()

    # --- Determine second date source (sheet vs literal) ---
    if len(if_pairs) > 1:
        sheet_date2, col_date2 = if_pairs[1]
    else:
        sheet_date2, col_date2 = (None, None)

    if sheet_date2 and sheet_date2 in dfs_by_sheet:
        # Case 1: compare two sheet columns
        df2 = dfs_by_sheet[sheet_date2]
        base = base.merge(df2[["id_key", col_date2]], on="id_key", how="outer")
        base[col_date2] = pd.to_datetime(base[col_date2], errors="coerce")
        condition_label_target = f"{col_date2} ({sheet_date2})"
    else:
        # Case 2: compare to static date literal
        static_date = pd.to_datetime(col_date2 or reference_date, errors="coerce")
        base["__static_ref_date__"] = static_date
        col_date2 = "__static_ref_date__"
        condition_label_target = f"{reference_date or col_date2}"

    # --- Convert first date ---
    base[col_date1] = pd.to_datetime(base[col_date1], errors="coerce")

    # --- Evaluate the date condition ---
    if relation == "after":
        date_condition = base[col_date1] > base[col_date2]
        condition_label = f"{col_date1} ({sheet_date1}) is after {condition_label_target}"
    elif relation == "before":
        date_condition = base[col_date1] < base[col_date2]
        condition_label = f"{col_date1} ({sheet_date1}) is before {condition_label_target}"
    else:
        raise ValueError("relation must be 'before' or 'after'.")

    all_violations = []

    # --- Process each 'then' column independently (avoids merge explosion) ---
    for sheet_value, col_value in then_pairs:
        dfv = dfs_by_sheet[sheet_value]

        merged = base.merge(dfv[["id_key", col_value, "row_number"]], on="id_key", how="left")

        # Clean value
        val_clean = merged[col_value].astype("string").str.strip().replace("", pd.NA)

        # Allowed logic
        if allowed_values:
            allowed_norm = [a.casefold().strip() for a in allowed_values]
            val_not_allowed = val_clean.notna() & ~val_clean.str.casefold().isin(allowed_norm)
        else:
            val_not_allowed = val_clean.isna()  # must NOT be blank when condition holds

        # Violation mask
        violation_mask = date_condition.reindex(merged.index, fill_value=False) & val_not_allowed

        allowed_text = allowed_values if allowed_values else ["not blank"]
        message = (
            f"Conditionally required by date comparison: When {condition_label}, "
            f"'{col_value}' ({sheet_value}) must be one of {allowed_text}."
        )

        errs = cross_errors_df(
            merged,
            [col_date1, col_date2, col_value],
            {message: violation_mask},
            file=file,
            sheet=f"{sheet_date1} <-> {sheet_date2 or 'Static Date'} <-> {sheet_value}",
            pairs=if_pairs + [(sheet_value, col_value)],
            row_offset=row_offset,
            column_error_index=column_error_index,
        )

        if not errs.empty:
            all_violations.append(errs)

    return pd.concat(all_violations) if all_violations else pd.DataFrame(
        columns=["file","sheet","row_number","column","rule","raw_value","normalized"]
    )


def conditional_link(
    dfs_by_sheet,
    if_pairs: list[tuple[str, str]] | tuple[str, str],
    then_pairs: list[tuple[str, str]] | tuple[str, str],
    trigger_values: dict[tuple[str, str], list[str]] | list[str] | None = None,
    operator: str = "AND",                 # 'AND' or 'OR'
    mode: str = "require",                 # 'require', 'blank', 'symmetric', 'equal', 'not_equal', 'enforce_value', 'date_require'
    allowed_values: list[str] | None = None,
    relation: str | None = None,           # for date_require: 'before' or 'after'
    reference_date: str | None = None,     # for date_require, optional literal
    symmetric: bool = False,
    require_when_trigger: bool | None = None,
    file=None,
    row_offset: int = 1,
    column_error_index=None,
):
    """
    Generalized cross-sheet rule handler.

    Supports:
      - Multiple IF conditions (AND/OR)
      - Multiple THEN conditions
      - All logic modes: 'require', 'blank', 'equal', 'not_equal', 'enforce_value', 'symmetric', 'date_require'
      - Date comparison conditions: date1 before/after date2 or a fixed reference date
    """

    import pandas as pd

    # --- Normalize inputs ---
    if isinstance(if_pairs, tuple):
        if_pairs = [if_pairs]
    if isinstance(then_pairs, tuple):
        then_pairs = [then_pairs]

    # ==========================================================
    # STEP 1: Build trigger or date condition
    # ==========================================================
    compound_trigger = None
    trigger_descriptions = []

    # --- Handle DATE comparison mode separately ---
    if mode == "date_require":

        # --- Base date (first pair) ---
        sheet_date1, col_date1 = if_pairs[0]
        df1 = dfs_by_sheet[sheet_date1]
        base = df1[["id_key", col_date1]].copy()

        # --- Second date: sheet column or static literal ---
        if len(if_pairs) > 1:
            sheet_date2, col_date2 = if_pairs[1]
        else:
            sheet_date2, col_date2 = (None, None)

        if sheet_date2 and sheet_date2 in dfs_by_sheet:
            df2 = dfs_by_sheet[sheet_date2]
            base = base.merge(df2[["id_key", col_date2]], on="id_key", how="outer")
            target_label = f"{col_date2} ({sheet_date2})"
        else:
            static_date = pd.Timestamp(reference_date or col_date2)
            base["__static_ref_date__"] = static_date
            col_date2 = "__static_ref_date__"
            target_label = f"static date {static_date.date()}"

        if relation == "after":
            condition_mask = base[col_date1] > base[col_date2]
            relation_text = "after"
        elif relation == "before":
            condition_mask = base[col_date1] < base[col_date2]
            relation_text = "before"
        else:
            raise ValueError("relation must be 'before' or 'after' for mode='date_require'.")

        condition_label = f"'{col_date1}' ({sheet_date1}) is {relation_text} {target_label}"
        base_condition = condition_mask
        compound_desc = condition_label

    else:
        
        # --- Regular (non-date) trigger logic ---
        for sheet_x, col_x in if_pairs:
            df_x = dfs_by_sheet[sheet_x]
            s = df_x[col_x].astype("string").str.strip()
            s_blank = s.replace("", pd.NA).isna()

            # Handle trigger values as dict or list
            if isinstance(trigger_values, dict):
                values = trigger_values.get((sheet_x, col_x), ["__NOT_BLANK__"])
            else:
                values = trigger_values or ["__NOT_BLANK__"]

            norm_values = [v.casefold().strip() for v in values]
            s_trigger = pd.Series(False, index=df_x.index)

            if "__NOT_BLANK__" in norm_values:
                s_trigger |= ~s_blank
            s_trigger |= s.str.casefold().isin(norm_values)

            if compound_trigger is None:
                compound_trigger = s_trigger
            elif operator.upper() == "AND":
                compound_trigger &= s_trigger
            elif operator.upper() == "OR":
                compound_trigger |= s_trigger
            else:
                raise ValueError(f"Unsupported operator: {operator}")

            trigger_desc = (
                "not blank"
                if "__NOT_BLANK__" in norm_values and len(norm_values) == 1
                else ", ".join([v for v in values if v != "__NOT_BLANK__"]) or "not blank"
            )
            trigger_descriptions.append(f"'{col_x}' ({sheet_x}) is {trigger_desc}")

        compound_desc = f" {'AND' if operator.upper() == 'AND' else 'OR'} ".join(trigger_descriptions)
        base_condition = compound_trigger

    # ==========================================================
    # STEP 2: Normalize mode aliases
    # ==========================================================
    if require_when_trigger is True:
        mode = "require"
    elif require_when_trigger is False:
        mode = "blank"
    elif symmetric:
        mode = "symmetric"

    all_errors = []

    # ==========================================================
    # STEP 3: Apply to each THEN pair
    # ==========================================================
    for sheet_y, col_y in then_pairs:
        df_y = dfs_by_sheet[sheet_y]

        # Merge with the first IF sheet as base
        base_sheet, base_col = if_pairs[0]
        df_base = dfs_by_sheet[base_sheet]

        merged = pd.merge(
            df_base[["id_key", base_col]],
            df_y[["id_key", col_y, "row_number"]],
            on="id_key",
            how="outer"
        )

        # Align condition mask to merged index
        condition_mask = base_condition.reindex(merged.index, fill_value=False)

        # ======================================================
        #  --- Mode logic ---
        # ======================================================
        y_str = merged[col_y].astype("string").str.strip()
        y_blank = y_str.replace("", pd.NA).isna()
        y_present = ~y_blank

        if mode == "symmetric":
            x_str = merged[base_col].astype("string").str.strip()
            x_blank = x_str.replace("", pd.NA).isna()
            mask = x_blank ^ y_blank
            rule_type = "Connected presence"
            message = (
                f"{rule_type} violation: '{base_col}' ({base_sheet}) and '{col_y}' ({sheet_y}) "
                f"must both be filled or both be blank."
            )

        elif mode == "require":
            mask = condition_mask & y_blank
            rule_type = "Conditionally required"
            message = (
                f"{rule_type} violation: '{col_y}' ({sheet_y}) must not be blank when {compound_desc}."
            )

        elif mode == "blank":
            mask = (~condition_mask) & y_present
            rule_type = "Conditionally blank"
            message = (
                f"{rule_type} violation: '{col_y}' ({sheet_y}) must be blank unless {compound_desc}."
            )

        elif mode == "equal":
            x_str = merged[base_col].astype("string").str.strip()
            mask = condition_mask & (x_str != y_str)
            rule_type = "Conditionally equal"
            message = (
                f"{rule_type} violation: when {compound_desc}, '{col_y}' ({sheet_y}) must equal '{base_col}' ({base_sheet})."
            )

        elif mode == "not_equal":
            x_str = merged[base_col].astype("string").str.strip()
            mask = condition_mask & (x_str == y_str)
            rule_type = "Conditionally not equal"
            message = (
                f"{rule_type} violation: when {compound_desc}, '{col_y}' ({sheet_y}) must differ from '{base_col}' ({base_sheet})."
            )

        elif mode == "enforce_value":
            mask = condition_mask & (~y_str.str.casefold().isin([v.casefold() for v in (allowed_values or [])]))
            rule_type = "Conditional value enforcement"
            allowed_desc = ", ".join(allowed_values or [])
            message = (
                f"{rule_type} violation: when {compound_desc}, '{col_y}' ({sheet_y}) must be one of: {allowed_desc}."
            )

        elif mode == "date_require":
            # (Condition already built in Step 1)
            if allowed_values:
                allowed_norm = [a.casefold().strip() for a in allowed_values]
                mask = (
                    condition_mask
                    & (y_str.notna() & ~y_str.str.casefold().isin(allowed_norm))
                )
                allowed_text = f"one of {allowed_values}"
            else:
                mask = condition_mask & y_blank
                allowed_text = "not blank"

            rule_type = "Conditionally required by date comparison"
            message = (
                f"{rule_type}: When {compound_desc}, '{col_y}' ({sheet_y}) must be {allowed_text}."
            )

        else:
            raise ValueError(f"Unknown mode: {mode}")

        errs = cross_errors_df(
            merged,
            [p[1] for p in if_pairs] + [col_y],
            {message: mask},
            file=file,
            sheet=f"{' & '.join([s for s, _ in if_pairs])} <-> {sheet_y}",
            pairs=if_pairs + [(sheet_y, col_y)],
            row_offset=row_offset,
            column_error_index=column_error_index,
        )

        if not errs.empty:
            all_errors.append(errs)

    return (
        pd.concat(all_errors)
        if all_errors
        else pd.DataFrame(columns=["file","sheet","row_number","column","rule","raw_value","normalized"])
    )
