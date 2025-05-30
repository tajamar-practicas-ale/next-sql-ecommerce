import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta

load_dotenv()
BASE_DIR = Path(__file__).parent.parent.resolve()  # Ajusta para que sea la raíz del proyecto

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")
    # Ruta absoluta para evitar problemas de SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", f"sqlite:///{BASE_DIR}/ecommerce.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=86400)  # 24 horas
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SECURE = False  # True en producción con HTTPS
    JWT_COOKIE_HTTPONLY = True
    JWT_ACCESS_COOKIE_PATH = "/"
