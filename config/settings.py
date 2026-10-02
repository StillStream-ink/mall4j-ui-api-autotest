# -*- coding: utf-8 -*-
"""Global config: local Mall4j admin system"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ============ URLs ============
WEB_URL = os.getenv("MALL4J_WEB_URL", "http://localhost:9527")
API_URL = os.getenv("MALL4J_API_URL", "http://localhost:8085")

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
BUYER = {
    "phone": os.getenv("BUYER_PHONE", "admin"),
    "password": os.getenv("BUYER_PASSWORD", "123456"),
}
SELLER = {
    "phone": os.getenv("SELLER_PHONE", "admin"),
    "password": os.getenv("SELLER_PASSWORD", "123456"),
}

# ============ Database ============
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3307"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Root@123456")
DB_NAME = os.getenv("DB_NAME", "yami_shops")

# ============ Paths ============
ALLURE_RESULTS_DIR = BASE_DIR / "reports" / "allure-results"
SCREENSHOT_DIR = BASE_DIR / "reports" / "screenshots"
LOG_DIR = BASE_DIR / "logs"

# ============ Notification ============
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")

# Ensure dirs exist
for d in (ALLURE_RESULTS_DIR, SCREENSHOT_DIR, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)