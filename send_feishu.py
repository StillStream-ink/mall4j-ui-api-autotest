# -*- coding: utf-8 -*-
"""飞书通知：自动读取 allure-results，推送测试报告"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

# ========== 配置区 ==========
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "reports" / "allure-results"

# 自动加载 .env
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

WEBHOOK_URL = os.getenv("FEISHU_WEBHOOK", "")
PROJECT_NAME = "Mall4j UI + API 自动化测试"
# ===========================


def parse_allure_results(results_dir: Path):
    """解析 allure-results 目录统计结果"""
    total = passed = failed = skipped = 0
    duration = 0.0
    failed_names = []

    if not results_dir.exists():
        return None

    for f in results_dir.glob("*-result.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            status = data.get("status", "unknown")
            total += 1
            duration += (data.get("stop", 0) - data.get("start", 0)) / 1000.0
            if status == "passed":
                passed += 1
            elif status == "failed":
                failed += 1
                failed_names.append(data.get("name", "unknown"))
            elif status == "skipped":
                skipped += 1
        except Exception:
            continue

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "duration": round(duration, 1),
        "failed_names": failed_names,
    }


def send_card(stats):
    """发送 interactive 卡片到飞书"""
    if not WEBHOOK_URL:
        print("[SKIP] FEISHU_WEBHOOK 未配置，跳过通知")
        print("       可在 .env 文件中设置: FEISHU_WEBHOOK=https://open.feishu.cn/...")
        return False

    total = stats["total"]
    passed = stats["passed"]
    failed = stats["failed"]
    skipped = stats["skipped"]

    if failed == 0:
        status_icon = "✅"
        status_text = "**测试通过**"
        color = "green"
    else:
        status_icon = "❌"
        status_text = "**测试失败**"
        color = "red"

    pass_rate = (passed / total * 100) if total else 0

    content = f"""**状态：** {status_text}
**执行时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

**📊 测试统计**

- 📋 总用例：**{total}**
- ✅ 通过：**{passed}**
- ❌ 失败：**{failed}**
- ⏭️ 跳过：**{skipped}**
- ⏱️ 耗时：**{stats['duration']} 秒**

**📈 通过率：** **{pass_rate:.1f}%** ({passed}/{total})

> 📎 详细报告请查看 Allure
"""

    if stats["failed_names"]:
        content += "\n**❌ 失败用例：**\n"
        for n in stats["failed_names"][:5]:
            content += f"- {n}\n"

    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "elements": [
                {"tag": "div", "text": {"content": content, "tag": "lark_md"}},
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [
                        {"content": f"🏷️ 项目: {PROJECT_NAME}", "tag": "plain_text"}
                    ],
                },
            ],
            "header": {
                "title": {
                    "content": f"{status_icon} Mall4j 测试报告",
                    "tag": "plain_text",
                },
                "template": color,
            },
        },
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        result = response.json()
        if result.get("code") == 0:
            print("[OK] 飞书通知已发送")
            return True
        else:
            print(f"[FAIL] 发送失败：{result}")
            return False
    except Exception as e:
        print(f"[FAIL] 发送异常：{e}")
        return False


def send_test_message():
    """发一条测试消息，验证 webhook 是否配置正确"""
    if not WEBHOOK_URL:
        print("[SKIP] FEISHU_WEBHOOK 未配置")
        return
    data = {"msg_type": "text", "content": {"text": "✅ Mall4j 飞书机器人测试成功！"}}
    resp = requests.post(WEBHOOK_URL, json=data)
    print(f"Response: {resp.status_code} {resp.json()}")


if __name__ == "__main__":
    # 参数模式：py send_feishu.py test  → 发一条测试消息
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        send_test_message()
        sys.exit(0)

    # 默认模式：解析 allure 结果并推送
    stats = parse_allure_results(RESULTS_DIR)
    if stats is None:
        print(f"[ERROR] 未找到 {RESULTS_DIR}，请先运行 pytest")
        sys.exit(1)

    print(f"统计结果: {stats}")
    send_card(stats)