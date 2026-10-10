# -*- coding: utf-8 -*-
"""HTTP session wrapper"""
from typing import Any, Dict, Optional

import requests

from common.logger import get_logger

logger = get_logger(__name__)


class APIClient:
    def __init__(self, base_url: str, timeout: int = 10) -> None:
        self.base_url: str = base_url.rstrip("/")
        self.timeout: int = timeout
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "mall4j-autotest/1.0",
        })

    def set_token(self, token: str) -> None:
        self.session.headers.update({"Authorization": token})

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}"
        kwargs.setdefault("timeout", self.timeout)

        # 日志脱敏：passWord 字段替换为 ****
        json_body = kwargs.get("json")
        log_json: Any = json_body
        if isinstance(json_body, dict) and "passWord" in json_body:
            log_json = {**json_body, "passWord": "****"}

        logger.info(
            f"[REQ] {method.upper()} {url} params={kwargs.get('params')} json={log_json}"
        )
        logger.info(f"      headers={dict(self.session.headers)}")

        resp: requests.Response = self.session.request(method, url, **kwargs)
        try:
            body: Any = resp.json()
        except Exception:
            body = resp.text[:500]
        logger.info(f"[RES] {resp.status_code}  {body}")
        return resp

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", path, **kwargs)

    def delete_json(
        self,
        path: str,
        json_body: Any,
        **kwargs: Any,
    ) -> requests.Response:
        """DELETE 请求带 JSON body（Mall4j 后端设计如此）"""
        return self.request("DELETE", path, json=json_body, **kwargs)

    def close(self) -> None:
        """关闭 session（fixture teardown 调用）"""
        try:
            self.session.close()
        except Exception:
            pass