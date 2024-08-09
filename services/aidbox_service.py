import requests
from typing import Literal, Any
import os
from aidbox.base import Meta, IncEx

from utils.common_utils import bearer_token

base = os.environ.get("AIDBOX_URL")


class AidboxApi:
    @classmethod
    def from_id(cls, id: str):
        assert bearer_token.get(None) is not None
        token = f"Bearer {bearer_token.get(None)}"
        headers = {'authorization': token}
        response = requests.get(url=f"{base}/fhir/{cls.__name__}/{id}", headers=headers,)
        response.raise_for_status()  # TODO: handle and type HTTP codes except 200+
        return response.json()

    @classmethod
    def bundle(cls, entry: list[Any], type: Literal["transaction"]):
        assert bearer_token.get(None) is not None
        token = f"Bearer {bearer_token.get(None)}"
        headers = {'authorization': token}
        data = {"resourceType": "Bundle", "type": type, "entry": entry}
        response = requests.post(url=f"{base}/fhir", json=data, headers=headers,)
        response.raise_for_status()  # TODO: handle and type HTTP codes except 200+

    @classmethod
    def get(cls, *args: dict[str, Any]):
        assert bearer_token.get(None) is not None
        token = f"Bearer {bearer_token.get(None)}"
        headers = {'authorization': token}
        search_params: dict[str, Any] = {}
        [search_params.update(d) for d in args]
        response = requests.get(
            url=f"{base}/fhir/{cls.__name__}", params=search_params, headers=headers,
        )
        response.raise_for_status()  # TODO: handle and type HTTP codes except 200+
        data = response.json()  # TODO: handle HTTP response bodies
        final_response = {}
        if "entry" in data and data["entry"]:
            final_response["entry"] = data["entry"]
        if "total" in data:
            final_response["total"] = data["total"]
        return final_response

    def delete(self):
        assert bearer_token.get(None) is not None
        token = f"Bearer {bearer_token.get(None)}"
        headers = {'authorization': token}
        assert self.id is not None
        resource_type = self.__class__.__name__
        response = requests.delete(
            url=f"{base}/fhir/{resource_type}/{self.id}", headers=headers,
        )
        response.raise_for_status()  # TODO: handle and type HTTP codes except 200+

    def save(self):  # create | persist | save
        assert bearer_token.get(None) is not None
        token = f"Bearer {bearer_token.get(None)}"
        headers = {'authorization': token}
        resource_type = self.__class__.__name__
        response = requests.put(
            url=f"{base}/fhir/{resource_type}/{self.id or ''}",
            json=self.dumps(exclude_unset=True),
            headers=headers,
        )
        print(f"{response.text}")
        response.raise_for_status()  # TODO: handle and type HTTP codes except 200+
        data = response.json()
        self.id = data["id"]
        self.meta = Meta(**data["meta"])

    def dumps(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ):
        data = self.model_dump(
            mode=mode,
            by_alias=by_alias,
            include=include,
            exclude=exclude,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )

        for item in ["class", "global", "for", "import"]:
            if (item + "_") in data:
                data[item] = data[item + "_"]
                del data[item + "_"]

        return data

    @classmethod
    def make_request(cls, endpoint, method="GET"):
        assert bearer_token.get(None) is not None
        url = f"{base}{endpoint}"
        token = f"Bearer {bearer_token.get(None)}"
        headers = {'authorization': token}
        return requests.request(method, url, headers=headers)

    @staticmethod
    def open_request(endpoint, method="GET", **kwargs):
        url = f"{base}{endpoint}"
        return requests.request(method, url, **kwargs)

