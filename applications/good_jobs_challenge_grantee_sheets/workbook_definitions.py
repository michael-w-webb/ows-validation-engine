
### this doc stors column label lists for reference in other functions 

#### GJC Training Provider Instrument 

training_provider_database_labels = [
    "Training Provider",  # 1
    "Training Program"    # 2
]

training_provider_database_accepted_responses = {
    "Training Provider": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Program": {
        "limited_response": False,
        "accepted_responses": []
    }
}

training_provider_database_accepted_responses_w_types = {
    "Training Provider": {
        "type":"identifier",
        "accepted_responses": []
    },
    "Training Program": {
        "type":"identifier",
        "accepted_responses": []
    }
}


institutional_information_labels = {
    "Training Provider Name": [
        "Training Provider Name"
    ],
    "Training Program Name": [
        "Training Program Name"
    ],
    "Length of Program": [
        "Length of Program"
    ],
    "Environment Type": [
        "Environment Type"
    ],
    "Program Hours": [
        "Program Hours"
    ],
    "Does your training program include soft skills training?": [
        "Does your training program include soft skills training?"
    ],
    "Program Tuition Cost (actual cost)": [
        "Program Tuition Cost (actual cost)"
    ]
}

institutional_information_accepted_responses = {
    "Training Provider": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Program": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Length of Program": {
        "limited_response": True,
        "accepted_responses": [
            "Less than 3 months",
            "3 - 6 months",
            "7 - 12 months",
            "13 - 24 months",
            "25 - 36 months",
            "37 - 48 months"
        ]
    },
    "Environment Type": {
        "limited_response": True,
        "accepted_responses": [
            "In-person",
            "Hybrid in-person and remote",
            "Permanently remote",
            "Remote only due to Covid"
        ]
    },
    "Program Hours": {
        "limited_response": True,
        "accepted_responses": [
            "Full time program",
            "Part time program",
            "Program has the option to take breaks and return"
        ]
    },
    "Soft skills?": {
        "limited_response": True,
        "accepted_responses": [
            "Yes",
            "No"
        ]
    },
    "Tuition Cost": {
        "limited_response": False,
        "accepted_responses": []
    }
}

