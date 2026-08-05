"""
cc_file_directory.py
====================

Configuration module defining the directory structure, file paths, workbook
formats, and metadata for all CareerConneCT training data submissions. This
mapping is consumed by the workbook loader (`WorkbookLoader` or
`MultiWorkbookLoader`) to locate, interpret, and ingest the correct files for
each organization and reporting period.

Structure
---------
The top-level dictionary is organized as:

    cc_file_directory[org][dataset_type][period] = {
        "file path": str or list[str],
        "format": "simple format" | "four sheet format",
        "starting_row": int (optional)
    }

Where:
    - ``org`` (str):
        Name of the submitting organization or program.
    - ``dataset_type`` (str):
        Currently `"training data"` for CareerConneCT. Additional types may be
        added for other program components.
    - ``period`` (str):
        Reporting period identifier (e.g., "PY3 Q4", "PY4 Q1").
    - ``file path`` (str or list[str]):
        Absolute path(s) to the Excel workbook(s). A list indicates a dataset
        split across multiple files (e.g., multi-location submissions).
    - ``format`` (str):
        Determines which workbook schema/layout to use during parsing:
            * `"simple format"` - single-sheet layout
            * `"four sheet format"` - multi-sheet program template
    - ``starting_row`` (int, optional):
        Used when the Excel file has header rows above the actual dataset.

Usage
-----
This module is imported by orchestration scripts such as
``cc_validation_main.py``, which iterate through all organizations and periods
to:

    1. Select the relevant file(s)
    2. Identify workbook format and any custom metadata
    3. Pass the mapping to ``WorkbookLoader`` for preprocessing and loading
    4. Forward loaded sheets to the ``ValidationEngine``

The validation pipeline depends on this dictionary for automated ingestion of
program submissions.

Maintenance Notes
-----------------
- File paths must be updated each reporting period as new submissions arrive.
- Workbook formats must match the underlying Excel template version used by
  the grantee.
- Avoid trailing spaces or inconsistent casing in organization names, as these
  act as dictionary keys.
- This module may contain PII file paths; store it in a controlled location if
  using version control.
- For multi-file submissions, ensure all related files for a period are
  grouped into a list.

Security Considerations
-----------------------
This file contains absolute local paths to directories that may house sensitive
participant data. While no data is loaded directly here, these paths should not
be published to public repositories. External users should define their own
directory mapping in a private environment.

This module is strictly configuration data and defines no executable logic.
"""
from config import FILE_DIRECTORY_ROOT

