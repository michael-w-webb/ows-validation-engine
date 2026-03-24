
simple_format_training_data_labels = {  "First Name": [
      "FIRSTNAME"
    ],
    "Last Name": [
      "LASTNAME"
    ],
    "CTHIRES Username":
    [
        "USERID"
    ],
    "Zip Code": [
      "ZIPCODE"
    ],
    "Client Date of Birth": [
      "DATEOFBIRTH"
    ],
    "Gender": [
      "GENDERDESC"
    ],
    "Race: American Indian / Alaska Native": [
      "AMERICAN INDIAN/ALASKAN NATIVE"
    ],
    "Race: Asian": [
      "ASIAN"
    ],
    "Race: Black or African American": [
      "BLACK OR AFRICAN AMERICAN"
    ],
    "Race: Native Hawaiian / Other Pacific Islander": [
      "HAWAIIAN/PACIFIC ISLANDER"
    ],
    "Race: White": [
      "WHITE"
    ],
    "Race: Hispanic/Latino": [
      "ETHNIC HISPANIC OR LATINO"
    ],  
    "Race: Middle Eastern/North African": [
      "MIDDLE EASTERN/NORTH AFRICAN"
    ],
    "Race: Declined to Answer":[
        "DECLINED TO ANSWER"
    ],
    "CT HIRES - Homeless": [
       "HOMELESSBARRIER"
    ],
    "QUESTIONNAIRE - Homeless":[
        "HOMELESS"
    ],
    "CT HIRES - Basic Skills Deficient": [
      "BASICSKILLSBARRIER"
    ],
    "QUESTIONNAIRE - Basic Skills Deficient":[
        "BASIC SKILLS DEFICIENT/LOW LEVELS OF LITERACY"
    ],
    "Low Income Status at Program Entry?": [
      "LOW INCOME STATUS AT PROGRAM ENTRY"
    ],
    "Single Parent at Program Entry?": [
      "SINGLE PARENT AT PROGRAM ENTRY"
    ],
    "Highest Education Level Completed at Program Entry": [
      "WHAT IS THE HIGHEST EDUCATION LEVEL THE CLIENT HAS COMPLETED?"
    ],
    "School Status at Program Entry": [
      "SCHOOL STATUS AT PROGRAM ENTRY"
    ],
    "Hourly Wage in most recent employment prior to participation": [
      "HOURLY WAGE IN MOST RECENT EMPLOYMENT"
    ],
    "Hours worked per week most recent employment prior to participation (Only go back 9 months.)": [
      "HOURS WORKED IN MOST RECENT EMPLOYMENT"
    ],
    "Occupational Code of Most Recent Employment Prior to Participation": [
      "OCCUPATIONAL CODE OF MOST RECENT EMPLOYMENT"
    ],
    "CT HIRES - TANF": [
      "TANFRECIPIENT"
    ],
    "CT HIRES - SSI/SSD": [
      "SSIRECIPIENT"
    ],
    "CT HIRES - SNAP": [
      "SNAPRECIPIENT"
    ],
    "QUESTIONNAIRE - TANF": [
      "TEMPORARY ASSISTANCE TO NEEDY FAMILIES (TANF)"
    ],
    "QUESTIONNAIRE - SSI/SSD": [
      "SUPPLEMENTAL SECURITY INCOME(SSI) / SOCIAL SECURITY DISABILITY INSURANCE (SSDI)"
    ],
    "QUESTIONNAIRE - SNAP": [
      "SUPPLEMENTAL NUTRITION ASSISTANCE PROGRAM (SNAP)"
    ],
    "QUESTIONNAIRE - Other public assistance recipient": [
      "OTHER PUBLIC ASSISTANCE"
    ],
    "QUESTIONNAIRE - Receiving Medicaid": [
      "RECEIVING MEDICAID SERVICES"
    ],
    "CT HIRES - Receiving Medicaid": [
      "MEDICAIDRECIPIENT"
    ],
    "CareerConneCT Training Provider": [
      "TRAINING PROVIDER"
    ],
    "Training Industry": [
        "TRAINING INDUSTRY"
    ],
    "Type of Training Service": [
      "TRAINING TYPE"
    ],
    "Date Entered Training": [
      "TRAINING START DATE"
    ],
    "Date Completed or Withdrew From Training #1": [
      "TRAINING END DATE"
    ],
    "Training Completed?": [
      "TRAINING COMPLETED?"
    ],
    "Training Provider #2": [
      "2ND TRAINING PROVIDER"
    ],
    "Type of Training Service #2": [
      "2ND TRAINING TYPE"
    ],
    "Date Entered Training #2": [
      "2ND TRAINING START DATE"
    ],
    "Date Completed or Withdrew From Training #2": [
      "2ND TRAINING END DATE"
    ],
    "Training Completed #2": [
      "2ND TRAINING COMPLETED?"
    ],
    "Training Provider #3": [
      "3RD TRAINING PROVIDER"
    ],
    "Type of Training Service #3": [
      "3RD TRAINING TYPE"
    ],
    "Date Entered Training #3": [
      "3RD TRAINING START DATE"
    ],
    "Date Completed or Withdrew From Training #3": [
      "3RD TRAINING END DATE"
    ],
    "Training Completed #3": [
      "3RD TRAINING COMPLETED?"
    ],
    "Employment Status at exit": [
      "EMPLOYMENT STATUS AT EXIT",
    ],
    "Hourly Wage at Exit": [
      "HOURLY WAGE AT EXIT"
    ],
    "Employer": [
      "EMPLOYER"
    ],
    "Occupational Code of Employment After Exit": [
      "OCCUPATIONAL CODE"
    ],
    "Occupational Code of Employment 2nd Quarter After Exit Quarter": [
      "OCCUPATIONAL CODE OF EMPLOYMENT 2ND QUARTER AFTER EXIT QUARTER"
    ],
    "Occupational Code of Employment 4th Quarter After Exit": [
      "OCCUPATIONAL CODE OF EMPLOYMENT 4TH QUARTER AFTER EXIT QUARTER"
    ]
}