institutional_information_accepted_responses_w_types = {
    "Training Provider Name": {
        "type": "fileSpecificCategorical",
        "accepted_responses": {
        "NRWIB_MFG": {
            "Manufacturing Alliance Service Corporation": [
                "manufacturing alliance service corporation",
                "manufacturing alliance sevice corporation (masc)",
                "masc"
            ]
        },
        "BRBC": {
            "Academy at Coffee Project": ["academy at coffee project"],
            "University of Bridgeport/Goodwin": ["university of bridgeport/goodwin"],
            "CT State - Housatonic/Platt Technical High School": [
                "ct state - housatonic/platt technical high school"
            ],
            "Southern Connecticut University": ["southern connecticut university"],
            "CT State - Housatonic at Housatonic": ["ct state - housatonic at housatonic"],
            "MATCH": ["match"],
            "CT State - Norwalk": ["ct state - norwalk"]
        },
        "CWP": {
            "Marrakech, Inc.": ["marrakech, inc."],
            "National Institute for Medical Assistant Advancement - NIMAA": [
                "national institute for medical assistant advancement - nimaa"
            ],
            "Charter Oak State College": ["charter oak state college"],
            "Northeast Medical Institute": ["northeast medical institute"],
            "CT State - Capital Campus": ["ct state community college - capital campus"],
            "CT State - Tunxis Campus": ["ct state community college - tunxis campus"],
            "Career Resource Inc. - Strive": [
                "strive connecticut - career resources, inc."
            ],
            "JobWorks": ["jobworks"],
            "DCI Resources": ["dci resources"]
        },
        "EWIB_MFG": {
            "Bacon Academy": ["bacon academy"],
            "EO Smith High School": ["eo smith high school"],
            "Griswold High School": ["griswold high school"],
            "RHAM High School": ["rham high school"],
            "Norwich Free Academy (NFA)": ["norwich free academy (nfa)"],
            "Stonington High School": ["stonington high school"],
            "Tourtellotte Memorial High School": ["tourtellotte memorial high school"],
            "Woodstock Academy": ["woodstock academy"],
            "Putnam High School": ["putnam high school"],
            "New London High School": ["new london high school"],
            "CT STATE Three Rivers": ["ct state three rivers"],
            "Community College Rhode Island": ["community college rhode island"],
            "Lyman Memorial High School": ["lyman memorial high school"],
            "Windham High School": ["windham high school"],
            "Parish Hill High School": ["parish hill"]
        },
        "EWIB_HC": {
            "CT State Community College - Quinebaug Valley": [
                "ct state community college - quinebaug valley"
            ],
            "American Professional Educational Services": [
                "american professional educational services"
            ],
            "New London Adult and Continuing Education": [
                "new london adult and continuing education"
            ],
            "CNA Bootcamp of CT": ["cna bootcamp of ct"],
            "Health Education Center, Inc.": ["health education center, inc."],
            "CT State Community College - Three Rivers": [
                "ct state community college - three rivers"
            ],
            "East Lyme High School": ["east lyme high school"],
            "Robert E. Fitch High School": ["robert e. fitch high school"],
            "Griswold High School": ["griswold high school"],
            "CT State Community College - Asnuntuck": [
                "ct state community college - asnuntuck"
            ],
            "Killingly High School": ["killingly high school"],
            "Stonington High School": ["stonington high school"],
            "Windham High School": ["windham high school"],
            "New London High School": ["new london high school"],
            "Norwich Free Academy (NFA)": ["norwich free academy (nfa)"],
            "Lyman Memorial High School": ["lyman memorial high school"],
            "Tourtellotte Memorial High School": ["tourtellotte memorial high school"],
            "Woodstock Academy": ["woodstock academy"]
        },
        "GNHCC": {
            "Connecticut Center for Arts and Technology": [
                "connecticut center for arts and technology"
            ],
            "Greater New Haven Chamber of Commerce": [
                "greater new haven chamber of commerce"
            ],
            "Connecticut Center for Arts and Technology & Greater New Haven Chamber of Commerce": [
                "connecticut center for arts and technology & greater new haven chamber of commerce"
            ],
            "Northeast Medical Institute": ["northeast medical institute"],
            "Southern Connecticut State University": ["southern connecticut state university"],
            "Excel Academy": ["excel academy"]
        },
        "TWP": {
            "Southern Connecticut State University": ["southern connecticut state university"],
            "Housatonic Community College": ["housatonic community college"],
            "DCI Resources": ["dci", "dci resources"]
        },
        "WFA": {
            "Manufacturing and Technology Community Hub": [
                "match",
                "manufacturing and technology community hub",
                "manufacturing and technical community hub (match)"
            ],
            "CT State - Middlesex": ["ctstate-middlesex"]
        },
        "NRWIB_HC": {
            "Griffin Health": ["griffin hospital school of allied heath careers"],
            "Northeast Medical Institute": ["northeast medical institute"],
            "Academy of Medical Training, Inc.": ["academy of medical training, inc."],
            "Northwestern Connecticut Community College": [
                "northwestern connecticut community college"
            ],
            "Hispanic Coalition of Greater Waterbury": [
                "hispanic coalition of greater waterbury"
            ]
        }
    },
        "required": True
    },
    "Training Program Name": {
    "type": "fileSpecificCategorical",
    "accepted_responses": {
        "NRWIB_MFG": {
            "CNC Entry Level": ["cnc entry level"],
            "Introduction to Plastics": [
                "introduction to plastics",
                "introduction to plastic injection molding"
            ],
            "MASTERCAM/CNC II": ["mastercam/cnc ii"],
            "MFG Machinist": ["mfg machinist"],
            "Apprenticeship Training": ["apprenticeship training"],
            "Fundamentals of Manufacturing": [
                "fundamentals of manufacturing",
                "fundamentals of mfg technology"
            ]
        },
        "BRBC": {
            "SCA Roasting Skills Beginner & Intermediate Bundle": [
                "sca roasting skills beginner & intermediate bundle"
            ],
            "Module 1: Welding Safety": ["module 1: welding safety"],
            "Basic Welding Credential Training": [
                "basic welding credential training"
            ],
            "CNC Level 1": ["cnc level 1"],
            "Intro to Manufacturing": ["intro to manufacturing"],
            "Intro to Manufacturing (HCC)": [
                "intro to manufacturing (hcc)",
                "intro to manufacturing"
            ],
            "Certified Manufacturing Associate": [
                "certified manufacturing associate"
            ],
            "Metrology Technologies": ["metrology technologies"],
            "SolidWorks": ["solidworks"],
            "AI Fundamentals for Workplace Success": [
                "ai fundamentals for workplace success"
            ],
            "Manufacturing Essentials": ["manufacturing essentials"],
            "Optic Fabrication and Metrology": [
                "optic fabrication and metrology"
            ],
            "Swiss CNC Level 1": ["swiss cnc level 1"],
            "Multi-Disciplinary Manufacturing Pre-Apprenticeship": [
                "multi-disciplinary manufacturing pre-apprenticeship"]
        },
        "CWP": {
            # Health programs
            "Direct Support Specialist": ["direct support specialist"],
            "Medical Assistant": ["medical assistant"],
            "Revenue Cycle Management": ["revenue cycle management"],
            "Certified Nurses Aide": ["certified nurse aide/assistant"],
            "Patient Care Technician": ["patient care technician"],
            "Pharmacy Technician": ["pharmacy technician"],
            "Central Sterile Processing Technician": [
                "central sterile processing technician",
                "certified sterile processing technician"

            ],
            "Career Training": [
                "strive (support and training result in valuable employees)"
            ],
            # Tech programs
            "TechWorks": ["techworks"],
            "Business Analyst": ["business analyst"],
            "Cloud Network Specialist": ["cloud network specialist"],
            "Cloud Tech Specialist": ["cloud tech specialist"],
            "Cybersecurity Specialist": ["cybersecurity specialist"],
            "Full Stack Developer": ["full stack developer"],
            "Help Desk Analyst": ["help desk analyst"]
        },
        "EWIB_MFG": {
            "YMPI": ["ympi"],
            "Design": ["design"],
            "Electrical": ["electrical"],
            "Inside Machinist": ["inside machinist"],
            "Painter": ["painter"],
            "Outside Machinist": ["outside machinist"],
            "Pipefitter": ["pipefitter"],
            "Shipfitter": ["shipfitter"],
            "Sheetmetal": ["sheetmetal"],
            "Welding": ["welding"]
        },
        "EWIB_HC": {
            "Certified Nursing Assistant (CNA)": [
                "certified nursing assistant (cna)",
                "certified nursing assistant (cna) - high school"
            ],
            "Emergency Medical Technician (EMT)": [
                "emergency medical technician (emt)"
            ],
            "Medical Interpreter": ["medical interpreter"],
            "Medical Billing & Coding": ["medical billing & coding"],
            "Pharmacy Technician": ["pharmacy technician"],
            "Phlebotomy": ["phlebotomy"],
            "EKG Technician": ["ekg technician"],
            "Community Health Worker (CHW)": ["community health worker (chw)"],
            "Sterile Processing Technician": ["sterile processing technician"],
            "Medical Assistant": ["medical assistant"],
            "Dental Assistant": ["dental assistant"]
        },
        "GNHCC": {
            "BioLaunch Basic Training Program": ["biolaunch basic training program"],
            "Professional Skills Program": ["professional skills program", 
                                            "professional skills training program"],
            "BioLaunch Basic Training Program & Professional Skills Program": [
                "biolaunch basic training program & professional skills program",
                "biolaunch basic training program professional skills training"
            ],
            "BioLaunch Advanced Training Program": ["biolaunch advanced training program"],
            "Patient Care Technician": ["patient care technician training program"],
            "Phlebotomy": ["phlebotomy"],
            "Certified Nurses Aide":["cna training program",
                                     "cna training program (8 week)",
                                     "cna training program (11 week)"]
        },
        "TWP": {
            "Generative AI": ["generative ai"],
            "Comp TIA A+": ["comp tia a+"],
            "Comp TIA Security +": ["comp tia security +", "comp tia seurity +"],
            "AWS Cloud Practitioner": ["aws cloud practitioner"],
            "AWS Solutions Architect": ["aws solutions architect"],
            "Project Management": ["project management", "project mangement"],
            "Google Cybersecurity": ["google cybersecurity"],
            "Google Project Management": ["google project management"],
            "CMMC": ["cmmc"],
            "Python I": ["python i", "python 1"],
            "Python II": ["python ii"],
            "SQL": ["sql"]
        },
        "WFA": {
            "Machinist Pre-Apprenticeship": [
                "machinist pre-apprenticeship",
                "manufacturing pre-apprenticeship"
            ],
            "Manufacturing Administration": ["manufacturing administration"],
            "Forklift & Material Handling": ["forklift & material handling"]
        },
        "NRWIB_HC": {
            "Clinical Medical Assistant": [
                "clinical medical assistant",
                "medical assistant"
            ],
            "Certified EKG Technician": [
                "certified ekg technician",
                "ekg",
                "ekg technician"
            ],
            "Pharmacy Technician": [
                "pharmacy tech",
                "pharmacy technician"
            ],
            "Certified Nurses Aide": [
                "certified nurses aide",
                "cna/cpt"
            ],
            "Phlebotomy Technician": [
                "phlebotomy technician",
                "certified phlebotomy technician"
            ],
            "Patient Care Technician": ["certified patient care technician", "patient care technician","EKG Technician and Phlebotomy Technician & PCT Exam","Certified Nurses Aide and EKG Technician& PCT exam"],
            "CPT & EKG Technician": ["cpt & ekg technician"],
            "EKG Technician and Phlebotomy Technician":["EKG Technician and Phlebotomy Technician"],
            "CNA and Phlebotomy Technician": ["CNA/Phlebotomy","Certified Nurses Aide and Phlebotomy Technician"],
            "CNA and EKG Technician": ["certified nurses aide and ekg technician"],
            "CEntral Sterile Processing Technician": ["central sterile processing"],
            "Emergency Medical Technician (EMT)": [
                "emergency medical tech"
            ]
        }
    },
        "required": True
},
     "Length of Program": {
        "type": "categorical",
        "accepted_responses": [
            "Less than 3 months",
            "3 - 6 months",
            "7 - 12 months",
            "13 - 24 months",
            "25 - 36 months",
            "37 - 48 months"
        ]
    },
    "Environment Type": {
        "type": "categorical",
        "accepted_responses": [
            "In-person",
            "Hybrid in-person and remote",
            "Permanently remote",
            "Remote only due to Covid"
        ]
    },
    "Program Hours": {
        "type": "categorical",
        "accepted_responses": [
            "Full time program",
            "Part time program",
            "Program has the option to take breaks and return"
        ]
    },
    "Does your training program include soft skills training?": {
        "type": "categorical",
        "accepted_responses": ["Yes", "No"]
    },
    "Program Tuition Cost (actual cost)": {
        "type": "hourlyWage",
        "accepted_responses": []
    }
}



participant_info_labels = {
    "First Name": [
        "First Name"
    ],
    "Middle Name": [
        "Middle Name"
    ],
    "Last Name": [
        "Last Name"
    ],
    "CTHires Username or State ID #": [
        "CTHires Username or State ID #"
    ],
    "Date of Birth": [
        "Date of Birth"
    ],
    "Street Address 1": [
        "Street Address 1"
    ],
    "Street Address 2 (apt, etc)": [
        "Street Address 2 (apt, etc)"
    ],
    "City": [
        "City"
    ],
    "State": [
        "State"
    ],
    "Zip Code": [
        "Zip Code"
    ],
    "Highest Education Level Obtained": [
        "Highest Education Level Obtained"
    ],
    "School Status at Program Entry": [
        "School Status at Program Entry"
    ],
    "Low Income Status": [
        "Low Income Status"
    ],
    "Basic Skills Deficient": [
        "Basic Skills Deficient"
    ],
    "Single Parent at Program Entry": [
        "Single Parent at Program Entry"
    ],
    "Co-Enrollment (WIOA or WP)": [
        "Co-Enrollment (WIOA or WP)"
    ],
    "TANF": [
        "TANF"
    ],
    "SSI or SSDI": [
        "SSI or SSDI"
    ],
    "SNAP": [
        "SNAP"
    ]
}

