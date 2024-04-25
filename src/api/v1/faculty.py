from fastapi import APIRouter, Depends, HTTPException, Body, status, Header
from src.schema.faculty import FacultyRequest, FacultyCreate, FacultyResponse
from src.services.faculty import get_faculty_service, FacultyService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from typing import Annotated

router = APIRouter(prefix="/faculty", tags=["faculty"])

oauth2_scheme = HTTPBearer()


@router.get('')
async def faculty_list(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        faculty_service: FacultyService = Depends(get_faculty_service)
):
    return await faculty_service.get_all_with_pagination()

@router.post('', response_model=FacultyRequest)
async def faculty_create(
        form_data: FacultyCreate,
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        faculty_service: FacultyService = Depends(get_faculty_service)
):
    return await faculty_service.create_object(form_data)


@router.put("/{faculty_id}", response_model=FacultyRequest)
async def faculty_update(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        faculty_id: str,
        faculty_service: FacultyService = Depends(get_faculty_service),
        faculty_schema: FacultyCreate = Body()
):
    return await faculty_service.update_object(faculty_id, faculty_schema)


@router.delete('/{faculty_id}', status_code=status.HTTP_204_NO_CONTENT)
async def faculty_delete(
        faculty_id: str,
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        faculty_service: FacultyService = Depends(get_faculty_service)
):
    return await faculty_service.delete_by_id(faculty_id)
