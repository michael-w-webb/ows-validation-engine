from applications.career_connect_grantee_sheets.workbook_definitions import workbook_definitions
from applications.career_connect_grantee_sheets.file_directory import file_directory
import sqlite3
import pandas as pd
from pathlib import Path

def get_last_present_run(conn, participant_id, org, dataset_name):
    return pd.read_sql_query("""
        SELECT vr.run_id, vr.quarter, vr.run_timestamp
        FROM participant_presence_log ppl
        JOIN validation_run vr
          ON ppl.run_id = vr.run_id
        WHERE ppl.participant_id = ?
          AND vr.organization = ?
          AND vr.dataset_name = ?
          AND ppl.status <> 'missing'
        ORDER BY vr.run_timestamp DESC
        LIMIT 1
    """, conn, params=[participant_id, org, dataset_name])

def write_sheet_with_banner(writer, sheet_name, df, title, body, banner_rows=3):
    """
    Writes a banner in rows 0..banner_rows-1, then writes df starting at banner_rows.
    Freezes panes below banner + header row (if df exists).
    Handles empty or None dataframes safely.
    """
    workbook = writer.book

    # Create worksheet explicitly
    worksheet = workbook.add_worksheet(sheet_name)
    writer.sheets[sheet_name] = worksheet

    # ---- Validate dataframe ----
    has_df = (
        df is not None
        and hasattr(df, "columns")
        and len(df.columns) > 0
    )

    if has_df:
        ncols = max(5, len(df.columns))
    else:
        # Fallback banner width if no dataframe columns exist
        ncols = 5  # or choose something like 5 if you prefer wider banners

    # ---- Formats ----
    title_fmt = workbook.add_format({
        "bold": True,
        "font_size": 12,
        "valign": "vcenter",
        "text_wrap": True
    })

    box_fmt = workbook.add_format({
        "bg_color": "#F2F2F2",
        "border": 1,
        "valign": "top",
        "text_wrap": True
    })

    # ---- Banner ----
    worksheet.merge_range(0, 0, 0, ncols - 1, title, title_fmt)
    worksheet.merge_range(1, 0, banner_rows - 1, ncols - 1, body, box_fmt)

    worksheet.set_row(0, 20)
    for r in range(1, banner_rows):
        worksheet.set_row(r, 45)

    # ---- Write dataframe if valid ----
    if has_df:
        df.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            startrow=banner_rows
        )

        # Freeze below banner + header row
        worksheet.freeze_panes(banner_rows + 1, 0)
    else:
        # Optionally write a placeholder message
        worksheet.write(banner_rows, 0, "No data available.")

    return worksheet, banner_rows

