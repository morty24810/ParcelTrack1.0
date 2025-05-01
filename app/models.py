"""
快递业务管理系统 · 终端版 CLI
Author : 傅懋杰
Date   : 2025-05-01
"""

from datetime import datetime, timezone
from . import db

class Package(db.Model):
    # 包裹主键 ID，自增
    id = db.Column(db.Integer, primary_key=True)

    # 包裹唯一编号，不能为空
    code = db.Column(db.String(32), unique=True, nullable=False)

    # 收件人姓名（可选）
    recipient = db.Column(db.String(32))            # 收件人

    # 收件人电话（可选）
    phone = db.Column(db.String(16))

    # 取件码（如短信通知中的验证码）
    pickup_code = db.Column(db.String(6))

    # 包裹状态，默认是 WAIT，可选值包括 WAIT（待取）、OUT（已取）
    status = db.Column(
        db.Enum("WAIT", "OUT", name="pkg_status"),
        default="WAIT"
    )

    # 入库时间，使用带时区的 UTC 时间作为默认值
    in_time = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # 出库时间，可为空（即未取出）
    out_time = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    # 所属用户 ID，外键关联到 user 表的 id 字段
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))