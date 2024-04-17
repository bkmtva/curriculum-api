from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from src.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, RESET_SECRET_KEY
from src.utils.cache_db import auth_redis_db

# Схема аутентификации OAuth2
oauth2_scheme = HTTPBearer()


# Модель данных токена
class TokenData(BaseModel):
    user_id: str | None = None
    is_superuser: bool = False
    disabled: bool | None = None
    email: str | None = None
    faculty_id: str | None = None

class ResetTokenData(BaseModel):
    email: str | None = None
    reset_token: str | None = None

# Функция проверки токена на наличие в черном списке
async def is_token_blacklisted(jti: str = 'ghj') -> bool:
    key = 'expired_access::' + str(jti)
    token_in_redis = await auth_redis_db.get(key)
    return token_in_redis is not None


async def set_token_blacklisted(jti: str, token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> bool:
    access_key = 'expired_access::' + str(jti)
    # refresh_key = 'refresh::' + jti
    await auth_redis_db.setex(access_key, ACCESS_TOKEN_EXPIRE_MINUTES, str(token))
    return None

async def logout_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    # Исключение для невалидных учетных данных
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:

        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_sub": False})
        jti = payload.get("jti")
        if await is_token_blacklisted(jti):
            raise HTTPException(status_code=400, detail="Already logged out")
        else:
            await set_token_blacklisted(jti, token)
    except JWTError:
        raise credentials_exception
    return {'message': 'Logout success'}


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    # Исключение для невалидных учетных данных
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_sub": False})
        jti = payload.get("jti")
        if await is_token_blacklisted(jti):
            raise credentials_exception
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception

        token_data = TokenData(user_id=subject['user_id'], email=subject['email'],
                               is_superuser=subject["is_superuser"], faculty_id=subject.get("faculty_id"))
    except JWTError:
        raise credentials_exception
    return token_data



async def get_current_active_user(
    token_data: TokenData = Depends(get_current_user)
):
    # Проверка на активность пользователя
    if token_data.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return token_data


async def get_current_reset_email(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(token)
        payload = jwt.decode(token.credentials, RESET_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_sub": False})
        jti = payload.get("jti")
        if await is_token_blacklisted(jti):
            raise credentials_exception
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception

        token_data = ResetTokenData(email=subject['email'], reset_token=token.credentials)
    except JWTError:
        raise credentials_exception
    return token_data