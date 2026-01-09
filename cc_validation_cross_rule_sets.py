"""
Rule Definitions for Cross-Sheet Validation
===========================================

This module defines the structured rule sets used by the CrossRuleEngine
to evaluate logical, conditional, and relational dependencies across the
normalized workbook.

Each rule is expressed as a nested "clause tree" describing:

    • which variables the rule applies to (via (sheet, column) tuples)
    • the logical operator to apply (e.g., AND, OR, NOT, IF_THEN)
    • the comparison relationship (e.g., is_blank, connected_presence, before)

Rules are grouped into semantic categories that mirror common data-quality
requirements for CareerConneCT and GJC datasets:

    CONNECTED_PRESENCE_RULES
        Ensure that two or more related fields share consistent blank/non-blank
        status. Used for contexts such as training program fields where the
        existence of one item implies the existence of another.

    CONDITIONALLY_BLANK_UNLESS_RULES
        Identify fields that must remain blank unless a specific prerequisite
        condition is met (e.g., “training received” flags).

    CONDITIONALLY_ALLOWED_RULES
        Ensure that certain fields are *only* allowed when a triggering condition
        is true, preventing spurious or contradictory data entry.

    CONDITIONALLY_REQUIRED_RULES
        Require certain downstream fields to be completed if prerequisite fields
        are filled (e.g., training completion dates when a participant has exited).

    CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES
        Require data fields based on chronological relationships, such as training
        entries that occur before or after fixed program deadlines.

These rule structures are consumed by CrossRuleEngine.expand_rules(), which
automatically resolves grouped “var” or “compare_to” fields and produces
individual atomic rules for evaluation.
"""

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
                    "var": ("Training", "Date of Program Exit"),
                    "op": "is_not_blank"
                },
                {
                    "var": ("Training", "Date of Program Entry (Enrollment Date)"),
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
        "rule_name": "Training fields must be blank when training not received",
        "logic": {
            "IF_THEN": [
                {
                "NOT":{
                    "var": ("Training", "Received Training?"),
                    "op": "equals",
                    "value": 1
                }
                },
                {
                    "var": [
                        ("Training", "CareerConneCT Training Provider"),
                        ("Training", "Date Entered Training"),
                        ("Training", "Type of Training Service"),
                        ("Training", "CareerConneCT Training Provider Program of Study"),
                        ("Training", "CareerConneCT Training Provider CIP Code"),
                        ("Training", "Occupational Skills Training Code #1"),
                        ("Training", "Date Completed or Withdrew From Training #1")
                    ],
                    "op": "is_blank"
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