# Auto-generated results module
file_directory = {
  "Marrakech": {
    "training data": {
      "PY2 Q2":{
          "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "PY2 Q2" / "CareerConneCT CBO Data Entry Spreadsheet as of 1.16.2024 (Uploaded to SFTP 1.16.2024).xlsx",
          "format": "simple format"
      }, 
      "PY2 Q3":{
          "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "PY2 Q3" / "CareerConneCT CBO Data Entry Spreadsheet as of 3.31.2024 (Uploaded to SFTP 4.11.2024).xlsx",
          "format": "simple format"
      }, 
      "PY2 Q4":{
          "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "PY2 Q4" / "CareerConneCT CBO Data Entry Spreadsheet as of 6.30.2024 (Uploaded to SFTP 7.10.2024).xlsx",
          "format": "simple format"
      }, 
      "PY3 Q1":{
          "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "PY3 Q1" / "Marrakech_PY3Q1_SS_Cleaned.xlsx",
          "format": "simple format"
      }, 
      "PY3 Q2":{
          "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "PY3Q2" / "Y3Q2 participant spreadsheet.xlsx",
          "format": "simple format"
      },  
      "PY3 Q3":{
          "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "Y3Q3" / "Y2Q2 Marrakech Data Entry Spreadsheet.xlsx",
          "format": "simple format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "Y3Q4" / "Marrakech_CareerConneCT_Import_7.9.25.xlsx",
        "format": "simple format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "Y4Q1" / "CareerConneCT Import 10.10.25.xlsx",
        "format": "simple format",
        "starting row": 3
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "Y4Q2" / "CareerConneCT Import 1.6.26.xlsx",
        "format": "simple format",
        "starting row": 3
      },
      "PY4 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Marrakech" / "Y4Q3" / "CareerConneCT Import 4.10.26 (3).xlsx",
        "format": "simple format",
        "starting row": 3
      }
    }
  },
  "Career Resources We Rise": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "PY2 Q1" / "2023-10-10_CRI_WeRise_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "PY2 Q2" / "CRI. WE RISE. CareerConneCT Client Data Entry Spreadsheet Y2.Q2..xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "PY2 Q3" / "CRI. Y2. Q3. WE RISE CareerConneCT Client Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "PY2 Q4" / "Y2 Q4 CRI WE RISE CareerConneCT Client Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },      
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "PY3 Q1" / "CRI WE RISE CareerConneCT Client Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "PY3Q2" / "Y3Q2 Staggered Spreadsheet CRI WR.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "PY3Q3" / "Y3Q3 Data Entry Spreadsheet CRI WR.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "PY3Q4" / "Career_Resources_We_Rise_WERISE_Y3Q4__Data_Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        ## this is currently missing transfers, need to talk to Dave about how he formats these.  
        "file path": [FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q1" / "Y4.Q1. CRI WeRise. Hartford Client Data Entry Spreadsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q1" / "Y4.Q1. CRI WeRise. Waterbury Client Data Entry Sheetsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q1" / "Y4.Q1. CRI WR New Haven - Data Entry Spreadsheet Updated.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q1" / "Y4.Q1. CRI WR New London - Data Entry Spreadsheet Updated.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q1" / "Y4Q1. CRI WeRise. Bridgeport. Client Data Entry Spreadsheet.xlsm"],
        "format": "four sheet format"
      },
      "PY4 Q2": {
        ## this is currently missing transfers, need to talk to Dave about how he formats these.  
        "file path": [FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q2" / "To OWS. Bridgeport Client Data Entry Spreadsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q2" / "To OWS. Hartford Client Data Entry Spreadsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q2" / "To OWS. New Haven Client Data Entry Spreadsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q2" / "To OWS. New London Client Data Entry Spreadsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q2" / "To OWS. Waterbury Client Data Entry Sheet.xlsm"],
        "format": "four sheet format"
      },
      "PY4 Q3": {
        ## this is currently missing transfers, need to talk to Dave about how he formats these.  
        "file path": [FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q3" / "4.15.26. Refinement. Bridgeport Client Data Entry Sheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q3" / "4.15.26. Refinement. Hartford Client Data Entry Spreadsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q3" / "4.15.26. Refinement. New Haven Client Data Entry Spreadsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q3" / "4.15.26. Adjust and Refinement. New London Client Data Entry Spreadsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q3" / "4.15.26. Refinement. Waterbury Client Data Entry Sheet.xlsm"],
        "format": "four sheet format"
      },
      "PY4 Q4": {
        ## this is currently missing transfers, need to talk to Dave about how he formats these.  
        "file path": [FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q4 FINAL" / "Close Out. Y4.Q4. Waterbury Client Data Entry Sheet 7.7.26.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q4 FINAL" / "Close Out. Y4.Q4. New London Client Data Entry Spreadsheet.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q4 FINAL" / "Close Out. Y4.Q4. Hartford Client Data Entry Spreadsheet 7.6.26.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q4 FINAL" / "Close Out. Y4.Q4. Bridgeport Client Data Entry Sheet 7.17.26.xlsm",
                      FILE_DIRECTORY_ROOT / "Career Connect"  / "Career Resources WeRise" / "Y4Q4 FINAL" / "Close Out. Y4.Q4 New Haven Client Data Entry Spreadsheet.xlsm"],
        "format": "four sheet format"
      }
    }
  },
  "Career Resources Health Career": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "PY2 Q1" / "2023-10-10_CRI_HCTP_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "PY2 Q2" / "Y2. Q2. Healthcare Careers. Client Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "PY2 Q3" / "Healthcare Careers. Client Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "PY2 Q4" / "Y2. Q4. Healthcare Careers. Client Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "PY3 Q1" / "Y3. Q1 Healthcare Careers. Client Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "PY3 Q2" / "Y3Q2 Staggered Spreadsheet CRI HC.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "PY3Q3" / "CRI HC Client Entry Spreadsheet Y3 Q3.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "Y3Q4" / "Career_Resources_Health_Career_Y3Q4_CRI_HC_Data_Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "Y4Q1" / "NEW OWS. Y4 Q1.CRI Healthcare Careers Client Data Entry Spreadsheet.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Career Resources Health Career Training Program" / "Y4Q2" / "To OWS. Y4 Q2.CRI Healthcare Careers Client Data Entry Spreadsheet.xlsm",
        "format": "four sheet format"
      }
    }
  },
  "CWP CDL": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "PY2" / "Q1" / "PY2Q1 - CWP - CDL Data_20231010 -.xlsx",
        "format": "simple format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "PY2" / "Q2" / "PY2Q2 - CWP - CDL Data_20240109.xlsx",
        "format": "simple format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "PY2" / "Q3" / "PY2Q3 - CWP - CDL Data_20240412.xlsx",
        "format": "simple format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "PY2" / "Q4" / "PY2Q4 - CWP - CDL Data_20240711.xlsx",
        "format": "simple format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "PY3" / "Q1" / "PY3Q1 - CWP - CDL Data_20241007.xlsx",
        "format": "simple format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "Y3Q2" / "Y3Q2  CWP CDL staggered spreadsheer.xlsx",
        "format": "simple format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "Y3Q3" / "Y3Q3  Data Entry Sheet CWP CDL.xlsx",
        "format": "simple format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "Y3Q4" / "CWP_CDL_PY3Q4_CWP_CDL_Data_2025710.xlsx",
        "format": "simple format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "Y4Q1" / "CWP - CCT - CDL Data_20251010.xlsx",
        "format": "simple format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "Y4Q2" / "PY4Q2 CWP CDL Data_20260108.xlsx",
        "format": "simple format"
      },
      "PY4 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "Y4Q3" / "PY4Q3 CWP CDL Data 20260410.xlsx",
        "format": "simple format"
      },
      "PY4 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners CDL" / "Y4Q4 FINAL" / "PY4Q4 CWP CDL Data 20260707.xlsx",
        "format": "simple format"
      }
    }
  },
  "CWP IT": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "PY2" / "Q1" / "PY2Q1 - CWP - IT Data_20231010.xlsx",
        "format": "simple format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "PY2" / "Q2" / "PY2Q2 - CWP - IT Data_20240109.xlsx",
        "format": "simple format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "PY2" / "Q3" / "PY2Q3 - CWP - IT Data_20240412.xlsx",
        "format": "simple format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "PY2" / "Q4" / "PY2Q4 - CWP - IT Data_20240711.xlsx",
        "format": "simple format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "PY3 Q1" / "PY3Q1 - CWP - IT Data_20241007.xlsx",
        "format": "simple format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "Y3Q2" / "Y3Q2 CWP  IT staggered spreadsheet.xlsx",
        "format": "simple format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "Y3Q3" / "Y3Q3 data entry CWP IT.xlsx",
        "format": "simple format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "Y3Q4" / "CWP_IT_PY3Q4_CWP_IT_Data_2025710.xlsx",
        "format": "simple format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "Y4Q1" / "PY4Q1 - CWP - IT Data_20251010.xlsx",
        "format": "simple format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "Y4Q2" / "PY4Q2 CWP IT Data_20260108.xlsx",
        "format": "simple format"
      },
      "PY4 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "Y4Q3" / "PY4Q3 CWP IT Data 20260410.xlsx",
        "format": "simple format"
      },
      "PY4 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Capital Workforce Partners" / "Capital Workforce Partners IT" / "Y4Q4 FINAL" / "PY4Q4 CWP IT Data 20260707.xlsx",
        "format": "simple format"
      }
    }
  },
  "EWIB": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "PY2" / "Q1" / "2023-10-06_EWIB_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "PY2" / "Q2" / "CareerConneCT Staggered Data Entry Spreadsheet (2).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "PY2" / "Q3" / "CareerConneCT Staggered Data Entry Spreadsheet (3).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "PY2" / "Q4" / "Y2 Q4 CareerConneCT Staggered Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "PY3 Q1" / "Y3 Q1 CareerConneCT Staggered Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "PY3 Q2" / "Y3 Q2 EWIB CCT Staggered Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "PY3Q3" / "Y3 Q3 Staggered Spreadsheet EWIB.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "PY3Q4" / "EWIB_Y3Q4_Data_Entry_Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "Y4Q1" / "EWIB - Data Entry Spreadsheet 10-9-25.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "Y4Q2" / "EWIB - Data Entry Spreadsheet Updated 12-30-25.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "Y4Q3" / "EWIB - Data Entry Spreadsheet Updated (3).xlsm",
        "format": "four sheet format"
      },
      "PY4 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Eastern Workforce Investment Board" / "Y4Q4 FINAL" / "EWIB - Data Entry Spreadsheet Updated (4).xlsm",
        "format": "four sheet format"
      }
    }
  },
  "TWP Health CareeRx Academy": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "PY2" / "Q1" / "2023-10-11_TWP_CareeRx_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "PY2" / "Q2" / "Y2Q2 CareerConneCT Staggered Data Entry Spreadsheet (1).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "PY2 Q3" / "Y2Q3 - CareerConneCT Data Entry Spreadsheet (1).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "PY2 Q4" / "Y2Q4 - CareerConneCT Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "PY3 Q1" / "Y3Q1 - CareerConneCT Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "PY3 Q2" / "Y3Q2 CCT Staggered Spreadsheet TWP HC.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "Y3Q3" / "Y3Q3  TWP HCA Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "Y3Q4" / "TWP_Health_CareeRx_Academy_Y3Q4_-TWP_HC_Data_Entry_Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "Y4Q1" / "TWP HC - Data Entry Spreadsheet Updated (9) (1).xlsm",
        "format": "four sheet format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "Y4Q2" / "Y4Q2 - CareerConneCT Data Entry Spreadsheet (1).xlsx",
        "format": "four sheet format"
      },
      "PY4 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Health CareeRx" / "Y4Q4 FINAL" / "Y4Q4- CareerConneCT Data Entry Spreadsheet  (3).xlsx",
        "format": "four sheet format"
      }
    }
  },
  "TWP Remote Works": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "PY2 Q1" / "RemoteWorks CareerConneCT Staggered Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "PY2 Q2" / "RemoteWorks CareerConneCT Staggered Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "PY2 Q3" / "RemoteWorks CareerConneCT Staggered Data Entry Spreadsheet Y2Q3.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "PY2 Q4" / "RemoteWorks CareerConneCT Staggered Data Entry Spreadsheet Y2Q4.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "PY3 Q1" / "RemoteWorks CareerConneCT Staggered Data Entry Spreadsheet Y3 Q1.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "Y3 Q2" / "Y3 Q2 Staggered Spreadsheet TWP RW.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "Y3Q3" / "TWP RW Data Entry Spreadsheet Y3Q3.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "Y3Q4" / "TWP_Remote_Works_Y3_Q4_TWP_RW_Data_Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "Y4Q1" / "RemoteWorks CareerConneCT Staggered Data Entry Spreadsheet Y4 Q1.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "Y4Q2" / "RemoteWorks CareerConneCT Staggered Data Entry Spreadsheet Y4 Q2.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "Y4Q3" / "RemoteWorks CareerConneCT Staggered Data Entry Spreadsheet Y4 Q3.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "TWP Remote Works" / "Y4Q4 FINAL" / "RemoteWorks CareerConneCT Staggered Data Entry Spreadsheet Y4 Q4.xlsm",
        "format": "four sheet format"
      }
    }
  },
  "Charter Oak State College Foundation": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "PY2 Q1" / "2023-10-16_COSCF_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "PY2 Q3" / "CareersConneCT .xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "PY2 Q4" / "COSCF_PY2Q4_SDS.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "PY3 Q1" / "COSCF_PY3Q1_ProgData.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "PY3 Q2" / "Y3Q2 CCT Staggered Spreadsheet COSCF.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "Y3Q3" / "Y3Q3 Data Entry Spreadsheet COSCF.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "Y3Q4" / "COSCF_Y3Q4_Data_Entry_Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "Y4Q1" / "CareerConneCT Staggered Data Entry Spreadsheet Charter Oak State College Foundation JUNE 2025 FINAL.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "Y4Q2" / "Career ConneCT Staggered DataEntry Spreadsheet Charter OakState College Foundation December2025FINAL.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "Y4Q3" / "CareerConneCT Staggered Data Entry Spreadsheet Charter Oak State College FoundationApril152026FINAL.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Charter Oak State College Foundation" / "Y4Q4 FINAL" / "CareerConneCT Staggered Data Entry Spreadsheet Charter Oak State College FoundationJuly2026FINAL.xlsx",
        "format": "four sheet format"
      }
    }
  },
  "Connecticut State Building Trades Training Institute": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "PY2 Q1" / "2023-10-10_CSBTTI_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "PY2 Q2" / "CareerConneCT Staggered Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "PY2 Q3" / "CareerConneCT Staggered Data Entry Spreadsheet  as of  33124 FINAL (1).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "PY2 Q4" / "CareerConneCT Staggered Data Entry Spreadsheet 63024 FINAL.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "PY3 Q2" / "Y3Q2 CCT Staggered Spreadsheet CSBTTI.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "Y3Q3" / "CareerConneCT Staggered Data Entry Spreadsheet 33125.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "Y3Q4" / "Connecticut_State_Building_Trades_Training_Institute_Y3Q4_CSBTTI_Data_Entry_Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "Y4Q1" / "Connecticut_State_Building_Trades_Training_Institute_Y4Q1.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "Y4Q2" / "CSBTTI Data Entry Spreadsheet PY4 Q2 - MW Corrected.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q3": { 
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Connecticut State Building Trades Training Institute" / "Y4Q3" / "CSBTTI Data Entry Spreadsheet PY4 Q3 - MW Corrected (1).xlsm",
        "format": "four sheet format"
      }
    }
  },
  "Family Centers": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "PY2 Q1" / "2023-10-12_FamilyCenters_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "PY2 Q2" / "FamilyCenters PY2Q2.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "PY2 Q3" / "CareerConneCT Staggered Data Entry Spreadsheet Jan. - Mar. 2024.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "PY2 Q4" / "CareerConneCT Staggered Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "PY3 Q1" / "CareerConneCT Staggered Data Entry Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "PY3 Q2" / "CCTStaggeredSpreadsheetY3Q2FC.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "Y3Q3" / "Y3Q3 Data Entry FC.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "Y3Q4" / "Family_Centers_Y3Q4_FC_Data_Entry_Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "Y4Q1" / "FC - Data Entry Spreadsheet.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "Y4Q2" / "FC - Data Entry Spreadsheet Y4Q2.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "Y4Q3" / "FC - Data Entry Spreadsheet.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Family Centers" / "Y4Q4 FINAL" / "FC - Data Entry Spreadsheet (June 2026).xlsm",
        "format": "four sheet format"
      }
    }
  },
  "Havenly": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "PY2 Q1" / "2023-10-10_Havenly_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "PY2 Q2" / "Havenly - CareerConneCT Staggered Data Entry Spreadsheet Y2Q2 (1) (1).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "PY2 Q3" / "Havenly - CareerConneCT Staggered Data Entry Spreadsheet Y2Q3(1).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "PY2 Q4" / "Havenly - CareerConneCT Staggered Data Entry Spreadsheet Y2Q4(1).xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "PY3 Q1" / "Havenly - CCT Staggered Data Entry Spreadsheet Y3Q1.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "PY3Q2" / "Y3Q2 Staggered Spreadsheet Havenly - Copy.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "Y3Q3" / "Havenly - CareerConneCT Staggered Data Entry Spreadsheet Y3Q3.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "Y3Q4" / "Havenly_Y3Q4_Data_Entry_Spreadsheet.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "Y4Q1" / "Havenly - Data Entry Spreadsheet_y4Q1.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "Y4Q2" / "Havenly - Data Entry Spreadsheet Y4Q2.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "Y4Q3" / "Havenly - Data Entry Spreadsheet Y4Q3.xlsm",
        "format": "four sheet format"
      },
      "PY4 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Havenly" / "Y4Q4 final" / "Havenly - Data Entry Spreadsheet Y4Q4.xlsm",
        "format": "four sheet format"
      }

    }
  },
  "ReadyCT": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "PY2 Q1" / "2023-10-10_ReadyCT_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "PY2 Q2" / "ReadyCT Staggered Data Entry (1_10_2024).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "PY2 Q3" / "ReadyCT Staggered Data Entry (4_8_2024).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "PY2 Q4" / "ReadyCT Staggered Data Entry (7_10_2024).xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "PY3 Q1" / "ReadyCT Staggered Data Entry (10_10_2024).xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "PY3Q2" / "Y3Q2 Staggered Spreadsheet ReadyCT.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "Y3Q3" / "Y3Q3 ReadyCT Staggered Data Entry.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "Y3Q4" / "ReadyCT_ReadyCT_Staggered_Data_Entry_(7.10.25).xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "Y4Q1" / "ReadyCT - Student 5.0 SDE w Macros (10_10_25).xlsm",
        "format": "four sheet format"
      },
      "PY4 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "Y4Q2" / "ReadyCT - Student 5.0 SDE w Macros (01_09_26).xlsm",
        "format": "four sheet format"
      },
      "PY4 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "Y4Q3" / "ReadyCT - Student 5.0 SDE w Macros (04_15_2026) (1).xlsm",
        "format": "four sheet format"
      },
      "PY4 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ReadyCT" / "Y4Q4 FINAL" / "ReadyCT - Student 5.0 SDE w Macros (07_30_2026) (2).xlsm",
        "format": "four sheet format"
      }
    }
  },
  "CCAT": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "CCAT" / "PY2 Q1" / "2023-10-10_CCAT_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "CCAT" / "PY2 Q2" / "CareerConneCT Staggered Data Entry Spreadsheet (Q4) .xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "CCAT" / "PY2 Q3" / "CareerConneCT Staggered Data Entry Spreadsheet (Q1.24).xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "CCAT" / "PY2 Q4" / "CareerConneCT Staggered Data Entry Spreadsheet (Q3.24).xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "CCAT" / "PY3 Q1" / "CareerConneCT Staggered Data Entry Spreadsheet (Q3.24).xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "CCAT" / "PY3Q2" / "Y3Q2 CCT Staggered  Spreadsheet CCAT.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "CCAT" / "Y3Q3" / "Data Entry Spreadsheet CCAT.xlsx",
        "format": "four sheet format"
      }
    }
  },
  "Efficiency For All": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Efficiency for All" / "PY2 Q1" / "2023-10-12_EFA_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Efficiency for All" / "PY2 Q2" / "EFA Expanded Staggered Data Entry Spreadsheet Current 2024-01-12.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Efficiency for All" / "PY2 Q3" / "2024-03-31 PY2 Q3 Data - Untouched.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Efficiency for All" / "PY2 Q4" / "EFA Expanded Staggered Data Entry Spreadsheet Current 2024-06-30.xlsx",
        "format": "four sheet format"
      }
    }
  },
  "DAE": {
    "training data": {
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "District Arts and Education" / "PY2 Q2" / "CareerConneCT Staggered Data Entry Spreadsheet_October-2023.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "District Arts and Education" / "PY2 Q3" / "CareerConneCT Staggered Data Entry Spreadsheet_April-2024.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "District Arts and Education" / "PY2 Q4" / "CareerConneCT Staggered Data Entry Spreadsheet_July-2024.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "District Arts and Education" / "PY3 Q1" / "CareerConneCT Staggered Data Entry Spreadsheet_October-2024.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "District Arts and Education" / "PY3 Q2" / "Y3Q2 CCT Staggered Spreadsheet DAE.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "District Arts and Education" / "Y3Q3" / "DAE_Y3Q3_Data_Entry_Spreadsheet_DAE.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "District Arts and Education" / "Y3Q4 FINAL" / "DAE_Y3Q3_Data_Entry_Spreadsheet_DAE.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "District Arts and Education" / "Y4Q1 Follow Up" / "DAE_Y4Q1_Data Entry_Spreadsheet.xlsm",
        "format": "four sheet format"
      }
    }
  },
  "ConnCat": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ConnCAT" / "PY2 Q1" / "ConnCAT BioLaunchCT FY24 Y2 Q1_submitted.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ConnCAT" / "PY2 Q2" / "CareerConneCT Staggered Data Entry Spreadsheet_ConnCAT BioLaunchCT FY24 Y2 Q2_submitted.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ConnCAT" / "PY2 Q3" / "CareerConneCT Staggered Data Entry Spreadsheet_ConnCAT BioLaunchCT FY24 Y2 Q3_subnmitted.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ConnCAT" / "PY2 Q4" / "CareerConneCT Staggered Data Entry Spreadsheet_ConnCAT BioLaunchCT FY24 Y2 Q4_Myles oy edit_submitted.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ConnCAT" / "PY3 Q1" / "CCT ConnCAT Staggered Spreadsheet V2 12.3.24.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ConnCAT" / "PY3 Q2" / "Y3 Q2 REVISED CCT Staggered Spreadsheet_ConnCAT.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ConnCAT" / "Y3Q3" / "Y3Q3 Data Entry Spreadsheet ConnCAT.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ConnCAT" / "Y3Q4" / "ConnCat_CareerConneCT_Staggered_Data_Entry_Spreadsheet_ConnCAT_BioLaunchCT_FY25_Y3_Q4_submitted.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "ConnCAT" / "Y4Q1 Follow Up" / "ConnCat_CareerConneCT_Staggered_Data_Entry_Spreadsheet_ConnCAT_BioLaunchCT_FY25_Y3_Q4_submitted.xlsm",
        "format": "four sheet format"
      }
    }
  },
  "Ability Beyond": {
    "training data": {
      "PY2 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Ability Beyond" / "PY2 Q1" / "2023-10-10_AbilityWorks_Participants.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Ability Beyond" / "PY2 Q2" / "CareerConneCT Staggered Date Entry Spreadsheet_AW1.10.24.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Ability Beyond" / "PY2 Q3" / "Staggered Data Entry Spreadsheet_4.10.24.xlsx",
        "format": "four sheet format"
      },
      "PY2 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Ability Beyond" / "PY2 Q4" / "Staggered Data Entry Spreadsheet_7.10.24.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Ability Beyond" / "PY3 Q1" / "Staggered Data Entry Spreadsheet_10.10.24.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q2": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Ability Beyond" / "PY3Q2" / "Y3Q2 Staggered Spreadsheet AB.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q3": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Ability Beyond" / "Y3Q3" / "Y3Q3 Data Entry Spreadsheet AB.xlsx",
        "format": "four sheet format"
      },
      "PY3 Q4": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Ability Beyond" / "Y3Q4" / "Ability_Beyond_Staggered_Data_Entry_Spreadsheet_7.30.25.xlsx",
        "format": "four sheet format"
      },
      "PY4 Q1": {
        "file path": FILE_DIRECTORY_ROOT / "Career Connect" / "Ability Beyond" / "Y4Q1 Follow Up" / "Ability_Beyond_Staggered_Data_Entry_Spreadsheet_Updated 10.29.25.xlsm",
        "format": "four sheet format"
      }
    }
  }
}