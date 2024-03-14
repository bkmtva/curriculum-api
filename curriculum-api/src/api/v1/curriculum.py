from fastapi import APIRouter, Depends, status
from src.schema.curriculum import CurriculumRequest, CurriculumCreate, CurriculumResponse, CurriculumFilter
from src.services.curriculum import get_curriculum_service, CurriculumService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from typing import Annotated
from src.utils.pagination import PaginationResponse, Pagination

router = APIRouter(prefix="/curriculum", tags=["curriculum"])

oauth2_scheme = HTTPBearer()


@router.post('/create_curriculum', response_model=CurriculumRequest)
async def curriculum_create(form_data: CurriculumCreate, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      curriculum_service: CurriculumService = Depends(get_curriculum_service)):
    return await curriculum_service.create_object(form_data)

@router.get('/list_all_curriculums_by', response_model=PaginationResponse)
async def curriculum_list_by(pagination: Annotated[Pagination, Depends()],
                       current_user: Annotated[TokenData, Depends(get_current_active_user)],
                       filter_params: Annotated[CurriculumFilter, Depends()],
                      curriculum_service: CurriculumService = Depends(get_curriculum_service)):
    return await curriculum_service.get_all_with_pagination(pagination, filter_params)



@router.get('/main_curriculum_by_program')
async def main_curriculum_list_by(current_user: Annotated[TokenData, Depends(get_current_active_user)], program_id: str, year: str = "2024", curriculum_service: CurriculumService = Depends(get_curriculum_service)):
    return await curriculum_service.get_all_main(year, program_id)

# @router.get("/curriculum-info", response_model=CurriculumResponse)
# async def get_current_curriculum(current_user: Annotated[TokenData, Depends(get_current_active_user)],
#                               curriculum_service: CurriculumService = Depends(get_curriculum_service)):
#     return await curriculum_service.get_curriculum_info(current_user)
