# CONNECTED_PRESENCE_RULES = [
#     # Personal Information sheet
#     {"sheet_x": "Personal Information", "col_x": "Hourly Wage in most recent employment prior to participation",
#      "sheet_y": "Personal Information", "col_y": "Hours worked per week most recent employment prior to participation (Only go back 9 months.)"},
#     {"sheet_x": "Personal Information", "col_x": "Hourly Wage in most recent employment prior to participation",
#      "sheet_y": "Personal Information", "col_y": "Occupational Code of Most Recent Employment Prior to Participation"},

#     # Training sheet
#     {"sheet_x": "Training", "col_x": "Date Entered Training #2",
#      "sheet_y": "Training", "col_y": "Type of Training Service #2"},
#     {"sheet_x": "Training", "col_x": "Date Entered Training #2",
#      "sheet_y": "Training", "col_y": "Occupational Skills Training Code #2"},
#     {"sheet_x": "Training", "col_x": "Date Entered Training #3",
#      "sheet_y": "Training", "col_y": "Type of Training Service #3"},
#     {"sheet_x": "Training", "col_x": "Date Entered Training #3",
#      "sheet_y": "Training", "col_y": "Occupational Skills Training Code #3"},
#     {"sheet_x": "Training", "col_x": "Date Entered Training #4",
#      "sheet_y": "Training", "col_y": "Type of Training Service #4"},
#     {"sheet_x": "Training", "col_x": "Date Entered Training #4",
#      "sheet_y": "Training", "col_y": "Occupational Skills Training Code #4"},

#     # Program Entry (from Training) linked to participant context (from Personal Information)
    
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "Low Income Status at Program Entry?"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "Basic Skills Deficient/Low Levels of Literacy?"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "Single Parent at Program Entry?"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "Co-enrollment (WIOA or WP)"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "Local Workforce Board Code"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "Highest Education Level Completed at Program Entry"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "School Status at Program Entry"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "TANF"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "SSI/SSD"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "SNAP"},
#     {"sheet_x": "Training", "col_x": "Date of Program Entry (Enrollment Date)",
#     "sheet_y": "Personal Information", "col_y": "Other public assistance recipient"},
# ]

CONNECTED_PRESENCE_RULES = [

    # ------------------------------------------------------------
    # 🧾 PERSONAL INFORMATION SHEET
    # ------------------------------------------------------------
    {
        "rule_name": "Connected presence: Prior Employment context",
        "logic": {
            "var": [
                ("Personal Information", "Hours worked per week most recent employment prior to participation (Only go back 9 months.)"),
                ("Personal Information", "Occupational Code of Most Recent Employment Prior to Participation")
            ],
            "op": "connected_presence",
            "compare_to": ("Personal Information", "Hourly Wage in most recent employment prior to participation")
        }
    },

    # ------------------------------------------------------------
    # 🧰 TRAINING SHEET – Training #2, #3
    # ------------------------------------------------------------
    {
        "rule_name": "Connected presence: Training #2 context",
        "logic": {
            "var": [
                ("Training", "Type of Training Service #2"),
                ("Training", "Occupational Skills Training Code #2")
            ],
            "op": "connected_presence",
            "compare_to": ("Training", "Date Entered Training #2")
        }
    },
    {
        "rule_name": "Connected presence: Training #3 context",
        "logic": {
            "var": [
                ("Training", "Type of Training Service #3"),
                ("Training", "Occupational Skills Training Code #3")
            ],
            "op": "connected_presence",
            "compare_to": ("Training", "Date Entered Training #3")
        }
    },

    # ------------------------------------------------------------
    # 🧭 CROSS-SHEET LINK – Enrollment ↔ Entry Context
    # ------------------------------------------------------------
    {
        "rule_name": "Connected presence: Enrollment Date ↔ Entry Context Fields",
        "logic": {
            "var": [
                ("Personal Information", "Low Income Status at Program Entry?"),
                ("Personal Information", "Basic Skills Deficient/Low Levels of Literacy?"),
                ("Personal Information", "Single Parent at Program Entry?"),
                ("Personal Information", "Co-enrollment (WIOA or WP)"),
                ("Personal Information", "Local Workforce Board Code"),
                ("Personal Information", "Highest Education Level Completed at Program Entry"),
                ("Personal Information", "School Status at Program Entry"),
                ("Personal Information", "TANF"),
                ("Personal Information", "SSI/SSD"),
                ("Personal Information", "SNAP"),
                ("Personal Information", "Other public assistance recipient")
            ],
            "op": "connected_presence",
            "compare_to": ("Training", "Date of Program Entry (Enrollment Date)")
        }
    },
]



# CONDITIONALLY_BLANK_UNLESS_RULES = [
        
#     ## Training received  
#         {
#         "if_pair": ["Training", "Received Training?"],
#         "then_pairs": [
#             ["Training", "CareerConneCT Training Provider"],
#             ["Training", "Date Entered Training"],
#             ["Training", "Type of Training Service"],
#             ["Training", "CareerConneCT Training Provider Program of Study"],
#             ["Training", "CareerConneCT Training Provider CIP Code"],
#             ["Training", "Occupational Skills Training Code #1"],
#             ["Training", "Date Completed or Withdrew From Training #1"]
#         ],
#         "trigger_values": ["1"]
#     },

