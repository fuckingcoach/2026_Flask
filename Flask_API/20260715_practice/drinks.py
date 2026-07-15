from flask import Flask, request, jsonify
from datetime import datetime

drink = Flask(__name__)

products = {
    "P001aBcD001": {
        "pname": "可可亞",
        "pnum": 3,
        "pstandard": "少糖",
        "pvolume": "大(1000cc-2000cc)",
        "pstatus": "上架",
        "topping": "仙草、珍珠",
        "supply": "冷飲",
        "price": 135,
        "create_at": "2026/05/22 11:45:10",
        "id": "P001aBcD001",
    },
    "P002aBcD002": {
        "pname": "摩卡",
        "pnum": 10,
        "pstandard": "半糖",
        "pvolume": "小(500cc以下)",
        "pstatus": "上架",
        "topping": "椰果",
        "supply": "熱飲",
        "price": 30,
        "create_at": "2026/05/23 12:30:22",
        "id": "P002aBcD002",
    },
    "P003aBcD003": {
        "pname": "美式咖啡",
        "pnum": 2,
        "pstandard": "正常",
        "pvolume": "大(1000cc-2000cc)",
        "pstatus": "上架",
        "topping": "仙草、椰果",
        "supply": "冷飲",
        "price": 80,
        "create_at": "2026/05/24 13:10:55",
        "id": "P003aBcD003",
    },
}

name_index = {"可可亞": "P001aBcD001", "摩卡": "P002aBcD002", "美式咖啡": "P003aBcD003"}

volumelist = {
    "⼩(500cc以下)": 1,
    "中(500cc-1000cc)": 2,
    "⼤(1000cc-2000cc)": 3,
    "特⼤(2000cc以上)": 4,
}

statuslist = {"上架": 1, "下架": 2}

supplylist = {"冷飲": 1, "熱飲": 2, "冷熱皆可": 3}


@drink.route("/products", methods=["GET"])
def getallproducts():
    return jsonify({"message": "查詢全部產品成功", "products": products}), 200


@drink.route("/products/<string:product_id>", methods=["GET"])
def getproduct(product_id):
    product = products.get(product_id)
    if product is None:
        return jsonify({"error": "查無此產品"}), 404
    return jsonify({"message": "查詢產品成功", "product": product}), 200


@drink.route("/products", methods=["POST"])
def addproduct():
    try:
        data = request.get_json(force=False)
        if data is None:
            raise ValueError
    except Exception:
        return jsonify({"error": "請傳送正確的json格式資料"}), 400

    check_response = checkdata(data)
    if check_response is None:
        global products, name_index

        pname = data.get("pname")
        pnum = data.get("pnum")
        price = data.get("price")
        pstandard = data.get("pstandard")
        pstatus = data.get("pstatus")
        pvolume = data.get("pvolume")
        topping = data.get("topping")
        supply = data.get("supply")

        indexname = name_index.get(pname)
        if indexname is not None:
            return jsonify({"error": "產品名稱重複，請輸入不同的產品名稱"}), 400

        newid = f"P{len(products) + 1:03d}aBcD{len(products) + 1:03d}"

        product = {
            "pname": pname,
            "pnum": pnum,
            "pstandard": pstandard,
            "pvolume": pvolume,
            "pstatus": pstatus,
            "topping": topping,
            "supply": supply,
            "price": price,
            "create_at": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "id": newid,
        }

        products[newid] = product
        name_index[pname] = newid

        return (
            jsonify(
                {
                    "message": "新增成功 !",
                    "product": product,
                    "products": products,
                    "index": name_index,
                }
            ),
            201,
        )

    return check_response


@drink.route("/products/<string:product_id>", methods=["PUT"])
def updateproduct(product_id):
    try:
        data = request.get_json(force=False)
        if data is None:
            raise ValueError
    except Exception:
        return jsonify({"error": "請傳送正確的json格式資料"}), 400

    check_response = checkdata(data)

    if check_response is None:
        global products, name_index

        product = products.get(product_id)
        if product is None:
            return jsonify({"error": "查無此產品"}), 404

        pname = data.get("pname")
        pnum = data.get("pnum")
        price = data.get("price")
        pstandard = data.get("pstandard")
        pstatus = data.get("pstatus")
        pvolume = data.get("pvolume")
        topping = data.get("topping")
        supply = data.get("supply")

        if pname in name_index and name_index[pname] != product_id:
            return jsonify({"error": "產品名稱重複，請輸入不同的產品名稱"}), 400

        product["pname"] = pname
        product["pnum"] = pnum
        product["price"] = price
        product["pstandard"] = pstandard
        product["pstatus"] = pstatus
        product["pvolume"] = pvolume
        product["topping"] = topping
        product["supply"] = supply

        name_index[pname] = product_id

        return (
            jsonify(
                {
                    "messgae": "修改資料成功",
                    "product": product,
                    "products": products,
                    "nameindex": name_index,
                }
            ),
            200,
        )

    return check_response


