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

@router.get('/list_all_curriculums_by')
async def curriculum_list_by(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        filter_params: Annotated[CurriculumFilter, Depends()],
        curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    year = filter_params.year
    program_id = filter_params.program_id
    user_id = current_user.user_id
    return await curriculum_service.get_all(user_id=user_id, year=year, program_id=program_id)



@router.get('/main_curriculum_by_program')
async def main_curriculum_list_by(current_user: Annotated[TokenData, Depends(get_current_active_user)], program_id: str, year: str = "2024", curriculum_service: CurriculumService = Depends(get_curriculum_service)):
    return await curriculum_service.get_all_main(year, program_id)


@router.delete('/delete_curriculum', status_code=status.HTTP_204_NO_CONTENT)
async def curriculum_delete(curriculum_id: str,
                         current_user: Annotated[TokenData, Depends(get_current_active_user)],
                         curriculum_service: CurriculumService = Depends(get_curriculum_service)):
    return await curriculum_service.delete_by_id(curriculum_id)

# @router.get("/curriculum-info", response_model=CurriculumResponse)
# async def get_current_curriculum(current_user: Annotated[TokenData, Depends(get_current_active_user)],
#                               curriculum_service: CurriculumService = Depends(get_curriculum_service)):
#     return await curriculum_service.get_curriculum_info(current_user)
