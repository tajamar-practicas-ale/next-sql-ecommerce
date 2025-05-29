import re
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50))
    image_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, name, description, price, stock, category, image_name, is_active=True):
        if price <= 0:
            raise ValueError("El precio debe ser mayor que 0.")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")
        if not name:
            raise ValueError("El nombre es obligatorio.")
        if not self.is_valid_image_name(image_name):
            raise ValueError("El nombre de imagen no es válido.")

        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.category = category
        self.image_name = image_name
        self.is_active = is_active

    @staticmethod
    def is_valid_image_name(name):
        return bool(re.match(r'.+\.(jpg|jpeg|png|gif)$', name, re.IGNORECASE))

    def update_stock(self, amount):
        if self.stock + amount < 0:
            raise ValueError("Stock insuficiente para esta operación.")
        self.stock += amount
        self.save()

    def reserve_stock(self, quantity):
        if quantity > self.stock:
            raise ValueError("No hay suficiente stock para reservar.")
        self.stock -= quantity
        self.save()

    def release_stock(self, quantity):
        self.stock += quantity
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "stock": self.stock,
            "category": self.category,
            "image_name": self.image_name,
            "is_active": self.is_active
        }

    @staticmethod
    def find_by_id(product_id):
        return Product.query.filter_by(id=product_id, is_active=True).first()

    @staticmethod
    def find_all_active():
        return Product.query.filter_by(is_active=True).all()

    @staticmethod
    def calculate_total_value():
        products = Product.query.filter_by(is_active=True).all()
        total = sum(p.price * p.stock for p in products)
        return total
