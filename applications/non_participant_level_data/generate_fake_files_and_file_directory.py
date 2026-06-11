import pandas as pd
from pathlib import Path
import os
from config import FILE_DIRECTORY_ROOT, PROJECT_ROOT



# --------------------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------------------
AGGREGATE_FILE = Path(
    r"C:\Users\DalyRob\State of Connecticut\OWS HQ - Documents\CareerConneCT\Data\Grantee Management (QPRs)\Non Participant Level Data\DataSummary_Non-Participant-Level_CCT.xlsx"
)

TEMPLATE_FILE = Path(
    r"C:\Users\DalyRob\State of Connecticut\OWS HQ - Documents\CareerConneCT\Data\Grantee Management (QPRs)\Non Participant Level Data\Template.xlsx"
)

OUTPUT_ROOT = FILE_DIRECTORY_ROOT



# --------------------------------------------------------------------------------------
# EXPORT FUNCTION
# --------------------------------------------------------------------------------------
def export_non_participant_files(user_grant="", user_org="", user_quarter=""):
    """
    Exports Excel files based on filters and returns a list of metadata describing each file created.
    """

    agg = pd.read_excel(AGGREGATE_FILE)
    template = pd.read_excel(TEMPLATE_FILE)
    template_columns = list(template.columns)

    # FILTERING
    df = agg.copy()

    if user_grant:
        df = df[df["Grant"] == user_grant]

    if user_org:
        df = df[df["Org Folder Name"] == user_org]

    if user_quarter:
        df = df[df["Quarter"] == user_quarter]

    if df.empty:
        print("No rows match the selected filters. Exiting.")
        return []

    results = []   # will collect metadata for file_directory

    for _, row in df.iterrows():

        grant = row["Grant"]
        if grant == "Career Connect": # assign grant_validation_engine_name so that it can seemlessly feed into PBI without adding any new logic.
            grant_validation_engine_name = "training data" 
        elif grant == "Good Jobs Challenge":
            grant_validation_engine_name = "TPI" 
        else: 
            grant_validation_engine_name = "Unknown"
        org = row["Org"]
        org_folder_name = row["Org Folder Name"]   # folder-safe name
        quarter = row["Quarter"]
        quarter_folder_name = quarter.replace("_", " ")
        output_folder_name = "Non Participant Level Data"

        # counts
        n_received_training = int(row["Received Training"])
        n_training_completed = int(row["Training Completed #1"])
        n_employed = int(row["Employment Status at exit"])

        # build participant rows
        records = []
        for i in range(1, n_received_training + 1):
            rec = {col: "" for col in template_columns}

            rec["First Name"] = f"NonParticipantLevelData{i}_{grant}"
            rec["Last Name"] = f"NonParticipantLevelData{i}_{grant}"
            rec["Received Training"] = 1

            if i <= n_training_completed:
                rec["Training Completed #1"] = 1
            if i <= n_employed:
                rec["Employment Status at exit"] = "employed"

            records.append(rec)

        df_out = pd.DataFrame(records, columns=template_columns)

        # output path
        output_dir = OUTPUT_ROOT / grant / org_folder_name / output_folder_name / quarter_folder_name
        output_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{org}_{quarter}_NPLD_Fake_Data.xlsx"
        output_file = output_dir / file_name
        df_out.to_excel(output_file, index=False)

        print(f"Created file: {output_file}")

        # store metadata needed for file_directory
        results.append({
            "grant": grant,
            "grant_validation_engine_name": grant_validation_engine_name,
            "org": org,
            "org_folder_name": org_folder_name,
            "quarter": quarter,
            "quarter_folder_name": quarter_folder_name,
            "file_path": output_file
        })

    return results


# --------------------------------------------------------------------------------------
# WORKBOOK DEFINITIONS GENERATOR
# --------------------------------------------------------------------------------------
def generate_file_directory(file_metadata_list, output_path="file_directory.py"):
    """
    Generates a file_directory.py file based on the exports.
    """

    structure = {}

    for item in file_metadata_list:
        org = item["org"]
        grant = item["grant"]
        grant_validation_engine_name = item["grant_validation_engine_name"] # this will allow PBI logic to correctly categorize as Career Connect or GJC
        org_folder_name = item["org_folder_name"]
        quarter = item["quarter"]  # keep original but also want a clean key
        quarter_folder_name = item["quarter_folder_name"]
        file_path = item["file_path"]

        if org not in structure:
            structure[org] = {
                f"{grant_validation_engine_name}": {}
            }

        relative_path = file_path.relative_to(FILE_DIRECTORY_ROOT)
        relative_parts = list(relative_path.parts)

        # produce: FILE_DIRECTORY_ROOT / "Career ConneCT" / "Org" / ... / "file.xlsx"
        joined_parts = " / ".join(f'"{p}"' for p in relative_parts)

        structure[org][f"{grant_validation_engine_name}"][quarter_folder_name] = {
            "file path": f"FILE_DIRECTORY_ROOT / {joined_parts}",
            "format": "simple format"
        }

    # -----------------------------------------------
    # Write the Python file
    # -----------------------------------------------

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("from config import FILE_DIRECTORY_ROOT\n\n")
        f.write("file_directory = {\n")

        for org, data_section in structure.items():
            f.write(f'    "{org}": {{\n')
            f.write(f'        "{grant_validation_engine_name}": {{\n')

            for quarter_folder_name, attrs in data_section[f"{grant_validation_engine_name}"].items():
                f.write(f'            "{quarter_folder_name}": {{\n')
                f.write(f'                "file path": {attrs["file path"]},\n')
                f.write(f'                "format": "simple format"\n')
                f.write("            },\n")

            f.write("        }\n")
            f.write("    },\n")

        f.write("}\n")

    print(f"file_directory.py created at: {output_path}")


# --------------------------------------------------------------------------------------
# MAIN SCRIPT
# --------------------------------------------------------------------------------------
if __name__ == "__main__":

    # User chooses filter or leaves blank
    USER_GRANT = ""
    USER_ORG = ""
    USER_QUARTER = ""

    APPLICATION = "non_participant_level_data"

    FILE_DIRECTORY_CREATION_PATH = PROJECT_ROOT / "applications" / APPLICATION / "file_directory.py"

    metadata = export_non_participant_files(
        user_grant=USER_GRANT,
        user_org=USER_ORG,
        user_quarter=USER_QUARTER
    )

    if metadata:
        generate_file_directory(file_metadata_list=metadata, output_path=FILE_DIRECTORY_CREATION_PATH)