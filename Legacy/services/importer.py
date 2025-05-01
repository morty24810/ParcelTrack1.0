# app/services/importer.py
import csv, random, string

def gen_code(n=6):
    return "".join(random.choices(string.digits, k=n))

def import_csv(path):
    from app.models import Package, User, db

    with open(path, newline='', encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pkg = Package(
                code=row["code"],
                recipient=row["recipient"],
                phone=row["phone"],
                pickup_code=gen_code(),
                status="WAIT",
                user_id=User.query.filter_by(username=row["username"]).first().id
            )
            db.session.add(pkg)
        db.session.commit()