def rebuild_submission(run_id: str, output_path: Path, conn):
    
    # Get run metadata
    run_meta = pd.read_sql_query("""
        SELECT dataset_name, organization, quarter
        FROM validation_run
        WHERE run_id = ?
    """, conn, params=[run_id])

    if run_meta.empty:
        raise ValueError(f"Run {run_id} not found.")

    dataset_name = run_meta["dataset_name"].iloc[0]
    org = run_meta["organization"].iloc[0]
    quarter = run_meta["quarter"].iloc[0]

    org = org.replace("_", " ")
    quarter = quarter.replace("_", " ")

    format_type = file_directory[org][dataset_name][quarter]["format"]

    format_def = workbook_definitions[dataset_name][format_type]

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:

        
        # ---------------------------------------------------
        # Build Missing Participants Sheet
        # ---------------------------------------------------

        # Participants present for this sheet/run
        participants = pd.read_sql_query("""
            SELECT DISTINCT participant_id
            FROM participant_presence_log
            WHERE run_id = ?
            AND status <> 'missing'
        """, conn, params=[run_id])

        missing_df = pd.read_sql_query("""
            SELECT participant_id
            FROM participant_presence_log
            WHERE run_id = ?
            AND status = 'missing'
        """, conn, params=[run_id])

        missing_rows = []
        simple_label_dict = workbook_definitions["training data"]["simple format"]["Report"]["labels"]
        canonical_order = list(simple_label_dict.keys())


        if not missing_df.empty:

            for pid in missing_df["participant_id"]:

                last_run = get_last_present_run(conn, pid, org, dataset_name)

                if last_run.empty:
                    continue

                last_run_id = last_run["run_id"].iloc[0]
                last_quarter = last_run["quarter"].iloc[0]

                values = pd.read_sql_query("""
                    SELECT
                        cvh.participant_id,
                        dc.column_name,
                        cvh.value_normalized
                    FROM cell_value_history cvh
                    JOIN dataset_column dc
                    ON cvh.column_id = dc.column_id
                    WHERE cvh.run_id = ?
                    AND cvh.participant_id = ?
                """, conn, params=[last_run_id, pid])

                if values.empty:
                    continue

                row_df = (
                    values.pivot_table(
                        index="participant_id",
                        columns="column_name",
                        values="value_normalized",
                        aggfunc="last"
                    )
                    .reset_index()
                )

                row_df["last_quarter_seen"] = last_quarter

                missing_rows.append(row_df)


        # Always create the tab
        if missing_rows:

            missing_sheet = pd.concat(missing_rows, ignore_index=True)

            missing_sheet = missing_sheet.drop_duplicates(subset=["participant_id"])

            missing_sheet.insert(
                0,
                "Reason_Removed",
                ""
            )

            

            # Ensure canonical order
            existing = [c for c in canonical_order if c in missing_sheet.columns]

            ordered_cols = []

            if "last_quarter_seen" in missing_sheet.columns:
                ordered_cols.append("last_quarter_seen")
                ordered_cols.append("participant_id")

            ordered_cols.extend(existing)

            missing_sheet = missing_sheet.reindex(columns=ordered_cols)

        else:
            missing_sheet = pd.DataFrame({
                "last_quarter_seen": ["—"],
                "Message": ["No missing participants identified"]
            })

        # missing_sheet.to_excel(
        #     writer,
        #     sheet_name="Missing Participants",
        #     index=False
        # )
        # worksheet = writer.sheets["Missing Participants"]

        # for i, col in enumerate(missing_sheet.columns):
        #     column_series = missing_sheet[col].astype(str)
        #     max_len = max(
        #         column_series.map(len).max(),
        #         len(col)
        #     ) + 2  # padding

        #     worksheet.set_column(i, i, max_len)
        mp_title = "Missing Participants"
        mp_body = (
            "This tab lists the most recent complete entry for individuals who were previously present in a prior submission, but are now missing.\n"
            "• 'last_quarter_seen' indicates the most recent quarter they appeared, if you wish to find them in your own records.\n"
            "• Please add these participants back into your next quarterly submission, or provide an explanation for why they were removed in the 'Reason_Removed' column.\n"
        )

        worksheet, startrow = write_sheet_with_banner(
            writer,
            sheet_name="Missing Participants",
            df=missing_sheet,
            title=mp_title,
            body=mp_body,
            banner_rows=3
        )

        # Auto-fit columns (same as before)
        for i, col in enumerate(missing_sheet.columns):
            column_series = missing_sheet[col].astype(str)
            max_len = max(column_series.map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)
        
    # ## regenerate spreadsheets for grantee reference 

    #     # Pull values for this sheet/run
    #     all_values = pd.read_sql_query("""
    #         SELECT
    #             cvh.participant_id,
    #             dc.sheet_name,
    #             dc.column_name,
    #             cvh.value_normalized
    #         FROM cell_value_history cvh
    #         JOIN dataset_column dc
    #         ON cvh.column_id = dc.column_id
    #         WHERE cvh.run_id = ?;
    #     """, conn, params=[run_id])

    #     for sheet_name, sheet_config in format_def.items():
    #         label_dict = sheet_config["labels"]

    #         sheet_values = all_values[all_values["sheet_name"] == sheet_name]

    #         # Pivot
    #         if not sheet_values.empty:
    #             sheet_df = (
    #                 sheet_values.pivot_table(
    #                     index="participant_id",
    #                     columns="column_name",
    #                     values="value_normalized",
    #                     aggfunc="last"
    #                 )
    #                 .reset_index()
    #             )
    #             sheet_df = participants.merge(sheet_df, on="participant_id", how="left")
    #         else:
    #             sheet_df = participants.copy()

    #         # Order columns using label_dict
    #         canonical_order = list(label_dict.keys())
    #         sheet_df = sheet_df.reindex(columns=["participant_id"] + canonical_order)

    #         # Write
    #         sheet_tab = sheet_name[:31]
    #         sheet_df.to_excel(writer, sheet_name=sheet_tab, index=False)

    #         worksheet = writer.sheets[sheet_tab]
    #         for i, col in enumerate(sheet_df.columns):
    #             column_series = sheet_df[col].astype(str)
    #             max_len = max(column_series.map(len).max(), len(col)) + 2
    #             worksheet.set_column(i, i, max_len)

        key_mismatches = pd.read_sql_query("""
            SELECT
                mismatch_id,
                sheet_name,
                id_key,
                issue,
                timestamp
            FROM participant_key_mismatch
            WHERE run_id = ?
            ORDER BY sheet_name, id_key
        """, conn, params=[run_id])

        km_title = "Key Mismatches"
        km_body = (
            "This tab lists keys that are either duplicated or only partially present in the staggered spreadsheet. Participants should appear in only one row and should be present across all four sheets.\n"
            "• Please adjust your existing staggered spreadsheet to resolve these key mismatches, removing duplicates or filling in missing values as needed.\n"
            "• 'missing_in_sheet' - A participant is present in the personal information sheet, but not in the sheet listed.\n"
            "• 'extra_in_sheet' - A participant is absent from the personal information sheet, but is present in the sheet listed.\n"
            "• 'duplicate_in_sheet' - A participant is included twice in the listed sheet.\n"
            "• Please adjust your staggered spreadsheet to resolve these key mismatches before your next submission.\n"
        )

        if key_mismatches.empty:
            mismatch_sheet = pd.DataFrame({
                "Message": ["No key mismatches identified"]
            })
            
            worksheet, _ = write_sheet_with_banner(
                writer, "Key Mismatches", mismatch_sheet, km_title, km_body, banner_rows=4
            )

        if not key_mismatches.empty:

            
            key_mismatches = pd.read_sql_query("""
                SELECT
                    mismatch_id,
                    org,
                    quarter,
                    sheet_name,
                    id_key,
                    issue,
                    timestamp
                FROM participant_key_mismatch
                WHERE run_id = ?
                ORDER BY sheet_name, id_key
            """, conn, params=[run_id])

            if key_mismatches.empty:
                mismatch_sheet = pd.DataFrame({
                    "Message": ["No key mismatches identified"]
                })
            else:
                mismatch_sheet = key_mismatches

            worksheet, _ = write_sheet_with_banner(
                writer, "Key Mismatches", mismatch_sheet, km_title, km_body, banner_rows=4
            )

            # Auto-fit columns (same as before)
            for i, col in enumerate(mismatch_sheet.columns):
                column_series = mismatch_sheet[col].astype(str)
                max_len = max(column_series.map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)


                # ---------------------------------------------------
        
        # VALUE CHANGES (for this run's organization)
        # ---------------------------------------------------
        value_changes = pd.read_sql_query("""
            WITH current_run AS (
                SELECT run_timestamp
                FROM validation_run
                WHERE run_id = ?
            ),

            target_columns AS (
                SELECT
                    column_id,
                    column_name,
                    sheet_name
                FROM dataset_column
                WHERE dataset_name = ?
                  AND sheet_name IN (
                      'Personal Information',
                      'Training',
                      'Credential',
                      'Outcomes',
                      'Report'
                  )
            ),

            ordered_values AS (

                -- Pull first/last name values per participant per run
                WITH name_values AS (
                    SELECT
                        cvh.run_id,
                        cvh.participant_id,
                        MAX(CASE WHEN dc.column_name = 'First Name'
                                THEN cvh.value_normalized END) AS first_name,
                        MAX(CASE WHEN dc.column_name = 'Last Name'
                                THEN cvh.value_normalized END) AS last_name
                    FROM cell_value_history cvh
                    JOIN dataset_column dc
                    ON cvh.column_id = dc.column_id
                    WHERE dc.dataset_name = ?
                    AND dc.column_name IN ('First Name', 'Last Name')
                    GROUP BY cvh.run_id, cvh.participant_id
                )

                SELECT
                    vr.organization AS org,
                    cvh.participant_id,
                    nv.first_name,
                    nv.last_name,
                    tc.sheet_name,
                    tc.column_name,
                    ppl.quarter,
                    cvh.value_normalized AS value_of_interest,

                    LAG(cvh.value_normalized) OVER (
                        PARTITION BY cvh.participant_id, tc.sheet_name, tc.column_name
                        ORDER BY vr.run_timestamp
                    ) AS previous_value,

                    vr.run_timestamp

                FROM cell_value_history cvh
                JOIN target_columns tc
                ON cvh.column_id = tc.column_id
                JOIN validation_run vr
                ON vr.run_id = cvh.run_id
                JOIN participant_presence_log ppl
                ON ppl.run_id = cvh.run_id
                AND ppl.participant_id = cvh.participant_id
                LEFT JOIN name_values nv
                ON nv.run_id = cvh.run_id
                AND nv.participant_id = cvh.participant_id

                WHERE vr.organization = ?
                AND vr.dataset_name = ?
                AND vr.run_timestamp <= (
                        SELECT run_timestamp FROM current_run
                )
            ),
                                          
            latest_values AS (
                SELECT
                    cvh.participant_id,
                    tc.sheet_name,
                    tc.column_name,
                    cvh.value_normalized AS current_value,
                    ROW_NUMBER() OVER (
                        PARTITION BY cvh.participant_id, tc.sheet_name, tc.column_name
                        ORDER BY vr.run_timestamp DESC
                    ) AS rn
                FROM cell_value_history cvh
                JOIN target_columns tc
                ON cvh.column_id = tc.column_id
                JOIN validation_run vr
                ON vr.run_id = cvh.run_id
                WHERE vr.organization = ?
                AND vr.dataset_name = ?
                AND vr.run_timestamp <= (
                        SELECT run_timestamp FROM current_run
                )
            ),

           previous_values_agg AS (
            SELECT
                participant_id,
                sheet_name,
                column_name,
                GROUP_CONCAT(value_normalized, '|') AS previous_values
            FROM (
                SELECT DISTINCT
                    cvh.participant_id,
                    tc.sheet_name,
                    tc.column_name,
                    cvh.value_normalized
                FROM cell_value_history cvh
                JOIN target_columns tc
                    ON cvh.column_id = tc.column_id
                JOIN validation_run vr
                    ON vr.run_id = cvh.run_id
                JOIN current_run cr
                    ON vr.run_timestamp < cr.run_timestamp
                WHERE vr.organization = ?
                AND vr.dataset_name = ?
                AND cvh.value_normalized IS NOT NULL
                AND TRIM(cvh.value_normalized) <> ''
                AND LOWER(TRIM(cvh.value_normalized)) <> 'nan'
            )
            GROUP BY participant_id, sheet_name, column_name
        ),

            cleaned_values AS (
                SELECT *
                FROM ordered_values
                WHERE
                    value_of_interest IS NOT NULL
                    AND TRIM(value_of_interest) <> ''
                    AND LOWER(TRIM(value_of_interest)) <> 'nan'
                    AND previous_value IS NOT NULL
                    AND TRIM(previous_value) <> ''
                    AND LOWER(TRIM(previous_value)) <> 'nan'
            ),

            changes AS (
                SELECT *
                FROM cleaned_values
                WHERE LOWER(value_of_interest) <> LOWER(previous_value)
            ),

            first_change AS (
                SELECT *,
                       ROW_NUMBER() OVER (
                           PARTITION BY participant_id, sheet_name, column_name
                           ORDER BY run_timestamp
                       ) AS change_rank
                FROM changes
            )

            SELECT
                fc.org,
                fc.participant_id,
                fc.first_name,
                fc.last_name,
                fc.sheet_name,
                fc.column_name,
                pva.previous_values,    
                fc.value_of_interest AS new_value,
                lv.current_value,
                fc.quarter AS change_quarter

            FROM first_change fc
            LEFT JOIN latest_values lv
                ON fc.participant_id = lv.participant_id
                AND fc.sheet_name = lv.sheet_name
                AND fc.column_name = lv.column_name
                AND lv.rn = 1
            LEFT JOIN previous_values_agg pva
                ON fc.participant_id = pva.participant_id
                AND fc.sheet_name = pva.sheet_name
                AND fc.column_name = pva.column_name

            WHERE fc.change_rank = 1
            ORDER BY fc.sheet_name, fc.column_name, fc.participant_id;
        """, conn, params=[
                run_id,
                dataset_name,  # for name_values
                dataset_name,  # for target_columns
                org,
                dataset_name,
                org,
                dataset_name,
                org,
                dataset_name
            ])
            
        # if value_changes.empty:
        #         value_changes = pd.DataFrame({
        #             "Message": [f"No value changes detected for {org}."]
        #         })
        # else:
        #     rules = {
        #         "CT Hires Username": "any",
        #         "Training Completed?": "1_to_0",
        #         "Client Date of Birth": "any",
        #         "Date Attained Recognized Credential": "any",
        #         "Date Completed or Withdrew From Training #1": "any",
        #         "Date Entered Training": "any",
        #         "Date of Program Entry (Enrollment Date)": "any",
        #         "Date of Program Exit": "any",
        #         "Zip Code": "any",
        #         "Date Attained Recognized Credential #2": "any",
        #         "Date Attained Recognized Credential #3": "any",
        #         "Date Attained Recognized Credential #4": "any",
        #         "Date Attained Recognized Credential #5": "any",
        #         "Basic Skills Deficient/Low Levels of Literacy?": "any",
        #         "Date Completed, or Withdrew from, Training #2": "any",
        #         "Date Completed, or Withdrew from, Training #3": "any",
        #         "Date Entered Training #2": "any",
        #         "Received Training?": "1_to_0",
        #         "Employment Status at exit": "to_unemployed"
        #     }

        if value_changes.empty:
            value_changes = pd.DataFrame({
                "Message": [f"No value changes detected for {org}."]
            })
        else:

            rules = {
                "CT Hires Username": {"type": "any"},

                "Training Completed?": {"type": "forbidden_value_change",
                                       "initial_value_set":["1", "yes", "true"],
                                       "current_value_set":["0", "no", "false"]},
                "Client Date of Birth": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date Attained Recognized Credential": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date Completed or Withdrew From Training #1": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date Entered Training": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date of Program Entry (Enrollment Date)": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date of Program Exit": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Zip Code": {"type": "any"},

                "Date Attained Recognized Credential #2": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date Attained Recognized Credential #3": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date Attained Recognized Credential #4": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date Attained Recognized Credential #5": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Basic Skills Deficient/Low Levels of Literacy?": {"type": "forbidden_value_change",
                                       "initial_value_set":["1", "yes", "true"],
                                       "current_value_set":["0", "no", "false"]},

                "Date Completed, or Withdrew from, Training #2": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date Completed, or Withdrew from, Training #3": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Date Entered Training #2": {
                    "type": "date_change",
                    "tolerance_days": 30
                },

                "Received Training?": {"type": "forbidden_value_change",
                                       "initial_value_set":["1", "yes", "true"],
                                       "current_value_set":["0", "no", "false"]},

                "Employment Status at exit": {"type": "forbidden_value_change",
                                              "initial_value_set":["employed"],
                                              "current_value_set":["unemployed", "not employed"]}
            }


             # Filter to only relevant columns
            value_changes = value_changes[
                value_changes["column_name"].isin(rules.keys())
            ].copy()   # important to avoid SettingWithCopy issues

            if "new_value" in value_changes.columns:
                value_changes = value_changes.drop(columns=["new_value", "column_name","rule_type"])

            def trim_previous_values(val):
                if pd.isna(val):
                    return val

                parts = [v.strip() for v in str(val).split("|") if v.strip()]

                # Only remove last element if more than one exists
                if len(parts) > 1:
                    return "|".join(parts[:-1])

                # Otherwise keep original single value
                return parts[0] if parts else val

            value_changes["previous_values"] = (
                value_changes["previous_values"]
                .apply(trim_previous_values)
            )

            def is_blank(val):
                if pd.isna(val):
                    return True
                s = str(val).strip().lower()
                return s in {"", "nan", "<na>", "<nat>", "none"}

            def passes_rule(row):
                
                rule_config = rules.get(row["column_name"])
                if not rule_config:
                    return False

                rule_type = rule_config.get("type")
                is_date = rule_config.get("is_date", False)
                tolerance = rule_config.get("tolerance_days", 0)

                prev_raw = str(row.get("previous_values", "")).strip()

                if prev_raw:
                    history_parts = [v.strip() for v in prev_raw.split("|") if v.strip()]
                else:
                    history_parts = []

                # Old value = second-to-last in history
                old = history_parts[-2] if len(history_parts) >= 2 else (history_parts[0] if history_parts else None)

                new = row.get("current_value", None)

                old_blank = is_blank(old)
                new_blank = is_blank(new)

                old = "" if old_blank else str(old).strip()
                new = "" if new_blank else str(new).strip()

                if is_blank(old) and not is_blank(new):
                    return False
                
                if is_blank(old) and is_blank(new):
                    return False

                # ---------------------------
                # Date tolerance logic
                # ---------------------------
                if is_date and old and new:
                    old_dt = pd.to_datetime(old, errors="coerce")
                    new_dt = pd.to_datetime(new, errors="coerce")

                    if pd.notna(old_dt) and pd.notna(new_dt):
                        diff = abs((new_dt - old_dt).days)
                        if diff < tolerance:
                            return False  # ignore small date shifts

                # ---------------------------
                # Rule logic
                # ---------------------------
                if rule_type == "any":
                    return True

                if rule_type == "date_change":

                    tolerance = rule_config.get("tolerance_days", 0)

                    old_dt = pd.to_datetime(old, errors="coerce")
                    new_dt = pd.to_datetime(new, errors="coerce")

                    if pd.notna(old_dt) and pd.notna(new_dt):
                        diff = abs((new_dt - old_dt).days)
                        if diff < tolerance:
                            return False  # ignore small date shifts

                if rule_type == "forbidden_value_change":

                    initial_value_set = rule_config.get("initial_value", None)
                    current_value_set = rule_config.get("subsequent_value", None)

                    current = str(row.get("current_value", "")).strip().lower()

                    history_values = {v.lower() for v in history_parts}

                    in_current_value_set = current in current_value_set
                    historic_values_in_initial_value_set = bool(history_values & initial_value_set)

                    return in_current_value_set and historic_values_in_initial_value_set

                return False


            # Apply filter WITHOUT dropping any columns
            mask = value_changes.apply(passes_rule, axis=1)
            value_changes = value_changes[mask]

        # value_changes.to_excel(
        #     writer,
        #     sheet_name="Value Changes",
        #     index=False
        # )

        # worksheet = writer.sheets["Value Changes"]

        # for i, col in enumerate(value_changes.columns):
        #     column_series = value_changes[col].astype(str)
        #     max_len = max(
        #         column_series.map(len).max(),
        #         len(col)
        #     ) + 2
        #     worksheet.set_column(i, i, max_len)
        mp_title = "Changed Values"
        mp_body = (
            "This tab lists column values that have changed which we expected to remain constant.\n"
            "• Please provide a reason that the value changed in the 'Reason_Changed' column, or revert to the previous value in your next submission.\n"
        )

        worksheet, startrow = write_sheet_with_banner(
            writer,
            sheet_name="Changed Values",
            df=value_changes,
            title=mp_title,
            body=mp_body,
            banner_rows=3
        )

        # Auto-fit columns (same as before)
        for i, col in enumerate(value_changes.columns):
            column_series = value_changes[col].astype(str)
            max_len = max(column_series.map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)

        
        CC_ALLOWED_RULES = [
            "Confirmation required, unusually high (> $45.00)",
            "Formatting Issue, identifier rejected",

            "If ('Date of Program Exit' (sheet 'Training') is  filled) and ('Date Entered Training #2' (sheet 'Training') is  filled), then 'Date Completed, or Withdrew from, Training #2' (sheet 'Training') must  be filled",
            "If ('Date of Program Exit' (sheet 'Training') is  filled) and ('Date Entered Training #3' (sheet 'Training') is  filled), then 'Date Completed, or Withdrew from, Training #3' (sheet 'Training') must  be filled",
            "If ('Date of Program Exit' (sheet 'Training') is  filled) and ('Date Entered Training' (sheet 'Training') is  filled), then 'Date Completed or Withdrew From Training #1' (sheet 'Training') must  be filled",

            "If 'Date Completed or Withdrew From Training #1' (sheet 'Training') is  filled, then 'Received Training?' (sheet 'Training') must  equal '1'",
            "If 'Date Entered Training' (sheet 'Training') is  filled, then 'Received Training?' (sheet 'Training') must  equal '1'",

            "If 'Date of Program Exit' (sheet 'Training') is  before 'the date 2025-09-30', then 'Employment Status at exit' (sheet 'Outcomes') must  be filled",
            "If 'Date of Program Exit' (sheet 'Training') is  before 'the date 2025-09-30', then 'School Status at Exit' (sheet 'Outcomes') must  be filled",
            "If 'Date of Program Exit' (sheet 'Training') is  filled, then 'Date of Program Entry (Enrollment Date)' (sheet 'Training') must  be filled",

            "If 'If employed, did participant report hourly salary?' (sheet 'Employment') is  equal to '1', then 'Hourly Earnings' (sheet 'Employment') must  be filled",

            "If 'Occupational Skills Training Code #1' (sheet 'Training') is  filled, then 'Received Training?' (sheet 'Training') must  equal '1'",

            "If 'Received Training?' (sheet 'Training') is *not* equal '1', then 'CareerConneCT Training Provider' (sheet 'Training') must  be blank",
            "If 'Received Training?' (sheet 'Training') is *not* equal '1', then 'CareerConneCT Training Provider CIP Code' (sheet 'Training') must  be blank",
            "If 'Received Training?' (sheet 'Training') is *not* equal '1', then 'CareerConneCT Training Provider Program of Study' (sheet 'Training') must  be blank",
            "If 'Received Training?' (sheet 'Training') is *not* equal '1', then 'Date Completed or Withdrew From Training #1' (sheet 'Training') must  be blank",
            "If 'Received Training?' (sheet 'Training') is *not* equal '1', then 'Date Entered Training' (sheet 'Training') must  be blank",
            "If 'Received Training?' (sheet 'Training') is *not* equal '1', then 'Occupational Skills Training Code #1' (sheet 'Training') must  be blank",
            "If 'Received Training?' (sheet 'Training') is *not* equal '1', then 'Type of Training Service' (sheet 'Training') must  be blank",

            "If 'Type of Training Service' (sheet 'Training') is  filled, then 'Received Training?' (sheet 'Training') must  equal '1'",

            "Invalid Value, cannot exceed 80 hours",
            "Invalid Value, date after maximum allowed",
            "Invalid Value, date before minimum allowed",
            "Invalid Value, must be >= $5.00",
            "Invalid Value, must be Yes/No",
            "Invalid Value, must match NAICS format (e.g. '31', '311', '31151', '311513')",
            "Invalid Value, must match ONET format (e.g. '15-2051.00')",
            "Invalid Value, not a valid date",
            "Invalid Value, not in accepted responses",
            "Invalid Value, State ID must be 7 Digits (e.g. '0123456')",
            "Invalid Value, zipcode must 5 digits (e.g. 06543) or 4 digits (6434)",

            "'Occupational Skills Training Code #2' (sheet 'Training') must  match the blank/non-blank status of ''Date Entered Training #2' (sheet 'Training')'",
            "'Occupational Skills Training Code #3' (sheet 'Training') must  match the blank/non-blank status of ''Date Entered Training #3' (sheet 'Training')'",

            "Required but missing"
        ]

        placeholders = ",".join(["?"] * len(CC_ALLOWED_RULES))

        errors = pd.read_sql_query(f"""
            SELECT
                vv.violation_id,
                vr.organization,
                vr.quarter,
                vv.participant_id,
                p.person_id,
                per.first_name,
                per.last_name,
                dc.sheet_name,
                dc.column_name,
                vrule.rule_type,
                vv.rule_id,
                vv.raw_value,
                vv.normalized,
                vv.severity,
                vv.timestamp
            FROM validation_violation vv
            JOIN validation_run vr
                ON vv.run_id = vr.run_id
            LEFT JOIN dataset_column dc
                ON vv.column_id = dc.column_id
            LEFT JOIN validation_rule vrule
                ON vv.rule_id = vrule.rule_id
            LEFT JOIN participant p
                ON vv.participant_id = p.participant_id
            LEFT JOIN person per
                ON p.person_id = per.person_id
            WHERE vv.run_id = ?
                AND vv.rule_id IN ({placeholders})
            ORDER BY dc.sheet_name, dc.column_name, vv.participant_id
        """, conn, params=[run_id] + CC_ALLOWED_RULES)

        # ---------------------------------------
        # Split into Cross Errors and Normalization Errors
        # ---------------------------------------

        import json
        import re

        def rebuild_with_raw_values(row, conn, run_id):
            try:
                norm_dict = json.loads(row["normalized"])
            except Exception:
                return row["normalized"]  # fallback if malformed

            participant_id = row["participant_id"]
            rebuilt = {}

            for key in norm_dict.keys():

                # Extract sheet and column from key
                # Format: (Sheet)Outcomes::(Column)Employment Status at exit
                sheet_match = re.search(r"\(Sheet\)(.*?)::", key)
                col_match = re.search(r"\(Column\)(.*)", key)

                if not sheet_match or not col_match:
                    rebuilt[key] = norm_dict[key]
                    continue

                if org in ["CWP CDL","CWP IT","Marrakech"]:

                    sheet_name = 'Report'    

                else:

                    sheet_name = sheet_match.group(1)
                
                column_name = col_match.group(1)

                # Pull raw value from DB
                raw = pd.read_sql_query(
                    """
                    SELECT cvh.value_raw
                    FROM cell_value_history cvh
                    JOIN dataset_column dc
                        ON cvh.column_id = dc.column_id
                    WHERE cvh.run_id = ?
                    AND cvh.participant_id = ?
                    AND dc.sheet_name = ?
                    AND dc.column_name = ?
                    ORDER BY cvh.timestamp DESC
                    LIMIT 1
                    """,
                    conn,
                    params=[run_id, participant_id, sheet_name, column_name]
                )

                if not raw.empty:
                    rebuilt[key] = raw.iloc[0]["value_raw"]
                else:
                    rebuilt[key] = None

            return json.dumps(rebuilt)

        if not errors.empty:

            cross_errors = errors[
                errors["raw_value"].astype(str).str.strip() == "Not Applicable."
            ].copy()

            cross_errors["raw_output"] = cross_errors.apply(
                lambda row: rebuild_with_raw_values(row, conn, run_id),
                axis=1
            )

            cross_errors.drop(columns=["normalized","severity","timestamp","raw_value","participant_id","person_id","violation_id"], inplace=True)

            normalization_errors = errors[
                errors["raw_value"].astype(str).str.strip() != "Not Applicable."
            ].copy()

            normalization_errors.drop(columns=["violation_id","participant_id","person_id", "rule_type","severity","timestamp"], inplace=True   )

        else:
            cross_errors = pd.DataFrame({
                "Message": ["No cross errors identified for this run."]
            })

            normalization_errors = pd.DataFrame({
                "Message": ["No normalization errors identified for this run."]
            })

        # ---------------------------------------
        # Write Cross Errors Sheet
        # ---------------------------------------

        ce_title = "Cross Errors"
        ce_body = (
            "Cross-field consistency checks.\n"
            "• These are usually logic/rule violations across multiple fields.\n"
            "• Fix in the source workbook and re-submit."
        )

        worksheet, _ = write_sheet_with_banner(
            writer, "Cross Errors", cross_errors, ce_title, ce_body, banner_rows=3
        )

        for i, col in enumerate(cross_errors.columns):
            column_series = cross_errors[col].astype(str)
            max_len = max(
                column_series.map(len).max(),
                len(col)
            ) + 2
            worksheet.set_column(i, i, max_len)


        # ---------------------------------------
        # Write Normalization Errors Sheet
        # ---------------------------------------

        ne_title = "Normalization Errors"
        ne_body = (
            "Field-level formatting/value errors.\n"
            "• Examples: invalid dates, invalid codes, missing required values.\n"
            "• Fix in the source workbook and re-submit."
        )

        worksheet, _ = write_sheet_with_banner(
            writer, "Normalization Errors", normalization_errors, ne_title, ne_body, banner_rows=3
        )

        for i, col in enumerate(normalization_errors.columns):
            column_series = normalization_errors[col].astype(str)
            max_len = max(
                column_series.map(len).max(),
                len(col)
            ) + 2
            worksheet.set_column(i, i, max_len)


