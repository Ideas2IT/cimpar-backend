import os
import requests

from aidbox.base import (
    API,
    Reference
)
from aidbox.resource.location import Location
from aidbox.resource.practitioner import Practitioner

from HL7v2.resources.observation import prepare_observation
from HL7v2.resources.patient import prepare_patient
from HL7v2.resources.encounter import prepare_encounters
from HL7v2.resources.diagnosticreport import prepare_diagnostic_report

CONNECTION_STRING = os.environ.get("CONNECTION_STRING")


def run(message):
    source = message['src'] if 'src' in message else None
    patient_data = message.get("patient_group")
    order_data = message.get("order_group") or message.get("patient_group").get("order_group")
    visit_data = message.get("visit") or message.get("patient_group").get("visit")
    specimens = message.get("specimens")
    
    entry = []
    patient, patient_url = prepare_patient(patient_data["patient"])
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
        
    if specimens:
        for specimen in message.get("specimens", []):
            for observation_data in specimen.get("observations", []):
                observation, organizations, practitioner_roles = prepare_observation(observation_data, patient, parent=None,
                                                                                 specimen=None, encounter=None)
                entry.append({
                        "resource": observation.dumps(exclude_unset=True, exclude_none=True),
                        "request": {"method": "PUT", "url": "Observation/" + observation.id}
                    })

    if order_data:
        order_data = order_data[0] if isinstance(order_data, list) else order_data
        if "order" in order_data:
            main_diagnostic_report, practitioner_roles, observations = prepare_diagnostic_report(order_data["order"],
                                                                                                 patient,
                                                                                                 encounter=None,
                                                                                                 parent=None)

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
            observation, organizations, practitioner_roles = prepare_observation(observation_data, patient, parent=None,
                                                                                 specimen=None, encounter=None)

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
            diagnostic_report, practitioner_roles, observations = prepare_diagnostic_report(observation_request_data,
                                                                                            patient,
                                                                                            encounter=encounter,
                                                                                            parent=main_diagnostic_report)

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
                observation, organizations, practitioner_roles = prepare_observation(observation_data, patient,
                                                                                     parent=None, specimen=None,
                                                                                     encounter=encounter)
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
        return {"patient_url": patient_url, "patient_id": patient.id}
    except requests.exceptions.RequestException as e:
        if e.response is not None:
            print(e.response.json())
        raise Exception({"message": 'Failed', 'error': str(e)})
