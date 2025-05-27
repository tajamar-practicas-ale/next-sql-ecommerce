import re
from database.db_handler import DBHandler

class Product:
    def __init__(self, name, description, price, stock, category, image_name, is_active=True):
        if price <= 0:
            raise ValueError("El precio debe ser mayor que 0.")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")
        if not name:
            raise ValueError("El nombre es obligatorio.")
        if not self.is_valid_image_name(image_name):
            raise ValueError("El nombre de imagen no es válido.")

        self.id = None
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.category = category
        self.image_name = image_name
        self.is_active = is_active

    @staticmethod
    def is_valid_image_name(name):
        # Validar que termine en extensión de imagen común
        return bool(re.match(r'.+\.(jpg|jpeg|png|gif)$', name, re.IGNORECASE))

    def update_stock(self, amount):
        if self.stock + amount < 0:
            raise ValueError("Stock insuficiente para esta operación.")
        self.stock += amount
        self._save_stock()

    def reserve_stock(self, quantity):
        if quantity > self.stock:
            raise ValueError("No hay suficiente stock para reservar.")
        self.stock -= quantity
        self._save_stock()

    def release_stock(self, quantity):
        self.stock += quantity
        self._save_stock()

    def _save_stock(self):
        db = DBHandler()
        db.execute(
            "UPDATE products SET stock = ? WHERE id = ?",
            (self.stock, self.id)
        )
        db.close()

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
        db = DBHandler()
        row = db.query("SELECT * FROM products WHERE id = ? AND is_active = 1", (product_id,), one=True)
        db.close()
        if not row:
            return None
        product = Product(
            row["name"], row["description"], row["price"], row["stock"],
            row["category"], row["image_name"], bool(row["is_active"])
        )
        product.id = row["id"]
        return product

    @staticmethod
    def find_all_active():
        db = DBHandler()
        rows = db.query("SELECT * FROM products WHERE is_active = 1")
        db.close()
        products = []
        for row in rows:
            p = Product(
                row["name"], row["description"], row["price"], row["stock"],
                row["category"], row["image_name"], bool(row["is_active"])
            )
            p.id = row["id"]
            products.append(p)
        return products

    @staticmethod
    def calculate_total_value():
        db = DBHandler()
        rows = db.query("SELECT price, stock FROM products WHERE is_active = 1")
        db.close()
        total = sum(row["price"] * row["stock"] for row in rows)
        return total
