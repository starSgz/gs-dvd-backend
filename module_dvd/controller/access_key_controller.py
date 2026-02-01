from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from module_admin.entity.vo.user_vo import CurrentUserModel
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_dvd.entity.vo.access_key_vo import (
    AccessKeyCreateModel,
    AccessKeyModel,
    AccessKeyPageQueryModel,
    ActivateAccessKeyModel,
    ActivateAccessKeyResponseModel,
    DeleteAccessKeyModel,
)
from module_dvd.service.access_key_service import AccessKeyService
from utils.log_util import logger
from utils.response_util import ResponseUtil

access_key_controller = APIRouterPro(
    prefix='/dvd/access-key', order_num=10, tags=['DVD配置-卡密管理'], dependencies=[PreAuthDependency()]
)


@access_key_controller.get(
    '/list',
    summary='获取卡密分页列表接口',
    description='用于获取卡密分页列表',
    response_model=PageResponseModel[AccessKeyModel],
    dependencies=[UserInterfaceAuthDependency('dvd:accessKey:list')],
)
async def get_access_key_list(
    request: Request,
    access_key_page_query: Annotated[AccessKeyPageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    # 获取分页数据
    access_key_page_query_result = await AccessKeyService.get_access_key_list_services(
        query_db, access_key_page_query, is_page=True
    )
    logger.info('获取卡密列表成功')

    return ResponseUtil.success(model_content=access_key_page_query_result)


@access_key_controller.post(
    '',
    summary='新增卡密接口',
    description='用于新增卡密',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('dvd:accessKey:add')],
)
@Log(title='卡密管理', business_type=BusinessType.INSERT)
async def add_access_key(
    request: Request,
    add_access_key_obj: AccessKeyCreateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_access_key_result = await AccessKeyService.add_access_key_services(query_db, add_access_key_obj)
    logger.info(add_access_key_result.message)

    return ResponseUtil.success(msg=add_access_key_result.message, data=add_access_key_result.result)


@access_key_controller.put(
    '',
    summary='编辑卡密接口',
    description='用于编辑卡密',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('dvd:accessKey:edit')],
)
@Log(title='卡密管理', business_type=BusinessType.UPDATE)
async def edit_access_key(
    request: Request,
    edit_access_key_obj: AccessKeyModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_access_key_result = await AccessKeyService.edit_access_key_services(query_db, edit_access_key_obj)
    logger.info(edit_access_key_result.message)

    return ResponseUtil.success(msg=edit_access_key_result.message)


@access_key_controller.delete(
    '/{access_keys}',
    summary='删除卡密接口',
    description='用于删除卡密',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('dvd:accessKey:remove')],
)
@Log(title='卡密管理', business_type=BusinessType.DELETE)
async def delete_access_key(
    request: Request,
    access_keys: Annotated[str, Path(description='需要删除的卡密，多个用逗号分隔')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_access_key_obj = DeleteAccessKeyModel(accessKeys=access_keys)
    delete_access_key_result = await AccessKeyService.delete_access_key_services(query_db, delete_access_key_obj)
    logger.info(delete_access_key_result.message)

    return ResponseUtil.success(msg=delete_access_key_result.message)


@access_key_controller.get(
    '/{access_key}',
    summary='获取卡密详情接口',
    description='用于获取指定卡密的详细信息',
    response_model=DataResponseModel[AccessKeyModel],
    dependencies=[UserInterfaceAuthDependency('dvd:accessKey:query')],
)
async def query_detail_access_key(
    request: Request,
    access_key: Annotated[str, Path(description='卡密')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    access_key_detail_result = await AccessKeyService.access_key_detail_services(query_db, access_key)
    logger.info(f'获取卡密 {access_key} 的信息成功')

    return ResponseUtil.success(data=access_key_detail_result)


@access_key_controller.post(
    '/activate',
    summary='激活卡密接口',
    description='用于激活卡密并绑定到当前用户',
    response_model=DataResponseModel[ActivateAccessKeyResponseModel],
)
@Log(title='卡密激活', business_type=BusinessType.UPDATE)
async def activate_access_key(
    request: Request,
    activate_model: ActivateAccessKeyModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    activate_result = await AccessKeyService.activate_access_key_services(
        query_db, activate_model.access_key, current_user.user.user_id
    )
    logger.info(f'用户 {current_user.user.user_name} 激活卡密成功')

    return ResponseUtil.success(data=activate_result)
