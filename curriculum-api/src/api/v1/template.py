from fastapi import APIRouter, Depends, status
from src.schema.template import TemplateRequest, TemplateCreate, TemplateResponse, TemplateFilter
from src.services.template import get_template_service, TemplateService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from typing import Annotated
from src.utils.pagination import PaginationResponse, Pagination

router = APIRouter(prefix="/template", tags=["template"])

oauth2_scheme = HTTPBearer()


@router.post('/create_template', response_model=TemplateRequest)
async def template_create(form_data: TemplateCreate, current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      template_service: TemplateService = Depends(get_template_service)):
    return await template_service.create_object(form_data)

@router.get('/list_template_by', response_model=PaginationResponse)
async def main_template_list_by(pagination: Annotated[Pagination, Depends()],
                       current_user: Annotated[TokenData, Depends(get_current_active_user)],
                      template_service: TemplateService = Depends(get_template_service)):
    return await template_service.get_all_with_pagination(pagination)


# @router.get("/template-info", response_model=TemplateResponse)
# async def get_current_template(current_user: Annotated[TokenData, Depends(get_current_active_user)],
#                               template_service: TemplateService = Depends(get_template_service)):
#     return await template_service.get_template_info(current_user)
