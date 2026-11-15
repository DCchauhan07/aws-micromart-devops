import os
import sqlite3
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://127.0.0.1:5001"
)

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "/home/ubuntu/micromart/data/orders.db"
)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price_cents INTEGER NOT NULL,
                total_cents INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


@app.get("/health")
def health():
    try:
        with get_connection() as connection:
            connection.execute("SELECT 1")

        return jsonify({
            "service": "order-service",
            "status": "healthy"
        }), 200

    except sqlite3.Error:
        app.logger.exception("Database health check failed")

        return jsonify({
            "service": "order-service",
            "status": "unhealthy"
        }), 503


@app.post("/orders")
def create_order():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    product_id = payload.get("product_id")
    quantity = payload.get("quantity")

    if (
        type(product_id) is not int
        or product_id <= 0
        or type(quantity) is not int
        or not 1 <= quantity <= 10
    ):
        return jsonify({
            "error": "Provide a positive integer product_id and quantity between 1 and 10"
        }), 400

    try:
        response = requests.get(
            f"{PRODUCT_SERVICE_URL}/products/{product_id}",
            timeout=3
        )

    except requests.RequestException:
        app.logger.exception("Product Service unavailable")
        return jsonify({
            "error": "Product Service unavailable"
        }), 503

    if response.status_code == 404:
        return jsonify({
            "error": "Product not found"
        }), 404

    if response.status_code != 200:
        return jsonify({
            "error": "Product lookup failed"
        }), 502

    try:
        product = response.json()

        if (
            type(product["stock"]) is not int
            or type(product["price_cents"]) is not int
            or product["price_cents"] < 0
            or not isinstance(product["name"], str)
        ):
            raise ValueError("Invalid product fields")

    except (ValueError, KeyError, TypeError):
        app.logger.exception("Invalid Product Service response")
        return jsonify({
            "error": "Invalid product data"
        }), 502

    if quantity > product["stock"]:
        return jsonify({
            "error": "Insufficient stock"
        }), 409

    unit_price_cents = product["price_cents"]
    total_cents = unit_price_cents * quantity

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    try:
        with get_connection() as connection:
            cursor = connection.execute("""
                INSERT INTO orders (
                    product_id,
                    product_name,
                    quantity,
                    unit_price_cents,
                    total_cents,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                product["name"],
                quantity,
                unit_price_cents,
                total_cents,
                created_at
            ))

            order_id = cursor.lastrowid

    except sqlite3.Error:
        app.logger.exception("Could not save order")
        return jsonify({
            "error": "Could not save order"
        }), 500

    app.logger.info(
        "Order created: id=%s product_id=%s quantity=%s",
        order_id,
        product_id,
        quantity
    )

    return jsonify({
        "order_id": order_id,
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "total_cents": total_cents,
        "created_at": created_at,
        "status": "created"
    }), 201


@app.get("/orders")
def list_orders():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM orders ORDER BY id DESC"
        ).fetchall()

    return jsonify([dict(row) for row in rows]), 200


@app.get("/orders/<int:order_id>")
def get_order(order_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,)
        ).fetchone()

    if row is None:
        return jsonify({
            "error": "Order not found"
        }), 404

    return jsonify(dict(row)), 200


initialize_database()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=False)
