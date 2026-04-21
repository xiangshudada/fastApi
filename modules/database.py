import random
from exceptions import DatabaseConnectionError, RecordNotFoundError

# 模拟数据库中已存在的商品
PRODUCTS_DB = {1, 2, 3}

# 模拟订单存储
ORDERS: list[dict] = []


def get_product(product_id: int) -> dict:
    """查询商品；不存在抛出 RecordNotFoundError"""
    # 模拟 10% 概率连接失败
    if random.random() < 0.1:
        raise DatabaseConnectionError()

    if product_id not in PRODUCTS_DB:
        raise RecordNotFoundError("Product", product_id)

    return {"product_id": product_id, "name": f"商品{product_id}"}


def save_order(user_id: int, product_id: int, quantity: int) -> dict:
    """持久化订单；失败抛出 DatabaseException"""
    if random.random() < 0.1:
        raise DatabaseConnectionError()

    order = {
        "order_id": len(ORDERS) + 1001,
        "user_id": user_id,
        "product_id": product_id,
        "quantity": quantity,
        "status": "created",
    }
    ORDERS.append(order)
    return order
