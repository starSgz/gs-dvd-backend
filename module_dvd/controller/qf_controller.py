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

qf_controller = APIRouterPro(prefix='/dvd/qf', order_num=99, tags=['数据大屏-千帆'])

@qf_controller.get(
    '/dashboard/store-list',
    summary='获取店铺列表',
    description='获取所有店铺列表用于筛选',
    response_model=DataResponseModel,
)
async def get_store_list(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    获取店铺列表
    """
    store_list = await QfOverviewService.get_store_list_service(query_db)
    logger.info('获取店铺列表成功')

    return ResponseUtil.success(data=store_list)


@qf_controller.get(
    '/dashboard/realtime-metrics',
    summary='获取实时指标',
    description='从 qf_realtime_metrics 获取当天实时GMV、订单、访问量等走势数据',
    response_model=DataResponseModel,
)
async def get_realtime_metrics(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    target_date: Annotated[Optional[str], Query(description='目标日期，格式：YYYY-MM-DD')] = None,
    store_name: Annotated[Optional[str], Query(description='店铺名称，用于筛选')] = None,
) -> Response:
    """
    获取实时指标
    """
    date_obj = date.fromisoformat(target_date) if target_date else None
    metrics_data = await QfOverviewService.get_realtime_metrics_service(query_db, date_obj, store_name)
    logger.info('获取实时指标成功')

    return ResponseUtil.success(data=metrics_data)


@qf_controller.get(
    '/dashboard/realtime-trend',
    summary='获取实时走势',
    description='获取当天24小时的实时GMV走势数据',
    response_model=DataResponseModel,
)
async def get_realtime_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    target_date: Annotated[Optional[str], Query(description='目标日期，格式：YYYY-MM-DD')] = None,
    store_name: Annotated[Optional[str], Query(description='店铺名称，用于筛选')] = None,
) -> Response:
    """
    获取实时GMV走势
    """
    date_obj = date.fromisoformat(target_date) if target_date else None
    trend_data = await QfOverviewService.get_realtime_trend_service(query_db, date_obj, store_name)
    logger.info('获取实时走势数据成功')

    return ResponseUtil.success(data=trend_data)


@qf_controller.get(
    '/dashboard/top-stores',
    summary='获取热销店铺TOP10',
    description='获取销售量/订单量前十的店铺',
    response_model=DataResponseModel,
)
async def get_top_stores(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    target_date: Annotated[Optional[str], Query(description='目标日期，格式：YYYY-MM-DD')] = None,
    sort_by: Annotated[str, Query(description='排序方式：orders-按订单量，sales-按销售额')] = 'orders',
    limit: Annotated[int, Query(description='返回数量', ge=1, le=100)] = 10,
) -> Response:
    """
    获取热销店铺TOP排行
    """
    date_obj = date.fromisoformat(target_date) if target_date else None
    top_stores = await QfOverviewService.get_top_stores_service(query_db, date_obj, sort_by, limit)
    logger.info(f'获取热销店铺TOP{limit}成功，排序方式：{sort_by}')

    return ResponseUtil.success(data=top_stores)


@qf_controller.get(
    '/dashboard/realtime-orders',
    summary='获取实时订单',
    description='获取实时订单列表，支持店铺筛选和日期筛选',
    response_model=DataResponseModel,
)
async def get_realtime_orders(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    target_date: Annotated[Optional[str], Query(description='目标日期，格式：YYYY-MM-DD')] = None,
    store_name: Annotated[Optional[str], Query(description='店铺名称，用于筛选')] = None,
    limit: Annotated[int, Query(description='返回数量', ge=1, le=100)] = 20,
) -> Response:
    """
    获取实时订单列表
    """
    date_obj = date.fromisoformat(target_date) if target_date else None
    orders = await QfOverviewService.get_realtime_orders_service(query_db, date_obj, store_name, limit)
    logger.info(f'获取实时订单成功，日期：{target_date or "今天"}，店铺：{store_name or "全部"}，数量：{len(orders)}')

    return ResponseUtil.success(data=orders)


@qf_controller.get(
    '/dashboard/sku-sales-data',
    summary='获取SKU销售数据',
    description='获取SKU销售数据，按销量或销售额排序',
    response_model=DataResponseModel,
)
async def get_sku_sales_data(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    target_date: Annotated[Optional[str], Query(description='目标日期，格式：YYYY-MM-DD')] = None,
    sort_by: Annotated[str, Query(description='排序方式：sales-按销量，amount-按销售额')] = 'sales',
) -> Response:
    """
    获取SKU销售数据
    """
    date_obj = date.fromisoformat(target_date) if target_date else None
    sku_data = await QfOverviewService.get_sku_sales_data_service(query_db, date_obj, sort_by)
    logger.info(f'获取SKU销售数据成功，排序方式：{sort_by}，数量：{len(sku_data)}')

    return ResponseUtil.success(data=sku_data)


@qf_controller.get(
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


@qf_controller.get(
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


@qf_controller.get(
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


@qf_controller.get(
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


@qf_controller.get(
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


@qf_controller.get(
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
