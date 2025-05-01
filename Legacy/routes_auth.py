from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import request
from app.models_user import User
from .schemas import package_to_dict   # 如需查角色

ns_auth = Namespace("auth", description="认证相关")

login_model = ns_auth.model("Login", {
    "username": fields.String(required=True),
    "password": fields.String(required=True)
})

@ns_auth.route("/login")
class Login(Resource):
    @ns_auth.expect(login_model, validate=True)
    def post(self):
        data = request.json
        user = User.query.filter_by(username=data["username"]).first()
        if not user or not user.verify_password(data["password"]):
            ns_auth.abort(401, "用户名或密码错误")
        token = create_access_token(identity={"id": user.id, "role": user.role})
        return {"token": token}, 200