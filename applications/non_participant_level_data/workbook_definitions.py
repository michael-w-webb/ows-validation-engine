"""
Workbook Definitions, Label Maps, and Schema Metadata
=====================================================

This module contains the authoritative schema specification for all
Non participant level data (npld) data” workbooks supported by the validation
pipeline. It encodes:

    • Canonical column names used throughout the pipeline  
    • All known spelling / formatting variants (“label maps”) that appear
      in provider-submitted Excel files  
    • Column-level metadata describing expected types, requirements, and
      accepted categorical responses  
    • Workbook-level structure (sheet names, starting rows/columns, and
      schema for both *simple format* and *four-sheet format*)  
    • Logic template phrases used by natural-language rule descriptions  

These definitions serve as the central contract between:

    1. **WorkbookLoader** – to map raw header text → canonical names  
    2. **NormalizationEngine / ColumnType classes** – to validate, clean,
       and coerce column values into standardized formats  
    3. **CrossRuleEngine** – to interpret variable types and retrieve the
       correct pandas Series for cross-sheet logic evaluation  
    4. **UI or reporting layers** – to generate intelligible messages and
       consistent descriptions of rule expectations  

-----------------------------------------------------------------------
Label Maps (“labels”)
-----------------------------------------------------------------------

Each sheet definition includes a mapping:

    {
        "Canonical Name": ["Variant A", "Variant B", ...]
    }

The workbook loader uses these maps to:

    • Match raw column headers from provider files  
    • Normalize them into predictable, canonical field names  
    • Tolerate typos, punctuation differences, capitalization,
      OWS-specific export labels, and Salesforce-style field names  

These maps are *lossless*: they never drop fields, they only expand the
set of acceptable column headers.

-----------------------------------------------------------------------
Accepted Responses and Types (“accepted_responses_w_types”)
-----------------------------------------------------------------------

Each canonical column has a metadata block describing:

    • type – one of the defined column classes
      (e.g., "dateTime", "categorical", "boolean", "identifier",
      "hourlyWage", "hoursWorked", "stateID7", "CIPCode", "ONETCode")

    • required – whether the field must be present and non-blank

    • accepted_responses – (optional) list of canonical categorical
      values used by CategoricalColumn normalization and by
      CrossRuleEngine for logical operations

These definitions are consumed by:

    • BaseColumn subclasses during normalization  
    • CrossRuleEngine.get_variable() when creating Variable instances  
    • Rule authoring and error-message templates  

-----------------------------------------------------------------------
Workbook Structure (“workbook_definitions”)
-----------------------------------------------------------------------

The outer `workbook_definitions` object organizes schemas by:

    workbook_type → workbook_format → sheet_name → sheet_definition

For example:

    "npld data" →
        "simple format" →
            "Report" → {labels, accepted_responses, starting_row, ...}


Each sheet definition includes:

    • labels – a full header normalization map  
    • accepted_responses – the column metadata schema  
    • starting_row – where data begins (allows skipping header clutter)  
    • starting_column – permits partial-sheet ingestion  
    • columns_used – reserved for restricting the importable subset

This structure makes it easy for the loader to select the correct
parsing logic depending on which workbook format the provider uploaded.

-----------------------------------------------------------------------
Logic Templates and Expectations
-----------------------------------------------------------------------

Two auxiliary dictionaries define natural-language templates used by
`CrossRuleEngine.describe_logic()`:

    • Logic_Templates – maps operator categories to English snippets
      (e.g., “is in the past”, “is blank”, “is {values}”)

    • Logic_Expectations – indicates whether a field is “required” or
      “should be blank” in IF/THEN constructions

These templates ensure that every rule written in clause-tree syntax can
be rendered into a readable English explanation without custom text.

-----------------------------------------------------------------------
Extending or Updating This Module
-----------------------------------------------------------------------

To add new fields or update schemas:

    1. Add new label variants under the correct sheet’s `labels` dict  
    2. Add (or update) a canonical entry under `accepted_responses`
       with its correct type and accepted categorical responses  
    3. If a new sheet or workbook format is added, create a new
       nested dictionary under `workbook_definitions` following the
       established pattern  
    4. If a new variable type is introduced (e.g., NAICSCode),
       ensure that BaseColumn+Variable subclasses support the type
       before referencing it here  

All changes propagate automatically through:

    • Column mapping  
    • Data normalization  
    • Cross-sheet rule evaluation  
    • Validation reporting  

This module is therefore the **single source of truth** for schema
consistency across every component of the CareerConneCT validation
pipeline.
"""


