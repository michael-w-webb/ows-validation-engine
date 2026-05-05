import sqlite3
import pandas as pd
from pathlib import Path
from config import DB_PATH, OUTPUT_DIRECTORY


#### CONFIG #### 
# Daly added hard-coded path on 4/23 b/c PATH was not working with sqlite3.connect. TODO: Investigate why. This should be fixed and should not need the ""'s now. The issue was that the .env file had "" around the file path and that's not needed.
# DB_PATH = "C:/Users/DalyRob/OneDrive - State of Connecticut/Documents/GitHub Repos/ows-validation-engine/database/validation_dev.db"

config_key = "CC"
#config_key = "GJC"


quarter = "PY4_Q3"

if config_key == "GJC":

    from applications.good_jobs_challenge_grantee_sheets.workbook_definitions import workbook_definitions

    dataset_name = "TPI"

    value_change_rules = {
                    "CTHires Username or State ID #": {"type": "any"},
                    "City": {"type": "any"},
                    "Zip Code": {"type": "any"},
                    "Date of Birth": {"type": "date_change", "tolerance_days": 30},
                    "Training Start Date": {"type": "date_change", "tolerance_days": 30},
                    "Training End Date": {"type": "date_change", "tolerance_days": 30},
                    "Job Start Date": {"type": "date_change", "tolerance_days": 30},
                    "Employment Status": {"type": "forbidden_value_change",
                                        "initial_value_set":["employed in-field by an employer who doesn't partner with your training program",
                        "employed in-field by an employer who partners with your training program",
                        "employed out of field"],
                                        "current_value_set":["still seeking employment", "in job search assistance","not seeking employment in-field","could not contact","","<na>","nan",None]},
                    "Training Completion Status": {"type": "forbidden_value_change",
                                                "initial_value_set":["completed training on time","yes but not continuous"],
                                        "current_value_set":["did not complete training (please code exit reason)","","<na>","nan",None]},
                        }
    
    reported_error_rule_set = [

            "Confirmation required, unusually high (> $45.00)",
            "Formatting Issue, identifier rejected",

            "If 'Employment Status' (sheet 'Employment') is  one of ''an employment status indicating the participant is employed'', then 'Employer' (sheet 'Employment') must  be filled",
            "If 'Employment Status' (sheet 'Employment') is  one of ''an employment status indicating the participant is employed'', then 'Employer Zip Code' (sheet 'Employment') must  be filled",
            "If 'Employment Status' (sheet 'Employment') is  one of ''an employment status indicating the participant is employed'', then 'If employed, did participant report hourly salary?' (sheet 'Employment') must  be filled",
            "If 'Employment Status' (sheet 'Employment') is  one of ''an employment status indicating the participant is employed'', then 'Job Start Date' (sheet 'Employment') must  be filled",
            "If 'Employment Status' (sheet 'Employment') is  one of ''an employment status indicating the participant is employed'', then 'Occupation (NAICS) code' (sheet 'Employment') must  be filled",
            "If 'Employment Status' (sheet 'Employment') is  one of ''an employment status indicating the participant is employed'', then 'Employment Type' (sheet 'Employment') must  be filled",
            
            "If 'If employed, did participant report hourly salary?' (sheet 'Employment') is  equal to '1', then 'Hourly Earnings' (sheet 'Employment') must  be filled",

            "If 'Training Completion Status' (sheet 'Program_Enrollment') is  equal to ''Did not complete training (please code exit reason)'', then 'Non-Completion Exit Reason' (sheet 'Program_Enrollment') must  be filled",
            "If 'Training End Date' (sheet 'Program_Enrollment') is  before 'the date 2025-12-31', then 'Employment Status' (sheet 'Employment') must  be filled",
            "If 'Training End Date' (sheet 'Program_Enrollment') is  before 'the date 2025-12-31', then 'School Status at Exit' (sheet 'Employment') must  be filled",
            "If 'Training End Date' (sheet 'Program_Enrollment') is  before 'the date 2025-12-31', then 'Training Completion Status' (sheet 'Program_Enrollment') must  be filled"

            "Invalid Value, must be a number indicating typical weekly hours (ideal format: '25')",
            "Invalid Value, not a valid date",
            "Invalid Value, not in accepted responses",
            "Invalid Value, zipcode must 5 digits (e.g. 06543) or 4 digits (6434)",
            "Required but missing"

        ]
    
    sheet_order = [
            "Participant_Info",
            "Program_Enrollment",
            "Credential_Attainment",
            "Employment"
        ]

    all_keys = []

    for sheet_name in sheet_order:
        label_dict = workbook_definitions["TPI"]["standard"][sheet_name]["labels"]
        all_keys.extend(label_dict.keys())


    canonical_order = list(dict.fromkeys(all_keys))

    sheetname_placeholders = ",".join(["?"] * len(sheet_order))
    
