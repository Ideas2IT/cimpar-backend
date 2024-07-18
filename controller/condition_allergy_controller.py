import logging
import traceback
from typing import Dict, Any

from fastapi import status
from fastapi.responses import JSONResponse

from aidbox.resource.condition import Condition
from aidbox.resource.allergyintolerance import AllergyIntolerance
from aidbox.base import CodeableConcept, Reference, Coding, Annotation

from services.aidbox_service import AidboxApi
from constants import (
    PATIENT_REFERENCE,
    STATUS_SYSTEM,
    CURRENT,
    FAMILY,
    OTHER
)
from services.aidbox_resource_wrapper import Condition
from services.aidbox_resource_wrapper import AllergyIntolerance
from models.condition_validation import ConditionModel, ConditionUpdateModel

logger = logging.getLogger("log")


class ConditionClient:
    @staticmethod
    def create_condition_allergy(con: ConditionModel, patient_id: str):
        try:
            result = {}
            response_condition = Condition.make_request(
                method="GET", endpoint=f"/fhir/Condition/?subject=Patient/{patient_id}"
            )
            response_allergy = AllergyIntolerance.make_request(
                method="GET",
                endpoint=f"/fhir/AllergyIntolerance/?patient=Patient/{patient_id}",
            )
            data: dict[str, bool | Any] = ConditionClient.get_condition(response_condition.json())
            allergy_response = ConditionClient.get_allergy(response_allergy.json())
            if allergy_response.get("is_current_allergy_exist"):
                result['is_current_allergy_exist'] = True
            if allergy_response.get("is_other_allergy_exist"):
                result["is_other_allergy_exist"] = True
            if data.get('is_current_condition_exist'):
                result['is_current_condition_exist'] = True
            if data.get('is_other_condition_exist'):
                result['is_other_condition_exist'] = True
            if data.get('is_family_condition_exist'):
                result['is_family_condition_exist'] = True

            if con.current_condition and data.get('is_current_condition_exist') == False:
                current_condition = Condition(
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.current_condition
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=CURRENT)],
                )
                current_condition.save()
                result["current_condition_id"] = current_condition.id

            if con.additional_condition and data.get('is_other_condition_exist') == False:
                additional_condition = Condition(
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.additional_condition
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=OTHER)],
                )
                additional_condition.save()
                result["other_condition_id"] = additional_condition.id


            if con.current_allergy and allergy_response.get("is_current_allergy_exist") == False:
                current_allergy = AllergyIntolerance(
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.current_allergy
                        ]
                    ),
                    patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=CURRENT)],
                )
                current_allergy.save()
                result["current_allergy_id"] = current_allergy.id


            if con.additional_allergy and allergy_response.get("is_other_allergy_exist") == False:
                additional_allergy = AllergyIntolerance(
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.additional_allergy
                        ]
                    ),
                    patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=OTHER)],
                )
                additional_allergy.save()
                result["other_allergy_id"] = additional_allergy.id

            if con.family_condition and data.get('is_family_condition_exist') == False:
                family_status = "active" if con.family_condition == True else "unknown"
                family_condition = Condition(
                    clinicalStatus=CodeableConcept(
                        coding=[Coding(system=STATUS_SYSTEM, code=family_status)]
                    ),
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.family_medical_condition
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=FAMILY)],
                )
                family_condition.save()
                result["family_condition_id"] = family_condition.id

            result["condition_allergy"] = "Created"
            logger.info(f"Added Successfully in DB: {result}")
            return result
        except Exception as e:
            logger.error(f"Error creating condition: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create Allergy and condition",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_condition_by_patient_id(patient_id: str):
        try:
            response_condition = Condition.make_request(
                method="GET", endpoint=f"/fhir/Condition/?subject=Patient/{patient_id}"
            )
            response_allergy = AllergyIntolerance.make_request(
                method="GET",
                endpoint=f"/fhir/AllergyIntolerance/?patient=Patient/{patient_id}",
            )
            if response_condition.json().get('total', 0) == 0 and response_allergy.json().get('total', 0) == 0:
                logger.info(f"No condition and allergy found for patient: {patient_id}")
                return JSONResponse(
                    content=[],
                    status_code=status.HTTP_200_OK
                )
            return [response_condition.json(), response_allergy.json()]

        except Exception as e:
            logger.error(f"Error getting condition: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Allergy and Condition",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def update_by_patient_id(patient_id: str, con: ConditionUpdateModel):
        try:
            result = {}
            response_condition = Condition.make_request(
                method="GET", endpoint=f"/fhir/Condition/?subject=Patient/{patient_id}"
            )
            response_allergy = AllergyIntolerance.make_request(
                method="GET",
                endpoint=f"/fhir/AllergyIntolerance/?patient=Patient/{patient_id}",
            )
            data: dict[str, bool | Any] = ConditionClient.get_condition(response_condition.json())
            allergy_response = ConditionClient.get_allergy(response_allergy.json())
            if allergy_response.get("is_current_allergy_exist"):
                result['is_current_allergy_exist'] = True
            if allergy_response.get("is_other_allergy_exist"):
                result["is_other_allergy_exist"] = True
            if data.get('is_current_condition_exist'):
                result['is_current_condition_exist'] = True
            if data.get('is_other_condition_exist'):
                result['is_other_condition_exist'] = True
            if data.get('is_family_condition_exist'):
                result['is_family_condition_exist'] = True
            if not con.family_condition:
                if data.get('is_family_resource'):
                    family_data = Condition(**data.get('is_family_resource'))
                    family_data.delete()
                    result["family_condition"] = "deleted"
            if not con.current_condition:
                if data.get('is_current_resource'):
                    current_data = Condition(**data.get('is_current_resource'))
                    current_data.delete()
                    result["current_condition"] = "deleted"
            if not con.additional_condition:
                if data.get('is_other_resource'):
                    other_data = Condition(**data.get('is_other_resource'))
                    other_data.delete()
                    result["other_condition"] = "deleted"
            if not con.current_allergy:
                if allergy_response.get("is_current_resource"):
                    current_allergy_data = AllergyIntolerance(**allergy_response.get("is_current_resource"))
                    current_allergy_data.delete()
                    result["current_allergy"] = "deleted"
            if not con.additional_allergy:
                if allergy_response.get("is_other_resource"):
                    other_allergy_data = AllergyIntolerance(**allergy_response.get("is_other_resource"))
                    other_allergy_data.delete()
                    result["other_allergy"] = "deleted"

            if con.current_condition and con.current_allergy_id:
                current_condition = Condition(
                    id=con.current_condition_id,
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.current_condition
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=CURRENT)],
                )
                current_condition.save()
                result["current_condition_id"] = current_condition.id
            else:
                if con.current_condition and data.get('is_current_condition_exist') == False:
                    current_condition = Condition(
                        code=CodeableConcept(
                            coding=[
                                Coding(
                                    system=concept.system,
                                    code=concept.code,
                                    display=concept.display,
                                )
                                for concept in con.current_condition
                            ]
                        ),
                        subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        note=[Annotation(text=CURRENT)],
                    )
                    current_condition.save()
                    result["current_condition_id"] = current_condition.id
                    result["current_condition"] = "Created"

            if con.additional_condition and con.additional_condition_id:
                additional_condition = Condition(
                    id=con.additional_condition_id,
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.additional_condition
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=OTHER)],
                )
                additional_condition.save()
                result["other_condition_id"] = additional_condition.id
            else:
                if con.additional_condition and data.get('is_other_condition_exist') == False:
                    additional_condition = Condition(
                        code=CodeableConcept(
                            coding=[
                                Coding(
                                    system=concept.system,
                                    code=concept.code,
                                    display=concept.display,
                                )
                                for concept in con.additional_condition
                            ]
                        ),
                        subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        note=[Annotation(text=OTHER)],
                    )
                    additional_condition.save()
                    result["other_condition_id"] = additional_condition.id
                    result["other_condition"] = "Created"

            if con.current_allergy and con.current_allergy_id:
                current_allergy = AllergyIntolerance(
                    id=con.current_allergy_id,
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.current_allergy
                        ]
                    ),
                    patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=CURRENT)],
                )
                current_allergy.save()
                result["current_allergy"] = current_allergy.id
            else:
                if con.current_allergy and allergy_response.get("is_current_allergy_exist") == False:
                    current_allergy = AllergyIntolerance(
                        code=CodeableConcept(
                            coding=[
                                Coding(
                                    system=concept.system,
                                    code=concept.code,
                                    display=concept.display,
                                )
                                for concept in con.current_allergy
                            ]
                        ),
                        patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        note=[Annotation(text=CURRENT)],
                    )
                    current_allergy.save()
                    result["current_allergy_id"] = current_allergy.id
                    result["current_allergy"] = "Created"

            if con.additional_allergy and con.additional_allergy_id:
                additional_allergy = AllergyIntolerance(
                    id=con.additional_allergy_id,
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.additional_allergy
                        ]
                    ),
                    patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=OTHER)],
                )
                additional_allergy.save()
                result["other_allergy"] = additional_allergy.id
            else:
                if con.additional_allergy and allergy_response.get("is_other_allergy_exist") == False:
                    additional_allergy = AllergyIntolerance(
                        code=CodeableConcept(
                            coding=[
                                Coding(
                                    system=concept.system,
                                    code=concept.code,
                                    display=concept.display,
                                )
                                for concept in con.additional_allergy
                            ]
                        ),
                        patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        note=[Annotation(text=OTHER)],
                    )
                    additional_allergy.save()
                    result["other_allergy_id"] = additional_allergy.id
                    result["other_allergy"] = "Created"

            if con.family_condition and con.family_condition_id:
                family_status = "active" if con.family_condition == True else "unknown"
                family_condition = Condition(
                    id=con.family_condition_id,
                    clinicalStatus=CodeableConcept(
                        coding=[Coding(system=STATUS_SYSTEM, code=family_status)]
                    ),
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in con.family_medical_condition
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=FAMILY)],
                )
                family_condition.save()
                result["family_condition"] = family_condition.id
            else:
                if con.family_condition and data.get('is_family_condition_exist') == False:
                    family_status = "active" if con.family_condition == True else "unknown"
                    family_condition = Condition(
                        clinicalStatus=CodeableConcept(
                            coding=[Coding(system=STATUS_SYSTEM, code=family_status)]
                        ),
                        code=CodeableConcept(
                            coding=[
                                Coding(
                                    system=concept.system,
                                    code=concept.code,
                                    display=concept.display,
                                )
                                for concept in con.family_medical_condition
                            ]
                        ),
                        subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        note=[Annotation(text=FAMILY)],
                    )
                    family_condition.save()
                    result["family_condition_id"] = family_condition.id
                    result["family_condition"] = "Created"

            logger.info(f"Added Successfully in DB: {result}")
            return result
        except Exception as e:
            logger.error(f"Error creating condition: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to update allergy and condition",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_allergy_list(allergy_name: str):
        allergy_info_list = []
        try:
            allergy_list = AidboxApi.make_request(
                method="GET",
                endpoint=f"/Concept?.definition$contains={allergy_name}&system=http://hl7.org/fhir/sid/icd-10",
            )
            logger.info(f"Allergy List: {allergy_list}")
            data = allergy_list.json()
            entries = data.get('entry', [])

            for entry in entries:
                resource = entry.get('resource', {})
                system = resource.get('system', '')
                code = resource.get('code', '')
                definition = resource.get('definition', '')
                if definition:
                    allergy_info = {"system": system, "code": code, "display": definition}
                    allergy_info_list.append(allergy_info)
            if not allergy_list:
                return JSONResponse(status_code=status.HTTP_200_OK, content=[])
            return JSONResponse(status_code=status.HTTP_200_OK, content=allergy_info_list)
        except Exception as e:
            logger.error(f"Unable to get allergy list: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "No allergy found for allergy",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_condition(Condition_data):
        result = {
            "is_current_condition_exist": False,
            "is_other_condition_exist": False,
            "is_family_condition_exist": False
        }

        if Condition_data.get("total", 0) > 0:
            for entry in Condition_data.get("entry", []):
                resource_id = entry["resource"].get("id", "")
                resource = entry["resource"]
                notes = entry["resource"].get("note", [])
                if notes:
                    note_text = notes[0].get("text", "")
                    if note_text == "Current":
                        result["is_current_condition_exist"] = True
                        result['current_id'] = resource_id
                        result['is_current_resource'] = resource
                    elif note_text == "Other":
                        result["is_other_condition_exist"] = True
                        result['other_id'] = resource_id
                        result['is_other_resource'] = resource
                    elif note_text == "Family":
                        result["is_family_condition_exist"] = True
                        result['family_id'] = resource_id
                        result['is_family_resource'] = resource
        return result

    @staticmethod
    def get_allergy(allergy_data):
        result = {
            "is_current_allergy_exist": False,
            "is_other_allergy_exist": False,
        }
        if allergy_data.get("total", 0) > 0:
            for entry in allergy_data.get("entry", []):
                resource = entry["resource"]
                notes = entry["resource"].get("note", [])
                if notes:
                    note_text = notes[0].get("text", "")
                    if note_text == "Current":
                        result["is_current_allergy_exist"] = True
                        result['is_current_resource'] = resource
                    elif note_text == "Other":
                        result["is_other_allergy_exist"] = True
                        result['is_other_resource'] = resource
        return result
