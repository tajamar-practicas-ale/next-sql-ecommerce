import re
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from models import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self, name, email, password):
        if not self.is_valid_email(email):
            raise ValueError("Email inválido.")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres.")
        if not (2 <= len(name) <= 50):
            raise ValueError("El nombre debe tener entre 2 y 50 caracteres.")

        self.name = name
        self.email = email.lower()
        self.password_hash = generate_password_hash(password)

    # @staticmethod
    # def hash_password(password):
    #     return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def is_valid_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def save(self):
        existing = User.query.filter_by(email=self.email).first()
        if existing:
            raise ValueError("El email ya está registrado.")
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email.lower()).first()