#     ## Date of program entry 
#         {
#         "if_pair": ["Training", "Date of Program Entry (Enrollment Date)"],
#         "then_pairs": [
#             ["Training", "Date of Program Exit"],
#             ["Training", "Received Training?"]
#         ],
#         "trigger_values": ["__NOT_BLANK__"]
#     },

#     ## 
#     {
#     }
# ]
CONDITIONALLY_BLANK_UNLESS_RULES = [

    # ------------------------------------------------------------
    # 🎓 Training received → related fields conditionally blank
    # ------------------------------------------------------------
    {
        "rule_name": "Training received → related fields conditionally blank",
        "logic": {
            "IF_THEN": [
               {
                    "var": [("Training", "CareerConneCT Training Provider"),
                        ("Training", "Date Entered Training"),
                        ("Training", "Type of Training Service"),
                        ("Training", "CareerConneCT Training Provider Program of Study"),
                        ("Training", "CareerConneCT Training Provider CIP Code"),
                        ("Training", "Occupational Skills Training Code #1"),
                        ("Training", "Date Completed or Withdrew From Training #1")
                    ] ,
                    "op": "is_not_blank"
                },                
                {
                    "var": ("Training", "Received Training?"),
                    "op": "equals",
                    "value": 1
                }

            ]
        }
    },

    # ------------------------------------------------------------
    # 🧭 Program entry → exit or received training consistency
    # ------------------------------------------------------------
    {
        "rule_name": "Program entry → exit or received training consistency",
        "logic": {
            "IF_THEN": [
                {
                    "var": ("Training", "Date of Program Entry (Enrollment Date)"),
                    "op": "is_not_blank"
                },
                {
                    "var": ("Training", "Date of Program Exit"),
                    "op": "is_not_blank",
                    "compare_to": [
                        ("Training", "Received Training?")
                    ]
                }
            ]
        }
    },
]

CONDITIONALLY_ALLOWED_RULES = [

    # ------------------------------------------------------------
    # 🧾 Training fields conditionally allowed when training received
    # ------------------------------------------------------------
    {
        "rule_name": "Training fields conditionally allowed when training received",
        "logic": {
            "IF_THEN": [

                {
                    "var": [("Training", "CareerConneCT Training Provider"),
                        ("Training", "Date Entered Training"),
                        ("Training", "Type of Training Service"),
                        ("Training", "CareerConneCT Training Provider Program of Study"),
                        ("Training", "CareerConneCT Training Provider CIP Code"),
                        ("Training", "Occupational Skills Training Code #1"),
                        ("Training", "Date Completed or Withdrew From Training #1")
                    ],
                    "op": "is_blank"
                },
                {
                    "NOT": [
                        {
                            "var": ("Training", "Received Training?"),
                            "op": "equals",
                            "value": 1
                        }
                    ]
                }
            ]
        }
    }
]



CONDITIONALLY_REQUIRED_RULES = [

{
    "rule_name": "Completion required for Training #1 when exited and entered",
    "logic": {
        "IF_THEN": [
            {
                "AND": [
                    {"var": ("Training", "Date of Program Exit"), "op": "is_not_blank"},
                    {"var": ("Training", "Date Entered Training"), "op": "is_not_blank"}
                ]
            },
            {
                "var": ("Training", "Date Completed or Withdrew From Training #1"),
                "op": "is_not_blank"
            }
        ]
    }
},
{
    "rule_name": "Completion required for Training #2 when exited and entered",
    "logic": {
        "IF_THEN": [
            {
                "AND": [
                    {"var": ("Training", "Date of Program Exit"), "op": "is_not_blank"},
                    {"var": ("Training", "Date Entered Training #2"), "op": "is_not_blank"}
                ]
            },
            {
                "var": ("Training", "Date Completed, or Withdrew from, Training #2"),
                "op": "is_not_blank"
            }
        ]
    }
},
{
    "rule_name": "Completion required for Training #3 when exited and entered",
    "logic": {
        "IF_THEN": [
            {
                "AND": [
                    {"var": ("Training", "Date of Program Exit"), "op": "is_not_blank"},
                    {"var": ("Training", "Date Entered Training #3"), "op": "is_not_blank"}
                ]
            },
            {
                "var": ("Training", "Date Completed, or Withdrew from, Training #3"),
                "op": "is_not_blank"
            }
        ]
    }
} #,
# {
#     "rule_name": "Completion required for Training #4 when exited and entered",
#     "logic": {
#         "IF_THEN": [
#             {
#                 "AND": [
#                     {"var": ("Training", "Date of Program Exit"), "op": "is_not_blank"},
#                     {"var": ("Training", "Date Entered Training #4"), "op": "is_not_blank"}
#                 ]
#             },
#             {
#                 "var": ("Training", "Date Completed, or Withdrew from, Training #4"),
#                 "op": "is_not_blank"
#             }
#         ]
#     }
# }

]

CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES = [

    # ------------------------------------------------------------
    # 🗓️ Training End Date → must precede Reference Date
    # ------------------------------------------------------------
    {
        "rule_name": "Training end date before reference date → completion and exit statuses required",
        "logic": {
            "IF_THEN": [
                {
                    "var": ("Training", "Date of Program Exit"),
                    "op": "before",
                    "value": "2025-09-30"  # static reference date
                },
                {
                    "var":  [("Outcomes", "Employment Status at exit"),
                        ("Outcomes", "School Status at Exit")],
                    "op": "is_not_blank"
                }
            ]
        }
    }
]
