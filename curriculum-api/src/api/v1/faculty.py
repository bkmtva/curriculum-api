from fastapi import APIRouter, Depends, status
from src.schema.faculty import FacultyRequest, FacultyCreate, FacultyResponse
from src.services.faculty import get_faculty_service, FacultyService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from typing import Annotated
from src.utils.pagination import PaginationResponse, Pagination

router = APIRouter(prefix="/faculty", tags=["faculty"])

oauth2_scheme = HTTPBearer()


@router.post('/create_faculty', response_model=FacultyRequest)
async def faculty_create(form_data: FacultyCreate, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      faculty_service: FacultyService = Depends(get_faculty_service)):
    return await faculty_service.create_object(form_data)


@router.get('/get_all_faculties', response_model=PaginationResponse)
async def faculty_list(pagination: Annotated[Pagination, Depends()],
                       current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      faculty_service: FacultyService = Depends(get_faculty_service)):
    return await faculty_service.get_all_with_pagination(pagination)


@router.delete('/delete_faculty', status_code=status.HTTP_204_NO_CONTENT)
async def faculty_delete(faculty_id: str,
                         current_user: Annotated[TokenData, Depends(get_current_active_user)],
                         faculty_service: FacultyService = Depends(get_faculty_service)):
    return await faculty_service.delete_by_id(faculty_id)

# @router.get("/faculty-info", response_model=FacultyResponse)
# async def get_current_faculty(current_user: Annotated[TokenData, Depends(get_current_active_user)],
#                               faculty_service: FacultyService = Depends(get_faculty_service)):
#     return await faculty_service.get_faculty_info(current_user)
