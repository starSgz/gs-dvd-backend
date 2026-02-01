from datetime import date, datetime
from typing import Any

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.entity.do.qf_do import QfOverview
from module_dvd.entity.do.qf_realtime_trend_do import QfRealtimeTrend
from module_dvd.entity.do.qf_order_list_do import QfOrderList
from module_dvd.entity.do.qf_realtime_metrics_do import QfRealtimeMetrics


class QfOverviewDao:
    """
    小红书数据概览模块数据库操作层
    """

    @classmethod
    async def get_store_list(cls, db: AsyncSession) -> list[dict[str, Any]]:
        """
        获取店铺列表
        
        :param db: orm对象
        :return: 店铺列表
        """
        result = await db.execute(
            select(QfRealtimeMetrics.store_name)
            .distinct()
            .where(QfRealtimeMetrics.store_name.isnot(None))
            .order_by(QfRealtimeMetrics.store_name)
        )
        
        rows = result.scalars().all()
        return [{'storeName': store_name} for store_name in rows]

    @classmethod
    async def get_realtime_metrics(cls, db: AsyncSession, target_date: date = None, store_name: str = None) -> dict[str, Any]:
        """
        获取实时指标（从 qf_realtime_metrics 表获取 GMV、订单量、商品访问量等）
        每天每个店铺只有一条数据，直接累加即可
        
        :param db: orm对象
        :param target_date: 目标日期
        :param store_name: 店铺名称
        :return: 汇总指标数据
        """
        if target_date is None:
            target_date = date.today()

        # 构建查询：直接累加当天所有店铺的数据
        query = select(
            func.sum(QfRealtimeMetrics.pay_amount).label('total_gmv'),
            func.sum(QfRealtimeMetrics.pay_order_count).label('total_orders'),
            func.sum(QfRealtimeMetrics.goods_visit_count).label('total_goods_visits'),
            func.sum(QfRealtimeMetrics.shop_page_visit).label('total_shop_visits'),
            func.sum(QfRealtimeMetrics.ad_pay_amount).label('total_ad_amount'),
        ).where(QfRealtimeMetrics.collect_date == target_date)

        if store_name:
            query = query.where(QfRealtimeMetrics.store_name == store_name)

        result = await db.execute(query)
        row = result.first()

        return {
            'metrics': {
                'totalGmv': float(row.total_gmv or 0) if row else 0,
                'totalOrders': int(row.total_orders or 0) if row else 0,
                'totalGoodsVisits': int(row.total_goods_visits or 0) if row else 0,
                'totalShopVisits': int(row.total_shop_visits or 0) if row else 0,
                'totalAdAmount': float(row.total_ad_amount or 0) if row else 0,
            }
        }

    @classmethod
    async def get_realtime_trend(cls, db: AsyncSession, target_date: date = None, store_name: str = None) -> dict[str, Any]:
        """
        获取实时GMV走势（24小时数据）
        
        :param db: orm对象
        :param target_date: 目标日期
        :param store_name: 店铺名称
        :return: 实时趋势数据
        """
        if target_date is None:
            target_date = date.today()

        # 构建查询
        query = select(
            QfRealtimeTrend.dtm,
            func.sum(QfRealtimeTrend.pay_net_amt).label('total_gmv'),
            func.sum(QfRealtimeTrend.deal_order_cnt).label('total_orders'),
            func.sum(QfRealtimeTrend.card_click_cnt).label('total_card_clicks'),
        ).where(QfRealtimeTrend.collect_date == target_date)

        # 如果指定了店铺名称，添加筛选条件
        if store_name:
            query = query.where(QfRealtimeTrend.store_name == store_name)

        query = query.group_by(QfRealtimeTrend.dtm).order_by(QfRealtimeTrend.dtm)

        result = await db.execute(query)
        rows = result.all()

        # 初始化24小时数据
        time_labels = [f'{i:02d}:00' for i in range(24)]
        gmv_data = [0.0] * 24
        order_data = [0] * 24
        card_click_data = [0] * 24

        # 填充实际数据
        for row in rows:
            if row.dtm and row.dtm.isdigit():
                hour = int(row.dtm)
                if 0 <= hour < 24:
                    gmv_data[hour] = float(row.total_gmv or 0)
                    order_data[hour] = int(row.total_orders or 0)
                    card_click_data[hour] = int(row.total_card_clicks or 0)

        return {
            'timeLabels': time_labels,
            'gmvData': gmv_data,
            'orderData': order_data,
            'cardClickData': card_click_data,
        }

    @classmethod
    async def get_top_stores(cls, db: AsyncSession, target_date: date = None, sort_by: str = 'orders', limit: int = 10) -> list[dict[str, Any]]:
        """
        获取热销店铺TOP排行
        
        :param db: orm对象
        :param target_date: 目标日期
        :param sort_by: 排序方式，'orders'按订单量，'sales'按销售额
        :param limit: 返回数量
        :return: 店铺排行列表
        """
        if target_date is None:
            target_date = date.today()

        # 构建查询
        query = select(
            QfRealtimeTrend.store_name,
            func.sum(QfRealtimeTrend.deal_order_cnt).label('order_count'),
            func.sum(QfRealtimeTrend.pay_net_amt).label('sales_amount'),
        ).where(
            QfRealtimeTrend.collect_date == target_date,
            QfRealtimeTrend.store_name.isnot(None)
        ).group_by(QfRealtimeTrend.store_name)

        # 根据排序方式选择排序字段
        if sort_by == 'orders':
            query = query.order_by(desc('order_count'))
        else:  # sales
            query = query.order_by(desc('sales_amount'))
        
        query = query.limit(limit)

        result = await db.execute(query)
        rows = result.all()

        return [
            {
                'rank': idx + 1,
                'storeName': row.store_name,
                'orderCount': int(row.order_count or 0),
                'salesAmount': float(row.sales_amount or 0),
            }
            for idx, row in enumerate(rows)
        ]

    @classmethod
    async def get_realtime_orders(cls, db: AsyncSession, target_date: date = None, store_name: str = None, limit: int = 20) -> list[dict[str, Any]]:
        """
        获取实时订单列表（按package_id分组统计）

        :param db: orm对象
        :param target_date: 目标日期，默认为今天
        :param store_name: 店铺名称筛选
        :param limit: 返回数量
        :return: 订单列表
        """
        # 如果未指定日期，使用今天的日期
        query_date = target_date if target_date else date.today()

        # 构建查询 - 按 package_id 分组，累加金额（因为一个订单可能有多个SKU）
        query = select(
            QfOrderList.package_id,
            QfOrderList.store_name,
            func.max(QfOrderList.ordered_at).label('order_time'),
            func.sum(QfOrderList.sku_total_paid_amount).label('total_amount'),
            func.max(QfOrderList.update_time).label('latest_update'),
        ).where(
            QfOrderList.collect_date == query_date,  # 查询指定日期的数据
            QfOrderList.package_id.isnot(None),
            QfOrderList.sku_total_paid_amount.isnot(None),
            QfOrderList.sku_total_paid_amount > 0,
        )

        # 如果指定了店铺名称，添加筛选条件
        if store_name:
            query = query.where(QfOrderList.store_name == store_name)

        query = (
            query.group_by(
                QfOrderList.package_id,
                QfOrderList.store_name,
            )
            .order_by(desc('latest_update'))
            .limit(limit)
        )

        result = await db.execute(query)
        rows = result.all()

        orders = []
        for row in rows:
            orders.append({
                'orderNo': row.package_id or '未知订单',
                'storeName': row.store_name or '未知店铺',
                'orderTime': row.order_time or '',
                'orderAmount': round(float(row.total_amount or 0), 2),
            })

        return orders

    @classmethod
    async def get_dashboard_metrics(cls, db: AsyncSession, target_date: date = None) -> dict[str, Any]:
        """
        获取大屏核心指标
        
        :param db: orm对象
        :param target_date: 目标日期，默认为今天
        :return: 核心指标字典
        """
        if target_date is None:
            target_date = date.today()

        result = await db.execute(
            select(
                func.sum(QfOverview.pay_pkg_cnt).label('total_orders'),
                func.sum(QfOverview.pay_gmv).label('total_gmv'),
            ).where(QfOverview.collect_date == target_date)
        )
        row = result.first()

        return {
            'total_orders': int(row.total_orders or 0),
            'total_gmv': float(row.total_gmv or 0),
        }

    @classmethod
    async def get_store_sales_rank(cls, db: AsyncSession, target_date: date = None, limit: int = 10) -> list[dict[str, Any]]:
        """
        获取店铺销售排行
        
        :param db: orm对象
        :param target_date: 目标日期
        :param limit: 返回数量
        :return: 店铺排行列表
        """
        if target_date is None:
            target_date = date.today()

        result = await db.execute(
            select(
                QfOverview.store_name,
                func.sum(QfOverview.pay_pkg_cnt).label('order_count'),
                func.sum(QfOverview.pay_gmv).label('sales_amount'),
            )
            .where(QfOverview.collect_date == target_date)
            .group_by(QfOverview.store_name)
            .order_by(desc('sales_amount'))
            .limit(limit)
        )

        rows = result.all()
        return [
            {
                'rank': idx + 1,
                'store_name': row.store_name or '未知店铺',
                'order_count': int(row.order_count or 0),
                'sales_amount': float(row.sales_amount or 0),
            }
            for idx, row in enumerate(rows)
        ]

    @classmethod
    async def get_channel_sales_data(cls, db: AsyncSession, target_date: date = None) -> list[dict[str, Any]]:
        """
        获取渠道销售数据（笔记、直播、商卡）
        
        :param db: orm对象
        :param target_date: 目标日期
        :return: 渠道销售数据列表
        """
        if target_date is None:
            target_date = date.today()

        result = await db.execute(
            select(
                func.sum(QfOverview.note_pay_pkg_cnt).label('note_count'),
                func.sum(QfOverview.note_pay_gmv).label('note_gmv'),
                func.sum(QfOverview.live_pay_pkg_cnt).label('live_count'),
                func.sum(QfOverview.live_pay_gmv).label('live_gmv'),
                func.sum(QfOverview.card_pay_pkg_cnt).label('card_count'),
                func.sum(QfOverview.card_pay_gmv).label('card_gmv'),
            ).where(QfOverview.collect_date == target_date)
        )

        row = result.first()
        
        channels = []
        
        # 笔记数据
        note_count = int(row.note_count or 0)
        note_gmv = float(row.note_gmv or 0)
        if note_count > 0:
            channels.append({
                'channel_name': '笔记',
                'sales_count': note_count,
                'sales_amount': note_gmv,
                'avg_price': round(note_gmv / note_count, 2),
            })
        
        # 直播数据
        live_count = int(row.live_count or 0)
        live_gmv = float(row.live_gmv or 0)
        if live_count > 0:
            channels.append({
                'channel_name': '直播',
                'sales_count': live_count,
                'sales_amount': live_gmv,
                'avg_price': round(live_gmv / live_count, 2),
            })
        
        # 商卡数据
        card_count = int(row.card_count or 0)
        card_gmv = float(row.card_gmv or 0)
        if card_count > 0:
            channels.append({
                'channel_name': '商卡',
                'sales_count': card_count,
                'sales_amount': card_gmv,
                'avg_price': round(card_gmv / card_count, 2),
            })

        return channels

    @classmethod
    async def get_recent_orders(cls, db: AsyncSession, limit: int = 20) -> list[dict[str, Any]]:
        """
        获取最近订单（模拟数据，因为实际表没有订单明细）
        
        :param db: orm对象
        :param limit: 返回数量
        :return: 订单列表
        """
        result = await db.execute(
            select(
                QfOverview.store_name,
                QfOverview.pay_gmv,
                QfOverview.dtm,
                QfOverview.collect_date,
            )
            .order_by(desc(QfOverview.collect_date))
            .limit(limit)
        )

        rows = result.all()
        orders = []
        for row in rows:
            if row.pay_gmv and float(row.pay_gmv) > 0:
                orders.append({
                    'store_name': row.store_name or '未知店铺',
                    'channel': '小红书',
                    'order_amount': float(row.pay_gmv),
                    'order_time': row.dtm or str(row.collect_date),
                })

        return orders[:limit]

    @classmethod
    async def get_trend_data(cls, db: AsyncSession, days: int = 7) -> dict[str, Any]:
        """
        获取趋势数据（按天统计）
        
        :param db: orm对象
        :param days: 天数
        :return: 趋势数据
        """
        result = await db.execute(
            select(
                QfOverview.collect_date,
                func.sum(QfOverview.pay_gmv).label('total_gmv'),
                func.sum(QfOverview.pay_pkg_cnt).label('total_orders'),
                func.sum(QfOverview.note_pay_gmv).label('note_gmv'),
                func.sum(QfOverview.live_pay_gmv).label('live_gmv'),
                func.sum(QfOverview.card_pay_gmv).label('card_gmv'),
            )
            .group_by(QfOverview.collect_date)
            .order_by(QfOverview.collect_date)
            .limit(days)
        )

        rows = result.all()
        
        time_labels = []
        gmv_data = []
        order_data = []
        note_data = []
        live_data = []
        card_data = []

        for row in rows:
            time_labels.append(row.collect_date.strftime('%m-%d'))
            gmv_data.append(float(row.total_gmv or 0))
            order_data.append(int(row.total_orders or 0))
            note_data.append(float(row.note_gmv or 0))
            live_data.append(float(row.live_gmv or 0))
            card_data.append(float(row.card_gmv or 0))

        return {
            'time_labels': time_labels,
            'gmv_data': gmv_data,
            'order_data': order_data,
            'note_data': note_data,
            'live_data': live_data,
            'card_data': card_data,
        }

    @classmethod
    async def get_sku_sales_data(cls, db: AsyncSession, target_date: date = None, sort_by: str = 'sales') -> list[dict[str, Any]]:
        """
        获取SKU销售数据（按SKU统计销量和销售额）
        
        :param db: orm对象
        :param target_date: 目标日期，默认为今天
        :param sort_by: 排序方式，'sales'按销量，'amount'按销售额
        :return: SKU销售数据列表
        """
        if target_date is None:
            target_date = date.today()

        # 构建查询 - 按 sku_id 和 sku_name 分组统计
        query = select(
            QfOrderList.sku_id,
            QfOrderList.sku_name,
            func.count(QfOrderList.id).label('sales_count'),  # 销量：记录数量
            func.sum(QfOrderList.sku_total_paid_amount).label('sales_amount'),  # 销售额：累计金额
        ).where(
            QfOrderList.collect_date == target_date,
            QfOrderList.sku_id.isnot(None),
            QfOrderList.sku_total_paid_amount.isnot(None),
            QfOrderList.sku_total_paid_amount > 0,
        ).group_by(
            QfOrderList.sku_id,
            QfOrderList.sku_name,
        )

        # 根据排序方式选择排序字段
        if sort_by == 'sales':
            query = query.order_by(desc('sales_count'))
        else:  # amount
            query = query.order_by(desc('sales_amount'))

        result = await db.execute(query)
        rows = result.all()

        return [
            {
                'skuId': row.sku_id or '未知SKU',
                'skuName': row.sku_name or '未知商品',
                'salesCount': int(row.sales_count or 0),
                'salesAmount': round(float(row.sales_amount or 0), 2),
            }
            for row in rows
        ]

