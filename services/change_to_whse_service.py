import logging

class ChangeToWhseService:
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger("ChangeToWhseService")

    def execute(self, username, password, payload):
        self.logger.info(f"[ChangeToWhse] Request: {payload}")

        response = self.api.post(
            username,
            password,
            "Erp.BO.InvTransferSvc/ChangeToWhseRowMod",
            payload
        )

        self.logger.info(f"[ChangeToWhse] Response: {response}")
        return response
