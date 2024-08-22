import requests
from requests.auth import HTTPBasicAuth

AIDBOX_URL = {{HOST}}
AIDBOX_CLIENT_USERNAME = {{USERNAME}}
AIDBOX_CLIENT_PASSWORD = {{PASSWORD}}

# Common headers for all requests
headers = {"Content-Type": "application/json"}
concept_headers = {"Content-Type": "text/yaml","Accept": "text/yaml"}

# Auth credentials
auth = HTTPBasicAuth(AIDBOX_CLIENT_USERNAME, AIDBOX_CLIENT_PASSWORD)

# Table creation data
tables = [
    {"id": "CimparRace", "type": "resource", "isOpen": True},
    {"id": "CimparEthnicity", "type": "resource", "isOpen": True},
    {"id": "CimparState", "type": "resource", "isOpen": True},
    {"id": "CimparLabTest", "type": "resource", "isOpen": True},
    {"id": "CimparInsuranceCompany", "type": "resource", "isOpen": True},
    {"id": "Concept"}
]

# Data for each table
race_data = [
    {"code": "1002-5", "display": "American Indian or Alaska Native"},
    {"code": "2028-9", "display": "Asian"},
    {"code": "2054-5", "display": "Black or African American"},
    {"code": "2076-8", "display": "Native Hawaiian or Other Pacific Islander"},
    {"code": "2106-3", "display": "White"},
    {"code": "2131-1", "display": "Other Race"},
    {"code": "0", "display": "Unknown"}
]

ethnicity_data = [
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2186-5", "display": "Not Hispanic or Latino"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2137-8", "display": "Spaniard"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2140-2", "display": "Castillian"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2144-4", "display": "Valencian"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2145-1", "display": "Canarian"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2135-2", "display": "Hispanic or Latino"},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "0", "display": "Unknown"}
]

state_data = [
    {"code": "AL", "state": "Alabama", "capital": "Montgomery", "display": "Alabama"},
    {"code": "AK", "state": "Alaska", "capital": "Juneau", "display": "Alaska"},
    {"code": "AZ", "state": "Arizona", "capital": "Phoenix", "display": "Arizona"},
    {"code": "AR", "state": "Arkansas", "capital": "Little Rock", "display": "Arkansas"},
    {"code": "CA", "state": "California", "capital": "Sacramento", "display": "California"},
    {"code": "CO", "state": "Colorado", "capital": "Denver", "display": "Colorado"},
    {"code": "CT", "state": "Connecticut", "capital": "Hartford", "display": "Connecticut"},
    {"code": "DE", "state": "Delaware", "capital": "Dover", "display": "Delaware"},
    {"code": "FL", "state": "Florida", "capital": "Tallahassee", "display": "Florida"},
    {"code": "GA", "state": "Georgia", "capital": "Atlanta", "display": "Georgia"},
    {"code": "HI", "state": "Hawaii", "capital": "Honolulu", "display": "Hawaii"},
    {"code": "ID", "state": "Idaho", "capital": "Boise", "display": "Idaho"},
    {"code": "IL", "state": "Illinois", "capital": "Springfield", "display": "Illinois"},
    {"code": "IN", "state": "Indiana", "capital": "Indianapolis", "display": "Indiana"},
    {"code": "IA", "state": "Iowa", "capital": "Des Moines", "display": "Iowa"},
    {"code": "KS", "state": "Kansas", "capital": "Topeka", "display": "Kansas"},
    {"code": "KY", "state": "Kentucky", "capital": "Frankfort", "display": "Kentucky"},
    {"code": "LA", "state": "Louisiana", "capital": "Baton Rouge", "display": "Louisiana"},
    {"code": "ME", "state": "Maine", "capital": "Augusta", "display": "Maine"},
    {"code": "MD", "state": "Maryland", "capital": "Annapolis", "display": "Maryland"},
    {"code": "MA", "state": "Massachusetts", "capital": "Boston", "display": "Massachusetts"},
    {"code": "MI", "state": "Michigan", "capital": "Lansing", "display": "Michigan"},
    {"code": "MN", "state": "Minnesota", "capital": "Saint Paul", "display": "Minnesota"},
    {"code": "MS", "state": "Mississippi", "capital": "Jackson", "display": "Mississippi"},
    {"code": "MO", "state": "Missouri", "capital": "Jefferson City", "display": "Missouri"},
    {"code": "MT", "state": "Montana", "capital": "Helena", "display": "Montana"},
    {"code": "NE", "state": "Nebraska", "capital": "Lincoln", "display": "Nebraska"},
    {"code": "NV", "state": "Nevada", "capital": "Carson City", "display": "Nevada"},
    {"code": "NH", "state": "New Hampshire", "capital": "Concord", "display": "New Hampshire"},
    {"code": "NJ", "state": "New Jersey", "capital": "Trenton", "display": "New Jersey"},
    {"code": "NM", "state": "New Mexico", "capital": "Santa Fe", "display": "New Mexico"},
    {"code": "NY", "state": "New York", "capital": "Albany", "display": "New York"},
    {"code": "NC", "state": "North Carolina", "capital": "Raleigh", "display": "North Carolina"},
    {"code": "ND", "state": "North Dakota", "capital": "Bismarck", "display": "North Dakota"},
    {"code": "OH", "state": "Ohio", "capital": "Columbus", "display": "Ohio"},
    {"code": "OK", "state": "Oklahoma", "capital": "Oklahoma City", "display": "Oklahoma"},
    {"code": "OR", "state": "Oregon", "capital": "Salem", "display": "Oregon"},
    {"code": "PA", "state": "Pennsylvania", "capital": "Harrisburg", "display": "Pennsylvania"},
    {"code": "RI", "state": "Rhode Island", "capital": "Providence", "display": "Rhode Island"},
    {"code": "SC", "state": "South Carolina", "capital": "Columbia", "display": "South Carolina"},
    {"code": "SD", "state": "South Dakota", "capital": "Pierre", "display": "South Dakota"},
    {"code": "TN", "state": "Tennessee", "capital": "Nashville", "display": "Tennessee"},
    {"code": "TX", "state": "Texas", "capital": "Austin", "display": "Texas"},
    {"code": "UT", "state": "Utah", "capital": "Salt Lake City", "display": "Utah"},
    {"code": "VT", "state": "Vermont", "capital": "Montpelier", "display": "Vermont"},
    {"code": "VA", "state": "Virginia", "capital": "Richmond", "display": "Virginia"},
    {"code": "WA", "state": "Washington", "capital": "Olympia", "display": "Washington"},
    {"code": "WV", "state": "West Virginia", "capital": "Charleston", "display": "West Virginia"},
    {"code": "WI", "state": "Wisconsin", "capital": "Madison", "display": "Wisconsin"},
    {"code": "WY", "state": "Wyoming", "capital": "Cheyenne", "display": "Wyoming"}
]

