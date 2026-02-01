from datetime import datetime
from typing import Annotated

from fastapi import Path, Query, Request, Response
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, ResponseBaseModel
from module_dvd.entity.vo.config_menu_vo import (
    ConfigMenuModel,
    ConfigMenuQueryModel,
    ConfigMenuTreeModel,
    DeleteConfigMenuModel,
)
from module_dvd.service.config_menu_service import ConfigMenuService
from utils.log_util import logger
from utils.response_util import ResponseUtil

config_menu_controller = APIRouterPro(
    prefix='/dvd/config-menu', order_num=20, tags=['DVD配置-配置菜单管理'], dependencies=[PreAuthDependency()]
)


@config_menu_controller.get(
    '/treeselect',
    summary='获取配置菜单树接口',
    description='用于获取配置菜单树形下拉数据',
    response_model=DataResponseModel[list[ConfigMenuTreeModel]],
)
async def get_config_menu_tree(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    menu_query_result = await ConfigMenuService.get_config_menu_tree_services(query_db)
    logger.info('获取成功')

    return ResponseUtil.success(data=menu_query_result)


@config_menu_controller.get(
    '/list',
    summary='获取配置菜单列表接口',
    description='用于获取配置菜单列表',
    response_model=DataResponseModel[list[ConfigMenuModel]],
)
async def get_config_menu_list(
    request: Request,
    menu_query: Annotated[ConfigMenuQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    menu_query_result = await ConfigMenuService.get_config_menu_list_services(query_db, menu_query)
    logger.info('获取成功')

    return ResponseUtil.success(data=menu_query_result)


@config_menu_controller.post(
    '',
    summary='新增配置菜单接口',
    description='用于新增配置菜单',
    response_model=ResponseBaseModel,
)
@ValidateFields(validate_model='add_config_menu')
@Log(title='DVD配置菜单管理', business_type=BusinessType.INSERT)
async def add_config_menu(
    request: Request,
    add_config_menu: ConfigMenuModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    add_config_menu.create_time = datetime.now()
    add_config_menu.update_time = datetime.now()
    add_menu_result = await ConfigMenuService.add_config_menu_services(query_db, add_config_menu)
    logger.info(add_menu_result.message)

    return ResponseUtil.success(msg=add_menu_result.message)


@config_menu_controller.put(
    '',
    summary='编辑配置菜单接口',
    description='用于编辑配置菜单',
    response_model=ResponseBaseModel,
)
@ValidateFields(validate_model='edit_config_menu')
@Log(title='DVD配置菜单管理', business_type=BusinessType.UPDATE)
async def edit_config_menu(
    request: Request,
    edit_config_menu: ConfigMenuModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    edit_config_menu.update_time = datetime.now()
    edit_menu_result = await ConfigMenuService.edit_config_menu_services(query_db, edit_config_menu)
    logger.info(edit_menu_result.message)

    return ResponseUtil.success(msg=edit_menu_result.message)


@config_menu_controller.delete(
    '/{menu_ids}',
    summary='删除配置菜单接口',
    description='用于删除配置菜单',
    response_model=ResponseBaseModel,
)
@Log(title='DVD配置菜单管理', business_type=BusinessType.DELETE)
async def delete_config_menu(
    request: Request,
    menu_ids: Annotated[str, Path(description='需要删除的菜单ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    delete_menu = DeleteConfigMenuModel(dvdConfigMenuIds=menu_ids)
    delete_menu_result = await ConfigMenuService.delete_config_menu_services(query_db, delete_menu)
    logger.info(delete_menu_result.message)

    return ResponseUtil.success(msg=delete_menu_result.message)


@config_menu_controller.get(
    '/{menu_id}',
    summary='获取配置菜单详情接口',
    description='用于获取指定配置菜单的详情信息',
    response_model=DataResponseModel[ConfigMenuModel],
)
async def query_detail_config_menu(
    request: Request,
    menu_id: Annotated[int, Path(description='菜单ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    menu_detail_result = await ConfigMenuService.config_menu_detail_services(query_db, menu_id)
    logger.info(f'获取menu_id为{menu_id}的信息成功')

    return ResponseUtil.success(data=menu_detail_result)
