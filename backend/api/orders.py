from flask import Blueprint, request, jsonify
from models.Order import Order
from models.Product import Product
from flask_jwt_extended import jwt_required

orders_bp = Blueprint('orders', __name__)

@orders_bp.route("/", methods=["POST"])
@jwt_required()
def create_order():
    data = request.get_json()
    user_id = data.get("user_id")
    items = data.get("items", [])

    if not user_id or not items:
        return jsonify({"error": "user_id y items son requeridos"}), 400

    order = Order(user_id=user_id)

    for item in items:
        product = Product.find_by_id(item["product_id"])
        quantity = item["quantity"]
        try:
            order.add_item(product, quantity)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    order.save()
    return jsonify(order.get_order_summary()), 201

@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.find_by_id(order_id)
    if order:
        return jsonify(order.get_order_summary())
    return jsonify({"error": "Orden no encontrada"}), 404
