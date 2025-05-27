import re
import hashlib
import datetime
from database.db_handler import DBHandler

class User:
    def __init__(self, name, email, password):
        if not self.is_valid_email(email):
            raise ValueError("Email inválido.")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener mínimo 8 caracteres.")
        if not (2 <= len(name) <= 50):
            raise ValueError("El nombre debe tener entre 2 y 50 caracteres.")

        self.id = None
        self.name = name
        self.email = email.lower()
        self.password_hash = self.hash_password(password)
        self.created_at = datetime.datetime.utcnow()

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_password(self, password):
        return self.password_hash == self.hash_password(password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at.isoformat()
        }

    @staticmethod
    def is_valid_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    def save(self):
        db = DBHandler()
        # Verificar email único
        existing = db.query("SELECT * FROM users WHERE email = ?", (self.email,), one=True)
        if existing:
            db.close()
            raise ValueError("El email ya está registrado.")
        # Insertar usuario
        self.id = db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (self.name, self.email, self.password_hash)
        )
        db.close()

    @staticmethod
    def find_by_email(email):
        db = DBHandler()
        row = db.query("SELECT * FROM users WHERE email = ?", (email,), one=True)
        db.close()
        if not row:
            return None
        user = User(row["name"], row["email"], "")
        user.id = row["id"]
        user.password_hash = row["password"]
        user.created_at = row["created_at"]
        return user