participant_info_accepted_responses = {
    "First Name": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Middle Name": {
        "limited_response": False,
        "accepted_responses": [],
        "non_essential": True
    },
    "Last Name": {
        "limited_response": False,
        "accepted_responses": []
    },
    "CT Hires Username / State ID": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Date of Birth": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Participant Address - Street Address": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Participant Address - Apt No": {
        "limited_response": False,
        "accepted_responses": [],
        "non_essential": True
    },
    "Participant Address - City": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Participant Address - State": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Participant Address - Zip Code": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Participant Attribute - Highest Educational Attainment": {
        "limited_response": True,
        "accepted_responses": [
            "Attained secondary school diploma",
            "Attained a secondary school equivalency",
            "The participant with a disability receives a certificate of attendance/completion as a result of successfully completing an individualized education program (IEP)",
            "Completed one or more years of postsecondary education",
            "Attained a postsecondary technical or vocation certificate (non-degree)",
            "Attained an Associate's degree",
            "Attained a Bachelor's degree",
            "Attained a degree beyond a Bachelor's degree",
            "No educational level completed"
        ],
        "non_essential":"True"
    },
    "Participant Attribute - School Status at Program Entry": {
        "limited_response": True,
        "accepted_responses": [
            "In school, secondary school or less",
            "In school, alternative school",
            "In school, postsecondary school",
            "Not attending school or secondary school dropout",
            "Not attending school; secondary school school graduate or has a recognized equivalent",
            "Not attending school; secondary school graduate or has a recognized equivalent",
            "Not attending school; within age of compulsory school attendance"
        ],
        "non_essential":"True"
    },
    "Participant Attribute - Low Income Status": {
        "limited_response": True,
        "accepted_responses": [
            "Yes",
            "No"
        ],
        "non_essential":"True"
    },
    "Participant Attribute - Basic Skills Deficiency": {
        "limited_response": True,
        "accepted_responses": [
            "Yes",
            "No"
        ],
        "non_essential":"True"
    },
    "Participant Attribute - Single Parent at Program Entry": {
        "limited_response": True,
        "accepted_responses": [
            "Yes",
            "No"
        ],
        "non_essential":"True"
    },
    "Participant Attribute - Co-Enrollment (WIOA or WIP)": {
        "limited_response": True,
        "accepted_responses": {
            "Yes, WIOA": ["Yes, WIOA", "WIOA"],
            "Yes, WP": ["Yes, WP", "WP"],
            "Both WIOA and WP": ["Both WIOA and WP"],
            "No": ["No", "N"],
            "CCT": ["CCT", "C"]
        },
        "non_essential":"True"
    },
    "Participant Attribute - TANF recipient": {
        "limited_response": True,
        "accepted_responses": [
            "Yes",
            "No"
        ],
        "non_essential":"True"
    },
    "Participant Attribute - SSI or SSDI recipient": {
        "limited_response": True,
        "accepted_responses": [
            "SSI",
            "SSDI",
            "Both SSI and SSDI",
            "No"
        ],
        "non_essential":"True"
    },
    "Participant Attribute - SNAP recipient": {
        "limited_response": True,
        "accepted_responses": [
            "Yes",
            "No"
        ],
        "non_essential":"True"
    }
}

participant_info_accepted_responses_w_types = {
    "First Name": {
        "type": "identifier",
        "accepted_responses": [],
        "required": True
    },
    "Middle Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Last Name": {
        "type": "identifier",
        "accepted_responses": [],
        "required": True
    },
    "CTHires Username or State ID #": {
        "type": "identifier",
        "accepted_responses": [],
        "required": True
    },
    "Date of Birth": {
        "type": "dateTime",
        "accepted_responses": [],
        "required": True
    },
    "Street Address 1": {
        "type": "identifier",
        "accepted_responses": [],
        "required": True
    },
    "Street Address 2 (apt, etc)": {
        "type": "identifier",
        "accepted_responses": []
    },
    "City": {
        "type": "identifier",
        "accepted_responses": [],
        "required": True
    },
    "State": {
        "type": "identifier",
        "accepted_responses": [],
        "required": True
    },
    "Zip Code": {
        "type": "zipCode",
        "accepted_responses": [],
        "required": True
    },
    "Highest Education Level Obtained": {
        "type": "categorical",
        "accepted_responses": [
            "Attained secondary school diploma",
            "Attained a secondary school equivalency",
            "The participant with a disability receives a certificate of attendance/completion as a result of successfully completing an individualized education program (IEP)",
            "Completed one or more years of postsecondary education",
            "Attained a postsecondary technical or vocation certificate (non-degree)",
            "Attained an Associate's degree",
            "Attained a Bachelor's degree",
            "Attained a degree beyond a Bachelor's degree",
            "No educational level completed"
        ],
        "required": True
    },
    "School Status at Program Entry": {
        "type": "categorical",
        "accepted_responses": [
            "In school, secondary school or less",
            "In school, alternative school",
            "In school, postsecondary school",
            "Not attending school or secondary school dropout",
            "Not attending school; secondary school graduate or has a recognized equivalent",
            "Not attending school; within age of compulsory school attendance"
        ],
        "required": True
    },
    "Low Income Status": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"],
        "required": True
    },
    "Basic Skills Deficient": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"],
        "required": True
    },
    "Single Parent at Program Entry": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"],
        "required": True
    },
    "Co-Enrollment (WIOA or WP)": {
        "type": "categorical",
        "accepted_responses": [
            "Yes, WIOA",
            "Yes, WP",
            "Both WIOA and WP",
            "No",
            "CCT"
        ],
        "required": True
    },
    "TANF": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"],
        "required": True
    },
    "SSI or SSDI": {
        "type": "categorical",
        "accepted_responses": [
            "SSI",
            "SSDI",
            "Both SSI and SSDI",
            "No"
        ],
        "required": True
    },
    "SNAP": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"],
        "required": True
    }
}


program_enrollment_labels = {
    "First Name": [
        "First Name"
    ],
    "Middle Name": [
        "Middle Name"
    ],
    "Last Name": [
        "Last Name"
    ],
    "Training Provider Name": [
        "Training Provider Name"
    ],
    "Training Program Name": [
        "Training Program Name"
    ],
    "Training CIP Code": [
        "Training CIP Code"
    ],
    "Training Start Date": [
        "Training Start Date"
    ],
    "Training End Date": [
        "Training End Date"
    ],
    "Training Completion Status": [
        "Training Completion Status"
    ],
    "Non-Completion Exit Reason": [
        "Non-Completion Exit Reason",
        "Non-completion reason descriptor"
    ],
    "If other, please specify exit reason": [
        "If other, please specify exit reason"
    ]
}

