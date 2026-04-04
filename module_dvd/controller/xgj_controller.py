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
    '/dashboard/overview-metrics',
    summary='获取经营核心指标',
    description='按当天最新采集小时查询经营核心指标，用于经营核心指标卡片展示',
    response_model=DataResponseModel,
)
async def get_overview_metrics(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    dvd_data_scope: Annotated[Optional[object], DvdDataScopeDependency()],
    store_name: Annotated[Optional[str], Query(description='店铺名称，用于筛选')] = None,
    store_id: Annotated[Optional[str], Query(description='店铺ID，用于筛选')] = None,
) -> Response:
    """
    获取经营核心指标
    """
    metrics = await XgjOverviewService.get_overview_metrics_service(
        query_db, store_name, store_id, dvd_data_scope
    )
    logger.info(f'获取闲鱼经营核心指标成功，店铺名称：{store_name}，店铺ID：{store_id}')

    return ResponseUtil.success(data=metrics)


@xgj_controller.get(
    '/dashboard/pay-order-trend',
    summary='获取支付订单数小时走势图',
    description='按当天 0-23 点查询支付订单数走势，用于经营核心指标趋势图展示',
    response_model=DataResponseModel,
)
async def get_pay_order_trend(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    dvd_data_scope: Annotated[Optional[object], DvdDataScopeDependency()],
    store_name: Annotated[Optional[str], Query(description='店铺名称，用于筛选')] = None,
    store_id: Annotated[Optional[str], Query(description='店铺ID，用于筛选')] = None,
) -> Response:
    """
    获取支付订单数小时走势图
    """
    trend_data = await XgjOverviewService.get_pay_order_trend_service(
        query_db, store_name, store_id, dvd_data_scope
    )
    logger.info(f'获取闲鱼支付订单数小时走势图成功，店铺名称：{store_name}，店铺ID：{store_id}')

    return ResponseUtil.success(data=trend_data)


@xgj_controller.get(
    '/dashboard/product-status-distribution',
    summary='获取商品状态分布',
    description='按店铺筛选并汇总当天最新小时的商品状态快照，用于商品状态分布图',
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
    description='按当天最新采集小时查询Top店铺排行，用于Top店铺列表展示',
    response_model=DataResponseModel,
)
async def get_top_store_ranking(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    dvd_data_scope: Annotated[Optional[object], DvdDataScopeDependency()],
    store_name: Annotated[Optional[str], Query(description='店铺名称，用于筛选')] = None,
    store_id: Annotated[Optional[str], Query(description='店铺ID，用于筛选')] = None,
    sort_by: Annotated[Optional[str], Query(description='排序字段：amount-今日支付金额，orders-今日支付订单')] = 'amount',
    limit: Annotated[int, Query(description='返回数量，默认100')] = 100,
) -> Response:
    """
    获取Top店铺排行
    """
    stats = await XgjOverviewService.get_top_store_ranking_service(
        query_db, store_name, store_id, sort_by, limit, dvd_data_scope
    )
    logger.info(
        f'获取闲鱼Top店铺排行成功，店铺名称：{store_name}，店铺ID：{store_id}，排序字段：{sort_by}，返回数量：{limit}'
    )

    return ResponseUtil.success(data=stats)


@xgj_controller.get(
    '/dashboard/order-risk-summary',
    summary='获取售后预警与监控摘要',
    description='按当天最新采集小时查询所有订单数量和交易关闭数量，用于售后预警与监控展示',
    response_model=DataResponseModel,
)
async def get_order_risk_summary(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    dvd_data_scope: Annotated[Optional[object], DvdDataScopeDependency()],
    store_name: Annotated[Optional[str], Query(description='店铺名称，用于筛选')] = None,
    store_id: Annotated[Optional[str], Query(description='店铺ID，用于筛选')] = None,
) -> Response:
    """
    获取售后预警与监控摘要
    """
    stats = await XgjOverviewService.get_order_risk_summary_service(
        query_db, store_name, store_id, dvd_data_scope
    )
    logger.info(
        f'获取闲鱼售后预警与监控摘要成功，店铺名称：{store_name}，店铺ID：{store_id}'
    )

    return ResponseUtil.success(data=stats)
