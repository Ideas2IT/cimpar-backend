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
    {"code": "1002-5", "display": "American Indian or Alaska Native", "is_active": True},
    {"code": "2028-9", "display": "Asian", "is_active": True},
    {"code": "2054-5", "display": "Black or African American", "is_active": True},
    {"code": "2076-8", "display": "Native Hawaiian or Other Pacific Islander", "is_active": True},
    {"code": "2106-3", "display": "White", "is_active": True},
    {"code": "2131-1", "display": "Other Race", "is_active": True},
    {"code": "0", "display": "Unknown", "is_active": True}
]

ethnicity_data = [
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2186-5", "display": "Not Hispanic or Latino", "is_active": True},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2137-8", "display": "Spaniard", "is_active": True},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2140-2", "display": "Castillian", "is_active": True},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2144-4", "display": "Valencian", "is_active": True},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2145-1", "display": "Canarian", "is_active": True},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "2135-2", "display": "Hispanic or Latino", "is_active": True},
    {"system": "http://terminology.hl7.org/CodeSystem/v3-Ethnicity", "code": "0", "display": "Unknown", "is_active": True}
]

state_data = [
    {"code": "AL", "state": "Alabama", "capital": "Montgomery", "display": "Alabama", "is_active": True},
    {"code": "AK", "state": "Alaska", "capital": "Juneau", "display": "Alaska", "is_active": True},
    {"code": "AZ", "state": "Arizona", "capital": "Phoenix", "display": "Arizona", "is_active": True},
    {"code": "AR", "state": "Arkansas", "capital": "Little Rock", "display": "Arkansas", "is_active": True},
    {"code": "CA", "state": "California", "capital": "Sacramento", "display": "California", "is_active": True},
    {"code": "CO", "state": "Colorado", "capital": "Denver", "display": "Colorado", "is_active": True},
    {"code": "CT", "state": "Connecticut", "capital": "Hartford", "display": "Connecticut", "is_active": True},
    {"code": "DE", "state": "Delaware", "capital": "Dover", "display": "Delaware", "is_active": True},
    {"code": "FL", "state": "Florida", "capital": "Tallahassee", "display": "Florida", "is_active": True},
    {"code": "GA", "state": "Georgia", "capital": "Atlanta", "display": "Georgia", "is_active": True},
    {"code": "HI", "state": "Hawaii", "capital": "Honolulu", "display": "Hawaii", "is_active": True},
    {"code": "ID", "state": "Idaho", "capital": "Boise", "display": "Idaho", "is_active": True},
    {"code": "IL", "state": "Illinois", "capital": "Springfield", "display": "Illinois", "is_active": True},
    {"code": "IN", "state": "Indiana", "capital": "Indianapolis", "display": "Indiana", "is_active": True},
    {"code": "IA", "state": "Iowa", "capital": "Des Moines", "display": "Iowa", "is_active": True},
    {"code": "KS", "state": "Kansas", "capital": "Topeka", "display": "Kansas", "is_active": True},
    {"code": "KY", "state": "Kentucky", "capital": "Frankfort", "display": "Kentucky", "is_active": True},
    {"code": "LA", "state": "Louisiana", "capital": "Baton Rouge", "display": "Louisiana", "is_active": True},
    {"code": "ME", "state": "Maine", "capital": "Augusta", "display": "Maine", "is_active": True},
    {"code": "MD", "state": "Maryland", "capital": "Annapolis", "display": "Maryland", "is_active": True},
    {"code": "MA", "state": "Massachusetts", "capital": "Boston", "display": "Massachusetts", "is_active": True},
    {"code": "MI", "state": "Michigan", "capital": "Lansing", "display": "Michigan", "is_active": True},
    {"code": "MN", "state": "Minnesota", "capital": "Saint Paul", "display": "Minnesota", "is_active": True},
    {"code": "MS", "state": "Mississippi", "capital": "Jackson", "display": "Mississippi", "is_active": True},
    {"code": "MO", "state": "Missouri", "capital": "Jefferson City", "display": "Missouri", "is_active": True},
    {"code": "MT", "state": "Montana", "capital": "Helena", "display": "Montana", "is_active": True},
    {"code": "NE", "state": "Nebraska", "capital": "Lincoln", "display": "Nebraska", "is_active": True},
    {"code": "NV", "state": "Nevada", "capital": "Carson City", "display": "Nevada", "is_active": True},
    {"code": "NH", "state": "New Hampshire", "capital": "Concord", "display": "New Hampshire", "is_active": True},
    {"code": "NJ", "state": "New Jersey", "capital": "Trenton", "display": "New Jersey", "is_active": True},
    {"code": "NM", "state": "New Mexico", "capital": "Santa Fe", "display": "New Mexico", "is_active": True},
    {"code": "NY", "state": "New York", "capital": "Albany", "display": "New York", "is_active": True},
    {"code": "NC", "state": "North Carolina", "capital": "Raleigh", "display": "North Carolina", "is_active": True},
    {"code": "ND", "state": "North Dakota", "capital": "Bismarck", "display": "North Dakota", "is_active": True},
    {"code": "OH", "state": "Ohio", "capital": "Columbus", "display": "Ohio", "is_active": True},
    {"code": "OK", "state": "Oklahoma", "capital": "Oklahoma City", "display": "Oklahoma", "is_active": True},
    {"code": "OR", "state": "Oregon", "capital": "Salem", "display": "Oregon", "is_active": True},
    {"code": "PA", "state": "Pennsylvania", "capital": "Harrisburg", "display": "Pennsylvania", "is_active": True},
    {"code": "RI", "state": "Rhode Island", "capital": "Providence", "display": "Rhode Island", "is_active": True},
    {"code": "SC", "state": "South Carolina", "capital": "Columbia", "display": "South Carolina", "is_active": True},
    {"code": "SD", "state": "South Dakota", "capital": "Pierre", "display": "South Dakota", "is_active": True},
    {"code": "TN", "state": "Tennessee", "capital": "Nashville", "display": "Tennessee", "is_active": True},
    {"code": "TX", "state": "Texas", "capital": "Austin", "display": "Texas", "is_active": True},
    {"code": "UT", "state": "Utah", "capital": "Salt Lake City", "display": "Utah", "is_active": True},
    {"code": "VT", "state": "Vermont", "capital": "Montpelier", "display": "Vermont", "is_active": True},
    {"code": "VA", "state": "Virginia", "capital": "Richmond", "display": "Virginia", "is_active": True},
    {"code": "WA", "state": "Washington", "capital": "Olympia", "display": "Washington", "is_active": True},
    {"code": "WV", "state": "West Virginia", "capital": "Charleston", "display": "West Virginia", "is_active": True},
    {"code": "WI", "state": "Wisconsin", "capital": "Madison", "display": "Wisconsin", "is_active": True},
    {"code": "WY", "state": "Wyoming", "capital": "Cheyenne", "display": "Wyoming", "is_active": True}
]