program_enrollment_accepted_responses_w_types = {
    "First Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Middle Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Last Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Training Provider Name": {
        "type": "fileSpecificCategorical",
        "accepted_responses": {
        "NRWIB_MFG": {
            "Manufacturing Alliance Service Corporation": [
                "manufacturing alliance service corporation",
                "manufacturing alliance sevice corporation (masc)",
                "masc"
            ]
        },
        "BRBC": {
            "Academy at Coffee Project": ["academy at coffee project"],
            "University of Bridgeport/Goodwin": ["university of bridgeport/goodwin"],
            "CT State - Housatonic/Platt Technical High School": [
                "ct state - housatonic/platt technical high school"
            ],
            "Southern Connecticut University": ["southern connecticut university"],
            "CT State - Housatonic at Housatonic": ["ct state - housatonic at housatonic"],
            "MATCH": ["match"],
            "CT State - Norwalk": ["ct state - norwalk"]
        },
        "CWP": {
            "Marrakech, Inc.": ["marrakech, inc."],
            "National Institute for Medical Assistant Advancement - NIMAA": [
                "national institute for medical assistant advancement - nimaa"
            ],
            "Charter Oak State College": ["charter oak state college"],
            "Northeast Medical Institute": ["northeast medical institute"],
            "CT State - Capital Campus": ["ct state community college - capital campus"],
            "CT State - Tunxis Campus": ["ct state community college - tunxis campus"],
            "Career Resource Inc. - Strive": [
                "strive connecticut - career resources, inc."
            ],
            "JobWorks": ["jobworks"],
            "DCI Resources": ["dci resources"]
        },
        "EWIB_MFG": {
            "Bacon Academy": ["bacon academy"],
            "EO Smith High School": ["eo smith high school"],
            "Griswold High School": ["griswold high school"],
            "RHAM High School": ["rham high school", "RHAM"],
            "Norwich Free Academy (NFA)": ["norwich free academy (nfa)"],
            "Stonington High School": ["stonington high school"],
            "Tourtellotte Memorial High School": ["tourtellotte memorial high school"],
            "Woodstock Academy": ["woodstock academy"],
            "Putnam High School": ["putnam high school"],
            "New London High School": ["new london high school"],
            "CT STATE Three Rivers": ["ct state three rivers"],
            "Community College Rhode Island": ["community college rhode island"],
            "Lyman Memorial High School": ["lyman memorial high school"],
            "Windham High School": ["windham high school"],
            "Parish Hill High School": ["parish hill"],
            "Plainfield High School": ["plainfield high school"]
        },
        "EWIB_HC": {
            "CT State Community College - Quinebaug Valley": [
                "ct state community college - quinebaug valley"
            ],
            "American Professional Educational Services": [
                "american professional educational services"
            ],
            "New London Adult and Continuing Education": [
                "new london adult and continuing education"
            ],
            "CNA Bootcamp of CT": ["cna bootcamp of ct"],
            "Health Education Center, Inc.": ["health education center, inc."],
            "CT State Community College - Three Rivers": [
                "ct state community college - three rivers"
            ],
            "East Lyme High School": ["east lyme high school"],
            "Robert E. Fitch High School": ["robert e. fitch high school"],
            "Griswold High School": ["griswold high school"],
            "CT State Community College - Asnuntuck": [
                "ct state community college - asnuntuck"
            ],
            "Killingly High School": ["killingly high school"],
            "Stonington High School": ["stonington high school"],
            "Windham High School": ["windham high school"],
            "New London High School": ["new london high school"],
            "Norwich Free Academy (NFA)": ["norwich free academy (nfa)"],
            "Lyman Memorial High School": ["lyman memorial high school"],
            "Tourtellotte Memorial High School": ["tourtellotte memorial high school"],
            "Woodstock Academy": ["woodstock academy"],
            "RHAM High School": ["rham high school", "RHAM"],
            "Plainfield High School": ["plainfield high school"]
        },
        "GNHCC": {
            "Connecticut Center for Arts and Technology": [
                "connecticut center for arts and technology"
            ],
            "Greater New Haven Chamber of Commerce": [
                "greater new haven chamber of commerce"
            ],
            "Connecticut Center for Arts and Technology & Greater New Haven Chamber of Commerce": [
                "connecticut center for arts and technology & greater new haven chamber of commerce"
            ],
            "Northeast Medical Institute": ["northeast medical institute"],
            "Southern Connecticut State University": ["southern connecticut state university"],
            "Excel Academy": ["excel academy"],
            "Albertus Magnus College": ["albertus magnus college"],
            "Wallingford Adult Education": ["wallingford adult education"]

        },
        "TWP": {
            "Southern Connecticut State University": ["southern connecticut state university"],
            "Housatonic Community College": ["housatonic community college"],
            "DCI Resources": ["dci", "dci resources"]
        },
        "WFA": {
            "Manufacturing and Technology Community Hub": [
                "match",
                "manufacturing and technology community hub",
                "manufacturing and technical community hub (match)"
            ],
            "CT State - Middlesex": ["ctstate-middlesex"]
        },
        "NRWIB_HC": {
            "Griffin Health": ["griffin hospital school of allied heath careers"],
            "Northeast Medical Institute": ["northeast medical institute"],
            "Academy of Medical Training, Inc.": ["academy of medical training, inc."],
            "Northwestern Connecticut Community College": [
                "northwestern connecticut community college"
            ],
            "Hispanic Coalition of Greater Waterbury": [
                "hispanic coalition of greater waterbury"
            ]
        }
    },
        "required": True
    },
    "Training Program Name": {
    "type": "fileSpecificCategorical",
    "accepted_responses": {
        "NRWIB_MFG": {
            "CNC Entry Level": ["cnc entry level"],
            "Introduction to Plastics": [
                "introduction to plastics",
                "introduction to plastic injection molding"
            ],
            "MASTERCAM/CNC II": ["mastercam/cnc ii"],
            "MFG Machinist": ["mfg machinist"],
            "Apprenticeship Training": ["apprenticeship training"],
            "Fundamentals of Manufacturing": [
                "fundamentals of manufacturing",
                "fundamentals of mfg technology"
            ]
        },
        "BRBC": {
            "SCA Roasting Skills Beginner & Intermediate Bundle": [
                "sca roasting skills beginner & intermediate bundle"
            ],
            "Module 1: Welding Safety": ["module 1: welding safety"],
            "Basic Welding Credential Training": [
                "basic welding credential training"
            ],
            "CNC Level 1": ["cnc level 1"],
            "Intro to Manufacturing": ["intro to manufacturing"],
            "Intro to Manufacturing (HCC)": [
                "intro to manufacturing (hcc)",
                "intro to manufacturing"
            ],
            "Certified Manufacturing Associate": [
                "certified manufacturing associate"
            ],
            "Metrology Technologies": ["metrology technologies"],
            "SolidWorks": ["solidworks"],
            "AI Fundamentals for Workplace Success": [
                "ai fundamentals for workplace success"
            ],
            "Manufacturing Essentials": ["manufacturing essentials"],
            "Optic Fabrication and Metrology": [
                "optic fabrication and metrology"
            ],
            "Swiss CNC Level 1": ["swiss cnc level 1"],
            "Multi-Disciplinary Manufacturing Pre-Apprenticeship": [
                "multi-disciplinary manufacturing pre-apprenticeship"]
        },
        "CWP": {
            # Health programs
            "Direct Support Specialist": ["direct support specialist"],
            "Medical Assistant": ["medical assistant"],
            "Revenue Cycle Management": ["revenue cycle management"],
            "Certified Nurses Aide": ["certified nurse aide/assistant"],
            "Patient Care Technician": ["patient care technician"],
            "Pharmacy Technician": ["pharmacy technician"],
            "Central Sterile Processing Technician": [
                "central sterile processing technician",
                "certified sterile processing technician"

            ],
            "Career Training": [
                "strive (support and training result in valuable employees)"
            ],
            # Tech programs
            "TechWorks": ["techworks"],
            "Business Analyst": ["business analyst"],
            "Cloud Network Specialist": ["cloud network specialist"],
            "Cloud Tech Specialist": ["cloud tech specialist"],
            "Cybersecurity Specialist": ["cybersecurity specialist"],
            "Full Stack Developer": ["full stack developer"],
            "Help Desk Analyst": ["help desk analyst"]
        },
        "EWIB_MFG": {
            "YMPI": ["ympi"],
            "Design": ["design"],
            "Electrical": ["electrical"],
            "Inside Machinist": ["inside machinist"],
            "Painter": ["painter"],
            "Outside Machinist": ["outside machinist"],
            "Pipefitter": ["pipefitter"],
            "Shipfitter": ["shipfitter"],
            "Sheetmetal": ["sheetmetal"],
            "Welding": ["welding"]
        },
        "EWIB_HC": {
            "Certified Nursing Assistant (CNA)": [
                "certified nursing assistant (cna)",
                "certified nursing assistant (cna) - high school"
            ],
            "Emergency Medical Technician (EMT)": [
                "emergency medical technician (emt)"
            ],
            "Medical Interpreter": ["medical interpreter"],
            "Medical Billing & Coding": ["medical billing & coding"],
            "Pharmacy Technician": ["pharmacy technician"],
            "Phlebotomy": ["phlebotomy"],
            "EKG Technician": ["ekg technician"],
            "Community Health Worker (CHW)": ["community health worker (chw)"],
            "Sterile Processing Technician": ["sterile processing technician"],
            "Medical Assistant": ["medical assistant"],
            "Dental Assistant": ["dental assistant"]
        },
        "GNHCC": {
            "BioLaunch Basic Training Program": ["biolaunch basic training program"],
            "Professional Skills Program": ["professional skills program", 
                                            "professional skills training program"],
            "BioLaunch Basic Training Program & Professional Skills Program": [
                "biolaunch basic training program & professional skills program",
                "biolaunch basic training program professional skills training"
            ],
            "BioLaunch Advanced Training Program": ["biolaunch advanced training program"],
            "Patient Care Technician": ["patient care technician training program"],
            "Phlebotomy": ["phlebotomy", "phlebotomy technician"],
            "Certified Nurses Aide":["cna training program",
                                     "cna training program (8 week)",
                                     "cna training program (11 week)",
                                     "certified nursing assistant course (8 week)",
                                     "certified nursing assistant course"],
        },
        "TWP": {
            "Generative AI": ["generative ai"],
            "Comp TIA A+": ["comp tia a+"],
            "Comp TIA Security +": ["comp tia security +", "comp tia seurity +"],
            "AWS Cloud Practitioner": ["aws cloud practitioner"],
            "AWS Solutions Architect": ["aws solutions architect"],
            "Project Management": ["project management", "project mangement"],
            "Google Cybersecurity": ["google cybersecurity"],
            "Google Project Management": ["google project management"],
            "CMMC": ["cmmc"],
            "Python I": ["python i", "python 1"],
            "Python II": ["python ii"],
            "SQL": ["sql"]
        },
        "WFA": {
            "Machinist Pre-Apprenticeship": [
                "machinist pre-apprenticeship",
                "manufacturing pre-apprenticeship"
            ],
            "Manufacturing Administration": ["manufacturing administration"],
            "Forklift & Material Handling": ["forklift & material handling"]
        },
        "NRWIB_HC": {
            "Clinical Medical Assistant": [
                "clinical medical assistant",
                "medical assistant"
            ],
            "Certified EKG Technician": [
                "certified ekg technician",
                "ekg",
                "ekg technician"
            ],
            "Pharmacy Technician": [
                "pharmacy tech",
                "pharmacy technician"
            ],
            "Certified Nurses Aide": [
                "certified nurses aide",
                "cna/cpt"
            ],
            "Phlebotomy Technician": [
                "phlebotomy technician",
                "certified phlebotomy technician"
            ],
            "Patient Care Technician": ["certified patient care technician", "patient care technician","EKG Technician and Phlebotomy Technician & PCT Exam","Certified Nurses Aide and EKG Technician& PCT exam"],
            "CPT & EKG Technician": ["cpt & ekg technician"],
            "EKG Technician and Phlebotomy Technician":["EKG Technician and Phlebotomy Technician"],
            "CNA and Phlebotomy Technician": ["CNA/Phlebotomy","Certified Nurses Aide and Phlebotomy Technician"],
            "CNA and EKG Technician": ["certified nurses aide and ekg technician"],
            "CEntral Sterile Processing Technician": ["central sterile processing"],
            "Emergency Medical Technician (EMT)": [
                "emergency medical tech"
            ]
        }
    },
        "required": True
},
    "Training CIP Code": {
        "type": "CIPCode",
        "accepted_responses": [],
        "required": True
    },
    "Training Start Date": {
        "type": "dateTime",
        "accepted_responses": [],
        "required": True
    },
    "Training End Date": {
        "type": "dateTime",
        "accepted_responses": []
    },
    "Training Completion Status": {
        "type": "categorical",
        "accepted_responses" : {
    "Completed training on time": [
        "Completed training on time",
        "Yes"
    ],
    "Did not complete training (please code exit reason)": [
        "Did not complete training (please code exit reason)",
        "No"
    ],
    "Yes but not continuous": [
        "Yes but not continuous"
    ]
}
    },
    "Non-Completion Exit Reason": {
        "type": "categorical",
        "accepted_responses" : {
    "Could not meet the technical requirements for graduation": [
        "Could not meet the technical requirements for graduation"
    ],
    "Withdrew due to family obligations": [
        "Withdrew due to family obligations"
    ],
    "Withdrew due to physical health reasons": [
        "Withdrew due to physical health reasons"
    ],
    "Withdrew due to mental health reasons": [
        "Withdrew due to mental health reasons"
    ],
    "Withdrew due to lack of adequate transportation": [
        "Withdrew due to lack of adequate transportation"
    ],
    "Withdrew due to lack of childcare": [
        "Withdrew due to lack of childcare"
    ],
    "Withdrew due to financial obligation(s) (e.g., had to get a full-time job)": [
        "Withdrew due to financial obligation(s) (e.g., had to get a full-time job)"
    ],
    "Participant was dismissed due to behavior": [
        "Participant was dismissed due to behavior"
    ],
    "Participant did not meet attendance requirements": [
        "Participant did not meet attendance requirements"
    ],
    "Withdrew because they started a new job during training": [
        "Withdrew because they started a new job during training",
        "Secured Employed"
    ],
    "Other": [
        "Other"
    ]
}

    },
    "If other, please specify exit reason": {
        "type": "identifier",
        "accepted_responses": []
    }
}


