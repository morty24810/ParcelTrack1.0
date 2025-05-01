import random, string
from app.models import Package, db

def gen_pickup_code(length=6):
    return "".join(random.choices(string.digits, k=length))

def create_package(code):
    if Package.query.filter_by(code=code).first():
        raise ValueError("重复单号")
    pkg = Package(code=code, pickup_code=gen_pickup_code(), status="WAIT")
    db.session.add(pkg)
    db.session.commit()
    return pkg

def fetch_package_by_code(code):
    return Package.query.filter_by(code=code).first()