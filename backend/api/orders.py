from flask import Blueprint, request, jsonify
from models.Order import Order
from models.Product import Product

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['POST'])
def create_order():
    data = request.json
    try:
        order = Order(data['user_id'], data['shipping_address'])
        for item in data['items']:
            product = Product.find_by_id(item['product_id'])
            if not product:
                return jsonify({"error": f"Producto {item['product_id']} no encontrado"}), 404
            order.add_item(product, item['quantity'])
        order.process_order()
        return jsonify({"message": "Orden creada", "order": order.get_order_summary()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.find_by_id(order_id)
    if order:
        return jsonify(order.get_order_summary())
    return jsonify({"error": "Orden no encontrada"}), 404
