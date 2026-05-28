"""
Workbook Definitions, Label Maps, and Schema Metadata
=====================================================

This module contains the authoritative schema specification for all
CareerConneCT “training data” workbooks supported by the validation
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

    "training data" →
        "simple format" →
            "Report" → {labels, accepted_responses, starting_row, ...}

        "four sheet format" →
            "Personal Information"
            "Training"
            "Credential"
            "Outcomes"

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


simple_format_training_data_labels = {  "First Name": [
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
      "Hourly wage in most recent employment prior to participation:_12129",
      "Hourly Wage in most recent employment prior to participation"
    ],
    "Hours worked per week most recent employment prior to participation (Only go back 9 months.)": [
      "Hours worked per week most recent employment prior to participation",
      "Hours worked per week most recent employment prior to participation:_12081"
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

simple_format_training_data_accepted_responses_w_types = {
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
            'apprenticeship'
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

simple_format_supportive_services_labels = {
    "First Name": [
        "First Name",
        "FirstName",
        "FirstLast",
        "first_name"
    ],
    "Last Name": [
        "Last Name",
        "last_name"
    ],
    "CT Hires Username": [
        "CT Hires Username",
        "CTHires User Name",
        "CTHires_Username",
        "ct_hires_username"
    ],
    "CT Hires State ID #": [
        "CTH State ID",
        "State ID #"
    ],
    "Zip Code": [
        "Zip Code",
        "ZIP",
        "zip_code",
        "Program Enrollment: Account: Person Account: Mailing Zip/Postal Code"
    ],

    # Supportive Services Columns
    "Category of Support 1": ["Category of Support 1", "Category_1", "category_of_support_1"],
    "Specific Use 1": ["Specific Use of Funds 1", "Use_1", "specific_use_1"],
    "Dollar Amount 1": ["Dollar Amount ($) 1", "Dollar_1", "dollar_amount_1", "Dollar Amount 1"],

    "Category of Support 2": ["Category of Support 2", "Category_2", "category_of_support_2"],
    "Specific Use 2": ["Specific Use of Funds 2", "Use_2", "specific_use_2"],
    "Dollar Amount 2": ["Dollar Amount ($) 2", "Dollar_2", "dollar_amount_2", "Dollar Amount 2"],

    "Category of Support 3": ["Category of Support 3", "Category_3", "category_of_support_3"],
    "Specific Use 3": ["Specific Use of Funds 3", "Use_3", "specific_use_3"],
    "Dollar Amount 3": ["Dollar Amount ($) 3", "Dollar_3", "dollar_amount_3", "Dollar Amount 3"],

    "Category of Support 4": ["Category of Support 4", "Category_4", "category_of_support_4"],
    "Specific Use 4": ["Specific Use of Funds 4", "Use_4", "specific_use_4"],
    "Dollar Amount 4": ["Dollar Amount ($) 4", "Dollar_4", "dollar_amount_4", "Dollar Amount 4"],

    "Category of Support 5": ["Category of Support 5", "Category_5", "category_of_support_5"],
    "Specific Use 5": ["Specific Use of Funds 5", "Use_5", "specific_use_5"],
    "Dollar Amount 5": ["Dollar Amount ($) 5", "Dollar_5", "dollar_amount_5", "Dollar Amount 5"],

    "Category of Support 6": ["Category of Support 6", "Category_6", "category_of_support_6"],
    "Specific Use 6": ["Specific Use of Funds 6", "Use_6", "specific_use_6"],
    "Dollar Amount 6": ["Dollar Amount ($) 6", "Dollar_6", "dollar_amount_6", "Dollar Amount 6"],

    "Category of Support 7": ["Category of Support 7", "Category_7", "category_of_support_7"],
    "Specific Use 7": ["Specific Use of Funds 7", "Use_7", "specific_use_7"],
    "Dollar Amount 7": ["Dollar Amount ($) 7", "Dollar_7", "dollar_amount_7", "Dollar Amount 7"],

    "Category of Support 8": ["Category of Support 8", "Category_8", "category_of_support_8"],
    "Specific Use 8": ["Specific Use of Funds 8", "Use_8", "specific_use_8"],
    "Dollar Amount 8": ["Dollar Amount ($) 8", "Dollar_8", "dollar_amount_8", "Dollar Amount 8"],

    "Category of Support 9": ["Category of Support 9", "Category_9", "category_of_support_9"],
    "Specific Use 9": ["Specific Use of Funds 9", "Use_9", "specific_use_9"],
    "Dollar Amount 9": ["Dollar Amount ($) 9", "Dollar_9", "dollar_amount_9", "Dollar Amount 9"],

    "Category of Support 10": ["Category of Support 10", "Category_10", "category_of_support_10"],
    "Specific Use 10": ["Specific Use of Funds 10", "Use_10", "specific_use_10"],
    "Dollar Amount 10": ["Dollar Amount ($) 10", "Dollar_10", "dollar_amount_10", "Dollar Amount 10"],

    "Category of Support 11": ["Category of Support 11", "Category_11", "category_of_support_11"],
    "Specific Use 11": ["Specific Use of Funds 11", "Use_11", "specific_use_11"],
    "Dollar Amount 11": ["Dollar Amount ($) 11", "Dollar_11", "dollar_amount_11", "Dollar Amount 11"],

    "Category of Support 12": ["Category of Support 12", "Category_12", "category_of_support_12"],
    "Specific Use 12": ["Specific Use of Funds 12", "Use_12", "specific_use_12"],
    "Dollar Amount 12": ["Dollar Amount ($) 12", "Dollar_12", "dollar_amount_12", "Dollar Amount 12"],

    "Category of Support 13": ["Category of Support 13", "Category_13", "category_of_support_13"],
    "Specific Use 13": ["Specific Use of Funds 13", "Use_13", "specific_use_13"],
    "Dollar Amount 13": ["Dollar Amount ($) 13", "Dollar_13", "dollar_amount_13", "Dollar Amount 13"],

    "Category of Support 14": ["Category of Support 14", "Category_14", "category_of_support_14"],
    "Specific Use 14": ["Specific Use of Funds 14", "Use_14", "specific_use_14"],
    "Dollar Amount 14": ["Dollar Amount ($) 14", "Dollar_14", "dollar_amount_14", "Dollar Amount 14"],

    "Category of Support 15": ["Category of Support 15", "Category_15", "category_of_support_15"],
    "Specific Use 15": ["Specific Use of Funds 15", "Use_15", "specific_use_15"],
    "Dollar Amount 15": ["Dollar Amount ($) 15", "Dollar_15", "dollar_amount_15", "Dollar Amount 15"],

    "Category of Support 16": ["Category of Support 16", "Category_16", "category_of_support_16"],
    "Specific Use 16": ["Specific Use of Funds 16", "Use_16", "specific_use_16"],
    "Dollar Amount 16": ["Dollar Amount ($) 16", "Dollar_16", "dollar_amount_16", "Dollar Amount 16"],

    "Category of Support 17": ["Category of Support 17", "Category_17", "category_of_support_17"],
    "Specific Use 17": ["Specific Use of Funds 17", "Use_17", "specific_use_17"],
    "Dollar Amount 17": ["Dollar Amount ($) 17", "Dollar_17", "dollar_amount_17", "Dollar Amount 17"],

    "Category of Support 18": ["Category of Support 18", "Category_18", "category_of_support_18"],
    "Specific Use 18": ["Specific Use of Funds 18", "Use_18", "specific_use_18"],
    "Dollar Amount 18": ["Dollar Amount ($) 18", "Dollar_18", "dollar_amount_18", "Dollar Amount 18"],

    "Category of Support 19": ["Category of Support 19", "Category_19", "category_of_support_19"],
    "Specific Use 19": ["Specific Use of Funds 19", "Use_19", "specific_use_19"],
    "Dollar Amount 19": ["Dollar Amount ($) 19", "Dollar_19", "dollar_amount_19", "Dollar Amount 19"],

    "Category of Support 20": ["Category of Support 20", "Category_20", "category_of_support_20"],
    "Specific Use 20": ["Specific Use of Funds 20", "Use_20", "specific_use_20"],
    "Dollar Amount 20": ["Dollar Amount ($) 20", "Dollar_20", "dollar_amount_20", "Dollar Amount 20"]
}

four_sheet_personal_information_labels = {

      "First Name": [
        "First Name"
      ],
      "Last Name": [
        "Last Name"
      ],
      "CT Hires Username": [
        "CT Hires Username (OWS)",
        "CT Hires Username",
        "CT Hires"
      ],
      "CT Hires State ID #": [
        "State ID #",
        "State ID Number (OWS)",
        "CT Hires State ID #",
        "State ID # (NA)"
      ],
      "Submitted Required OWS Forms?": [
        "Submitted Required OWS Forms?"
      ],
      "Zip Code": [
        "Zip Code",
        "Zip"
      ],
      "Client Date of Birth": [
        "Client Date of Birth",
        "Student Date of Birth"
      ],
      "Low Income Status at Program Entry?": [
        "Low Income Status at Program Entry?",
        "Low-income status at program entry (OWS)"
      ],
      "Basic Skills Deficient/Low Levels of Literacy?": [
        "Basic skills deficit/Low levels of literacy (OWS)",
        "Basic Skills Deficient/Low Levels of Literacy?"
      ],
      "Single Parent at Program Entry?": [
        "Single Parent at Program Entry?",
        "Single parent at program entry (OWS)"
      ],
      "Co-enrollment (WIOA or WP)": [
        "Co-enrollment (WIOA or WP)",
        "Co-enrollment (WIOA or WP) (OWS)"
      ],
      "Local Workforce Board Code": [
        "Local Workforce Board Code",
        "Local workforce board code (OWS)"
      ],
      "Highest Education Level Completed at Program Entry": [
        "Highest ed level completed @ program entry (OWS)",
        "Highest Education Level Completed at Program Entry"
      ],
      "School Status at Program Entry": [
        "School status at program entry (OWS)",
        "School Status at Program Entry"
      ],
      "TANF": [
        "TANF (OWS)",
        "TANF"
      ],
      "SSI/SSD": [
        "SSI/SSD",
        "SSI/SSDI (OWS)"
      ],
      "SNAP": [
        "SNAP",
        "SNAP (OWS)"
      ],
      "Other public assistance recipient": [
        "Recipient of other public assistance (OWS)",
        "Other public assistance recipient"
      ],
      "Hourly Wage in most recent employment prior to participation": [
        "Hourly wage: pre program (OWS)",
        "Hourly Wage in most recent employment prior to participation"
      ],
      "Hours worked per week most recent employment prior to participation (Only go back 9 months.)": [
        "Hours worked per week most recent employment prior to participation                                                          (Only go back 9 months.)",
        "Hours worked per week most recent employment prior to participation",
        "Hours per week: pre program (OWS)"
      ],
      "Occupational Code of Most Recent Employment Prior to Participation": [
        "Occupational Code of Most Recent Employment Prior to Participation"
      ]

}

four_sheet_personal_information_accepted_responses_w_types = {
    "First Name": {
        "type": "identifier"
    },
    "Last Name": {
        "type": "identifier"
    },
    "CT Hires Username": {
        "type": "identifier"
    },
    "CT Hires State ID #": {
        "type": "stateID7"
    },
    "Submitted Required OWS Forms?": {
        "type": "boolean",
        "required": True
    },
    "Zip Code": {
        "type": "zipCode",
        "required": True
    },
    "Client Date of Birth": {
        "type": "dateTime",
        "required": True
    },
    "Low Income Status at Program Entry?": {
        "type": "boolean"
    },
    "Basic Skills Deficient/Low Levels of Literacy?": {
        "type": "boolean"
    },
    "Single Parent at Program Entry?": {
        "type": "boolean"
    },
    "Co-enrollment (WIOA or WP)": {
        "type": "boolean"
    },
    "Local Workforce Board Code": {
        "type": "identifier"
    },
    "Highest Education Level Completed at Program Entry": {
        "type": "categorical",
        "accepted_responses": {
            "no education level completed": [
                "no education level completed"
            ],
            "attained secondary school diploma": [
                "attained secondary school diploma",
                "attained secondary diploma"
            ],
            "attained a secondary school equivalency": [
                "attained a secondary school equivalency"
            ],
            "completed one or more years of postsecondary education": [
                "completed one or more years of post secondary",
                "completed one or more years of postsecondary education"
            ],
            "attained a bachelor's degree": [
                "attained a bachelor's degree"
            ],
            "attained an associate's degree": [
                "attained an associate's degree"
            ],
            "attained a postsecondary technical or vocational certificate (non-degree)": [
                "attained a postsecondary technical or vocational certificate (non-degree)"
            ],
            "attained a degree beyond a bachelor's degree": [
                "attained a degree beyond a bachelor's degree"
            ]
          }
    },
    "School Status at Program Entry": {
        "type": "categorical",
        "accepted_responses": {
            "not attending school or secondary school dropout": [
                "not attending school or secondary school dropout"
            ],
            "not attending school; within age of compulsory school attendance": [
                "not attending school; within age of compulsory school attendance"
            ],
            "not attending school; secondary school graduate or has a recognized equivalent": [
                "not attending school; secondary school graduate or has a recognized equivalent"
            ],
            "in-school, postsecondary school": [
                "in-school, postsecondary school"
                "in school, postsecondary school"
            ],
            "in-school, alternative school": [
                "in-school, alternative school"
            ],
            "in-school, secondary school or less": [
                "in-school, secondary school or less"
            ]
          }
    },
    "TANF": {
        "type": "boolean"
    },
    "SSI/SSD": {
        "type": "categorical",
        "accepted_responses":["SSI/SSDI",
                              "SSI",
                              "SSDI",
                              "No"]
    },
    "SNAP": {
        "type": "boolean"
    },
    "Other public assistance recipient": {
        "type": "boolean"
    },
    "Hourly Wage in most recent employment prior to participation": {
        "type": "hourlyWage"
    },
    "Hours worked per week most recent employment prior to participation (Only go back 9 months.)": {
        "type": "hoursWorked"
    },
    "Occupational Code of Most Recent Employment Prior to Participation": {
        "type": "ONETCode"
    }
}

four_sheet_training_labels = {
      "First Name": [
        "First Name"
      ],
      "Last Name": [
        "Last Name"
      ],
      "Date of Program Entry (Enrollment Date)": [
        "Program Entry",
        "Date of Program Entry (Enrollment Date)",
        "Date of Program Entry"
      ],
      "Date of Program Exit": [
        "Date of Program Exit",
        "Program Exit"
      ],
      "Received Training?": [
        "Received Training?"
      ],
      "CareerConneCT Training Provider": [
        "CareerConneCT Training Provider"
      ],
      "Date Entered Training": [
        "Date Entered Training (Micro-Credentials)",
        "Date Entered Training"
      ],
      "Type of Training Service": [
        "Type of Training Service"
      ],
      "CareerConneCT Training Provider Program of Study": [
        "CareerConneCT Training Provider Program of Study"
      ],
      "CareerConneCT Training Provider CIP Code": [
        "CareerConneCT Training Provider CIP Code"
      ],
      "Occupational Skills Training Code #1": [
        "Occupational Skills Training Code #1"
      ],
      "Training Completed?": [
        "Training Completed?"
      ],
      "Date Completed or Withdrew From Training #1": [
        "Date Completed or Withdrew From Training #1",
        "Date Completed or Withdrew From Training"
      ],
      "Date Entered Training #2": [
        "Date Entered Training #2"
      ],
      "Type of Training Service #2": [
        "Type of Training Service #2"
      ],
      "Occupational Skills Training Code #2": [
        "Occupational Skills Training Code #2"
      ],
      "Training Completed #2": [
        "Training Completed #2"
      ],
      "Date Completed, or Withdrew from, Training #2": [
        "Date Completed, or Withdrew from, Training #2"
      ],
      "Date Entered Training #3": [
        "Date Entered Training #3"
      ],
      "Type of Training Service #3": [
        "Type of Training Service #3"
      ],
      "Occupational Skills Training Code #3": [
        "Occupational Skills Training Code #3"
      ],
      "Training Completed #3": [
        "Training Completed #3"
      ],
      "Date Completed, or Withdrew from, Training #3": [
        "Date Completed, or Withdrew from, Training #3"
      ],
      "Date Entered Training #4": [
        "Date Entered Training #4"
      ],
      "Type of Training Service #4": [
        "Type of Training Service #4"
      ],
      "Occupational Skills Training Code #4": [
        "Occupational Skills Training Code #4"
      ],
      "Training Completed #4": [
        "Training Completed #4"
      ],
      "Date Completed, or Withdrew from, Training #4": [
        "Date Completed, or Withdrew from, Training #4"
      ]
}

four_sheet_training_accepted_responses_w_types = {
    "First Name": {
        "type": "identifier"
    },
    "Last Name": {
        "type": "identifier"
    },
    "Date of Program Entry (Enrollment Date)": {
        "type": "dateTime"
    },
    "Date of Program Exit": {
        "type": "dateTime"
    },
    "Received Training?": {
        "type": "boolean"
    },
    "CareerConneCT Training Provider": {
        "type": "identifier"
    },
    "Date Entered Training": {
        "type": "dateTime"
    },
    "Type of Training Service": {
        "type": "categorical",
        "accepted_responses": {"customized training":["customized training"],
                               "prerequisite training":["prerequisite training"],
                               "occupational skills training (non-wioa youth)":["occupational skills training (non-wioa youth)","Occupational Skills Building (non-WIOA Youth)"],                               
                               "youth occupational skills training":["youth occupational skills training"],
                               "on the job training (non-wioa youth)":["on the job training (non-wioa youth)"],
                               "skill upgrading":["skill upgrading"]}
    },
    "CareerConneCT Training Provider Program of Study": {
        "type": "categorical",
        "accepted_responses":[
            "a program of study leading to an industry-recognized certificate or certification",
            "a program of study leading to a measurable skills gain",
            "a program of study leading to a certificate of completion of a registered apprenticeship",
            "a program of study leading to a license recognized by the state involved or the federal government",
            "a program of study leading to a community college certificate of completion",
            "a program of study leading to employment"]
    },
    "CareerConneCT Training Provider CIP Code": {
        "type": "CIPCode"
    },
    "Occupational Skills Training Code #1": {
        "type": "ONETCode"
    },
    "Training Completed?": {
        "type": "boolean"
    },
    "Date Completed or Withdrew From Training #1": {
        "type": "dateTime"
    },
    "Date Entered Training #2": {
        "type": "dateTime"
    },
    "Type of Training Service #2": {
        "type": "categorical",
        "accepted_responses": ["customized training",
                               "prerequisite training",
                               "occupational skills training (non-wioa youth)",
                               "youth occupational skills training",
                               "on the job training (non-wioa youth)",
                               "skill upgrading"]
    },
    "Occupational Skills Training Code #2": {
        "type": "ONETCode"
    },
    "Training Completed #2": {
        "type": "boolean"
    },
    "Date Completed, or Withdrew from, Training #2": {
        "type": "dateTime"
    },
    "Date Entered Training #3": {
        "type": "dateTime"
    },
    "Type of Training Service #3": {
        "type": "categorical",
        "accepted_responses": ["customized training",
                               "prerequisite training",
                               "occupational skills training (non-wioa youth)",
                               "youth occupational skills training",
                               "on the job training (non-wioa youth)",
                               "skill upgrading"]
    },
    "Occupational Skills Training Code #3": {
        "type": "ONETCode"
    },
    "Training Completed #3": {
        "type": "boolean"
    },
    "Date Completed, or Withdrew from, Training #3": {
        "type": "dateTime"
    },
    "Date Entered Training #4": {
        "type": "dateTime"
    },
    "Type of Training Service #4": {
        "type": "categorical",
        "accepted_responses": ["customized training",
                               "prerequisite training",
                               "occupational skills training (non-wioa youth)",
                               "youth occupational skills training",
                               "on the job training (non-wioa youth)",
                               "skill upgrading"]
    },
    "Occupational Skills Training Code #4": {
        "type": "ONETCode"
    },
    "Training Completed #4": {
        "type": "boolean"
    },
    "Date Completed, or Withdrew from, Training #4": {
        "type": "dateTime"
    }
}

four_sheet_credential_labels = {
    
      "First Name": [
        "First Name"
      ],
      "Last Name": [
        "Last Name"
      ],
      "Type of Recognized Credential": [
        "Type of Recognized Credential #1",
        "Type of Recognized Credential"
      ],
      "Date Attained Recognized Credential": [
        "Date Finished CNA Training",
        "Date Attained Recognized Credential",
        "Date Attained Recognized Credential #1"
      ],
      "Type of Recognized Credential #2": [
        "Type of Recognized Credential #2",
        "Occupational Certification- CNA License"
      ],
      "Date Attained Recognized Credential #2": [
        "Date Attained Recognized Credential #2"
      ],
      "Type of Recognized Credential #3": [
        "Type of Recognized Credential #3"
      ],
      "Date Attained Recognized Credential #3": [
        "Date Attained Recognized Credential #3"
      ],
      "Type of Recognized Credential #4": [
        "Type of Recognized Credential #4"
      ],
      "Date Attained Recognized Credential #4": [
        "Date Attained Recognized Credential #4"
      ],
      "Type of Recognized Credential #5": [
        "Type of Recognized Credential #5"
      ],
      "Date Attained Recognized Credential #5": [
        "Date Attained Recognized Credential #5"
      ]

}

four_sheet_credential_accepted_responses_w_types = {
    "First Name": {
        "type": "identifier"
    },
    "Last Name": {
        "type": "identifier"
    },
    "Type of Recognized Credential": {
        "type": "categorical",
        "accepted_responses":["occupational certificate",
                              "occupational licensure",
                              "secondary school diploma/or equivalency",
                              "certificate of completion",
                              "industry-recognized credential/certification"]
    },
    "Date Attained Recognized Credential": {
        "type": "dateTime"
    },
    "Type of Recognized Credential #2": {
        "type": "categorical",
        "accepted_responses":["occupational certificate",
                              "occupational licensure",
                              "secondary school diploma/or equivalency",
                              "certificate of completion",
                              "industry-recognized credential/certification"]
    },
    "Date Attained Recognized Credential #2": {
        "type": "dateTime"
    },
    "Type of Recognized Credential #3": {
        "type": "categorical",
        "accepted_responses":["occupational certificate",
                              "occupational licensure",
                              "secondary school diploma/or equivalency",
                              "certificate of completion",
                              "industry-recognized credential/certification"]
    },
    "Date Attained Recognized Credential #3": {
        "type": "dateTime"
    },
    "Type of Recognized Credential #4": {
        "type": "categorical",
        "accepted_responses":["occupational certificate",
                              "occupational licensure",
                              "secondary school diploma/or equivalency",
                              "certificate of completion",
                              "industry-recognized credential/certification"]
    },
    "Date Attained Recognized Credential #4": {
        "type": "dateTime"
    },
    "Type of Recognized Credential #5": {
        "type": "categorical",
        "accepted_responses":["occupational certificate",
                              "occupational licensure",
                              "secondary school diploma/or equivalency",
                              "certificate of completion",
                              "industry-recognized credential/certification"]
    },
    "Date Attained Recognized Credential #5": {
        "type": "dateTime"
    }
}

four_sheet_outcomes_labels = {
      
      "First Name": [
        "First Name"
      ],
      "Last Name": [
        "Last Name"
      ],
      "School Status at Exit": [
        "School Status at Exit"
      ],
      "Employment Status at exit": [
        "Employment Status at exit"
      ],
      "Hourly Wage at Exit": [
        "Hourly Wage at Exit"
      ],
      "Hours Worked per Week": [
        "Hours Worked per Week"
      ],
      "Employer": [
        "Employer"
      ],
      "Job Title": [
        "Job Title"
      ],
      "Employer Zip Code": [
        "Employer Zip Code",
        "Zipcode"
      ],
      "Occupational Code of Employment After Exit": [
        "Occupational Code of Employment After Exit"
      ],
      "Occupational Code of Employment 2nd Quarter After Exit Quarter": [
        "Occupational Code of Employment 2nd Quarter After Exit Quarter"
      ],
      "Occupational Code of Employment 4th Quarter After Exit": [
        "Occupational Code of Employment 4th Quarter After Exit Quarter",
        "Occupational Code of Employment 4th Quarter After Exit"
      ],
      "Employment Related to Training  (2nd Quarter After Exit)": [
        "Employment Related to Training  (2nd Quarter After Exit)"
      ]
}

four_sheet_outcomes_accepted_responses_w_types = {
    "First Name": {
        "type": "identifier"
    },
    "Last Name": {
        "type": "identifier"
    },
    "School Status at Exit": {
        "type": "categorical",
        "accepted_responses":["not attending school or secondary school dropout",
                             "not attending school; secondary school graduate or has a recognized equivalent",
                             "not attending school; within age of compulsory school attendance",
                             "in-school, secondary school or less",
                             "in-school, alternative school",
                             "in-school, postsecondary school",
                             ]
    },
    "Employment Status at exit": {
        "type": "categorical",
        "accepted_responses":["employed; part-time",
                              "employed; full-time",
                              "unemployed",
                              "temporarily employed",
                              "internship",
                              "apprenticeship"]
    },
    "Hourly Wage at Exit": {
        "type": "hourlyWage"
    },
    "Hours Worked per Week": {
        "type": "hoursWorked"
    },
    "Employer": {
        "type": "identifier"
    },
    "Job Title": {
        "type": "identifier"
    },
    "Employer Zip Code": {
        "type": "zipCode"
    },
    "Occupational Code of Employment After Exit": {
        "type": "ONETCode"
    },
    "Occupational Code of Employment 2nd Quarter After Exit Quarter": {
        "type": "ONETCode"
    },
    "Occupational Code of Employment 4th Quarter After Exit": {
        "type": "ONETCode"
    },
    "Employment Related to Training  (2nd Quarter After Exit)": {
        "type": "boolean"
    }
}

workbook_definitions = {

"training data":{
  "simple format": {
  
    "Report":{
    "labels": simple_format_training_data_labels,
    "accepted_responses": simple_format_training_data_accepted_responses_w_types,
    "columns_used": None,
    "starting_row": 0,
    "sheet_name": "Report",
    "starting_column": 0 # zero covers whole df
    }

  },
  "four sheet format": {
      
      "Personal Information":{
          "labels": four_sheet_personal_information_labels,
          "sheet_name": "Personal Information",
          "accepted_responses": four_sheet_personal_information_accepted_responses_w_types,
          "columns_used": None,
          "starting_row": 0,
          "starting_column": 0 # zero covers whole df
      } 
    ,
      "Training": {
          "labels": four_sheet_training_labels,
          "sheet_name": "Training",
          "accepted_responses": four_sheet_training_accepted_responses_w_types,
          "columns_used":None,
          "starting_row": 0,
          "starting_column": 0 # zero covers whole df
    },
    "Credential": {
          "labels": four_sheet_credential_labels,
          "sheet_name": "Credential",
          "accepted_responses": four_sheet_credential_accepted_responses_w_types,
          "columns_used": None,
          "starting_row": 0,
          "starting_column": 0 # zero covers whole df
    },
    "Outcomes": {
          "labels": four_sheet_outcomes_labels,
          "sheet_name": "Outcomes",
          "accepted_responses": four_sheet_outcomes_accepted_responses_w_types,
          "columns_used": None,
          "starting_row": 0,
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