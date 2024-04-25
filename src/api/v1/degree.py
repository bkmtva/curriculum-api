from fastapi import APIRouter, Depends, HTTPException, Body, status, Header
from src.schema.degree import DegreeRequest, DegreeCreate, DegreeResponse, DegreeFilter
from src.services.degree import get_degree_service, DegreeService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from typing import Annotated


router = APIRouter(prefix="/degree", tags=["degree"])

oauth2_scheme = HTTPBearer()


@router.post('', response_model=DegreeRequest)
async def degree_create(form_data: DegreeCreate, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      degree_service: DegreeService = Depends(get_degree_service)):
    if not form_data.faculty_id:
        form_data.faculty_id = current_user.faculty_id
    return await degree_service.create_object(form_data)

@router.get('/list_degree_by')
async def degree_list_by(current_user: Annotated[TokenData, Depends(get_current_active_user)],
                       filter_params: Annotated[DegreeFilter, Depends()],
                      degree_service: DegreeService = Depends(get_degree_service)):
    filter_params.faculty_id = current_user.faculty_id
    return await degree_service.get_all_with_pagination(filter_params)

@router.put("/{degree_id}", response_model=DegreeRequest)
async def degree_update(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        degree_id: str,
        degree_service: DegreeService = Depends(get_degree_service),
        degree_schema: DegreeCreate = Body()
):
    return await degree_service.update_object(degree_id, degree_schema)


@router.delete('/{degree_id}', status_code=status.HTTP_204_NO_CONTENT)
async def degree_delete(degree_id: str,
                         current_user: Annotated[TokenData, Depends(get_current_active_user)],
                         degree_service: DegreeService = Depends(get_degree_service)):
    return await degree_service.delete_by_id(degree_id)
