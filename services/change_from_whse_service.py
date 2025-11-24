import logging

class ChangeFromWhseService:
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger("ChangeFromWhseService")

    def execute(self, username, password, payload):
        self.logger.info(f"[ChangeFromWhse] Request: {payload}")

        response = self.api.post(
            username,
            password,
            "Erp.BO.InvTransferSvc/ChangeFromWhseRowMod",
            payload
        )

        self.logger.info(f"[ChangeFromWhse] Response: {response}")
        return response
