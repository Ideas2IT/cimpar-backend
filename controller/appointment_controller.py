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
    INTEND, 
    STATUS, 
    APPOINTMENT_STATUS, 
    PARTICIPANT_STATUS,
    CURRENT, 
    OTHER, 
    APPOINTMENT_SYSTEM
)
from services.aidbox_resource_wrapper import Appointment
from models.appointment_validation import AppoinmentModel
from controller.patient_controller import PatientClient
from services.aidbox_resource_wrapper import MedicationRequest
from services.aidbox_resource_wrapper import AllergyIntolerance
from services.aidbox_resource_wrapper import MedicationStatement
from services.aidbox_resource_wrapper import Condition
from utils.common_utils import paginate
from services.aidbox_service import AidboxApi
from controller.lab_result_controller import ObservationClient
from controller.insurance_controller import CoverageClient

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
                response_data["current_medication_id"] = current_condition.id if current_condition else None


            if app.other_medical_condition:
                medication_request = MedicationRequest(
                    medicationCodeableConcept=CodeableConcept(
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
                    status=STATUS,
                    intent=INTEND,
                    note=[Annotation(text=OTHER)],
                )
                medication_request.save()
                response_data["other_medication_id"] = medication_request.id if medication_request else None


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
        appointment_id: str,
        current_medication_id: str,
        other_medication_id: str,
        allergy_id: str,
    ):
        try:
            patient = PatientClient.get_patient_by_id(patient_id)
            appointment = Appointment.make_request(
                method="GET",
                endpoint=f"/fhir/Appointment/{appointment_id}?participant=Patient/{patient_id}",
            )
            current_medication = MedicationStatement.make_request(
                method="GET",
                endpoint=f"/fhir/MedicationStatement/{current_medication_id}?subject=Patient/{patient_id}",
            )
            other_medication = MedicationRequest.make_request(
                method="GET",
                endpoint=f"/fhir/MedicationRequest/{other_medication_id}?subject=Patient/{patient_id}",
            )
            current_allergy = AllergyIntolerance.make_request(
                method="GET",
                endpoint=f"/fhir/AllergyIntolerance/{allergy_id}/?patient=Patient/{patient_id}",
            )
            if (
                appointment.status_code == 404
                and current_medication.status_code == 404
                and other_medication.status_code == 404
                and current_allergy.status_code == 404
                and current_allergy.status_code == 404
            ):
                logger.info("No Record Found")
                error_response_data = {
                "error": "Unable to retrieve data"
                }
                return JSONResponse(
                    content=error_response_data,
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            return {
                "patient": patient,
                "appointment": appointment.json() if appointment.status_code == 200 else None,
                "current_medication": current_medication.json() if current_medication.status_code == 200 else None,
                "other_medication": other_medication.json() if other_medication.status_code == 200 else None,
                "current_allergy": current_allergy.json() if current_allergy.status_code == 200 else None,
            }
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
            final_response = {
                "data": formatted_data,
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
            final_response = {
                "data": formatted_data,
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
    def get_appointment(patient_name: str, state_date:str, end_date: str, all_appointment: bool, lab_test: str, page: int, page_size: int):
        if patient_name:
            return AppointmentClient.get_by_patient_name(patient_name, page, page_size)
        elif lab_test:
            return ObservationClient.get_lab_result_by_name(lab_test, page, page_size)
        elif state_date and end_date:
            return AppointmentClient.get_appointment_by_date(state_date, end_date, page, page_size)
        else:
            return AppointmentClient.get_appointment_detail(page, page_size)
         

    @staticmethod
    def get_appointment_detail(page, page_size):
        results = [] 
        total_coverage = 0
        appointment = AppointmentClient.get_all_appointment(page, page_size)
        appointment_value = AppointmentClient.get_patient_id_and_service_type_from_appointment(json.loads(appointment.body))        
        if appointment_value:
            for patient in appointment_value:
                patient_id = patient.get("patient_id")
                patient_details = PatientClient.get_patient_by_id(patient_id)
                patient_result = {
                    "appointmentId": patient.get("appointment_id"),
                    "patientId": patient_details.get("id"),
                    "name": (patient_details.get('firstName', '') + " " + patient_details.get('lastName', '')).strip(),
                    "dob": patient_details.get('dob'),
                    "gender": patient_details.get("gender"),
                    "appointmentFor": patient.get("service_type"),
                    'start': patient.get("start"),
                    'end': patient.get("end") 
                }
                coverage_response = CoverageClient.get_coverage_by_patient_id(patient_id)
                total_coverage = 0
                if coverage_response:
                    if isinstance(coverage_response, dict) and 'coverage' in coverage_response:
                        total_coverage = coverage_response.get('coverage', {}).get('total', 0)
                    elif isinstance(coverage_response, list) and len(coverage_response) > 0:
                        total_coverage = coverage_response[0].get('coverage', {}).get('total', 0)
                patient_result["insurance"] = "No" if total_coverage == 0 else "Yes"
                results.append(patient_result)
        return JSONResponse(
            content=results,
            status_code=status.HTTP_200_OK
        )
                

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

