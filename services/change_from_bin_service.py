import logging

class ChangeFromBinService:
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger("ChangeFromBinService")

    def execute(self, username, password, payload):
        self.logger.info(f"[ChangeFromBin] Request: {payload}")

        response = self.api.post(
            username,
            password,
            "Erp.BO.InvTransferSvc/ChangeFromBinRowMod",
            payload
        )

        self.logger.info(f"[ChangeFromBin] Response: {response}")
        return response
