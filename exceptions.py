from fastapi import Request
from fastapi.responses import JSONResponse


# ── 各模块基础异常 ──────────────────────────────────────────

class AuthException(Exception):
    """认证模块异常"""
    def __init__(self, message: str, code: str = "AUTH_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class BusinessException(Exception):
    """业务模块异常"""
    def __init__(self, message: str, code: str = "BUSINESS_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class DatabaseException(Exception):
    """数据库模块异常"""
    def __init__(self, message: str, code: str = "DB_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


# ── 具体子类异常 ────────────────────────────────────────────

class TokenExpiredError(AuthException):
    def __init__(self):
        super().__init__("Token 已过期，请重新登录", code="TOKEN_EXPIRED")


class PermissionDeniedError(AuthException):
    def __init__(self, resource: str):
        super().__init__(f"无权访问资源: {resource}", code="PERMISSION_DENIED")


class InsufficientStockError(BusinessException):
    def __init__(self, product_id: int, requested: int, available: int):
        super().__init__(
            f"商品 {product_id} 库存不足，请求 {requested} 件，库存仅剩 {available} 件",
            code="INSUFFICIENT_STOCK",
        )


class OrderLimitExceededError(BusinessException):
    def __init__(self, limit: int):
        super().__init__(f"单次下单不能超过 {limit} 件", code="ORDER_LIMIT_EXCEEDED")


class RecordNotFoundError(DatabaseException):
    def __init__(self, entity: str, entity_id: int):
        super().__init__(f"{entity} (id={entity_id}) 不存在", code="RECORD_NOT_FOUND")


class DatabaseConnectionError(DatabaseException):
    def __init__(self):
        super().__init__("数据库连接失败，请稍后重试", code="DB_CONNECTION_FAILED")


# ── 全局异常处理器（注册到 FastAPI app）───────────────────────

async def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=401,
        content={"layer": "auth", "code": exc.code, "message": exc.message},
    )


async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=422,
        content={"layer": "business", "code": exc.code, "message": exc.message},
    )


async def database_exception_handler(request: Request, exc: DatabaseException):
    return JSONResponse(
        status_code=503,
        content={"layer": "database", "code": exc.code, "message": exc.message},
    )
