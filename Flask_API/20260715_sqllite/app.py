# API CRUD 路由表
# /products POST  新增      {"name":"紅茶", "price": 88 }
# /products GET   讀取      INPUT: None
# /products/<id> GET   讀取id


import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)


# 啟動時自動建立資料庫與資料表(如果尚未存在)
def init_db():
    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL
            )                   
    """)
    conn.commit()
    conn.close()


@app.route("/products", methods=["POST"])
def add_product():
    try:
        data = request.get_json(force=False)
        if data is None:
            raise ValueError
    except Exception:
        return jsonify({"error": "請傳送正確的json格式資料"}), 400

    # 從資料中讀取產品名稱與數量
    name = data.get("name")
    price = data.get("price")

    # 資料驗證
    if not name or not price:
        return jsonify({"error": "請提供產品名稱和價格"}), 400
    if not isinstance(name, str):
        return jsonify({"error": "產品名稱必須是文字格式"}), 400
    if not isinstance(price, (int, float)):
        return jsonify({"error": "產品價格必須是數字格式"}), 400

    # 驗證: 價格不能為負數
    if price < 0:
        return jsonify({"error": "產品價格必須不能是負數"}), 400

    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()
    # 確認產品名稱是否已經存在 (name, )參數右邊加上","
    cursor.execute("SELECT name FROM products WHERE name = ?", (name,))
    result = cursor.fetchone()
    if result:
        conn.close()
        return jsonify({"error": "產品名稱已存在，請使用其他名稱"}), 400

    # 連線資料庫 寫入資料

    cursor.execute("INSERT INTO products(name, price) VALUES(?, ?)", (name, price))
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()

    return jsonify(
        {
            "message": "新增產品成功",
            "product": {"id": product_id, "name": name, "price": price},
        }
    )


@app.route("/products", methods=["GET"])
def get_product():
    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    # rows 長這個樣子 {name: "xxx", price: 10} 不是json
    # {id: 1, name: "紅茶01", price: 10}
    # {id: 2, name: "紅茶02", price: 10}
    # {id: 3, name: "紅茶03", price: 10}
    rows = cursor.fetchall()
    conn.close()

    # rows 轉成陣列 ==> 轉成json
    products = []
    for row in rows:
        product = {"id": row[0], "name": row[1], "price": row[2]}
        products.append(product)

    return jsonify({"message": "資料讀取成功", "products": products}), 200


@app.route("/products/<int>", methods=["GET"])
def get_sproduct():
    return jsonify()


@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "test"})


if __name__ == "__main__":
    init_db()
    print("SQLLITE 資料庫已初始化!")
    app.run(debug=True)
