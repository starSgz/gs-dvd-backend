from datetime import date, datetime
from typing import Any, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_dvd.dao.dd_dao import DdOverviewDao, DdOrderListDao


class DdOverviewService:
    """
    抖店数据概览服务层
    """

    @classmethod
    async def get_store_list_service(cls, query_db: AsyncSession, dvd_data_scope=None) -> list[dict[str, Any]]:
        """
        获取店铺列表service
        
        :param query_db: orm对象
        :param dvd_data_scope: 数据权限子查询
        :return: 店铺列表
        """
        return await DdOverviewDao.get_store_list(query_db, dvd_data_scope)

    @classmethod
    async def get_store_service(
        cls, 
        query_db: AsyncSession, 
        store_id: str = None,
        sort_by: str = 'amount', 
        limit: int = 100,
        dvd_data_scope=None,
    ) -> list[dict[str, Any]]:
        """
        获取店铺 service
        
        :param query_db: orm对象
        :param store_id: 店铺ID筛选
        :param sort_by: 排序方式，'amount'-按成交金额，'orders'-按订单数
        :param limit: 返回数量
        :param dvd_data_scope: 数据权限子查询
        :return: 店铺列表
        """
        return await DdOverviewDao.get_store(query_db, store_id, sort_by, limit, dvd_data_scope)

    @classmethod
    async def get_overview_metrics_service(
        cls,
        query_db: AsyncSession,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取抖店概览指标数据 service
        
        :param query_db: orm对象
        :param store_id: 店铺ID筛选
        :param dvd_data_scope: 数据权限子查询
        :return: 概览指标数据
        """
        return await DdOverviewDao.get_overview_metrics(query_db, store_id, dvd_data_scope)

    @classmethod
    async def get_hourly_trend_service(
        cls,
        query_db: AsyncSession,
        store_id: str = None,
        index_display: str = None,
        dvd_data_scope=None,
    ) -> list[dict[str, Any]]:
        """
        获取小时趋势 service
        
        :param query_db: orm对象
        :param store_id: 店铺ID筛选
        :param index_display: 指标显示名称筛选
        :param dvd_data_scope: 数据权限子查询
        :return: 24小时趋势数据
        """
        return await DdOverviewDao.get_hourly_trend(query_db, store_id, index_display, dvd_data_scope)

    @classmethod
    async def get_available_indices_service(
        cls,
        query_db: AsyncSession,
        dvd_data_scope=None,
    ) -> list[dict[str, Any]]:
        """
        获取可用的指标列表 service
        
        :param query_db: orm对象
        :param dvd_data_scope: 数据权限子查询
        :return: 指标列表
        """
        return await DdOverviewDao.get_available_indices(query_db, dvd_data_scope)

    @classmethod
    async def get_daily_overview_metrics_service(
        cls,
        query_db: AsyncSession,
        start_date: date = None,
        end_date: date = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取每日概览指标数据 service（支持日期范围聚合）

        :param query_db: orm对象
        :param start_date: 开始日期，为 None 时不过滤
        :param end_date: 结束日期，为 None 时不过滤
        :param store_id: 店铺ID筛选
        :param dvd_data_scope: 数据权限子查询
        :return: 日期范围内聚合的概览指标数据
        """
        return await DdOverviewDao.get_daily_overview_metrics(query_db, start_date, end_date, store_id, dvd_data_scope)

    @classmethod
    async def get_geo_order_stats_service(
        cls,
        query_db: AsyncSession,
        level: str = 'province',
        parent_province: str = None,
        parent_city: str = None,
        store_id: str = None,
        start_date: date = None,
        end_date: date = None,
        dvd_data_scope=None,
    ) -> list[dict[str, Any]]:
        """
        按地理层级聚合订单支付金额和订单数 service（用于地图展示）

        :param query_db: orm对象
        :param level: 聚合层级，'province'按省份、'city'按城市、'town'按区县
        :param parent_province: 父级省份名称（level='city'/'town'时生效）
        :param parent_city: 父级城市名称（level='town'时生效）
        :param store_id: 店铺ID筛选（可选）
        :param start_date: 采集日期开始（可选）
        :param end_date: 采集日期结束（可选）
        :param dvd_data_scope: 数据权限子查询
        :return: 地理聚合数据列表
        """
        return await DdOrderListDao.get_geo_order_stats(   
            query_db, level, parent_province, parent_city, store_id, start_date, end_date, dvd_data_scope
        )

    @classmethod
    async def get_traffic_trend_service(
        cls,
        query_db: AsyncSession,
        start_date: date = None,
        end_date: date = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> list[dict]:
        """
        按日期查询商品曝光/点击流量趋势 service（用于柱线混合图）

        :param query_db: orm对象
        :param start_date: 开始日期，为 None 时不过滤
        :param end_date: 结束日期，为 None 时不过滤
        :param store_id: 店铺ID筛选（可选）
        :param dvd_data_scope: 数据权限子查询
        :return: 按日期升序排列的流量趋势列表
        """
        return await DdOverviewDao.get_traffic_trend(
            query_db, start_date, end_date, store_id, dvd_data_scope
        )

    @classmethod
    async def get_category_stats_service(
        cls,
        query_db: AsyncSession,
        start_date: date = None,
        end_date: date = None,
        store_id: str = None,
        top_n: int = 10,
        dvd_data_scope=None,
    ) -> dict:
        """
        按商品名称和商品规格聚合订单数量 service（用于玫瑰图展示）

        :param query_db: orm对象
        :param start_date: 采集日期开始（可选）
        :param end_date: 采集日期结束（可选）
        :param store_id: 店铺ID筛选（可选）
        :param top_n: 取前N条记录
        :param dvd_data_scope: 数据权限子查询
        :return: 包含 productStats 和 skuStats 的字典
        """
        return await DdOrderListDao.get_category_stats(
            query_db, start_date, end_date, store_id, top_n, dvd_data_scope
        )

    @classmethod
    async def get_order_list_service(
        cls,
        query_db: AsyncSession,
        start_date: date = None,
        end_date: date = None,
        store_id: str = None,
        order_status_text: str = None,
        page_num: int = 1,
        page_size: int = 20,
        dvd_data_scope=None,
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取抖店订单列表 service（支持日期范围 + 分页）

        :param query_db: orm对象
        :param start_date: 开始日期，为 None 时不过滤
        :param end_date: 结束日期，为 None 时不过滤
        :param store_id: 店铺ID筛选
        :param order_status_text: 订单状态筛选
        :param page_num: 当前页码
        :param page_size: 每页记录数
        :param dvd_data_scope: 数据权限子查询
        :return: 分页订单列表
        """
        return await DdOrderListDao.get_order_list(
            query_db, start_date, end_date, store_id, order_status_text, page_num, page_size, dvd_data_scope
        )
