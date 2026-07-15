from flask import Flask, request, jsonify

app = Flask(__name__)

# 建立一個模擬產品的資料 陣列 products
products = [
    {"id": 1, "name": "伯爵紅茶", "num": 7},
    {"id": 2, "name": "梅子綠茶", "num": 8},
    {"id": 3, "name": "烏龍奶茶", "num": 9},
]

products_dic = {
    1: {"id": 1, "name": "伯爵紅茶", "num": 7},
    2: {"id": 2, "name": "梅子綠茶", "num": 8},
    3: {"id": 3, "name": "烏龍奶茶", "num": 9},
}

name_index = {"伯爵紅茶": 1, "梅子綠茶": 2, "烏龍奶茶": 3}


@app.route("/add_product", methods=["POST"])
def add_product():
    try:
        data = request.get_json(force=False)
        if data is None:
            raise ValueError
    except Exception:
        return jsonify({"error": "請傳送正確的json格式資料"}), 400

    # 從資料中讀取產品名稱與數量
    pname = data.get("pname")
    pnum = data.get("pnum")
    # pstandard = data.get("pstandard")
    # pvolume = data.get("pvolume")

    # 資料驗證
    if not pname or not pnum:
        return jsonify({"error": "請提供產品名稱和數量"}), 400
    # 字串驗證
    if not isinstance(pname, str):
        return jsonify({"error": "產品名稱必須是文字格式"}), 400
    # if not isinstance(pstandard, str):
    #     return jsonify({"error": "產品規格必須是文字格式"}), 400
    # 數字驗證
    if not isinstance(pnum, (int, float)):
        return jsonify({"error": "產品數量必須是數字格式"}), 400
    # if not isinstance(pvolume, (int)):
    #     return jsonify({"error": "產品容量必須是整數格式"}), 400

    # 驗證 : 數量不能為負數
    if pnum < 0:
        return jsonify({"error": "產品數量必須不能是負數"}), 400
    # if pvolume < 0:
    #     return jsonify({"error": "產品容量必須不能是負數"}), 400

    # 驗證 : 產品名稱不能重複
    for p in products:
        if p["name"] == pname:
            return jsonify({"error": "產品名稱已存在，請重新命名"}), 400

    # 將資料加入資料庫 products 並給他一個ID
    product = {
        "id": len(products) + 1,
        "name": pname,
        "num": pnum,
        # "standard": pstandard,
        # "volume": pvolume,
    }

    products.append(product)

    return (
        jsonify({"message": "產品新增成功", "product": product, "products": products}),
        200,
    )


# 讀取產品資料
@app.route("/products", methods=["GET"])
def get_all_products():
    return jsonify({"message": "資料讀取成功", "data": products})


# 讀取單筆產品資料
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return jsonify({"message": "資料讀取成功", "data": product})

    return jsonify({"message": "查無資料"})


# 更新資料 PUT
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    try:
        data = request.get_json(force=False)
        if data is None:
            raise ValueError
    except Exception:
        return jsonify({"error": "請傳送正確的json格式資料"}), 400

    # 從資料中讀取產品名稱與數量
    pname = data.get("pname")
    pnum = data.get("pnum")
    # pstandard = data.get("pstandard")
    # pvolume = data.get("pvolume")

    if not pname or not pnum:
        return jsonify({"error": "請提供產品名稱和數量"}), 400
    if not isinstance(pname, str):
        return jsonify({"error": "產品名稱必須是文字格式"}), 400
    if not isinstance(pnum, (int, float)):
        return jsonify({"error": "產品數量必須是數字格式"}), 400

    if pnum < 0:
        return jsonify({"error": "產品數量必須不能是負數"}), 400

    for product in products:
        if product["id"] == product_id:
            # 檢查產品名稱是否與其他產品重複
            for p in products:
                if p["name"] == pname and p["id"] != product_id:
                    return jsonify({"message": "產品名稱存在，請重新命名。"}), 400

            product["name"] = pname
            product["num"] = pnum
            return (
                jsonify(
                    {
                        "message": "產品更新成功。",
                        "product": product,
                        "products": products,
                    }
                ),
                200,
            )

    return jsonify({"message": "找不到此產品"}), 400


# 更新資料 PATCH
@app.route("/products/<int:product_id>", methods=["PATCH"])
def patch_product(product_id):
    try:
        data = request.get_json(force=False)
        if data is None:
            raise ValueError
    except Exception:
        return jsonify({"error": "請傳送正確的json格式資料"}), 400

    # 至少提供一個欄位
    if "pname" not in data and "pnum" not in data:
        return jsonify({"error": "請至少提供一個欄位"})

    # 尋找指定更新的產品
    # for product in products:
    #     if product["id"] == product_id:
    # 修改產品名稱
    # if "pname" in data:
    #     pname = data.get("pname")
    #     if pname is None:
    #         return jsonify({"error": "請提供產品名稱和數量"}), 400
    #     if not isinstance(pname, str):
    #         return jsonify({"error": "產品名稱必須是文字格式"}), 400

    #     # 檢查產品名稱
    #     for p in products:
    #         if p["name"] == pname and p["id"] != product_id:
    #             return jsonify({"message": "產品名稱存在，請重新命名。"}), 400

    #     product["name"] = pname

    # 修改產品數量
    # if "pnum" in data:
    #     pnum = data.get("pnum")
    #     if pnum is None:
    #         return jsonify({"error": "請提供產品數量"}), 400
    #     if not isinstance(pnum, (int, float)):
    #         return jsonify({"error": "產品數量必須是數字格式"}), 400
    #     if pnum < 0:
    #         return jsonify({"error": "產品數量必須不能是負數"}), 400

    #     product["num"] = pnum

    # 資料修改完回傳
    # return (
    #     jsonify(
    #         {
    #             "message": "產品更新成功。",
    #             "product": product,
    #             "products": products,
    #         }
    #     ),
    #     200,
    # )

    # dictionary
    product = products_dic.get(product_id)

    if product is None:
        return jsonify({"error": "請至少提供一個欄位"}), 400

    if "pname" in data:
        pname = data.get("pname")
        if pname is None:
            return jsonify({"error": "請提供產品名稱和數量"}), 400
        if not isinstance(pname, str):
            return jsonify({"error": "產品名稱必須是文字格式"}), 400

        if pname in name_index and name_index[pname] != product_id:
            return jsonify({"message": "產品名稱存在，請重新命名。"}), 400

        product["name"] = pname

    if "pnum" in data:
        pnum = data.get("pnum")
        if pnum is None:
            return jsonify({"error": "請提供產品數量"}), 400
        if not isinstance(pnum, (int, float)):
            return jsonify({"error": "產品數量必須是數字格式"}), 400
        if pnum < 0:
            return jsonify({"error": "產品數量必須不能是負數"}), 400

        product["num"] = pnum

    return (
        jsonify(
            {
                "message": "產品更新成功。",
                "product": product,
                "products": products_dic,
            }
        ),
        200,
    )

    # return jsonify({"error": "查無此產品"}), 400


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    # 尋找要刪除的產品
    for product in products:
        if product["id"] == product_id:
            products.remove(product)
            return (
                jsonify(
                    {
                        "message": "產品刪除成功",
                        "product": product,
                        "products": products,
                    }
                ),
                200,
            )

    return jsonify({"error": "查無此產品"}), 400


@app.route("/test")
def test():
    return "app is working!"


if __name__ == "__main__":
    app.run(debug=True)
