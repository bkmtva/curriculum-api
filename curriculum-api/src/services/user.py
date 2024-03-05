from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid
from typing import Optional
from src.db.database import get_db
from src.db.elastic import get_elastic
from src.db.redis import get_redis

from src.models.user import User
from src.schema.user import UserInDB, TokenData, UserLogin, UserRequest, UserResponse
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.services.base import BaseService
from fastapi.responses import JSONResponse
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")

SECRET_KEY = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 0.23
REFRESH_TOKEN_EXPIRE_MINUTES = 60*24


class UserService:
    model = User
    schema = UserInDB
    service_name = 'user'
    OBJECT_CACHE_EXPIRE_IN_SECONDS = 60 * 5

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, db: AsyncSession):
        self.redis = redis
        self.elastic = elastic
        self.db = db

    async def create_user(self, form_data):
        existing_user = await self._get_object_from_db(email=form_data.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        form_data.password = await self._get_password_hash(form_data.password)
        db_obj = self.model(**form_data.dict())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def create_access_token(self, data: dict, expires_delta: timedelta or None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str):
        credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                             detail="Could not validate credentials",
                                             headers={"WWW-Authenticate": "Bearer"})
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credential_exception

            token_data = TokenData(email=email)
        except JWTError:
            raise credential_exception

        user = await self.get_user_by_email(email=token_data.email)
        if user is None:
            raise credential_exception

        return user

    async def get_current_active_user(self, current_user: UserInDB = Depends(get_current_user)):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")

        return current_user


    async def _get_password_hash(self, password):
        return pwd_context.hash(password)

    async def _verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    async def _get_object_from_db(self, email: str):
        return (await self.db.execute(select(self.model).filter_by(email=email))).scalar()

    async def _delete_object_from_cache(self, email: str):
        await self.redis.delete(f'{self.service_name}_{email}')

    async def _put_object_to_cache(self, obj_sch):
        print('Set Object To Cache')
        await self.redis.set(
            f'{self.service_name}_{obj_sch.email}',
            obj_sch.json(),
            self.OBJECT_CACHE_EXPIRE_IN_SECONDS
        )

    async def _object_from_cache(self, email: str):
        print('Get Object From Cache')
        data = await self.redis.get(f'{self.service_name}_{email}')
        if not data:
            return None
        data = self.schema.parse_raw(data)
        return data

    async def get_user_by_email(self, email: str):
        db_obj = await self._object_from_cache(email)
        if not db_obj:
            db_obj = await self._get_object_from_db(email)
            if not db_obj:
                raise HTTPException(status_code=404, detail="Incorrect email or password")
            db_obj = self.schema.model_validate(db_obj.__dict__)
            await self._put_object_to_cache(db_obj)
        return db_obj

    async def authenticate_user(self, email: str, password: str):
        user = await self.get_user_by_email(email)
        if not user:
            return False
        if not await self._verify_password(password, user.password):
            return False

        return user

    async def create_refresh_token(self, data: dict, expires_delta: timedelta or None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def login_for_access_token(self, email: str, password: str):
        user = await self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        access_token = await self.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        refresh_token = await self.create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token, "message": "Authentication success"}

    async def get_all(self, rubric_type: str = 'news'):
        result = await self.db.execute(
            select(self.model).
            filter_by(parent_id=None, rubric_type=rubric_type).
            options(
                selectinload(self.model.children)
            )
        )
        return result.scalars()

    async def verify_token(self, token: str):

        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            email: str = payload.get("sub")
            if email is None:
                raise credential_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credential_exception

        return token_data

    async def refresh_access_token(self, token: str):
        refesh_data = await self.verify_token(token)
        new_access_token = await self.create_access_token(refesh_data.dict())

        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "status": status.HTTP_200_OK
        }

    # async def get_user_info(self, token: str):
    #     user_data = await self.verify_token(token)
    #
    #     # dummy_user_info = {
    #     #     "id": uuid.UUID('5e1fb87d-4db4-4c06-ace3-b3a4d1302536'),
    #     #     "first_name": "John",
    #     #     "last_name": "Doe",
    #     #     "email": "john@example.com",
    #     #     "profile_image": "profile_image_url",
    #     #     "last_login_at": datetime.now(),
    #     #     "created_at": datetime.now(),
    #     #     "is_active": True,
    #     #     "is_superuser": False,
    #     #     "faculty_id": uuid.UUID('5e1fb87d-4db4-4c06-ace3-b3a4d1302536')
    #     # }
    #
    #     return dummy_user_info

    async def get_user_info(self, token: str):
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        token_data = await self.verify_token(token)
        user = await self.get_user_by_email(email=token_data.email)
        if user is None:
            raise credential_exception
        
        user_response = UserResponse(**user.dict())

        return user_response


@lru_cache()
def get_user_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> UserService:
    return UserService(redis, elastic, db)