simple_format_npld_data_labels = {  "First Name": [
      "First Name"
    ],
    "Last Name": [
      "Last Name"
    ],
    "CT Hires Username": [
      "CT Hires Username",
      "CTHires User Name"
    ],
    "CT Hires State ID #": [
      "State ID #"
    ],
    "Submitted Required OWS Forms?": [
      "Submitted Required OWS Forms?",
      "Has participant submitted Required OWS Forms?"
    ],
    "Zip Code": [
      "Zip Code"
    ],
    "Client Date of Birth": [
      "Client Date of Birth",
      "DOB"
    ],
    "Low Income Status at Program Entry?": [
      "Low Income Status at Program Entry?",
      "Low Income Status?"
    ],
    "Basic Skills Deficient/Low Levels of Literacy?": [
      "Basic Skills Deficient/Low Levels of Literacy?_12062",
      "Basic Skills Deficient/Low Levels of Literacy?"
    ],
    "Single Parent at Program Entry?": [
      "Single Parent at Program Entry?",
      "Single parent at program entry?_12063"
    ],
    "Co-enrollment (WIOA or WP)": [
      "Co-enrollment (WIOA or WP)",
      "Co-Enrollment (WIOA or WP)?_12064"
    ],
    "Local Workforce Board Code": [
      "Local Workforce Board Code"
    ],
    "Highest Education Level Completed at Program Entry": [
      "Highest Education Level Completed at Program Entry",
      "Highest education level completed at program entry?_12065"
    ],
    "School Status at Program Entry": [
      "School Status at Program Entry",
      "School status at program entry?_12066"
    ],
    "TANF": [
      "Receiving TANF (Temporary Assistance for Needy Families) benefits?_12067",
      "TANF"
    ],
    "SSI/SSD": [
      "SSI/SSD",
      "Receiving SSI/SSDI or related benefits?_12068"
    ],
    "SNAP": [
      "SNAP",
      "Receiving SNAP (Supplemental Nutrition Assistance Program) benefits?_12069"
    ],
    "Other public assistance recipient": [
      "Other public assistance recipient",
      "Is the participant receiving any other forms of public assistance not listed here?_12070"
    ],
    "Hourly Wage in most recent employment prior to participation": [
      "Hours worked per week most recent employment prior to participation:_12081",
      "Hourly Wage in most recent employment prior to participation"
    ],
    "Hours worked per week most recent employment prior to participation (Only go back 9 months.)": [
      "Hours worked per week most recent employment prior to participation"
    ],
    "Occupational Code of Most Recent Employment Prior to Participation": [
      "Occupational Code of Most Recent Employment Prior to Participation"
    ],
    "Date of Program Entry (Enrollment Date)": [
      "Program Start Date",
      "Date of Program Entry"
    ],
    "Date of Program Exit": [
      "Date of program exit:_12117",
      "Date of Program Exit"
    ],
    "Received Training?": [
      "Received Training",
      "Did participant receive training?_12089"
    ],
    "CareerConneCT Training Provider": [
      "CarerConneCT Training Provider",
      "Career ConneCT Training Provider"
    ],
    "Date Entered Training": [
      "Date participant entered training #1:_12094",
      "Date Entered Training"
    ],
    "Type of Training Service": [
      "Type of Training Service",
      "Type of training service #1:_12099"
    ],
    "CareerConneCT Training Provider Program of Study": [
      "Career ConneCT Training Provider Program of Study",
      "CareerConneCT Training Provider program of study?_12073"
    ],
    "CareerConneCT Training Provider CIP Code": [
      "CIP Code",
      "Career ConneCT Training Provider CIP Code"
    ],
    "Occupational Skills Training Code #1": [
      "Occupational Skills Training Code #1:_12090",
      "Occupational Skills Training Code #1"
    ],
    "Training Completed?": [
      "Did participant complete training #1?_12091",
      "Training Completed #1"
    ],
    "Date Completed or Withdrew From Training #1": [
      "Date Completed or Withdrew From Training #1",
      "Date Completed or Withdrew From Training #1:_12092"
    ],
    "Date Entered Training #2": [
      "Date Entered Training #2",
      "Date participant entered training #2:_12095"
    ],
    "Type of Training Service #2": [
      "Type of Training Service #2",
      "Type of recognized credential received #2:_12108"
    ],
    "Occupational Skills Training Code #2": [
      "Occupational Skills Training Code #2",
      "Occupational Skills Training Code #2:_12096"
    ],
    "Training Completed #2": [
      "Did participant receive training #2?_12093",
      "Training Completed #2"
    ],
    "Date Completed, or Withdrew from, Training #2": [
      "Date Completed, or Withdrew from, Training #2",
      "Date participant entered training #2:_12095"
    ],
    "Date Entered Training #3": [
      "Date Entered Training #3",
      "Date participant entered training #3:_12102"
    ],
    "Type of Training Service #3": [
      "Type of Training Service #3",
      "Type of training service #3:_12106"
    ],
    "Occupational Skills Training Code #3": [
      "Occupational Skills Training Code #3",
      "Occupational Skills Training Code #3:_12103"
    ],
    "Training Completed #3": [
      "Training Completed #3",
      "Did participant complete training #3?_12104"
    ],
    "Date Completed, or Withdrew from, Training #3": [
      "Date Completed, or Withdrew from, Training #3",
      "Date Completed or Withdrew From Training #3:_12105"
    ],
    "Type of Recognized Credential": [
      "Type of Recognized Credential #1",
      "Type of recognized credential received #1:_12107"
    ],
    "Date Attained Recognized Credential": [
      "Date Attained Recognized Credential #1",
      "Date credential #1 received:_12110"
    ],
    "Type of Recognized Credential #2": [
      "Type of recognized credential received #2:_12108",
      "Type of Recognized Credential #2"
    ],
    "Date Attained Recognized Credential #2": [
      "Date credential #2 received:_12111",
      "Date Attained Recognized Credential #2"
    ],
    "Type of Recognized Credential #3": [
      "Type of Recognized Credential #3",
      "Type of recognized credential received #3:_12109"
    ],
    "Date Attained Recognized Credential #3": [
      "Date credential #3 received:_12113",
      "Date Attained Recognized Credential #3"
    ],
    "Type of Recognized Credential #4": [
      "Type of Recognized Credential #4"
    ],
    "Date Attained Recognized Credential #4": [
      "Date Attained Recognized Credential #4",
      "Date Attained Reecognized Credential #4"
    ],
    "Type of Recognized Credential #5": [
      "Type or Recognized Credential #5",
      "Type of Recognized Credential #5"
    ],
    "Date Attained Recognized Credential #5": [
      "Date Attained Recognized Credential #5"
    ],
    "School Status at Exit": [
      "School status at program exit:_12119",
      "School Status at Exit"
    ],
    "Employment Status at exit": [
      "Employment status at exit: (NEED PICK LIST OPTIONS!!)_12118",
      "Employment Status at exit"
    ],
    "Hourly Wage at Exit": [
      "Hourly wage at exit:_12125",
      "Hourly Wage at Exit"
    ],
    "Hours Worked per Week": [
      "Hours Worked per Week"
    ],
    "Employer": [
      "Employer",
      "Employer:_12126"
    ],
    "Job Title": [
      "Job Title",
      "Job Title:_12127"
    ],
    "Employer Zip Code": [
      "Employer Zip Code"
    ],
    "Occupational Code of Employment After Exit": [
      "Occupational Code of employment at exit:_12121",
      "Occupational Code of Employment After Exit"
    ],
    "Occupational Code of Employment 2nd Quarter After Exit Quarter": [
      "Occupational Code of Employment 2nd Quarter After Exit Quarter",
      "Occupational Code of employment - 2nd quarter after program exit:_12123"
    ],
    "Occupational Code of Employment 4th Quarter After Exit": [
      "Occupational Code of Employment 4th Quarter After Exit Quarter",
      "Occupational Code of employment - 4th quarter after program exit:_12124"
    ],
    "Employment Related to Training  (2nd Quarter After Exit)": [
      "Employment Related to Training  (2nd Quarter After Exit)"
    ]}

