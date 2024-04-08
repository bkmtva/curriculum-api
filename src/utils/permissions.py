from typing import Annotated, List

from fastapi import Depends, status, HTTPException

from src.utils.cache_db import auth_redis_db
from src.utils.jwt import TokenData, get_current_active_user


async def get_permissions(role: str) -> List[str]:
    if role:
        return [p.decode() for p in await auth_redis_db.lrange(role, 0, -1)]
    return []


class PermissionChecker:

    def __init__(self, permission_name: str) -> None:
        self.permission_name = permission_name

    async def __call__(self, current_user: Annotated[TokenData, Depends(get_current_active_user)]) -> TokenData:
        if not current_user.is_superuser:
            role = await auth_redis_db.get(f"user_{current_user.user_id}_1")
            permissions = await get_permissions(role)
            if self.permission_name not in permissions:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="You don't have enough permissions"
                )
        return current_user
