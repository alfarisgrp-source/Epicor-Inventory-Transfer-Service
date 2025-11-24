import logging

class PreCommitTransferService:
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger("PreCommitTransferService")

    def execute(self, username, password, payload):
        self.logger.info(f"[PreCommitTransfer] Request: {payload}")

        response = self.api.post(
            username,
            password,
            "Erp.BO.InvTransferSvc/PreCommitTransfer",
            payload
        )

        self.logger.info(f"[PreCommitTransfer] Response: {response}")
        return response