# DB_PATH = Path("validation_dev.db")

# org = "CWP_CDL"
# dataset_name = "training data"
# quarter = "PY4_Q2"

# conn = sqlite3.connect(DB_PATH)
# conn.execute("PRAGMA foreign_keys = ON;")

# runs = pd.read_sql_query("""
#     SELECT run_id, run_timestamp
#     FROM validation_run
#     WHERE organization = ?
#       AND dataset_name = ?
#       AND quarter = ?
#     ORDER BY run_timestamp DESC
# """, conn, params=[org, dataset_name, quarter])

# if runs.empty:
#     raise ValueError("No runs found.")

# run_id = runs.iloc[0]["run_id"]

# rebuild_submission(
#     run_id=run_id,
#     output_path=Path(rf"C:\Users\webbm\OneDrive - State of Connecticut\Documents\{org}_{quarter}_rebuilt.xlsx"),
#     conn=conn
# )

# conn.close()

from pathlib import Path
import sqlite3
import pandas as pd
from config import DB_PATH, OUTPUT_DIRECTORY

dataset_name = "training data"
quarter = "PY4_Q2"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")

# -------------------------------------------------
# 1. Get all distinct orgs for this dataset + quarter
# -------------------------------------------------
orgs = pd.read_sql_query("""
    SELECT DISTINCT organization
    FROM validation_run
    WHERE dataset_name = ?
      AND quarter = ?
""", conn, params=[dataset_name, quarter])

if orgs.empty:
    raise ValueError("No organizations found for this dataset/quarter.")

# -------------------------------------------------
# 2. Loop through orgs
# -------------------------------------------------
for org in orgs["organization"]:

    runs = pd.read_sql_query("""
        SELECT run_id, run_timestamp
        FROM validation_run
        WHERE organization = ?
          AND dataset_name = ?
          AND quarter = ?
        ORDER BY run_timestamp DESC
    """, conn, params=[org, dataset_name, quarter])

    if runs.empty:
        print(f"No runs found for {org}. Skipping.")
        continue

    run_id = runs.iloc[0]["run_id"]

    print(f"Rebuilding {org} ({quarter}) using run_id {run_id}")

    output_path = Path(
         OUTPUT_DIRECTORY / f"{org}_{quarter}_rebuilt_2.xlsx"
    )

    rebuild_submission(
        run_id=run_id,
        output_path=output_path,
        conn=conn
    )

conn.close()