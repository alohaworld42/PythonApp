from flask import Blueprint

integrations_bp = Blueprint('integrations', __name__)

@integrations_bp.route('/test')
def test():
    return "Integrations blueprint working"