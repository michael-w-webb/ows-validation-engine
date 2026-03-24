CONDITIONALLY_REQUIRED_BY_DATE_COMPARISON_RULES = [

    {
        "rule_name": (
            "Training end date before 2025-12-31 → "
            "completion and exit statuses required"
        ),
        "logic": {
            "IF_THEN": [
                {
                    "var": ("Program_Enrollment", "Training End Date"),
                    "op": "before",
                    "value": "2025-12-31"
                },
                {
                    "var": [
                        ("Program_Enrollment", "Training Completion Status"),
                        ("Employment", "Employment Status"),
                        ("Employment", "School Status at Exit"),
                    ],
                    "op": "is_not_blank"
                }
            ]
        }
    }

]


CONDITIONALLY_REQUIRED_RULES = [

    {
        "rule_name": (
            "Non-completion reason required when training not completed"
        ),
        "logic": {
            "IF_THEN": [
                {
                    "var": ("Program_Enrollment", "Training Completion Status"),
                    "op": "equals",
                    "value": "Did not complete training (please code exit reason)"
                },
                {
                    "var": ("Program_Enrollment", "Non-Completion Exit Reason"),
                    "op": "is_not_blank"
                }
            ]
        }
    },

    {
        "rule_name": (
            "Employment details required when employment status indicates employed"
        ),
        "logic": {
            "IF_THEN": [
                {
                    "var": ("Employment", "Employment Status"),
                    "op": "in",
                    "values": [
                        "Employed in-field by an employer who partners with your training program",
                        "Employed in-field by an employer who doesn't partner with your training program",
                        "Employed out of field",
                        "Employed not in-field",
                        "Employed in-field",
                    ],
                    "language_substitute": "an employment status indicating the participant is employed"
                },
                {
                    "var": [
                        ("Employment", "Job Start Date"),
                        ("Employment", "Employment Type"),
                        ("Employment", "Employer"),
                        ("Employment", "Employer Zip Code"),
                        ("Employment", "If employed, did participant report hourly salary?"),
                        ("Employment", "Occupation (NAICS) code"),
                    ],
                    "op": "is_not_blank"
                }
            ]
        }
    },


    {
    "rule_name": (
        "Hourly earnings required when participant reports hourly salary"
    ),
    "logic": {
        "IF_THEN": [
            {
                "var": (
                    "Employment",
                    "If employed, did participant report hourly salary?"
                ),
                "op": "equals",
                "value": 1
            },
            {
                "var": ("Employment", "Hourly Earnings"),
                "op": "is_not_blank"
            }
        ]
    }
},

{
    "rule_name": (
        "Earn and Learn type required when employment type is Earn and Learn"
    ),
    "logic": {
        "IF_THEN": [
            {
                "var": ("Employment", "Employment Type"),
                "op": "equals",
                "value": "Earn and Learn employment"
            },
            {
                "var": ("Employment", "If earn and learn, type"),
                "op": "is_not_blank"
            }
        ]
    }
}


]

CONNECTED_PRESENCE_RULES = []

CONDITIONALLY_ALLOWED_RULES = []

CONDITIONALLY_BLANK_RULES = []
