import logging

class ChangeToBinService:
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger("ChangeToBinService")

    def execute(self, username, password, payload):
        self.logger.info(f"[ChangeToBin] Request: {payload}")

        response = self.api.post(
            username,
            password,
            "Erp.BO.InvTransferSvc/ChangeToBinRowMod",
            payload
        )

        self.logger.info(f"[ChangeToBin] Response: {response}")
        return response