credential_attainment_labels = {
    "First Name": [
        "First Name"
    ],
    "Middle Name": [
        "Middle Name"
    ],
    "Last Name": [
        "Last Name"
    ],
    "Training Provider": [
        "Training Provider"
    ],
    "Training Program": [
        "Training Program"
    ],
    "Credential 1 Type": [
        "Credential 1 Type"
    ],
    "Credential 2 Type": [
        "Credential 2 Type"
    ],
    "Credential 3 Type": [
        "Credential 3 Type"
    ],
    "Credential 4 Type": [
        "Credential 4 Type"
    ],
    "Credential 5 Type": [
        "Credential 5 Type"
    ],
    "New Skills Acquired (select all that apply)": [
        "New Skills Acquired (select all that apply)"
    ],
    "Other Skills (NAICS code)": [
        "Other Skills (NAICS code)"
    ]
}

credential_attainment_accepted_responses = {
    "First Name": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Middle Name": {
        "limited_response": False,
        "accepted_responses": [],
        "non_essential": True
    },
    "Last Name": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Provider": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Program": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Credential 1 Type": {
        "limited_response": True,
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ],
        "non_essential": True
        # "conditional":{
        #     "conditional_sheet":"Program_Enrollment",
        #     "conditional_column":"Training Completion Status",
        #     "conditional_logic":"specific_value_different_sheet",
        #     "conditional_value":["Yes","Completed training on time","Yes but not continuous"]
        # }
    },
    "Credential 2 Type": {
        "limited_response": True,
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ],
        "non_essential": True
    },
    "Credential 3 Type": {
        "limited_response": True,
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ],
        "non_essential": True
    },
    "Credential 4 Type": {
        "limited_response": True,
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ],
        "non_essential": True
    },
    "Credential 5 Type": {
        "limited_response": True,
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ],
        "non_essential": True
    },
    "New Skills Acquired": {
        "limited_response": True,
        "accepted_responses": [
            "Data analytics",
            "Management/leadership",
            "Project management",
            "Marketing/sales",
            "Engineering/computer science",
            "Finance/investment",
            "Product development",
            "Business analytics",
            "Business development",
            "Information technology",
            "Healthcare",
            "Trade Skills",
            "Other"
        ],
        "non_essential": True
        # "conditional":{
        #     "conditional_sheet":"Program_Enrollment",
        #     "conditional_column":"Training Completion Status",
        #     "conditional_logic":"specific_value_different_sheet",
        #     "conditional_value":["Yes","Completed training on time","Yes but not continuous"]
        # },
        # "non_essential": True
    },
    "Other Skills (NAICS)": {
        "limited_response": False,
        "accepted_responses": [],
        # "conditional":{
        #     "conditional_sheet":"Program_Enrollment",
        #     "conditional_column":"Training End Date",
        #     "conditional_logic":"date_in_past_different_sheet"
        # },
        "non_essential": True
    }
}

credential_attainment_accepted_responses_w_types = {
    "First Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Middle Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Last Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Training Provider": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Training Program": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Credential 1 Type": {
        "type": "categorical",
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ]
    },
    "Credential 2 Type": {
        "type": "categorical",
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ]
    },
    "Credential 3 Type": {
        "type": "categorical",
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ]
    },
    "Credential 4 Type": {
        "type": "categorical",
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ]
    },
    "Credential 5 Type": {
        "type": "categorical",
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ]
    },
    "New Skills Acquired (select all that apply)": {
        "type": "categorical",
        "accepted_responses": [
            "Data analytics",
            "Management/leadership",
            "Project management",
            "Marketing/sales",
            "Engineering/computer science",
            "Finance/investment",
            "Product development",
            "Business analytics",
            "Business development",
            "Information technology",
            "Healthcare",
            "Trade Skills",
            "Other"
        ]
    },
    "Other Skills (NAICS code)": {
        "type": "NAICSCode",
        "accepted_responses": []
    }
}


employment_labels = {
    "First Name": [
        "First Name"
    ],
    "Middle Name": [
        "Middle Name"
    ],
    "Last Name": [
        "Last Name"
    ],
    "Training Provider": [
        "Training Provider"
    ],
    "Training Program": [
        "Training Program"
    ],
    "School Status at Exit": [
        "School Status at Exit"
    ],
    "Employment Status": [
        "Employment Status"
    ],
    "Job Start Date": [
        "Job Start Date"
    ],
    "Employment Type": [
        "Employment Type"
    ],
    "If earn and learn, type": [
        "If earn and learn, type"
    ],
    "If other, please specify": [
        "If other, please specify"
    ],
    "Employer": [
        "Employer"
    ],
    "Employer Zip Code": [
        "Employer Zip Code"
    ],
    "If employed, did participant report hourly salary?": [
        "If employed, did participant report hourly salary?"
    ],
    "Hourly Earnings": [
        "Hourly Earnings"
    ],
    "Weekly Hours (Est.)": [
        "Weekly Hours (Est.)"
    ],
    "Occupation (NAICS) code": [
        "Occupation (NAICS) code"
    ],
    "Access to healthcare benefits through employer?": [
        "Access to healthcare benefits through employer?"
    ],
    "Access to PTO benefits through employer?": [
        "Access to PTO benefits through employer?"
    ],
    "Access to retirement benefits?": [
        "Access to retirement benefits?"
    ],
    "Access to sick leave?": [
        "Access to sick leave?"
    ],
    "Access to additional training through employer?": [
        "Access to additional training through employer?"
    ],
    "Access to flexible work schedule?": [
        "Access to flexible work schedule?"
    ]
}

