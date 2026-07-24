# API CRUD 路由表
# /products      POST   新增      INPUT: {"name":"紅茶", "price": 88 }
# /products      GET    讀取      INPUT: None
# /products/:id  PUT    更新全部  INPUT: {"name":"紅茶", "price": 88 }
# /products/:id  DELETE 刪除      INPUT: None

# practice
# /products/:id     GET    讀取id
# /products/:id     PATCH  更新欄位  INPUT: {"name":"紅茶" or "price": 88 }
# /products/:name   GET    指定讀取
# /products/?price=price  GET    指定讀取


import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


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

    return (
        jsonify(
            {
                "message": "新增產品成功",
                "product": {"id": product_id, "name": name, "price": price},
            }
        ),
        200,
    )


@app.route("/products", methods=["GET"])
def get_product():
    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()

    price_str = request.args.get("price")
    try:
        price = float(price_str)
    except ValueError:
        conn.close()
        return jsonify({"error": "產品價格必須是數字格式"}), 400
    # 路由查詢價格
    if price is not None:
        if price < 0:
            conn.close()
            return jsonify({"error": "產品價格必須不能是負數"}), 400

        cursor.execute("SELECT id, name, price FROM products WHERE price = ?", (price,))
        result = cursor.fetchall()
        if not result:
            return jsonify({"message": "查無此產品價格!"}), 400

        # rows 轉成陣列 ==> 轉成json
        products = []
        for row in result:
            product = {"id": row[0], "name": row[1], "price": row[2]}
            products.append(product)
        return (
            jsonify(
                {
                    "message": "產品價格查詢成功",
                    "products": products,
                }
            ),
            200,
        )

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


@app.route("/products/<int:product_id>", methods=["GET"])
def get_sproduct(product_id):
    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return jsonify({"error": "產品不存在!"}), 400

    cursor.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()

    return (
        jsonify(
            {
                "message": "查詢產品成功",
                "product": {"id": row[0], "name": row[1], "price": row[2]},
            }
        ),
        200,
    )


@app.route("/products/<string:name>", methods=["GET"])
def get_product_name(name):
    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()

    if not name:
        return jsonify({"error": "請提供產品名稱"}), 400
    if not isinstance(name, str):
        conn.close()
        return jsonify({"error": "產品名稱必須是文字格式"}), 400

    cursor.execute("SELECT id, name, price FROM products WHERE name = ?", (name,))
    result = cursor.fetchone()
    if result is None:
        return jsonify({"message": "查無此產品名稱!"}), 400
    conn.close()
    return (
        jsonify(
            {
                "message": "產品名稱查詢成功",
                "product": {"id": result[0], "name": result[1], "price": result[2]},
            }
        ),
        200,
    )


# 更新產品 PUT
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
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

    # 連線資料庫 執行更新
    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()

    # 確認更新產品是否存在 (id是否存在)
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return jsonify({"error": "產品不存在!"}), 400

    # 產品名稱是否已經存在
    cursor.execute(
        "SELECT id FROM products WHERE name = ? AND id != ?", (name, product_id)
    )
    result = cursor.fetchone()
    if result:
        conn.close()
        return jsonify({"error": "產品名稱請勿重複!"}), 400

    # 執行更新
    cursor.execute(
        "UPDATE products SET name = ?, price = ? WHERE id = ?",
        (name, price, product_id),
    )
    conn.commit()
    conn.close()

    return (
        jsonify(
            {
                "message": "更新產品成功",
                "product": {"id": product_id, "name": name, "price": price},
            }
        ),
        200,
    )


@app.route("/products/<int:product_id>", methods=["PATCH"])
def update_productfield(product_id):
    try:
        data = request.get_json(force=False)
        if data is None:
            raise ValueError
    except Exception:
        return jsonify({"error": "請傳送正確的json格式資料"}), 400

    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()

    # 產品名稱是否已經存在
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return jsonify({"error": "產品不存在!"}), 400

    # 從資料中讀取產品名稱與數量
    name = data.get("name")
    price = data.get("price")
    flag = False

    # 名稱驗證
    if name:
        if not isinstance(name, str):
            conn.close()
            return jsonify({"error": "產品名稱必須是文字格式"}), 400

        # 產品名稱是否已經存在
        cursor.execute(
            "SELECT id FROM products WHERE name = ? AND id != ?", (name, product_id)
        )
        result = cursor.fetchone()
        if result:
            conn.close()
            return jsonify({"error": "產品名稱請勿重複!"}), 400

        cursor.execute("UPDATE products SET name = ? WHERE id = ?", (name, product_id))
        conn.commit()
        flag = True

    # 驗證價格
    if price is not None:
        if not isinstance(price, (int, float)):
            conn.close()
            return jsonify({"error": "產品價格必須是數字格式"}), 400

        if price < 0:
            conn.close()
            return jsonify({"error": "產品價格必須不能是負數"}), 400

        cursor.execute(
            "UPDATE products SET price = ? WHERE id = ?", (price, product_id)
        )
        conn.commit()
        flag = True

    conn.close()

    if flag:
        return (
            jsonify(
                {
                    "message": "更新產品成功",
                    "product": {"id": product_id, "name": name, "price": price},
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "未更新"}), 400


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    # 連線資料庫 執行更新
    conn = sqlite3.connect("product.db")
    cursor = conn.cursor()

    # 確認更新產品是否存在 (id是否存在)
    cursor.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return jsonify({"error": "查無此產品產品!"}), 400

    # 執行刪除
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

    return (
        jsonify(
            {
                "message": "產品刪除成功!",
                "product": {"id": result[0], "name": result[1], "price": result[2]},
            }
        ),
        200,
    )


@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "test"})


if __name__ == "__main__":
    init_db()
    print("SQLLITE 資料庫已初始化!")
    app.run(host="0.0.0.0", port=5000, debug=True)
