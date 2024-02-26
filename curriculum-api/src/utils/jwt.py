from datetime import datetime, timedelta, timezone
from typing import Annotated
import asyncio
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class JwtGenerator:
    def __init__(self, user_id: str, is_superuser: bool = False, access_token_expires_in: int = None,
                 refresh_token_expires_in: int = None):
        self.user_id = user_id
        self.is_superuser = is_superuser
        self.access_token_expires_in = access_token_expires_in
        self.refresh_token_expires_in = refresh_token_expires_in

    async def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        loop = asyncio.get_event_loop()

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})

        encoded_jwt = await loop.run_in_executor(None, jwt.encode, to_encode, SECRET_KEY, ALGORITHM)
        return encoded_jwt

    async def create_refresh_token(self, data: dict, expires_delta: timedelta | None = None):
        loop = asyncio.get_event_loop()

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=30)  # Example: Refresh token expires in 30 days
        to_encode.update({"exp": expire})

        encoded_jwt = await loop.run_in_executor(None, jwt.encode, to_encode, SECRET_KEY, ALGORITHM)
        return encoded_jwt

    async def _get_identity(self):
        return {
            'user_id': self.user_id,
            'is_superuser': self.is_superuser,
            # 'user_agent': self.user_agent,
            # 'unique_payload_key': self.unique_payload_key,
            # 'rules': self.rules,
        }
