from datetime import date
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.entity.do.xgj_order_stats_do import XgjOrderStats
from module_dvd.entity.do.xgj_real_order_stats_do import XgjRealOrderStats
from module_dvd.entity.do.xgj_real_product_stats_do import XgjRealProductStats
from module_dvd.entity.do.xgj_real_refund_stats_do import XgjRealRefundStats
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

    @staticmethod
    def _normalize_date_range(start_date, end_date):
        """
        规范化日期范围，避免开始日期晚于结束日期。
        """
        if start_date and end_date and start_date > end_date:
            return end_date, start_date
        return start_date, end_date

    @staticmethod
    async def _get_today_latest_collect_hour(db: AsyncSession, model, filters: list):
        query_date = date.today()
        latest_hour_query = select(
            func.max(model.collect_hour).label('latest_collect_hour')
        ).where(
            *filters,
            model.collect_date == query_date,
        )
        latest_collect_hour = (await db.execute(latest_hour_query)).scalar_one_or_none()
        return query_date, latest_collect_hour

    @staticmethod
    def _build_latest_collect_time(query_date: date, latest_collect_hour):
        if latest_collect_hour is None:
            return None
        return f"{query_date} {int(latest_collect_hour):02d}:00:00"

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
    async def get_daily_order_analysis(
        cls,
        db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        start_date=None,
        end_date=None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取经营数据日维度分析

        基于 xgj_order_stats 按天聚合，支持店铺和日期范围筛选，
        用于订单数量/支付金额，以及退款/关闭相关趋势图展示。
        """
        start_date, end_date = cls._normalize_date_range(start_date, end_date)

        query = select(
            XgjOrderStats.collect_date,
            func.sum(XgjOrderStats.all_order_num).label('all_order_num'),
            func.sum(XgjOrderStats.paid_order_amount).label('paid_order_amount'),
            func.sum(XgjOrderStats.refund_order_num).label('refund_order_num'),
            func.sum(XgjOrderStats.refund_order_amount).label('refund_order_amount'),
            func.sum(XgjOrderStats.closed_order_num).label('closed_order_num'),
            func.sum(XgjOrderStats.closed_order_amount).label('closed_order_amount'),
        ).where(XgjOrderStats.collect_date.isnot(None))

        if store_name:
            query = query.where(XgjOrderStats.store_name == store_name)
        if store_id:
            query = query.where(XgjOrderStats.store_id == store_id)
        if start_date is not None:
            query = query.where(XgjOrderStats.collect_date >= start_date)
        if end_date is not None:
            query = query.where(XgjOrderStats.collect_date <= end_date)
        if dvd_data_scope is not None:
            query = query.where(XgjOrderStats.bind_user_id.in_(dvd_data_scope))

        query = query.group_by(XgjOrderStats.collect_date).order_by(XgjOrderStats.collect_date)

        result = await db.execute(query)
        rows = result.all()

        return {
            'startDate': str(start_date) if start_date else '',
            'endDate': str(end_date) if end_date else '',
            'dates': [str(row.collect_date) for row in rows],
            'orderNumSeries': [int(round(float(row.all_order_num or 0))) for row in rows],
            'payAmountSeries': [round(float(row.paid_order_amount or 0), 2) for row in rows],
            'refundOrderNumSeries': [int(round(float(row.refund_order_num or 0))) for row in rows],
            'refundAmountSeries': [round(float(row.refund_order_amount or 0), 2) for row in rows],
            'closedOrderNumSeries': [int(round(float(row.closed_order_num or 0))) for row in rows],
            'closedAmountSeries': [round(float(row.closed_order_amount or 0), 2) for row in rows],
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
                'sellingEfficiency': '0%',
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

        selling_num = float(getattr(row, 'sellingNum', 0) or 0)
        on_sale_stock_num = float(getattr(row, 'onSaleStockNum', 0) or 0)
        selling_efficiency_denominator = selling_num + on_sale_stock_num
        selling_efficiency = '0%'
        if selling_efficiency_denominator > 0:
            selling_efficiency_value = (selling_num / selling_efficiency_denominator) * 100
            selling_efficiency = f"{selling_efficiency_value:.2f}".rstrip('0').rstrip('.') + '%'

        latest_collect_time = f"{query_date} {int(latest_collect_hour):02d}:00:00"

        return {
            'stats': stats,
            'total': total,
            'sellingEfficiency': selling_efficiency,
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
    async def get_shop_order_flow(
        cls,
        db: AsyncSession,
        store_name: str = None,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取店铺订单流转数据
        """
        today_filters = []
        refund_filters = []

        if store_name:
            today_filters.append(XgjRealTodayStats.store_name == store_name)
            refund_filters.append(XgjRealRefundStats.store_name == store_name)
        if store_id:
            today_filters.append(XgjRealTodayStats.store_id == store_id)
            refund_filters.append(XgjRealRefundStats.store_id == store_id)
        if dvd_data_scope is not None:
            today_filters.append(XgjRealTodayStats.bind_user_id.in_(dvd_data_scope))
            refund_filters.append(XgjRealRefundStats.bind_user_id.in_(dvd_data_scope))

        today_query_date, today_latest_collect_hour = await cls._get_today_latest_collect_hour(
            db, XgjRealTodayStats, today_filters
        )
        refund_query_date, refund_latest_collect_hour = await cls._get_today_latest_collect_hour(
            db, XgjRealRefundStats, refund_filters
        )

        today_stats = {
            'pendingPaymentNum': 0,
            'waitSendNum': 0,
            'shippedNum': 0,
            'pendingAfterSaleNum': 0,
        }
        if today_latest_collect_hour is not None:
            today_summary_query = select(
                func.sum(XgjRealTodayStats.pending_payment_num).label('pending_payment_num'),
                func.sum(XgjRealTodayStats.wait_send_num).label('wait_send_num'),
                func.sum(XgjRealTodayStats.shipped_num).label('shipped_num'),
                func.sum(XgjRealTodayStats.pending_after_sale_num).label('pending_after_sale_num'),
            ).where(
                *today_filters,
                XgjRealTodayStats.collect_date == today_query_date,
                XgjRealTodayStats.collect_hour == today_latest_collect_hour,
            )
            today_row = (await db.execute(today_summary_query)).one_or_none()
            today_stats = {
                'pendingPaymentNum': int(round(float(getattr(today_row, 'pending_payment_num', 0) or 0))),
                'waitSendNum': int(round(float(getattr(today_row, 'wait_send_num', 0) or 0))),
                'shippedNum': int(round(float(getattr(today_row, 'shipped_num', 0) or 0))),
                'pendingAfterSaleNum': int(round(float(getattr(today_row, 'pending_after_sale_num', 0) or 0))),
            }

        refund_stats = {
            'aboutToTimeoutNum': 0,
            'sellerPendingNum': 0,
            'buyerPendingNum': 0,
        }
        if refund_latest_collect_hour is not None:
            refund_summary_query = select(
                func.sum(XgjRealRefundStats.about_to_timeout_num).label('about_to_timeout_num'),
                func.sum(XgjRealRefundStats.seller_pending_num).label('seller_pending_num'),
                func.sum(XgjRealRefundStats.buyer_pending_num).label('buyer_pending_num'),
            ).where(
                *refund_filters,
                XgjRealRefundStats.collect_date == refund_query_date,
                XgjRealRefundStats.collect_hour == refund_latest_collect_hour,
            )
            refund_row = (await db.execute(refund_summary_query)).one_or_none()
            refund_stats = {
                'aboutToTimeoutNum': int(round(float(getattr(refund_row, 'about_to_timeout_num', 0) or 0))),
                'sellerPendingNum': int(round(float(getattr(refund_row, 'seller_pending_num', 0) or 0))),
                'buyerPendingNum': int(round(float(getattr(refund_row, 'buyer_pending_num', 0) or 0))),
            }

        return {
            **today_stats,
            **refund_stats,
            'todayLatestCollectTime': cls._build_latest_collect_time(today_query_date, today_latest_collect_hour),
            'refundLatestCollectTime': cls._build_latest_collect_time(refund_query_date, refund_latest_collect_hour),
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
