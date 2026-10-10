# -*- coding: utf-8 -*-
"""Global config: local Mall4j admin system"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ============ URLs ============
# 本地后台管理前端
WEB_URL = os.getenv("MALL4J_WEB_URL", "http://127.0.0.1:9527")
# 本地后台管理后端 API
API_URL = os.getenv("MALL4J_API_URL", "http://127.0.0.1:8085")
# 买家端 API（8086 前台）
BUYER_API_URL = os.getenv("MALL4J_BUYER_API_URL", "http://127.0.0.1:8086")
# 买家端 H5 前端（80）
BUYER_WEB_URL = os.getenv("MALL4J_BUYER_WEB_URL", "http://127.0.0.1")

# 备用：线上演示环境
DEMO_WEB_URL = "https://b2b2b-pc-demo.mall4j.com/"
DEMO_API_URL = "https://b2b2b-pc-demo.mall4j.com/"

# ============ Browser ============
BROWSER = os.getenv("BROWSER", "chromium")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
SLOW_MO = int(os.getenv("SLOW_MO", "0"))
DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "15000"))

# ============ Accounts ============
ADMIN = {
    "username": os.getenv("ADMIN_USERNAME", "admin"),
    "password": os.getenv("ADMIN_PASSWORD", "123456"),
}

# 买家端账号（8086 前台 API）
BUYER = {
    "mobile": os.getenv("BUYER_MOBILE", "13000000001"),
    "password": os.getenv("BUYER_PASSWORD", "123456"),
}

# ============ Database ============
# 注意：本地 Mall4j 使用非标准端口 3307（默认 3306，避免本机冲突）
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3307"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Root@123456")
DB_NAME = os.getenv("DB_NAME", "yami_shops")

# ============ Redis ============
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# ============ Crypto ============
# AES 加密密钥（与前端 crypto.js 保持一致）
AES_KEY = os.getenv("MALL4J_AES_KEY", "-mall4j-password")

# ============ Paths ============
ALLURE_RESULTS_DIR = BASE_DIR / "reports" / "allure-results"
SCREENSHOT_DIR = BASE_DIR / "reports" / "screenshots"
LOG_DIR = BASE_DIR / "logs"

# ============ Notification ============
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")

for d in (ALLURE_RESULTS_DIR, SCREENSHOT_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)