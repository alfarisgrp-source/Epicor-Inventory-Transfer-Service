import logging

class ChangeTransferQtyService:
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger("ChangeTransferQtyService")

    def execute(self, username, password, payload):
        self.logger.info(f"[ChangeTransferQty] Request: {payload}")

        response = self.api.post(
            username,
            password,
            "Erp.BO.InvTransferSvc/ChangeTransferQtyRowMod",
            payload
        )

        self.logger.info(f"[ChangeTransferQty] Response: {response}")
        return response
