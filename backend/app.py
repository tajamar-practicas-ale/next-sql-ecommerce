from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config.settings import Config
from database.db_handler import DBHandler
from api.auth import auth_bp
from api.products import products_bp
from api.orders import orders_bp

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Configurar CORS
CORS(app, origins=Config.CORS_ORIGINS.split(","))

# Crear tablas y precargar productos
with app.app_context():
    db.create_all()
    db_handler = DBHandler()
    db_handler.initialize_products()

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/users')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(orders_bp, url_prefix='/orders')

if __name__ == '__main__':
    app.run(debug=True)
