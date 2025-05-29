import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "ecommerce.db"

class DBHandler:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def create_tables(self):
        with open(Path(__file__).parent / "schema.sql", "r", encoding="utf-8") as f:
            sql_script = f.read()
            self.cursor.executescript(sql_script)
            self.connection.commit()

    def query(self, query, params=(), one=False):
        self.cursor.execute(query, params)
        result = self.cursor.fetchall()
        return (result[0] if result else None) if one else result

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.lastrowid

    def initialize_products(self):
        from models.Product import Product

        if Product.query.count() == 0:
            productos = [
                Product(name="Teclado Retro Mecánico", description="Teclado mecánico con estilo retro y switches azules.", price=79.99, stock=20, category="Periféricos", image_name="teclado-retro.jpg", is_active=True),
                Product(name="Mouse Ergonómico Inalámbrico", description="Mouse inalámbrico con diseño ergonómico y batería recargable.", price=49.99, stock=15, category="Periféricos", image_name="mouse-ergonomico.jpg", is_active=True),
                Product(name="Auriculares Gamer RGB", description="Auriculares con sonido envolvente 7.1 y luces RGB.", price=59.99, stock=10, category="Audio", image_name="auriculares-rgb.jpg", is_active=True),
            ]
            db.session.bulk_save_objects(productos)
            db.session.commit()

    def close(self):
        self.connection.close()
