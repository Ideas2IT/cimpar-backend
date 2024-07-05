import requests
from requests.auth import HTTPBasicAuth

AIDBOX_URL = {{HOST}}
AIDBOX_CLIENT_USERNAME = {{USERNAME}}
AIDBOX_CLIENT_PASSWORD = {{PASSWORD}}

# Common headers for all requests
headers = {"Content-Type": "application/json"}

# Auth credentials
auth = HTTPBasicAuth(AIDBOX_CLIENT_USERNAME, AIDBOX_CLIENT_PASSWORD)

# Table creation data
tables = [
    #{"id": "CimparRace", "type": "resource", "isOpen": True},
    {"id": "CimparEthnicity", "type": "resource", "isOpen": True},
    {"id": "CimparState", "type": "resource", "isOpen": True},
    {"id": "CimparLabTest", "type": "resource", "isOpen": True}
]

# Data for each table
race_data = [
    {"code": "1002-5", "display": "American Indian or Alaska Native"},
    {"code": "2028-9", "display": "Asian"},
    {"code": "2054-5", "display": "Black or African American"},
    {"code": "2076-8", "display": "Native Hawaiian or Other Pacific Islander"},
    {"code": "2106-3", "display": "White"}
]

ethnicity_data = [
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2186-5", "display": "Not Hispanic or Latino"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2137-8", "display": "Spaniard"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2140-2", "display": "Castillian"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2144-4", "display": "Valencian"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2145-1", "display": "Canarian"}
]

state_data = [
    {"code": "AL", "state": "Alabama", "capital": "Montgomery"},
    {"code": "AK", "state": "Alaska", "capital": "Juneau"},
    {"code": "AZ", "state": "Arizona", "capital": "Phoenix"},
    {"code": "AR", "state": "Arkansas", "capital": "Little Rock"},
    {"code": "CA", "state": "California", "capital": "Sacramento"},
    {"code": "CO", "state": "Colorado", "capital": "Denver"},
    {"code": "CT", "state": "Connecticut", "capital": "Hartford"},
    {"code": "DE", "state": "Delaware", "capital": "Dover"},
    {"code": "FL", "state": "Florida", "capital": "Tallahassee"},
    {"code": "GA", "state": "Georgia", "capital": "Atlanta"},
    {"code": "HI", "state": "Hawaii", "capital": "Honolulu"},
    {"code": "ID", "state": "Idaho", "capital": "Boise"},
    {"code": "IL", "state": "Illinois", "capital": "Springfield"},
    {"code": "IN", "state": "Indiana", "capital": "Indianapolis"},
    {"code": "IA", "state": "Iowa", "capital": "Des Moines"},
    {"code": "KS", "state": "Kansas", "capital": "Topeka"},
    {"code": "KY", "state": "Kentucky", "capital": "Frankfort"},
    {"code": "LA", "state": "Louisiana", "capital": "Baton Rouge"},
    {"code": "ME", "state": "Maine", "capital": "Augusta"},
    {"code": "MD", "state": "Maryland", "capital": "Annapolis"},
    {"code": "MA", "state": "Massachusetts", "capital": "Boston"},
    {"code": "MI", "state": "Michigan", "capital": "Lansing"},
    {"code": "MN", "state": "Minnesota", "capital": "Saint Paul"},
    {"code": "MS", "state": "Mississippi", "capital": "Jackson"},
    {"code": "MO", "state": "Missouri", "capital": "Jefferson City"},
    {"code": "MT", "state": "Montana", "capital": "Helena"},
    {"code": "NE", "state": "Nebraska", "capital": "Lincoln"},
    {"code": "NV", "state": "Nevada", "capital": "Carson City"},
    {"code": "NH", "state": "New Hampshire", "capital": "Concord"},
    {"code": "NJ", "state": "New Jersey", "capital": "Trenton"},
    {"code": "NM", "state": "New Mexico", "capital": "Santa Fe"},
    {"code": "NY", "state": "New York", "capital": "Albany"},
    {"code": "NC", "state": "North Carolina", "capital": "Raleigh"},
    {"code": "ND", "state": "North Dakota", "capital": "Bismarck"},
    {"code": "OH", "state": "Ohio", "capital": "Columbus"},
    {"code": "OK", "state": "Oklahoma", "capital": "Oklahoma City"},
    {"code": "OR", "state": "Oregon", "capital": "Salem"},
    {"code": "PA", "state": "Pennsylvania", "capital": "Harrisburg"},
    {"code": "RI", "state": "Rhode Island", "capital": "Providence"},
    {"code": "SC", "state": "South Carolina", "capital": "Columbia"},
    {"code": "SD", "state": "South Dakota", "capital": "Pierre"},
    {"code": "TN", "state": "Tennessee", "capital": "Nashville"},
    {"code": "TX", "state": "Texas", "capital": "Austin"},
    {"code": "UT", "state": "Utah", "capital": "Salt Lake City"},
    {"code": "VT", "state": "Vermont", "capital": "Montpelier"},
    {"code": "VA", "state": "Virginia", "capital": "Richmond"},
    {"code": "WA", "state": "Washington", "capital": "Olympia"},
    {"code": "WV", "state": "West Virginia", "capital": "Charleston"},
    {"code": "WI", "state": "Wisconsin", "capital": "Madison"},
    {"code": "WY", "state": "Wyoming", "capital": "Cheyenne"}
]

