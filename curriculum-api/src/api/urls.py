from fastapi import APIRouter
from src.api.v1.user import router as user_route

urls = APIRouter(prefix='/v1')

urls.include_router(user_route)
