import time
import logging
import yaml
from utils.http_client import create_session
import base64
import requests

class TokenService:
    def __init__(self, config_path="config.yaml"):
        self.session = create_session()
        self._load_config(config_path)
        self._token_cache = {}
        self.logger = logging.getLogger("TokenService")

    def _load_config(self, path):
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
        epicor = cfg["epicor"]
        self.token_url = epicor["token_url"]
        self.api_key = epicor["api_key"]
        self.default_password = epicor["default_password"]

    def _basic_auth_header(self, username, password):
        creds = f"{username}:{password}"
        encoded = base64.b64encode(creds.encode("utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {encoded}"}

    def get_access_token(self, username, password=None):
        """Generate or reuse Epicor Access Token"""
        password = password or self.default_password
        now = int(time.time())

        # Check cache
        cached = self._token_cache.get(username)
        if cached and now < cached["expiry"]:
            self.logger.info(f"Using cached token for {username}")
            return cached["token"]

        # Build request
        headers = self._basic_auth_header(username, password)
        headers.update({
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        })

        payload = {
            "clientId": "00000000-0000-0000-0000-000000000000",
            "clientSecret": "string",
            "scope": "string"
        }

        # Request token
        self.logger.info(f"Requesting token for {username}...")
        resp = self.session.post(self.token_url, json=payload, headers=headers, timeout=30)

        # Log raw response for debugging
        self.logger.info(f"Token API status: {resp.status_code}")
        self.logger.debug(f"Token API body: {resp.text}")

        # Raise if request itself failed (network or 401, etc.)
        resp.raise_for_status()
        body = resp.json()

        # Extract token safely from nested structure
        try:
            token_info = body.get("returnObj", {}).get("TokenService", [])[0]
            token = token_info.get("AccessToken")
            expires_in = int(token_info.get("ExpiresIn", 3600))
        except Exception as ex:
            self.logger.error(f"Unexpected token response structure: {body}")
            raise Exception(f"Failed to parse token response: {ex}")

        if not token:
            raise Exception(f"No AccessToken found in response: {body}")

        expiry = now + expires_in

        # Cache the token
        self._token_cache[username] = {"token": token, "expiry": expiry}
        self.logger.info(f"[OK] Token generated for {username}, expires in {expires_in} seconds")

        return token