lab_test_data = [
    {"code": "ALT", "display": "ALANINE AMINOTRANS"},
    {"code": "ALB", "display": "ALBUMIN"},
    {"code": "AGR", "display": "ALBUMIN GLOBULIN RATIO"},
    {"code": "ALKP", "display": "ALKALINE PHOSPHATASE"},
    {"code": "AMYL", "display": "AMYLASE"},
    {"code": "AHCV", "display": "ANTI HEPATITIS C"},
    {"code": "AST", "display": "AST"},
    {"code": "BCR", "display": "BUN CREATININE RATIO"},
    {"code": "CA", "display": "CALCIUM"},
    {"code": "ECO2", "display": "CARBON DIOXIDE"},
    {"code": "CL", "display": "CHLORIDE"},
    {"code": "BC", "display": "CONJUGATED BILIRUBIN"},
    {"code": "CREA", "display": "CREATININE"},
    {"code": "DBIL", "display": "DIRECT BILIRUBIN"},
    {"code": "DHDL", "display": "DIRECT HDLC"},
    {"code": "FERR", "display": "FERRITIN"},
    {"code": "FOL", "display": "FOLATE"},
    {"code": "GFR", "display": "GLOMERULAR FILTRATION RATE"},
    {"code": "GLU", "display": "GLUCOSE"},
    {"code": "HIVC", "display": "HIV COMBO"},
    {"code": "LAC", "display": "LACTATE"},
    {"code": "LDH", "display": "LDH"},
    {"code": "LIPA", "display": "LIPASE"},
    {"code": "MG", "display": "MAGNESIUM"},
    {"code": "PHOS", "display": "PHOSPHOROUS"},
    {"code": "K", "display": "POTASSIUM"},
    {"code": "PCT", "display": "PROCALCITONIN"},
    {"code": "NA", "display": "SODIUM"},
    {"code": "BHCG", "display": "TOTAL BETA HCG"},
    {"code": "TBIL", "display": "TOTAL BILIRUBIN"},
    {"code": "CHOL", "display": "TOTAL CHOLESTEROL"},
    {"code": "TP", "display": "TOTAL PROTEIN"},
    {"code": "TRIG", "display": "TRIGLYCERIDES"}
]

# Create tables and populate them with data
for table in tables:
    # Create table
    table_creation_response = requests.put(
        f"{AIDBOX_URL}/admin/{table['id']}",
        headers=headers,
        auth=auth,
        json=table
    )
    print(f"Creating table {table['id']} - Status code: {table_creation_response.status_code}")

    # Populate table with data
    if table['id'] == "CimparRace":
        data_list = race_data
    elif table['id'] == "CimparEthnicity":
        data_list = ethnicity_data
    elif table['id'] == "CimparState":
        data_list = state_data
    elif table['id'] == "CimparLabTest":
        data_list = lab_test_data

    for data in data_list:
        entry_creation_response = requests.post(
            f"{AIDBOX_URL}/{table['id']}",
            headers=headers,
            auth=auth,
            json=data
        )
        print(f"Adding data to {table['id']} - Status code: {entry_creation_response.status_code}")

print("Script execution completed.")
