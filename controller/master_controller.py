from fastapi import status, HTTPException
from fastapi.responses import JSONResponse

from services.aidbox_service import AidboxApi


class MasterClient:
    @staticmethod
    def get_master_data(table_name: str):
        table = {"race": "CimparRace", "state": "CimparState", "lab_test": "CimparLabTest",
                 "ethnicity": "CimparEthnicity"}
        if table_name not in table:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Kindly, verify the name.")
        try:
            master_values = AidboxApi.make_request(
                method="GET",
                endpoint=f"/fhir/{table[table_name]}?_sort=.display"
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
            return  JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=f"Failed to fetch data: {str(e)}")