employment_accepted_responses = {
    "First Name": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Middle Name": {
        "limited_response": False,
        "accepted_responses": [],
        "non_essential": True
    },
    "Last Name": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Provider": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Program": {
        "limited_response": False,
        "accepted_responses": []
    },
    "School Status at Exit": {
        "limited_response": True,
        "accepted_responses": [
            "In-school; secondary school or less",
            "In-school; alternative school",
            "In-school; Postsecondary school",
            "Not attending school or secondary school dropout",
            "Not attending school; secondary school graduate or has recognized equivalent",
            "Not attending school; secondary school graduate or has a recognized equivalent",
            "Not attending school; secondary school school graduate or has a recognized equivalent",
            "Not attending school; within age of compulsory school attendance"
        ],
        "conditional":{
            "conditional_sheet":"Program_Enrollment",
            "conditional_column":"Training End Date",
            "conditional_logic":"date_in_past_different_sheet",
            "conditional_error_message":"School Status at Exit must be specified after training end date has expired."
        },
        "non_essential":"True"
    },
    "Employment Status": {
        "limited_response": True,
        "accepted_responses": [
            "Employed in-field by an employer who partners with your training program",
            "Employed in-field by an employed who doesn't partner with your training program",
            "Employed in-field by an employer who doesn't partner with your training program",
            "Still seeking employment",
            "Seeking Employment",
            "Not seeking employment in-field",
            "Could not contact",
            "Employed out of field",
            "Employed not in-field",
            "Employed in-field",
            "In Job Search Assistance",
            "Going to college"

        ],
        "conditional":
            [
            {
            "conditional_sheet":"Program_Enrollment",
            "conditional_column":"Training End Date",
            "conditional_logic":"date_in_past_different_sheet",
            "conditional_error_message":"Check training end date, this should be specified if training is over."
            }]

        },
    "Job Start Date": {
        "limited_response": False,
        "accepted_responses": [],
        "conditional":
            [
            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            }
            ]
        
    },
    "Employment Type": {
        "limited_response": True,
        "accepted_responses": [
            "Full-time employment",
            "Part-time employment",
            "Seasonal employment",
            "Earn and Learn employment",
            "Other"
        ],
        "conditional":[            
            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }]
    },
    "Earn and Learn Type": {
        "limited_response": True,
        "accepted_responses": [
            "Registered Apprenticeships",
            "Non-registered Apprenticeship",
            "Internship",
            "Customized Training",
            "Incumbent Worker Training",
            "Transitional Jobs",
            "Cooperatives",
            "Practicums, Residences, or Fellowships",
            "Other"
        ],
        "conditional": [
        {
            "conditional_column": "Employment Type",
            "conditional_logic": "specific_value",
            "conditional_value": "Earn and Learn employment",
            "conditional_error_message":"Check employment type, this should only be specified if type is earn and learn."
            
        }
        ]
    },
    "Other Employment Description": {
        "limited_response": False,
        "accepted_responses": [],
        "conditional": [
        {
            "conditional_column": "Employment Type",
            "conditional_logic": "specific_value",
            "conditional_value": "Other",
            "conditional_error_message":"Check employment type, this should only be specified if type is other."
            
        }
        ]
    },
    "Employer": {
        "limited_response": False,
        "accepted_responses": [],
        "conditional":[            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }]

    },
    "Employer Zip Code": {
        "limited_response": False,
        "accepted_responses": [],
        "conditional":[            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }],
        "non_essential":True
    },
    "Hourly Salary Reported?": {
        "limited_response": True,
        "accepted_responses": ["Yes", "No"],
        "conditional":[            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }]
    },
    "Hourly Earnings": {
        "limited_response": False,
        "accepted_responses": [],
        "conditional":[{
            "conditional_column":"Hourly Salary Reported",
            "conditional_logic":"specific_value",
            "conditional_value":""
        }]
    },
    "Weekly Hours": {
        "limited_response": False,
        "accepted_responses": [],
        "conditional":[            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }],
        "non_essential":True
    },
    "Occupation (NAICS) code": {
        "limited_response": False,
        "accepted_responses": [],
        "conditional":[            
            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }]
    },
    "Access to Healthcare Benefits through employer?": {
        "limited_response": True,
        "accepted_responses": ["Yes", "No"],
        "conditional":[            
            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }],
        "non_essential":"True"
    },
    "Access to PTO through employer?": {
        "limited_response": True,
        "accepted_responses": ["Yes", "No"],
        "conditional":[            
            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }],
        "non_essential":"True"
    },
    "Access to retirement benefits through employer?": {
        "limited_response": True,
        "accepted_responses": ["Yes", "No"],
        "conditional":[
            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }
        ],
        "non_essential":"True"
    },
    "Access to sick leave through employer?": {
        "limited_response": True,
        "accepted_responses": ["Yes", "No"],
        "conditional":[
            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }
        ],
        "non_essential":"True"
    },
    "Access to additional training through employer?": {
        "limited_response": True,
        "accepted_responses": ["Yes", "No"],
        "conditional":[
            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }
        ],
        "non_essential":"True"
    },
    "Access to flexible work schedule through employer?": {
        "limited_response": True,
        "accepted_responses": ["Yes", "No"],
        "conditional":[
            {"conditional_column":"Employment Status",
            "conditional_logic":"specific_value",
            "conditional_value":["Employed in-field by an employer who partners with your training program",
                                 "Employed in-field by an employed who doesn't partner with your training program",
                                 "Employed in-field by an employer who doesn't partner with your training program",
                                 "Employed out of field",
                                 "Employed not in-field",
                                 "Employed in-field"
                                 ],
            "conditional_error_message":"Check employment status, this should only be specified if participant is employed."
            
            }

        ],
        "non_essential":"True"
    } 
}

employment_accepted_responses_w_types = {
    "First Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Middle Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Last Name": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Training Provider": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Training Program": {
        "type": "identifier",
        "accepted_responses": []
    },
    "School Status at Exit": {
        "type": "categorical",
        "accepted_responses": [
            "In-school; secondary school or less",
            "In-school; alternative school",
            "In-school; Postsecondary school",
            "Not attending school or secondary school dropout",
            "Not attending school; secondary school graduate or has recognized equivalent",
            "Not attending school; within age of compulsory school attendance"
        ]
    },
    "Employment Status": {
        "type": "categorical",
        "accepted_responses": [
            "Employed in-field by an employer who partners with your training program",
            "Employed in-field by an employer who doesn't partner with your training program",
            "Still seeking employment",
            "Seeking Employment",
            "Not seeking employment in-field",
            "Could not contact",
            "Employed out of field",
            "Employed not in-field",
            "Employed in-field",
            "In Job Search Assistance",
            "Going to college"
        ]
    },
    "Job Start Date": {
        "type": "dateTime",
        "accepted_responses": []
    },
    "Employment Type": {
        "type": "categorical",
        "accepted_responses": [
            "Full-time employment",
            "Part-time employment",
            "Seasonal employment",
            "Earn and Learn employment",
            "Other"
        ]
    },
    "If earn and learn, type": {
        "type": "categorical",
        "accepted_responses": [
            "Registered Apprenticeships",
            "Non-registered Apprenticeship",
            "Internship",
            "Customized Training",
            "Incumbent Worker Training",
            "Transitional Jobs",
            "Cooperatives",
            "Practicums, Residences, or Fellowships",
            "Other"
        ]
    },
    "If other, please specify": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Employer": {
        "type": "identifier",
        "accepted_responses": []
    },
    "Employer Zip Code": {
        "type": "zipCode",
        "accepted_responses": []
    },
    "If employed, did participant report hourly salary?": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"]
    },
    "Hourly Earnings": {
        "type": "hourlyWage",
        "accepted_responses": []
    },
    "Weekly Hours (Est.)": {
        "type": "hoursWorked",
        "accepted_responses": []
    },
    "Occupation (NAICS) code": {
        "type": "NAICSCode",
        "accepted_responses": []
    },
    "Access to healthcare benefits through employer?": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"]
    },
    "Access to PTO benefits through employer?": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"]
    },
    "Access to retirement benefits?": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"]
    },
    "Access to sick leave?": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"]
    },
    "Access to additional training through employer?": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"]
    },
    "Access to flexible work schedule?": {
        "type": "boolean",
        "accepted_responses": ["Yes", "No"]
    }
}

