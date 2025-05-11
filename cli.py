"""
快递业务管理系统 · 终端版 CLI
Author : 傅懋杰
Date   : 2025-05-01
"""

# ---------------- 模块导入 ----------------
import os, sys, csv, warnings, getpass
from getpass import GetPassWarning
from datetime import timezone, datetime
from app import create_app, db
from app.models_user import User
from app.models import Package

# ---------------- 初始化 Flask 应用上下文 ----------------
app = create_app()
app.app_context().push()  # 激活应用上下文，允许数据库操作等

# ---------------- 工具函数 ----------------

def safe_getpass(prompt="密码: "):
    """在某些 IDE 中无法关闭回显时，自动降级为普通输入"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", GetPassWarning)
        try:
            return getpass.getpass(prompt)
        except GetPassWarning:
            return input("(输入将可见) " + prompt)

def gen_pickup(n=6):
    """生成 n 位随机取件码"""
    from random import choices
    from string import digits
    return ''.join(choices(digits, k=n))

def clear_screen():
    """
    清空终端屏幕：
    - Windows 用 cls
    - Unix-like 用 clear
    - 若在 IDE / PyCharm 运行且非 TTY，则简单打印多行空白
    """
    if os.name == "nt":
        os.system("cls")
    else:
        if sys.stdout.isatty():
            os.system("clear")
        else:
            # IDE 运行环境下避免打印 \033c 控制符
            print("\n" * 80)

# ---------------- 主菜单 ----------------

def main_menu():
    """显示主菜单并处理选项"""
    while True:
        print("=== 快递终端系统 ===")
        print("1) 管理员登录")
        print("2) 用户登录")
        print("3) 用户注册")
        print("4) 无需登录取件")
        print("0) 退出程序")
        opt = input("> ").strip()
        if opt == "1":
            admin_login()
        elif opt == "2":
            user_login()
        elif opt == "3":
            user_register()
        elif opt == "4":
            pickup_no_login()
        elif opt == "0":
            sys.exit(0)
        else:
            print("无效选项\n")

# ---------------- 管理员功能 ----------------

def admin_login():
    """管理员登录并进入操作界面"""
    clear_screen()
    u = input("管理员用户名: ")
    p = safe_getpass("密码: ")

    admin = User.query.filter_by(username=u, role="ADMIN").first()
    if not (admin and admin.verify_password(p)):
        print("登录失败\n")
        return

    print("登录成功\n")
    while True:
        print("1) 添加包裹  2) 查看全部包裹  3) 批量导入 CSV  4) 清空数据库  0) 返回主菜单")
        opt = input("> ").strip()
        if opt == "1":
            # 手动添加包裹
            code = input("单号: ")
            rec  = input("收件人: ")
            phone= input("手机号: ")
            pkg  = Package(code=code, recipient=rec, phone=phone,
                           pickup_code=gen_pickup())
            db.session.add(pkg)
            db.session.commit()
            print(f"添加成功，取件码 {pkg.pickup_code}\n")

        elif opt == "2":
            # 查看所有包裹
            pkgs = Package.query.all()
            print("ID | 单号 | 收件人 | 手机 | 状态 | 取件码")
            for p in pkgs:
                print(f"{p.id} | {p.code} | {p.recipient} | {p.phone} | {p.status} | {p.pickup_code}")
            print()

        elif opt == "3":
            # 从 CSV 文件导入包裹数据
            path = input("CSV 文件路径: ").strip()
            if not os.path.exists(path):
                print("文件不存在\n")
                continue
            import_csv(path)

        elif opt == "4":
            # 清空数据库
            yn = input("确定清空数据库?(y/n) ").lower()
            if yn == "y":
                db.drop_all()
                db.session.commit()  # 确保 DROP 提交
                db.session.close()  # <— 新增，清理旧 Session
                db.create_all()
                # 重新创建默认管理员
                if not User.query.filter_by(username="admin").first():
                    User.create("admin", "admin123", role="ADMIN")
                print("数据库已清空\n")

        elif opt == "0":
            clear_screen()
            break
        else:
            print("无效选项\n")

def import_csv(path):
    """批量导入包裹数据（CSV 文件）"""
    count, fail = 0, 0
    with open(path, newline='', encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                code, rec, phone = [x.strip() for x in row[:3]]
                if not all([code, rec, phone]):
                    raise ValueError
                if Package.query.filter_by(code=code).first():
                    continue
                db.session.add(Package(code=code, recipient=rec,
                                       phone=phone, pickup_code=gen_pickup()))
                count += 1
            except (ValueError, IndexError, csv.Error):
                fail += 1
    db.session.commit()
    print(f"导入完毕：成功 {count} 条，失败 {fail} 条\n")

# ---------------- 用户功能 ----------------

def user_register():
    """用户注册"""
    phone = input("手机号: ")
    if User.query.filter_by(username=phone).first():
        print("已注册\n")
        return
    pwd = safe_getpass("密码: ")
    User.create(phone, pwd, role="EMP")
    print("注册成功，请登录\n")

def user_login():
    """用户登录并进入用户面板"""
    phone = input("手机号: ")
    pwd   = safe_getpass("密码: ")
    user  = User.query.filter_by(username=phone, role="EMP").first()
    if not (user and user.verify_password(pwd)):
        print("登录失败\n")
        return

    print("登录成功\n")
    while True:
        print("1) 查看包裹  2) 凭取件码取件  0) 返回主菜单")
        opt = input("> ").strip()
        if opt == "1":
            # 展示该手机号绑定的所有包裹
            pkgs = Package.query.filter_by(phone=phone).all()
            print("单号 | 收件人 | 状态 | 取件码")
            for p in pkgs:
                print(f"{p.code} | {p.recipient} | {p.status} | {p.pickup_code}")
            print()
        elif opt == "2":
            # 取件操作（登录用户）
            pickup_operation(phone)
        elif opt == "0":
            clear_screen()
            break
        else:
            print("无效选项\n")

# ---------------- 取件操作 ----------------

def pickup_operation(phone=None):
    """
    取件操作，支持登录用户（带手机号）或匿名用户
    """
    code   = input("单号: ")
    pickup = input("取件码: ")
    query  = Package.query.filter_by(code=code, pickup_code=pickup)
    if phone:
        query = query.filter_by(phone=phone)
    pkg = query.first()
    if pkg and pkg.status == "WAIT":
        pkg.status = "OUT"
        pkg.out_time = datetime.now(timezone.utc)
        db.session.commit()
        print("取件成功\n")
    else:
        print("单号或取件码错误\n")

def pickup_no_login():
    """无需登录的公共取件入口"""
    pickup_operation()

# ---------------- 程序入口 ----------------

if __name__ == "__main__":
    clear_screen()
    # 启动前确保管理员账号存在
    if not User.query.filter_by(username="admin").first():
        User.create("admin", "admin123", role="ADMIN")
    main_menu()