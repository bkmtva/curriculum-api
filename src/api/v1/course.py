from typing import Annotated, List
from fastapi import UploadFile, Response, File, APIRouter, Depends, HTTPException, Body, status, Header, BackgroundTasks
from fastapi.security import HTTPBearer
from src.schema.course import CourseInfo, CourseUpdate, CourseRequest, CourseCreate, CourseResponse, CourseFilter, CourseDetailSchema
from src.services.course import get_course_service, CourseService
from src.utils.jwt import TokenData, get_current_active_user
from src.excel_files.from_excel import get_courses
import os
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
async def courses_create(
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
async def course_get(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        course_id: str,
        course_service: CourseService = Depends(get_course_service)
):
    user_id = current_user.user_id
    return await course_service.get_by_id(course_id)

@router.get('/courses_img/')
async def courses_img(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],

        course_service: CourseService = Depends(get_course_service)
):
    user_id = current_user.user_id
    return 'http://49.13.154.79/media/example_excel.png'

@router.put("/{course_id}", response_model=CourseDetailSchema)
async def course_update(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        course_id: str,
        course_schema: CourseUpdate = Body(),
        course_service: CourseService = Depends(get_course_service),

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


@router.post('/upload_excel', response_model=List[CourseInfo])
async def courses_import(
        excel_file: UploadFile = File(...),
        current_user: Annotated[TokenData, Depends(get_current_active_user)] = '',
        course_service: CourseService = Depends(get_course_service)
):

    if not excel_file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Uploaded file must be a Excel (xlsx) file.")
    upload_dir = "/app/excel_files/courses"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, excel_file.filename)
    with open(file_path, "wb") as file:
        file.write(excel_file.file.read())

    courses_data = await get_courses(file_path)

    created_courses = []
    for course_data in courses_data:
        if not course_data.get('user_id'):
            course_data['user_id'] = current_user.user_id
        course_data['term'] = str(course_data['term'])
        course = CourseCreate(**course_data)
        created_courses.append(course)
        # created_course = await course_service.create_object(course)
        # created_courses.append(created_course)
    return created_courses


@router.get('/example_excel/')
async def courses_excel(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        course_service: CourseService = Depends(get_course_service)
):
    # user_id = current_user.user_id

    excel_file_path = f"src/excel_files/add_courses.xlsx"
    with open(excel_file_path, "rb") as file:
        content = file.read()
    response = Response(content=content)
    response.headers["Content-Disposition"] = f"attachment; filename=example_excel.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response
