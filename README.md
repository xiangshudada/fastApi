# FastAPI 自定义异常 Demo

演示 FastAPI 中三层模块的自定义异常设计与全局处理。

## 项目结构

```
fastApi/
├── main.py          # FastAPI 应用入口、路由、异常处理器注册
├── exceptions.py    # 自定义异常类 + 全局 handler
└── modules/
    ├── auth.py      # 认证模块 → AuthException
    ├── business.py  # 业务模块 → BusinessException
    └── database.py  # 数据库模块 → DatabaseException
```

## 快速启动

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

访问 http://localhost:8000/docs 使用 Swagger UI 测试。

## 异常层级

| 层级 | 基类 | 子类 | HTTP 状态码 |
|------|------|------|------------|
| 认证层 | `AuthException` | `TokenExpiredError` / `PermissionDeniedError` | 401 |
| 业务层 | `BusinessException` | `InsufficientStockError` / `OrderLimitExceededError` | 422 |
| 数据库层 | `DatabaseException` | `RecordNotFoundError` / `DatabaseConnectionError` | 503 |

## 测试场景

| 场景 | 请求参数 | Token |
|------|---------|-------|
| 正常下单 | `product_id=2, quantity=3` | `user-token-abc` |
| Token 过期 | 任意 | `expired-token-123` |
| 超购上限 | `quantity=15` | `user-token-abc` |
| 库存不足 | `product_id=1, quantity=6` | `user-token-abc` |
| 商品不存在 | `product_id=99` | `user-token-abc` |
| DB 连接失败 | 任意 | `user-token-abc`（随机 10% 概率）|
