from datetime import date
from typing import Annotated, Optional

from fastapi import Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_dvd.service.qf_service import QfOverviewService
from utils.log_util import logger
from utils.response_util import ResponseUtil

dvd_controller = APIRouterPro(prefix='/dvd', order_num=99, tags=['数据大屏'])


@dvd_controller.get(
    '/dashboard/metrics',
    summary='获取大屏核心指标',
    description='获取订单总数和GMV总额',
    response_model=DataResponseModel,
)
async def get_dashboard_metrics(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    target_date: Annotated[Optional[str], Query(description='目标日期，格式：YYYY-MM-DD')] = None,
) -> Response:
    """
    获取大屏核心指标
    """
    date_obj = date.fromisoformat(target_date) if target_date else None
    metrics = await QfOverviewService.get_dashboard_metrics_service(query_db, date_obj)
    logger.info('获取大屏核心指标成功')

    return ResponseUtil.success(data=metrics)


@dvd_controller.get(
    '/dashboard/store-rank',
    summary='获取店铺销售排行',
    description='获取店铺销售排行TOP10',
    response_model=DataResponseModel,
)
async def get_store_sales_rank(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    target_date: Annotated[Optional[str], Query(description='目标日期，格式：YYYY-MM-DD')] = None,
    limit: Annotated[int, Query(description='返回数量')] = 10,
) -> Response:
    """
    获取店铺销售排行
    """
    date_obj = date.fromisoformat(target_date) if target_date else None
    store_rank = await QfOverviewService.get_store_sales_rank_service(query_db, date_obj, limit)
    logger.info('获取店铺销售排行成功')

    return ResponseUtil.success(data=store_rank)


@dvd_controller.get(
    '/dashboard/channel-data',
    summary='获取渠道销售数据',
    description='获取笔记、直播、商卡的销售数据',
    response_model=DataResponseModel,
)
async def get_channel_sales_data(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    target_date: Annotated[Optional[str], Query(description='目标日期，格式：YYYY-MM-DD')] = None,
) -> Response:
    """
    获取渠道销售数据
    """
    date_obj = date.fromisoformat(target_date) if target_date else None
    channel_data = await QfOverviewService.get_channel_sales_data_service(query_db, date_obj)
    logger.info('获取渠道销售数据成功')

    return ResponseUtil.success(data=channel_data)


@dvd_controller.get(
    '/dashboard/recent-orders',
    summary='获取最近订单',
    description='获取最近的订单列表',
    response_model=DataResponseModel,
)
async def get_recent_orders(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    limit: Annotated[int, Query(description='返回数量')] = 20,
) -> Response:
    """
    获取最近订单
    """
    recent_orders = await QfOverviewService.get_recent_orders_service(query_db, limit)
    logger.info('获取最近订单成功')

    return ResponseUtil.success(data=recent_orders)


@dvd_controller.get(
    '/dashboard/trend-data',
    summary='获取趋势数据',
    description='获取GMV和订单量的趋势数据',
    response_model=DataResponseModel,
)
async def get_trend_data(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    days: Annotated[int, Query(description='天数')] = 7,
) -> Response:
    """
    获取趋势数据
    """
    trend_data = await QfOverviewService.get_trend_data_service(query_db, days)
    logger.info('获取趋势数据成功')

    return ResponseUtil.success(data=trend_data)


@dvd_controller.get(
    '/dashboard/all',
    summary='获取大屏所有数据',
    description='一次性获取大屏所有需要的数据',
    response_model=DataResponseModel,
)
async def get_all_dashboard_data(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    target_date: Annotated[Optional[str], Query(description='目标日期，格式：YYYY-MM-DD')] = None,
) -> Response:
    """
    获取大屏所有数据
    """
    date_obj = date.fromisoformat(target_date) if target_date else None
    all_data = await QfOverviewService.get_all_dashboard_data_service(query_db, date_obj)
    logger.info('获取大屏所有数据成功')

    return ResponseUtil.success(data=all_data)
