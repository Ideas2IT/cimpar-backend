import requests

from aidbox.base import (
    API,
    Reference
)
from aidbox.resource.patient import Patient
from aidbox.resource.location import Location
from aidbox.resource.practitioner import Practitioner

from HL7v2.resources.observation import prepare_observation
from HL7v2.resources.patient import prepare_patient
from HL7v2.resources.allergyintolerance import prepare_allergies
from HL7v2.resources.encounter import prepare_encounters
from HL7v2.resources.coverage import prepare_coverage
from HL7v2.resources.relatedperson import prepare_related_persons
from HL7v2.resources.procedure import prepare_procedure
from HL7v2.resources.condition import prepare_condition
from HL7v2.resources.diagnosticreport import prepare_diagnostic_report


def run(message):
    patient_data = message.get("patient_group")
    order_data = message.get("order_group")
    visit_data = message.get("visit")
    entry = []
    patient = prepare_patient(patient_data["patient"])

    patient_url = "Patient"
    if Patient.get({"id": patient.id}):
        patient_url += f"/{patient.id}"

    if "patient" in patient_data:
        entry.append(
            {
                "resource": patient.dumps(exclude_none=True, exclude_unset=True),
                "request": {"method": "PUT", "url": patient_url},
            }
        )

    if visit_data:
        locations, practitioners, encounter = prepare_encounters(visit_data, patient=patient)
        for location in locations:
            location_url = 'Location'
            if Location.get({"id": location.id}):
                location_url += f"/{location.id}"
            entry.append(
                {
                    "resource": location.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": location_url},
                }
            )

        for practitioner in practitioners:
            practitioners_url = 'Practitioner'
            if Practitioner.get({"id": practitioner.id}):
                practitioners_url += f"/{practitioner.id}"
            entry.append(
                {
                    "resource": practitioner.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": practitioners_url},
                }
            )

        entry.append(
            {
                "resource": encounter.dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "Encounter"},
            }
        )

    if order_data:
        if "order" in order_data:
            main_diagnostic_report, practitioner_roles, observations = prepare_diagnostic_report(order_data["order"], patient, encounter=None, parent=None)

            for practitioner_role in practitioner_roles:
                entry.append({
                    "resource": practitioner_role.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "PractitionerRole/" + practitioner_role.id}
                })

            for observation in observations:
                entry.append({
                    "resource": observation.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Observation/" + observation.id}
                })

            entry.append({
                "resource": main_diagnostic_report.dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "DiagnosticReport/" + main_diagnostic_report.id}
            })

        for observation_data in order_data.get("observations", []):
            observation, organizations, practitioner_roles = prepare_observation(observation_data, patient, parent = None, specimen=None, encounter=None)

            entry.append({
                "resource": observation.dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "Observation/" + observation.id}
            })

            for organization in organizations:
                entry.append({
                    "resource": organization.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Organization/" + organization.id}
                })

            for practitioner_role in practitioner_roles:
                entry.append({
                    "resource": practitioner_role.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "PractitionerRole/" + practitioner_role.id}
                })

        for observation_request_data in order_data.get("observation_requests", []):
            diagnostic_report, practitioner_roles, observations = prepare_diagnostic_report(observation_request_data, patient, encounter=encounter, parent=main_diagnostic_report)

            for practitioner_role in practitioner_roles:
                entry.append({
                    "resource": practitioner_role.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "PractitionerRole/" + practitioner_role.id}
                })

            for observation in observations:
                entry.append({
                    "resource": observation.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Observation/" + observation.id}
                })

            for observation_data in observation_request_data.get("observations", []):
                observation, organizations, practitioner_roles = prepare_observation(observation_data, patient, parent = None, specimen=None, encounter=encounter)
                if diagnostic_report.result:
                    diagnostic_report.result.append(Reference(reference="Observation/" + observation.id))
                else:
                    diagnostic_report.result = [Reference(reference="Observation/" + observation.id)]

                entry.append({
                    "resource": observation.dumps(exclude_unset=True, exclude_none=True),
                    "request": {"method": "PUT", "url": "Observation/" + observation.id}
                })

                for organization in organizations:
                    entry.append({
                        "resource": organization.dumps(exclude_unset=True, exclude_none=True),
                        "request": {"method": "PUT", "url": "Organization/" + organization.id}
                    })

                for practitioner_role in practitioner_roles:
                    entry.append({
                        "resource": practitioner_role.dumps(exclude_unset=True, exclude_none=True),
                        "request": {"method": "PUT", "url": "PractitionerRole/" + practitioner_role.id}
                    })

            entry.append({
                "resource": diagnostic_report.dumps(exclude_unset=True, exclude_none=True),
                "request": {"method": "PUT", "url": "DiagnosticReport/" + diagnostic_report.id}
            })

    try:
        API.bundle(entry=entry, type="transaction")
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())
        raise Exception({"message": 'Failed', 'error': str(e)})
