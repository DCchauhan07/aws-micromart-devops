from flask import Flask, jsonify

app = Flask(__name__)

PRODUCTS = {
    1: {
        "id": 1,
        "name": "Wireless Mouse",
        "price_cents": 1500,
        "stock": 25
    },
    2: {
        "id": 2,
        "name": "Mechanical Keyboard",
        "price_cents": 4500,
        "stock": 12
    },
    3: {
        "id": 3,
        "name": "USB-C Hub",
        "price_cents": 2999,
        "stock": 20
    }
}


@app.get("/health")
def health():
    return jsonify({
        "service": "product-service",
        "status": "healthy"
    }), 200


@app.get("/products")
def get_products():
    return jsonify(list(PRODUCTS.values())), 200


@app.get("/products/<int:product_id>")
def get_product(product_id):
    product = PRODUCTS.get(product_id)

    if product is None:
        return jsonify({
            "error": "Product not found"
        }), 404

    return jsonify(product), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)