lab_test_data = [
    {'code': '49765-1', 'display': 'Calcium'},
    {'code': '2069-3', 'display': 'Chloride'},
    {'code': '59826-8', 'display': 'Creatinine'},
    {'code': '2024-8', 'display': 'Carbon Dioxide'},
    {'code': '1557-8', 'display': 'Glucose'},
    {'code': '6298-4', 'display': 'Potassium'},
    {'code': '2947-0', 'display': 'Sodium'},
    {'code': '6299-2', 'display': 'Urea Nitrogen'},
    {'code': '', 'display': 'CMP'},
    {'code': '1751-7', 'display': 'Albumin'},
    {'code': '42719-5', 'display': 'Total Bilirubin'},
    {'code': '77141-0', 'display': 'Alkaline Phosphatase'},
    {'code': '', 'display': 'Total Protein'},
    {'code': '76625-3', 'display': 'ALT'},
    {'code': '48136-6', 'display': 'AST'},
    {'code': '', 'display': 'Lipid Panel'},
    {'code': '2093-3', 'display': 'Total Cholesterol'},
    {'code': '3043-7', 'display': 'Triglycerides'},
    {'code': '2085-9', 'display': 'HDL-Cholesterol'},
    {'code': '98981-4', 'display': 'Uric Acid'},
    {'code': '4548-4', 'display': 'Hemoglobin A1C'},
    {'code': '3015-5', 'display': 'TSH'},
    {'code': '3024-7', 'display': 'Free T4'},
    {'code': '20507-0', 'display': 'RPR'}, 
    {'code': '58410-2', 'display': 'Covid'},
    {'code': '0101U', 'display': 'Test for detection of high-risk human papillomavirus in male urine'},
    {'code': '0240U', 'display': 'Respiratory infectious agent detection by RNA for severe acute respiratory'},
    {'code': '0353U', 'display': 'Detection of bacteria causing vaginosis and vaginitis by multiplex amplified'},
    {'code': '0354U', 'display': 'Detection of Chlamydia trachomatis and Neisseria gonorrhoeae by multiplex'},
    {'code': '0372U', 'display': 'Test for 16 genitourinary bacterial organisms and 1 genitourinary fungal'},
    {'code': "80061", 'display': 'Blood test, lipids (cholesterol and triglycerides)'},
    {'code': "82731", 'display': 'Ferritin (blood protein) level'},
    {'code': "82747", 'display': 'Folic acid level, serum'},
    {'code': "83036", 'display': 'Hemoglobin A1C level'},
    {'code': "83037", 'display': 'Hemoglobin A1C level'},
    {'code': "85032", 'display': 'Complete blood cell count (red cells, white blood cell, platelets), automated'},
    {'code': "86704", 'display': 'Analysis for antibody to HIV-1 and HIV-2 virus'},
    {'code': "86707", 'display': 'Hepatitis B surface antibody measurement'},
    {'code': "86709", 'display': 'Measurement of Hepatitis A antibody'},
    {'code': "86710", 'display': 'Measurement of Hepatitis A antibody (IgM)'},
    {'code': "86711", 'display': 'Analysis for antibody to Influenza virus'},
    {'code': "86780", 'display': 'Analysis for antibody, Treponema pallidum'},
    {'code': "86803", 'display': 'Hepatitis C antibody measurement'},
    {'code': "87154", 'display': 'Identification of organisms by nucleic acid sequencing method'},
    {'code': "87341", 'display': 'Detection test by immunoassay technique for Hepatitis B surface antigen'},
    {'code': "87389", 'display': 'Detection test by immunoassay technique for HIV-1 antigen and HIV-1 and HIV-2'},
    {'code': "87506", 'display': 'Detection test by nucleic acid for digestive tract pathogen, multiple types or'},
    {'code': "87512", 'display': 'Detection test for gardnerella vaginalis (bacteria), amplified probe technique'},
    {'code': "87591", 'display': 'Detection test by nucleic acid for Neisseria gonorrhoeae (gonorrhoeae'},
    {'code': "87631", 'display': 'Detection test by nucleic acid for human papillomavirus (hpv), types 16 and 18'},
    {'code': "87631", 'display': 'Detection test by nucleic acid for multiple types of respiratory virus,'},
    {'code': "87634", 'display': 'Detection test by nucleic acid for respiratory syncytial virus, amplified probe'},
    {'code': "87635", 'display': 'Amplifed DNA or RNA probe detection of severe acute respiratory syndrome'}
]

