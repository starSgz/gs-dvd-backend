from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.dao.dd_dao import DdOverviewDao


class DdOverviewService:
    """
    抖店数据概览服务层
    """

    @classmethod
    async def get_store_list_service(cls, query_db: AsyncSession) -> list[dict[str, Any]]:
        """
        获取店铺列表service
        
        :param query_db: orm对象
        :return: 店铺列表
        """
        return await DdOverviewDao.get_store_list(query_db)

    @classmethod
    async def get_store_top5_service(
        cls, 
        query_db: AsyncSession, 
        store_id: str = None,
        sort_by: str = 'amount', 
        limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        获取店铺TOP5 service
        
        :param query_db: orm对象
        :param store_id: 店铺ID筛选
        :param sort_by: 排序方式，'amount'-按成交金额，'orders'-按订单数
        :param limit: 返回数量
        :return: TOP5店铺列表
        """
        return await DdOverviewDao.get_store_top5(query_db, store_id, sort_by, limit)

    @classmethod
    async def get_overview_metrics_service(
        cls,
        query_db: AsyncSession,
        store_id: str = None
    ) -> dict[str, Any]:
        """
        获取抖店概览指标数据 service
        
        :param query_db: orm对象
        :param store_id: 店铺ID筛选
        :return: 概览指标数据
        """
        return await DdOverviewDao.get_overview_metrics(query_db, store_id)

    @classmethod
    async def get_hourly_trend_service(
        cls,
        query_db: AsyncSession,
        store_id: str = None,
        index_display: str = None
    ) -> list[dict[str, Any]]:
        """
        获取小时趋势 service
        
        :param query_db: orm对象
        :param store_id: 店铺ID筛选
        :param index_display: 指标显示名称筛选
        :return: 24小时趋势数据
        """
        return await DdOverviewDao.get_hourly_trend(query_db, store_id, index_display)

    @classmethod
    async def get_available_indices_service(
        cls,
        query_db: AsyncSession
    ) -> list[dict[str, Any]]:
        """
        获取可用的指标列表 service
        
        :param query_db: orm对象
        :return: 指标列表
        """
        return await DdOverviewDao.get_available_indices(query_db)
