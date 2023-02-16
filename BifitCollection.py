import requests
import logging
from settings import PASS, LOG, BASE_URL, TOKEN, REFRESH
import hashlib
import base64

class BifitCollection:

    nomenclatureId = None
    nomenclatureExternalId = None
    nomenclatureName = None
    nomenclaturePurchasePrice = None
    nomenclatureSellPrice = None
    nomenclatureVatValue = None
    nomenclatureUnitCode = None

    def __init__(self):
        nomenclatureId = None
        nomenclatureExternalId = None
        nomenclatureName = None
        nomenclaturePurchasePrice = 0
        nomenclatureSellPrice = 0
        nomenclatureVatValue = 0
        nomenclatureUnitCode = 796

        logging.basicConfig(
            filename='app.log',
            level=logging.DEBUG
        )


    def hashPassword(self, password):
        a = hashlib.sha256(password.encode('utf8'))
        hash = base64.b64encode(a.digest()).decode()
        return hash

    def getAccessTokenByLogin(self):
        access_token = None
        url = BASE_URL + "/oauth/token"
        data = {
            "username": LOG,
            "password": self.hashPassword(PASS),
            "client_id": "cashdesk-rest-client",
            "client_secret": "cashdesk-rest-client",
            "grant_type": "password"
        }

        headers = {
            "Accept - Encoding": "deflate"
        }

        result = requests.post(url, data=data, headers=headers)
        if result.status_code == 200:
            try:
                data = result.json()
                access_token = data["access_token"]
            except:
                print("Error")

        return access_token

    def getAccessTokenByRefresh(self):
        access_token = None
        url = BASE_URL + "/oauth/token"
        data = {
            "refresh_token": f"{REFRESH}",
            "client_id": "cashdesk-rest-client",
            "client_secret": "cashdesk-rest-client",
            "grant_type": "refresh_token"
        }

        headers = {
            "Accept - Encoding": "deflate"
        }

        result = requests.post(url, data=data, headers=headers)
        if result.status_code == 200:
            try:
                data = result.json()
                access_token = data["access_token"]
            except:
                print("Error")

        return access_token


    def getNomenclature(self, nomenclature_id):
        url = f"{BASE_URL}/protected/nomenclatures/{nomenclature_id}"

        headers = {
            "Accept - Encoding": "deflate",
            "Authorization": f"Bearer {self.getAccessTokenByRefresh()}"
        }

        result = requests.get(url, headers=headers)
        if result.status_code != 200:
            logging.error(f"Nomenclature read: {result.text}")

        result = result.json()


        self.nomenclatureId = result['id']
        self.nomenclatureExternalId = result['externalId']
        self.nomenclatureName = result['name']
        self.nomenclatureVatValue = result['vatValue']
        self.nomenclatureUnitCode = result['unitCode']
        self.nomenclaturePurchasePrice = result['purchasePrice']
        self.nomenclatureSellPrice = result['sellingPrice']

        return self

    def createReceipt(self, json):
        url = f"{BASE_URL}/protected/receipts"

        headers = {
            "Accept-Encoding": "deflate",
            "Authorization": f"Bearer {self.getAccessTokenByRefresh()}"
        }

        result = requests.post(url, headers=headers, json=json)
        if result.status_code != 200:
            print(f"Receipt create: {result.text}")
            logging.error(f"Receipt create: {result.text}")
        else:
            print(f"{result.status_code} {result.text}")
            logging.debug(f"{result.status_code} {result.text}")
        return result.status_code