lab_test_data =  [
    {"code": "49765-1", "display": "Calcium", "is_active": True},
    {"code": "2069-3", "display": "Chloride", "is_active": True},
    {"code": "59826-8", "display": "Creatinine", "is_active": True},
    {"code": "2024-8", "display": "Carbon Dioxide", "is_active": True},
    {"code": "1557-8", "display": "Glucose", "is_active": True},
    {"code": "6298-4", "display": "Potassium", "is_active": True},
    {"code": "2947-0", "display": "Sodium", "is_active": True},
    {"code": "6299-2", "display": "Urea Nitrogen", "is_active": True},
    {"code": "1751-7", "display": "Albumin", "is_active": True},
    {"code": "42719-5", "display": "Total Bilirubin", "is_active": True},
    {"code": "77141-0", "display": "Alkaline Phosphatase", "is_active": True},
    {"code": "76625-3", "display": "ALT", "is_active": True},
    {"code": "48136-6", "display": "AST", "is_active": True},
    {"code": "2093-3", "display": "Total Cholesterol", "is_active": True},
    {"code": "3043-7", "display": "Triglycerides", "is_active": True},
    {"code": "2085-9", "display": "HDL-Cholesterol", "is_active": True},
    {"code": "98981-4", "display": "Uric Acid", "is_active": True},
    {"code": "4548-4", "display": "Hemoglobin A1C", "is_active": True},
    {"code": "3015-5", "display": "TSH", "is_active": True},
    {"code": "3024-7", "display": "Free T4", "is_active": True},
    {"code": "20507-0", "display": "RPR", "is_active": True},
    {"code": "58410-2", "display": "Covid", "is_active": True},
    {"code": "0101U", "display": "Test for detection of high-risk human papillomavirus in male urine", "is_active": True},
    {"code": "0240U", "display": "Respiratory infectious agent detection by RNA for severe acute respiratory", "is_active": True},
    {"code": "0353U", "display": "Detection of bacteria causing vaginosis and vaginitis by multiplex amplified", "is_active": True},
    {"code": "0354U", "display": "Detection of Chlamydia trachomatis and Neisseria gonorrhoeae by multiplex", "is_active": True},
    {"code": "0372U", "display": "Test for 16 genitourinary bacterial organisms and 1 genitourinary fungal", "is_active": True},
    {"code": "80061", "display": "Blood test, lipids (cholesterol and triglycerides)", "is_active": True},
    {"code": "82731", "display": "Ferritin (blood protein) level", "is_active": True},
    {"code": "82747", "display": "Folic acid level, serum", "is_active": True},
    {"code": "83037", "display": "Hemoglobin A1C level", "is_active": True},
    {"code": "85032", "display": "Complete blood cell count (red cells, white blood cell, platelets), automated", "is_active": True},
    {"code": "86704", "display": "Analysis for antibody to HIV-1 and HIV-2 virus", "active": True},
    {"code": "86707", "display": "Hepatitis B surface antibody measurement", "is_active": True},
    {"code": "86709", "display": "Measurement of Hepatitis A antibody", "is_active": True},
    {"code": "86710", "display": "Measurement of Hepatitis A antibody (IgM)", "is_active": True},
    {"code": "86711", "display": "Analysis for antibody to Influenza virus", "is_active": True},
    {"code": "86780", "display": "Analysis for antibody, Treponema pallidum", "is_active": True},
    {"code": "86803", "display": "Hepatitis C antibody measurement", "is_active": True},
    {"code": "87154", "display": "Identification of organisms by nucleic acid sequencing method", "is_active": True},
    {"code": "87341", "display": "Detection test by immunoassay technique for Hepatitis B surface antigen", "is_active": True},
    {"code": "87389", "display": "Detection test by immunoassay technique for HIV-1 antigen and HIV-1 and HIV-2", "is_active": True},
    {"code": "87506", "display": "Detection test by nucleic acid for digestive tract pathogen, multiple types or", "is_active": True},
    {"code": "87512", "display": "Detection test for gardnerella vaginalis (bacteria), amplified probe technique", "is_active": True},
    {"code": "87591", "display": "Detection test by nucleic acid for Neisseria gonorrhoeae (gonorrhoeae", "is_active": True},
    {"code": "87631", "display": "Detection test by nucleic acid for human papillomavirus (hpv), types 16 and 18", "is_active": True},
    {"code": "87631", "display": "Detection test by nucleic acid for multiple types of respiratory virus,", "is_active": True},
    {"code": "87634", "display": "Detection test by nucleic acid for respiratory syncytial virus, amplified probe", "is_active": True},
    {"code": "87635", "display": "Amplifed DNA or RNA probe detection of severe acute respiratory syndrome", "is_active": True}
]


insurance_company_data = [
    {"display": "AAA Insurance Company", "code": "11983", "is_active": True},
    {"display": "Allstate Insurance", "code": "19232", "is_active": True},
    {"display": "Direct Auto Insurance", "code": "20133", "is_active": True},
    {"display": "Geico Insurance", "code": "35882", "is_active": True},
    {"display": "Liberty Mutual Insurance", "code": "23043", "is_active": True},
    {"display": "Progressive Insurance", "code": "24260", "is_active": True},
    {"display": "State Farm Insurance", "code": "25178", "is_active": True},
    {"display": "The General Insurance", "code": "13703", "is_active": True},
    {"display": "Travelers Insurance", "code": "25658", "is_active": True},
    {"display": "USAA Insurance", "code": "186000", "is_active": True}
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
