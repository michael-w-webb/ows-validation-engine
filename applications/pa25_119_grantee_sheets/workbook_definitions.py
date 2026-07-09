# Auto-generated dictionary file
# Generated: 2026-07-09 11:16:37.486409

"""

Workbook Definitions, Label Maps, and Schema Metadata
=====================================================

This module contains the authoritative schema specification for all
CareerConneCT “pa25_119 data” workbooks supported by the validation
pipeline. It encodes:

    • Canonical  names used throughout the pipeline  
    • All known spelling / formatting variants (“label maps”) that appear
      in provider-submitted Excel files  
    • -level metadata describing expected types, requirements, and
      accepted categorical responses  
    • Workbook-level structure (sheet names, starting rows/s, and
      schema for both *simple format* and *four-sheet format*)  
    • Logic template phrases used by natural-language rule descriptions  

These definitions serve as the central contract between:

    1. **WorkbookLoader** – to map raw header text → canonical names  
    2. **NormalizationEngine / Type classes** – to validate, clean,
       and coerce  values into standardized formats  
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

    • Match raw  headers from provider files  
    • Normalize them into predictable, canonical field names  
    • Tolerate typos, punctuation differences, capitalization,
      OWS-specific export labels, and Salesforce-style field names  

These maps are *lossless*: they never drop fields, they only expand the
set of acceptable  headers.

-----------------------------------------------------------------------
Accepted Responses and Types (“accepted_responses_w_types”)
-----------------------------------------------------------------------

Each canonical  has a metadata block describing:

    • type – one of the defined  classes
      (e.g., "dateTime", "categorical", "boolean", "identifier",
      "hourlyWage", "hoursWorked", "stateID7", "CIPCode", "ONETCode")

    • required – whether the field must be present and non-blank

    • accepted_responses – (optional) list of canonical categorical
      values used by categorical normalization and by
      CrossRuleEngine for logical operations

These definitions are consumed by:

    • Base subclasses during normalization  
    • CrossRuleEngine.get_variable() when creating Variable instances  
    • Rule authoring and error-message templates  

-----------------------------------------------------------------------
Workbook Structure (“workbook_definitions”)
-----------------------------------------------------------------------

The outer `workbook_definitions` object organizes schemas by:

    workbook_type → workbook_format → sheet_name → sheet_definition

For example:

    "pa25_119 data" →
        "simple format" →
            "Report" → {labels, accepted_responses, starting_row, ...}

        "four sheet format" →
            "Personal Information"
            "Training"
            "Credential"
            "Outcomes"

Each sheet definition includes:

    • labels – a full header normalization map  
    • accepted_responses – the  metadata schema  
    • starting_row – where data begins (allows skipping header clutter)  
    • starting_ – permits partial-sheet ingestion  
    • s_used – reserved for restricting the importable subset

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
       ensure that Base+Variable subclasses support the type
       before referencing it here  

All changes propagate automatically through:

    •  mapping  
    • Data normalization  
    • Cross-sheet rule evaluation  
    • Validation reporting  

This module is therefore the **single source of truth** for schema
consistency across every component of the CareerConneCT validation
pipeline.

"""
from applications.pa25_119_grantee_sheets.workbook_definition_dictionaries import DISABILITY_MAPPING, DISLOCATED_WORKER_MAPPING, EMPLOYMENT_STATUS_MAPPING, GENDER_MAPPING, INCUMBENT_WORKER_MAPPING, RACE_ETHNICITY_MAPPING, UC_MAPPING, WAGNER_PEYSER_MAPPING, YOUTH_PLACEMENT_MAPPING, YOUTH_SERVICES_MAPPING


