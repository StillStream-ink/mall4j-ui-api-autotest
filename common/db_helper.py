# -*- coding: utf-8 -*-
"""数据库直连工具"""
from typing import Any, Dict, List, Optional, Sequence

import pymysql
from pymysql.cursors import DictCursor

from config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from common.logger import get_logger

logger = get_logger(__name__)


class DBHelper:
    def __init__(self) -> None:
        self.conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=DictCursor,
            autocommit=True,
        )

    def query_one(
        self,
        sql: str,
        args: Optional[Sequence[Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchone()

    def query_all(
        self,
        sql: str,
        args: Optional[Sequence[Any]] = None,
    ) -> List[Dict[str, Any]]:
        with self.conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchall()

    def execute(
        self,
        sql: str,
        args: Optional[Sequence[Any]] = None,
    ) -> None:
        with self.conn.cursor() as cur:
            cur.execute(sql, args or ())

    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass