"""
快递业务管理系统
Author : 傅懋杰
Date   : 2025-05-21
"""

import pytest
from app import create_app, db as _db

@pytest.fixture
def app():
    """创建 Flask 应用（使用内存中的 SQLite 数据库）并初始化数据库表"""
    app = create_app()
    app.config.update(
        TESTING=True,  # 启用测试模式
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",  # 使用内存数据库，避免污染正式数据
        WTF_CSRF_ENABLED=False,  # 测试时关闭 CSRF 保护
        SERVER_NAME="localhost"  # 配置 SERVER_NAME，便于使用 url_for
    )
    with app.app_context():
        _db.create_all()  # 创建所有数据库表
        yield app  # 提供 app 对象给测试使用
        _db.session.remove()  # 清理数据库会话
        _db.drop_all()  # 删除所有表，恢复干净状态

@pytest.fixture
def client(app):
    """返回 Flask 测试客户端，用于发送请求"""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """提供 SQLAlchemy 的 Session 对象，用于数据库操作"""
    return _db.session