if config_key == "CC":

    from applications.career_connect_grantee_sheets.workbook_definitions import workbook_definitions

    dataset_name = "training data"

    value_change_rules = {
                "CT Hires Username": {"type": "any"},
                "Training Completed?": {"type": "forbidden_value_change", 
                                        "initial_value_set":["1", "yes", "true"], 
                                        "current_value_set":["0", "no", "false","<na>","nan",None]},
                "Client Date of Birth": {"type": "date_change","tolerance_days": 30},
                "Date Attained Recognized Credential": {"type": "date_change","tolerance_days": 30},
                "Date Completed or Withdrew From Training #1": {"type": "date_change","tolerance_days": 30},
                "Date Entered Training": {"type": "date_change","tolerance_days": 30},
                "Date of Program Entry (Enrollment Date)": {"type": "date_change","tolerance_days": 30},
                "Date of Program Exit": {"type": "date_change","tolerance_days": 30},
                "Zip Code": {"type": "any"},
                "Date Attained Recognized Credential #2": {"type": "date_change","tolerance_days": 30},
                "Date Attained Recognized Credential #3": {"type": "date_change","tolerance_days": 30},
                "Date Attained Recognized Credential #4": {"type": "date_change","tolerance_days": 30},
                "Date Attained Recognized Credential #5": {"type": "date_change","tolerance_days": 30},
                "Date Completed, or Withdrew from, Training #2": {"type": "date_change","tolerance_days": 30},
                "Date Completed, or Withdrew from, Training #3": {"type": "date_change","tolerance_days": 30},
                "Date Entered Training #2": {"type": "date_change","tolerance_days": 30},
                "Received Training?": {"type": "forbidden_value_change",
                                       "initial_value_set":["1", "yes", "true"],
                                       "current_value_set":["0", "no", "false","","<na>","nan",None]},
                "Employment Status at exit": {"type": "forbidden_value_change",
                                    "initial_value_set": [
                                        "employed; part-time",
                                        "employed; full-time",
                                        "temporarily employed",
                                        "internship",
                                        "apprenticeship"
                                    ],
                                    "current_value_set": [
                                        "unemployed",
                                        "",
                                        "<na>",
                                        "nan",
                                        None
                                    ]
}
            }
    
    reported_error_rule_set = [
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
    
    simple_label_dict = workbook_definitions["training data"]["simple format"]["Report"]["labels"]
    canonical_order = list(simple_label_dict.keys())
    canonical_order.append("source_file")

    sheet_order = [ "Personal Information",
                      "Training",
                      "Credential",
                      "Outcomes",
                      "Report"]

    sheetname_placeholders = ",".join(["?"] * len(sheet_order))


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
        ncols = max(7, len(df.columns))
    else:
        # Fallback banner width if no dataframe columns exist
        ncols = 7  # or choose something like 5 if you prefer wider banners

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

    quarter = quarter.replace("_", " ")

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
                row_df["removed_intentionally"] = ""
                row_df["associated_first_name"] = ""
                row_df["associated_last_name"] = ""
                row_df["personal_info_reconciled"] = ""

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
                ordered_cols.append("removed_intentionally")
                ordered_cols.append("personal_info_reconciled")
                ordered_cols.append("associated_first_name")
                ordered_cols.append("associated_last_name")
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

            mismatch_sheet = key_mismatches

            name_parts = mismatch_sheet["id_key"].str.split("|", expand=True)

            mismatch_names = set(
                zip(name_parts[0].str.strip(), name_parts[1].str.strip())
            )

            # Remove matching rows from missing_sheet
            missing_sheet = missing_sheet[
                ~missing_sheet.apply(
                    lambda r: (r["First Name"].strip(), r["Last Name"].strip()) in mismatch_names,
                    axis=1
                )
            ]

        ### write missing participants to file after key matches have been found 

        mp_title = "Missing Participants"
        mp_body = (
            "This tab lists the most recent complete entry for individuals who were previously present in a prior submission, but are now missing.\n"
            "• 'last_quarter_seen' indicates the most recent quarter they appeared, if you wish to find them in your own records.\n"
            "• if a participant on this list is in your quarterly report with a slightly different name, add that name in the 'associated_first_name' and 'associated_last_name' columns.\n"
            "• if a participant on this list is unintentionally absent from your quarterly report, please add them back in with your next submission.\n"
            "• if you removed a particpant on this list intentionally, please put a 1 in the 'removed_intentionally' column\n"
            "• if a person on this list does appear in your quarterly report with an exact name spelling match, then their birth date and/or zip code has changed, please reconcile their personal information and esnure that the correct values are in your next quarterly submission and place a 1 in the 'personal_info_reconciled' column"
        )

        if "source_file" in missing_sheet.columns:
            if missing_sheet["source_file"].fillna("").str.strip().eq("").all():
                missing_sheet.drop(columns=["source_file"], inplace=True)


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
            max_len = max(
                column_series.map(len).max(),
                len(col)
            ) + 2
            worksheet.set_column(i, i, max_len)
        
        km_title = "Key Mismatches"
        km_body = (
            "This tab lists keys that are either duplicated or only partially present in the staggered spreadsheet. Participants should appear in only one row and should be present across all four sheets.\n"
            "• Please adjust your existing quarterly report to resolve these key mismatches, removing duplicates or filling in missing values as needed.\n"
            "• 'missing_in_sheet' - A participant is present in the personal information sheet, but not in the sheet listed.\n"
            "• 'extra_in_sheet' - A participant is absent from the personal information sheet, but is present in the sheet listed.\n"
            "• 'duplicate_in_sheet' - A participant is included twice in the listed sheet.\n"
            "• Please adjust your quarterly report to resolve these key mismatches before your next submission.\n"
        )

        if key_mismatches.empty:

            mismatch_sheet = pd.DataFrame({
                "Message": ["No key mismatches identified"]
            })
            
            worksheet, _ = write_sheet_with_banner(
                writer, "Key Mismatches", mismatch_sheet, km_title, km_body, banner_rows=4
            )

            for i, col in enumerate(mismatch_sheet.columns):
                column_series = mismatch_sheet[col].astype(str)
                max_len = max(
                    column_series.map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)



        if not key_mismatches.empty:

            worksheet, _ = write_sheet_with_banner(
                    writer, "Key Mismatches", mismatch_sheet, km_title, km_body, banner_rows=4
                )

            # Auto-fit columns (same as before)
            for i, col in enumerate(mismatch_sheet.columns):
                column_series = mismatch_sheet[col].astype(str)
                max_len = max(
                    column_series.map(len).max(),
                    len(col)
                ) + 2
                worksheet.set_column(i, i, max_len)

        # ---------------------------------------------------
        # VALUE CHANGES (NEW APPROACH - RUN_ID SCOPED)
        # ---------------------------------------------------

# --- Get run metadata ---
        run_meta = pd.read_sql_query("""
            SELECT organization, dataset_name, run_timestamp
            FROM validation_run
            WHERE run_id = ?
        """, conn, params=[run_id])

        if run_meta.empty:
            value_changes = pd.DataFrame({"Message": ["Run not found."]})
        else:
            org = run_meta.loc[0, "organization"]
            dataset_name = run_meta.loc[0, "dataset_name"]
            run_ts = run_meta.loc[0, "run_timestamp"]

            # --- Get all completed runs up to this run for this org ---
            run_lookup = pd.read_sql_query("""
                SELECT run_id, quarter, run_timestamp
                FROM validation_run
                WHERE organization = ?
                AND dataset_name = ?
                AND completed = 1
                ORDER BY run_timestamp
            """, conn, params=[org, dataset_name])

            if run_lookup.empty or len(run_lookup) < 2:
                value_changes = pd.DataFrame({
                    "Message": [f"No prior runs available for comparison for {org}."]
                })
            else:

                # keep latest run per quarter
                latest_runs = (
                    run_lookup
                    .sort_values("run_timestamp")
                    .drop_duplicates("quarter", keep="last")
                    .sort_values("quarter")
                    .reset_index(drop=True)
                )

                # --- helper to get diffs ---
                def get_value_changes(conn, curr_id, prev_id):
                    return pd.read_sql_query("""
                        WITH current_run AS (
                            SELECT participant_id, column_id,
                                CASE
                                    WHEN value_normalized IS NULL THEN NULL
                                    WHEN LOWER(TRIM(value_normalized)) IN ('', 'nan', '<na>', '<nat>', 'none') THEN NULL
                                    ELSE TRIM(value_normalized)
                                END AS val
                            FROM cell_value_history
                            WHERE run_id = :curr_id
                        ),
                        previous_run AS (
                            SELECT participant_id, column_id,
                                CASE
                                    WHEN value_normalized IS NULL THEN NULL
                                    WHEN LOWER(TRIM(value_normalized)) IN ('', 'nan', '<na>', '<nat>', 'none') THEN NULL
                                    ELSE TRIM(value_normalized)
                                END AS val
                            FROM cell_value_history
                            WHERE run_id = :prev_id
                        )
                        SELECT 
                            COALESCE(c.participant_id, p.participant_id) AS participant_id,
                            COALESCE(c.column_id, p.column_id) AS column_id,
                            dc.column_name,
                            p.val AS old_value,
                            c.val AS new_value
                        FROM current_run c
                        FULL OUTER JOIN previous_run p 
                            ON c.participant_id = p.participant_id 
                        AND c.column_id = p.column_id
                        LEFT JOIN dataset_column dc
                            ON dc.column_id = COALESCE(c.column_id, p.column_id)
                        WHERE c.val IS NOT p.val;
                    """, conn, params={"curr_id": curr_id, "prev_id": prev_id})

                # --- collect all changes ---
                all_dfs = []

                for i in range(1, len(latest_runs)):
                    prev_row = latest_runs.iloc[i - 1]
                    curr_row = latest_runs.iloc[i]

                    df = get_value_changes(conn, curr_row["run_id"], prev_row["run_id"])

                    if df.empty:
                        continue

                    df["organization"] = org
                    df["from_quarter"] = prev_row["quarter"]
                    df["to_quarter"] = curr_row["quarter"]

                    all_dfs.append(df)

                final_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

                if final_df.empty:
                    value_changes = pd.DataFrame({
                        "Message": [f"No value changes detected for {org}."]
                    })
                else:

                    # --- quarter ordering ---
                    def quarter_key(q):
                        py, qtr = q.split("_")
                        return int(py.replace("PY", "")) * 10 + int(qtr.replace("Q", ""))

                    final_df["quarter_order"] = final_df["to_quarter"].apply(quarter_key)

                    # --- latest change per field ---
                    latest_changes = (
                        final_df
                        .sort_values("quarter_order")
                        .drop_duplicates(
                            subset=["organization", "participant_id", "column_id"],
                            keep="last"
                        )
                    )

                    # --- rule evaluation ---
                    def clean(v):
                        if pd.isna(v):
                            return None
                        v = str(v).strip().lower()
                        if v in ["", "nan", "<na>", "<nat>", "none"]:
                            return None
                        return v

                    def evaluate_change(row):
                        col = row["column_name"]
                        if col not in value_change_rules:
                            return False

                        rule = value_change_rules[col]
                        old = clean(row["old_value"])
                        new = clean(row["new_value"])

                        if rule["type"] == "any":
                            return old != new

                        if rule["type"] == "date_change":
                            if old is None or new is None:
                                return False
                            try:
                                diff = abs((pd.to_datetime(new) - pd.to_datetime(old)).days)
                                return diff > rule["tolerance_days"]
                            except:
                                return False

                        if rule["type"] == "forbidden_value_change":
                            return (
                                old in [clean(v) for v in rule["initial_value_set"]]
                                and new in [clean(v) for v in rule["current_value_set"]]
                            )

                        return False

                    latest_changes["flagged"] = latest_changes.apply(evaluate_change, axis=1)
                    flagged_df = latest_changes[latest_changes["flagged"]].copy()

                    if flagged_df.empty:
                        value_changes = pd.DataFrame({
                            "Message": [f"No rule-breaking value changes for {org}."]
                        })
                    else:

                        # --- filter full history to flagged keys ---
                        flagged_keys = flagged_df[
                            ["organization", "participant_id", "column_id"]
                        ].drop_duplicates()

                        filtered_final_df = final_df.merge(
                            flagged_keys,
                            on=["organization", "participant_id", "column_id"],
                            how="inner"
                        ).sort_values(
                            ["organization", "participant_id", "column_id", "quarter_order"]
                        )

                        filtered_final_df["new_value_clean"] = filtered_final_df["new_value"].map(clean)

                        # --- build full history ---
                        def build_history(group):
                            history = []
                            first_old = clean(group.iloc[0]["old_value"])
                            history.append(first_old)
                            history.extend(group["new_value_clean"].tolist())
                            return history

                        history_df = (
                            filtered_final_df
                            .groupby(["organization", "participant_id", "column_id"])
                            .apply(build_history)
                            .reset_index(name="value_history")
                        )

                        # --- merge history ---
                        value_changes = filtered_final_df.merge(
                            history_df,
                            on=["organization", "participant_id", "column_id"],
                            how="left"
                        )

                        # --- format for report ---
                        value_changes["current_value"] = value_changes["new_value"]

                        value_changes["previous_values"] = value_changes["value_history"].apply(
                            lambda x: "|".join(
                                [str(v) for v in x[:-1]]
                            ) if isinstance(x, list) else ""
                        )

                        # cleanup
                        value_changes = value_changes.drop(
                            columns=["new_value", "old_value", "value_history", "column_id"],
                            errors="ignore"
                        )

                        value_changes["list_length"] = value_changes["previous_values"].apply(lambda x: len(x.split("|")) if x else 0)

                        cond_length = value_changes['list_length'] == 1
                        cond_none = value_changes['previous_values'].astype(str).str.split('|').str[0] == None

                        mask = ~(cond_length & cond_none)

                        filtered_value_changes = value_changes[mask]

        mp_title = "Changed Values"
        mp_body = (
            "This tab lists column values that have changed which we expected to remain constant.\n"
            "• Inspect each 'current_value' and either confirm that it is correct and place a '1' in the 'confirmed_correct' column, or change to the correct value and then place a '1' in the 'confirmed_correct' column.\n" 
            "• The previous values column provides a '|' delimited list of all prior non-blank values for that cell, with the most recent values listed last. In many cases there will only be one historical value, but in some cases there may be multiple if the value has changed multiple times across submissions.\n"
        )

        if filtered_value_changes.empty:
            filtered_value_changes = pd.DataFrame(columns=["organization", "participant_id", "current_value", "previous_values"])
            worksheet, startrow = write_sheet_with_banner(
            writer,
            sheet_name="Changed Values",
            df=filtered_value_changes,
            title=mp_title,
            body=mp_body,
            banner_rows=3
        )
            
        else:
            filtered_value_changes.insert(0, "confirmed_correct", "")

            if "source_file" in filtered_value_changes.columns:
                if filtered_value_changes["source_file"].fillna("").str.strip().eq("").all():
                    filtered_value_changes.drop(columns=["source_file"], inplace=True)

            filtered_value_changes.drop(columns=["list_length"], inplace=True)

            worksheet, startrow = write_sheet_with_banner(
                writer,
                sheet_name="Changed Values",
                df=filtered_value_changes,
                title=mp_title,
                body=mp_body,
                banner_rows=3
            )

        # Auto-fit columns (same as before)
        for i, col in enumerate(filtered_value_changes.columns):
            column_series = filtered_value_changes[col].astype(str)
            max_len = max(
                column_series.map(len).max(),
                len(col)
            ) + 2
            worksheet.set_column(i, i, max_len)

        placeholders = ",".join(["?"] * len(reported_error_rule_set))

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
    vv.timestamp,
    sf.source_file
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
LEFT JOIN (
    SELECT
        cvh.participant_id,
        cvh.run_id,
        MAX(cvh.value_normalized) AS source_file
    FROM cell_value_history cvh
    JOIN dataset_column dc
        ON cvh.column_id = dc.column_id
    WHERE dc.column_name = 'source_file'
    GROUP BY cvh.participant_id, cvh.run_id
) sf
    ON sf.participant_id = vv.participant_id
   AND sf.run_id = vv.run_id
WHERE vv.run_id = ?
  AND vv.rule_id IN ({placeholders})
ORDER BY dc.sheet_name, dc.column_name, vv.participant_id
        """, conn, params=[run_id] + reported_error_rule_set)

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
                    AND dc.column_name = ?
                    ORDER BY cvh.timestamp DESC
                    LIMIT 1
                    """,
                    conn,
                    params=[run_id, participant_id, column_name]
                )

                if not raw.empty:
                    rebuilt[key] = raw.iloc[0]["value_raw"]
                else:
                    rebuilt[key] = None

            return json.dumps(rebuilt)

        if not errors.empty:

            errors = errors[
                errors["first_name"].notna() &
                errors["last_name"].notna() &
                (errors["first_name"].str.strip() != "") &
                (errors["last_name"].str.strip() != "")
            ]

            cross_errors = errors[
                errors["raw_value"].astype(str).str.strip() == "Not Applicable."
            ].copy()

            if not cross_errors.empty:

                cross_errors["raw_output"] = cross_errors.apply(
                    lambda row: rebuild_with_raw_values(row, conn, run_id),
                    axis=1
                )

                cross_errors.drop(columns=["normalized","severity","timestamp","raw_value","participant_id","person_id","violation_id"], inplace=True)

                # Ensure source_file is last
                cols = [c for c in cross_errors.columns if c != "source_file"] + ["source_file"]
                cross_errors = cross_errors[cols]

            else:

                cross_errors = pd.DataFrame({
                    "Message": ["No cross errors identified for this run."]
                })

            normalization_errors = errors[
                errors["raw_value"].astype(str).str.strip() != "Not Applicable."
            ].copy()

            if not normalization_errors.empty:

                normalization_errors.drop(columns=["violation_id","participant_id","person_id", "rule_type","severity","timestamp"], inplace=True   )

            else: 

                normalization_errors = pd.DataFrame({
                    "Message": ["No normalization errors identified for this run."]
                })

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
            "• The 'rule_id' column explains the issue and the 'raw_output' column shows the original values that triggered the error.\n"
            "• Please address all of the identified issues in your next submission, or contact us to explain why specific issues cannot be addressed."
        )

        if "source_file" in cross_errors.columns:
            if cross_errors["source_file"].fillna("").str.strip().eq("").all():
                cross_errors.drop(columns=["source_file"], inplace=True)

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
            "• Please address all of the identified issues in your next submission, or contact us to explain why specific issues cannot be addressed.\n"
            "• The 'rule_id' column explains the issue and the 'raw_value' column shows the original values that triggered the error.\n"
            "• If you are asked to confirm high wage entries, please perform a brief reasonableness check to ensure the wage does not appear clearly incorrect for the participant."
        )

        if "source_file" in normalization_errors.columns:
            if normalization_errors["source_file"].fillna("").str.strip().eq("").all():
                normalization_errors.drop(columns=["source_file"], inplace=True)

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
          AND completed = 1
        ORDER BY run_timestamp DESC
    """, conn, params=[org, dataset_name, quarter])

    if runs.empty:
        print(f"No runs found for {org}. Skipping.")
        continue

    run_id = runs.iloc[0]["run_id"]

    print(f"Rebuilding {org} ({quarter}) using run_id {run_id}")

    output_path = OUTPUT_DIRECTORY / f"{config_key}_{org}_{quarter}_Data_Refinement_Report_4_24.xlsx"

    rebuild_submission(
        run_id=run_id,
        output_path=output_path,
        conn=conn
    )

conn.close()