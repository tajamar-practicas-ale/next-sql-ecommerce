from flask import Blueprint
from .auth import auth_bp
from .products import products_bp
from .orders import orders_bp

api_bp = Blueprint('api', __name__)
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(products_bp)
api_bp.register_blueprint(orders_bp)
