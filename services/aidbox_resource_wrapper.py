"""
Created the Separate aidbox resources which is wrapper for already existing resources.
To support the Bearer token authentication for each API request for all the API calls.
"""
from services.aidbox_service import AidboxApi
from aidbox.resource.patient import Patient as PatientR
from aidbox.resource.encounter import Encounter as EncounterR
from aidbox.resource.coverage import Coverage as CoverageR
from aidbox.resource.immunization import Immunization as ImmunizationR
from aidbox.resource.medicationrequest import MedicationRequest as MedicationRequestR
from aidbox.resource.medicationstatement import MedicationStatement as MedicationStatementR
from aidbox.resource.condition import Condition as ConditionR
from aidbox.resource.allergyintolerance import AllergyIntolerance as AllergyIntoleranceR
from aidbox.resource.appointment import Appointment as AppointmentR
from aidbox.resource.observation import Observation as ObservationR



class Patient(AidboxApi, PatientR):
    pass

class Encounter(AidboxApi, EncounterR):
    pass

class Coverage(AidboxApi, CoverageR):
    pass

class Immunization(AidboxApi, ImmunizationR):
    pass

class MedicationRequest(AidboxApi, MedicationRequestR):
    pass

class MedicationStatement(AidboxApi, MedicationStatementR):
    pass

class Condition(AidboxApi, ConditionR):
    pass

class AllergyIntolerance(AidboxApi, AllergyIntoleranceR):
    pass

class Appointment(AidboxApi, AppointmentR):
    pass

class Observation(AidboxApi, ObservationR):
    pass