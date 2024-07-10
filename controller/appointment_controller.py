import logging
import traceback
from fastapi import status
from fastapi.responses import JSONResponse

from aidbox.base import CodeableConcept, Reference, Coding, Annotation
from aidbox.resource.appointment import Appointment_Participant

from constants import PATIENT_REFERENCE, INTEND, STATUS, APPOINTMENT_STATUS, PARTICIPANT_STATUS,CURRENT, OTHER
from services.aidbox_resource_wrapper import Appointment
from models.appointment_validation import AppoinmentModel
from controller.patient_controller import PatientClient
from services.aidbox_resource_wrapper import MedicationRequest
from services.aidbox_resource_wrapper import AllergyIntolerance
from services.aidbox_resource_wrapper import MedicationStatement
from services.aidbox_resource_wrapper import Condition
from services.aidbox_service import AidboxApi

logger = logging.getLogger("log")


class AppointmentClient:
    @staticmethod
    def create_appointment(patient_id: str, app: AppoinmentModel):
        try:
            response_data = {}
            appointment = Appointment(
                status=APPOINTMENT_STATUS,
                description=app.other_reason,
                participant=[
                    Appointment_Participant(
                        actor=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                        status=PARTICIPANT_STATUS,
                    )
                ],
                start=app.date_of_appoinment,
                end=app.schedule_time,
                patientInstruction=app.reason_for_test,
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
    def get_all_appointment():
        try:
            appointment = Appointment.get()
            if appointment:
                return appointment
            return JSONResponse(
                content={"Error retrieving appointments"},
                status_code=status.HTTP_404_NOT_FOUND,
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
                "error": "Unable to retrieve datas"
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
    def get_by_patient_name(name: str):
        try:
            responce_name = AidboxApi.make_request(method="GET", endpoint=f"/$query/appointmentByPatientName?patientName={name}")
            data = responce_name.json()
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
                    status_code=status.HTTP_404_NOT_FOUND
                )
            return JSONResponse(
                content=formatted_data,
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
    def get_appointment_by_date(state_date: str , end_date: str):
        try:
            responce_name = AidboxApi.make_request(method="GET", endpoint=f"/$query/appointmentByStartDate?start={state_date}&end={end_date}")
            data = responce_name.json()
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
                    status_code=status.HTTP_404_NOT_FOUND
                )
            return JSONResponse(
                content=formatted_data,
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




