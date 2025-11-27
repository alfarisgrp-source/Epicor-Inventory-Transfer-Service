# services/update_status_service.py

import requests
import logging

class UpdateStatusService:
    def __init__(self):
        self.logger = logging.getLogger("UpdateStatusService")
        self.url = "https://rpa-api.alfarishost.com/salesBuz/inventory/status/update"

    def update_status(self, transfer_no, status):
        """
        Update the status of an inventory transfer record in SalesBuzz.
        """
        try:
            payload = {
                "TransferNo": transfer_no,
                "status": status
            }

            response = requests.post(self.url, json=payload, timeout=15)

            if response.status_code == 200:
                self.logger.info(f"[STATUS UPDATED] {transfer_no} → {status}")
            else:
                self.logger.error(f"[STATUS UPDATE FAILED] {transfer_no} → HTTP {response.status_code}, {response.text}")

        except Exception as e:
            self.logger.exception(f"❌ Error updating status for {transfer_no}: {str(e)}")
