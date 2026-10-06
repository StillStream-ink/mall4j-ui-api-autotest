# -*- coding: utf-8 -*-
"""HTTP session wrapper"""
import requests
from common.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    def __init__(self, base_url: str, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "mall4j-autotest/1.0",
        })

    def set_token(self, token: str):
        self.session.headers.update({"Authorization": token})

    def request(self, method: str, path: str, **kwargs):
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

    def get(self, path: str, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def delete_json(self, path: str, json_body, **kwargs):
        """DELETE 请求带 JSON body（Mall4j 后端设计如此）"""
        return self.request("DELETE", path, json=json_body, **kwargs)

    def close(self):
        """关闭 session（fixture teardown 调用）"""
        try:
            self.session.close()
        except Exception:
            pass