import warnings
warnings.filterwarnings("ignore", message="Workbook contains no default style")
import tempfile

import allure
import openpyxl
import pytest

from api.admin.export_api import ExportApi


def _save_and_parse(resp, prefix: str = "export") -> openpyxl.Workbook:
    """把二进制响应保存为 xlsx，返回 Workbook 对象"""
    assert resp.status_code == 200, f"HTTP {resp.status_code}: {resp.text[:200]}"

    ct = resp.headers.get("Content-Type", "")
    print(f"\nContent-Type: {ct}")
    assert (
        "excel" in ct.lower()
        or "spreadsheet" in ct.lower()
        or "octet-stream" in ct.lower()
    ), f"返回的不是 Excel: {ct}"

    tmp_path = None
    try:
        tmp = tempfile.NamedTemporaryFile(
            prefix=prefix, suffix=".xlsx", delete=False
        )
        tmp_path = tmp.name
        tmp.write(resp.content)
        tmp.close()
        print(f"文件大小: {len(resp.content)} bytes")

        wb = openpyxl.load_workbook(tmp_path, read_only=True)
        return wb
    finally:
        # 延迟删除交给测试结束后清理，避免 Windows 文件锁
        pass


@allure.feature("订单管理")
@allure.story("导出待发货订单 - Excel 可解析")
def test_export_waiting_consignment(api_session):
    """导出待发货订单，验证 Excel 能打开且表头非空"""
    api = ExportApi(api_session)
    resp = api.export_waiting_consignment()

    wb = _save_and_parse(resp, prefix="waiting")
    assert len(wb.sheetnames) > 0, "Excel 没有 sheet"

    ws = wb.active
    # 取第一行作为表头
    header = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    print(f"Sheet: {ws.title}, 表头: {header}")

    assert len(header) > 0, "表头为空"
    assert any(header), "表头全是空值"

    # 统计总行数
    row_count = ws.max_row
    print(f"总行数（含表头）: {row_count}")
    assert row_count >= 1, "Excel 至少应有表头"


@allure.feature("订单管理")
@allure.story("导出销售记录 - Excel 可解析")
def test_export_sold(api_session):
    """导出销售记录，验证 Excel 能打开且表头非空"""
    api = ExportApi(api_session)
    resp = api.export_sold()

    wb = _save_and_parse(resp, prefix="sold")
    assert len(wb.sheetnames) > 0, "Excel 没有 sheet"

    ws = wb.active
    header = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    print(f"Sheet: {ws.title}, 表头: {header}")

    assert len(header) > 0, "表头为空"
    assert any(header), "表头全是空值"

    row_count = ws.max_row
    print(f"总行数（含表头）: {row_count}")
    assert row_count >= 1, "Excel 至少应有表头"


@allure.feature("订单管理")
@allure.story("导出待发货订单 - 带筛选条件")
def test_export_waiting_with_filter(api_session):
    """带收货人筛选条件导出，验证仍返回合法 Excel"""
    api = ExportApi(api_session)
    resp = api.export_waiting_consignment(consignment_name="不存在的人")

    wb = _save_and_parse(resp, prefix="filter")
    ws = wb.active
    header = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
    print(f"\n带筛选导出，表头: {header}")

    # 即使筛选无结果，Excel 结构也应完整
    assert len(header) > 0, "筛选后表头丢失"