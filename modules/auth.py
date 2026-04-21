from exceptions import PermissionDeniedError, TokenExpiredError

# 模拟已过期的 token
EXPIRED_TOKENS = {"expired-token-123"}
# 模拟普通用户（无管理员权限）
NORMAL_USERS = {"user-token-abc"}
# 模拟管理员
ADMIN_TOKENS = {"admin-token-xyz"}


def verify_token(token: str) -> dict:
    """验证 token，返回用户信息；失败则抛出 AuthException"""
    if token in EXPIRED_TOKENS:
        raise TokenExpiredError()

    if token in NORMAL_USERS:
        return {"user_id": 1001, "role": "user"}

    if token in ADMIN_TOKENS:
        return {"user_id": 9999, "role": "admin"}

    # token 无效也视为过期/未认证
    raise TokenExpiredError()


def require_role(user: dict, required_role: str, resource: str) -> None:
    """检查用户角色权限；不足则抛出 PermissionDeniedError"""
    role_hierarchy = {"user": 1, "admin": 2}
    user_level = role_hierarchy.get(user["role"], 0)
    required_level = role_hierarchy.get(required_role, 99)

    if user_level < required_level:
        raise PermissionDeniedError(resource)
