from fastapi import APIRouter, Depends, HTTPException, Body, status, Header
from src.schema.template import TemplateRequest, TemplateCreate, TemplateResponse, TemplateFilter
from src.services.template import get_template_service, TemplateService
from fastapi.security import HTTPBearer
from src.utils.jwt import TokenData, get_current_active_user
from typing import Annotated

router = APIRouter(prefix="/template", tags=["template"])

oauth2_scheme = HTTPBearer()


@router.post('', response_model=TemplateRequest)
async def template_create(
        form_data: TemplateCreate,
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        template_service: TemplateService = Depends(get_template_service)
):
    return await template_service.create_object(form_data)


@router.get('')
async def template_list(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        template_service: TemplateService = Depends(get_template_service)
):
    return await template_service.get_all_with_pagination()


@router.put("/{template_id}", response_model=TemplateRequest)
async def template_update(
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        template_id: str,
        template_service: TemplateService = Depends(get_template_service),
        template_schema: TemplateCreate = Body()
):
    return await template_service.update_object(template_id, template_schema)


@router.delete('/{template_id}', status_code=status.HTTP_204_NO_CONTENT)
async def template_delete(
        template_id: str,
        current_user: Annotated[TokenData, Depends(get_current_active_user)],
        template_service: TemplateService = Depends(get_template_service)
):
    return await template_service.delete_by_id(template_id)
