from flask_restx import Namespace, fields, Resource
from flask import request
from flask_jwt_extended import jwt_required
from app.services import create_package, fetch_package_by_code
from .schemas  import package_to_dict
from app.models import Package
from datetime import datetime
from app import db

ns_package = Namespace("packages", description="包裹接口")

pkg_model = ns_package.model("Package", {
    "code": fields.String(required=True, description="快递单号")
})

@ns_package.route("/")
class PackageList(Resource):
    @jwt_required()
    @ns_package.expect(pkg_model, validate=True)
    def post(self):
        data = request.json
        try:
            pkg = create_package(data["code"])
            return package_to_dict(pkg), 201
        except ValueError as e:
            ns_package.abort(400, str(e))

    @jwt_required()
    def get(self):
        pkgs = Package.query.all()
        return [package_to_dict(p) for p in pkgs]

@ns_package.route("/<string:code>")
class PackageItem(Resource):
    @jwt_required()
    def get(self, code):
        pkg = fetch_package_by_code(code)
        if not pkg:
            ns_package.abort(404, "未找到包裹")
        return package_to_dict(pkg)

@ns_package.route("/<string:code>/out")
class PackageOut(Resource):
    @jwt_required()
    def put(self, code):
        pkg = fetch_package_by_code(code)
        if not pkg:
            ns_package.abort(404, "未找到包裹")
        if pkg.status == "OUT":
            ns_package.abort(400, "包裹已取出")
        pkg.status = "OUT"
        pkg.out_time = datetime.utcnow()
        db.session.commit()
        return package_to_dict(pkg)