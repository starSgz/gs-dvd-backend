from datetime import date
from typing import Annotated, Optional

from fastapi import Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_dvd.service.dd_service import DdOverviewService
from utils.log_util import logger
from utils.response_util import ResponseUtil

dd_controller = APIRouterPro(prefix='/dvd/dd', order_num=99, tags=['数据大屏-抖店'])


@dd_controller.get(
    '/dashboard/store-list',
    summary='获取抖店店铺列表',
    description='获取所有抖店店铺列表用于筛选',
    response_model=DataResponseModel,
)
async def get_store_list(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    获取抖店店铺列表
    """
    store_list = await DdOverviewService.get_store_list_service(query_db)
    logger.info('获取抖店店铺列表成功')

    return ResponseUtil.success(data=store_list)


@dd_controller.get(
    '/dashboard/store-top5',
    summary='获取抖店店铺销售TOP5',
    description='获取成交金额/订单数前五的店铺',
    response_model=DataResponseModel,
)
async def get_store_top5(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    store_id: Annotated[Optional[str], Query(description='店铺ID，用于筛选')] = None,
    sort_by: Annotated[str, Query(description='排序方式：orders-按订单量，amount-按成交金额')] = 'amount',
    limit: Annotated[int, Query(description='返回数量', ge=1, le=100)] = 5,
) -> Response:
    """
    获取抖店店铺销售TOP5
    """
    top_stores = await DdOverviewService.get_store_top5_service(query_db, store_id, sort_by, limit)
    logger.info(f'获取抖店店铺TOP{limit}成功，排序方式：{sort_by}')

    return ResponseUtil.success(data=top_stores)


@dd_controller.get(
    '/dashboard/overview-metrics',
    summary='获取抖店概览指标',
    description='获取用户支付金额、成交订单数、商品曝光人数等概览指标',
    response_model=DataResponseModel,
)
async def get_overview_metrics(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    store_id: Annotated[Optional[str], Query(description='店铺ID，用于筛选')] = None,
) -> Response:
    """
    获取抖店概览指标
    """
    metrics = await DdOverviewService.get_overview_metrics_service(query_db, store_id)
    logger.info('获取抖店概览指标成功')

    return ResponseUtil.success(data=metrics)


@dd_controller.get(
    '/dashboard/hourly-trend',
    summary='获取小时趋势数据',
    description='获取24小时的趋势数据，支持按指标筛选',
    response_model=DataResponseModel,
)
async def get_hourly_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    store_id: Annotated[Optional[str], Query(description='店铺ID，用于筛选')] = None,
    index_display: Annotated[Optional[str], Query(description='指标显示名称，如：用户支付金额')] = '用户支付金额',
) -> Response:
    """
    获取小时趋势数据
    """
    trend_data = await DdOverviewService.get_hourly_trend_service(query_db, store_id, index_display)
    logger.info(f'获取小时趋势数据成功，指标：{index_display}')

    return ResponseUtil.success(data=trend_data)


@dd_controller.get(
    '/dashboard/available-indices',
    summary='获取可用的指标列表（调试用）',
    description='查看数据库中有哪些可用的指标名称',
    response_model=DataResponseModel,
)
async def get_available_indices(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    获取可用的指标列表
    """
    indices = await DdOverviewService.get_available_indices_service(query_db)
    logger.info('获取可用指标列表成功')

    return ResponseUtil.success(data=indices)
