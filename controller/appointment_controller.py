import logging
import traceback
import json
from fastapi import status
from typing import Any
from fastapi.responses import JSONResponse

from aidbox.base import CodeableConcept, Reference, Coding, Annotation
from aidbox.resource.appointment import Appointment_Participant
from models.appointment_validation import StatusModel
from HL7v2 import get_md5
from HL7v2.resources.observation import get_status

from constants import (
    PATIENT_REFERENCE,  
    APPOINTMENT_STATUS, 
    PARTICIPANT_STATUS,
    CURRENT, 
    OTHER, 
    APPOINTMENT_SYSTEM,
    UPCOMING_APPOINTMENT,
    START_DATE,
    END_DATE
)
from services.aidbox_resource_wrapper import Appointment
from models.appointment_validation import AppoinmentModel
from controller.patient_controller import PatientClient
from services.aidbox_resource_wrapper import AllergyIntolerance
from services.aidbox_resource_wrapper import Condition
from utils.common_utils import paginate
from services.aidbox_service import AidboxApi
from controller.insurance_controller import CoverageClient
from controller.condition_allergy_controller import ConditionClient

logger = logging.getLogger("log")


class AppointmentClient:
    @staticmethod
    def create_appointment(patient_id: str, app: AppoinmentModel):
        try:
            response_data = {}
            response_condition = Condition.make_request(
                method="GET", endpoint=f"/fhir/Condition/?subject=Patient/{patient_id}"
            )
            response_allergy = AllergyIntolerance.make_request(
                method="GET",
                endpoint=f"/fhir/AllergyIntolerance/?patient=Patient/{patient_id}",
            )
            condition_response: dict[str, bool | Any] = ConditionClient.get_condition(response_condition.json())
            allergy_response = ConditionClient.get_allergy(response_allergy.json())
            if allergy_response.get("is_current_allergy_exist"):
                response_data['is_current_allergy_exist'] = True
            if allergy_response.get("is_other_allergy_exist"):
                response_data["is_other_allergy_exist"] = True
            if condition_response.get('is_current_condition_exist'):
                response_data['is_current_condition_exist'] = True
            if condition_response.get('is_other_condition_exist'):
                response_data['is_other_condition_exist'] = True
            if not app.current_medical_condition:
                if condition_response.get('is_current_resource'):
                    current_data = Condition(**condition_response.get('is_current_resource'))
                    current_data.delete()
                    response_data["current_condition"] = "deleted"
            if not app.other_medical_condition:
                if condition_response.get('is_other_resource'):
                    other_data = Condition(**condition_response.get('is_other_resource'))
                    other_data.delete()
                    response_data["other_condition"] = "deleted"
            if not app.current_allergy:
                if allergy_response.get("is_current_resource"):
                    current_allergy_data = AllergyIntolerance(**allergy_response.get("is_current_resource"))
                    current_allergy_data.delete()
                    response_data["current_allergy"] = "deleted"
            if not app.other_allergy:
                if allergy_response.get("is_other_resource"):
                    other_allergy_data = AllergyIntolerance(**allergy_response.get("is_other_resource"))
                    other_allergy_data.delete()
                    response_data["other_allergy"] = "deleted"

            appointment = Appointment(
                status=APPOINTMENT_STATUS,
                description=app.other_reason,
                comment=UPCOMING_APPOINTMENT,
                participant=[
                    Appointment_Participant(
                        actor=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        status=PARTICIPANT_STATUS,
                    )
                ],
                start=app.date_of_appointment,
                end=app.schedule_time,
                patientInstruction=app.reason_for_test,
                serviceType=[CodeableConcept(
                        coding=[
                            Coding(
                                system=APPOINTMENT_SYSTEM,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in app.test_to_take
                        ]
                    ),]
            )
            appointment.save()
            response_data["appointment_id"] = appointment.id if appointment else None

            if app.current_medical_condition and app.current_condition_id:
                current_condition = Condition(
                    id=app.current_condition_id,
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in app.current_medical_condition
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=CURRENT)],
                )
                current_condition.save()
                response_data["current_condition_id"] = current_condition.id
            else:
                if app.current_medical_condition and condition_response.get('is_current_condition_exist') == False:
                    current_condition = Condition(
                        code=CodeableConcept(
                            coding=[
                                Coding(
                                    system=concept.system,
                                    code=concept.code,
                                    display=concept.display,
                                )
                                for concept in app.current_medical_condition
                            ]
                        ),
                        subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        note=[Annotation(text=CURRENT)],
                    )
                    current_condition.save()
                    response_data["current_condition_id"] = current_condition.id
                    response_data["current_condition"] = "Created"

            if app.other_medical_condition and app.other_condition_id:
                additional_condition = Condition(
                    id=app.other_condition_id,
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in app.other_medical_condition
                        ]
                    ),
                    subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=OTHER)],
                )
                additional_condition.save()
                response_data["other_condition_id"] = additional_condition.id
            else:
                if app.other_medical_condition and condition_response.get('is_other_condition_exist') == False:
                    additional_condition = Condition(
                        code=CodeableConcept(
                            coding=[
                                Coding(
                                    system=concept.system,
                                    code=concept.code,
                                    display=concept.display,
                                )
                                for concept in app.other_medical_condition
                            ]
                        ),
                        subject=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        note=[Annotation(text=OTHER)],
                    )
                    additional_condition.save()
                    response_data["other_condition_id"] = additional_condition.id
                    response_data["other_condition"] = "Created"

            if app.current_allergy and app.current_allergy_id:
                current_allergy = AllergyIntolerance(
                    id=app.current_allergy_id,
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in app.current_allergy
                        ]
                    ),
                    patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=CURRENT)],
                )
                current_allergy.save()
                response_data["current_allergy"] = current_allergy.id
            else:
                if app.current_allergy and allergy_response.get("is_current_allergy_exist") == False:
                    current_allergy = AllergyIntolerance(
                        code=CodeableConcept(
                            coding=[
                                Coding(
                                    system=concept.system,
                                    code=concept.code,
                                    display=concept.display,
                                )
                                for concept in app.current_allergy
                            ]
                        ),
                        patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        note=[Annotation(text=CURRENT)],
                    )
                    current_allergy.save()
                    response_data["current_allergy_id"] = current_allergy.id
                    response_data["current_allergy"] = "Created"

            if app.other_allergy and app.other_allergy_id:
                additional_allergy = AllergyIntolerance(
                    id=app.other_allergy_id,
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system=concept.system,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in app.other_allergy
                        ]
                    ),
                    patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    note=[Annotation(text=OTHER)],
                )
                additional_allergy.save()
                response_data["other_allergy"] = additional_allergy.id
            else:
                if app.other_allergy and allergy_response.get("is_other_allergy_exist") == False:
                    additional_allergy = AllergyIntolerance(
                        code=CodeableConcept(
                            coding=[
                                Coding(
                                    system=concept.system,
                                    code=concept.code,
                                    display=concept.display,
                                )
                                for concept in app.other_allergy
                            ]
                        ),
                        patient=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        note=[Annotation(text=OTHER)],
                    )
                    additional_allergy.save()
                    response_data["other_allergy_id"] = additional_allergy.id
                    response_data["other_allergy"] = "Created"
            response_data["created"] = True
            logger.info(f"Added Successfully in DB: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Error creating Appointment {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create Appointment",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_appointment_by_patient_id(patient_id: str, search: str):
        try:
            appointment = Appointment.make_request(
                method="GET",
                endpoint=f"/fhir/Appointment/?.participant.0.actor.id={patient_id}&.comment={search}"
                         f"&_sort=-lastUpdated",
            )
            appointment_data = appointment.json()
            if appointment_data.get('total', 0) == 0:
                return []
            result = appointment_data["entry"]
            for each_result in result:
                if "resource" in each_result and each_result["resource"]:
                    each_result["resource"]["record_type"] = "appointment"
            return result
        except Exception as e:
            logger.error(f"Error retrieving appointment: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve appointment",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_all_appointment(page, page_size):
        try:
            appointment = paginate(Appointment, page, page_size)
            if appointment.get('total_items', 1) == 0:
                return JSONResponse(
                    content=[],
                    status_code=status.HTTP_200_OK
                )
            return JSONResponse(
                content=appointment,
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error retrieving encounters: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve appointments",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            ) 

    @staticmethod
    def get_by_id(
        patient_id: str,
        appointment_id: str
    ):
        try:
            result = []
            try:
                patient_details = AppointmentClient.get_patient_detail(patient_id)
                patient_id = patient_details["id"]
            except Exception as e:
                logger.error(f"Unable to fetch the patient details: {e}")
                patient_details = {}
            appointment = Appointment.make_request(
                method="GET",
                endpoint=f"/fhir/Appointment/{appointment_id}?participant=Patient/{patient_id}",
            )
            if appointment.status_code == 200:
                appointment_detail = appointment.json()
                condition_allergy_resource = ConditionClient.get_condition_by_patient_id(patient_id)
                extracted_conditions = AppointmentClient.process_conditions_and_allergies(condition_allergy_resource)
                insurance_detail = CoverageClient.get_insurance_detail(patient_id)
                participant_reference = appointment_detail.get("participant", [{}])[0].get("actor", {}).get("reference", "")
                patient_id_extracted = participant_reference.split('/')[1] if participant_reference else ""
                service_type_coding = appointment_detail.get("serviceType", [{}])[0].get("coding", [{}])
                service_type_display = ', '.join([coding['display'] for coding in service_type_coding if 'display' in coding])
                patient_result = {
                    "appointmentId": appointment_detail.get("id"),
                    "reason_for_test": appointment_detail.get("patientInstruction"),
                    "patientId": patient_id_extracted,
                    "name": (patient_details.get('firstName', '') + " " + patient_details.get('lastName', '')).strip(),
                    "dob": patient_details.get('dob'),
                    "gender": patient_details.get("gender"),
                    "email": patient_details.get("email"),
                    "phoneNo": patient_details.get("phoneNo"),
                    "alternativeNumber": patient_details.get("alternativeNumber"),
                    "appointmentFor": service_type_display,
                    'start': appointment_detail.get("start"),
                    'end': appointment_detail.get("end"),
                    "condition": extracted_conditions,
                    "insurance": insurance_detail
                }
                result.append(patient_result)
                final_response = {
                    "data": result
                }
                return JSONResponse(
                    content=final_response,
                    status_code=status.HTTP_200_OK,
                )
            
        except Exception as e:
            logger.error(f"Error retrieving appointments: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve appointments",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data, status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_by_patient_name(name: str, page: int, page_size: int):
        try:
            limit = page_size
            offset = (page - 1) * page_size
            response_name = AidboxApi.make_request(
                method="GET",
                endpoint=f"/$query/appointmentByPatientName?patientName={name}&limit={limit}&offset={offset}"
            )
            data = response_name.json()
            count_res = AidboxApi.make_request(
                method="GET",
                endpoint=f"/$query/appointmentByPatientNameCount?patientName={name}"
            )
            count_resp = count_res.json()
            total_count = count_resp["data"][0]["count"]
            formatted_data = [
                {
                    "resource": {
                        "id": item["id"],  
                        **item["resource"] 
                    }
                } for item in data.get('data', [])
            ]
            if not data.get('data', []):
                return JSONResponse(
                    content=[],
                    status_code=status.HTTP_200_OK
                )
            values = AppointmentClient.formated_data(formatted_data)
            final_response = {
                "data": values,
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_items": total_count,
                    "total_pages": (total_count // page_size) + (1 if total_count % page_size != 0 else 0)
                }
            }
            return JSONResponse(
                content=final_response,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            error_response_data = {
                "error": "Unable to retrieve appointments",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data, 
                status_code=status.HTTP_400_BAD_REQUEST
            )


    @staticmethod
    def get_appointment_by_date(start_date: str, end_date: str, page: int, page_size: int):
        try:
            limit = page_size
            offset = (page - 1) * page_size
            response_name = AidboxApi.make_request(
                method="GET",
                endpoint=f"/$query/appointmentByStartDate?start={start_date}&end={end_date}&limit={limit}&offset={offset}"
            )
            data = response_name.json()
            count_res = AidboxApi.make_request(
                method="GET",
                endpoint=f"/$query/appointmentByStartDateCount?start={start_date}&end={end_date}"
            )
            count_resp = count_res.json()
            total_count = count_resp["data"][0]["count"]
            formatted_data = [
                {
                    "resource": {
                        "id": item["id"],  
                        **item["resource"] 
                    }
                } for item in data.get('data', [])
            ]
            values = AppointmentClient.formated_data(formatted_data)
            final_response = {
                "data": values,
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_items": total_count,
                    "total_pages": (total_count // page_size) + (1 if total_count % page_size != 0 else 0)
                }
            }
            if not data.get('data', []):
                return JSONResponse(
                    content=[],
                    status_code=status.HTTP_200_OK
                )
            return JSONResponse(
                content=final_response,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            error_response_data = {
                "error": "Unable to retrieve appointments between dates",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data, 
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_appointment(patient_name: str = "", start_date: str = "", end_date: str = "",
                        service_name: str = "", page: int = 1, page_size: int = 100):
        # if patient_name:
        #     return AppointmentClient.get_by_patient_name(patient_name, page, page_size)
        # elif start_date or end_date:
        #     start_date = start_date if start_date else START_DATE
        #     end_date = end_date if end_date else END_DATE
        #     return AppointmentClient.get_appointment_by_date(start_date, end_date, page, page_size)
        # elif service_name:
        #     return AppointmentClient.custom_query_with_pagination(
        #             "filteredAppointmentServiceType", service_name, page, page_size
        #         )
        # else:
        #     return AppointmentClient.get_appointment_detail(page, page_size)
        start_date = start_date if start_date else START_DATE
        end_date = end_date if end_date else END_DATE
        return AppointmentClient.custom_query_with_pagination(
            "filteredAppointments", patient_name, start_date, end_date, service_name, page, page_size
            )

    @staticmethod
    def get_appointment_detail(page, page_size):
        results = []
        appointment = AppointmentClient.get_all_appointment(page, page_size)
        data = json.loads(appointment.body)
        appointment_value = AppointmentClient.get_patient_id_and_service_type_from_appointment(data)
        if appointment_value:
            unique_patient_ids = set(patient.get("patient_id") for patient in appointment_value)
            patient_details_map = {}
            insurance_details_map = {}
            for patient_id in unique_patient_ids:
                try:
                    patient_details = AppointmentClient.get_patient_detail(patient_id)
                    patient_details_map[patient_id] = patient_details
                    patient_id = patient_details["id"]
                except Exception as e:
                    logger.error(f"Unable to fetch the patient details for patient_id {patient_id}: {e}")
                    patient_details_map[patient_id] = {}

                try:
                    coverage_response = CoverageClient.get_insurance_detail(patient_id)
                    insurance_details_map[patient_id] = coverage_response
                except Exception as e:
                    logger.error(f"Unable to fetch the insurance details for patient_id {patient_id}: {e}")
                    insurance_details_map[patient_id] = {}
            for patient in appointment_value:
                patient_id = patient.get("patient_id")
                patient_details = patient_details_map.get(patient_id, {})
                coverage_response = insurance_details_map.get(patient_id, {})
                patient_result = {
                    "appointmentId": patient.get("appointment_id"),
                    "patientId": patient_id,
                    "name": (patient_details.get('firstName', '') + " " + patient_details.get('lastName', '')).strip(),
                    "dob": patient_details.get('dob'),
                    "gender": patient_details.get("gender"),
                    "appointmentFor": patient.get("service_type"),
                    'start': patient.get("start"),
                    'end': patient.get("end"),
                }
                results.append(patient_result)
            final_result = {
                "data": results,
                "pagination": data.get('pagination')
            }
        else:
            final_result = {
                "data": [],
                "pagination": {}
            }

        return JSONResponse(
            content=final_result,
            status_code=status.HTTP_200_OK
        )

    @staticmethod
    def formated_data(formatted_data: list):
        appointment_values = AppointmentClient.get_appointment_data(formatted_data)
        results = [] 
        unique_patient_ids = set(each_appointment["patient_id"] for each_appointment in appointment_values)
        patient_details_map = {}
        insurance_details_map = {}
        for patient_id in unique_patient_ids:
            try:
                patient_details = AppointmentClient.get_patient_detail(patient_id)
                patient_details_map[patient_id] = patient_details
                patient_id = patient_details["id"]
            except Exception as e:
                logger.error(f"Unable to fetch the patient details for patient_id {patient_id}: {e}")
                patient_details_map[patient_id] = {}
            try:
                insurance_detail = CoverageClient.get_insurance_detail(patient_id)
                insurance_details_map[patient_id] = insurance_detail
            except Exception as e:
                logger.error(f"Unable to fetch the Insurance details for patient_id {patient_id}: {e}")
                insurance_details_map[patient_id] = {}
        patient_id_extract = []
        results = []
        for each_appointment in appointment_values:
            patient_id = each_appointment["patient_id"]
            patient_id_extract.append(patient_id)
            patient_details = patient_details_map.get(patient_id, {})
            insurance_detail = insurance_details_map.get(patient_id, {})
            result = {
                "patientId": patient_details.get("id"),
                "name": (patient_details.get('firstName', '') + " " + patient_details.get('lastName', '')).strip(),
                "dob": patient_details.get('dob'),
                "gender": patient_details.get("gender"),
                "insurance": insurance_detail.get("insurance"),
                "appointmentId": each_appointment.get("appointment_id"),
                "appointmentFor": each_appointment.get("service_type"),
                'start': each_appointment.get("start"),
                'end': each_appointment.get("end")
            }
            results.append(result)

        return results

    @staticmethod
    def get_patient_detail(patient_id):
        patient = PatientClient.get_patient_by_id(patient_id)
        return patient

    @staticmethod
    def get_patient_id_and_service_type_from_appointment(appointment_value):
        patient_service_types = []
        for entry in appointment_value['data']:
            appointment_id = entry['resource'].get('id', '')
            start_time = entry['resource'].get('start', '')
            end_time = entry['resource'].get('end', '')
            reason_for_test = entry['resource'].get('patientInstruction', '')
            for participant in entry['resource']['participant']:
                if participant['actor'].get('reference', ''):
                    patient_id = participant['actor']['reference'].split('/')[-1]
                    service_types = entry['resource'].get('serviceType', [])
                    service_type_displays = []  
                    for service_type in service_types:
                        for coding in service_type.get('coding', []):
                            service_type_display = coding.get('display', '')
                            service_type_displays.append(service_type_display)  
                    combined_service_type = ', '.join(service_type_displays)
                    patient_service_types.append({
                        'patient_id': patient_id,
                        'appointment_id': appointment_id,
                        'service_type': combined_service_type, 
                        'reason_for_test' : reason_for_test,
                        'start': start_time,
                        'end': end_time
                    })
        return patient_service_types

    @staticmethod
    def get_appointment_data(appointment_value):
        patient_service = []
        for entry in appointment_value:
            appointment_id = entry['resource'].get('id', '')
            start_time = entry['resource'].get('start', '')
            end_time = entry['resource'].get('end', '')
            for participant in entry['resource']['participant']:
                if participant['actor'].get('id', ''):
                    patient_id = participant['actor']['id'].split('/')[-1]
                    service_types = entry['resource'].get('serviceType', [])
                    service_type_displays = []
                    for service_type in service_types:
                        for coding in service_type.get('coding', []):
                            service_type_display = coding.get('display', '')
                            service_type_displays.append(service_type_display)
                    combined_service_type = ', '.join(service_type_displays)
                    patient_service_details = {
                        'patient_id': patient_id,
                        'service_type': combined_service_type,
                        'appointment_id': appointment_id,
                        'start': start_time,
                        'end': end_time
                    }
                    patient_service.append(patient_service_details)
        return patient_service

    @staticmethod
    def process_conditions_and_allergies(data):
        result = {
            "allergies": [],
            "conditions": []
        }

        def process_entries(entries, resource_type):
            for entry in entries:
                resource = entry.get("resource", {})
                notes = resource.get("note", [])
                code_display = [coding.get("display") for coding in resource.get("code", {}).get("coding", [])]
                resource_id = resource.get("id")

                patient_reference = resource.get("patient", {}).get("reference", "") or resource.get("subject", {}).get("reference", "")
                patient_id = patient_reference.split("/")[-1] if patient_reference else ""
                
                for note in notes:
                    note_text = note.get("text", "")
                    if resource_type == "AllergyIntolerance":
                        result["allergies"].append({
                            "note": note_text,
                            "code_display": code_display,
                            "resource_id": resource_id,
                            "patient_id": patient_id
                        })
                    elif resource_type == "Condition":
                        result["conditions"].append({
                            "note": note_text,
                            "code_display": code_display,
                            "resource_id": resource_id,
                            "patient_id": patient_id
                        })

        for bundle in data:
            if bundle.get("resourceType") == "Bundle":
                for entry in bundle.get("entry", []):
                    resource_type = entry.get("resource", {}).get("resourceType")
                    process_entries([entry], resource_type)
        
        return result

    @staticmethod
    def custom_query_with_pagination(query_name: str, patient_name, start_date, end_date, service_name, page, page_size):
        limit = page_size
        offset = (page - 1) * page_size
        response_name = AidboxApi.make_request(
            method="GET",
            endpoint=f"/$query/{query_name}?patientName={patient_name}&start_date={start_date}&end_date={end_date}"
                     f"&service_name={service_name}&limit={limit}&offset={offset}"
        )
        data = response_name.json()
        count_res = AidboxApi.make_request(
            method="GET",
            endpoint=f"/$query/{query_name}Count?patientName={patient_name}&start_date={start_date}&end_date={end_date}"
                     f"&service_name={service_name}"
        )
        count_resp = count_res.json()
        total_count = count_resp["data"][0]["count"]
        formatted_data = [
            {
                "resource": {
                    "id": item["id"],
                    "record_type": item["record_type"],
                    **item["resource"]
                }
            } for item in data.get('data', [])
        ]
        values = AppointmentClient.formated_data(formatted_data)
        final_response = {
            "data": values,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_items": total_count,
                "total_pages": (total_count // page_size) + (1 if total_count % page_size != 0 else 0)
            }
        }
        if not data.get('data', []):
            final_response = []
        return final_response

    @staticmethod
    def update_appointment_status(appointment_id: str, update_status: StatusModel):
        try:
            appointment_result = Appointment.make_request(method="GET", endpoint=f"/fhir/Appointment/{appointment_id}")
            appointment_json = appointment_result.json()
            if appointment_result.status_code == 404:
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            data = Appointment(**appointment_json)
            data.comment = update_status.status
            data.save()
            response_data = {"id": data.id, "status": data.comment}
            logger.info(f"Updated Successfully in DB: {response_data}")
            return response_data
        except Exception as e:
            logger.error(f"Error retrieving Lab Result: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Lab Result",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

