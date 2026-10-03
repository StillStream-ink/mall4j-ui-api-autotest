# -*- coding: utf-8 -*-
"""Mall4j 环境检查（Python 版，Windows 友好）"""
import socket
import subprocess
import sys
from pathlib import Path

def check_port(host, port):
    """检查端口是否监听"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        s.close()

def check_service(name):
    """检查 Windows 服务"""
    r = subprocess.run(
        ["powershell", "-Command", f"Get-Service {name} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Status"],
        capture_output=True, text=True, timeout=5,
    )
    return "Running" in r.stdout

def check_process(name):
    """检查进程"""
    r = subprocess.run(
        ["powershell", "-Command", f"Get-Process {name} -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count"],
        capture_output=True, text=True, timeout=5,
    )
    try:
        return int(r.stdout.strip()) > 0
    except Exception:
        return False

def count_process(name):
    r = subprocess.run(
        ["powershell", "-Command", f"Get-Process {name} -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count"],
        capture_output=True, text=True, timeout=5,
    )
    try:
        return int(r.stdout.strip())
    except Exception:
        return 0


def main():
    print()
    print("=" * 60)
    print("  Mall4j 环境健康检查")
    print("=" * 60)

    fail = 0

    # 1. 端口
    print("\n[1/5] 端口检查")
    for port in [6379, 8085, 8086, 9527]:
        ok = check_port("127.0.0.1", port)
        flag = "[OK]" if ok else "[FAIL]"
        print(f"  {flag} Port {port}")
        if not ok:
            fail += 1

    # 2. MySQL
    print("\n[2/5] MySQL 服务")
    if check_service("MySQL80"):
        print("  [OK] MySQL80 Running")
    else:
        print("  [FAIL] MySQL80 Not Running")
        fail += 1

    # 3. Redis
    print("\n[3/5] Redis 进程")
    if check_process("redis-server"):
        print("  [OK] Redis Running")
    else:
        print("  [FAIL] Redis Not Running")
        fail += 1

    # 4. Java
    print("\n[4/5] Java 进程")
    n = count_process("java")
    print(f"  [OK] Java 进程数: {n}")

    # 5. 磁盘
    print("\n[5/5] 磁盘")
    disk = Path("E:/")
    try:
        import shutil
        total, used, free = shutil.disk_usage(disk)
        pct = round(used / total * 100, 1)
        print(f"  E 盘使用率: {pct}%")
    except Exception as e:
        print(f"  [SKIP] 磁盘检查失败: {e}")

    # 汇总
    print()
    print("=" * 60)
    if fail == 0:
        print("  全部通过")
    else:
        print(f"  发现 {fail} 个问题")
    print("=" * 60)

    return fail


if __name__ == "__main__":
    sys.exit(main())