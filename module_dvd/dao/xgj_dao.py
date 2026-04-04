from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.entity.do.xgj_order_stats_do import XgjOrderStats
from module_dvd.entity.do.xgj_real_product_stats_do import XgjRealProductStats
from module_dvd.entity.do.xgj_real_today_stats_do import XgjRealTodayStats


class XgjOverviewDao:
    """
    闲鱼大屏数据访问层
    """

    @classmethod
    async def get_store_list(cls, db: AsyncSession, dvd_data_scope=None) -> list[dict[str, Any]]:
        """
        获取店铺列表

        :param db: orm对象
        :param dvd_data_scope: 数据权限子查询
        :return: 店铺列表
        """
        query = (
            select(XgjOrderStats.store_name)
            .distinct()
            .where(XgjOrderStats.store_name.isnot(None))
        )
        if dvd_data_scope is not None:
            query = query.where(XgjOrderStats.bind_user_id.in_(dvd_data_scope))
        query = query.order_by(XgjOrderStats.store_name)

        result = await db.execute(query)
        rows = result.scalars().all()
        return [{'storeName': store_name} for store_name in rows]

    @classmethod
    async def get_product_status_distribution(
        cls,
        db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取商品状态分布

        按当前筛选条件，只取最新采集日期下最大的采集小时对应的那一批数据进行汇总。

        :param db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param dvd_data_scope: 数据权限子查询
        :return: 商品状态分布
        """
        status_fields = [
            ('waitPublishNum', XgjRealProductStats.wait_publish_num),
            ('sellingNum', XgjRealProductStats.selling_num),
            ('auctioningNum', XgjRealProductStats.auctioning_num),
            ('onSaleStockNum', XgjRealProductStats.on_sale_stock_num),
            ('soldOffShelfNum', XgjRealProductStats.sold_off_shelf_num),
            ('auctionOffShelfNum', XgjRealProductStats.auction_off_shelf_num),
            ('afterSaleRestoreNum', XgjRealProductStats.after_sale_restore_num),
            ('processingNum', XgjRealProductStats.processing_num),
        ]

        filters = []
        if store_name:
            filters.append(XgjRealProductStats.store_name == store_name)
        if store_id:
            filters.append(XgjRealProductStats.store_id == store_id)
        if dvd_data_scope is not None:
            filters.append(XgjRealProductStats.bind_user_id.in_(dvd_data_scope))

        latest_date_query = select(
            func.max(XgjRealProductStats.collect_date).label('latest_collect_date')
        )
        if filters:
            latest_date_query = latest_date_query.where(*filters)
        latest_collect_date = (await db.execute(latest_date_query)).scalar_one_or_none()

        if latest_collect_date is None:
            return {
                'stats': [{'key': key, 'value': 0} for key, _field in status_fields],
                'total': 0,
                'latestCollectTime': None,
            }

        latest_hour_query = select(
            func.max(XgjRealProductStats.collect_hour).label('latest_collect_hour')
        ).where(*filters, XgjRealProductStats.collect_date == latest_collect_date)
        latest_collect_hour = (await db.execute(latest_hour_query)).scalar_one_or_none()

        if latest_collect_hour is None:
            return {
                'stats': [{'key': key, 'value': 0} for key, _field in status_fields],
                'total': 0,
                'latestCollectTime': None,
            }

        aggregate_query = select(
            *[func.sum(field).label(key) for key, field in status_fields],
        ).where(
            *filters,
            XgjRealProductStats.collect_date == latest_collect_date,
            XgjRealProductStats.collect_hour == latest_collect_hour,
        )

        result = await db.execute(aggregate_query)
        row = result.one_or_none()

        stats: list[dict[str, Any]] = []
        total = 0
        for key, _field in status_fields:
            value = int(round(float(getattr(row, key, 0) or 0)))
            total += value
            stats.append({'key': key, 'value': value})

        latest_collect_time = f"{latest_collect_date} {int(latest_collect_hour):02d}:00:00"

        return {
            'stats': stats,
            'total': total,
            'latestCollectTime': latest_collect_time,
        }

    @classmethod
    async def get_top_store_ranking(
        cls,
        db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        limit: int = 100,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取Top店铺排行

        按当前筛选条件，只取最新采集日期下最大的采集小时对应的那一批数据，
        按今日支付金额倒序、今日支付订单数倒序返回店铺排行。

        :param db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param limit: 返回数量
        :param dvd_data_scope: 数据权限子查询
        :return: Top店铺排行
        """
        filters = [XgjRealTodayStats.store_name.isnot(None)]
        if store_name:
            filters.append(XgjRealTodayStats.store_name == store_name)
        if store_id:
            filters.append(XgjRealTodayStats.store_id == store_id)
        if dvd_data_scope is not None:
            filters.append(XgjRealTodayStats.bind_user_id.in_(dvd_data_scope))

        latest_date_query = select(
            func.max(XgjRealTodayStats.collect_date).label('latest_collect_date')
        ).where(*filters)
        latest_collect_date = (await db.execute(latest_date_query)).scalar_one_or_none()

        if latest_collect_date is None:
            return {
                'items': [],
                'latestCollectTime': None,
            }

        latest_hour_query = select(
            func.max(XgjRealTodayStats.collect_hour).label('latest_collect_hour')
        ).where(*filters, XgjRealTodayStats.collect_date == latest_collect_date)
        latest_collect_hour = (await db.execute(latest_hour_query)).scalar_one_or_none()

        if latest_collect_hour is None:
            return {
                'items': [],
                'latestCollectTime': None,
            }

        ranking_query = (
            select(
                XgjRealTodayStats.store_name.label('store_name'),
                XgjRealTodayStats.store_id.label('store_id'),
                func.sum(XgjRealTodayStats.pay_amount_today).label('pay_amount_today'),
                func.sum(XgjRealTodayStats.pay_order_num_today).label('pay_order_num_today'),
            )
            .where(
                *filters,
                XgjRealTodayStats.collect_date == latest_collect_date,
                XgjRealTodayStats.collect_hour == latest_collect_hour,
            )
            .group_by(XgjRealTodayStats.store_name, XgjRealTodayStats.store_id)
            .order_by(
                desc(func.sum(XgjRealTodayStats.pay_amount_today)),
                desc(func.sum(XgjRealTodayStats.pay_order_num_today)),
                XgjRealTodayStats.store_name.asc(),
            )
            .limit(limit)
        )

        result = await db.execute(ranking_query)
        rows = result.all()

        items = []
        for row in rows:
            pay_amount_today = round(float(row.pay_amount_today or 0), 2)
            pay_order_num_today = int(round(float(row.pay_order_num_today or 0)))
            items.append(
                {
                    'name': row.store_name,
                    'storeId': row.store_id,
                    'payAmountToday': pay_amount_today,
                    'payOrderNumToday': pay_order_num_today,
                }
            )

        latest_collect_time = f"{latest_collect_date} {int(latest_collect_hour):02d}:00:00"

        return {
            'items': items,
            'latestCollectTime': latest_collect_time,
        }
