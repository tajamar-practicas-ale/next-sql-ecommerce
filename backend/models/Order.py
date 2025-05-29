import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from models.product import Product

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    items_json = db.Column(db.Text, nullable=False, default='[]')  # Guardar lista de items serializados
    total = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    shipping_address = db.Column(db.String(255), nullable=False)

    VALID_STATUSES = {"pending", "confirmed", "shipped", "delivered", "cancelled"}

    def __init__(self, user_id, shipping_address):
        self.user_id = user_id
        self.items = []  # Lista de dicts {"product": Product, "quantity": int}
        self.total = 0.0
        self.status = "pending"
        self.created_at = datetime.datetime.utcnow()
        self.shipping_address = shipping_address
        self.items_json = json.dumps([])

    @property
    def items(self):
        raw_items = json.loads(self.items_json)
        # Reconstruir productos
        result = []
        for item in raw_items:
            product = Product.find_by_id(item['product_id'])
            if product:
                result.append({"product": product, "quantity": item['quantity']})
        return result

    @items.setter
    def items(self, value):
        # Espera lista de dicts con "product" y "quantity"
        raw_items = []
        for item in value:
            raw_items.append({"product_id": item["product"].id, "quantity": item["quantity"]})
        self.items_json = json.dumps(raw_items)

    def add_item(self, product, quantity):
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        if quantity > product.stock:
            raise ValueError("No hay stock suficiente para este producto.")
        current_items = self.items
        # Añadir o actualizar cantidad
        found = False
        for item in current_items:
            if item["product"].id == product.id:
                item["quantity"] += quantity
                found = True
                break
        if not found:
            current_items.append({"product": product, "quantity": quantity})
        self.items = current_items
        self.calculate_total()

    def remove_item(self, product_id):
        current_items = [item for item in self.items if item["product"].id != product_id]
        self.items = current_items
        self.calculate_total()

    def calculate_total(self):
        subtotal = sum(item["product"].price * item["quantity"] for item in self.items)
        self.total = round(subtotal * 1.16, 2)  # IVA 16%

    def process_order(self):
        for item in self.items:
            item["product"].reserve_stock(item["quantity"])
        self.status = "confirmed"
        self.save()

    def cancel_order(self):
        if self.status not in {"pending", "confirmed"}:
            raise ValueError("No se puede cancelar esta orden en su estado actual.")
        for item in self.items:
            item["product"].release_stock(item["quantity"])
        self.status = "cancelled"
        self.save()

    def get_order_summary(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "items": [
                {
                    "product_id": item["product"].id,
                    "name": item["product"].name,
                    "quantity": item["quantity"],
                    "price": item["product"].price
                } for item in self.items
            ],
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "shipping_address": self.shipping_address
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def find_by_id(order_id):
        return Order.query.filter_by(id=order_id).first()
