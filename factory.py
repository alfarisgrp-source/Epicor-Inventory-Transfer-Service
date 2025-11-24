from services.token_service import TokenService
from services.api_client_service import ApiClientService
from modules.inventory_transfer import InventoryTransfer

class ServiceFactory:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self._token_service = None
        self._api_client = None
        self._inventory_transfer = None

    def token_service(self):
        if not self._token_service:
            self._token_service = TokenService(config_path=self.config_path)
        return self._token_service

    def api_client(self):
        if not self._api_client:
            self._api_client = ApiClientService(
                token_service=self.token_service(),
                config_path=self.config_path
            )
        return self._api_client

    def inventory_transfer(self):
        if not self._inventory_transfer:
            self._inventory_transfer = InventoryTransfer(self.api_client())
        return self._inventory_transfer