simple_format_npld_data_accepted_responses_w_types = {
    'First Name': {'type': 'identifier'},
    'Last Name': {'type': 'identifier'},
    'CT Hires Username': {'type': 'identifier'},
    'CT Hires State ID #': {'type': 'stateID7'},
    'Submitted Required OWS Forms?': {'type': 'boolean', 'required': True},
    'Zip Code': {'type': 'zipCode', 'required': True},
    'Client Date of Birth': {'type': 'dateTime', 'required': True},
    'Low Income Status at Program Entry?': {'type': 'boolean'},
    'Basic Skills Deficient/Low Levels of Literacy?': {'type': 'boolean'},
    'Single Parent at Program Entry?': {'type': 'boolean'},
    'Co-enrollment (WIOA or WP)': {'type': 'boolean'},
    'Local Workforce Board Code': {'type': 'identifier'},
    'Highest Education Level Completed at Program Entry': {
        'type': 'categorical',
        'accepted_responses': [
            'no education level completed',
            'attained secondary school diploma',
            'attained a secondary school equivalency',
            'completed one of more years of postsecondary education',
            "attained a bachelor's degree",
            "attained an associate's degree",
            'attained a postsecondary technical or vocational certificate (non-degree)',
            "attained a degree beyond a bachelor's degree"
        ]
    },
    'School Status at Program Entry': {
        'type': 'categorical',
        'accepted_responses': [
            'not attending school or secondary school dropout',
            'not attending school; within age of compulsory school attendance',
            'not attending school; secondary school graduate or has a recognized equivalent',
            'in-school, postsecondary school',
            'in-school, alternative school',
            'in-school, secondary school or less'
        ]
    },
    'TANF': {'type': 'boolean'},
    'SSI/SSD': {
        'type': 'categorical',
        'accepted_responses': ['SSI/SSDI', 'SSI', 'SSDI', 'No']
    },
    'SNAP': {'type': 'boolean'},
    'Other public assistance recipient': {'type': 'boolean'},
    'Hourly Wage in most recent employment prior to participation': {'type': 'hourlyWage'},
    'Hours worked per week most recent employment prior to participation (Only go back 9 months.)': {'type': 'hoursWorked'},
    'Occupational Code of Most Recent Employment Prior to Participation': {'type': 'ONETCode'},
    'Date of Program Entry (Enrollment Date)': {'type': 'dateTime'},
    'Date of Program Exit': {'type': 'dateTime'},
    'Received Training?': {'type': 'boolean'},
    'CareerConneCT Training Provider': {'type': 'identifier'},
    'Date Entered Training': {'type': 'dateTime'},
    'Type of Training Service': {
        'type': 'categorical',
        'accepted_responses': [
            'customized training',
            'prerequisite training',
            'occupational skills training (non-wioa youth)',
            'youth occupational skills training',
            'on the job training (non-wioa youth)',
            'skill upgrading'
        ]
    },
    'CareerConneCT Training Provider Program of Study': {
        'type': 'categorical',
        'accepted_responses': [
            'a program of study leading to an industry-recognized certificate or certification',
            'a program of study leading to a measurable skills gain',
            'a program of study leading to a certificate of completion of a registered apprenticeship',
            'a program of study leading to a license recognized by the state involved or the federal government',
            'a program of study leading to a community college certificate of completion',
            'a program of study leading to employment'
        ]
    },
    'CareerConneCT Training Provider CIP Code': {'type': 'CIPCode'},
    'Occupational Skills Training Code #1': {'type': 'ONETCode'},
    'Training Completed?': {'type': 'boolean'},
    'Date Completed or Withdrew From Training #1': {'type': 'dateTime'},
    'Date Entered Training #2': {'type': 'dateTime'},
    'Type of Training Service #2': {
        'type': 'categorical',
        'accepted_responses': [
            'customized training',
            'prerequisite training',
            'occupational skills training (non-wioa youth)',
            'youth occupational skills training',
            'on the job training (non-wioa youth)',
            'skill upgrading'
        ]
    },
    'Occupational Skills Training Code #2': {'type': 'ONETCode'},
    'Training Completed #2': {'type': 'boolean'},
    'Date Completed, or Withdrew from, Training #2': {'type': 'dateTime'},
    'Date Entered Training #3': {'type': 'dateTime'},
    'Type of Training Service #3': {
        'type': 'categorical',
        'accepted_responses': [
            'customized training',
            'prerequisite training',
            'occupational skills training (non-wioa youth)',
            'youth occupational skills training',
            'on the job training (non-wioa youth)',
            'skill upgrading'
        ]
    },
    'Occupational Skills Training Code #3': {'type': 'ONETCode'},
    'Training Completed #3': {'type': 'boolean'},
    'Date Completed, or Withdrew from, Training #3': {'type': 'dateTime'},
    'Type of Recognized Credential': {
        'type': 'categorical',
        'accepted_responses': [
            'occupational certificate',
            'occupational licensure',
            'secondary school diploma/or equivalency',
            'certificate of completion',
            'industry-recognized credential/certification'
        ]
    },
    'Date Attained Recognized Credential': {'type': 'dateTime'},
    'Type of Recognized Credential #2': {
        'type': 'categorical',
        'accepted_responses': [
            'occupational certificate',
            'occupational licensure',
            'secondary school diploma/or equivalency',
            'certificate of completion',
            'industry-recognized credential/certification'
        ]
    },
    'Date Attained Recognized Credential #2': {'type': 'dateTime'},
    'Type of Recognized Credential #3': {
        'type': 'categorical',
        'accepted_responses': [
            'occupational certificate',
            'occupational licensure',
            'secondary school diploma/or equivalency',
            'certificate of completion',
            'industry-recognized credential/certification'
        ]
    },
    'Date Attained Recognized Credential #3': {'type': 'dateTime'},
    'Type of Recognized Credential #4': {
        'type': 'categorical',
        'accepted_responses': [
            'occupational certificate',
            'occupational licensure',
            'secondary school diploma/or equivalency',
            'certificate of completion',
            'industry-recognized credential/certification'
        ]
    },
    'Date Attained Recognized Credential #4': {'type': 'dateTime'},
    'Type of Recognized Credential #5': {
        'type': 'categorical',
        'accepted_responses': [
            'occupational certificate',
            'occupational licensure',
            'secondary school diploma/or equivalency',
            'certificate of completion',
            'industry-recognized credential/certification'
        ]
    },
    'Date Attained Recognized Credential #5': {'type': 'dateTime'},
    'School Status at Exit': {
        'type': 'categorical',
        'accepted_responses': [
            'not attending school or secondary school dropout',
            'not attending school; secondary school graduate or has a recognized equivalent',
            'not attending school; within age of compulsory school attendance',
            'in-school, secondary school or less',
            'in-school, alternative school',
            'in-school, postsecondary school'
        ]
    },
    'Employment Status at exit': {
        'type': 'categorical',
        'accepted_responses': [
            'employed; part-time',
            'employed; full-time',
            'unemployed',
            'temporarily employed',
            'internship',
            'apprenticeship',
            'employed' # added specifically for npld
        ]
    },
    'Hourly Wage at Exit': {'type': 'hourlyWage'},
    'Hours Worked per Week': {'type': 'hoursWorked'},
    'Employer': {'type': 'identifier'},
    'Job Title': {'type': 'identifier'},
    'Employer Zip Code': {'type': 'zipCode'},
    'Occupational Code of Employment After Exit': {'type': 'ONETCode'},
    'Occupational Code of Employment 2nd Quarter After Exit Quarter': {'type': 'ONETCode'},
    'Occupational Code of Employment 4th Quarter After Exit': {'type': 'ONETCode'},
    'Employment Related to Training  (2nd Quarter After Exit)': {'type': 'boolean'}
}

workbook_definitions = {

"training data":{
  "simple format": {
  
    "Report":{
    "labels": simple_format_npld_data_labels,
    "accepted_responses": simple_format_npld_data_accepted_responses_w_types,
    "columns_used": None,
    "starting_row": 0,
    "sheet_name": "Report",
    "starting_column": 0 # zero covers whole df
    }

  }
},

  "Logic_Templates":{
        "specific_value": "is {values}",
        "not_specific_value": "is not {values}",
        "date_in_past": "is in the past",
        "not_date_in_past": "is not in the past",
        "date_in_past_different_sheet": "is in the past",
        "not_date_in_past_different_sheet": "is not in the past",
        "specific_value_different_sheet": "is {values}",
        "not_specific_value_different_sheet":"is not {values}",
        "is_blank": "is blank",
        "is_blank_different_sheet": "is blank",
        "date_in_past_365": "is one year in the past",
        "date_in_past_132": "is two quarters in the past",
        "date_in_past_different_sheet_365": "is one year in the past",
        "date_in_past_different_sheet_182": "is two quarters in the past"
  },

  "Logic_Expectations":{
        "if_then": "is required",
        "if_then_not": "should be blank"
  }
}