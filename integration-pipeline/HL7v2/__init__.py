import hashlib
from typing import Optional, Union
import random, string, hashlib, argparse, sys
from aidbox.resource.patient import Patient

def random_md5():
    random_string = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    return hashlib.md5(random_string.encode()).hexdigest()


def get_md5(strings: list[Union[str, None]] = []):
    data: list[str] = []

    if len(strings) == 0 or all(element is None for element in strings):
        return random_md5()

    for s in strings:
        if s is not None:
            data.append(s)

    return hashlib.md5("".join(data).encode("utf-8")).hexdigest()


def pop_string(data: Union[list[str], str, None]):
    if isinstance(data, list):
        return data.pop()

    if isinstance(data, str):
        return data

    return ""


def get_resource_id(data):
    if "patient" in data:
        if "identifier" in data["patient"]:
            official = next(
                (
                    item
                    for item in data["patient"]["identifier"]
                    if item.get("use") == "official"
                ),
                None,
            )
            if official is not None:
                return get_md5([official["value"]])

    return get_md5([""])


def get_first_last_name_dob(data):
    if "patient" in data:
        patient = data["patient"]
        # Extract the first name and last name
        if "name" in patient:
            official_name = next((item for item in patient["name"] if item.get("use") == "official"), None)
            if official_name:
                first_name = official_name["given"][0] if "given" in official_name and official_name["given"] else ""
                last_name = official_name["family"] if "family" in official_name else ""
            else:
                first_name = last_name = ""
        else:
            first_name = last_name = ""
        dob = patient.get("birthDate")
        return first_name, last_name, dob
    return "", "", ""


def get_patient_id(data):
    first_name, last_name, dob = get_first_last_name_dob(data)
    patients = Patient.get({".name.0.given.0": str(first_name), ".birthDate": str(dob),
                            ".name.0.family": str(last_name)})
    if patients:
        return patients[0].id, patients[0]
    patient_id = get_md5([first_name, last_name, dob])
    return patient_id, Patient(id=patient_id)


def get_unique_patient_id_json(first_name="", last_name="", dob=""):
    return get_md5([first_name, last_name, dob])


