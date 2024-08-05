from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from aidbox.base import API

from services.aidbox_service import AidboxApi
import logging

logger = logging.getLogger("log")


class MasterClient:

    table = {"race": "CimparRace", "state": "CimparState", "lab_test": "CimparLabTest",
             "ethnicity": "CimparEthnicity", "company": "CimparInsuranceCompany"}

    @staticmethod
    def get_master_data(table_name: str):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            master_values = AidboxApi.make_request(
                method="GET",
                endpoint=f"/fhir/{MasterClient.table[table_name]}?_sort=.display"
            )
            values = master_values.json()
            master_value = []
            for entry in values["entry"]:
                master_value.append(
                    {
                        "id": entry.get("resource", {}).get("id"),
                        "code": entry.get("resource", {}).get("code"),
                        "display": entry.get("resource", {}).get("display")
                    }
                )
            return master_value
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=f"Failed to fetch data: {str(e)}")

    @staticmethod
    def fetch_master_using_code(table_name: str, code: str):
        if table_name not in MasterClient.table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            master_values = API.make_request(
                method="GET",
                endpoint=f"/fhir/{MasterClient.table[table_name]}?.code={code}"
            )
            values = master_values.json()
            master_value = {}
            if values and values["entry"]:
                master_value.update(
                    {
                        "id": values["entry"][0].get("resource", {}).get("id"),
                        "code": values["entry"][0].get("resource", {}).get("code"),
                        "display": values["entry"][0].get("resource", {}).get("display")
                    }
                )
            return master_value
        except Exception as e:
            logger.error(f"Unable to fetch the code: {e}")
            return {}