##### GJC Supportive Services 

training_provider_list_labels = [
    "Training Provider",  # 1
    "Training Program"    # 2
]

gjc_funding_labels = [
    "First Name",                              # 1
    "Middle Name",                             # 2
    "Last Name",                               # 3
    "CTHires Username",                        # 4
    "State ID",                                # 5
    "Resident Address - Zip Code",             # 6
    "Training Provider",                       # 7
    "Training Program",                        # 8
    "Funding Source (GJC/Other - Please State)", # 9
    "Supportive Service 1 - Specific Use",     # 10
    "Supportive Service 1 - Amount",           # 11
    "Supportive Service 2 - Specific Use",     # 12
    "Supportive Service 2 - Amount",           # 13
    "Supportive Service 3 - Specific Use",     # 14
    "Supportive Service 3 - Amount",           # 15
    "Supportive Service 4 - Specific Use",     # 16
    "Supportive Service 4 - Amount",           # 17
    "Supportive Service 5 - Specific Use",     # 18
    "Supportive Service 5 - Amount"            # 19
]

### CWP 

cwp_participant_info_labels = [
    "Board Identifier",                                           # 1
    "First Name",                                                 # 2
    "Middle Name",                                                # 3
    "Last Name",                                                  # 4
    "CT Hires Username / State ID",                               # 5
    "Date of Birth",                                              # 6
    "Participant Address - Street Address",                       # 7
    "Participant Address - Apt No",                               # 8
    "Participant Address - City",                                 # 9
    "Participant Address - State",                                # 10
    "Participant Address - Zip Code",                             # 11
    "Participant Attribute - Highest Educational Attainment",     # 12
    "Participant Attribute - School Status at Program Entry",     # 13
    "Participant Attribute - Low Income Status",                  # 14
    "Participant Attribute - Basic Skills Deficiency",            # 15
    "Participant Attribute - Single Parent at Program Entry",     # 16
    "Participant Attribute - Co-Enrollment (WIOA or WIP)",        # 17
    "Participant Attribute - TANF recipient",                     # 18
    "Participant Attribute - SSI or SSDI recipient",              # 19
    "Participant Attribute - SNAP recipient",                     # 20
    "Training Program Name",                                      # 21
    "Training CIP Code",                                          # 22
    "Training Start Date",                                        # 23
    "Training End Date",                                          # 24
    "Training Completion Status",                                 # 25
    "Non-Completion Exit Reason",                                 # 26
    "Non-completion reason descriptor",                           # 27
    "Credential 1 Type",                                          # 28
    "Credential 2 Type",                                          # 29
    "Credential 3 Type",                                          # 30
    "Credential 4 Type",                                          # 31
    "Credential 5 Type",                                          # 32
    "New Skills Acquired",                                        # 33
    "Other Skills (NAICS)",                                       # 34
    "School Status at Exit",                                      # 35
    "Employment Status",                                          # 36
    "Job Start Date",                                             # 37
    "Employment Type",                                            # 38
    "Earn and Learn Type",                                        # 39
    "Other Employment Description",                               # 40
    "Employer",                                                   # 41
    "Employer Zip Code",                                          # 42
    "Hourly Salary Reported?",                                    # 43
    "Hourly Earnings",                                            # 44
    "Weekly Hours",                                               # 45
    "Occupation (NAICS) code",                                    # 46
    "Access to Healthcare Benefits through employer?",            # 47
    "Access to PTO through employer?",                            # 48
    "Access to retirement benefits through employer?",            # 49
    "Access to sick leave through employer?",                     # 50
    "Access to additional training through employer?",            # 51
    "Access to flexible work schedule through employer?"          # 52
]

### EDA Report Labels 

eda_training_provider_labels = eda_training_provider_labels = (
    ["Sectoral Partnership", "Training Provider"] +
    [f"Training Program {i}" for i in range(1, 21)]
)

eda_updated_list_labels = [
    "Training Provider",
    "Training Program",
    "Sectoral Partnership"
]

eda_participant_database_labels = [
    "Training Provider",                        # 1
    "Training Program",                         # 2
    "First Name",                               # 3
    "Middle Name",                              # 4
    "Last Name",                                # 5
    "Training Start Date - Month",              # 6
    "Training Start Date - Day",                # 7
    "Training Start Date - Year",               # 8
    "Training End Date - Month",                # 9
    "Training End Date - Day",                  #10
    "Training End Date - Year",                 #11
    "Completed Training",                       #12 (Yes/No) — limited response
    "Job Start Date - Month",                   #13
    "Job Start Date - Day",                     #14
    "Job Start Date - Year",                    #15
    "Address of Residence - Street",            #16
    "Address of Residence - Apt. No.",          #17
    "Address of Residence - City",              #18
    "Address of Residence - State",             #19
    "Address of Residence - Zip"                #20
]

eda_participant_database_accepted_responses = {
    "Training Provider": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Program": {
        "limited_response": False,
        "accepted_responses": []
    },
    "First Name": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Middle Name": {
        "limited_response": False,
        "accepted_responses": [],
        "non_essential": True
    },
    "Last Name": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Start Date - Month": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Start Date - Day": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Start Date - Year": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training End Date - Month": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training End Date - Day": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training End Date - Year": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Completed Training": {
        "limited_response": True,
        "accepted_responses": ["Yes", "No"]
    },
    "Job Start Date - Month": {
        "limited_response": False,
        "accepted_responses": [],
        "non_essential": True
    },
    "Job Start Date - Day": {
        "limited_response": False,
        "accepted_responses": [],
        "non_essential": True
    },
    "Job Start Date - Year": {
        "limited_response": False,
        "accepted_responses": [],
        "non_essential": True
    },
    "Address of Residence - Street": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Address of Residence - Apt. No.": {
        "limited_response": False,
        "accepted_responses": [],
        "non_essential": True
    },
    "Address of Residence - City": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Address of Residence - State": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Address of Residence - Zip": {
        "limited_response": False,
        "accepted_responses": []
    }
}

eda_institutional_information_labels = [
    "Training Provider",
    "Training Program",
    "Length of Program",
    "Environment Type",
    "Program Hours",
    "Soft Skills?",
    "Program Tuition Cost",
    "Type of Credential"
]

eda_institutional_information_accepted_responses = {
    "Training Provider": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Training Program": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Length of Program": {
        "limited_response": True,
        "accepted_responses": [
            "Less than 3 months",
            "3 – 6 months",
            "7 – 12 months",
            "13 – 24 months",
            "25 – 36 months",
            "37 – 48 months"
        ]
    },
    "Environment Type": {
        "limited_response": True,
        "accepted_responses": [
            "In-person",
            "Hybrid in-person and remote",
            "Permanently remote"
        ]
    },
    "Program Hours": {
        "limited_response": True,
        "accepted_responses": [
            "Full time program",
            "Part time program",
            "Program has the option to take breaks and return"
        ]
    },
    "Soft Skills?": {
        "limited_response": True,
        "accepted_responses": [
            "Yes",
            "No"
        ]
    },
    "Program Tuition Cost": {
        "limited_response": False,
        "accepted_responses": []
    },
    "Type of Credential": {
        "limited_response": True,
        "accepted_responses": [
            "Title IV Degree (Post-secondary educational degrees and certifications)",
            "Title IV Certificate (Post-secondary educational degrees and certifications)",
            "Non-Title IV Degree (Post-secondary educational degrees and certifications)",
            "Non-Title IV Certifications (Post-secondary educational degrees and certifications)",
            "Micro-credentials (MOOC Providers)",
            "Degrees from Foreign Universities (MOOC Providers)",
            "Course Completion Certifications (MOOC Providers)",
            "Occupational Licenses (Non-Academic Organizations)",
            "Occupational Certificates (Non-Academic Organizations)",
            "Registered Apprenticeships (Non-Academic Organizations)",
            "Unregistered Apprenticeships (Non-Academic Organizations)",
            "Coding Bootcamp Course Completion Certificate (Non-Academic Organizations)",
            "Online Course Completion Certificate (Non-Academic Organizations)",
            "Public School District Diplomas (Secondary Schools)",
            "Private School Diplomas (Secondary Schools)"
        ]
    }
}

eda_admissions_labels = [
    "Training Provider",
    "Training Program",
    "How many GJC participants recruited this quarter?",
    "How many GJC participants admitted this quarter?",
    "How many GJC participants enrolled this quarter?"
]

