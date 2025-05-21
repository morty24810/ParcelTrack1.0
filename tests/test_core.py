"""
快递业务管理系统
Author : 傅懋杰
Date   : 2025-05-21
"""

import csv, tempfile
from app.models_user import User
from app.models import Package
from app.routes_html import gen_pickup
from cli import import_csv                      # CLI 中的批量导入函数

def test_user_password(db_session):
    """T1: 测试用户创建与密码验证"""
    u = User.create("18888888888", "pwd123")  # 创建用户（含密码加密逻辑）
    assert u.password != "pwd123"             # 验证密码已加密
    assert u.verify_password("pwd123")        # 验证密码校验成功

def test_add_package(db_session):
    """T2: 管理员手动添加包裹"""
    p = Package(
        code="PKG001",
        recipient="张三",
        phone="13900000000",
        pickup_code=gen_pickup()              # 生成随机取件码
    )
    db_session.add(p)
    db_session.commit()

    row = Package.query.filter_by(code="PKG001").first()
    assert row and row.status == "WAIT"       # 确认状态为等待取件

def test_pickup_no_login(client, db_session):
    """T3: 无需登录完成取件流程"""
    # 插入测试包裹
    p = Package(
        code="PKG002",
        recipient="李四",
        phone="13700000000",
        pickup_code="111111"
    )
    db_session.add(p)
    db_session.commit()

    # 使用客户端模拟提交表单取件
    resp = client.post("/pickup", data={
        "code": "PKG002",
        "pickup": "111111"
    })
    assert "取件成功" in resp.data.decode()    # 页面提示成功

    # 确认数据库中状态已更新
    pkg = Package.query.filter_by(code="PKG002").first()
    assert pkg.status == "OUT"
    assert pkg.out_time is not None           # 确认取件时间被记录

def test_import_csv(db_session, capsys):
    """T4: 测试批量导入 CSV 并验证导入统计输出"""
    # 临时生成一个 CSV 文件用于测试
    with tempfile.NamedTemporaryFile("w", delete=False, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PKG003", "王五", "13600000000"])  # 合法记录
        writer.writerow(["", "缺失", "错误"])               # 非法记录
        csv_path = f.name

    import_csv(csv_path)                      # 调用 CLI 中的导入函数
    captured = capsys.readouterr().out        # 捕获命令行输出
    assert "成功 1 条，失败 1 条" in captured  # 验证输出统计信息