from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.dao.qf_dao import QfOverviewDao


class QfOverviewService:
    """
    千帆数据概览服务层
    """

    @classmethod
    async def get_store_list_service(cls, query_db: AsyncSession) -> list[dict[str, Any]]:
        """
        获取店铺列表service
        
        :param query_db: orm对象
        :return: 店铺列表
        """
        return await QfOverviewDao.get_store_list(query_db)

    @classmethod
    async def get_realtime_metrics_service(
        cls, query_db: AsyncSession, target_date: date = None, store_name: str = None
    ) -> dict[str, Any]:
        """
        获取实时指标service
        
        :param query_db: orm对象
        :param target_date: 目标日期
        :param store_name: 店铺名称
        :return: 实时指标数据
        """
        return await QfOverviewDao.get_realtime_metrics(query_db, target_date, store_name)

    @classmethod
    async def get_realtime_trend_service(
        cls, query_db: AsyncSession, target_date: date = None, store_name: str = None
    ) -> dict[str, Any]:
        """
        获取实时GMV走势service
        
        :param query_db: orm对象
        :param target_date: 目标日期
        :param store_name: 店铺名称
        :return: 实时趋势数据
        """
        return await QfOverviewDao.get_realtime_trend(query_db, target_date, store_name)

    @classmethod
    async def get_top_stores_service(
        cls, query_db: AsyncSession, target_date: date = None, sort_by: str = 'orders', limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取热销店铺TOP排行service
        
        :param query_db: orm对象
        :param target_date: 目标日期
        :param sort_by: 排序方式
        :param limit: 返回数量
        :return: 店铺排行数据
        """
        return await QfOverviewDao.get_top_stores(query_db, target_date, sort_by, limit)

    @classmethod
    async def get_realtime_orders_service(
        cls, query_db: AsyncSession, target_date: date = None, store_name: str = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        获取实时订单列表service
        
        :param query_db: orm对象
        :param target_date: 目标日期
        :param store_name: 店铺名称
        :param limit: 返回数量
        :return: 订单列表
        """
        return await QfOverviewDao.get_realtime_orders(query_db, target_date, store_name, limit)

    @classmethod
    async def get_dashboard_metrics_service(cls, query_db: AsyncSession, target_date: date = None) -> dict[str, Any]:
        """
        获取大屏核心指标service
        
        :param query_db: orm对象
        :param target_date: 目标日期
        :return: 核心指标数据
        """
        return await QfOverviewDao.get_dashboard_metrics(query_db, target_date)

    @classmethod
    async def get_store_sales_rank_service(
        cls, query_db: AsyncSession, target_date: date = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取店铺销售排行service
        
        :param query_db: orm对象
        :param target_date: 目标日期
        :param limit: 返回数量
        :return: 店铺排行数据
        """
        return await QfOverviewDao.get_store_sales_rank(query_db, target_date, limit)

    @classmethod
    async def get_channel_sales_data_service(
        cls, query_db: AsyncSession, target_date: date = None
    ) -> list[dict[str, Any]]:
        """
        获取渠道销售数据service
        
        :param query_db: orm对象
        :param target_date: 目标日期
        :return: 渠道销售数据
        """
        return await QfOverviewDao.get_channel_sales_data(query_db, target_date)

    @classmethod
    async def get_recent_orders_service(cls, query_db: AsyncSession, limit: int = 20) -> list[dict[str, Any]]:
        """
        获取最近订单service
        
        :param query_db: orm对象
        :param limit: 返回数量
        :return: 订单列表
        """
        return await QfOverviewDao.get_recent_orders(query_db, limit)

    @classmethod
    async def get_trend_data_service(cls, query_db: AsyncSession, days: int = 7) -> dict[str, Any]:
        """
        获取趋势数据service
        
        :param query_db: orm对象
        :param days: 天数
        :return: 趋势数据
        """
        return await QfOverviewDao.get_trend_data(query_db, days)

    @classmethod
    async def get_sku_sales_data_service(
        cls, query_db: AsyncSession, target_date: date = None, sort_by: str = 'sales'
    ) -> list[dict[str, Any]]:
        """
        获取SKU销售数据service
        
        :param query_db: orm对象
        :param target_date: 目标日期
        :param sort_by: 排序方式
        :return: SKU销售数据列表
        """
        return await QfOverviewDao.get_sku_sales_data(query_db, target_date, sort_by)

    @classmethod
    async def get_all_dashboard_data_service(cls, query_db: AsyncSession, target_date: date = None) -> dict[str, Any]:
        """
        获取大屏所有数据service
        
        :param query_db: orm对象
        :param target_date: 目标日期
        :return: 大屏所有数据
        """
        metrics = await cls.get_dashboard_metrics_service(query_db, target_date)
        store_rank = await cls.get_store_sales_rank_service(query_db, target_date, 10)
        channel_data = await cls.get_channel_sales_data_service(query_db, target_date)
        recent_orders = await cls.get_recent_orders_service(query_db, 20)
        trend_data = await cls.get_trend_data_service(query_db, 7)

        return {
            'metrics': metrics,
            'storeRank': store_rank,
            'channelData': channel_data,
            'recentOrders': recent_orders,
            'trendData': trend_data,
        }

