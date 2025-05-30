import datetime
from models import db
from models.Product import Product

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def __init__(self, user_id):
        self.user_id = user_id
        self.total = 0.0

    def add_item(self, product, quantity):
        if not product:
            raise ValueError("Producto no encontrado.")
        if quantity <= 0:
            raise ValueError("Cantidad inválida.")
        if quantity > product.stock:
            raise ValueError("Stock insuficiente.")

        existing_item = next((item for item in self.items if item.product_id == product.id), None)
        if existing_item:
            existing_item.quantity += quantity
        else:
            self.items.append(OrderItem(product_id=product.id, quantity=quantity))

        self.calculate_total()

    def calculate_total(self):
        subtotal = sum(item.product.price * item.quantity for item in self.items if item.product)
        self.total = round(subtotal * 1.16, 2)  # IVA 16%

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_order_summary(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "total": self.total,
            "created_at": self.created_at.isoformat(),
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.product.name,
                    "price": item.product.price,
                    "quantity": item.quantity
                }
                for item in self.items if item.product
            ]
        }

    @staticmethod
    def find_by_id(order_id):
        return Order.query.filter_by(id=order_id).first()


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product", backref="order_items")

