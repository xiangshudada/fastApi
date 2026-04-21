from exceptions import InsufficientStockError, OrderLimitExceededError

ORDER_MAX_QUANTITY = 10  # 单次最多购买件数

# 模拟商品库存
STOCK = {
    1: 5,   # 商品1 库存5件
    2: 100, # 商品2 库存充足
    3: 0,   # 商品3 无库存
}


def validate_order(product_id: int, quantity: int) -> None:
    """业务规则校验；违规则抛出 BusinessException"""
    if quantity > ORDER_MAX_QUANTITY:
        raise OrderLimitExceededError(ORDER_MAX_QUANTITY)

    available = STOCK.get(product_id, 0)
    if quantity > available:
        raise InsufficientStockError(product_id, quantity, available)


def deduct_stock(product_id: int, quantity: int) -> None:
    """扣减库存（业务操作，调用前须已通过 validate_order）"""
    STOCK[product_id] -= quantity
