"""
快递业务管理系统 · 终端版 CLI
Author : 傅懋杰
Date   : 2025-05-01
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_restx import Api                        # 已弃用：用于生成 REST API 文档
from flask_jwt_extended import JWTManager           # 第一步：导入 JWT 管理器

# 第二步：初始化数据库和 JWT 管理器实例
db = SQLAlchemy()                                   # 创建 SQLAlchemy 实例
jwt = JWTManager()                                  # 创建 JWT 管理器实例
# api = Api(title="Courier API", version="1.0", doc="/swagger")  # 已弃用：Swagger API 文档

def create_app():
    app = Flask(__name__)                           # 创建 Flask 应用实例
    app.config.from_object("config.Config")         # 加载配置文件

    # 设置 Flask 所需的密钥（用于会话和 JWT 加密）
    app.config['SECRET_KEY'] = '5c3d2f9e8f30b2c7f8f4a914ae929ed6'         # Flask 会话密钥
    app.config["JWT_SECRET_KEY"] = "40886f618e0b2f6159c2df62c7c9b10c004c45fceaf60588e8d02281c08aef56"  # JWT 加密密钥

    # 第三步：将数据库和 JWT 与应用绑定
    db.init_app(app)
    jwt.init_app(app)
    # api.init_app(app)                              # 已弃用：不再启用 Swagger API 文档

    # 第四步：导入并注册 HTML 路由模块
    from app.routes_html import html
    app.register_blueprint(html)                    # 注册 HTML 蓝图，用于网页界面

    # 以下为已弃用的 REST API 路由注册
    # api.add_namespace(ns_package, path="/api")
    # api.add_namespace(ns_auth,    path="/api/auth")
    # api.add_namespace(ns_admin,   path="/api/admin")
    # api.add_namespace(ns_user,    path="/api")
    # api.add_namespace(ns_report,  path="/api")

    with app.app_context():
        db.create_all()                             # 自动创建数据库表（如果不存在）

        # 自动创建默认管理员账户
        from .models_user import User
        if not User.query.filter_by(username="admin").first():
            User.create("admin", "admin123", role="ADMIN")
            app.logger.info("Created default admin account (admin/admin123)")

    return app                                       # 返回应用实例