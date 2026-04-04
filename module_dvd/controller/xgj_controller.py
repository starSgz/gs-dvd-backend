from typing import Annotated, Optional

from fastapi import Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.data_scope import DvdDataScopeDependency
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_dvd.service.xgj_service import XgjOverviewService
from utils.log_util import logger
from utils.response_util import ResponseUtil

xgj_controller = APIRouterPro(
    prefix='/dvd/xgj',
    order_num=99,
    tags=['数据大屏-闲鱼'],
    dependencies=[PreAuthDependency()],
)


@xgj_controller.get(
    '/dashboard/store-list',
    summary='获取店铺列表',
    description='获取所有闲鱼店铺列表用于大屏筛选',
    response_model=DataResponseModel,
)
async def get_store_list(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    dvd_data_scope: Annotated[Optional[object], DvdDataScopeDependency()],
) -> Response:
    """
    获取店铺列表
    """
    store_list = await XgjOverviewService.get_store_list_service(query_db, dvd_data_scope)
    logger.info('获取闲鱼店铺列表成功')

    return ResponseUtil.success(data=store_list)


@xgj_controller.get(
    '/dashboard/product-status-distribution',
    summary='获取商品状态分布',
    description='按店铺筛选并汇总最新商品状态快照，用于商品状态分布图',
    response_model=DataResponseModel,
)
async def get_product_status_distribution(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    dvd_data_scope: Annotated[Optional[object], DvdDataScopeDependency()],
    store_name: Annotated[Optional[str], Query(description='店铺名称，用于筛选')] = None,
    store_id: Annotated[Optional[str], Query(description='店铺ID，用于筛选')] = None,
) -> Response:
    """
    获取商品状态分布
    """
    stats = await XgjOverviewService.get_product_status_distribution_service(
        query_db, store_name, store_id, dvd_data_scope
    )
    logger.info(f'获取闲鱼商品状态分布成功，店铺名称：{store_name}，店铺ID：{store_id}')

    return ResponseUtil.success(data=stats)


@xgj_controller.get(
    '/dashboard/top-store-ranking',
    summary='获取Top店铺排行',
    description='按最新采集小时查询Top店铺排行，用于Top店铺列表展示',
    response_model=DataResponseModel,
)
async def get_top_store_ranking(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    dvd_data_scope: Annotated[Optional[object], DvdDataScopeDependency()],
    store_name: Annotated[Optional[str], Query(description='店铺名称，用于筛选')] = None,
    store_id: Annotated[Optional[str], Query(description='店铺ID，用于筛选')] = None,
    limit: Annotated[int, Query(description='返回数量，默认100')] = 100,
) -> Response:
    """
    获取Top店铺排行
    """
    stats = await XgjOverviewService.get_top_store_ranking_service(
        query_db, store_name, store_id, limit, dvd_data_scope
    )
    logger.info(
        f'获取闲鱼Top店铺排行成功，店铺名称：{store_name}，店铺ID：{store_id}，返回数量：{limit}'
    )

    return ResponseUtil.success(data=stats)
