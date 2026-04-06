from typing import Any
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.dao.xgj_dao import XgjOverviewDao


class XgjOverviewService:
    """
    闲鱼大屏服务层
    """

    @classmethod
    async def get_store_list_service(cls, query_db: AsyncSession, dvd_data_scope=None) -> list[dict[str, Any]]:
        """
        获取店铺列表

        :param query_db: orm对象
        :param dvd_data_scope: 数据权限子查询
        :return: 店铺列表
        """
        return await XgjOverviewDao.get_store_list(query_db, dvd_data_scope)

    @classmethod
    async def get_overview_metrics_service(
        cls,
        query_db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取经营核心指标

        :param query_db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param dvd_data_scope: 数据权限子查询
        :return: 经营核心指标
        """
        return await XgjOverviewDao.get_overview_metrics(
            query_db, store_name, store_id, dvd_data_scope
        )

    @classmethod
    async def get_pay_order_trend_service(
        cls,
        query_db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取支付订单数小时走势图

        :param query_db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param dvd_data_scope: 数据权限子查询
        :return: 支付订单数小时走势图
        """
        return await XgjOverviewDao.get_pay_order_trend(
            query_db, store_name, store_id, dvd_data_scope
        )

    @classmethod
    async def get_daily_order_analysis_service(
        cls,
        query_db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        start_date: date = None,
        end_date: date = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取经营数据日维度分析

        :param query_db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param dvd_data_scope: 数据权限子查询
        :return: 日维度趋势分析数据
        """
        return await XgjOverviewDao.get_daily_order_analysis(
            query_db, store_name, store_id, start_date, end_date, dvd_data_scope
        )

    @classmethod
    async def get_product_status_distribution_service(
        cls,
        query_db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取商品状态分布

        :param query_db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param dvd_data_scope: 数据权限子查询
        :return: 商品状态分布
        """
        return await XgjOverviewDao.get_product_status_distribution(
            query_db, store_name, store_id, dvd_data_scope
        )

    @classmethod
    async def get_top_store_ranking_service(
        cls,
        query_db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        sort_by: str = 'amount',
        limit: int = 100,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取Top店铺排行

        :param query_db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param sort_by: 排序字段
        :param limit: 返回数量
        :param dvd_data_scope: 数据权限子查询
        :return: Top店铺排行
        """
        return await XgjOverviewDao.get_top_store_ranking(
            query_db, store_name, store_id, sort_by, limit, dvd_data_scope
        )

    @classmethod
    async def get_shop_order_flow_service(
        cls,
        query_db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取店铺订单流转数据
        :param query_db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param dvd_data_scope: 数据权限子查询
        :return: 店铺订单流转数据
        """
        return await XgjOverviewDao.get_shop_order_flow(
            query_db, store_name, store_id, dvd_data_scope
        )

    @classmethod
    async def get_order_risk_summary_service(
        cls,
        query_db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取售后预警与监控摘要

        :param query_db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param dvd_data_scope: 数据权限子查询
        :return: 售后预警与监控摘要
        """
        return await XgjOverviewDao.get_order_risk_summary(
            query_db, store_name, store_id, dvd_data_scope
        )
