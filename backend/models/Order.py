import datetime
from database.db_handler import DBHandler
from models.Product import Product

class Order:
    VALID_STATUSES = {"pending", "confirmed", "shipped", "delivered", "cancelled"}

    def __init__(self, user_id, shipping_address):
        self.id = None
        self.user_id = user_id
        self.items = []  # Lista de dicts: {"product": Product, "quantity": int}
        self.total = 0.0
        self.status = "pending"
        self.created_at = datetime.datetime.utcnow()
        self.shipping_address = shipping_address

    def add_item(self, product, quantity):
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        if quantity > product.stock:
            raise ValueError("No hay stock suficiente para este producto.")
        self.items.append({"product": product, "quantity": quantity})
        self.calculate_total()

    def remove_item(self, product_id):
        self.items = [item for item in self.items if item["product"].id != product_id]
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
            "created_at": self.created_at.isoformat(),
            "shipping_address": self.shipping_address
        }

    def save(self):
        db = DBHandler()
        if self.id is None:
            self.id = db.execute(
                "INSERT INTO orders (user_id, total, status, created_at, shipping_address) VALUES (?, ?, ?, ?, ?)",
                (self.user_id, self.total, self.status, self.created_at, self.shipping_address)
            )
            for item in self.items:
                db.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
                    (self.id, item["product"].id, item["quantity"])
                )
        else:
            # Actualizar orden y sus items si fuera necesario
            pass
        db.close()

    @staticmethod
    def find_by_id(order_id):
        db = DBHandler()
        row = db.query("SELECT * FROM orders WHERE id = ?", (order_id,), one=True)
        if not row:
            db.close()
            return None
        order = Order(row["user_id"], row["shipping_address"])
        order.id = row["id"]
        order.total = row["total"]
        order.status = row["status"]
        order.created_at = row["created_at"]
        items_rows = db.query("SELECT * FROM order_items WHERE order_id = ?", (order.id,))
        for item_row in items_rows:
            product = Product.find_by_id(item_row["product_id"])
            if product:
                order.items.append({"product": product, "quantity": item_row["quantity"]})
        db.close()
        return order