eda_training_completion_labels = [
    "Training Provider",
    "Training Program",
    "# GJC participants completed program?",
    "# GJC participants completed on time?",
    "# GJC participants completed but not continuous?"
]

eda_reason_for_non_completion_labels = [
    "Training Provider",
    "Training Program",
    "# GJC participants non-completing",
    "# GJC participants could not meet technical requirements",
    "# GJC participants withdrew due to family obligations",
    "# GJC participants withdrew due to physical health reasons",
    "# GJC participants withdrew due to mental health reasons",
    "# GJC participants withdrew due to lack of adequate transportation",
    "# GJC participants withdrew due to lack of childcare",
    "# GJC participants withdrew due to financial obligations (e.g. had to get a job)",
    "# GJC participants dismissed due to behavior",
    "# GJC participants dismissed for not meeting attendance requirements",
    "# GJC participants withdrew because they started a new job during training",
    "# GJC participants who withdrew for another reason",
    "Please specify other reason"
]

eda_employment_type_labels = [
    "Training Provider",
    "Training Program",
    "Full Time Employment",
    "Part-time Employment",
    "Seasonal Employment",
    "Earn and Learn Employment",
    "Other"
]

eda_earn_and_learn_labels = [
    "Training Provider",
    "Training Program",
    "Does your program include work-based learning opportunities?",
    "# GJC participants in a Registered Apprenticeship?",
    "# GJC participants in a Non-registered Apprenticeship?",
    "# GJC participants in an Internship",
    "# GJC participants in a customized training",
    "# GJC participants in an Incumbent Worker Training",
    "# GJC participants in another type of earn and learn"
]

eda_salaries_of_participants_labels = [
    "Training Provider",
    "Training Program",
    "Median Hourly Earnings - Full Employment",
    "Median Hourly Earnings - Part-time Employment",
    "Median Hourly Earnings - Seasonal Employment",
    "Median Hourly Earnings - Earn and Learn",
    "Median Hourly Earnings - Other",
    "What % of participants reported their salaries?"
]

eda_employment_status_after_6_months_labels = [
    "Training Provider",
    "Training Program",
    "Employed in field by employer who partners with training program",
    "Employed in field by employer who doesn't partner with training program",
    "Still seeking employment in field",
    "Not seeking employment in field",
    "Could not contact",
    "Top 3 occupational categories (NAICS)",
    "Top 3 employers"
]

workbook_definitions = {

    "TPI":{

    "standard":{

    # "Training_Provider_Database": {
    #     "labels": training_provider_database_labels,
    #     "columns_used": range(0, len(training_provider_database_labels)),
    #     "sheet_name": "Training_Provider_Database",
    #     "starting_row": 2,
    #     "accepted_responses": training_provider_database_accepted_responses_w_types,
    #     "starting_column": 0
    # },

    # "Institutional_Information": {
    #     "labels": institutional_information_labels,
    #     "columns_used": range(0, len(institutional_information_labels)),
    #     "sheet_name": "Institutional_Information",
    #     "starting_row": 2,
    #     "accepted_responses": institutional_information_accepted_responses_w_types,
    #     "starting_column": 0
    # },

    "Participant_Info": {
        "labels": participant_info_labels,
        "columns_used": None,
        "sheet_name": "Participant_Info",
        "starting_row": 0,
        "accepted_responses": participant_info_accepted_responses_w_types,
        "starting_column": 0
    },

    "Program_Enrollment":{
        "labels": program_enrollment_labels,
        "columns_used": None,
        "sheet_name": "Program_Enrollment",
        "starting_row": 0,
        "accepted_responses": program_enrollment_accepted_responses_w_types,
        "starting_column": 0
    },

    "Credential_Attainment":{
        "labels": credential_attainment_labels,
        "columns_used": None,
        "sheet_name": "Credential_Attainment",
        "starting_row": 0,
        "accepted_responses": credential_attainment_accepted_responses_w_types,
        "starting_column": 0
    },

    "Employment":{
        "labels": employment_labels,
        "columns_used": None,
        "sheet_name": "Employment",
        "starting_row": 0,
        "accepted_responses": employment_accepted_responses_w_types,
        "starting_column": 0
    },
    
    # "CWP_Participant_Info":{
    # "labels": cwp_participant_info_labels,
    # "columns_used": range(0, len(cwp_participant_info_labels)),
    # "sheet_name": "Participant_Info",
    # "is_supportive_services": False,
    # "starting_row": 2  
    # }


    } } ,
    "SS":{

    "Training_Provider_List":{
        "labels": training_provider_list_labels,
        "columns_used": range(0, len(training_provider_list_labels)),
        "sheet_name": "Training_Provider",
        "is_supportive_services": True,
        "starting_row": 2
    },

    "GJC_Funding":{
    "labels": gjc_funding_labels,
    "columns_used": range(0, len(gjc_funding_labels)),
    "sheet_name": "GJC_Funding",
    "is_supportive_services": True,
    "starting_row": 2 
    }
    },

    "EDA_Report":{

    "eda_Training_Provider":{
        "labels": eda_training_provider_labels,
        "columns_used": range(1, 23),
        "sheet_name": "Training Provider",
        "is_supportive_services": False,
        "starting_row": 6
    },

    "eda_Updated_List": {
        "labels": eda_updated_list_labels,
        "columns_used": range(0, len(eda_updated_list_labels)),  # A to C
        "sheet_name": "Updated_List",
        "is_supportive_services": False,
        "starting_row": 2
    },

    "eda_Participant_Database": {
        "labels": eda_participant_database_labels,
        "columns_used": range(0, len(eda_participant_database_labels)),  # Columns A to T
        "sheet_name": "Participant_Database",
        "is_supportive_services": False,
        "starting_row": 6
    },

    "eda_Institutional_Information": {
    "labels": eda_institutional_information_labels,
    "columns_used": range(1, len(eda_institutional_information_labels)+1),  # Starts at column B
    "sheet_name": "Institutional_Information",
    "is_supportive_services": False,
    "starting_row": 3
    },

    "eda_Admissions": {
    "labels": eda_admissions_labels,
    "columns_used": range(0, len(eda_admissions_labels)),  # Columns A to E
    "sheet_name": "Admissions",
    "is_supportive_services": False,
    "starting_row": 3
    },

    "eda_Training_Completion": {
    "labels": eda_training_completion_labels,
    "columns_used": range(0, len(eda_training_completion_labels)),  # Columns A to E
    "sheet_name": "Training Completion",
    "is_supportive_services": False,
    "starting_row": 3
    },

    "eda_Reason_for_Non_Completion": {
    "labels": eda_reason_for_non_completion_labels,
    "columns_used": range(0, len(eda_reason_for_non_completion_labels)),  # Columns A to O
    "sheet_name": "Reason for non-completion",
    "is_supportive_services": False,
    "starting_row": 4
    },

    "eda_Earn_and_Learn": {
    "labels": eda_earn_and_learn_labels,
    "columns_used": range(0, len(eda_earn_and_learn_labels)),  # Columns A to I
    "sheet_name": "Earn and Learn",
    "is_supportive_services": False,
    "starting_row": 4
    },

    "eda_Salaries_of_Participants": {
    "labels": eda_salaries_of_participants_labels,
    "columns_used": range(0, len(eda_salaries_of_participants_labels)),  # A to H
    "sheet_name": "Salaries of participants",
    "is_supportive_services": False,
    "starting_row": 4
    },  
    
    "eda_Employment_Status_after_6_months": {
    "labels": eda_employment_status_after_6_months_labels,
    "columns_used": range(0, len(eda_employment_status_after_6_months_labels)),  # A to I
    "sheet_name": "Employment Status (6 months)",
    "is_supportive_services": False,
    "starting_row": 4
    },

    },

    "Logic_Templates":{
        "specific_value": "is {values}",
        "not_specific_value": "is not {values}",
        "date_in_past": "is in the past",
        "not_date_in_past": "is not in the past",
        "date_in_past_different_sheet": "is in the past",
        "not_date_in_past_different_sheet": "is not in the past",
        "specific_value_different_sheet": "is {values}",
        "not_specific_value_different_sheet":"is not {values}"
    }
}

### this is for the program level sheet 

workbook_program_definitions = {

    "TPI":{

    "standard":{

    "Institutional_Information": {
        "labels": institutional_information_labels,
        "columns_used": None,
        "sheet_name": "Institutional_Information",
        "starting_row": 0,
        "accepted_responses": institutional_information_accepted_responses_w_types,
        "starting_column": 0
    }
    }
    }
    }