simple_format_pa25_119_data_labels = {
    '1001 Date of First Basic Career Service (Staff-Assisted)': [
        '1001 Date of First Basic Career Service (Staff-Assisted)',
    ],
    '1002 Most Recent Date Received Basic Career Services (Self-Service/Information-Only)': [
        '1002 Most Recent Date Received Basic Career Services (Self-Service/Information-Only)',
    ],
    '1004 Date of Most Recent Career Service (WIOA)': [
        '1004 Date of Most Recent Career Service (WIOA)',
    ],
    '1007 Date of Most Recent Reportable Individual Contact': [
        '1007 Date of Most Recent Reportable Individual Contact',
    ],
    '105 Special Project ID - 1': [
        '105 Special Project ID - 1',
    ],
    '106 Special Project ID - 2': [
        '106 Special Project ID - 2',
    ],
    '107 Special Project ID - 3': [
        '107 Special Project ID - 3',
    ],
    '1200 Date of First Individualized Career Service': [
        '1200 Date of First Individualized Career Service',
    ],
    '1201 Most Recent Date Received Individualized Career Service': [
        '1201 Most Recent Date Received Individualized Career Service',
    ],
    '1205 Type of Work Experience': [
        '1205 Type of Work Experience',
    ],
    '12_month_date_benchmark': [
        '12 Month Date - benchmark',
    ],
    '12_months_employed': [
        '12 Months Continuously Employed',
    ],
    '1328 Training Provided Virtual/Online': [
        '1328 Training Provided Virtual/Online',
    ],
    '1331 Training Leading to an Associate Degree': [
        '1331 Training Leading to an Associate Degree',
    ],
    '1332 Participated in Postsecondary Education During Program Participation': [
        '1332 Participated in Postsecondary Education During Program Participation',
    ],
    '1332 Participated in Postsecondary Education During Program Participation (WIOA)': [
        '1332 Participated in Postsecondary Education During Program Participation (WIOA)',
    ],
    '1333 Received Private Sector Training': [
        '1333 Received Private Sector Training',
    ],
    '1333 Received training from program(s) operated by the private sector': [
        '1333 Received training from program(s) operated by the private sector',
    ],
    '1401 Enrolled in Secondary Education Program (WIOA)': [
        '1401 Enrolled in Secondary Education Program (WIOA)',
    ],
    '18_month_date_benchmark': [
        '18 Month Date - benchmark',
    ],
    '18_months_employed': [
        '18 Months Continuously Employed',
    ],
    '24_month_date_benchmark': [
        '24 Month Date - benchmark',
    ],
    '24_months_employed': [
        '24 Months Continuously Employed',
    ],
    '6_month_date_benchmark': [
        '6 Month Date - benchmark',
    ],
    '6_months_employed': [
        '6 Months Continuously Employed',
    ],
    '807 Displaced Homemaker at Program Entry (WIOA)': [
        '807 Displaced Homemaker at Program Entry (WIOA)',
    ],
    'Apt. Floor': [
        'Apt. Floor',
    ],
    'CATDLP': [
        'CATDLP',
    ],
    'CATP': [
        'CATP',
    ],
    'CDS eligibility': [
        'CDS eligibility',
    ],
    'CNA Certified Nursing Assistant - currently hold': [
        'CNA Certified Nursing Assistant - currently hold',
    ],
    'Certification appointment date': [
        'Certification appointment date',
    ],
    'Certification appointment location': [
        'Certification appointment location',
    ],
    'Citizenship': [
        'Citizenship',
    ],
    'Closure Date': [
        'Closure Date',
    ],
    'Co-Enrolled': [
        'Co-Enrolled',
    ],
    'Co-funded': [
        'Co-funded',
    ],
    'Communication': [
        'Communication',
    ],
    'Completed80PercProg': [
        'Completed80PercProg',
    ],
    'Contact Location or Method': [
        'Contact Location or Method',
    ],
    'Contextualized Education': [
        'Contextualized Education',
    ],
    'Core Services to Employers': [
        'Core Services to Employers',
    ],
    'Cover Letter': [
        'Cover Letter',
    ],
    'Cover Letter Completed': [
        'Cover Letter Completed',
    ],
    'Critical Thinking/Problem Solving': [
        'Critical Thinking/Problem Solving',
    ],
    'Culinary Work Experience': [
        'Culinary Work Experience',
    ],
    'Currently Enrolled in WIOA': [
        'Currently Enrolled in WIOA',
    ],
    'Customer Service': [
        'Customer Service',
    ],
    'Dancing': [
        'Dancing',
    ],
    'Data Entry/Typing WPM': [
        'Data Entry/Typing WPM',
    ],
    'Date Co-Enrolled': [
        'Date Co-Enrolled',
    ],
    'Date Referral Made': [
        'Date Referral Made',
    ],
    'Date Status Updated': [
        'Date Status Updated',
    ],
    'Date Taken': [
        'Date Taken',
    ],
    'Deobligation Amount': [
        'Deobligation Amount',
    ],
    'Developed By': [
        'Developed By',
    ],
    'Did this individual enter new employment?': [
        'Did this individual enter new employment?',
    ],
    'Did youth attend Job Readiness Training?': [
        'Did youth attend Job Readiness Training?',
    ],
    'Diversity and Inclusion': [
        'Diversity and Inclusion',
    ],
    'Do you currently receive, or have you received in the past six months, any of the following?': [
        'Do you currently receive, or have you received in the past six months, any of the following?',
    ],
    'Do you have an LLC?': [
        'Do you have an LLC?',
    ],
    'Do you have an updated resume?': [
        'Do you have an updated resume?',
    ],
    'Do you have medical insurance?': [
        'Do you have medical insurance?',
    ],
    'Do you have stable housing?': [
        'Do you have stable housing?',
    ],
    'Do you have your high school credential (diploma or GED)?': [
        'Do you have your high school credential (diploma or GED)?',
    ],
    'Do you own a vehicle?': [
        'Do you own a vehicle?',
    ],
    'Do you speak a language, other than English, If so what?': [
        'Do you speak a language, other than English, If so what?',
    ],
    'Drywall Work Experience': [
        'Drywall Work Experience',
    ],
    'EB': [
        'EB',
    ],
    'EB_Job Title': [
        'EB_Job Title',
    ],
    'EB_JobOfferSTatus': [
        'EB_JobOfferSTatus',
    ],
    'EB_Start_Date': [
        'EB_Start_Date',
    ],
    'EB_Step': [
        'EB_Step',
    ],
    'EB_Wage': [
        'EB_Wage',
    ],
    'Electrical Work Experience': [
        'Electrical Work Experience',
    ],
    'Email': [
        'Email',
    ],
    'Employment Management (Job Seeking)': [
        'Employment Management (Job Seeking)',
    ],
    'Employment Readiness': [
        'Employment Readiness',
    ],
    'Engagement and Employer Onboarding': [
        'Engagement and Employer Onboarding',
    ],
    'Enrolled': [
        'Enrolled',
    ],
    'Entity Subtype': [
        'Entity Subtype',
    ],
    'Entity Type': [
        'Entity Type',
    ],
    'Entity Unique Identifier': [
        'Entity Unique Identifier',
    ],
    'Estimated Days in Training': [
        'Estimated Days in Training',
    ],
    'Estimated Number of Slots': [
        'Estimated Number of Slots',
    ],
    'Ethnicity, Hispanic or Latino': [
        '210 Ethnicity: Hispanic / Latino (WIOA)',
        'Hispanic or Latino',
        'Hispanic or Latino (CWP)',
    ],
    'Final Placement Status': [
        'Final Placement Status',
    ],
    'First Name': [
        'First Name',
        'First name',
        'fname',
    ],
    'First Referral Date': [
        'First Referral Date',
    ],
    'General Construction Labor Work Experience': [
        'General Construction Labor Work Experience',
    ],
    'General Professionalism': [
        'General Professionalism',
    ],
    'HVAC Work Experience': [
        'HVAC Work Experience',
    ],
    'Have you attended any college or post-high school training?': [
        'Have you attended any college or post-high school training?',
    ],
    'Have you ever been incarcerated?': [
        'Have you ever been incarcerated?',
    ],
    'Have you ever owned a business?': [
        'Have you ever owned a business?',
    ],
    'Have you ever worked on a construction site?': [
        'Have you ever worked on a construction site?',
    ],
    'Have you participated in Summer Youth Program before?': [
        'Have you participated in Summer Youth Program before?',
    ],
    'Head of Household': [
        'Head of Household',
    ],
    'High School Diploma / GED': [
        'High School Diploma / GED',
    ],
    'Hire Count': [
        'Hire Count',
    ],
    'Hire Date': [
        'Hire Date',
    ],
    'Hired Permanently?': [
        'Hired Permanently?',
    ],
    'Hired by Worksite': [
        'Hired by Worksite',
    ],
    'How did you hear about this program?': [
        'How did you hear about this program?',
    ],
    'How many college credits have you earned?': [
        'How many college credits have you earned?',
    ],
    'How proficient are you with this language?': [
        'How proficient are you with this language?',
    ],
    'Identifier': [
        'Identifier',
    ],
    'If Other, please specify:': [
        'If Other, please specify:',
    ],
    'If earn and learn, type': [
        'If earn and learn, type',
    ],
    'If employed, did participant report hourly salary?': [
        'If employed, did participant report hourly salary?',
    ],
    'If other, describe': [
        'If other, describe',
    ],
    'If yes, how many years did you complete?': [
        'If yes, how many years did you complete?',
    ],
    'If yes, where and what did you do?': [
        'If yes, where and what did you do?',
    ],
    'If yes, where?': [
        'If yes, where?',
    ],
    'If you are attending college, Will you be going to college in fall?': [
        'If you are attending college, Will you be going to college in fall?',
    ],
    'IfNo-TerminationReason': [
        'IfNo-TerminationReason',
    ],
    'In the last 5 years, have you had an OSHA license?': [
        'In the last 5 years, have you had an OSHA license?',
    ],
    'Installation or Insulation Work Experience': [
        'Installation or Insulation Work Experience',
    ],
    'Intake Statuses': [
        'Intake Statuses',
    ],
    'Interested in: Computer Literacy': [
        'Interested in: Computer Literacy',
    ],
    'Interested in: Interview Preparation': [
        'Interested in: Interview Preparation',
    ],
    'Interested in: Resume Support': [
        'Interested in: Resume Support',
    ],
    'Interested in: Training': [
        'Interested in: Training',
    ],
    'Internet Search': [
        'Internet Search',
    ],
    'Interpersonal/Collaboration and Teamwork': [
        'Interpersonal/Collaboration and Teamwork',
    ],
    'Interview Date': [
        'Interview Date',
    ],
    'Is the vehicle registered and insured?': [
        'Is the vehicle registered and insured?',
    ],
    'Is this active military service?': [
        'Is this active military service?',
    ],
    'Is this job related to training received?': [
        'Is this job related to training received?',
    ],
    'JD End': [
        'JD End',
    ],
    'JD Exit Reason': [
        'JD Exit Reason',
    ],
    'JD Start': [
        'JD Start',
    ],
    'Job Application': [
        'Job Application',
    ],
    'Job Description': [
        'Job Description',
    ],
    'Job Developer': [
        'Job Developer',
    ],
    'Job Market': [
        'Job Market',
    ],
    'Job Referral': [
        'Job Referral',
    ],
    'Job Search': [
        'Job Search',
    ],
    'Jobs Funnel eligibility': [
        'Jobs Funnel eligibility',
    ],
    'LPN Licensed Practical Nurse - currently hold': [
        'LPN Licensed Practical Nurse - currently hold',
    ],
    'Labor Market and Employment Information Services are split across three areas.': [
        'Labor Market and Employment Information Services are split across three areas.',
    ],
    'Landscaping Work Experience': [
        'Landscaping Work Experience',
    ],
    'Last Modified': [
        'Last Modified',
    ],
    'Last Name': [
        'Last Name',
        'lname',
    ],
    'Length of Agreement (Days)': [
        'Length of Agreement (Days)',
    ],
    'Linking_ID': [
        'Linking_ID',
    ],
    'Low_AJC': [
        'Low_AJC',
    ],
    'MA Medical Assistant': [
        'MA Medical Assistant',
    ],
    'MPI Youth': [
        'MPI Youth',
    ],
    'Managing Region': [
        'Managing Region',
    ],
    'Manufacturing Machinist or CNC Work Experience': [
        'Manufacturing Machinist or CNC Work Experience',
    ],
    'Masonry Work Experience': [
        'Masonry Work Experience',
    ],
    'Medium_Remediation': [
        'Medium_Remediation',
    ],
    'Member of Populations': [
        'Member of Populations',
    ],
    'Microsoft Word, PowerPoint, Excel': [
        'Microsoft Word, PowerPoint, Excel',
    ],
    'Middle Name': [
        'Middle',
        'Middle Initial',
    ],
    'Mock Interview': [
        'Mock Interview',
    ],
    'NAACP eligibility': [
        'NAACP eligibility',
    ],
    'New Skills Acquired (select all that apply)': [
        'New Skills Acquired (select all that apply)',
    ],
    'No Longer Available': [
        'No Longer Available',
    ],
    'Number of Slots Filled': [
        'Number of Slots Filled',
    ],
    'Office Equipment (i.e. copier, fax machine, scanner, etc.)': [
        'Office Equipment (i.e. copier, fax machine, scanner, etc.)',
    ],
    'Other': [
        'Other',
    ],
    'Other Costs': [
        'Other Costs',
    ],
    'Other Program Recommendation': [
        'Other Program Recommendation',
    ],
    'Other Skills (NAICS code)': [
        'Other Skills (NAICS code)',
    ],
    'PY15': [
        'PY15',
    ],
    'PY16': [
        'PY16',
    ],
    'PY17': [
        'PY17',
    ],
    'PY18': [
        'PY18',
    ],
    'PY19': [
        'PY19',
    ],
    'PY20': [
        'PY20',
    ],
    'PY21': [
        'PY21',
    ],
    'PY22': [
        'PY22',
    ],
    'PY23': [
        'PY23',
    ],
    'PY24': [
        'PY24',
    ],
    'PY25': [
        'PY25',
    ],
    'Painting Work Experience': [
        'Painting Work Experience',
    ],
    'Parent or Corporate Entity': [
        'Parent or Corporate Entity',
    ],
    'Participant Site Identifier': [
        'Participant Site Identifier',
    ],
    'Participant Status': [
        'Participant Status',
    ],
    'Partnership Activities': [
        'Partnership Activities',
    ],
    'Payroll Type': [
        'Payroll Type',
    ],
    'Pell Grant': [
        'Pell Grant',
    ],
    'Permanently Closed': [
        'Permanently Closed',
    ],
    'Phone Number': [
        'Phone Number',
    ],
    'Placed at Worksite?': [
        'Placed at Worksite?',
    ],
    'Plays an instrument': [
        'Plays an instrument',
    ],
    'Plumbing Work Experience': [
        'Plumbing Work Experience',
    ],
    'Position': [
        'Position',
    ],
    'Post-Secondary Plans': [
        'Post-Secondary Plans',
    ],
    'Prefix': [
        'Prefix',
    ],
    'Professionalism': [
        'Professionalism',
    ],
    'Program Vendor': [
        'Program Vendor',
    ],
    'Projected Completion Date': [
        'Projected Completion Date',
    ],
    'Pronouns': [
        'Pronouns',
    ],
    'Prove IT': [
        'Prove IT',
    ],
    'Quadrant of Residency': [
        'Quadrant of Residency',
    ],
    'RN Registered Nurse - currently hold': [
        'RN Registered Nurse - currently hold',
    ],
    'Race': [
        'Race',
    ],
    'Race (CWP)': [
        'Race (CWP)',
    ],
    'Race - Self-Identify': [
        'Race - Self-Identify',
    ],
    'Race Ethnicity': [
        'Race Ethnicity',
    ],
    'Race, American Indian or Alaska Native': [
        '211 American Indian / Alaska Native (WIOA)',
    ],
    'Race, Asian': [
        '212 Asian (WIOA)',
    ],
    'Race, Black': [
        '213 Black / African American (WIOA)',
    ],
    'Race, Native Hawaiian or Other Pacific Islander': [
        '214 Native Hawaiian / Other Pacific Islander (WIOA)',
    ],
    'Race, White': [
        '215 White (WIOA)',
    ],
    'Race1': [
        'Race1',
    ],
    'Race2': [
        'Race2',
    ],
    'Race3': [
        'Race3',
    ],
    'Race4': [
        'Race4',
    ],
    'Reason for Referral': [
        'Reason for Referral',
    ],
    'Reason for Unfilled Slots': [
        'Reason for Unfilled Slots',
    ],
    'Reference Letters Completed': [
        'Reference Letters Completed',
    ],
    'Referral Closed': [
        'Referral Closed',
    ],
    'Referral Count': [
        'Referral Count',
    ],
    'Referral Status': [
        'Referral Status',
    ],
    'Referral to Workshop or Service': [
        'Referral to Workshop or Service',
    ],
    'Referred To': [
        'Referred To',
    ],
    'Registration Season(s)': [
        'Registration Season(s)',
    ],
    'Registration Year': [
        'Registration Year',
    ],
    'Registration Year:': [
        'Registration Year:',
    ],
    'Reporting Complete': [
        'Reporting Complete',
    ],
    'Resume Completed': [
        'Resume Completed',
    ],
    'Resume Creation': [
        'Resume Creation',
    ],
    'Resume Critique': [
        'Resume Critique',
    ],
    'Resume Revision': [
        'Resume Revision',
    ],
    'Secondary Education': [
        'Secondary Education',
    ],
    'SiMentor': [
        'SiMentor',
    ],
    'Special Requirements (check all that apply)': [
        'Special Requirements (check all that apply)',
    ],
    'Specify Other Post-Secondary Plans': [
        'Specify Other Post-Secondary Plans',
    ],
    'Specify Workshop or Service': [
        'Specify Workshop or Service',
    ],
    'Spoken Word or Poetry': [
        'Spoken Word or Poetry',
    ],
    'Status': [
        'Status',
    ],
    'Status Change': [
        'Status Change',
    ],
    'Status Change Date': [
        'Status Change Date',
    ],
    'Street Address': [
        'Street Address',
    ],
    'Student Key': [
        'Student Key',
    ],
    'Subsidized Loans': [
        'Subsidized Loans',
    ],
    'Summer Duties': [
        'Summer Duties',
    ],
    'Summer Worksite': [
        'Summer Worksite',
    ],
    'Swimming': [
        'Swimming',
    ],
    'Technology/Digital Literacy': [
        'Technology/Digital Literacy',
    ],
    'Test Score': [
        'Test Score',
    ],
    'Tests and Fees': [
        'Tests and Fees',
    ],
    'Tier': [
        'Tier',
    ],
    'Time/Self-Management': [
        'Time/Self-Management',
    ],
    'Total Number Provided': [
        'Total Number Provided',
    ],
    'Tracking Eligible': [
        'Tracking Eligible',
    ],
    'Training Class': [
        'Training Class',
    ],
    'Tuition': [
        'Tuition',
    ],
    'Tutoring': [
        'Tutoring',
    ],
    'Verification Date': [
        'Verification Date',
    ],
    'Visual Arts (Drawing, painting, etc)': [
        'Visual Arts (Drawing, painting, etc)',
    ],
    'Voucher Amendment Date': [
        'Voucher Amendment Date',
    ],
    'Voucher Award Date': [
        'Voucher Award Date',
    ],
    'Voucher Instance': [
        'Voucher Instance',
    ],
    'Voucher Status': [
        'Voucher Status',
    ],
    'We Rise eligibility': [
        'We Rise eligibility',
    ],
    'What are your career interests?': [
        'What are your career interests?',
    ],
    'What is the reason for this incentive?': [
        'What is the reason for this incentive?',
    ],
    'What is your current work eligibility status?': [
        'What is your current work eligibility status?',
    ],
    'What is your preferred language?': [
        'What is your preferred language?',
    ],
    'What is your race? Select one or more:': [
        'What is your race? Select one or more:',
    ],
    'What type of transportation will you be using to get to work?': [
        'What type of transportation will you be using to get to work?',
    ],
    'Which industries interest you for an intership?': [
        'Which industries interest you for an intership?',
    ],
    'Which program sector are you interested in ?': [
        'Which program sector are you interested in ?',
    ],
    'Which program training are you interested in?': [
        'Which program training are you interested in?',
    ],
    'Work Experience': [
        'Work Experience',
    ],
    'Workforce Region': [
        'Workforce Region',
    ],
    'Worksite': [
        'Worksite',
    ],
    'Worksite Assignment': [
        'Worksite Assignment',
    ],
    'Worksite Department': [
        'Worksite Department',
    ],
    'Worksite Number/location': [
        'Worksite Number/location',
    ],
    'Year-Round Worksite': [
        'Year-Round Worksite',
    ],
    'Year-Round Worksite Duties': [
        'Year-Round Worksite Duties',
    ],
    'Youth Active in program?': [
        'Youth Active in program?',
    ],
    'Youth Match Status': [
        'Youth Match Status',
    ],
    'access_to_flexible_work_schedule': [
        'Access to flexible work schedule?',
    ],
    'access_to_healthcare_benefits': [
        'Access to healthcare benefits through employer?',
        'Does this position offer health insurance?',
        'Medical Benefits?',
    ],
    'access_to_other_benefits': [
        'Other fringe Benefits?',
    ],
    'access_to_other_insurance': [
        'Does this position offer other insurance (dental, life, vision, etc.)?',
    ],
    'access_to_pto': [
        'Access to PTO benefits through employer?',
        'Does this position offer paid time off (personal, sick, vacation, etc.)?',
    ],
    'access_to_retirement_benefits': [
        'Access to retirement benefits?',
        'Does this position offer a retirement plan (401K, pension, etc.)?',
    ],
    'access_to_sick_leave': [
        'Access to sick leave?',
    ],
    'access_to_training_through_employer': [
        'Access to additional training through employer?',
    ],
    'accomodations_training_and_employment': [
        'Describe needed accommodations for training and employment',
    ],
    'accountability_exit_status': [
        '935 Accountability Exit Status',
    ],
    'achieving_below_grade_level': [
        'Achieving below grade level',
    ],
    'actual_completion_date': [
        'Actual Completion Date',
    ],
    'adapatability_continuous_learning': [
        'Adaptability/Continuous Learning',
    ],
    'address_1': [
        'Address 1',
    ],
    'address_2': [
        'Address 2',
    ],
    'adult_services': [
        '903 Adult (WIOA)',
    ],
    'adults_in_household': [
        'Including yourself, how many adults (ages 18 and older) currently live in your household?',
    ],
    'age': [
        'Age',
        'Age at Program Start',
    ],
    'agreement_end_date': [
        'Agreement End Date',
    ],
    'app_id': [
        'App ID',
    ],
    'applicant_household_eligible_for': [
        "Applicant's household is eligible for",
    ],
    'application_date': [
        'Application Date',
    ],
    'application_status': [
        'Application Status',
    ],
    'apprenticeship_program': [
        '931 Registered Apprenticeship Program',
    ],
    'arrested_or_convicted_of_crime': [
        '801 Ex-Offender Status at Program Entry',
        '801 Ex-Offender Status at Program Entry (WIOA)',
        'Have you ever been arrested or convicted of a crime?',
        'Have you ever been arrested?',
        'Have you ever been convicted of a crime?',
        'Offender',
    ],
    'asbestos_work_experience': [
        'Asbestos Work Experience',
        'Automotive Work Experience',
    ],
    'assessment_date': [
        'Assessment Date',
    ],
    'basic_skills_deficient': [
        '804 Basic Skills Deficient/Low Levels of Literacy at Program Entry',
        'Basic Skills Deficient',
        'Basic skills deficient',
    ],
    'best_chance_eligibility': [
        'Best Chance eligibility',
    ],
    'blue_hills_zone': [
        'Blue Hills Zone',
    ],
    'books_and_supplies_amount': [
        'Books and Supplies',
    ],
    'business/organization_size': [
        'Business/Organization Size',
    ],
    'business_summary_mission': [
        'Business Summary/Mission',
    ],
    'cadd': [
        'CADD (Computer Aided Drafting and Design)',
    ],
    'cahp': [
        'CAHP',
    ],
    'career_awareness': [
        'Career Awareness',
    ],
    'career_connect': [
        'CareerConneCT',
    ],
    'career_exploration': [
        'Career Exploration',
    ],
    'career_interest': [
        'Career Interest',
    ],
    'career_interest_inventory': [
        'Career Interest Inventory',
    ],
    'career_pathways_interest': [
        'Career Pathways Interests',
    ],
    'carpentry_work_experience': [
        'Carpentry Work Experience',
    ],
    'case_number': [
        'Case Number',
    ],
    'cash_assistance': [
        'Cash Assistance',
    ],
    'cct_program_recommendation': [
        'Career ConneCT Program Recommendation',
    ],
    'change_related_to_training': [
        'Is this change related to training received?',
    ],
    'childcare': [
        'Childcare',
        'What types of support will you need to be successful in a training/workforce program: Childcare',
    ],
    'children_in_household': [
        'Including yourself, how many children (ages 17 and younger) currently live in your household?',
    ],
    'cip_training_1': [
        'Career ConneCT Training Provider CIP Code',
        'Training CIP Code',
    ],
    'cohort_enrollment_date': [
        'Cohort - Enrollment Date',
    ],
    'completed_returned_to_hs': [
        'Completed-Returned to HS',
    ],
    'counseling_services': [
        'Counseling Services',
    ],
    'credential_issuer': [
        'Credential Issuer',
    ],
    'credential_name': [
        'Credential Name',
    ],
    'credential_received': [
        'Credential Received',
    ],
    'credential_type_1': [
        '1800 Type of Recognized Credential (WIOA)',
        '1800 Type of Recognized Credential 1',
        'Credential 1 Type',
        'Credential Type',
        'Type of Recognized Credential 1',
    ],
    'credential_type_2': [
        '1802 Type of Recognized Credential #2 (WIOA)',
        '1802 Type of Recognized Credential 2',
        'Credential 2 Type',
        'Type of Recognized Credential 2',
    ],
    'credential_type_3': [
        '1804 Type of Recognized Credential #3 (WIOA)',
        '1804 Type of Recognized Credential 3',
        'Credential 3 Type',
        'Type of Recognized Credential 3',
    ],
    'credential_type_4': [
        'Credential 4 Type',
        'Type of Recognized Credential 4',
    ],
    'credential_type_5': [
        'Credential 5 Type',
        'Type of Recognized Credential 5',
    ],
    'credentials_obtained': [
        'Credentials Obtained',
    ],
    'cssd_referral': [
        'CSSD Referral',
    ],
    'cthires_id': [
        'CTHires State ID',
        'CTHires User ID',
        'CTHires UserID',
    ],
    'cultural_barriers_at_program_entry': [
        '805 Cultural Barriers at Program Entry (WIOA)',
    ],
    'current_housing_situation_stable': [
        'Current Housing Situation Stable',
    ],
    'current_scholarship_amount': [
        'Current Scholarship Amount',
    ],
    'current_school': [
        'Current School',
        'School',
        'School or Program Name',
    ],
    'currently_attending': [
        'Are you currently attending?',
    ],
    'currently_needs_assistance_accomodations_for_training_and_employment': [
        'Currently Needs Assistance: Accommodations for Training and Employment',
    ],
    'currently_needs_assistance_acquiring_eligibility_documentation': [
        'Currently needs assistance: Acquiring Eligibility Documentation',
    ],
    'currently_needs_assistance_books_and_supplies': [
        'Currently Needs Assistance: Books and Supplies',
    ],
    'currently_needs_assistance_childcare': [
        'Currently Needs Assistance: Childcare',
    ],
    'currently_needs_assistance_complete_education_program_or_secure_and_maintain_employment': [
        'Needs additional assistance to complete an education program or secure and maintain employment',
    ],
    'currently_needs_assistance_educational_testing': [
        'Currently Needs Assistance: Educational Testing',
    ],
    'currently_needs_assistance_housing': [
        'Currently Needs Assistance: Housing',
    ],
    'currently_needs_assistance_legal_aid_services': [
        'Currently Needs Assistance: Legal Aid Services',
    ],
    'currently_needs_assistance_securing_food': [
        'Currently Needs Assistance: Securing Food',
    ],
    'currently_needs_assistance_tests_and_certifications': [
        'Currently Needs Assistance: Tests and Certifications',
    ],
    'currently_needs_assistance_transportation': [
        'Currently Needs Assistance: Transportation',
    ],
    'currently_needs_assistance_work_apparel_or_gear': [
        'Currently Needs Assistance: Work Apparel or Gear',
    ],
    'date_actual_dislocation': [
        '410 Date of Actual Dislocation',
    ],
    'date_attained_recognized_credential_4': [
        'Date Attained Recognized Credential 4',
    ],
    'date_attained_recognized_credential_5': [
        'Date Attained Recognized Credential 5',
    ],
    'date_change_occured': [
        'Date Change Occurred',
    ],
    'date_completed_mid_program_in_education_or_training_program_leading_to_credential_or_employment': [
        '1813 Date Completed During Program Participation an Education or Training Program Leading to a Recognized Credential or Employment',
        '1813 Date Completed, During Program Participation, an Education or Training Program Leading to a Recognized Postsecondary Credential or Employment (WIOA)',
    ],
    'date_contact_initiated': [
        'Dt_Contact_Initiated',
    ],
    'date_credential_1': [
        '1801 Date Attained Recognized Credential (WIOA)',
        '1801 Date Attained Recognized Credential 1',
    ],
    'date_credential_2': [
        '1803 Date Attained Recognized Credential #2 (WIOA)',
        '1803 Date Attained Recognized Credential 2',
    ],
    'date_credential_3': [
        '1805 Date Attained Recognized Credential #3 (WIOA)',
        '1805 Date Attained Recognized Credential 3',
    ],
    'date_enrolled_mid_program_in_education_or_training_program_leading_to_credential_or_employment': [
        '1811 Date Enrolled During Program Participation in an Education or Training Program Leading to a Recognized Credential or Employment',
        '1811 Date Enrolled During Program Participation in an Education or Training Program Leading to a Recognized Postsecondary Credential or Employment (WIOA)',
    ],
    'date_entered_training_1': [
        '1302 Date Entered Training #1 (WIOA)',
        '1302 Date Entered Training 1',
        'Date Entered Training',
        'Date Entered Training 1',
        'Start Date',
        'Start Dt',
        'Training Start Date',
    ],
    'date_entered_training_2': [
        '1309 Date Entered Training #2',
        '1309 Date Entered Training 2',
        'Date Entered Training 2',
        'Start Date_2',
    ],
    'date_entered_training_3': [
        '1314 Date Entered Training #3',
        '1314 Date Entered Training 3',
        'Date Entered Training 3',
    ],
    'date_first_dwg_service': [
        '933 Date of First DWG Service',
    ],
    'date_most_recent_contact': [
        'Dt_Successful_Contact',
    ],
    'date_of_birth': [
        '200 Date of Birth',
        'DOB',
        'Date of Birth',
        'birthday',
    ],
    'date_program_entry': [
        '900 Date of Program Entry',
        '900 Date of Program Entry (WIOA)',
        'Date of Program Entry',
    ],
    'date_program_exit': [
        '901 Date of Program Exit',
        '901 Date of Program Exit (WIOA)',
        'Date of Program Exit',
    ],
    'date_received_assessment_services': [
        '2103 Most Recent Date Received Assessment Services',
    ],
    'date_received_credential_1': [
        'Date Attained Recognized Credential 1',
        'Date Credential Attained',
        'Date Credential Obtained',
    ],
    'date_received_credential_2': [
        'Date Attained Recognized Credential 2',
    ],
    'date_received_credential_3': [
        'Date Attained Recognized Credential 3',
    ],
    'date_scheduled_orientation': [
        'Sched_Orientation_Dt',
    ],
    'date_skill_gains_educational_functioning_level': [
        '1806 Date of Most Recent Measurable Skill Gains: Educational Functioning Level (EFL) (WIOA)',
    ],
    'date_skill_gains_postsecondary_transcript_report_card': [
        '1807 Date of Most Recent Measurable Skill Gains: Postsecondary Transcript/Report Card (WIOA)',
    ],
    'date_skill_gains_secondary_transcript_report_card': [
        '1808 Date of Most Recent Measurable Skill Gains: Secondary Transcript/Report Card (WIOA)',
    ],
    'date_skill_gains_skills_progression': [
        '1810 Date of Most Recent Measurable Skill Gains: Skills Progression',
        '1810 Date of Most Recent Measurable Skill Gains: Skills Progression (WIOA)',
    ],
    'date_skill_gains_training_milestone': [
        '1809 Date of Most Recent Measurable Skill Gains: Training Milestone',
        '1809 Date of Most Recent Measurable Skill Gains: Training Milestone (WIOA)',
    ],
    'date_taken': [
        'Date Taken',
    ],
    'date_taken_service_delivery': [
        'Date Taken',
    ],
    'date_training_completed_1': [
        '1308 Date Completed or Withdrew from Training 1',
        '1308 Date Completed, or Withdrew from, Training #1',
        'Date Completed Training',
        'Date Completed or Withdrew from Training 1',
        'End Date',
        'Training End Date',
    ],
    'date_training_completed_2': [
        '1313 Date Completed or Withdrew from Training 2',
        '1313 Date Completed, or Withdrew from, Training #2',
        'Date Completed or Withdrew from Training 2',
        'End Date_2',
    ],
    'date_training_completed_3': [
        '1318 Date Completed or Withdrew from Training 3',
        '1318 Date Completed, or Withdrew from, Training #3',
        'Date Completed or Withdrew from Training 3',
    ],
    'days_in_training': [
        'Actual Days in Training',
    ],
    'detailed_status': [
        'Detailed Status',
    ],
    'disability': [
        '202 Individual with a Disability (WIOA)',
        '203 Category of Disability',
        'Are you an ADS(Aging Disability Services) participant?',
        'Disability',
        'Do you have a disability?',
        'Youth with a disability and / or special needs',
    ],
    'dislocated_worker': [
        '904 Dislocated Worker',
        '904 Dislocated Worker (WIOA)',
    ],
    'driver_license': [
        "Do you have a valid driver's license?",
        "Do you have an active driver's license?",
    ],
    'eligibility_1': [
        'Eligibility1',
    ],
    'eligibility_2': [
        'Eligibility2',
    ],
    'eligibility_3': [
        'Eligibility3',
    ],
    'employer': [
        'Employer',
        'Employer Name',
    ],
    'employer_entity_name': [
        'Entity Name',
    ],
    'employer_zip_code': [
        'Employer Zip Code',
        'Zip Code',
    ],
    'employment_and_training_services_related_to_snap': [
        '921 Employment and Training Services Related to SNAP',
    ],
    'employment_hours_worked': [
        'Average Hours per Week',
        'Hours',
    ],
    'employment_job_title': [
        'Job Title',
    ],
    'employment_match_method_1q_after_exit': [
        '1601 Type of Employment Match 1st Quarter After Exit Quarter (WIOA)',
    ],
    'employment_match_method_2q_after_exit': [
        '1603 Type of Employment Match 2nd Quarter After Exit Quarter (WIOA)',
    ],
    'employment_match_method_3q_after_exit': [
        '1605 Type of Employment Match 3rd Quarter After Exit Quarter (WIOA)',
    ],
    'employment_match_method_4q_after_exit': [
        '1607 Type of Employment Match 4th Quarter After Exit Quarter (WIOA)',
    ],
    'employment_naics': [
        'NAICS 2 Digit Code',
        'NAICS 6 Digit Code',
        'NAICS 6 Digit Description',
        'Occupation (NAICS) code',
    ],
    'employment_naics_q1': [
        '1614 Industry Code of Employment 1st Quarter After Exit Quarter',
    ],
    'employment_naics_q2': [
        '1615 Industry Code of Employment 2nd Quarter After Exit Quarter',
    ],
    'employment_naics_q3': [
        '1616 Industry Code of Employment 3rd Quarter After Exit Quarter',
    ],
    'employment_naics_q4': [
        '1617 Industry Code of Employment 4th Quarter After Exit Quarter',
    ],
    'employment_onet': [
        'O*NET Code',
    ],
    'employment_onet_q1': [
        '1610 Occupational Code (if available)',
        'O*NET Code',
        'Occupational Code of Employment after Exit',
    ],
    'employment_onet_q2': [
        '1612 Occupational Code of Employment 2nd Quarter After Exit Quarter (If available)',
        'Occupational Code of Employment 2nd Quarter after Exit Quarter',
    ],
    'employment_onet_q4': [
        '1613 Occupational Code of Employment 4th Quarter After Exit Quarter (If available)',
        'Occupational Code of Employment 4th Quarter after Exit Quarter',
    ],
    'employment_related_to_training_2q_after_exit': [
        '1608 Employment Related to Training (2nd Quarter After Exit) (WIOA)',
        'Employment Related to Training (2nd Quarter after Exit)',
    ],
    'employment_start_date': [
        '2118 Date Entered Employment',
        '2118 Date Entered Employment (Discretionary Grants)',
        'Employment Start Date',
        'Employment Type',
        'Job Start Date',
        'Start Date',
    ],
    'employment_status_2q_after_exit': [
        '1602 Employed in 2nd Quarter After Exit Quarter (WIOA)',
    ],
    'employment_status_3q_after_exit': [
        '1604 Employed in 3rd Quarter After Exit Quarter (WIOA)',
    ],
    'employment_status_4q_after_exit': [
        '1606 Employed in 4th Quarter After Exit Quarter (WIOA)',
    ],
    'employment_status_after_exit_q1': [
        '1600 Employed in 1st Quarter After Exit Quarter (WIOA)',
    ],
    'employment_status_at_exit': [
        'Completed-Employed',
        'Completed-Enrolled in PSEd or Adv Trng or Mil',
        'Employment Status',
        'Employment Status at Exit',
        'Employment Status at Placement End',
        'Outcome-Employed?',
    ],
    'employment_status_at_start': [
        '400 Employment Status at Program Entry (WIOA)',
        'Are you currently employed?',
        'Currently Working',
        'Employed at Enrollment',
        'Employment Status at Intake',
        'employment_status',
    ],
    'employment_town': [
        'Town',
    ],
    'end_date_funding': [
        'End Date',
    ],
    'end_reason': [
        'Non-Completion Exit Reason',
        'Why did this employment end?',
    ],
    'end_reason_for_funding_history': [
        'End Reason',
    ],
    'end_reason_for_training_record': [
        'Reason Did Not Complete',
    ],
    'english_language_learner': [
        '803 English Language Learner at Program Entry (WIOA)',
        'Are you an English language learner?',
        'English Language Learner',
    ],
    'enrolled_in_training_program': [
        'Did this individual enroll in a training program?',
    ],
    'enrollment_grade_level': [
        'Current Grade',
        'Current Grade:',
        'Grade Level',
        'Present Grade',
    ],
    'enrollment_gross_annual_income': [
        'What is your current gross annual household income (total income of all household members)?',
    ],
    'enrollment_start_date': [
        'Enrollment Date (start date)',
    ],
    'entered_non_traditional_employment': [
        '1611 Entered Non-Traditional Employment',
    ],
    'entered_training_related_employment': [
        '2126 Entered Training-Related Employment',
        '2126 Entered Training-Related Employment after Training Program Completion',
    ],
    'entrepreneurship': [
        'Entrepreneurial Education',
        'Entrepreneurship',
    ],
    'estimated_financial_aid': [
        'Estimated Financial Aid',
    ],
    'ethnicity': [
        'Ethnicity',
    ],
    'experience_carpentry': [
        'experience_carpentry',
    ],
    'experience_drafting': [
        'experience_drafting',
    ],
    'experience_electrical': [
        'experience_electrical',
    ],
    'experience_enginerepair': [
        'experience_enginerepair',
    ],
    'experience_excel': [
        'experience_excel',
    ],
    'experience_generalrepairs': [
        'experience_generalrepairs',
    ],
    'experience_machining': [
        'experience_machining',
    ],
    'experience_painting': [
        'experience_painting',
    ],
    'experience_pipefitting': [
        'experience_pipefitting',
    ],
    'experience_planning': [
        'experience_planning',
    ],
    'experience_plastics': [
        'experience_plastics',
    ],
    'experience_rigging': [
        'experience_rigging',
    ],
    'experience_sheetmetal': [
        'experience_sheetmetal',
    ],
    'experience_sheetmetal_plastics': [
        'experience_sheetmetal_plastics',
    ],
    'experience_shipfitting': [
        'experience_shipfitting',
    ],
    'experience_welding': [
        'experience_welding',
    ],
    'final_scholarship_amount': [
        'Final Scholarship Amount',
    ],
    'financial_literacy': [
        'Financial Literacy',
    ],
    'financial_support': [
        'What types of support will you need to be successful in a training/workforce program: Financial Support',
    ],
    'first_job': [
        'First Job',
    ],
    'first_language_english': [
        'First Language English',
    ],
    'food': [
        'Food',
    ],
    'food_and_nutrition': [
        'What types of support will you need to be successful in a training/workforce program: Food and Nutrition',
    ],
    'foster_care': [
        '704 Foster Care Youth Status at Program Entry (WIOA)',
        'Foster Care/Ward of State',
    ],
    'funding_source': [
        'Funding',
        'Funding Source',
        'Select the funding source.',
    ],
    'funding_start_date?': [
        'Start Date',
    ],
    'gender': [
        '201 Sex (WIOA)',
        'Gender',
        'Gender Identity - Self-Identify',
        'gender',
    ],
    'graduating_senior': [
        'Graduating Senior',
    ],
    'graduation_year': [
        'Graduation Year',
    ],
    'green_job': [
        'Is this a green job?',
    ],
    'gross_annual_income': [
        'Annualized Family Income',
        'Family Income',
    ],
    'hartford_promise_zone': [
        'Hartford Promise Zone',
    ],
    'have_you_been_impacted_by_covid_19?': [
        'Have you been impacted by COVID-19?',
    ],
    'head_of_household': [
        'Are you the head of household?',
    ],
    'healthcare': [
        'What types of support will you need to be successful in a training/workforce program: Healthcare',
    ],
    'high_passed': [
        'High_Passed',
    ],
    'high_school_diploma': [
        'High School Diploma or GED',
    ],
    'high_school_dropout': [
        'Are you a high school dropout?',
        'School Dropout',
    ],
    'highest_education_level_completed_at_program_entry': [
        '407 Highest School Grade Completed at Program Entry (WIOA)',
        '408 Highest Educational Level Completed at Program Entry (WIOA)',
        'Highest Education Level Completed at Program Entry',
        'Highest Education Level Obtained',
        'Highest Grade Completed',
        'Highest Level of Education at Intake',
        'Last Grade Completed',
        'What is your highest level of grade school education completed?',
        'What is your highest level of post-secondary education completed?',
        'highest_grade completed',
    ],
    'homeless_at_risk': [
        'Currently at Risk of Homelessness',
    ],
    'homeless_or_runaway': [
        '800 Homeless participant, Homeless Children and Youths, or Runaway Youth at Program Entry (WIOA)',
        'Are you currently homeless?',
        'Homeless',
        'Homeless at time of registration',
        'Runaway',
    ],
    'hourly_wage_at_exit': [
        'Hourly Earnings',
        'Hourly Wage',
        'Hourly Wage at Exit',
    ],
    'hourly_wage_at_worksite': [
        'Hourly Pay Rate',
    ],
    'hours_wk_2': [
        'Hours-Wk_2',
    ],
    'household_size': [
        'Family Size',
        'Total Family Members in Household (including yourself):',
    ],
    'housing': [
        'Housing',
        'What types of support will you need to be successful in a training/workforce program: Housing',
    ],
    'how_long_work_construction_and_what_did_you_do': [
        'How long did you work construction and what did you do?',
    ],
    'hps_credit_recovery_cohort': [
        'HPS Credit Recovery Cohort',
    ],
    'incentive_amount': [
        'What was the incentive value?',
    ],
    'incentive_form': [
        'What was the incentive form?',
    ],
    'incumbent_worker_advanced_to_new_position_1q_after_completion': [
        '2120 Incumbent Workers Advanced into a New Position with Current or New Employer in the 1st Quarter after Completion',
        '2120 Incumbent Workers Advanced into a New Position with Current or New Employer in the 1st Quarter after Training Program Completion',
    ],
    'incumbent_worker_advanced_to_new_position_2q_after_completion': [
        '2121 Incumbent Workers Retained Current Position in the 2nd Quarter after Training Program Completion',
        '2122 Incumbent Workers Advanced into a New Position with Current Employer or New Employer in the 2nd Quarter after Training Program Completion',
        '2122 Incumbent Workers Advanced into a New Position with Current or New Employer in the 2nd Quarter after Training Program Completion',
    ],
    'incumbent_worker_advanced_to_new_position_3q_after_completion': [
        '2123 Incumbent Workers Retained Current Position in the 3rd Quarter after Training Program Completion',
        '2124 Incumbent Workers Advanced into a New Position with Current or New Employer in the 3rd Quarter after Training Program Completion',
    ],
    'incumbent_worker_retained_position': [
        '2119 Incumbent Workers Retained Current Position',
    ],
    'incumbent_worker_retained_position_1q_after_completion': [
        '2119 Incumbent Workers Retained Current Position in the 1st Quarter after Training Program Completion',
    ],
    'incumbent_worker_training': [
        '907 Recipient of Incumbent Worker Training',
    ],
    'industry': [
        'Industry',
    ],
    'initial_scholarship_amount': [
        'Initial Scholarship Amount',
    ],
    'interested_in_employment_search_support': [
        'Interested in: Employment Search Support',
    ],
    'interested_working_outside': [
        'Are you interested in working outside?',
    ],
    'interested_working_with_computers': [
        'Are you interested in working with computers?',
    ],
    'interested_working_with_dress_code_in_professional_setting': [
        'Are you interested in working with a dress code in a professional setting?',
    ],
    'jfes': [
        'Currently Enrolled in JFES',
        'JFES',
    ],
    'job_readiness': [
        'Job Readiness',
    ],
    'job_shadowing': [
        'Job Shadowing',
    ],
    'job_title': [
        'Job Title',
    ],
    'job_title_2': [
        'Job Title_2',
    ],
    'justice_involved': [
        'Justice Involved',
        'Justice-Involved',
    ],
    'last_date_of_employment': [
        'What was the last date of employment?',
    ],
    'leadership_development': [
        'Leadership Dev',
        'Leadership Development',
    ],
    'legal_aid': [
        'What types of support will you need to be successful in a training/workforce program: Legal Aid',
    ],
    'legally_allowed_to_work_in_us': [
        'Are you legally allowed to work in US?',
        'Are you legally allowed to work in the United States?',
        'Legally Allowed to Work in US',
    ],
    'level_up_referral': [
        'Level Up Referral',
    ],
    'long_term_unemployed_at_program_entry': [
        '402 Long-Term Unemployed at Program Entry (WIOA)',
        'Has the participant been unemployed for 27 or more consecutive weeks?',
    ],
    'longest_employed_with_one_employer': [
        'What is the longest amount of time you have worked for an employer?',
    ],
    'low_income': [
        '802 Low Income Status at Program Entry (WIOA)',
        'Does the participant qualify as low income?',
        'Low Income',
        'Meets Definition of Low Income',
    ],
    'lunch_status': [
        'Eligible Free Lunch',
        'Lunch Status',
    ],
    'manufacturing_experience': [
        'manufacturing_experience',
    ],
    'marital_status': [
        'Marital Status',
    ],
    'mental_health': [
        'Mental Health',
    ],
    'mentoring': [
        'Mentoring',
    ],
    'migrant_and_seasonal_farmworker': [
        '808 Eligible Migrant and Seasonal Farmworker Status (WIOA sec. 167)',
    ],
    'monitoring_status': [
        'Monitoring Status',
    ],
    'most_recent_date_basic_career_services': [
        '1003 Most Recent Date Received Basic Career Services (Staff-Assisted)',
    ],
    'most_recent_date_follow_up_service': [
        '1503 Most Recent Date Received Follow-up Service',
    ],
    'most_recent_date_supportive_services': [
        '1409 Most Recent Date Received Supportive Services',
    ],
    'most_recent_job_days_employed': [
        'Days Employed',
    ],
    'most_recent_job_hourly_wage': [
        'For your most recent job, what was your hourly wage?',
        'Hourly Wage in Most Recent Employment Prior to Participation',
    ],
    'most_recent_job_hours_worked': [
        'For your most recent job, how many hours did you work each week, on average?',
        'Hours Worked per Week',
        'Hours Worked per Week Most Recent Employment Prior to Participation',
        'Weekly Hours (Est.)',
    ],
    'most_recent_job_industry': [
        'For your most recent job, what was the industry?',
    ],
    'most_recent_job_last_date_of_employment': [
        'For your most recent job, what was your last date of employment?',
    ],
    'most_recent_job_onet': [
        '403 Occupational Code of Most Recent Employment Prior to Participation (if available)',
        'Enter O*NET code for most recent job.',
        'Occupational Code of Most Recent Employment Prior to Participation',
    ],
    'most_recent_job_title': [
        'For your most recent job, what was the job title?',
    ],
    'most_recent_sye_participation': [
        'Most Recent SYE Participation',
    ],
    'national_dislocated_workers_grant': [
        '932 National Dislocated Worker Grants (DWG)',
    ],
    'occupational_skills_training': [
        'Occupational Skills Training',
        'Occupational Skills Trng',
    ],
    'onet_training_1': [
        '1306 Occupational Skills Training Code #1',
        '1306 Occupational Skills Training Code 1',
        'O*NET Code',
        'O*NET-SOC Code (XX-XXXX.XX)',
        'Occupational Skills Training Code 1',
    ],
    'onet_training_2': [
        '1311 Occupational Skills Training Code #2',
        '1311 Occupational Skills Training Code 2',
        'Occupational Skills Training Code 2',
    ],
    'onet_training_3': [
        '1316 Occupational Skills Training Code #3',
        '1316 Occupational Skills Training Code 3',
        'Occupational Skills Training Code 3',
    ],
    'organization': [
        'Organization',
    ],
    'orientation_s_or_ns': [
        'Orientation S or NS',
    ],
    'other_barriers_1': [
        'Other Barrier (1)',
        'Other Barriers',
    ],
    'other_barriers_2': [
        'Other Barrier (2)',
    ],
    'other_public_assistance_recipient': [
        '604 Other Public Assistance Recipient',
    ],
    'other_reasons_for_exit': [
        '923 Other Reasons for Exit',
        '923 Other Reasons for Exit (WIOA)',
    ],
    'other_supportive_services': [
        'Other Supportive Services',
    ],
    'other_work/trade_certifications': [
        'Do you have any other work or trade certifications? If yes, please explain.',
    ],
    'paid_competency_training_hours': [
        'Paid Competency Training Hours',
    ],
    'paid_worksite_hours': [
        'Paid Worksite Hours',
    ],
    'parent_or_pregnant': [
        '701 Pregnant or Parenting Youth',
        "Applicant's household is pregnant or is a custodial parent",
        'Are you currently a parent?',
        'Parent',
        'Pregnant or Parent',
    ],
    'past_participant_in_cyep': [
        'Past Participant in CYEP',
    ],
    'pathways': [
        'Pathways',
    ],
    'permit_or_driver_license': [
        'Currently Has Learnerâ€™s Permit or Driverâ€™s License',
    ],
    'placement_made_through_program': [
        'Was this placement made through this program?',
    ],
    'portal_application_date': [
        'Portal application Date',
    ],
    'post_secondary_transition_activities': [
        'Post-Secondary Transition Activities',
    ],
    'pre_apprenticeship': [
        'Pre-apprenticeship',
    ],
    'primary_funding': [
        'Primary Funding',
    ],
    'primary_funding_other': [
        'Primary Funding-Other',
    ],
    'primary_training_funding': [
        'Primary Training Funding',
    ],
    'primary_type_training_service_for_training_activity_1': [
        '2109 Primary Type of Training Service for Training Activity 1',
    ],
    'primary_type_training_service_for_training_activity_2': [
        '2112 Primary Type of Training Service for Training Activity 2',
    ],
    'primary_type_training_service_for_training_activity_3': [
        '2115 Primary Type of Training Service for Training Activity 3',
    ],
    'program_operator': [
        'Program Operator',
    ],
    'provider': [
        'Provider',
    ],
    'race/ethnicity': [
        'race/ethnicity',
    ],
    'rapid_response': [
        '908 Rapid Response',
    ],
    'rapid_response_additional_assistance': [
        '909 Rapid Response (Additional Assistance)',
    ],
    'received_needs_related_payments': [
        '1500 Received Needs-Related Payments',
    ],
    'received_training': [
        '1300 Received Training',
        '1300 Received Training (WIOA)',
        'Received Training',
    ],
    'receiving_dcf_or_foster_care_services': [
        'Appliciant is receiving DCF Services',
        'DCF Involved',
        'Foster Care or DCF',
    ],
    'referral_source': [
        'referral_source',
    ],
    'registered_apprenticeship': [
        'Is this a registered apprenticeship?',
    ],
    'registered_selective_service': [
        'Are you registered for Selective Service?',
        'Are you registered for selective service?',
    ],
    'registration_submission_date': [
        'Registration Submitted Date:',
    ],
    'reliable_transportation': [
        'Do you have reliable transportation?',
        'Do you have trouble getting to work?',
    ],
    'resume': [
        'Resume',
    ],
    'retention_with_same_employer_2q_and_4q': [
        '1618 Retention with the same employer in the 2nd Quarter and the 4th Quarter (WIOA)',
    ],
    'saga': [
        'Do you currently receive, or have you received in the past six months, any of the following: State Administered General Assistance',
        'Do you currently receive, or have you received in the past six months: State Adminstered General Assistance',
    ],
    'sasid': [
        'SASID',
    ],
    'scheduled_end_date': [
        'Est End Dt',
        'Projected End Date',
        'Scheduled End Date',
    ],
    'scheduled_start_date': [
        'Agreement Start Date',
        'Est Start Dt',
        'Scheduled Start Date',
    ],
    'school_status_at_exit': [
        'Education Status at Placement End',
        'School Status at Exit',
    ],
    'school_status_at_program_entry': [
        '409 School Status at Program Entry (WIOA)',
        'Are you currently enrolled in an education program?',
        'Are you currently enrolled in and attending an education program?',
        'College Status',
        'Education Status',
        'Education Status at Intake',
        'School Status at Program Entry',
        'School Status at time of registration',
    ],
    'secondary_funding': [
        'Secondary Funding',
    ],
    'secondary_funding_other': [
        'Secondary Funding-Other',
    ],
    'secondary_type_training_service_for_training_activity_1': [
        '2110 Secondary Type of Training Service for Training Activity 1',
    ],
    'secondary_type_training_service_for_training_activity_2': [
        '2113 Secondary Type of Training Service for Training Activity 2',
    ],
    'secondary_type_training_service_for_training_activity_3': [
        '2116 Secondary Type of Training Service for Training Activity 3',
    ],
    'sector': [
        'Sector',
    ],
    'selective_service': [
        'Selective Service',
    ],
    'servsafe_certified': [
        'Are you ServSafe certified?',
    ],
    'single_parent': [
        '806 Single Parent at Program Entry (WIOA)',
        'Are you a single parent?',
    ],
    'snap': [
        '603 Supplemental Nutrition Assistance Program (SNAP)',
        'Currently Receiving SNAP or Other Nutrition Supports',
        'Do you currently receive Supplemental Nutrition Assistance Program?',
        'Do you currently receive, or have you received in the past six months, any of the following: Supplemental Nutrition Assistance Program',
        'Do you currently receive, or have you received in the past six months: Supplemental Nutrition Assistance Program',
        'Food Stamps',
        'Receipt of SNAP',
        'SNAP',
    ],
    'snap_tanf_saga': [
        "Applicant's household currently receives SNAP/TFA/SAGA",
    ],
    'special_requirement': [
        'Please Specify Other Special Requirement',
    ],
    'ssi/ssdi': [
        'Do you currently receive, or have you received in the past six months, any of the following: Social Security Disability Income',
        'Do you currently receive, or have you received in the past six months, any of the following: Supplemental Security Income',
        'Do you currently receive, or have you received in the past six months: Social Security Disability Income',
        'Do you currently receive, or have you received in the past six months: Supplemental Security Income',
    ],
    'ssi_ssdi': [
        '602 Supplemental Security Income(SSI) / Social Security Disability Insurance (SSDI)',
        'SSI or SSDI',
        'SSI/SSD',
    ],
    'ssn': [
        '2700 Social Security Number',
        'SSN',
        'Social Security #',
        'Social Security Number',
    ],
    'state': [
        '101 State Code of Residence (WIOA)',
        'State',
        'state',
    ],
    'substance_use': [
        'Substance Use',
    ],
    'suffix': [
        'Suffix',
    ],
    'summer_program_end_date': [
        'Summer Program Exit Date',
    ],
    'summer_program_start_date': [
        'Summer Program Start Date',
    ],
    'support_type': [
        'Support Type',
    ],
    'support_value': [
        'Support Value',
    ],
    'supports_other': [
        'Supports-Other',
    ],
    'supports_provided_1': [
        'Supports Provided',
    ],
    'supports_provided_2': [
        'Supports Provided-Other',
    ],
    'tanf': [
        '600 Temporary Assistance to Needy Families (TANF)',
        '601 Exhausting TANF Within 2 Years (Part A Title IV of the Social Security Act) at Program Entry (WIOA)',
        'Do you currently receive, or have you received in the past six months, any of the following: Temporary Family Assistance',
        'Do you currently receive, or have you received in the past six months: Temporary Family Assistance',
        'Does the participant qualify for TANF?',
        'Receipt of TANF',
    ],
    'tertiary_type_training_service_for_training_activity_1': [
        '2111 Tertiary Type of Training Service for Training Activity 1',
    ],
    'tertiary_type_training_service_for_training_activity_2': [
        '2114 Tertiary Type of Training Service for Training Activity 2',
    ],
    'tertiary_type_training_service_for_training_activity_3': [
        '2117 Tertiary Type of Training Service for Training Activity 3',
    ],
    'test_score': [
        'Test Score',
    ],
    'third_funding': [
        'Third Funding',
    ],
    'third_funding_other': [
        'Third Funding-Other',
    ],
    'ticket_to_work': [
        'Do you currently receive, or have you received in the past six months, any of the following: Ticket to Work',
        'Do you currently receive, or have you received in the past six months: Ticket to Work',
    ],
    'total_program_costs': [
        'Total Program Costs',
    ],
    'town_person': [
        '102 County Code',
        '102 County Code of Residence',
        'City',
        'City, State County',
        'Town at Intake',
        'Town of Residence',
        'Town/Region',
        'city',
    ],
    'training_1': [
        'Training Name',
        'training_1',
    ],
    'training_1_area': [
        'Training Area',
    ],
    'training_1_category': [
        'Training Category',
    ],
    'training_2': [
        'training_2',
    ],
    'training_3': [
        'training_3',
    ],
    'training_completed_1': [
        '1307 Training Completed #1',
        '1307 Training Completed 1',
        'Completion Status',
        'Training Completed',
        'Training Completed 1',
        'Training Completion Status',
    ],
    'training_completed_2': [
        '1312 Training Completed #2',
        '1312 Training Completed 2',
        'Training Completed 2',
    ],
    'training_completed_3': [
        '1317 Training Completed #3',
        '1317 Training Completed 3',
        'Training Completed 3',
    ],
    'training_end_date': [
        'Actual End Date',
        'End Date',
        'End Dt',
        'Program End',
    ],
    'training_format': [
        'Training Format',
    ],
    'training_job_title': [
        'Job Title',
        'Title',
    ],
    'training_program_id': [
        'Training Program ID',
    ],
    'training_provider': [
        'Career ConneCT Training Provider',
        'Career ConneCT Training Provider Program of Study 1',
        'College or Training Program Name',
        'Provider',
        'School or Program Name',
        'Training Program Name',
        'Training Provider',
        'Training Provider Name',
        'Youth Provider',
    ],
    'training_wages': [
        'Wage-Hr',
    ],
    'training_weekly_hours': [
        'Hours-Wk',
        'Total Hours',
    ],
    'transportation': [
        'Transportation',
        'What types of support will you need to be successful in a training/workforce program: Transportation',
    ],
    'type_of_crime': [
        'What type of crime was it?',
    ],
    'type_service': [
        'Type of Supportive Service',
    ],
    'type_training_1': [
        '1303 Type of Training Service #1 (WIOA)',
        '1303 Type of Training Service 1',
        'Type of Training',
        'Type of Training Service 1',
    ],
    'type_training_2': [
        '1310 Type of Training Service #2 (WIOA)',
        '1310 Type of Training Service 2',
        'Type of Training Service 2',
    ],
    'type_training_3': [
        '1315 Type of Training Service #3 (WIOA)',
        '1315 Type of Training Service 3',
        'Type of Training Service 3',
    ],
    'underemployed': [
        '2101 Underemployed Worker',
        'If you are currently employed, are you underemployed?',
        'If you are employed, are you currently underemployed?',
    ],
    'unemployment_compensation': [
        '401 UC Eligible Status',
        'If you are not employed, are you currently receiving unemployment compensation?',
    ],
    'veteran_status': [
        '300 Veteran Status',
        'Are you a veteran?',
        'Veteran',
        'veteran_status',
    ],
    'wage_hr_2': [
        'Wage-Hr_2',
    ],
    'wages_1q_after_exit': [
        '1703 Wages 1st Quarter After Exit Quarter (WIOA)',
    ],
    'wages_1q_prior': [
        '1702 Wages 1st Quarter Prior to Participation Quarter',
    ],
    'wages_2q_after_exit': [
        '1704 Wages 2nd Quarter After Exit Quarter (WIOA)',
    ],
    'wages_2q_prior': [
        '1701 Wages 2nd Quarter Prior to Participation Quarter',
    ],
    'wages_3q_after_exit': [
        '1705 Wages 3rd Quarter After Exit Quarter (WIOA)',
    ],
    'wages_3q_prior': [
        '1700 Wages 3rd Quarter Prior to Participation Quarter',
    ],
    'wages_4q_after_exit': [
        '1706 Wages 4th Quarter After Exit Quarter (WIOA)',
    ],
    'wages_after_exit': [
        'Hourly Wage',
        'Wage',
    ],
    'wagner_peyser_employment_service': [
        '918 Wagner-Peyser Employment Service (WIOA)',
    ],
    'week_end_date': [
        'Week Ending Date',
    ],
    'week_ending_date': [
        'Week Ending Date',
    ],
    'which_services_would_be_helpful': [
        'Which supportive services would you find helpful?',
    ],
    'wioa_id': [
        '100 Unique Individual Identifier (WIOA)',
    ],
    'work_site': [
        'Work Site',
    ],
    'work_site_town': [
        'Work Site Town',
    ],
    'work_supports': [
        'Work Supports',
    ],
    'workforce_board_code': [
        'Local Workforce Board Code',
    ],
    'worksite_2': [
        'Work Site_2',
    ],
    'worksite_end_date': [
        'Job End Date',
    ],
    'worksite_total_hours': [
        'Total Hours',
    ],
    'worksite_town': [
        'Work Site Town_2',
    ],
    'year_of_graduation': [
        'Year of Graduation:',
    ],
    'year_round_program_end_date': [
        'Year-Round Program End Date',
    ],
    'year_round_program_start_date': [
        'Year-Round Program Start Date',
    ],
    'youth_needs_additional_assistance': [
        '702 Youth Who Needs Additional Assistance',
    ],
    'youth_placement_2q': [
        '1900 Youth 2nd Quarter Placement (Title I) (WIOA)',
    ],
    'youth_placement_4q': [
        '1901 Youth 4th Quarter Placement (Title I) (WIOA)',
    ],
    'youth_services': [
        '905 Youth (WIOA)',
    ],
    'zip_code': [
        '103 Zip Code of Residence',
        'Zip Code',
        'Zip Code at Intake',
        'zip',
    ],
}


