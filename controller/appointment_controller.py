import logging
import traceback
import json
from fastapi import status
from fastapi.responses import JSONResponse

from aidbox.base import CodeableConcept, Reference, Coding, Annotation
from aidbox.resource.appointment import Appointment_Participant
from aidbox.resource.observation import Observation
from HL7v2 import get_md5
from HL7v2.resources.observation import get_status

from constants import (
    PATIENT_REFERENCE,  
    APPOINTMENT_STATUS, 
    PARTICIPANT_STATUS,
    CURRENT, 
    OTHER, 
    APPOINTMENT_SYSTEM
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

            # Storing the lab result for the appointments.

            observation = Observation(
                id=get_md5(),
                status=get_status("R"),
                valueString="upcoming appointment",
                subject=Reference(reference="Patient/" + (patient_id or "")),
                code=CodeableConcept(coding=[
                            Coding(
                                system=APPOINTMENT_SYSTEM,
                                code=concept.code,
                                display=concept.display,
                            )
                            for concept in app.test_to_take
                        ]),
                effectiveDateTime=app.date_of_appointment

            )
            observation.save()

            appointment = Appointment(
                status=APPOINTMENT_STATUS,
                description=app.other_reason,
                comment=f"Observation/{observation.id}",
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

            if app.current_medical_condition:
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
                response_data["current_condition_id"] = current_condition.id if current_condition else None

            if app.other_medical_condition:
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
                response_data["other_medication_id"] = additional_condition.id if additional_condition else None

            if app.current_allergy:
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
                response_data["current_allergy"] = current_allergy.id if current_allergy else None

            if app.other_allergy:
                other_allergy = AllergyIntolerance(
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
                other_allergy.save()
                response_data["other_allergy"] = other_allergy.id if other_allergy else None
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
    def get_appointment_by_patient_id(patient_id: int, page: int, page_size: int):
        try:
            result = {}
            appointment = Appointment.make_request(
                method="GET",
                endpoint=f"/fhir/Appointment/?.participant.0.actor.id={patient_id}&_page={page}&_count={page_size}",
            )
            appointment_data = appointment.json()
            result["data"] = appointment_data
            result["current_page"] = page
            result["page_size"] = page
            result["total_items"] = appointment_data.get('total', 0)
            result["total_pages"] = (int(appointment_data["total"]) + page_size - 1) // page_size
            if appointment_data.get('total', 0) == 0:
                logger.info(f"No appointment found for patient: {patient_id}")
                return JSONResponse(
                    content=[],
                    status_code=status.HTTP_200_OK
                )
            return result
        except Exception as e:
            logger.error(f"Error retrieving appointment: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve appointment",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
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
            patient_details = AppointmentClient.get_patient_detail(patient_id)
            appointment = Appointment.make_request(
                method="GET",
                endpoint=f"/fhir/Appointment/{appointment_id}?participant=Patient/{patient_id}",
            )
            if appointment.status_code == 200:
                appointment_detail = appointment.json()
                condition_allergy_resource = ConditionClient.get_condition_by_patient_id(patient_id)
                extracted_conditions = AppointmentClient.process_conditions_and_allergies(condition_allergy_resource)
                insurance_detail = AppointmentClient.get_insurance_detail(patient_id)
                participant_reference = appointment_detail.get("participant", [{}])[0].get("actor", {}).get("reference", "")
                patient_id_extracted = participant_reference.split('/')[1] if participant_reference else ""
                service_type_display = appointment_detail.get("serviceType", [{}])[0].get("coding", [{}])[0].get("display", "")
                patient_result = {
                    "appointmentId": appointment_detail.get("id"),
                    "patientId": patient_id_extracted,
                    "name": (patient_details.get('firstName', '') + " " + patient_details.get('lastName', '')).strip(),
                    "dob": patient_details.get('dob'),
                    "gender": patient_details.get("gender"),
                    "appointmentFor": service_type_display,
                    'start': appointment_detail.get("start"),
                    'end': appointment_detail.get("end"),
                    "condition": extracted_conditions,
                    "insurance" : insurance_detail
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
                "error": "Unable to retrieve appointments",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data, 
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_appointment_by_date(state_date: str, end_date: str, page: int, page_size: int):
        try:
            limit = page_size
            offset = (page - 1) * page_size
            response_name = AidboxApi.make_request(
                method="GET",
                endpoint=f"/$query/appointmentByStartDate?start={state_date}&end={end_date}&limit={limit}&offset={offset}"
            )
            data = response_name.json()
            count_res = AidboxApi.make_request(
                method="GET",
                endpoint=f"/$query/appointmentByStartDateCount?start={state_date}&end={end_date}"
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
    def get_appointment(patient_name: str, state_date: str, end_date: str, service_name: str, page: int, page_size: int):
        if patient_name:
            return AppointmentClient.get_by_patient_name(patient_name, page, page_size)
        elif state_date or end_date:
            state_date = state_date if state_date else "1999-01-01"
            end_date = end_date if end_date else "2999-12-01"
            return AppointmentClient.get_appointment_by_date(state_date, end_date, page, page_size)
        elif service_name:
            return AppointmentClient.custom_query_with_pagination(
                    "filteredAppointmentServiceType", service_name, page, page_size
                )
        else:
            return AppointmentClient.get_appointment_detail(page, page_size)

         
    @staticmethod
    def get_appointment_detail(page, page_size):
        results = [] 
        appointment = AppointmentClient.get_all_appointment(page, page_size)
        data = json.loads(appointment.body)
        appointment_value = AppointmentClient.get_patient_id_and_service_type_from_appointment(data)   
        if appointment_value:
            for patient in appointment_value:
                patient_id = patient.get("patient_id")
                patient_details = AppointmentClient.get_patient_detail(patient_id)
                patient_result = {
                    "appointmentId": patient.get("appointment_id"),
                    "patientId": patient_details.get("id"),
                    "name": (patient_details.get('firstName', '') + " " + patient_details.get('lastName', '')).strip(),
                    "dob": patient_details.get('dob'),
                    "gender": patient_details.get("gender"),
                    "appointmentFor": patient.get("service_type"),
                    'start': patient.get("start"),
                    'end': patient.get("end"),
                }
                results.append(patient_result)
                coverage_response = AppointmentClient.get_insurance_detail(patient_id)
                patient_result["insurance"] = coverage_response.get("insurance")
                results.append(patient_result)
                final_result = {
                    "data": results,
                    "pagination": data.get('pagination')
                }
        return JSONResponse(
            content=final_result,
            status_code=status.HTTP_200_OK
        )

    @staticmethod
    def formated_data(formatted_data: list):
        appointment_values = AppointmentClient.get_appointment_data(formatted_data)
        results = [] 
        for appointment in appointment_values:  
            for item in formatted_data: 
                for participant in item["resource"]["participant"]:
                    patient_id = participant["actor"]["id"]
        patient_details = AppointmentClient.get_patient_detail(patient_id)
        insurance_detail = AppointmentClient.get_insurance_detail(patient_id)
        result = {
            "patientId": patient_details.get("id"),
            "name": (patient_details.get('firstName', '') + " " + patient_details.get('lastName', '')).strip(),
            "dob": patient_details.get('dob'),
            "gender": patient_details.get("gender"),
            "insurance": insurance_detail.get("insurance"),
            "appointmentId": appointment.get("appointment_id"),
            "appointmentFor": appointment.get("service_type"),
            'start': appointment.get("start"),
            'end': appointment.get("end")
        }
        results.append(result) 
        return results 


    @staticmethod
    def get_insurance_detail(patient_id: str):
        patient_result = {}
        total_coverage = 0
        coverage_response = CoverageClient.get_coverage_by_patient_id(patient_id)
        coverages = []
        if isinstance(coverage_response, dict) and 'coverage' in coverage_response:
            total_coverage = coverage_response.get('coverage', {}).get('total', 0)
            coverage_entries = coverage_response.get('coverage', {}).get('entry', [])
            for entry in coverage_entries:
                resource = entry.get('resource', {})
                class_info = resource.get('class', [{}])[0]
                beneficiary_reference = resource.get('beneficiary', {}).get('reference', "")
                patient_id_from_response = beneficiary_reference.split("/")[-1] if beneficiary_reference else ""
                coverage_info = {
                    "id": resource.get('id', ''),
                    "patient_id": patient_id_from_response,
                    "providerName": resource.get('payor', [{}])[0].get('display', ''),
                    "policyNumber": resource.get('subscriberId', ''),
                    "groupNumber": class_info.get('name', ''),
                    "note": class_info.get('value', '')
                }
                coverages.append(coverage_info)
        elif isinstance(coverage_response, list) and len(coverage_response) > 0:
            total_coverage = coverage_response[0].get('coverage', {}).get('total', 0) 
        patient_result["insurance"] = "No" if total_coverage == 0 else "Yes"
        patient_result["coverage_details"] = coverages
        return patient_result
    

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
                        'service_type': combined_service_type, 
                        'appointment_id': appointment_id,
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
    def custom_query_with_pagination(query_name: str, search: str, page: int, page_size: int):
        limit = page_size
        offset = (page - 1) * page_size
        response_name = AidboxApi.make_request(
            method="GET",
            endpoint=f"/$query/{query_name}?display={search}&limit={limit}&offset={offset}"
        )
        data = response_name.json()
        count_res = AidboxApi.make_request(
            method="GET",
            endpoint=f"/$query/{query_name}Count?display={search}"
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
    

