import logging

class ValidatePartNumService:
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger("ValidatePartNumService")

    def execute(self, username, password, payload):
        self.logger.info(f"[ValidatePartNum] Request: {payload}")

        response = self.api.post(
            username,
            password,
            "Erp.BO.InvTransferSvc/ValidatePartNum",
            payload
        )

        self.logger.info(f"[ValidatePartNum] Response: {response}")
        return response
