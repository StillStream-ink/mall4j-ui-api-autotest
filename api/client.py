# -*- coding: utf-8 -*-
"""HTTP session wrapper"""
import requests
from common.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    def __init__(self, base_url, timeout=15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "mall4j-autotest/1.0",
        })

    def set_token(self, token):
        self.session.headers.update({"Authorization": token})

    def request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        kwargs.setdefault("timeout", self.timeout)
        logger.info(f"[REQ] {method.upper()} {url} params={kwargs.get('params')} json={kwargs.get('json')}")
        logger.info(f"      headers={dict(self.session.headers)}")
        resp = self.session.request(method, url, **kwargs)
        try:
            body = resp.json()
        except Exception:
            body = resp.text[:500]
        logger.info(f"[RES] {resp.status_code}  {body}")
        return resp

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)