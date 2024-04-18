from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Body, status, Header, BackgroundTasks
from fastapi.security import HTTPBearer
from src.schema.course import CourseRequest, CourseCreate, CourseResponse, CourseFilter, CourseDetailSchema
from src.services.course import get_course_service, CourseService
from src.utils.jwt import TokenData, get_current_active_user


router = APIRouter(prefix="/course", tags=["course"])

oauth2_scheme = HTTPBearer()


@router.post('', response_model=CourseRequest)
async def course_create(
        form_data: CourseCreate,
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        course_service: CourseService = Depends(get_course_service)
):
    if not form_data.user_id:
        form_data.user_id = current_user.user_id
    return await course_service.create_object(form_data)

@router.post('/bulk_create', response_model=List[CourseRequest])
async def course_create(
        courses_data: List[CourseCreate],
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        course_service: CourseService = Depends(get_course_service)
):
    created_courses = []
    for course_data in courses_data:
        if not course_data.user_id:
            course_data.user_id = current_user.user_id
        created_course = await course_service.create_object(course_data)
        created_courses.append(created_course)
    return created_courses

@router.get('/get_all_courses')
async def course_list(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        filter_params: Annotated[CourseFilter, Depends()],
        course_service: CourseService = Depends(get_course_service)
):
    if not filter_params.user_id:
        filter_params.user_id = current_user.user_id
    return await course_service.get_all_with_pagination(filter_params)

@router.get('/{course_id}', response_model=CourseDetailSchema)
async def get_course(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        course_id: str,
        course_service: CourseService = Depends(get_course_service)
):
    user_id = current_user.user_id
    return await course_service.get_by_id(course_id)

@router.put("/{course_id}", response_model=CourseDetailSchema)
async def update_course(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        course_id: str,
        course_service: CourseService = Depends(get_course_service),
        course_schema: CourseCreate = Body()
):
    user_id = current_user.user_id
    return await course_service.update_object(course_id, course_schema)

@router.delete('/{course_id}', status_code=status.HTTP_204_NO_CONTENT)
async def course_delete(
        course_id: str,
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        course_service: CourseService = Depends(get_course_service)
):
    return await course_service.delete_by_id(course_id)