@drink.route("/products/<string:product_id>", methods=["PATCH"])
def updatefield(product_id):
    try:
        data = request.get_json(force=False)
        if data is None:
            raise ValueError
    except Exception:
        return jsonify({"error": "請傳送正確的json格式資料"}), 400

    product = products.get(product_id)
    if product is None:
        return jsonify({"error": "查無此產品"}), 404

    if "pname" in data:
        pname = data.get("pname")
        if pname is None:
            return jsonify({"error": "請提供產品名稱"}), 400
        if not isinstance(pname, str):
            return jsonify({"error": "產品名稱必須是文字格式"}), 400
        if pname in name_index and name_index[pname] != product_id:
            return jsonify({"error": "產品名稱重複，請輸入不同的產品名稱"}), 400

        name_index.pop(product["pname"])
        name_index[pname] = product["id"]
        product["pname"] = pname

    if "pnum" in data:
        pnum = data.get("pnum")
        if pnum is None:
            return jsonify({"error": "請提供產品數量"}), 400
        if not isinstance(pnum, int):
            return jsonify({"error": "產品數量必須為整數"}), 400
        if pnum < 0:
            return jsonify({"error": "產品數量必須不能是負數"}), 400

        product["pnum"] = pnum

    if "price" in data:
        price = data.get("price")
        if price is None:
            return jsonify({"error": "請提供產品價格"}), 400
        if not isinstance(price, int):
            return jsonify({"error": "產品價格必須為整數"}), 400
        if price < 0:
            return jsonify({"error": "產品價格必須不能是負數"}), 400

        product["price"] = price

    if "pstandard" in data:
        pstandard = data.get("pstandard")
        if pstandard is None:
            return jsonify({"error": "請提供產品規格"}), 400
        if not isinstance(pstandard, str):
            return jsonify({"error": "產品規格必須是文字格式"}), 400

        product["pstandard"] = pstandard

    if "pstatus" in data:
        pstatus = data.get("pstatus")
        if pstatus is None:
            return jsonify({"error": "請提供上架狀態"}), 400
        if not isinstance(pstatus, str):
            return jsonify({"error": "上架狀態必須是文字格式"}), 400
        product["pstatus"] = pstatus

    if "pvolume" in data:
        pvolume = data.get("pvolume")
        if pvolume is None:
            return jsonify({"error": "請提供產品容量"}), 400
        if not isinstance(pvolume, str):
            return jsonify({"error": "產品容量必須是文字格式"}), 400

        product["pvolume"] = pvolume

    if "topping" in data:
        topping = data.get("topping")
        if topping is None:
            return jsonify({"error": "請提供產品配料"}), 400
        if not isinstance(topping, str):
            return jsonify({"error": "產品配料必須是文字格式"}), 400

        product["topping"] = topping

    if "supply" in data:
        supply = data.get("supply")
        if supply is None:
            return jsonify({"error": "請提供產品供應方式"}), 400
        if not isinstance(supply, str):
            return jsonify({"error": "產品供應方式必須是文字格式"}), 400
        product["supply"] = supply

    return (
        jsonify(
            {
                "messgae": "修改欄位成功",
                "product": product,
                "products": products,
                "nameindex": name_index,
            }
        ),
        200,
    )


@drink.route("/products/<string:product_id>", methods=["DELETE"])
def deleteproduct(product_id):

    product = products.get(product_id)
    if product is None:
        return jsonify({"error": "查無此產品"}), 404

    name_index.pop(product["pname"])
    products.pop(product_id)

    return (
        jsonify(
            {
                "messgae": "刪除成功",
                "product": product,
                "products": products,
                "nameindex": name_index,
            }
        ),
        200,
    )


@drink.route("/test")
def test():
    return "app is working!"


def checkdata(data):
    global name_index, volumelist, supplylist, statuslist

    pname = data.get("pname")
    pnum = data.get("pnum")
    price = data.get("price")
    pstandard = data.get("pstandard")
    pstatus = data.get("pstatus")
    pvolume = data.get("pvolume")
    topping = data.get("topping")
    supply = data.get("supply")

    if (
        pname is None
        or pnum is None
        or price is None
        or pstandard is None
        or pstatus is None
        or pvolume is None
        or topping is None
        or supply is None
    ):
        return jsonify({"error": "請輸入完整的產品欄位"}), 400

    if pname is None:
        return jsonify({"error": "請提供產品名稱"}), 400
    if not isinstance(pname, str):
        return jsonify({"error": "產品名稱必須是文字格式"}), 400
    if pnum is None:
        return jsonify({"error": "請提供產品數量"}), 400
    if not isinstance(pnum, int):
        return jsonify({"error": "產品數量必須為整數"}), 400
    if price is None:
        return jsonify({"error": "請提供產品價格"}), 400
    if not isinstance(price, int):
        return jsonify({"error": "產品價格必須為整數"}), 400
    if pstandard is None:
        return jsonify({"error": "請提供產品規格"}), 400
    if not isinstance(pstandard, str):
        return jsonify({"error": "產品規格必須是文字格式"}), 400
    if pstatus is None:
        return jsonify({"error": "請提供上架狀態"}), 400
    if statuslist.get(pstatus) is None:
        return jsonify({"error": "請輸入正確的上架狀態 : 上架/下架"}), 400
    if pvolume is None:
        return jsonify({"error": "請提供產品容量"}), 400
    if volumelist.get(pvolume) is None:
        return (
            jsonify(
                {
                    "error": "請輸入正確的產品容量 : ⼩(500cc以下)/中(500cc-1000cc)/⼤(1000cc-2000cc)/特⼤(2000cc以上)"
                }
            ),
            400,
        )
    if topping is None:
        return jsonify({"error": "請提供產品配料"}), 400
    if not isinstance(topping, str):
        return jsonify({"error": "產品配料必須是文字格式"}), 400
    if supply is None:
        return jsonify({"error": "請提供產品供應方式"}), 400
    if supplylist.get(supply) is None:
        return jsonify({"error": "請輸入正確的產品供應方式 : 冷飲/熱飲/冷熱皆可"}), 400

    if pnum < 0:
        return jsonify({"error": "產品數量必須不能是負數"}), 400
    if price < 0:
        return jsonify({"error": "產品價格必須不能是負數"}), 400

    return None


if __name__ == "__main__":
    drink.run(debug=True)
