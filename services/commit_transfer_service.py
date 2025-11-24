import logging

class CommitTransferService:
    def __init__(self, api_client):
        self.api = api_client
        self.logger = logging.getLogger("CommitTransferService")

    def execute(self, username, password, payload):
        self.logger.info(f"[CommitTransfer] Request: {payload}")

        response = self.api.post(
            username,
            password,
            "Erp.BO.InvTransferSvc/CommitTransferAndUpdateHistory",
            payload
        )

        self.logger.info(f"[CommitTransfer] Response: {response}")
        return response