simple_format_pa25_119_data_accepted_responses_w_types = {
    '1001 Date of First Basic Career Service (Staff-Assisted)': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1002 Most Recent Date Received Basic Career Services (Self-Service/Information-Only)': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1004 Date of Most Recent Career Service (WIOA)': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1007 Date of Most Recent Reportable Individual Contact': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '105 Special Project ID - 1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    '106 Special Project ID - 2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    '107 Special Project ID - 3': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    '1200 Date of First Individualized Career Service': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1201 Most Recent Date Received Individualized Career Service': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1205 Type of Work Experience': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '12_month_date_benchmark': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '12_months_employed': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1328 Training Provided Virtual/Online': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1331 Training Leading to an Associate Degree': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1332 Participated in Postsecondary Education During Program Participation': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1332 Participated in Postsecondary Education During Program Participation (WIOA)': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1333 Received Private Sector Training': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1333 Received training from program(s) operated by the private sector': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '1401 Enrolled in Secondary Education Program (WIOA)': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '18_month_date_benchmark': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '18_months_employed': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '24_month_date_benchmark': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '24_months_employed': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '6_month_date_benchmark': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '6_months_employed': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    '807 Displaced Homemaker at Program Entry (WIOA)': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'Apt. Floor': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'CATDLP': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'CATP': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'CDS eligibility': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'CNA Certified Nursing Assistant - currently hold': {
        'type': '',
        'accepted_responses': None,
        'Program': 'H1B Nursing Expansion Grant',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Certification appointment date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Certification appointment location': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Citizenship': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Closure Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Co-Enrolled': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Co-funded': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Communication': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Completed80PercProg': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Contact Location or Method': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Contextualized Education': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Core Services to Employers': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'Cover Letter': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Cover Letter Completed': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Critical Thinking/Problem Solving': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Culinary Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Currently Enrolled in WIOA': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP',
        'Category': 'Unmatched',
    },
    'Customer Service': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Dancing': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Data Entry/Typing WPM': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Date Co-Enrolled': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Date Referral Made': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;HFPG, UW;O2i, Free to Succeed;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Date Status Updated': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;HFPG, UW;O2i, Free to Succeed;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Date Taken': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed;WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Deobligation Amount': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Developed By': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Did this individual enter new employment?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Unmatched',
    },
    'Did youth attend Job Readiness Training?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Diversity and Inclusion': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Do you currently receive, or have you received in the past six months, any of the following?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Unmatched',
    },
    'Do you have an LLC?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Do you have an updated resume?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Do you have medical insurance?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Unmatched',
    },
    'Do you have stable housing?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Unmatched',
    },
    'Do you have your high school credential (diploma or GED)?': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Section D - Program Outcomes Information',
    },
    'Do you own a vehicle?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Do you speak a language, other than English, If so what?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Drywall Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'EB': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'EB_Job Title': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'EB_JobOfferSTatus': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'EB_Start_Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'EB_Step': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'EB_Wage': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Electrical Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Email': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Employment Management (Job Seeking)': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Employment Readiness': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Engagement and Employer Onboarding': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'Enrolled': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Entity Subtype': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Entity Type': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Entity Unique Identifier': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Estimated Days in Training': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Estimated Number of Slots': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Ethnicity, Hispanic or Latino': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'Final Placement Status': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'First Name': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;HRSA CHWT;IREE;JFES;Manufacturing;Manufacturing Pipeline;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;State Youth Employment Programs (OYE, DCF, DADS);WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;WIOA Youth Recruitment;YARG',
        'Category': 'Section A - Individual Information',
    },
    'First Referral Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'General Construction Labor Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'General Professionalism': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'HVAC Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Have you attended any college or post-high school training?': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Have you ever been incarcerated?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Have you ever owned a business?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Have you ever worked on a construction site?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Have you participated in Summer Youth Program before?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Head of Household': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Unmatched',
    },
    'High School Diploma / GED': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Hire Count': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Hire Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Hired Permanently?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Hired by Worksite': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'How did you hear about this program?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Unmatched',
    },
    'How many college credits have you earned?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Unmatched',
    },
    'How proficient are you with this language?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Identifier': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'If Other, please specify:': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'If earn and learn, type': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Good Jobs',
        'Category': 'Unmatched',
    },
    'If employed, did participant report hourly salary?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Good Jobs',
        'Category': 'Unmatched',
    },
    'If other, describe': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'If yes, how many years did you complete?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'If yes, where and what did you do?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'If yes, where?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'If you are attending college, Will you be going to college in fall?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'IfNo-TerminationReason': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'In the last 5 years, have you had an OSHA license?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Installation or Insulation Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Intake Statuses': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Interested in: Computer Literacy': {
        'type': '',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Unmatched',
    },
    'Interested in: Interview Preparation': {
        'type': '',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Unmatched',
    },
    'Interested in: Resume Support': {
        'type': '',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Unmatched',
    },
    'Interested in: Training': {
        'type': '',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Unmatched',
    },
    'Internet Search': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Interpersonal/Collaboration and Teamwork': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Interview Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Is the vehicle registered and insured?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Is this active military service?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Is this job related to training received?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'JD End': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'JD Exit Reason': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'JD Start': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Job Application': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Job Description': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Job Developer': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Job Market': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Job Referral': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Job Search': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Jobs Funnel eligibility': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'LPN Licensed Practical Nurse - currently hold': {
        'type': '',
        'accepted_responses': None,
        'Program': 'H1B Nursing Expansion Grant',
        'Category': 'Unmatched',
    },
    'Labor Market and Employment Information Services are split across three areas.': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Landscaping Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Last Modified': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Last Name': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;HRSA CHWT;IREE;JFES;Manufacturing;Manufacturing Pipeline;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;State Youth Employment Programs (OYE, DCF, DADS);WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;WIOA Youth Recruitment;YARG',
        'Category': 'Section A - Individual Information',
    },
    'Length of Agreement (Days)': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Linking_ID': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'All',
        'Category': 'Section A - Individual Information',
    },
    'Low_AJC': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'MA Medical Assistant': {
        'type': '',
        'accepted_responses': None,
        'Program': 'H1B Nursing Expansion Grant',
        'Category': 'Unmatched',
    },
    'MPI Youth': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Managing Region': {
        'type': '',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP;OWS Basic Skills Remediation',
        'Category': 'Unmatched',
    },
    'Manufacturing Machinist or CNC Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Masonry Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Medium_Remediation': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Member of Populations': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Microsoft Word, PowerPoint, Excel': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Middle Name': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'Mock Interview': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'NAACP eligibility': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'New Skills Acquired (select all that apply)': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Good Jobs',
        'Category': 'Unmatched',
    },
    'No Longer Available': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Number of Slots Filled': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Office Equipment (i.e. copier, fax machine, scanner, etc.)': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Other': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP;Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Other Costs': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Other Program Recommendation': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Unmatched',
    },
    'Other Skills (NAICS code)': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Good Jobs',
        'Category': 'Unmatched',
    },
    'PY15': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY16': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY17': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY18': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY19': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY20': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY21': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY22': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY23': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY24': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'PY25': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Painting Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Parent or Corporate Entity': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Participant Site Identifier': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Participant Status': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Partnership Activities': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Payroll Type': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Pell Grant': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Permanently Closed': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Phone Number': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Placed at Worksite?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Plays an instrument': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Plumbing Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Position': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Post-Secondary Plans': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Prefix': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Professionalism': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Program Vendor': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Projected Completion Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Pronouns': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Prove IT': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Quadrant of Residency': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'RN Registered Nurse - currently hold': {
        'type': '',
        'accepted_responses': None,
        'Program': 'H1B Nursing Expansion Grant',
        'Category': 'Unmatched',
    },
    'Race': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;DCF;DOL Energy Works;Good Jobs;HRSA CHWT;IREE;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;ODEP/ETM;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;State Youth Employment Programs (OYE, DCF, DADS);WHISP;WIOA Youth;YARG',
        'Category': 'Section A - Individual Information',
    },
    'Race (CWP)': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'Race - Self-Identify': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'Race Ethnicity': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'Race, American Indian or Alaska Native': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'Race, Asian': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'Race, Black': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'Race, Native Hawaiian or Other Pacific Islander': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'Race, White': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'Race1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'Race2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'Race3': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'Race4': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'Reason for Referral': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;HFPG, UW;O2i, Free to Succeed;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Reason for Unfilled Slots': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Reference Letters Completed': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Referral Closed': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Referral Count': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Referral Status': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;HFPG, UW;O2i, Free to Succeed;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Referral to Workshop or Service': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Referred To': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;HFPG, UW;O2i, Free to Succeed;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Registration Season(s)': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Registration Year': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Registration Year:': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Reporting Complete': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Resume Completed': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Resume Creation': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Resume Critique': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Resume Revision': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Secondary Education': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'SiMentor': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Special Requirements (check all that apply)': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Specify Other Post-Secondary Plans': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Specify Workshop or Service': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Unmatched',
    },
    'Spoken Word or Poetry': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Status': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Status Change': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Status Change Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Street Address': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Unmatched',
    },
    'Student Key': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Unmatched',
    },
    'Subsidized Loans': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Summer Duties': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Unmatched',
    },
    'Summer Worksite': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Unmatched',
    },
    'Swimming': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Technology/Digital Literacy': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Test Score': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Unmatched',
    },
    'Tests and Fees': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Tier': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Time/Self-Management': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Total Number Provided': {
        'type': '',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;DCF;DOL Energy Works;Good Jobs;HRSA CHWT;IREE;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;ODEP/ETM;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;WHISP;WIOA Youth;YARG',
        'Category': 'Unmatched',
    },
    'Tracking Eligible': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Unmatched',
    },
    'Training Class': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Unmatched',
    },
    'Tuition': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Tutoring': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Verification Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Visual Arts (Drawing, painting, etc)': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Voucher Amendment Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Voucher Award Date': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Voucher Instance': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Voucher Status': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'We Rise eligibility': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'What are your career interests?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'What is the reason for this incentive?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'What is your current work eligibility status?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'What is your preferred language?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Unmatched',
    },
    'What is your race? Select one or more:': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'What type of transportation will you be using to get to work?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Which industries interest you for an intership?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Which program sector are you interested in ?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs;H1B CT-WHISP;OWS Basic Skills Remediation',
        'Category': 'Unmatched',
    },
    'Which program training are you interested in?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Unmatched',
    },
    'Work Experience': {
        'type': '',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Unmatched',
    },
    'Workforce Region': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Unmatched',
    },
    'Worksite': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Unmatched',
    },
    'Worksite Assignment': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Worksite Department': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Worksite Number/location': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Year-Round Worksite': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Unmatched',
    },
    'Year-Round Worksite Duties': {
        'type': '',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Unmatched',
    },
    'Youth Active in program?': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'Youth Match Status': {
        'type': '',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'access_to_flexible_work_schedule': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Good Jobs',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'access_to_healthcare_benefits': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'access_to_other_benefits': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'access_to_other_insurance': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'access_to_pto': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'access_to_retirement_benefits': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'access_to_sick_leave': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Good Jobs',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'access_to_training_through_employer': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Good Jobs',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'accomodations_training_and_employment': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'accountability_exit_status': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'achieving_below_grade_level': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'actual_completion_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'adapatability_continuous_learning': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'address_1': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'address_2': {
        'type': '',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'adult_services': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'adults_in_household': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'age': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'agreement_end_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'app_id': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'applicant_household_eligible_for': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'application_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'application_status': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'apprenticeship_program': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'arrested_or_convicted_of_crime': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'asbestos_work_experience': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'assessment_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section D - Program Outcomes Information',
    },
    'basic_skills_deficient': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'best_chance_eligibility': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'blue_hills_zone': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'books_and_supplies_amount': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'business/organization_size': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'business_summary_mission': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'cadd': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'cahp': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'career_awareness': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'career_connect': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'career_exploration': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'career_interest': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'career_interest_inventory': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'career_pathways_interest': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'carpentry_work_experience': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'case_number': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'cash_assistance': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'cct_program_recommendation': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'change_related_to_training': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section D - Program Outcomes Information',
    },
    'childcare': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;HFPG, UW',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'children_in_household': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'cip_training_1': {
        'type': 'CIPCode',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'cohort_enrollment_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'completed_returned_to_hs': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'counseling_services': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'credential_issuer': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section D - Program Outcomes Information',
    },
    'credential_name': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section D - Program Outcomes Information',
    },
    'credential_received': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section D - Program Outcomes Information',
    },
    'credential_type_1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HRSA CHWT;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;Project RISE;Project Retail;WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;YARG',
        'Category': 'Section D - Program Outcomes Information',
    },
    'credential_type_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'credential_type_3': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'credential_type_4': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs',
        'Category': 'Section D - Program Outcomes Information',
    },
    'credential_type_5': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs',
        'Category': 'Section D - Program Outcomes Information',
    },
    'credentials_obtained': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section D - Program Outcomes Information',
    },
    'cssd_referral': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'cthires_id': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'cultural_barriers_at_program_entry': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'current_housing_situation_stable': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'current_scholarship_amount': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'current_school': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'currently_attending': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_accomodations_for_training_and_employment': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_acquiring_eligibility_documentation': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_books_and_supplies': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_childcare': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_complete_education_program_or_secure_and_maintain_employment': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_educational_testing': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_housing': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_legal_aid_services': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_securing_food': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_tests_and_certifications': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_transportation': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'currently_needs_assistance_work_apparel_or_gear': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_actual_dislocation': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'date_attained_recognized_credential_4': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_attained_recognized_credential_5': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_change_occured': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_completed_mid_program_in_education_or_training_program_leading_to_credential_or_employment': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_contact_initiated': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_credential_1': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_credential_2': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_credential_3': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_enrolled_mid_program_in_education_or_training_program_leading_to_credential_or_employment': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_entered_training_1': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HRSA CHWT;JFES;Manufacturing;Manufacturing Pipeline;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;Project RISE;Project Retail;WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;YARG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_entered_training_2': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_entered_training_3': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_first_dwg_service': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_most_recent_contact': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_of_birth': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;HRSA CHWT;IREE;JFES;Manufacturing;Manufacturing Pipeline;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;State Youth Employment Programs (OYE, DCF, DADS);WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;WIOA Youth Recruitment;YARG',
        'Category': 'Section A - Individual Information',
    },
    'date_program_entry': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_program_exit': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_received_assessment_services': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section A - Individual Information',
    },
    'date_received_credential_1': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP, Bloomfield;Career ConneCT;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HRSA CHWT;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;Project RISE;Project Retail;WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;YARG',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_received_credential_2': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_received_credential_3': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_scheduled_orientation': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_skill_gains_educational_functioning_level': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_skill_gains_postsecondary_transcript_report_card': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_skill_gains_secondary_transcript_report_card': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_skill_gains_skills_progression': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_skill_gains_training_milestone': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'date_taken': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_taken_service_delivery': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_training_completed_1': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;Career ConneCT;Congressional Direct Spending/Community Project;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;HRSA CHWT;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;Project RISE;Project Retail;WHISP;WIOA Youth;YARG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_training_completed_2': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'date_training_completed_3': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'days_in_training': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'detailed_status': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'disability': {
        'type': 'categorical',
        'accepted_responses': DISABILITY_MAPPING,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;State Youth Employment Programs (OYE, DCF, DADS);WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'dislocated_worker': {
        'type': 'categorical',
        'accepted_responses': DISLOCATED_WORKER_MAPPING,
        'Program': 'Congressional Direct Spending/Community Project;H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'driver_license': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;O2i, Free to Succeed',
        'Category': 'Section A - Individual Information',
    },
    'eligibility_1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'eligibility_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'eligibility_3': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'employer': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employer_entity_name': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employer_zip_code': {
        'type': 'zipCode',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_and_training_services_related_to_snap': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'employment_hours_worked': {
        'type': 'hoursWorked',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_job_title': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_match_method_1q_after_exit': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_match_method_2q_after_exit': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_match_method_3q_after_exit': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_match_method_4q_after_exit': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_naics': {
        'type': 'NAICSCode',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_naics_q1': {
        'type': 'NAICSCode',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_naics_q2': {
        'type': 'NAICSCode',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_naics_q3': {
        'type': 'NAICSCode',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_naics_q4': {
        'type': 'NAICSCode',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_onet': {
        'type': 'ONETCode',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_onet_q1': {
        'type': 'ONETCode',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_onet_q2': {
        'type': 'ONETCode',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_onet_q4': {
        'type': 'ONETCode',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_related_to_training_2q_after_exit': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_start_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_status_2q_after_exit': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_status_3q_after_exit': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_status_4q_after_exit': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_status_after_exit_q1': {
        'type': 'categorical',
        'accepted_responses': EMPLOYMENT_STATUS_MAPPING,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_status_at_exit': {
        'type': 'categorical',
        'accepted_responses': EMPLOYMENT_STATUS_MAPPING,
        'Program': 'Career ConneCT;Good Jobs;H1B CT-WHISP;Manufacturing Pipeline;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES',
        'Category': 'Section D - Program Outcomes Information',
    },
    'employment_status_at_start': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'employment_town': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section D - Program Outcomes Information',
    },
    'end_date_funding': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'end_reason': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'end_reason_for_funding_history': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'end_reason_for_training_record': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'english_language_learner': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'enrolled_in_training_program': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Section D - Program Outcomes Information',
    },
    'enrollment_grade_level': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'enrollment_gross_annual_income': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'enrollment_start_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'entered_non_traditional_employment': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'entered_training_related_employment': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section D - Program Outcomes Information',
    },
    'entrepreneurship': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'estimated_financial_aid': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'ethnicity': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;DCF;DOL Energy Works;Good Jobs;HRSA CHWT;IREE;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;ODEP/ETM;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;State Youth Employment Programs (OYE, DCF, DADS);WHISP;WIOA Youth;YARG',
        'Category': 'Section A - Individual Information',
    },
    'experience_carpentry': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_drafting': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_electrical': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_enginerepair': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_excel': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_generalrepairs': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_machining': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_painting': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_pipefitting': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_planning': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_plastics': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_rigging': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_sheetmetal': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_sheetmetal_plastics': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_shipfitting': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'experience_welding': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'final_scholarship_amount': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'financial_literacy': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'financial_support': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'first_job': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'first_language_english': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'food': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'food_and_nutrition': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'foster_care': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'funding_source': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;State Youth Employment Programs (OYE, DCF, DADS);WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'funding_start_date?': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'gender': {
        'type': 'categorical',
        'accepted_responses': GENDER_MAPPING,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;HRSA CHWT;IREE;JFES;Manufacturing;Manufacturing Pipeline;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;State Youth Employment Programs (OYE, DCF, DADS);WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;WIOA Youth Recruitment;YARG',
        'Category': 'Section A - Individual Information',
    },
    'graduating_senior': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'graduation_year': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'green_job': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'gross_annual_income': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information;Unmatched',
    },
    'hartford_promise_zone': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'have_you_been_impacted_by_covid_19?': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Section A - Individual Information',
    },
    'head_of_household': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section A - Individual Information',
    },
    'healthcare': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'high_passed': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section D - Program Outcomes Information',
    },
    'high_school_diploma': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'high_school_dropout': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;Career ConneCT;Good Jobs;H1B CT-WHISP;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'highest_education_level_completed_at_program_entry': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'homeless_at_risk': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'homeless_or_runaway': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'hourly_wage_at_exit': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section D - Program Outcomes Information',
    },
    'hourly_wage_at_worksite': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section D - Program Outcomes Information',
    },
    'hours_wk_2': {
        'type': 'hoursWorked',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'household_size': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'housing': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;HFPG, UW',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'how_long_work_construction_and_what_did_you_do': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section A - Individual Information',
    },
    'hps_credit_recovery_cohort': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'incentive_amount': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'incentive_form': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'incumbent_worker_advanced_to_new_position_1q_after_completion': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project;H1B CT-WHISP',
        'Category': 'Section D - Program Outcomes Information',
    },
    'incumbent_worker_advanced_to_new_position_2q_after_completion': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project;H1B CT-WHISP',
        'Category': 'Section D - Program Outcomes Information',
    },
    'incumbent_worker_advanced_to_new_position_3q_after_completion': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project;H1B CT-WHISP',
        'Category': 'Section D - Program Outcomes Information',
    },
    'incumbent_worker_retained_position': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'incumbent_worker_retained_position_1q_after_completion': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section D - Program Outcomes Information',
    },
    'incumbent_worker_training': {
        'type': 'categorical',
        'accepted_responses': INCUMBENT_WORKER_MAPPING,
        'Program': 'Congressional Direct Spending/Community Project;H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'industry': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section D - Program Outcomes Information',
    },
    'initial_scholarship_amount': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'interested_in_employment_search_support': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'interested_working_outside': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'interested_working_with_computers': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'interested_working_with_dress_code_in_professional_setting': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'jfes': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'job_readiness': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'job_shadowing': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'job_title': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;Career ConneCT;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HRSA CHWT;IREE;JFES;Manufacturing;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;YARG',
        'Category': 'Section D - Program Outcomes Information',
    },
    'job_title_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'justice_involved': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'last_date_of_employment': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'leadership_development': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'legal_aid': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'HFPG, UW',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'legally_allowed_to_work_in_us': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'level_up_referral': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'long_term_unemployed_at_program_entry': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'longest_employed_with_one_employer': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section A - Individual Information',
    },
    'low_income': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'lunch_status': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'manufacturing_experience': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'marital_status': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'mental_health': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'mentoring': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'migrant_and_seasonal_farmworker': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'monitoring_status': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'most_recent_date_basic_career_services': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': '0',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'most_recent_date_follow_up_service': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'most_recent_date_supportive_services': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'most_recent_job_days_employed': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'most_recent_job_hourly_wage': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs;H1B CT-WHISP;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'most_recent_job_hours_worked': {
        'type': 'hoursWorked',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs;H1B CT-WHISP;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'most_recent_job_industry': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs;H1B CT-WHISP;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'most_recent_job_last_date_of_employment': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'most_recent_job_onet': {
        'type': 'ONETCode',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'most_recent_job_title': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs;H1B CT-WHISP;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'most_recent_sye_participation': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'national_dislocated_workers_grant': {
        'type': 'categorical',
        'accepted_responses': DISLOCATED_WORKER_MAPPING,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'occupational_skills_training': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'onet_training_1': {
        'type': 'ONETCode',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'onet_training_2': {
        'type': 'ONETCode',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'onet_training_3': {
        'type': 'ONETCode',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'organization': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'orientation_s_or_ns': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'other_barriers_1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'other_barriers_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'other_public_assistance_recipient': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'other_reasons_for_exit': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'other_supportive_services': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs;H1B CT-WHISP;OWS Basic Skills Remediation',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'other_work/trade_certifications': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section A - Individual Information',
    },
    'paid_competency_training_hours': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'paid_worksite_hours': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'parent_or_pregnant': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'past_participant_in_cyep': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'pathways': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'permit_or_driver_license': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'placement_made_through_program': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section D - Program Outcomes Information',
    },
    'portal_application_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'post_secondary_transition_activities': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'pre_apprenticeship': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'primary_funding': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'primary_funding_other': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'primary_training_funding': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'primary_type_training_service_for_training_activity_1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'primary_type_training_service_for_training_activity_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'primary_type_training_service_for_training_activity_3': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'program_operator': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'provider': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'race/ethnicity': {
        'type': 'multiCategorical',
        'accepted_responses': RACE_ETHNICITY_MAPPING,
        'columns': ['Ethnicity', 'Race Ethnicity', 'Race1', 'Race2', 'Race3', 'Race4', 'Race (CWP)', 'Race - Self-Identify', 'What is your race? Select one or more:', 'Race ', 'Race'],
        'Program': '',
        'Category': 'Section A - Individual Information',
    },
    'rapid_response': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'rapid_response_additional_assistance': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'received_needs_related_payments': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'received_training': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;Career ConneCT;Congressional Direct Spending/Community Project;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;HRSA CHWT;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;Project RISE;Project Retail;WHISP;WIOA Youth;YARG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'receiving_dcf_or_foster_care_services': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'referral_source': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'registered_apprenticeship': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'registered_selective_service': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;O2i, Free to Succeed',
        'Category': 'Section A - Individual Information',
    },
    'registration_submission_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'reliable_transportation': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;HFPG, UW;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'resume': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield',
        'Category': 'Section A - Individual Information',
    },
    'retention_with_same_employer_2q_and_4q': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'saga': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section A - Individual Information',
    },
    'sasid': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - INDIVIDUAL INFORMATION',
    },
    'scheduled_end_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'scheduled_start_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;H1B CT-WHISP;Manufacturing Pipeline;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'school_status_at_exit': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs',
        'Category': 'Section D - Program Outcomes Information',
    },
    'school_status_at_program_entry': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;State Youth Employment Programs (OYE, DCF, DADS);WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'secondary_funding': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'secondary_funding_other': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'secondary_type_training_service_for_training_activity_1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'secondary_type_training_service_for_training_activity_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'secondary_type_training_service_for_training_activity_3': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'sector': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'selective_service': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'servsafe_certified': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'single_parent': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project;Good Jobs;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'snap': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;State Youth Employment Programs (OYE, DCF, DADS);WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'snap_tanf_saga': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'special_requirement': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section A - Individual Information',
    },
    'ssi/ssdi': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'ssi_ssdi': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs',
        'Category': 'Section A - Individual Information',
    },
    'ssn': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;State Youth Employment Programs (OYE, DCF, DADS);WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'state': {
        'type': 'stateID7',
        'accepted_responses': None,
        'Program': 'CYEP;Congressional Direct Spending/Community Project;Manufacturing Pipeline;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'substance_use': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'suffix': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
    'summer_program_end_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'summer_program_start_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'support_type': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'support_value': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'supports_other': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'supports_provided_1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'supports_provided_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section A - Individual Information',
    },
    'tanf': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section A - Individual Information',
    },
    'tertiary_type_training_service_for_training_activity_1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'tertiary_type_training_service_for_training_activity_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'tertiary_type_training_service_for_training_activity_3': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'H1B CT-WHISP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'test_score': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section A - Individual Information',
    },
    'third_funding': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'third_funding_other': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'ticket_to_work': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'total_program_costs': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'town_person': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;HRSA CHWT;IREE;JFES;Manufacturing;Manufacturing Pipeline;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;State Youth Employment Programs (OYE, DCF, DADS);WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;WIOA Youth Recruitment;YARG',
        'Category': 'Section A - Individual Information',
    },
    'training_1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_1_area': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_1_category': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_3': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Manufacturing Pipeline',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_completed_1': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP, Bloomfield;Career ConneCT;Congressional Direct Spending/Community Project;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HRSA CHWT;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;OWS Basic Skills Remediation;Project RISE;Project Retail;WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth;WIOA Youth Pathways;YARG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_completed_2': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_completed_3': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_end_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_format': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_job_title': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_program_id': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT;H1B CT-WHISP;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_provider': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG and CYEP, Bloomfield;Career ConneCT;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_wages': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'training_weekly_hours': {
        'type': 'hoursWorked',
        'accepted_responses': None,
        'Program': 'CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'transportation': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP;HFPG, UW',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'type_of_crime': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;O2i, Free to Succeed',
        'Category': 'Section A - Individual Information',
    },
    'type_service': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;CYEP;DCF;DOL Energy Works;Good Jobs;HRSA CHWT;IREE;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;ODEP/ETM;P2E;P2E Reentry;P2E Youth;Pathway HOME;Project RISE;Project Retail;WHISP;WIOA Youth;YARG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'type_training_1': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'ACI Healthcare;ACI Manufacturing;ACJ WIOA;ARPA Youth;BBF ARPA;BBF CT;BRBC;BRS;Best Chance, Jobs Funnel, WE RISE, CDS;Bpt ARPA CHW;CCCT;CCCT CDL;CCCT Green Jobs;CCCT Healthcare;CCCT Remote Works;CSSD;Career ConneCT;Congressional Direct Spending/Community Project;DCF;DOL Energy Works;Good Jobs;H1B CT-WHISP;HRSA CHWT;JFES;Manufacturing;Mortgage Crisis;Mortgage Crisis ARPA;NEXP;New Youth Build;O2i, Free to Succeed;ODEP/ETM;Project RISE;Project Retail;WHISP;WIOA Youth;YARG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'type_training_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'type_training_3': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;H1B CT-WHISP;O2i, Free to Succeed',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'underemployed': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'unemployment_compensation': {
        'type': 'categorical',
        'accepted_responses': UC_MAPPING,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;O2i, Free to Succeed;OWS Basic Skills Remediation',
        'Category': 'Section A - Individual Information',
    },
    'veteran_status': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City Of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways',
        'Category': 'Section A - Individual Information',
    },
    'wage_hr_2': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'wages_1q_after_exit': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'wages_1q_prior': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'wages_2q_after_exit': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'wages_2q_prior': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'wages_3q_after_exit': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'wages_3q_prior': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'wages_4q_after_exit': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'wages_after_exit': {
        'type': 'hourlyWage',
        'accepted_responses': None,
        'Program': 'CYEP;Manufacturing Pipeline',
        'Category': 'Section D - Program Outcomes Information',
    },
    'wagner_peyser_employment_service': {
        'type': 'categorical',
        'accepted_responses': WAGNER_PEYSER_MAPPING,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'week_end_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'week_ending_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'which_services_would_be_helpful': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT;Good Jobs;H1B CT-WHISP;OWS Basic Skills Remediation',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'wioa_id': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'work_site': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'work_site_town': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'work_supports': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'workforce_board_code': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'Career ConneCT',
        'Category': 'Section A - Individual Information',
    },
    'worksite_2': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'worksite_end_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'worksite_total_hours': {
        'type': 'hoursWorked',
        'accepted_responses': None,
        'Program': 'WIOA Youth Pathways',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'worksite_town': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'year_of_graduation': {
        'type': 'identifier',
        'accepted_responses': None,
        'Program': 'CYEP',
        'Category': 'Unmatched',
    },
    'year_round_program_end_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'year_round_program_start_date': {
        'type': 'dateTime',
        'accepted_responses': None,
        'Program': 'State Youth Employment Programs (OYE, DCF, DADS)',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'youth_needs_additional_assistance': {
        'type': 'boolean',
        'accepted_responses': None,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section A - Individual Information',
    },
    'youth_placement_2q': {
        'type': 'categorical',
        'accepted_responses': YOUTH_PLACEMENT_MAPPING,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'youth_placement_4q': {
        'type': 'categorical',
        'accepted_responses': YOUTH_PLACEMENT_MAPPING,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section D - Program Outcomes Information',
    },
    'youth_services': {
        'type': 'categorical',
        'accepted_responses': YOUTH_SERVICES_MAPPING,
        'Program': 'Congressional Direct Spending/Community Project',
        'Category': 'Section C - One Stop Services and Activities',
    },
    'zip_code': {
        'type': 'zipCode',
        'accepted_responses': None,
        'Program': 'Best Chance, Jobs Funnel, WE RISE, CDS;CYEP;CYEP, Bloomfield;CYEP, DCF, CSSD, ADS, City of Hartford, HFPG;Career ConneCT;Congressional Direct Spending/Community Project;Good Jobs;H1B CT-WHISP;H1B Nursing Expansion Grant;HFPG, UW;Manufacturing Pipeline;O2i, Free to Succeed;OWS Basic Skills Remediation;State Youth Employment Programs (OYE, DCF, DADS);WIOA Adult, WIOA Dislocated Worker, JFES;WIOA Youth Pathways;WIOA Youth Recruitment',
        'Category': 'Section A - Individual Information',
    },
}


workbook_definitions = {
    'pa25_119 data': {
        'simple format': {
            'Report': {
                'labels': simple_format_pa25_119_data_labels,
                'accepted_responses': simple_format_pa25_119_data_accepted_responses_w_types,
                's_used': None,
                'starting_row': 0,
                'sheet_name': 'Report',
                'starting_': 0,
            }
        }
    }
}
