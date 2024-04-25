from fastapi import APIRouter
from src.api.v1.auth import router as auth_route
from src.api.v1.user import router as user_route
from src.api.v1.faculty import router as faculty_route
from src.api.v1.degree import router as degree_route
from src.api.v1.template import router as template_route
from src.api.v1.program import router as program_route
from src.api.v1.curriculum import router as curriculum_route
from src.api.v1.course import router as course_route

urls = APIRouter(prefix='/v1')

urls.include_router(auth_route)
urls.include_router(user_route)
urls.include_router(faculty_route)
urls.include_router(degree_route)
urls.include_router(template_route)
urls.include_router(program_route)
urls.include_router(curriculum_route)
urls.include_router(course_route)
