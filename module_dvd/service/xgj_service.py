from typing import Any

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
        limit: int = 100,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取Top店铺排行

        :param query_db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param limit: 返回数量
        :param dvd_data_scope: 数据权限子查询
        :return: Top店铺排行
        """
        return await XgjOverviewDao.get_top_store_ranking(
            query_db, store_name, store_id, limit, dvd_data_scope
        )
