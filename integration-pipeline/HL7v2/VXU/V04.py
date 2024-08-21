import requests
import logging
from aidbox.base import API

from HL7v2.resources.patient import prepare_patient
from HL7v2.resources.encounter import prepare_encounters
from HL7v2.resources.immunization import prepare_immunization

logger = logging.getLogger("log")


def run(message):
    entry = []
    patient_group = message.get("patient_group", {})
    patient_group["patient"]["icare_patient_id"] = message["icare_patient_id"]
    patient, patient_url = prepare_patient(patient_group["patient"])

    if "patient" in patient_group:
        entry.append(
            {
                "resource": patient.dumps(exclude_none=True, exclude_unset=True),
                "request": {"method": "PUT", "url": patient_url},
            }
        )

    if "visit" in patient_group:
        visit = prepare_encounters(patient_group["visit"], patient=patient)

        for item in visit[0]:
            entry.append(
                {
                    "resource": item.dumps(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Location"},
                }
            )

        for item in visit[1]:
            entry.append(
                {
                    "resource": item.dumps(exclude_unset=True),
                    "request": {"method": "PUT", "url": "Practitioner"},
                }
            )

        entry.append(
            {
                "resource": visit[2].dumps(exclude_unset=True),
                "request": {"method": "PUT", "url": "Encounter"},
            }
        )

    if "immunization" in message:
        immunization = prepare_immunization(message["immunization"], patient)

        entry.append(
            {
                "resource": immunization.dumps(exclude_none=True, exclude_unset=True),
                "request": {"method": "PUT", "url": "Immunization"},
            }
        )

    try:
        API.bundle(entry=entry, type="transaction")
        return {"patient_url": patient_url, "patient_id": patient.id}
    except requests.exceptions.RequestException as e:
        logger.error("Unable to create the VX04: %s" % str(e))
        if e.response is not None:
            print(e.response.json())
        raise Exception("Unable to create the VXU_V04 Entry: %s" % str(e))

