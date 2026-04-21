import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Header
from pydantic import BaseModel, Field

from exceptions import (
    AuthException, BusinessException, DatabaseException,
    auth_exception_handler, business_exception_handler, database_exception_handler,
)
from modules.auth import verify_token, require_role
from modules.business import validate_order, deduct_stock
from modules.database import get_product, save_order

app = FastAPI(title="自定义异常 Demo")

# 注册全局异常处理器
app.add_exception_handler(AuthException, auth_exception_handler)
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)


class OrderRequest(BaseModel):
    product_id: int = Field(..., examples=[1], description="商品ID (1=库存5, 2=充足, 3=无库存, 99=不存在)")
    quantity: int = Field(..., ge=1, examples=[2], description="购买数量")


class OrderResponse(BaseModel):
    order_id: int
    user_id: int
    product_id: int
    quantity: int
    status: str


@app.post("/orders", response_model=OrderResponse, summary="创建订单")
def create_order(
    body: OrderRequest,
    x_token: str = Header(..., description="认证 Token"),
):
    """
    下单流程，依次经过三个模块层：

    | 模块       | 异常类型              | 触发场景                          |
    |------------|----------------------|----------------------------------|
    | auth       | AuthException        | token 无效 / 无权限               |
    | business   | BusinessException    | 超购上限 / 库存不足               |
    | database   | DatabaseException    | 商品不存在 / DB 连接失败（随机）   |

    **测试用 Token：**
    - `user-token-abc`  — 普通用户（有下单权限）
    - `admin-token-xyz` — 管理员
    - `expired-token-123` — 已过期 → 触发 TokenExpiredError
    - 其他任意字符串  → 触发 TokenExpiredError
    """

    # ── 层1: 认证模块 ─────────────────────────────────────────
    user = verify_token(x_token)          # 可抛 TokenExpiredError
    require_role(user, "user", "orders")  # 可抛 PermissionDeniedError

    # ── 层3(先查): 数据库模块 — 确认商品存在 ─────────────────
    product = get_product(body.product_id)  # 可抛 RecordNotFoundError / DatabaseConnectionError

    # ── 层2: 业务模块 — 在确认商品存在后做规则校验 ────────────
    validate_order(body.product_id, body.quantity)  # 可抛 InsufficientStockError / OrderLimitExceededError

    # ── 层3(再写): 数据库模块 — 持久化订单 ───────────────────
    order = save_order(user["user_id"], product["product_id"], body.quantity)

    # 扣减库存（全部持久化成功后再扣）
    deduct_stock(body.product_id, body.quantity)

    return order


@app.get("/", summary="触发场景速查")
def index():
    return {
        "触发 TokenExpiredError (401)":       "Header x-token: expired-token-123",
        "触发 PermissionDeniedError (401)":   "暂无只读角色，可在 auth.py 扩展",
        "触发 OrderLimitExceededError (422)":  "quantity > 10",
        "触发 InsufficientStockError (422)":   "product_id=1, quantity=6 (库存仅5)",
        "触发 RecordNotFoundError (503)":      "product_id=99 (不存在)",
        "触发 DatabaseConnectionError (503)":  "随机10%概率，多试几次",
        "正常成功":                             "product_id=2, quantity=3, token=user-token-abc",
    }
