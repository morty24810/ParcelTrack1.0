"""
快递业务管理系统 · 终端版 CLI
Author : 傅懋杰
Date   : 2025-05-01
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models_user import User
from app.models import Package, db
import random, string
import io, csv
from datetime import datetime

# 创建 Blueprint 对象，用于注册 HTML 页面相关路由
html = Blueprint("html", __name__)

# ---------------- 工具函数 ----------------
def gen_pickup(n=6):
    """生成 n 位数字组成的取件码"""
    return ''.join(random.choices(string.digits, k=n))

# ---------------- 首页 ----------------
@html.route("/home")
def home():
    """首页页面"""
    return render_template("home.html")


# =================== 管理员相关 ===================

@html.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """管理员登录"""
    if request.method == "POST":
        u, p = request.form["username"], request.form["password"]
        admin = User.query.filter_by(username=u, role="ADMIN").first()
        if admin and admin.verify_password(p):
            session.clear()            # 清空旧会话，避免角色冲突
            session["admin"] = admin.id
            return redirect(url_for("html.admin_panel"))
        flash("登录失败")
    return render_template("admin_login.html")

@html.route("/admin")
def admin_panel():
    """管理员控制面板"""
    if "admin" not in session:
        return redirect(url_for("html.admin_login"))
    pkgs  = Package.query.all()
    users = User.query.filter(User.role != "ADMIN").all()
    return render_template("admin_panel.html", pkgs=pkgs, users=users)

@html.route("/admin/add", methods=["POST"])
def admin_add():
    """管理员添加单个包裹"""
    if "admin" not in session:
        return "forbidden", 403
    code  = request.form["code"]
    rec   = request.form["rec"]
    phone = request.form["phone"]
    pkg = Package(code=code, recipient=rec, phone=phone,
                  pickup_code=gen_pickup())
    db.session.add(pkg)
    db.session.commit()
    flash(f"添加成功，取件码 {pkg.pickup_code}")
    return redirect(url_for("html.admin_panel"))

@html.route("/admin/import", methods=["POST"])
def admin_import():
    """
    管理员批量导入包裹（CSV 格式）
    每行包含：code, recipient, phone
    """
    if "admin" not in session:
        return "forbidden", 403

    f = request.files.get("file")
    if not f or f.filename == "":
        flash("请选择 CSV 文件", "warning")
        return redirect(url_for("html.admin_panel"))

    stream = io.StringIO(f.stream.read().decode("utf-8-sig"))
    reader = csv.reader(stream)

    count, fail = 0, 0
    for row in reader:
        try:
            code, rec, phone = row[0].strip(), row[1].strip(), row[2].strip()
            if not (code and rec and phone):
                raise ValueError("字段缺失")
            if Package.query.filter_by(code=code).first():
                continue  # 跳过重复的包裹单号
            pkg = Package(code=code, recipient=rec, phone=phone,
                          pickup_code=gen_pickup())
            db.session.add(pkg)
            count += 1
        except Exception:
            fail += 1

    db.session.commit()
    flash(f"成功导入 {count} 条，失败 {fail} 条",
          "success" if fail == 0 else "warning")
    return redirect(url_for("html.admin_panel"))

@html.route("/admin/clear")
def admin_clear():
    """管理员清空数据库并重建"""
    if "admin" not in session:
        return "forbidden", 403
    db.drop_all()
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        User.create("admin", "admin123", role="ADMIN")
    flash("数据库已清空")
    return redirect(url_for("html.admin_panel"))


# =================== 用户相关 ===================

@html.route("/user/reg", methods=["GET", "POST"])
def user_reg():
    """用户注册"""
    if request.method == "POST":
        phone, pwd = request.form["phone"], request.form["password"]
        if User.query.filter_by(username=phone).first():
            flash("手机号已注册")
            return redirect(url_for("html.user_reg"))
        User.create(phone, pwd, role="EMP")
        flash("注册成功，请登录")
        return redirect(url_for("html.user_login"))
    return render_template("user_reg.html")

@html.route("/user/login", methods=["GET", "POST"])
def user_login():
    """用户登录"""
    if request.method == "POST":
        phone, pwd = request.form["phone"], request.form["password"]
        user = User.query.filter_by(username=phone, role="EMP").first()
        if user and user.verify_password(pwd):
            session.clear()            # 清空旧会话
            session["user"] = phone
            return redirect(url_for("html.user_panel"))
        flash("登录失败")
    return render_template("user_login.html")

@html.route("/user")
def user_panel():
    """用户面板，展示属于该用户的包裹列表"""
    phone = session.get("user")
    if not phone:
        return redirect(url_for("html.user_login"))
    pkgs = Package.query.filter_by(phone=phone).all()
    return render_template("user_panel.html", pkgs=pkgs)

@html.route("/user/pick", methods=["POST"])
def user_pick():
    """用户通过取件码领取包裹"""
    phone = session.get("user")
    if not phone:
        return "forbidden", 403
    code = request.form["code"]
    pickup = request.form["pickup"]
    pkg = Package.query.filter_by(code=code, pickup_code=pickup, phone=phone).first()
    if pkg and pkg.status == "WAIT":
        pkg.status = "OUT"
        db.session.commit()
        flash("取件成功")
    else:
        flash("单号或取件码错误")
    return redirect(url_for("html.user_panel"))


# =================== 无需登录的取件功能 ===================

@html.route("/pickup", methods=["GET", "POST"])
def pickup():
    """公共取件页面，无需登录"""
    msg = None
    if request.method == "POST":
        code = request.form["code"]
        pickup = request.form["pickup"]
        pkg = Package.query.filter_by(code=code, pickup_code=pickup).first()
        if pkg and pkg.status == "WAIT":
            pkg.status   = "OUT"
            pkg.out_time = datetime.utcnow()   # 记录取件时间
            db.session.commit()
            msg = "取件成功"
        else:
            msg = "单号或取件码错误"
    return render_template("pickup.html", msg=msg)


# =================== 登出功能 ===================

@html.route("/logout")
def logout():
    """清除所有会话信息，登出系统"""
    session.clear()
    flash("登出成功", "success")
    return redirect(url_for("html.home"))


# =================== 一键取件通用接口 ===================

@html.route("/package_pickup", methods=["POST"])
def package_pickup():
    """
    管理员 / 用户 一键取件：
    表单需携带 hidden 字段 package_id
    """
    # 权限检查：必须已登录（管理员或用户）
    is_admin = "admin" in session
    is_user  = "user"  in session
    if not (is_admin or is_user):
        flash("未授权操作", "danger")
        return redirect(url_for("html.home"))

    pkg_id = request.form.get("package_id")
    pkg = Package.query.get(pkg_id)

    if pkg and pkg.status == "WAIT":
        pkg.status   = "OUT"
        pkg.out_time = datetime.utcnow()
        db.session.commit()
        flash(f"包裹 {pkg.code} 取件成功", "success")
    else:
        flash("包裹不存在或已取件", "warning")

    # 按登录角色返回对应面板
    return redirect(url_for("html.admin_panel" if is_admin else "html.user_panel"))