import json

import requests
from decouple import config
from werkzeug.exceptions import InternalServerError


class WiseService:
    def __init__(self):
        self.token = config("WISE_API_KEY")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        self.base_url = config("WISE_URL")
        self.profile_id = self.get_profile_id()

    def get_profile_id(self):
        url = self.base_url + "/v1/profiles"
        response = requests.get(url, headers=self.headers)
        if response.status_code in (200, 201):
            return [el["id"] for el in response.json() if el["type"] == "personal"][0]
        # logger.exceptions("")
        raise InternalServerError("Payment provider is not available at the moment")

    def create_quote(self, amount):
        url = self.base_url + "/v2/quotes"
        data = {
            "sourceCurrency": "EUR",
            "targetCurrency": "EUR",
            "sourceAmount": amount,
            "targetAmount": None,
            "profile": self.profile_id,
        }
        response = requests.post(url, data=json.dumps(data), headers=self.headers)
        if response.status_code in (200, 201):
            return response.json()["id"]
        raise InternalServerError("Payment provider is not available at the moment")

    def create_recipient(self, full_name, iban):
        url = self.base_url + "/v1/accounts"
        data = {
            "currency": "EUR",
            "type": "iban",
            "profile": self.profile_id,
            "accountHolderName": full_name,
            "legalType": "PRIVATE",
            "details": {"iban": iban},
        }
        response = requests.post(url, data=json.dumps(data), headers=self.headers)
        if response.status_code in (200, 201):
            return response.json()["id"]
        raise InternalServerError("Payment provider is not available at the moment")

    def create_transfer(self, recipient_id, quote_id, custom_id):
        url = self.base_url + "/v1/transfers"
        data = {
            "targetAccount": recipient_id,
            "quoteUuid": quote_id,
            "customerTransactionId": custom_id,
            "details": {},
        }
        response = requests.post(url, data=json.dumps(data), headers=self.headers)
        if response.status_code in (200, 201):
            return response.json()["id"]
        raise InternalServerError("Payment provider is not available at the moment")

    def fund_transfer(self, transfer_id):
        # url = self.base_url + "/v3/profiles/" + self.profile_id + "/transfers/" + transfer_id + "/payments"
        url = f"{self.base_url}/v3/profiles/{self.profile_id}/transfers/{transfer_id}/payments"
        data = {"type": "BALANCE"}
        response = requests.post(url, data=json.dumps(data), headers=self.headers)
        if response.status_code in (200, 201):
            return response.json()["status"]
        raise InternalServerError("Payment provider is not available at the moment")


# if __name__ == "__main__":
#
#     status = wise.fund_transfer(transfer_id)
#     print(status)
