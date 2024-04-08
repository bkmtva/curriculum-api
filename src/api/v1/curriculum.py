from fastapi import APIRouter, Depends, status, Response
from src.schema.curriculum import CurriculumRequest, CurriculumCreate, CurriculumResponse, CurriculumFilter
from src.services.curriculum import get_curriculum_service, CurriculumService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from src.excel_files.to_excel import to_excel
from typing import Annotated, List
router = APIRouter(prefix="/curriculum", tags=["curriculum"])

oauth2_scheme = HTTPBearer()


@router.post('/create_curriculum', response_model=CurriculumRequest)
async def curriculum_create(form_data: CurriculumCreate, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      curriculum_service: CurriculumService = Depends(get_curriculum_service)):
    if not form_data.year:
        form_data.year = "2024"
    if not form_data.created_by:
        form_data.created_by = current_user.user_id
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

@router.put("/update_curriculum")
async def update_curriculum_courses(
        curriculum_id: str, courses_info: list[dict],
        curriculum_service: CurriculumService = Depends(get_curriculum_service)
):

    return await curriculum_service.update_curriculum(user_id=None, curriculum_id=curriculum_id, courses=courses_info)


@router.get('/get_all_curriculums_by_program')
async def get_all_curriculums_by_program(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        filter_params: Annotated[CurriculumFilter, Depends()],
        curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    year = filter_params.year
    program_id = filter_params.program_id
    user_id = current_user.user_id
    return await curriculum_service.get_all_curriculums_by_program(user_id=user_id, year=year, program_id=program_id)



@router.get('/get_curriculum_by_id')
async def curriculum_by_id(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        curriculum_id: str,
        curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    user_id = current_user.user_id
    return await curriculum_service.get_curriculum_by_id(user_id=user_id, curriculum_id=curriculum_id)


@router.get('/main_curriculum_by_program')
async def main_curriculum_list_by(current_user: Annotated[TokenData, Depends(get_current_active_user)], program_id: str, year: str = "2024", curriculum_service: CurriculumService = Depends(get_curriculum_service)):
    return await curriculum_service.get_all_main(year, program_id)


@router.delete('/delete_curriculum', status_code=status.HTTP_204_NO_CONTENT)
async def curriculum_delete(curriculum_id: str,
                         current_user: Annotated[TokenData, Depends(get_current_active_user)],
                         curriculum_service: CurriculumService = Depends(get_curriculum_service)):
    return await curriculum_service.delete_by_id(curriculum_id)


@router.get('/download_curriculum')
async def curriculum_download(curriculum_id: str, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                         curriculum_service: CurriculumService = Depends(get_curriculum_service)):
    user_id = current_user.user_id
    currciculum = await curriculum_service.get_curriculum(user_id=user_id, curriculum_id=curriculum_id)
    print(currciculum)
    to_excel(currciculum)
    excel_file_path = "src/excel_files/curriculum.xlsx"
    with open(excel_file_path, "rb") as file:
        content = file.read()
    response = Response(content=content)
    response.headers["Content-Disposition"] = "attachment; filename=existing_file.xlsx"
    response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return response


@router.put('/set_main_curriculum')
async def set_main_curriculum(curriculum_id: str, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                         curriculum_service: CurriculumService = Depends(get_curriculum_service)):

    return await curriculum_service.set_as_main(curriculum_id)

# @router.get("/curriculum-info", response_model=CurriculumResponse)
# async def get_current_curriculum(current_user: Annotated[TokenData, Depends(get_current_active_user)],
#                               curriculum_service: CurriculumService = Depends(get_curriculum_service)):
#     return await curriculum_service.get_curriculum_info(current_user)
