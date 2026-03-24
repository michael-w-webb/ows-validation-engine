


simple_format_training_data_labels = {  "First Name": [
      "FIRSTNAME"
    ],
    "Last Name": [
      "LASTNAME"
    ],
    "CT Hires Username": [
      "USERNAME"
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
    "Language": [
       "LANG"
    ],
    "Education Level": [
      "EDULEVEL"
    ],
    "Migrant Status": [
      "MIGRANT"
    ],
    "Migrant Descriptor": [
      "MIGRANTTYPE"
    ],
    "Disability Status": [
      "DISABILITY"
    ],
    "Citizenship": [
      "CITIZENSHIP"
    ],
    "LWIA": [
      "COL_LWIA"
    ],
    "Local Office": [
      "COL_OFFICE"
    ]
}

simple_format_training_data_accepted_responses_w_types = {
    'First Name': {'type': 'identifier'},
    'Last Name': {'type': 'identifier'},
    'CT Hires Username': {'type': 'identifier'},
    'Zip Code': {'type': 'zipCode', 'required': True},
    'Client Date of Birth': {'type': 'dateTime', 'required': True},
    'Gender': {'type': 'categorical',
               'accepted_responses':{
                    "Female": ["0"],
                    "Male": ["1"],
                    "Information not provided": ["9"],
                    "Non-Binary or Another Gender": ["2", "3"]
                }},
    'Race': {'type': 'categorical',
             'accepted_responses':{
                "White": ["1"],
                "African American/Black": ["2"],
                "Ethnic Hispanic or Latino": ["3"],
                "American Indian/Alaskan Native": ["4"],
                "Asian": ["5"],
                "Hawaiian/Other Pacific Islander": ["6"],
                "Other": ["8"],
                "Middle Eastern/North African": ["9"],
                "I do not wish to answer.": ["99"]
            }},
    'Language': {'type': 'categorical',
                 'accepted_responses':[
                 'E',
                 'S'
                 ]},
    'Education Level': {'type': 'categorical',
                        'accepted_responses':
                        {
                            "No School Grades Completed": ["00"],
                            "1st Grade Completed": ["01"],
                            "2nd Grade Completed": ["02"],
                            "3rd Grade Completed": ["03"],
                            "4th Grade Completed": ["04"],
                            "5th Grade Completed": ["05"],
                            "6th Grade Completed": ["06"],
                            "7th Grade Completed": ["07"],
                            "8th Grade Completed": ["08"],
                            "9th Grade Completed": ["09"],
                            "10th Grade Completed": ["10"],
                            "11th Grade Completed": ["11"],
                            "12th Grade Completed & Did not receive diploma or equivalent": ["12"],
                            "1 Year at College or a Technical or Vocational School": ["13"],
                            "2 Years at College or a Technical or Vocational School": ["14"],
                            "3 Years at College or a Technical or Vocational School": ["15"],
                            "Eighth Grade or Less": ["50"],
                            "Some High School": ["51"],
                            "High School Graduate": ["52"],
                            "GED": ["53"],
                            "Some College": ["54"],
                            "College Graduate": ["55"],
                            "Post-College Graduate": ["56"],
                            "High School Diploma": ["87"],
                            "High School Equivalency Diploma": ["88"],
                            "Certificate of Attendance/Completion (Disabled Individuals)": ["89"],
                            "High School Diploma or Equivalent": ["90"],
                            "Associate's Degree": ["AD"],
                            "Bachelor's Degree": ["BD"],
                            "Master's Degree": ["MD"],
                            "No Minimum Education Requirement": ["NH"],
                            "Doctorate Degree": ["PD"],
                            "Specialized Degree (e.g. MD, DDS)": ["SD"],
                            "Vocational School Certificate": ["VC"]
                        }
                        },
    'Migrant Status': {'type': 'boolean'},
    'Migrant Descriptor': {
        'type': 'categorical',
        'accepted_responses': {
            "No": ["0"],
            "Seasonal Farm Worker": ["1"],
            "Migrant Farm Worker": ["2"],
            "Migrant Food Processing Worker": ["3"]
        }
    },
    'Disability Status': {
        'type': 'categorical',
        'accepted_responses': {
            "Yes":["1"],
            "No":["0"],
            "Prefer Not To Say":["9"]

        }
    },
    'Citizenship': {'type': 'categorical',
                    'accepted_repsonses':{
                        "Citizen of U.S. or U.S. Territory": ["1"],
                        "U.S. Permanent Resident": ["3"],
                        "Alien/Refugee Lawfully Admitted to U.S.": ["2"],
                        "Citizen of Freely Associated States": ["5"],
                        "None of the above": ["4"]
                    }},
    'LWIA': {
        'type': 'categorical',
        'accepted_responses': {
            "Eastern Workforce Investment Area": ["10"],
            "North Central Workforce Investment Area": ["11"],
            "Northwest Workforce Investment Area": ["12"],
            "South Central Workforce Investment Area": ["13"],
            "Southwest Workforce Investment Area": ["14"],
            "System Set": ["98"],
            "Statewide Providers": ["99"]
        }
    },
    'Local Office': {'type': 'categorical',
                     'accepted_repsonses':{
    "System Set - Default Office": ["1"],
    "VOScan": ["2"],
    "Statewide Providers": ["3"],
    "Danielson American Job Center": ["100", "512"],
    "EWIB - Danielson": ["102"],
    "EASTCONN NE Learning Center": ["103"],
    "EASTCONN - Hampton": ["107"],
    "New London American Job Center": ["108"],
    "EWIB - New London": ["110"],
    "Thames Valley Council for Community Action, Inc. - New London (Cove 3)": ["112"],
    "New London Youth Affairs": ["115"],
    "Norwich American Job Center": ["117"],
    "EWIB - Norwich": ["119"],
    "CT DSS - Norwich": ["123"],
    "Access Agency, Inc.": ["124"],
    "Norwich Youth and Family Services": ["125"],
    "Creative Connections - Norwich": ["126"],
    "Employment & Training Institute - Old Saybrook": ["127"],
    "Thames Valley Council for Community Action, Inc. - Storrs": ["128"],
    "EWIB - Waterford": ["129"],
    "Willimantic American Job Center": ["130"],
    "EWIB - Willimantic": ["132"],
    "EASTCONN Community Learning Center - Willimantic": ["136"],
    "CT DSS - Willimantic": ["137"],
    "Enfield American Job Center- inactive": ["138"],
    "NC WIB - Enfield (786 Enfield St)": ["140"],
    "NC WIB - Enfield (620 Enfield St)": ["142"],
    "Career TEAM - Enfield": ["143"],
    "KRA Corporation - Enfield (620 Enfield St)": ["145"],
    "Hartford American Job Center": ["146"],
    "NC WIB - Hartford (Main St)": ["148"],
    "Hartford Public Library": ["155"],
    "NC WIB - Hartford (Sargeant St)": ["157"],
    "Catholic Family Services - Hartford (Jefferson St)": ["158"],
    "NC WIB - Hartford (Pratt St)": ["159"],
    "CT DSS - Central Office Hartford": ["161"],
    "Manchester American Job Center": ["162"],
    "NC WIB - Manchester": ["164"],
    "Community Renewal Team - Manchester": ["165"],
    "CT DSS - Manchester": ["167"],
    "New Britain American Job Center": ["168"],
    "NC WIB - New Britain (Lafayette St)": ["170"],
    "KRA Corporation - New Britain": ["172"],
    "NC WIB - New Britain (Main St)": ["173"],
    "CT DSS - New Britain": ["174"],
    "HRA of New Britain - New Britain": ["175"],
    "NC WIB - New Britain (Grove St)": ["176"],
    "Care-4-Kids": ["177"],
    "Connecticut Department of Labor Central Office": ["178"],
    "DOL Central Office - Alien Labor Office": ["179"],
    "DOL Central Office - ES Operations": ["180"],
    "DOL Central Office - Performance and Accountability": ["181"],
    "DOL Central Office - UI Technical Unit": ["182"],
    "DOL Central Office - Welfare-To-Work": ["183"],
    "DOL Central Office - WIOA Administration": ["184"],
    "Auditors of Public Accounts": ["185"],
    "USDOL VETS": ["186"],
    "DOL Central Office - Veterans": ["187"],
    "DOL Central Office - Business Engagement Unit (OWC)": ["188"],
    "Danbury American Job Center": ["189"],
    "NW WIB - Danbury": ["191"],
    "CT DSS - Danbury": ["195"],
    "Workforce Connection - Danbury (W. St)": ["197"],
    "Torrington American Job Center": ["198"],
    "NW WIB - Torrington": ["200"],
    "CT DSS - Torrington": ["205"],
    "Family Service of Greater Waterbury - Torrington": ["206"],
    "Workforce Connection - Torrington": ["207"],
    "Waterbury American Job Center": ["208"],
    "NW WIB - Waterbury": ["210"],
    "Workforce Connection - Waterbury (Bishop St)": ["220"],
    "Hamden American Job Center": ["221"],
    "SC WIB - Hamden": ["223"],
    "Meriden American Job Center": ["227"],
    "SC WIB - Meriden": ["229"],
    "Human Resources Agency of New Britain Middletown (Riverview Center)": ["231"],
    "CT DSS - Middletown": ["232"],
    "Human Resources Agency of New Britain Middletown (S. Main St)": ["233"],
    "New Haven American Job Center": ["234"],
    "SC WIB - New Haven": ["236"],
    "CT DSS - New Haven": ["238"],
    "Ansonia American Job Center": ["239"],
    "SW WIB - Ansonia": ["241"],
    "Bridgeport American Job Center": ["243"],
    "SW WIB - Bridgeport (Lafayette Sq)": ["245"],
    "SW WIB - Bridgeport (350 Fairfield Ave)": ["248"],
    "SW WIB - Bridgeport (240 Fairfield Ave)": ["249"],
    "Career Resources, Inc. - Bridgeport (Islandbrook Ave)": ["250"],
    "CT DSS-Bridgeport": ["251"],
    "Derby American Job Center": ["252"],
    "SW WIB - Derby": ["254"],
    "SW WIB - Norwalk": ["256"],
    "Career Resources, Inc. - Norwalk": ["257"],
    "Stamford American Job Center": ["258"],
    "SW WIB - Stamford": ["260"],
    "Career Resources, Inc. - Stamford (Bedford St)": ["261"],
    "CT DSS - Stamford": ["262"],
    "American Job Center Career Coach": ["265"],
    "Eastern CT Workforce Investment Board": ["266"],
    "Capital Workforce Partners": ["267"],
    "Northwest Regional Workforce Investment Board": ["268"],
    "Workforce Alliance": ["269"],
    "The Workplace, Inc.": ["270"],
    "Fairfield Public Library": ["271"],
    "Monroe Public Library": ["272"],
    "Trumbull Public Library": ["273"],
    "Westport Public Library": ["274"],
    "Electric Boat Career Center": ["300"],
    "Bristol": ["301"],
    "East Hartford": ["302", "521"],
    "Meriden-WIB": ["303"],
    "Middletown American Job Center": ["304", "314"],
    "CT DSS - Hartford": ["305"],
    "Human Resources Agency of New Britain - Middletown (Hamlin St)": ["306"],
    "Norwalk": ["307"],
    "Our Peice of the Pie - Hartford": ["308"],
    "Urban League of Greater Hartford": ["309"],
    "Blue Hills Civic Association": ["310"],
    "Center for Latino Progress": ["311"],
    "OIC of New Britain": ["312"],
    "Chrysalis Center": ["313"],
    "CT DSS - Greater Hartford": ["315"],
    "CT DSS-Waterbury": ["316"],
    "DOL Central Office-Apprenticeship": ["511"],
    "Enfield American Job Center": ["513"],
    "Montville American Job Center": ["514"],
    "Norwich Adult Education": ["515"],
    "New London Adult Education": ["516"],
    "Career Resources, Inc. - North Central": ["517"],
    "Billings Forge Community Works": ["518"],
    "Bristol American Job Center": ["519"],
    "Northern Fairfield County Networking Group": ["520"],
    "Clinton Public Library": ["522"],
    "MacDougall-Walker Correctional Institution": ["523"],
    "York Correctional Institution": ["524"],
    "Capital Region Education Council (CREC)": ["525"],
    "Office of Workforce Strategy": ["526"],
    "Forge City Works": ["527"],
    "Robinson Correctional Institution": ["528"]
}},
    }

workbook_definitions = {
"cc_demo_pull":{
  "simple format": {
  
    "Report":{
    "labels": simple_format_training_data_labels,
    "accepted_responses": simple_format_training_data_accepted_responses_w_types,
    "columns_used": None,
    "starting_row": 0,
    "sheet_name": "ct_hires_cc_demo_match",
    "starting_column": 0 # zero covers whole df
    }
  }
}
}