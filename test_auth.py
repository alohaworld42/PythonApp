from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/test')
def test():
    return "Test route"

print("Auth blueprint created successfully")
print(f"Blueprint name: {auth_bp.name}")