insurance_company_data = [
    {"display": "AAA Insurance Company", "code": "11983"},
    {"display": "Allstate Insurance", "code": "19232"},
    {"display": "Direct Auto Insurance", "code": "20133"},
    {"display": "Geico Insurance", "code": "35882"},
    {"display": "Liberty Mutual Insurance", "code": "23043"},
    {"display": "Progressive Insurance", "code": "24260"},
    {"display": "State Farm Insurance", "code": "25178"},
    {"display": "The General Insurance", "code": "13703"},
    {"display": "Travelers Insurance", "code": "25658"},
    {"display": "USAA Insurance", "code": "186000"},
]

concept_data = [
    {
        "icd10": "https://storage.googleapis.com/ftr/icd10cm/vs/http%3A--hl7.org-fhir-ValueSet-icd-10/tf.5e7b9e0dc05aace8f1a3c8b086556438b0b87848c9304fe9999d8b237e67a8ee.ndjson.gz",
        "rxnorm": "https://storage.googleapis.com/ftr/rxnorm/vs/http%3A--www.nlm.nih.gov-research-umls-rxnorm-valueset/tf.c32766ceb2ec7285a85529d18286565711c506e0cec5de6cfbe3f8ab5192a1bc.ndjson.gz",
        "snomed": "https://storage.googleapis.com/ftr/snomed/vs/http%3A--snomed.info-sct/tf.3534d92087b0acc5c88cd1ef10e38c5758073f4b5fd217bcce679b37aff5a86.ndjson.gz"
    }
]

# Create tables and populate them with data
for table in tables:
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
    elif table['id'] == "CimparInsuranceCompany":
        data_list = insurance_company_data
    elif table["id"] == "Concept":
        data_list = concept_data

    if table["id"] == "Concept":
        concept_headers = headers.copy()
        concept_headers["Content-Type"] = "text/yaml"
        concept_headers["Accept"] = "text/yaml"

        for url in concept_data[0].values():
            entry_creation_response = requests.post(
                f"{AIDBOX_URL}/terminology/$import",
                headers=concept_headers,
                auth=auth,
                json={"url": url}
            )
    else:
        for data in data_list:
            entry_creation_response = requests.post(
                f"{AIDBOX_URL}/{table['id']}",
                headers=headers,
                auth=auth,
                json=data
            )
        print(f"Adding data to {table['id']} - Status code: {entry_creation_response.status_code}")

print("Script execution completed.")
