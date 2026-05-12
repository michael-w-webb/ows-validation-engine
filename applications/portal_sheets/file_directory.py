"""
portal_file_directory.py
====================

Configuration module defining the directory structure, file paths, workbook
formats, and metadata for all CareerConneCT portal data submissions. This
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
from dotenv import load_dotenv
import os
from pathlib import Path
from config import FILE_DIRECTORY_ROOT

# Auto-generated results module
portal_file_directory = {
  None: {
    "portal data": {
      "PY2 Q2":{ # Even though this data is from PY3 Q4, we are labeling it as PY4 Q1 b/c we have not done a pull since.
          "file path": FILE_DIRECTORY_ROOT / "Portal" / "CC_portal_data_6_29_Modified.xlsm",
          "format": "simple format"
      },
      "PY2 Q3":{ # Even though this data is from PY3 Q4, we are labeling it as PY4 Q1 b/c we have not done a pull since.
          "file path": FILE_DIRECTORY_ROOT / "Portal" / "CC_portal_data_6_29_Modified.xlsm",
          "format": "simple format"
      },  
      "PY2 Q4":{ # Even though this data is from PY3 Q4, we are labeling it as PY4 Q1 b/c we have not done a pull since.
          "file path": FILE_DIRECTORY_ROOT / "Portal" / "CC_portal_data_6_29_Modified.xlsm",
          "format": "simple format"
      },
      "PY3 Q1":{ # Even though this data is from PY3 Q4, we are labeling it as PY4 Q1 b/c we have not done a pull since.
          "file path": FILE_DIRECTORY_ROOT / "Portal" / "CC_portal_data_6_29_Modified.xlsm",
          "format": "simple format"
      },
      "PY3 Q2":{ # Even though this data is from PY3 Q4, we are labeling it as PY4 Q1 b/c we have not done a pull since.
          "file path": FILE_DIRECTORY_ROOT / "Portal" / "CC_portal_data_6_29_Modified.xlsm",
          "format": "simple format"
      },
      "PY3 Q3":{ # Even though this data is from PY3 Q4, we are labeling it as PY4 Q1 b/c we have not done a pull since.
          "file path": FILE_DIRECTORY_ROOT / "Portal" / "CC_portal_data_6_29_Modified.xlsm",
          "format": "simple format"
      },
      "PY3 Q4":{ # Even though this data is from PY3 Q4, we are labeling it as PY4 Q1 b/c we have not done a pull since.
          "file path": FILE_DIRECTORY_ROOT / "Portal" / "CC_portal_data_6_29_Modified.xlsm",
          "format": "simple format"
      },
      "PY4 Q1":{ # Even though this data is from PY3 Q4, we are labeling it as PY4 Q1 b/c we have not done a pull since.
          "file path": FILE_DIRECTORY_ROOT / "Portal" / "CC_portal_data_6_29_Modified.xlsm",
          "format": "simple format"
      },
      "PY4 Q2":{ # Even though this data is from PY3 Q4, we are labeling it as PY4 Q1 b/c we have not done a pull since.
          "file path": FILE_DIRECTORY_ROOT / "Portal" / "CC_portal_data_6_29_Modified.xlsm",
          "format": "simple format"
      }
    }
  }    
}