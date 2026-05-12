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
simple_format_portal_data_labels = {  "First Name": [
      "First Name"
    ],
    "Last Name": [
      "Last Name"
    ],
    # "Location": [
    #   "Location"],
    "Zip Code": [
      "Zip/Postal Code"
    ],
    "Client Date of Birth": [
      "Client_Date_Of_Birth_Modified" # Simple Excel macro combining DOB columns and reformatting to consistent date format.
    ],
    # "If you are currently working, what is your hourly wage?": [ # How to handly multiple columns?
    #   "If you are currently working, what is your hourly wage?"
      # "If you are not currently working, what was your hourly wage in your most recent job?" # If we add this I think we need to add code to merge these columns
      # BQ1 has cleanest data but some erroneous annual salary entries. BT1 as well
    # ]
    "Gender": [
      "How do you currently identify your gender?"
    ],
    "Race": [ 
      "Race_Modified" # Macro to separate race and ethnicity from the column "What is your race/ethnicity? (Check all that apply)_Modified" 
    ],
    "Ethnicity": [
        "Ethnicity_Modified" # Macro to separate race and ethnicity from the column "What is your race/ethnicity? (Check all that apply)_Modified" 
    ]
}

simple_format_portal_data_accepted_responses_w_types = {
    'First Name': {'type': 'identifier'},
    'Last Name': {'type': 'identifier'},
    'Zip Code': {'type': 'zipCode'},
    'Client Date of Birth': {'type': 'dateTime'},
    'Gender': {
        'type': 'categorical', 
        'accepted_responses': {
            "Male": [
                    "Hombre",
                    "Homem",
                    "Hommes",
                    "Homme",
                    "Man",
                    "Masculino",
                    "Trans Male",
                    "Transgender man",
                ],
                "Female": [
                    "Mujer",
                    "Femme",             
                    "Woman",
                    "Feminino",
                    "Trans Female",
                    "Transgender woman",
                ],
                "Other": [
                    "Non-Binary",
                    "Non-binary or genderqueer person",
                    "Nonbinary",
                    "Genderqueer",
                    "Prefer to self-describe",
                ],
                "Unknown": [
                    "Prefer not to answer",
                    "Did not disclose",
                    "",                  # empty string
                    None
                ]
            }
    },
    'Race': {
        'type': 'multiCategorical',
        'accepted_responses': {
            "Black": [
                "Black or African American",
                "Noirs ou afro-américains",
                "Negro o afroamericano",
                "Negro ou afro-americano",
            ],
            "White": [
                "White",
                "blanco",
                "Blanc",
            ],
            "Hispanic": [
                "Hispanic",
                "Latino",
                "or Spanish",
                "Hispanic, Latino, or Spanish"
                "Hispano",
                "latino o español",
                "Hispano, latino o español",
                "Hispânicos",
                "latinos ou espanhóis",
                "Hispânicos, latinos ou espanhóis",
                "Hispanique",
                "latino ou espagnol",
                "Hispanique, latino ou espangnol"
            ],
            "Asian": [
                "Asian",
                "asiática",
            ],
            "American Indian": [
                "American Indian or Alaska Native",
            ],
            "Hawaiian/Pacific Islander": [
                "Native Hawaiian or Other Pacific Islander",
                "Nativo de Hawái u otras islas del Pacífico",
            ],
            "Unknown": [
                "Prefer not to answer",
                "Préférez ne pas répondre",
                "DID NOT DISCLOSE",
                "Choose not to answer",
                " ",
                "",                 # empty string
                None
            ],
            "Multi-Racial": []  # Added to canonical so indicators include in multiCategorical column logic
        }
        # 'protected_phrases': [ # These should not be needed now that I already split Race and Ethnicity out. But maybe keep b/c that might be logic worth having in the validation engine.
        #             "Hispanic, Latino, or Spanish",
        #             "Hispano, latino o español",
        #             "Hispânicos, latinos ou espanhóis",
        #             "Hispanique, latino ou espangnol"
        #         ]
    },

    "Ethnicity": {
        'type': 'categorical',
        'accepted_responses': {
            "Hispanic": [
                "Hispanic",
                "Latino",
                "or Spanish",
                "Hispanic, Latino, or Spanish",
                "Hispano",
                "latino o español",
                "Hispano, latino o español",
                "Hispânicos",
                "latinos ou espanhóis",
                "Hispânicos, latinos ou espanhóis",
                "Hispanique",
                "latino ou espagnol",
                "Hispanique, latino ou espangnol",
                "hispanique, latino ou espangnol"
            ],
            "non-Hispanic": [
                "Not Hispanic",
                "non-Hispanic",
                "Non-Hispanic",
                "Not Hispanic or Latino",
                "Non-Hispanic or Latino"
            ],
            "Unknown": [
                "Prefer not to answer",
                "DID NOT DISCLOSE",
                "Choose not to answer",
                " ",
                "",                 # empty string
                None
            ]
        }
        # 'protected_phrases': [ # These should not be needed now that I already split Race and Ethnicity out. But maybe keep b/c that might be logic worth having in the validation engine.
        #             "Hispanic, Latino, or Spanish",
        #             "Hispano, latino o español",
        #             "Hispânicos, latinos ou espanhóis",
        #             "Hispanique, latino ou espangnol"
        #         ]

    }
}

workbook_definitions = {

    "portal data":{
        "simple format": {
        
            "Report":{
            "labels": simple_format_portal_data_labels,
            "accepted_responses": simple_format_portal_data_accepted_responses_w_types,
            "columns_used": None,
            "starting_row": 0,
            "sheet_name": "Report",
            "starting_column": 0 # zero covers whole df
            }
        }
    }
}