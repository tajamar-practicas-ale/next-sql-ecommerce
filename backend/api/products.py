from flask import Blueprint, request, jsonify
from models.Product import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def list_products():
    products = Product.find_all_active()
    return jsonify([p.to_dict() for p in products])

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.find_by_id(product_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({"error": "Producto no encontrado"}), 404
