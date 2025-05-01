# app/routes_admin.py
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.datastructures import FileStorage

# Import Package model for listing packages
from app.models import Package

ns_admin = Namespace("admin", description="Admin Ops")
upload = ns_admin.parser()
upload.add_argument("file", location="files", type=FileStorage, required=True)

def is_admin():   # 简单判断
    return get_jwt_identity()["role"] == "ADMIN"

@ns_admin.route("/import")
class CSVImport(Resource):
    @jwt_required()
    @ns_admin.expect(upload)
    def post(self):
        if not is_admin():
            ns_admin.abort(403)
        file = upload.parse_args()["file"]
        tmp_path = f"/tmp/{file.filename}"
        file.save(tmp_path)

        from app.services import import_csv
        import_csv(tmp_path)
        return {"msg": "导入完成"}, 201


# Add GET handler for /api/admin/packages
@ns_admin.route("/packages")
class PackageList(Resource):
    @jwt_required()
    def get(self):
        # Check if the user is an admin
        if not is_admin():
            ns_admin.abort(403, "You are not authorized to access this resource")
        # Fetch all packages
        packages = Package.query.all()
        # Return package details in the response
        return [
            {
                "id": p.id,
                "code": p.code,
                "recipient": p.recipient,
                "status": p.status
            }
            for p in packages
        ], 200