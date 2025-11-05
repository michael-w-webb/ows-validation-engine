CONNECTED_PRESENCE_RULES = [
    # Personal Information sheet
    {"sheet_x": "Personal Information", "col_x": "Hourly Wage in most recent employment prior to participation",
     "sheet_y": "Personal Information", "col_y": "Hours worked per week most recent employment prior to participation (Only go back 9 months.)"},
    {"sheet_x": "Personal Information", "col_x": "Hourly Wage in most recent employment prior to participation",
     "sheet_y": "Personal Information", "col_y": "Occupational Code of Most Recent Employment Prior to Participation"},

    # Training sheet
    {"sheet_x": "Training", "col_x": "Date Entered Training #2",
     "sheet_y": "Training", "col_y": "Type of Training Service #2"},
    {"sheet_x": "Training", "col_x": "Date Entered Training #2",
     "sheet_y": "Training", "col_y": "Occupational Skills Training Code #2"},
    {"sheet_x": "Training", "col_x": "Date Entered Training #3",
     "sheet_y": "Training", "col_y": "Type of Training Service #3"},
    {"sheet_x": "Training", "col_x": "Date Entered Training #3",
     "sheet_y": "Training", "col_y": "Occupational Skills Training Code #3"},
    {"sheet_x": "Training", "col_x": "Date Entered Training #4",
     "sheet_y": "Training", "col_y": "Type of Training Service #4"},
    {"sheet_x": "Training", "col_x": "Date Entered Training #4",
     "sheet_y": "Training", "col_y": "Occupational Skills Training Code #4"},

    # Program Entry (from Training) linked to participant context (from Personal Information)
    
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "Low Income Status at Program Entry?"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "Basic Skills Deficient/Low Levels of Literacy?"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "Single Parent at Program Entry?"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "Co-enrollment (WIOA or WP)"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "Local Workforce Board Code"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "Highest Education Level Completed at Program Entry"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "School Status at Program Entry"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "TANF"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "SSI/SSD"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "SNAP"},
    {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
    "sheet_y": "Personal Information", "col_y": "Other public assistance recipient"},
]


CONDITIONALLY_BLANK_UNLESS_RULES = [
        
    ## Training received  
        {
        "if_pair": ["Training", "Received Training?"],
        "then_pairs": [
            ["Training", "CareerConneCT Training Provider"],
            ["Training", "Date Entered Training"],
            ["Training", "Type of Training Service"],
            ["Training", "CareerConneCT Training Provider Program of Study"],
            ["Training", "CareerConneCT Training Provider CIP Code"],
            ["Training", "Occupational Skills Training Code #1"],
            ["Training", "Date Completed or Withdrew From Training #1"]
        ],
        "trigger_values": ["1"]
    },

    ## Date of program entry 
        {
        "if_pair": ["Training", "Date of Program Entry (Enrollment Date)"],
        "then_pairs": [
            ["Training", "Date of Program Exit"],
            ["Training", "Received Training?"]
        ],
        "trigger_values": ["__NOT_BLANK__"]
    },

    ## 
    {
        


    }
]

CONDITIONALLY_ALLOWED_RULES = [
    {"sheet_x": "Training", "col_x": "Received Training?",
     "sheet_y": "Training", "col_y": "CareerConneCT Training Provider", "trigger_values": ["1"]},
    {"sheet_x": "Training", "col_x": "Received Training?",
     "sheet_y": "Training", "col_y": "Date Entered Training", "trigger_values": ["1"]},
    {"sheet_x": "Training", "col_x": "Received Training?",
     "sheet_y": "Training", "col_y": "Type of Training Service", "trigger_values": ["1"]},
    {"sheet_x": "Training", "col_x": "Received Training?",
     "sheet_y": "Training", "col_y": "CareerConneCT Training Provider Program of Study", "trigger_values": ["1"]},
    {"sheet_x": "Training", "col_x": "Received Training?",
     "sheet_y": "Training", "col_y": "CareerConneCT Training Provider CIP Code", "trigger_values": ["1"]},
    {"sheet_x": "Training", "col_x": "Received Training?",
     "sheet_y": "Training", "col_y": "Occupational Skills Training Code #1", "trigger_values": ["1"]},
    {"sheet_x": "Training", "col_x": "Received Training?",
     "sheet_y": "Training", "col_y": "Date Completed or Withdrew From Training #1", "trigger_values": ["1"]},
]

CONDITIONALLY_REQUIRED_RULES = [
    {
        "if_pairs": [
            ("Training", "Date of Program Exit"),
            ("Training", "Date Entered Training"),
        ],
        "then_pairs": [
            ("Training", "Date Completed or Withdrew From Training #1"),
        ],
    },
    {
        "if_pairs": [
            ("Training", "Date of Program Exit"),
            ("Training", "Date Entered Training #2"),
        ],
        "then_pairs": [
            ("Training", "Date Completed, or Withdrew from, Training #2"),
        ],
    },
    {
        "if_pairs": [
            ("Training", "Date of Program Exit"),
            ("Training", "Date Entered Training #3"),
        ],
        "then_pairs": [
            ("Training", "Date Completed, or Withdrew from, Training #3"),
        ],
    },
    {
        "if_pairs": [
            ("Training", "Date of Program Exit"),
            ("Training", "Date Entered Training #4"),
        ],
        "then_pairs": [
            ("Training", "Date Completed, or Withdrew from, Training #4"),
        ],
    },
]

CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES = [
    {
        "if_pairs": [
            [("Program_Enrollment", "Training End Date"),]   # use a dummy sheet or static reference date
        ],
        "then_pairs": [
            ("Program_Enrollment", "Training Completion Status"),
            ("Employment", "Employment Status"),
            ("Employment", "School Status at Exit"),
        ],
        "relation": "before",
        "reference_date": "2025-09-30"  # optional override if not using a sheet
    }
]