simple_format_training_data_accepted_responses_w_types = {
    'First Name': {'type': 'identifier'},
    'Last Name': {'type': 'identifier'},
    'CTHIRES Username': {'type':'identifier'},
    'Zip Code': {'type': 'zipCode', 'required': True},
    'Client Date of Birth': {'type': 'dateTime', 'required': True},
    'Gender': {'type': 'categorical',
               'accepted_responses':{
                    "Female": ["0","Female"],
                    "Male": ["1","Male"],
                    "Information not provided": ["9"],
                    "Non-Binary or Another Gender": ["2", "3"]
                }},
    "Race: American Indian / Alaska Native": { 'type': 'boolean'},
    "Race: Asian": { 'type': 'boolean'},
    "Race: Black or African American": { 'type': 'boolean'},
    "Race: Native Hawaiian / Other Pacific Islander": { 'type': 'boolean'},
    "Race: White": { 'type': 'boolean'},
    "Race: Hispanic/Latino": { 'type': 'boolean'},
    "Race: Middle Eastern/North African": { 'type': 'boolean'},
    "Race: Declined to Answer": { 'type': 'boolean'},

    "CT HIRES - Homeless": { 'type': 'boolean'},
    "QUESTIONNAIRE - Homeless": { 'type': 'boolean'},
    "CT HIRES - Basic Skills Deficient": { 'type': 'boolean'},
    "QUESTIONNAIRE - Basic Skills Deficient": { 'type': 'boolean'},
    "Low Income Status at Program Entry?": { 'type': 'boolean'},
    "Single Parent at Program Entry?": { 'type': 'boolean'},

    "Highest Education Level Completed at Program Entry": {
        'type': 'categorical',
        'accepted_responses': [
            'no education level completed',
            'attained secondary school diploma',
            'attained a secondary school equivalency',
            'completed one of more years of postsecondary education',
            "attained a bachelor's degree",
            "attained an associate's degree",
            'attained a postsecondary technical or vocational certificate (non-degree)',
            "attained a degree beyond a bachelor's degree",
            "The participant with a disability receives a certificate of attendance/completion as a result of successfully completing an Individualized Education Program (IEP)"
        ]
    },
    "School Status at Program Entry": {
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
    "Hourly Wage in most recent employment prior to participation": {'type': 'hourlyWage'},
    "Hours worked per week most recent employment prior to participation (Only go back 9 months.)": {'type': 'hoursWorked'},
    "Occupational Code of Most Recent Employment Prior to Participation": {'type': 'ONETCode'},
    "CT HIRES - TANF": {'type': 'boolean'},
    "CT HIRES - SSI/SSD": {'type': 'boolean'},
    "CT HIRES - SNAP": {'type': 'boolean'},
    "QUESTIONNAIRE - TANF": {'type': 'boolean'},
    "QUESTIONNAIRE - SSI/SSD": {
        'type': 'categorical',
        'accepted_responses': ['SSI/SSDI', 'SSI', 'SSDI', 'No']
    },
    "QUESTIONNAIRE - SNAP": {'type': 'boolean'},
    "QUESTIONNAIRE - Other public assistance recipient": {'type': 'boolean'},
    "QUESTIONNAIRE - Receiving Medicaid": {'type': 'boolean'},
    "CT HIRES - Receiving Medicaid": {'type': 'boolean'},
    "CareerConneCT Training Provider": {'type': 'identifier'},
    "Training Industry": {'type': 'identifier'},
    "Type of Training Service": {'type': 'identifier'},
    "Date Entered Training": {'type': 'dateTime'},
    "Date Completed or Withdrew From Training #1": {'type': 'dateTime'},
    "Training Completed?": {'type': 'boolean'},
    "Training Provider #2": {'type': 'identifier'},
    "Type of Training Service #2": {'type': 'identifier'},
    "Date Entered Training #2": {'type': 'dateTime'},
    "Date Completed or Withdrew From Training #2": {'type': 'dateTime'},
    "Training Completed #2": {'type': 'boolean'},
    "Training Provider #3": {'type': 'identifier'},
    "Type of Training Service #3": {'type': 'identifier'},
    "Date Entered Training #3": {'type': 'dateTime'},
    "Date Completed or Withdrew From Training #3": {'type': 'dateTime'},
    "Training Completed #3": {'type': 'boolean'},
    'Employment Status at exit': {
        'type': 'categorical',
        'accepted_responses': {
            'employed; part-time' : ["Part-time employment"],
            'employed; full-time' : ["Full-time employment"],
            'unemployed' : ["Unemployed"],
            'temporarily employed': ["Temporary employment"]
        }
    },
    "Hourly Wage at Exit": {'type': 'hourlyWage'},
    "Employer": {'type': 'identifier'},
    "Occupational Code of Employment After Exit": {'type': 'ONETCode'},
    "Occupational Code of Employment 2nd Quarter After Exit Quarter": {'type': 'ONETCode'},
    "Occupational Code of Employment 4th Quarter After Exit": {'type': 'ONETCode'}
    }

workbook_definitions = {
"cc_full_pull":{
  "simple format": {
  
    "Report":{
    "labels": simple_format_training_data_labels,
    "accepted_responses": simple_format_training_data_accepted_responses_w_types,
    "columns_used": None,
    "starting_row": 0,
    "sheet_name": "ct_hires_full_pull",
    "starting_column": 0 # zero covers whole df
    }
  }
}
}