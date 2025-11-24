import requests, yaml
import logging

class SalesBuzzClient:
    def __init__(self,  config_path="config.yaml"):
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)
        self.BASE_URL = cfg["salesbuzz"]["base_url"]
    # BASE_URL = "https://rpa-api.alfarishost.com/salesBuz"

    def get_inventory_transfers(self):
        """Fetches all pending inventory transfer documents."""
        url = f"{self.BASE_URL}/list/inventory"
        logging.info(f"Fetching inventory transfers -> {url}")

        res = requests.get(url)

        if res.status_code != 200:
            raise Exception(f"Failed to fetch inventory transfers: {res.text}")

        data = res.json()
        logging.info(f"Received {len(data)} transfer entries")
        return data

    def get_mapping(self, salesman_no):
        """Fetches mapping required for transfer based on SalesmanNumber."""
        url = f"{self.BASE_URL}/mapping/get?salesPerson={salesman_no}"

        logging.info(f"Fetching mapping for Salesman {salesman_no}")

        res = requests.get(url)
        if res.status_code != 200:
            logging.error(f"Mapping fetch failed for {salesman_no}: {res.text}")
            return None

        data = res.json()
        return data["mapping"][0] if data["count"] > 0 else None
