import yaml, logging
from utils.http_client import create_session

class ApiClientService:
    def __init__(self, token_service, config_path="config.yaml"):
        self.session = create_session()
        self.token_service = token_service
        self._load_config(config_path)
        self.logger = logging.getLogger("ApiClientService")

    def _load_config(self, path):
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        self.base_url = cfg["epicor"]["base_url"]
        self.api_key = cfg["epicor"]["api_key"]

    def _headers(self, token):
        return {
            "Authorization": f"Bearer {token}",
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    # ----------------------------------------------
    # Normal strict version: raises for any 4xx/5xx
    # ----------------------------------------------

    def post(self, username, password, endpoint, payload):
        token = self.token_service.get_access_token(username, password)
        headers = self._headers(token)

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        self.logger.info(f"POST {url} with payload: {payload}")

        resp = self.session.post(url, json=payload, headers=headers)

        raw = resp.text
        self.logger.info(
            f"Response status={resp.status_code}, RawBody={raw[:2000]}"
        )

        try:
            data = resp.json()
        except Exception:
            data = {"raw_response": raw}
            self.logger.warning("Response is not valid JSON; storing raw response.")

        # raise http errors
        try:
            resp.raise_for_status()
        except Exception as err:
            self.logger.error(f"HTTP error on {endpoint}: {err}, Body={raw}")
            raise

        return {
            "status_code": resp.status_code,
            "data": data
        }



    # ----------------------------------------------
    # Debug-friendly version: returns Response object
    # ----------------------------------------------
    def post_with_response(self, username, password, endpoint, payload, timeout=60):
        """
        Same as post(), but does NOT raise for 4xx/5xx so you can
        inspect resp.status_code and resp.text directly.
        """
        token = self.token_service.get_access_token(username, password)
        headers = self._headers(token)
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        self.logger.info(f"POST {url} (post_with_response)")

        resp = self.session.post(url, json=payload, headers=headers, timeout=timeout)
        print(f"Response status: {resp}")
        return resp  # <-- Return full response, do not raise_for_status
