from datetime import date
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.entity.do.xgj_order_stats_do import XgjOrderStats
from module_dvd.entity.do.xgj_real_order_stats_do import XgjRealOrderStats
from module_dvd.entity.do.xgj_real_product_stats_do import XgjRealProductStats
from module_dvd.entity.do.xgj_real_today_stats_do import XgjRealTodayStats


class XgjOverviewDao:
    """
    闲鱼大屏数据访问层
    """

    @staticmethod
    def _format_compare_rate(today_value: float, yesterday_value: float) -> tuple[str, str]:
        """
        格式化对比趋势

        :param today_value: 今日值
        :param yesterday_value: 昨日值
        :return: 趋势方向、百分比文本
        """
        if yesterday_value == 0:
            if today_value == 0:
                return 'flat', '0%'
            return 'up', '100%'

        diff_rate = ((today_value - yesterday_value) / yesterday_value) * 100
        if diff_rate > 0:
            trend = 'up'
        elif diff_rate < 0:
            trend = 'down'
        else:
            trend = 'flat'
        return trend, f"{abs(diff_rate):.1f}%"

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
    async def get_overview_metrics(
        cls,
        db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取经营核心指标

        按当前筛选条件，只取当天最大的采集小时对应的那一批数据进行汇总。

        :param db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param dvd_data_scope: 数据权限子查询
        :return: 经营核心指标
        """
        filters = []
        if store_name:
            filters.append(XgjRealTodayStats.store_name == store_name)
        if store_id:
            filters.append(XgjRealTodayStats.store_id == store_id)
        if dvd_data_scope is not None:
            filters.append(XgjRealTodayStats.bind_user_id.in_(dvd_data_scope))

        query_date = date.today()
        latest_hour_query = select(
            func.max(XgjRealTodayStats.collect_hour).label('latest_collect_hour')
        ).where(
            *filters,
            XgjRealTodayStats.collect_date == query_date,
        )
        latest_collect_hour = (await db.execute(latest_hour_query)).scalar_one_or_none()

        if latest_collect_hour is None:
            return {
                'metrics': [
                    {'label': '支付金额', 'symbol': '¥', 'unit': '¥', 'value': '0.00', 'previous': '昨日: ¥0.00', 'trend': 'flat', 'rate': '0%'},
                    {'label': '支付订单数', 'symbol': '单', 'value': '0', 'previous': '昨日: 0', 'trend': 'flat', 'rate': '0%'},
                    {'label': '支付客单价', 'symbol': '均', 'unit': '¥', 'value': '0.00', 'previous': '昨日: ¥0.00', 'trend': 'flat', 'rate': '0%'},
                    {'label': '新发布商品', 'symbol': '新', 'value': '0', 'previous': '昨日: 0', 'trend': 'flat', 'rate': '0%'},
                ],
                'latestCollectTime': None,
            }

        summary_query = select(
            func.sum(XgjRealTodayStats.pay_amount_today).label('pay_amount_today'),
            func.sum(XgjRealTodayStats.pay_amount_yesterday).label('pay_amount_yesterday'),
            func.sum(XgjRealTodayStats.pay_order_num_today).label('pay_order_num_today'),
            func.sum(XgjRealTodayStats.pay_order_num_yesterday).label('pay_order_num_yesterday'),
            func.sum(XgjRealTodayStats.new_product_num_today).label('new_product_num_today'),
            func.sum(XgjRealTodayStats.new_product_num_yesterday).label('new_product_num_yesterday'),
        ).where(
            *filters,
            XgjRealTodayStats.collect_date == query_date,
            XgjRealTodayStats.collect_hour == latest_collect_hour,
        )

        result = await db.execute(summary_query)
        row = result.one_or_none()

        pay_amount_today = float(getattr(row, 'pay_amount_today', 0) or 0)
        pay_amount_yesterday = float(getattr(row, 'pay_amount_yesterday', 0) or 0)
        pay_order_num_today = float(getattr(row, 'pay_order_num_today', 0) or 0)
        pay_order_num_yesterday = float(getattr(row, 'pay_order_num_yesterday', 0) or 0)
        new_product_num_today = float(getattr(row, 'new_product_num_today', 0) or 0)
        new_product_num_yesterday = float(getattr(row, 'new_product_num_yesterday', 0) or 0)

        unit_price_today = pay_amount_today / pay_order_num_today if pay_order_num_today else 0
        unit_price_yesterday = pay_amount_yesterday / pay_order_num_yesterday if pay_order_num_yesterday else 0

        pay_amount_trend, pay_amount_rate = cls._format_compare_rate(pay_amount_today, pay_amount_yesterday)
        pay_order_trend, pay_order_rate = cls._format_compare_rate(pay_order_num_today, pay_order_num_yesterday)
        unit_price_trend, unit_price_rate = cls._format_compare_rate(unit_price_today, unit_price_yesterday)
        new_product_trend, new_product_rate = cls._format_compare_rate(new_product_num_today, new_product_num_yesterday)

        latest_collect_time = f"{query_date} {int(latest_collect_hour):02d}:00:00"

        return {
            'metrics': [
                {
                    'label': '支付金额',
                    'symbol': '¥',
                    'unit': '¥',
                    'value': f"{pay_amount_today:,.2f}",
                    'previous': f"昨日: ¥{pay_amount_yesterday:,.2f}",
                    'trend': pay_amount_trend,
                    'rate': pay_amount_rate,
                },
                {
                    'label': '支付订单数',
                    'symbol': '单',
                    'value': f"{int(round(pay_order_num_today)):,}",
                    'previous': f"昨日: {int(round(pay_order_num_yesterday)):,}",
                    'trend': pay_order_trend,
                    'rate': pay_order_rate,
                },
                {
                    'label': '支付客单价',
                    'symbol': '均',
                    'unit': '¥',
                    'value': f"{unit_price_today:,.2f}",
                    'previous': f"昨日: ¥{unit_price_yesterday:,.2f}",
                    'trend': unit_price_trend,
                    'rate': unit_price_rate,
                },
                {
                    'label': '新发布商品',
                    'symbol': '新',
                    'value': f"{int(round(new_product_num_today)):,}",
                    'previous': f"昨日: {int(round(new_product_num_yesterday)):,}",
                    'trend': new_product_trend,
                    'rate': new_product_rate,
                },
            ],
            'latestCollectTime': latest_collect_time,
        }

    @classmethod
    async def get_pay_order_trend(
        cls,
        db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取支付订单数小时走势图

        按当前筛选条件，查询当天 0-23 点各小时的支付订单数，
        用于经营核心指标区域的趋势图展示。

        :param db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param dvd_data_scope: 数据权限子查询，None 表示不过滤
        :return: 支付订单数小时走势图
        """
        filters = []
        if store_name:
            filters.append(XgjRealTodayStats.store_name == store_name)
        if store_id:
            filters.append(XgjRealTodayStats.store_id == store_id)
        if dvd_data_scope is not None:
            filters.append(XgjRealTodayStats.bind_user_id.in_(dvd_data_scope))

        query_date = date.today()
        trend_query = (
            select(
                XgjRealTodayStats.collect_hour,
                func.sum(XgjRealTodayStats.pay_order_num_today).label('pay_order_num_today'),
            )
            .where(
                *filters,
                XgjRealTodayStats.collect_date == query_date,
            )
            .group_by(XgjRealTodayStats.collect_hour)
            .order_by(XgjRealTodayStats.collect_hour)
        )

        result = await db.execute(trend_query)
        rows = result.all()

        hour_value_map = {
            int(row.collect_hour): int(round(float(row.pay_order_num_today or 0)))
            for row in rows
            if row.collect_hour is not None
        }
        latest_collect_hour = max(hour_value_map.keys(), default=None)

        labels = [f'{hour:02d}:00' for hour in range(24)]
        values = [hour_value_map.get(hour, 0) for hour in range(24)]

        return {
            'labels': labels,
            'values': values,
            'latestCollectHour': latest_collect_hour,
            'latestCollectTime': (
                f"{query_date} {int(latest_collect_hour):02d}:00:00"
                if latest_collect_hour is not None
                else None
            ),
        }

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

        query_date = date.today()
        latest_hour_query = select(
            func.max(XgjRealProductStats.collect_hour).label('latest_collect_hour')
        ).where(
            *filters,
            XgjRealProductStats.collect_date == query_date,
        )
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
            XgjRealProductStats.collect_date == query_date,
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

        latest_collect_time = f"{query_date} {int(latest_collect_hour):02d}:00:00"

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
        sort_by: str = 'amount',
        limit: int = 100,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取Top店铺排行

        按当前筛选条件，只取当天最大的采集小时对应的那一批数据，
        按指定字段返回店铺排行。

        :param db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param sort_by: 排序字段，amount-今日支付金额，orders-今日支付订单
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

        query_date = date.today()
        latest_hour_query = select(
            func.max(XgjRealTodayStats.collect_hour).label('latest_collect_hour')
        ).where(*filters, XgjRealTodayStats.collect_date == query_date)
        latest_collect_hour = (await db.execute(latest_hour_query)).scalar_one_or_none()

        if latest_collect_hour is None:
            return {
                'items': [],
                'latestCollectTime': None,
            }

        amount_sort_expr = desc(func.sum(XgjRealTodayStats.pay_amount_today))
        order_sort_expr = desc(func.sum(XgjRealTodayStats.pay_order_num_today))
        sort_expressions = (
            [order_sort_expr, amount_sort_expr]
            if sort_by == 'orders'
            else [amount_sort_expr, order_sort_expr]
        )

        ranking_query = (
            select(
                XgjRealTodayStats.store_name.label('store_name'),
                XgjRealTodayStats.store_id.label('store_id'),
                func.sum(XgjRealTodayStats.pay_amount_today).label('pay_amount_today'),
                func.sum(XgjRealTodayStats.pay_order_num_today).label('pay_order_num_today'),
            )
            .where(
                *filters,
                XgjRealTodayStats.collect_date == query_date,
                XgjRealTodayStats.collect_hour == latest_collect_hour,
            )
            .group_by(XgjRealTodayStats.store_name, XgjRealTodayStats.store_id)
            .order_by(
                *sort_expressions,
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

        latest_collect_time = f"{query_date} {int(latest_collect_hour):02d}:00:00"

        return {
            'items': items,
            'latestCollectTime': latest_collect_time,
        }

    @classmethod
    async def get_order_risk_summary(
        cls,
        db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取售后预警与监控摘要

        按当前筛选条件，只取当天最大的采集小时对应的那一批订单数据进行汇总。

        :param db: orm对象
        :param store_name: 店铺名称
        :param store_id: 店铺ID
        :param dvd_data_scope: 数据权限子查询
        :return: 售后预警与监控摘要
        """
        filters = []
        if store_name:
            filters.append(XgjRealOrderStats.store_name == store_name)
        if store_id:
            filters.append(XgjRealOrderStats.store_id == store_id)
        if dvd_data_scope is not None:
            filters.append(XgjRealOrderStats.bind_user_id.in_(dvd_data_scope))

        query_date = date.today()
        latest_hour_query = select(
            func.max(XgjRealOrderStats.collect_hour).label('latest_collect_hour')
        ).where(
            *filters,
            XgjRealOrderStats.collect_date == query_date,
        )
        latest_collect_hour = (await db.execute(latest_hour_query)).scalar_one_or_none()

        if latest_collect_hour is None:
            return {
                'allOrderNum': 0,
                'closedOrderNum': 0,
                'latestCollectTime': None,
            }

        summary_query = select(
            func.sum(XgjRealOrderStats.all_order_num).label('all_order_num'),
            func.sum(XgjRealOrderStats.closed_order_num).label('closed_order_num'),
        ).where(
            *filters,
            XgjRealOrderStats.collect_date == query_date,
            XgjRealOrderStats.collect_hour == latest_collect_hour,
        )

        result = await db.execute(summary_query)
        row = result.one_or_none()

        all_order_num = int(round(float(getattr(row, 'all_order_num', 0) or 0)))
        closed_order_num = int(round(float(getattr(row, 'closed_order_num', 0) or 0)))
        latest_collect_time = f"{query_date} {int(latest_collect_hour):02d}:00:00"

        return {
            'allOrderNum': all_order_num,
            'closedOrderNum': closed_order_num,
            'latestCollectTime': latest_collect_time,
        }
