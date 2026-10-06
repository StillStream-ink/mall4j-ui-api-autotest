# -*- coding: utf-8 -*-
"""统一日志：控制台 + 文件（带大小轮转）"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "autotest.log"

# 从环境变量读日志级别（默认 INFO）
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# 单个日志文件最大 10MB，最多保留 5 个备份
MAX_BYTES = 10 * 1024 * 1024
BACKUP_COUNT = 5


def get_logger(name: str = "mall4j") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    # 控制台输出
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    # 文件输出：大小轮转，10MB × 6 个文件
    fh = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger