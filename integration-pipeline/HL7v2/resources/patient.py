from aidbox.resource.patient import Patient, Patient_Communication, Patient_Contact, Patient_Link
from aidbox.base import (
    HumanName,
    ContactPoint,
    Address,
    Identifier,
    CodeableConcept,
    Coding,
    Extension,
    Meta,
    Reference
)

from HL7v2 import get_patient_id
from models.patient_validation import validate_state
from HL7v2.resources.utils import format_birth_date


def get_gender_by_code(code):
    match code:
        case "F":
            return "female"
        case "M":
            return "male"
        case _:
            return "unknown"


def get_marital_status_code(code):
    system = "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus"

    match code:
        case "1":
            return Coding(system=system, code="A", display="Annulled")
        case "13":
            return Coding(system=system, code="M", display="Married")
        case _:
            return Coding(system=system, code="UNK", display="unknown")


def get_language_by_code(code):
    system = "http://hl7.org/fhir/ValueSet/languages"

    match code:
        case "13":
            return Coding(system=system, code="pl-PL", display="Polish (Poland)")
        case "27":
            return Coding(system=system, code="zh-CN", display="Chinese (China)")
        case _:
            return Coding(
                system=system, code="en-US", display="English (United States)"
            )


def prepare_patient(data):
    patient_id, patient = get_patient_id({"patient": data})
    patient_url = "Patient"
    if Patient.get({"id": patient_id}):
        patient_url += f"/{patient_id}"
    if "name" in data:
        patient.name = list(map(lambda item: HumanName(**item), data["name"]))

    if "birthDate" in data:
        patient.birthDate = format_birth_date(data["birthDate"])

    if "gender" in data:
        patient.gender = get_gender_by_code(data["gender"])

    if "address" in data:
        patient.address = list(
            map(
                lambda item: Address(
                    use=item.get("use", "work").lower(),
                    city=item.get("city", None),
                    state=validate_state(item.get("state")),
                    country=item.get("country", None),
                    line=item.get("line", []),
                    postalCode=item.get("postalCode", None),
                ),
                data["address"],
            )
        )
    if "telecom" in data and data["telecom"]:
        existing_telecom_dict = {}
        contact = patient.contact and patient.contact[0]
        if not contact:
            contact = Patient_Contact()
            patient.contact = [contact]
        if contact and contact.telecom:
            for tp in contact.telecom:
                if tp.system == "email":
                    existing_telecom_dict[(tp.system,)] = tp
                else:
                    existing_telecom_dict[(tp.use, tp.system)] = tp
        # Process new telecom data and update the existing dictionary
        for item in data.get("telecom", []):
            use = item.get("use")
            system = item.get("system")
            value = item.get(system)
            if system == "email":
                existing_telecom_dict[("email",)] = ContactPoint(system="email", value=value)
            elif system == "phone" and use == "home":
                existing_telecom_dict[("home", "phone")] = ContactPoint(use="home", system="phone", value=value)
            elif system == "phone" and use == "temp":
                existing_telecom_dict[("temp", "phone")] = ContactPoint(use="temp", system="phone", value=value)

        patient.contact[0].telecom = list(existing_telecom_dict.values())

    if "identifier" in data:
        patient.identifier = [
            Identifier(**item) for item in data["identifier"] if "system" in item
        ]

    if "marital_status" in data:
        patient.maritalStatus = CodeableConcept(coding=[get_marital_status_code(data)])

    if "language" in data:
        patient.communication = [
            Patient_Communication(
                language=CodeableConcept(
                    coding=[get_language_by_code(data["language"])]
                )
            )
        ]

    if ("race" in data) or ("ethnicity" in data):
        patient.meta = Meta(
            profile = ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
        )
    if not patient.extension:
        patient.extension = []
    if "race" in data:
        race_extension = Extension(
            extension = list(
                map(
                    lambda race: Extension(
                        url = "detailed",
                        valueCoding = Coding(
                            system = race.get("system", ""),
                            code = race.get("code", ""),
                            display = race.get("display", ""),
                        )
                    ),
                    data["race"]
                )
            ),

            url = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-race"
        )

        race_extension.extension.append(Extension(
            url = "text",
            valueString = race_extension.extension[0].valueCoding.display
            if race_extension.extension[0].valueCoding.display else race_extension.extension[0].valueCoding.code
        ))

        patient.extension.append(race_extension)

    if "ethnicity" in data:
        ethnicity_extension = Extension(
            extension = list(
                map(
                    lambda ethnicity: Extension(
                        url = "detailed",
                        valueCoding = Coding(
                            system = ethnicity.get("system", ""),
                            code = ethnicity.get("code", ""),
                            display = ethnicity.get("display", ""),
                        )
                    ),
                    data["ethnicity"]
                )
            ),
            url = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity"
        )

        ethnicity_extension.extension.append(Extension(
            url = "text",
            valueString = ethnicity_extension.extension[0].valueCoding.display
        ))
        
        patient.extension.append(ethnicity_extension)
        if "icare_patient_id" in data and data["icare_patient_id"]:
            patient.link = [
                Patient_Link(
                    type="refer",
                    other=Reference(
                        id=data["icare_patient_id"],
                        reference="icare_patient_id"
                    )
                )
            ]
    return patient, patient_url
