from fastapi import status
import logging
import traceback
from fastapi.responses import JSONResponse

from aidbox.base import Reference, CodeableConcept, Coding
from aidbox.resource.coverage import Coverage_Class

from constants import GROUP_SYSTEM, GROUP_CODE, PATIENT_REFERENCE, PRIMARY_STATUS, SECONDARY_STATUS, ACTIVE, \
    TERITORY_STATUS, INSURANCE_CONTAINER, DELETED
from services.aidbox_resource_wrapper import Coverage 
from models.insurance_validation import CoverageModel
from models.patient_validation import PatientModel 
from aidbox.resource.coverage import Coverage as CoverageWrapper

from utils.common_utils import azure_file_handler

logger = logging.getLogger("log")


class CoverageClient:
    @staticmethod
    def create_coverage(coverage: PatientModel, patient_id: str, from_patient=False):
        try:
            result = {}
            primary_insurance = CoverageWrapper if from_patient else Coverage
            secondary_insurance = CoverageWrapper if from_patient else Coverage
            if from_patient:
                response_coverage = CoverageWrapper.make_request(method="GET", endpoint=f"/fhir/Coverage/?beneficiary=Patient/{patient_id}")
                existing_coverages = response_coverage.json() if response_coverage else {}
                insurance_id = CoverageClient.get_insurance_ids(existing_coverages)
                for id, insurance_id in insurance_id.items():
                    if insurance_id is not None:
                        CoverageClient.delete_by_insurance_id(insurance_id, patient_id, from_patient)
                    logger.info(f"Coverage Not Found: {patient_id}")
                if coverage.haveInsurance:
                    primary_insurance_plan = CoverageClient.create_primary_insurance(primary_insurance, coverage, patient_id)
                    primary_insurance_plan.save()
                    result["is_primary_insurance"] = primary_insurance_plan.id
                if coverage.haveSecondaryInsurance:
                    secondary_insurance_plan = CoverageClient.create_secondary_insurance(secondary_insurance, coverage, patient_id)
                    secondary_insurance_plan.save()
                    result["is_secondary_insurance"] = secondary_insurance_plan.id
                    result["created"] = True
            return result
        except Exception as e:
            logger.error(f"Unable to create a insurance_plan: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create Insurance",
                "details": str(e),
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def create_coverage_insurance(ins_plan: CoverageModel, patient_id: str, upload_file, file_extension: str = None):
        try:
            result = {'file_url': None}
            response_coverage = Coverage.make_request(method="GET",
                                                      endpoint=f"/fhir/Coverage/?beneficiary=Patient/{patient_id}")
            existing_coverages = response_coverage.json() if response_coverage else {}

            patient_id_occurrences = sum(1 for entry in existing_coverages.get('entry', []) if
                                         entry['resource']['beneficiary']['reference'] == f"Patient/{patient_id}")

            if patient_id_occurrences >= 3:
                logger.error(f"A patient can only have 3 insurance")
                return JSONResponse(
                    content="A patient can only have 3 insurance", status_code=status.HTTP_400_BAD_REQUEST
                )
            if existing_coverages:
                primary_coverage_result = CoverageClient.get_primary_coverage(existing_coverages, patient_id)
                secondary_coverage_result = CoverageClient.get_secondary_coverage(existing_coverages, patient_id)
                tertiary_coverage_result = CoverageClient.get_tertiary_coverage(existing_coverages, patient_id)
                if primary_coverage_result.get('is_primary_insurance_exist') is True:
                    result["is_primary_coverage_exist"] = True
                if primary_coverage_result.get(
                        'is_primary_insurance_exist') is False and ins_plan.insurance_type == "primary":
                    primary_insurance_plan = CoverageClient.create_insurance_plan(patient_id, ins_plan)
                    primary_insurance_plan.save()
                    result["is_primary_insurance"] = primary_insurance_plan.id
                if secondary_coverage_result.get('is_secondary_insurance_exist') is True:
                    result["is_secondary_coverage_exist"] = True
                if secondary_coverage_result.get(
                        'is_secondary_insurance_exist') is False and ins_plan.insurance_type == "secondary":
                    secondary_insurance_plan = CoverageClient.create_insurance_plan(patient_id, ins_plan)
                    secondary_insurance_plan.save()
                    result["is_secondary_insurance"] = secondary_insurance_plan.id
                if tertiary_coverage_result.get("is_tertiary_insurance_exist") is True:
                    result["is_tertiary_insurance_exist"] = True
                if tertiary_coverage_result.get(
                        'is_tertiary_insurance_exist') is False and ins_plan.insurance_type == "tertiary":
                    tertiary_insurance_plan = CoverageClient.create_insurance_plan(patient_id, ins_plan)
                    tertiary_insurance_plan.save()
                    result["is_tertiary_insurance"] = tertiary_insurance_plan.id
            result["created"] = True
            if upload_file and (result.get("is_primary_insurance") or result.get("is_secondary_insurance") or
                                result.get("is_tertiary_insurance")):
                file_path_name = f'{patient_id}/{result.get("is_primary_insurance") or result.get("is_secondary_insurance") or result.get("is_tertiary_insurance")}{file_extension}'
                logger.info(f'Inserting blob data for path: {file_path_name}')
                blob_url = azure_file_handler(container_name=INSURANCE_CONTAINER,
                                              blob_name=file_path_name,
                                              blob_data=upload_file)
                result['file_url'] = blob_url
            logger.info(f"Added Successfully in DB: {result}")
            return result
        except Exception as e:
            logger.error(f"Unable to create a insurance_plan: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to create Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_coverage_by_patient_id(patient_id: str):
        try:
            response_coverage = Coverage.make_request(
                method="GET",
                endpoint=f"/fhir/Coverage/?beneficiary=Patient/{patient_id}&_sort=-lastUpdated"
            )
            coverage = response_coverage.json() 
            
            if coverage.get('total', 0) == 0:
                logger.info(f"No Coverage found for patient: {patient_id}")
                return {}
            for insurance in coverage['entry']:
                logger.info(f"identifying blob data for URL: {patient_id}/{insurance['resource']['id']}")
                file_url = azure_file_handler(container_name=INSURANCE_CONTAINER,
                                              blob_name=f"{patient_id}/{insurance['resource']['id']}",
                                              fetch=True)
                insurance['resource']['file_url'] = file_url
            return {"coverage": coverage}
        except Exception as e:
            logger.error(f"Unable to get coverage data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def get_coverage_by_id(patient_id: str, insurance_id: str):
        try:
            response_coverage = Coverage.make_request(method="GET", endpoint=f"/fhir/Coverage/{insurance_id}?beneficiary=Patient/{patient_id}")
            coverage = response_coverage.json()

            if response_coverage.status_code == 404:
                logger.info(f"Coverage Not Found: {patient_id}")
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )
            coverage['file_url'] = None
            if 'id' in coverage and coverage['id'] != DELETED:
                logger.info(f"identifying blob data for URL: {patient_id}/{insurance_id}")
                file_url = azure_file_handler(container_name=INSURANCE_CONTAINER,
                                              blob_name=f"{patient_id}/{insurance_id}",
                                              fetch=True)
                if not file_url:
                    return JSONResponse(
                        content={"error": "No matching file data found"},
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                coverage['file_url'] = file_url
            return {"coverage": coverage}
        except Exception as e:
            logger.error(f"Unable to get coverage data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to retrieve Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
    @staticmethod
    def update_by_insurance_id(patient_id: str, updated_coverage: CoverageModel, insurance_id: str, upload_file,
                               file_extension: str = None):
        try:
            result = {'file_url': ''}
            if patient_id and insurance_id:
                response_coverage = Coverage.make_request(method="GET", endpoint=f"/fhir/Coverage/{insurance_id}?beneficiary=Patient/{patient_id}")
                coverage = response_coverage.json() 
                patient_id_occurrences = sum(1 for entry in coverage.get('entry', []) if entry['resource']['beneficiary']['reference'] == f"Patient/{patient_id}")
                if patient_id_occurrences >= 3:
                    logger.error(f"A patient can only have 3 insurance")
                    return JSONResponse(
                        content="A patient can only have 3 insurance", status_code=status.HTTP_200_OK
                    )
                if response_coverage.status_code == 404:
                    logger.info(f"Coverage Not Found: {patient_id}")
                    return JSONResponse(
                        content={"error": "No Matching Record"},
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                insurance_plan_update = CoverageClient.update_insurance_plan(insurance_id, patient_id, updated_coverage) 
                insurance_plan_update.save()
                result["insurance_id"] = insurance_plan_update.id
                blob_insurance_id = result['insurance_id']
                result["Updated"] = True
            else:
                response_coverage = Coverage.make_request(method="GET", endpoint=f"/fhir/Coverage/?beneficiary=Patient/{patient_id}")
                coverages = response_coverage.json()
                patient_id_occurrences = sum(1 for entry in coverages.get('entry', []) if entry['resource']['beneficiary']['reference'] == f"Patient/{patient_id}")
                if patient_id_occurrences >= 3:
                    logger.error(f"A patient can only have 3 insurance")
                    return JSONResponse(
                        content="A patient can only have 3 insurance", status_code=status.HTTP_400_BAD_REQUEST
                    )
                if response_coverage.status_code == 404:
                    logger.info(f"Coverage Not Found: {patient_id}")
                    return JSONResponse(
                        content={"error": "No Matching Record"},
                        status_code=status.HTTP_404_NOT_FOUND
                    )
                primary_coverage_result, secondary_coverage_result, tertiary_coverage_result = {}, {}, {}
                if coverages:
                    primary_coverage_result = CoverageClient.get_primary_coverage(coverages, patient_id)
                    secondary_coverage_result = CoverageClient.get_secondary_coverage(coverages, patient_id)
                    tertiary_coverage_result = CoverageClient.get_tertiary_coverage(coverages, patient_id)
                if primary_coverage_result.get('is_primary_insurance_exist') is True:
                    result["is_primary_coverage_exist"] = True
                if primary_coverage_result.get('is_primary_insurance_exist') is False and updated_coverage.insurance_type== "primary":
                    primary_insurance_plan = CoverageClient.create_insurance_plan(patient_id, updated_coverage)
                    primary_insurance_plan.save()
                    result["primary_insurance_id"] = primary_insurance_plan.id
                if secondary_coverage_result.get('is_secondary_insurance_exist') is True:
                    result["is_secondary_coverage_exist"] = True
                if secondary_coverage_result.get('is_secondary_insurance_exist') is False and updated_coverage.insurance_type== "secondary":
                    secondary_insurance_plan = CoverageClient.create_insurance_plan(patient_id, updated_coverage)
                    secondary_insurance_plan.save()
                    result["secondary_insurance_id"] = secondary_insurance_plan.id
                if tertiary_coverage_result.get("is_tertiary_insurance_exist") is True:
                    result["is_tertiary_insurance_exist"] = True
                if tertiary_coverage_result.get('is_tertiary_insurance_exist') is False and updated_coverage.insurance_type== "tertiary":
                    tertiary_insurance_plan = CoverageClient.create_insurance_plan(patient_id, updated_coverage)
                    tertiary_insurance_plan.save()
                    result["tertiary_insurance_id"] = tertiary_insurance_plan.id
                result["created"] = True                 
                logger.info(f"Added Updated in DB: {result}")
                blob_insurance_id = result.get("primary_insurance_id") or result.get(
                    "secondary_insurance_id") or result.get("tertiary_insurance_id")
            if upload_file and blob_insurance_id:
                logger.info(f"Cresting/Updating blob data for URL: {patient_id}/{blob_insurance_id}")
                file_path_name = f'{patient_id}/{blob_insurance_id}{file_extension}'
                upload_url = azure_file_handler(container_name=INSURANCE_CONTAINER,
                                                blob_name=file_path_name,
                                                blob_data=upload_file)
                result['file_url'] = upload_url
            return JSONResponse(
                content=result,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Unable to update coverage data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to update Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def delete_by_insurance_id(insurance_id: str, patient_id: str, from_patient=False):
        try:
            insurance = CoverageWrapper if from_patient else Coverage
            response_coverage = insurance.make_request(method="GET", endpoint=f"/fhir/Coverage/{insurance_id}?beneficiary=Patient/{patient_id}")
            existing_coverage = response_coverage.json() if response_coverage else {}
            if response_coverage.status_code == 404:
                logger.info(f"Coverage Not Found: {patient_id}")
                return JSONResponse(
                    content={"error": "No Matching Record"},
                    status_code=status.HTTP_404_NOT_FOUND
                )

            if existing_coverage.get("id") == insurance_id and existing_coverage.get("beneficiary", {}).get("reference") == f"Patient/{patient_id}":
                delete_data = insurance(**existing_coverage)
                delete_data.delete()
                azure_file_handler(container_name=INSURANCE_CONTAINER,
                                   blob_name=f"{patient_id}/{insurance_id}",
                                   delete=True)
                return {"deleted": True, "patient_id": patient_id}
            error_response_data = { 
                "error": "No insurance matches for this patient"
            }
            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unable to delete coverage data: {str(e)}")
            logger.error(traceback.format_exc())
            error_response_data = {
                "error": "Unable to delete Insurance",
                "details": str(e),
            }

            return JSONResponse(
                content=error_response_data,
                status_code=status.HTTP_400_BAD_REQUEST
            )

    @staticmethod
    def get_primary_coverage(existing_coverages, patient_id):
        result = {}
        for entry in existing_coverages.get("entry", []):
            resource = entry["resource"]
            beneficiary_id = resource["beneficiary"]["reference"].split("/")[-1]
            if beneficiary_id == patient_id:
                for coverage_class in resource.get("class", []):
                    if coverage_class.get("value") == "Primary":
                        result["is_primary_insurance_exist"] = True
                        return result
        result["is_primary_insurance_exist"] = False
        return result

    @staticmethod
    def get_secondary_coverage(existing_coverages, patient_id):
        result = {}
        for entry in existing_coverages.get("entry", []):
            resource = entry["resource"]
            beneficiary_id = resource["beneficiary"]["reference"].split("/")[-1]
            if beneficiary_id == patient_id:
                for coverage_class in resource.get("class", []):
                    if coverage_class.get("value") == "Secondary":
                        result["is_secondary_insurance_exist"] = True
                        return result
        result["is_secondary_insurance_exist"] = False
        return result

    @staticmethod
    def get_tertiary_coverage(existing_coverages, patient_id):
        result = {}
        for entry in existing_coverages.get("entry", []):
            resource = entry["resource"]
            beneficiary_id = resource["beneficiary"]["reference"].split("/")[-1]
            if beneficiary_id == patient_id:
                for coverage_class in resource.get("class", []):
                    if coverage_class.get("value") == "Tertiary":
                        result["is_tertiary_insurance_exist"] = True
                        return result
        result["is_tertiary_insurance_exist"] = False
        return result

    @staticmethod
    def create_primary_insurance(primary_insurance, coverage: PatientModel, patient_id: str):
        insurance_status = "active" if coverage.haveInsurance else "draft"
        dependent_value = "Yes" if coverage.haveInsurance else "No"
        primary_dob = "active" if coverage.primaryMemberDob == 0 else ""
        return primary_insurance(
                status=insurance_status,
                beneficiary=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                subscriberId=coverage.insuranceDetails.policyNumber,
                payor=[Reference(display=coverage.insuranceDetails.providerName)],
                class_=[
                    Coverage_Class(
                        type=CodeableConcept(coding=[Coding(system=GROUP_SYSTEM, code=GROUP_CODE)]),
                        value=PRIMARY_STATUS, 
                        name=coverage.insuranceDetails.groupNumber
                )],
                dependent=dependent_value,
                relationship=CodeableConcept(
                        coding=[
                                Coding(
                                    system=GROUP_SYSTEM, 
                                    code=GROUP_CODE, 
                                    display=coverage.primaryMemberName
                                )
                            ],
                        text=primary_dob
                    ),
                )
    
    @staticmethod
    def create_secondary_insurance(secondary_insurance, coverage: PatientModel, patient_id: str):
        secondary_status = "active" if coverage.secondaryInsuranceDetails else "draft"
        secondary_value = "Yes" if coverage.haveSecondaryInsurance else "No"
        return secondary_insurance(
                    status=secondary_status,
                    beneficiary=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
                    subscriberId=coverage.secondaryInsuranceDetails.policyNumber,
                    payor=[Reference(display=coverage.secondaryInsuranceDetails.providerName)],
                    class_=[
                        Coverage_Class(
                            type=CodeableConcept(coding=[Coding(system=GROUP_SYSTEM, code=GROUP_CODE)]),
                            value=SECONDARY_STATUS,
                            name=coverage.secondaryInsuranceDetails.groupNumber 
                    )],
                    dependent=secondary_value
                )
        
    @staticmethod
    def update_insurance_plan(insurance_id, patient_id, updated_coverage: CoverageModel):
        return Coverage(
            id=insurance_id,
            status=ACTIVE,
            beneficiary=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
            subscriberId=updated_coverage.policyNumber,
            payor=[Reference(display=updated_coverage.providerName)],
            class_=[
                Coverage_Class(
                    type=CodeableConcept(coding=[Coding(system=GROUP_SYSTEM, code=GROUP_CODE)]),
                    value=updated_coverage.insurance_type,
                    name=updated_coverage.groupNumber
                )
            ]
        )
    
    @staticmethod
    def create_insurance_plan(patient_id, updated_coverage: CoverageModel):
        result = PRIMARY_STATUS if updated_coverage.insurance_type == "primary" else SECONDARY_STATUS \
            if updated_coverage.insurance_type == "secondary" else TERITORY_STATUS \
            if updated_coverage.insurance_type == "tertiary" else None
        return Coverage(
            status=ACTIVE,
            beneficiary=Reference(reference=f"{PATIENT_REFERENCE}/{patient_id}"),
            subscriberId=updated_coverage.policyNumber,
            payor=[Reference(display=updated_coverage.providerName)],
            class_=[
                Coverage_Class(
                    type=CodeableConcept(coding=[Coding(system=GROUP_SYSTEM, code=GROUP_CODE)]),
                    value=result,
                    name=updated_coverage.groupNumber
                )
            ]
        )

    @staticmethod
    def get_insurance_detail(patient_id: str):
        patient_result = {}
        total_coverage = 0
        coverage_response = CoverageClient.get_coverage_by_patient_id(patient_id)
        coverages = []
        if 'coverage' in coverage_response:
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
        elif len(coverage_response) > 0:
            total_coverage = coverage_response[0].get('coverage', {}).get('total', 0)
        patient_result["insurance"] = "No" if total_coverage == 0 else "Yes"
        patient_result["coverage_details"] = coverages
        return patient_result
    
    @staticmethod
    def get_insurance_ids(response_json):
        insurance_ids = {
            "primary_id": None,
            "secondary_id": None,
            "tertiary_id": None
        }
        if response_json.get('total', 0) == 0:
            logger.info(f"No Coverage found for patient")
            return {}
        for entry in response_json.get("entry", []):
            resource = entry.get("resource", {})
            coverage_class = resource.get("class", [])
            
            for cls in coverage_class:
                class_value = cls.get("value", "").lower()
                if class_value == "primary":
                    insurance_ids["primary_id"] = resource.get("id")
                elif class_value == "secondary":
                    insurance_ids["secondary_id"] = resource.get("id")
        return insurance_ids
