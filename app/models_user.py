"""
快递业务管理系统 · 终端版 CLI
Author : 傅懋杰
Date   : 2025-05-01
"""

from . import db
from passlib.hash import bcrypt

class User(db.Model):
    # 用户主键 ID，自增
    id = db.Column(db.Integer, primary_key=True)

    # 用户名，唯一且不能为空
    username = db.Column(db.String(32), unique=True, nullable=False)

    # 存储经过加密的密码，不能为空
    password = db.Column(db.String(128), nullable=False)

    # 用户角色，默认是普通员工 EMP，也可为管理员 ADMIN
    role = db.Column(
        db.Enum("EMP", "ADMIN", name="role_enum"),
        default="EMP"
    )

    @staticmethod
    def create(username, raw_pwd, role="EMP"):
        """
        创建用户对象并保存到数据库。
        密码会使用 bcrypt 进行加密。
        """
        user = User(username=username, password=bcrypt.hash(raw_pwd), role=role)
        db.session.add(user)
        db.session.commit()
        return user

    def verify_password(self, raw_pwd):
        """
        验证输入的原始密码是否与数据库中的加密密码匹配。
        """
        return bcrypt.verify(raw_pwd, self.password)