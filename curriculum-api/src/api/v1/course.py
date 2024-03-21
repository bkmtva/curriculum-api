from fastapi import APIRouter, Depends, status
from src.schema.course import CourseRequest, CourseCreate, CourseResponse, CourseFilter
from src.services.course import get_course_service, CourseService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from typing import Annotated
from src.utils.pagination import PaginationResponse, Pagination
from typing import List

router = APIRouter(prefix="/course", tags=["course"])

oauth2_scheme = HTTPBearer()


@router.post('/create_course', response_model=CourseRequest)
async def course_create(form_data: CourseCreate, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                        course_service: CourseService = Depends(get_course_service)):
    if not form_data.user_id:
        form_data.user_id = current_user.user_id
    return await course_service.create_object(form_data)


@router.post('/create_courses', response_model=List[CourseRequest])
async def course_create(courses_data: List[CourseCreate], current_user: Annotated[TokenData, Depends(get_current_active_user)],
                        course_service: CourseService = Depends(get_course_service)):
    created_courses = []
    for course_data in courses_data:
        if not course_data.user_id:
            course_data.user_id = current_user.user_id
        created_course = await course_service.create_object(course_data)
        created_courses.append(created_course)
    return created_courses


@router.get('/get_all_courses', response_model=PaginationResponse)
async def course_list(pagination: Annotated[Pagination, Depends()],
                      current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      filter_params: Annotated[CourseFilter, Depends()],
                      course_service: CourseService = Depends(get_course_service)):
    if not filter_params.user_id:
        filter_params.user_id = current_user.user_id
    return await course_service.get_all_with_pagination(pagination, filter_params)


@router.delete('/delete_course', status_code=status.HTTP_204_NO_CONTENT)
async def course_delete(course_id: str,
                        current_user: Annotated[TokenData, Depends(get_current_active_user)],
                        course_service: CourseService = Depends(get_course_service)):
    return await course_service.delete_by_id(course_id)

# @router.get("/course-info", response_model=CourseResponse)
# async def get_current_course(current_user: Annotated[TokenData, Depends(get_current_active_user)],
#                               course_service: CourseService = Depends(get_course_service)):
#     return await course_service.get_course_info(current_user)
