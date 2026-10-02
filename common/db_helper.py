# -*- coding: utf-8 -*-
"""数据库直连工具"""
import pymysql
from pymysql.cursors import DictCursor
from config.settings import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
from common.logger import get_logger

logger = get_logger(__name__)


class DBHelper:
    def __init__(self):
        self.conn = pymysql.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER,
            password=DB_PASSWORD, database=DB_NAME,
            charset="utf8mb4", cursorclass=DictCursor,
            autocommit=True,   # 关键：自动提交，每次查询都读最新
        )

    def query_one(self, sql, args=None):
        with self.conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchone()

    def query_all(self, sql, args=None):
        with self.conn.cursor() as cur:
            cur.execute(sql, args or ())
            return cur.fetchall()

    def execute(self, sql, args=None):
        with self.conn.cursor() as cur:
            cur.execute(sql, args or ())
        # autocommit=True 不需要显式 commit，但为了兼容留着
        self.conn.commit()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass