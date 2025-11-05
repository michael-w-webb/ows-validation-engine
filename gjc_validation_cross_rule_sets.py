CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES = [
    {
        "if_pairs": [
            ("Program_Enrollment", "Training End Date")   # use a dummy sheet or static reference date
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

CONDITIONALLY_REQUIRED_RULES = [
    
    ### required if training completion status 
    {
        "if_pairs": [
            ("Program_Enrollment", "Training Completion Status"),
        ],
        "then_pairs": [
            ("Program_Enrollment", "Non-Completion Exit Reason"),
        ],
        "trigger_values": [
            "Did not complete training (please code exit reason)"
        ]
    },
    ### required if job start date
    {
        "if_pairs": [
            ("Employment", "Job Start Date"),
        ],
        "then_pairs": [
            ("Employment", "Employment Type"),
            ("Employment", "Employer"),
            ("Employment", "Employer Zip Code"),
            ("Employment", "If employed, did participant report hourly salary?"),
            ("Employment", "Occupation (NAICS) code"),
        ]
    }
]

CONNECTED_PRESENCE_RULES = []

CONDITIONALLY_ALLOWED_RULES = []

CONDITIONALLY_BLANK_RULES = []
