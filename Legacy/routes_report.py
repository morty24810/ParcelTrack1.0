from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app.models import Package, db

ns_report = Namespace("reports", description="统计报表")

def is_admin():
    return get_jwt_identity()["role"] == "ADMIN"

@ns_report.route("/summary")
class Summary(Resource):
    @jwt_required()
    def get(self):
        if not is_admin():
            ns_report.abort(403)
        total = db.session.query(func.count(Package.id)).scalar()
        wait  = db.session.query(func.count(Package.id)).filter_by(status="WAIT").scalar()
        out   = db.session.query(func.count(Package.id)).filter_by(status="OUT").scalar()
        return {"total": total, "waiting": wait, "out": out}