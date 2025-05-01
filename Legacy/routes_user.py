from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Package, db
from .schemas import package_to_dict
from datetime import datetime

ns_user = Namespace("me", description="User Center")

pickup_model = ns_user.model("Pickup", {
    "code": fields.String(required=True, description="快递单号"),
    "pickup_code": fields.String(required=True, description="取件码")
})

@ns_user.route("/packages")
class MyPkgs(Resource):
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()["id"]
        pkgs = Package.query.filter_by(user_id=uid, status="WAIT").all()
        return [package_to_dict(p) for p in pkgs]

@ns_user.route("/pickup")
class Pickup(Resource):
    @jwt_required()
    @ns_user.expect(pickup_model)
    def put(self):
        data = ns_user.payload
        uid  = get_jwt_identity()["id"]
        pkg = Package.query.filter_by(code=data["code"], user_id=uid).first()
        if not pkg or pkg.pickup_code != data["pickup_code"]:
            ns_user.abort(400, "单号或取件码错误")
        pkg.status  = "OUT"
        pkg.out_time = datetime.utcnow()
        db.session.commit()
        return package_to_dict(pkg)