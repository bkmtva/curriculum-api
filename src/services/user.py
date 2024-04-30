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
from src.schema.user import UserInDB, TokenData, UserLogin, UserRequest, UserResponse, UserDetailSchema
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.services.base import BaseService
from fastapi.responses import JSONResponse
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from src.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, RESET_SECRET_KEY
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from urllib.parse import urlencode
import uuid

class UserService(BaseService):
    model = User
    schema = UserInDB
    service_name = 'user'
    OBJECT_CACHE_EXPIRE_IN_SECONDS = 60 * 5
    detail_schema = UserDetailSchema
    relationships = ['faculty']
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, db: AsyncSession):
        self.redis = redis
        self.elastic = elastic
        self.db = db

    async def create_user(self, form_data, token_data: str, file=None):
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access",
            headers={"WWW-Authenticate": "Bearer"}
        )
        if not token_data:
            raise credential_exception
        if token_data:
            user = await self.get_user_by_email(email=token_data.email)
            if not user or not user.is_superuser:
                raise credential_exception

        existing_user = await self._get_object_from_db_email(email=form_data.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        if file and file.filename:
            contents = await file.read()
            file_path = f"/app/media/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(contents)
            form_data.profile_image = file_path
        form_data.password = await self._get_password_hash(form_data.password)
        db_obj = self.model(**form_data.dict())
        self.db.add(db_obj)
        await self.db_commit()
        await self.db.refresh(db_obj)

        return db_obj

    async def _get_object_from_db(self, obj_id):
        return (await self.db.execute(select(User).options(
            selectinload(User.faculty),
        ).filter_by(id=obj_id))).scalar()

    async def update_object(self, obj_id: str, current_user: str, obj_sch, file=None):
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No access",
            headers={"WWW-Authenticate": "Bearer"}
        )


        if current_user.user_id != obj_id and not current_user.is_superuser:
            raise credential_exception


        db_obj = await self._get_object_from_db(obj_id)
        if not current_user.is_superuser:
            obj_sch.is_superuser = db_obj.is_superuser
        if not db_obj:
            raise HTTPException(status_code=404, detail="Object not found")
        for key, value in self.relationship_options.items():
            if getattr(obj_sch, key) is not None:
                setattr(db_obj, value['field'], await self._set_obj_ids(getattr(obj_sch, key), value['model']))

        if file and file.filename:
            contents = await file.read()
            file_path = f"/app/media/{file.filename}"
            with open(file_path, "wb") as f:
                f.write(contents)
            obj_sch.profile_image = file_path
        if obj_sch.password and obj_sch.old_password:
            if not await self._verify_password(obj_sch.old_password, db_obj.password):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password")
            obj_sch.password = await self._get_password_hash(obj_sch.password)
            del obj_sch.old_password

        await self._update_object_in_db(db_obj=db_obj, obj_sch=obj_sch)
        await self.db.refresh(db_obj)
        if self.detail_schema:
            obj_sch = self.detail_schema.model_validate(db_obj.__dict__)
        else:
            obj_sch = self.schema.model_validate(db_obj.__dict__)
        await self._put_object_to_cache(obj_sch)
        return obj_sch

    async def create_access_token(self, data: dict, expires_delta: timedelta or None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    
    async def create_refresh_token(self, data: dict, expires_delta: timedelta or None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
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

    async def _get_object_from_db_email(self, email: str):
        return (await self.db.execute(select(self.model).options(
            selectinload(User.faculty),
        ).filter_by(email=email))).scalar()

    async def _delete_object_from_cache(self, email: str):
        await self.redis.delete(f'{self.service_name}_{email}')

    async def _put_object_to_cache(self, obj_sch):
        print('Set Object To Cache')
        await self.redis.set(
            f'{self.service_name}_{obj_sch.email}',
            obj_sch.json(),
            self.OBJECT_CACHE_EXPIRE_IN_SECONDS
        )


    async def get_user_by_email(self, email: str):
        db_obj = None
        # db_obj = await self._object_from_cache(email)
        if not db_obj:
            db_obj = await self._get_object_from_db_email(email)
            if not db_obj:
                raise HTTPException(status_code=404, detail="Incorrect email or password")
            print(db_obj, "validifjiegferger")
            obj_sch = self.schema.model_validate(db_obj.__dict__)
            print(obj_sch, "egokoergkoroe")
            await self._put_object_to_cache(obj_sch)
        return obj_sch

    async def authenticate_user(self, email: str, password: str):
        user = await self.get_user_by_email(email)
        if not user:
            return False
        if not await self._verify_password(password, user.password):
            return False

        return user

    

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
        access_token = await self.create_access_token(data={"sub": {'user_id': str(user.id),  'is_superuser': user.is_superuser, 'email': user.email, 'faculty_id': str(user.faculty_id)}}, expires_delta=access_token_expires)
        refresh_token = await self.create_refresh_token(data={"sub": {'user_id': str(user.id),  'is_superuser': user.is_superuser, 'email': user.email, 'faculty_id': str(user.faculty_id)}}, expires_delta=refresh_token_expires)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer",  "message": "Authentication success"}

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
            payload = jwt.decode(token, RESET_SECRET_KEY, algorithms=[ALGORITHM], options={"verify_sub": False})
            email: str = payload.get("sub", {}).get('email')
            if email is None:
                raise credential_exception
            return email
        except JWTError as e:
            print(f"JWTError: {e}")
            raise credential_exception

        return email

    async def refresh_access_token(self, refesh_data: str):
        # refesh_data = await self.verify_token(token.refresh_token)
        new_access_token = await self.create_access_token(refesh_data.dict())

        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "status": status.HTTP_200_OK
        }

    async def get_user_info(self, token_data: str):
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        # token_data = await self.verify_token(token)
        user = await self.get_user_by_email(email=token_data.email)
        if user is None:
            raise credential_exception

        return user

    async def create_reset_token(self, data: dict, expires_delta: timedelta or None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
        encoded_jwt = jwt.encode(to_encode, RESET_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def send_email(self, password_reset_request):
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate email",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user = await self.get_user_by_email(email=password_reset_request.email)
        if user is None:
            raise credential_exception
        access_token_expires = timedelta(minutes=15)
        reset_token = await self.create_reset_token(data={"sub": {'email': user.email,}}, expires_delta=access_token_expires)
        await self.send_reset_email(password_reset_request.email, reset_token)


        return {"message": "Password reset requested. Check your email for further instructions"}

    async def send_reset_email(self, email: str, reset_token: str) -> None:
        """
        Send a reset password email to the user.
        """
        from_email = "hokkaido.vi@gmail.com"  # Your email address
        to_email = email
        password = "cymw uxty uytg qczi"  # Your email password

        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset"
        message["From"] = from_email
        message["To"] = to_email

        reset_link = f"http://49.13.154.79:3000/reset_password/{reset_token}"
        text = f"""\
            Hi,
            To reset your password, click on the following link:
            {reset_link}
            If you didn't request a password reset, please ignore this email."""

        html = f"""\
            <html>
              <body>
                <p>Hi,<br>
                   To reset your password, click on the following link:<br>
                   <a href="{reset_link}">{reset_link}</a><br>
                   If you didn't request a password reset, please ignore this email.
                </p>
              </body>
            </html>
            """



        smtp_server = 'smtp.gmail.com'
        smtp_port = 587

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, password)
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)
        server.sendmail(from_email, to_email, message.as_string())

        server.quit()
    async def change_password(self, new_password_data, email):
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate email",
            headers={"WWW-Authenticate": "Bearer"},
        )
        if new_password_data.new_password != new_password_data.repeat_new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New passwords do not match")

        db_obj = await self._get_object_from_db_email(email=email)
        if db_obj is None:
            raise credential_exception
        new_password = await self._get_password_hash(new_password_data.new_password)
        setattr(db_obj, 'password', new_password)
        self.db.add(db_obj)
        await self.db_commit()
        await self.db.refresh(db_obj)
        return {"message": "Password changed successfully!"}

@lru_cache()
def get_user_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
    db: AsyncSession = Depends(get_db)
) -> UserService:
    return UserService(redis, elastic, db)
