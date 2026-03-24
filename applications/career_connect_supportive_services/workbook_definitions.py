MAX_EXPENSES = 75

simple_format_training_data_labels = {

    "First Name": ["First Name"],

    "Last Name": ["Last Name"],

    "CT Hires Username": [
        "CT Hires Username",
        "CTH State ID",
        "CTHires_Username"
    ],

    "Zip Code": ["Zip Code", "ZIP"],

    "Program Sector": ["Program Sector"]
}

for i in range(1, MAX_EXPENSES + 1):

    simple_format_training_data_labels[f"Category of Support {i}"] = [
        f"Category of Support {i}",
        f"Category_{i}"
    ]

    simple_format_training_data_labels[f"Specific Use of Funds {i}"] = [
        f"Specific Use of Funds {i}",
        f"Use_{i}"
    ]

    simple_format_training_data_labels[f"Dollar Amount ($) {i}"] = [
        f"Dollar Amount ($) {i}",
        f"Dollar Amount {i}",
        f"Dollar_{i}"
    ]
    
simple_format_training_data_accepted_responses_w_types = {

    "First Name": {"type": "identifier", "required": True},
    "Last Name": {"type": "identifier", "required": True},
    "CT Hires Username": {"type": "identifier"},
    "Zip Code": {"type": "zipCode", "required": True},
    "Program Sector": {"type": "identifier"}
}

for i in range(1, MAX_EXPENSES + 1):

    simple_format_training_data_accepted_responses_w_types[f"Category of Support {i}"] = {
        "type": "identifier",
        "required": True
    }

    simple_format_training_data_accepted_responses_w_types[f"Specific Use of Funds {i}"] = {
        "type": "identifier"
    }

    simple_format_training_data_accepted_responses_w_types[f"Dollar Amount ($) {i}"] = {
        "type": "hourlyWage",
        "required": True,
        "max_wage": 100000
    }

workbook_definitions = {
"cc_supportive_services":{
  "simple format": {
  
    "Aggregate Report":{
    "labels": simple_format_training_data_labels,
    "accepted_responses": simple_format_training_data_accepted_responses_w_types,
    "columns_used": None,
    "sheet_name": "Aggregate Report",
    "starting_column": 0 # zero covers whole df
    }
  }
}
}