from fastapi import APIRouter, Depends, status
from src.schema.program import ProgramRequest, ProgramCreate, ProgramResponse, ProgramFilter
from src.services.program import get_program_service, ProgramService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from typing import Annotated
from src.utils.pagination import PaginationResponse, Pagination

router = APIRouter(prefix="/program", tags=["program"])

oauth2_scheme = HTTPBearer()


@router.post('/create_program', response_model=ProgramRequest)
async def program_create(form_data: ProgramCreate, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      program_service: ProgramService = Depends(get_program_service)):
    return await program_service.create_object(form_data)

@router.get('/list_programs_by', response_model=PaginationResponse)
async def program_list_by(pagination: Annotated[Pagination, Depends()],
                       current_user: Annotated[TokenData, Depends(get_current_active_user)],
                       filter_params: Annotated[ProgramFilter, Depends()],
                      program_service: ProgramService = Depends(get_program_service)):
    return await program_service.get_all_with_pagination(pagination, filter_params)


@router.get('/list_main_programs')
async def main_program_list_by(current_user: Annotated[TokenData, Depends(get_current_active_user)], year: str="2024", program_service: ProgramService = Depends(get_program_service)):
    return await program_service.get_all_main(year)


@router.delete('/delete_program', status_code=status.HTTP_204_NO_CONTENT)
async def program_delete(program_id: str,
                         current_user: Annotated[TokenData, Depends(get_current_active_user)],
                         program_service: ProgramService = Depends(get_program_service)):
    return await program_service.delete_by_id(program_id)

