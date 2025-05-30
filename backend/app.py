from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config.settings import Config
from models import db  # Importas la instancia global
from database.db_handler import DBHandler
from api.auth import auth_bp
from api.products import products_bp
from api.orders import orders_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app, origins=Config.CORS_ORIGINS.split(","))

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')

    # Crear tablas y precargar productos
    with app.app_context():
        db.create_all()
        db_handler = DBHandler()
        db_handler.initialize_products()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
