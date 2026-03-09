from datetime import date, datetime, timedelta
from typing import Any, Optional

from sqlalchemy import DECIMAL, Integer, cast, func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.entity.do.dd_do import DdRealOverview, DdRealHourlyTrend, DdRealIncomeExpenditureOverview


class DdOverviewDao:
    """
    抖店数据概览模块数据库操作层
    """

    @classmethod
    async def get_store_list(cls, db: AsyncSession, dvd_data_scope=None) -> list[dict[str, Any]]:
        """
        获取店铺列表
        
        :param db: orm对象
        :param dvd_data_scope: 数据权限子查询，None 表示不过滤
        :return: 店铺列表
        """
        query = (
            select(
                DdRealOverview.store_name,
                DdRealOverview.store_id
            )
            .distinct()
            .where(DdRealOverview.store_name.isnot(None))
        )
        if dvd_data_scope is not None:
            query = query.where(DdRealOverview.bind_user_id.in_(dvd_data_scope))
        query = query.order_by(DdRealOverview.store_name)

        result = await db.execute(query)
        rows = result.all()
        return [{'storeName': row.store_name, 'storeId': row.store_id} for row in rows]

    @classmethod
    async def get_store(
        cls, 
        db: AsyncSession, 
        store_id: str = None,
        sort_by: str = 'amount', 
        limit: int = 100,
        dvd_data_scope=None,
    ) -> list[dict[str, Any]]:
        """
        获取店铺销售
        
        :param db: orm对象
        :param store_id: 店铺ID筛选（可选）
        :param sort_by: 排序方式，'amount'-按成交金额，'orders'-按订单数
        :param limit: 返回数量
        :param dvd_data_scope: 数据权限子查询，None 表示不过滤
        :return: 店铺列表
        """
        latest_date_result = await db.execute(
            select(func.max(DdRealOverview.collect_date))
        )
        query_date = latest_date_result.scalar()
        
        if query_date is None:
            return []
        
        if sort_by == 'orders':
            sort_field = func.sum(cast(DdRealOverview.pay_cnt, Integer))
        else:
            sort_field = func.sum(cast(DdRealOverview.income_amt, DECIMAL(20, 2)))
        
        query = select(
            DdRealOverview.store_name,
            DdRealOverview.store_id,
            sort_field.label('total_value')
        ).where(
            DdRealOverview.collect_date == query_date,
            DdRealOverview.store_name.isnot(None)
        )
        
        if store_id:
            query = query.where(DdRealOverview.store_id == store_id)
        if dvd_data_scope is not None:
            query = query.where(DdRealOverview.bind_user_id.in_(dvd_data_scope))
        
        query = (
            query.group_by(
                DdRealOverview.store_name,
                DdRealOverview.store_id
            )
            .order_by(desc('total_value'))
            .limit(limit)
        )
        
        result = await db.execute(query)
        rows = result.all()

        top_stores = []
        for row in rows:
            today_value = float(row.total_value or 0)
            top_stores.append({
                'name': row.store_name,
                'storeId': row.store_id,
                'sales': round(today_value, 2) if sort_by == 'amount' else int(today_value),
            })
        
        return top_stores

    @classmethod
    async def get_overview_metrics(
        cls,
        db: AsyncSession,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取抖店概览指标数据
        
        :param db: orm对象
        :param store_id: 店铺ID筛选（可选）
        :param dvd_data_scope: 数据权限子查询，None 表示不过滤
        :return: 概览指标数据（含运营状态新字段）
        """
        latest_date_result = await db.execute(
            select(func.max(DdRealOverview.collect_date))
        )
        query_date = latest_date_result.scalar()
        
        if query_date is None:
            return {
                'payAmt': 0,
                'payCnt': 0,
                'productShowUcnt': 0,
                'productClickUcnt': 0,
                'payUcnt': 0,
                'rfndsucAmt': 0,
                'rfndsucAmtPayTime': 0,
                'refundOrderCnt': 0,
                'refundOrderCntPayTime': 0,
                'incomeAmt': 0,
                'costAmt': 0,
                'adCost': 0,
                'perUsrPayAmt': 0,
                'conversionRate': 0,
                'productClickPayCntRatio': 0,
                'productShowClickCntRatio': 0,
                'refundAmtRate': 0,
                'adExpenseRatioWithRefund': 0,
                'unpaid': 0,
                'unsend': 0,
                'abnormalPackage': 0,
                'unprocess': 0,
                'serviceOrder': 0,
                'toBerectifiedRisk': 0,
                'violationPending': 0,
            }
        
        if store_id:
            business_query = select(
                func.sum(cast(DdRealOverview.pay_amt, DECIMAL(20, 2))).label('pay_amt'),
                func.sum(cast(DdRealOverview.pay_cnt, Integer)).label('pay_cnt'),
                func.sum(cast(DdRealOverview.product_show_ucnt, Integer)).label('product_show_ucnt'),
                func.sum(cast(DdRealOverview.product_click_ucnt, Integer)).label('product_click_ucnt'),
                func.sum(cast(DdRealOverview.pay_ucnt, Integer)).label('pay_ucnt'),
                func.sum(cast(DdRealOverview.rfndsuc_amt, DECIMAL(20, 2))).label('rfndsuc_amt'),
                func.sum(cast(DdRealOverview.rfndsuc_amt_pay_time, DECIMAL(20, 2))).label('rfndsuc_amt_pay_time'),
                func.sum(cast(DdRealOverview.refund_order_cnt, Integer)).label('refund_order_cnt'),
                func.sum(cast(DdRealOverview.refund_order_cnt_pay_time, Integer)).label('refund_order_cnt_pay_time'),
                func.sum(cast(DdRealOverview.income_amt, DECIMAL(20, 2))).label('income_amt'),
                func.avg(cast(DdRealOverview.per_usr_pay_amt, DECIMAL(20, 2))).label('per_usr_pay_amt'),
                func.avg(cast(DdRealOverview.product_click_pay_cnt_ratio, DECIMAL(10, 4))).label('product_click_pay_cnt_ratio'),
                func.avg(cast(DdRealOverview.product_show_click_cnt_ratio, DECIMAL(10, 4))).label('product_show_click_cnt_ratio'),
            ).where(
                DdRealOverview.collect_date == query_date,
                DdRealOverview.store_id == store_id
            )
        else:
            business_query = select(
                func.sum(cast(DdRealOverview.pay_amt, DECIMAL(20, 2))).label('pay_amt'),
                func.sum(cast(DdRealOverview.pay_cnt, Integer)).label('pay_cnt'),
                func.sum(cast(DdRealOverview.product_show_ucnt, Integer)).label('product_show_ucnt'),
                func.sum(cast(DdRealOverview.product_click_ucnt, Integer)).label('product_click_ucnt'),
                func.sum(cast(DdRealOverview.pay_ucnt, Integer)).label('pay_ucnt'),
                func.sum(cast(DdRealOverview.rfndsuc_amt, DECIMAL(20, 2))).label('rfndsuc_amt'),
                func.sum(cast(DdRealOverview.rfndsuc_amt_pay_time, DECIMAL(20, 2))).label('rfndsuc_amt_pay_time'),
                func.sum(cast(DdRealOverview.refund_order_cnt, Integer)).label('refund_order_cnt'),
                func.sum(cast(DdRealOverview.refund_order_cnt_pay_time, Integer)).label('refund_order_cnt_pay_time'),
                func.sum(cast(DdRealOverview.income_amt, DECIMAL(20, 2))).label('income_amt'),
                func.avg(cast(DdRealOverview.per_usr_pay_amt, DECIMAL(20, 2))).label('per_usr_pay_amt'),
            ).where(
                DdRealOverview.collect_date == query_date
            )

        if dvd_data_scope is not None:
            business_query = business_query.where(DdRealOverview.bind_user_id.in_(dvd_data_scope))
        
        business_result = await db.execute(business_query)
        business_row = business_result.first()
        
        income_query = select(
            func.sum(DdRealIncomeExpenditureOverview.ad_cost).label('ad_cost'),
            func.sum(DdRealIncomeExpenditureOverview.cost_amt).label('cost_amt'),
            func.avg(DdRealIncomeExpenditureOverview.refund_amt_rate).label('refund_amt_rate'),
            func.avg(DdRealIncomeExpenditureOverview.ad_expense_ratio_with_refund).label('ad_expense_ratio_with_refund'),
        ).where(
            DdRealIncomeExpenditureOverview.collect_date == query_date
        )
        
        if store_id:
            income_query = income_query.where(DdRealIncomeExpenditureOverview.store_id == store_id)
        if dvd_data_scope is not None:
            income_query = income_query.where(DdRealIncomeExpenditureOverview.bind_user_id.in_(dvd_data_scope))
        
        income_result = await db.execute(income_query)
        income_row = income_result.first()

        # 查询 dd_real_overview 获取运营状态新字段
        overview_query = select(
            func.sum(cast(DdRealOverview.unpaid, Integer)).label('unpaid'),
            func.sum(cast(DdRealOverview.unsend, Integer)).label('unsend'),
            func.sum(cast(DdRealOverview.abnormal_package, Integer)).label('abnormal_package'),
            func.sum(cast(DdRealOverview.unprocess, Integer)).label('unprocess'),
            func.sum(cast(DdRealOverview.service_order, Integer)).label('service_order'),
            func.sum(cast(DdRealOverview.to_berectified_risk, Integer)).label('to_berectified_risk'),
            func.sum(cast(DdRealOverview.violation_pending, Integer)).label('violation_pending'),
        ).where(
            DdRealOverview.collect_date == query_date
        )
        if store_id:
            overview_query = overview_query.where(DdRealOverview.store_id == store_id)
        if dvd_data_scope is not None:
            overview_query = overview_query.where(DdRealOverview.bind_user_id.in_(dvd_data_scope))

        overview_result = await db.execute(overview_query)
        overview_row = overview_result.first()
        
        pay_ucnt = float(business_row.pay_ucnt or 0)
        product_show_ucnt = float(business_row.product_show_ucnt or 0)
        conversion_rate = round((pay_ucnt / product_show_ucnt * 100), 2) if product_show_ucnt > 0 else 0
        
        if store_id:
            product_click_pay_cnt_ratio = round(float(business_row.product_click_pay_cnt_ratio or 0), 2)
            product_show_click_cnt_ratio = round(float(business_row.product_show_click_cnt_ratio or 0), 2)
        else:
            pay_cnt = float(business_row.pay_cnt or 0)
            product_click_ucnt_val = float(business_row.product_click_ucnt or 0)
            product_click_pay_cnt_ratio = round((pay_cnt / product_click_ucnt_val * 100), 2) if product_click_ucnt_val > 0 else 0

            product_show_ucnt_val = float(business_row.product_show_ucnt or 0)
            product_show_click_cnt_ratio = round((product_click_ucnt_val / product_show_ucnt_val * 100), 2) if product_show_ucnt_val > 0 else 0
        
        return {
            # 交易核心指标
            'payAmt': round(float(business_row.pay_amt or 0), 2),
            'payCnt': int(business_row.pay_cnt or 0),
            'incomeAmt': round(float(business_row.income_amt or 0), 2),
            'perUsrPayAmt': round(float(business_row.per_usr_pay_amt or 0), 2),
            'productShowUcnt': int(business_row.product_show_ucnt or 0),
            'productClickUcnt': int(business_row.product_click_ucnt or 0),
            'payUcnt': int(business_row.pay_ucnt or 0),
            # 退款指标
            'rfndsucAmt': round(float(business_row.rfndsuc_amt or 0), 2),
            'rfndsucAmtPayTime': round(float(business_row.rfndsuc_amt_pay_time or 0), 2),
            'refundOrderCnt': int(business_row.refund_order_cnt or 0),
            'refundOrderCntPayTime': int(business_row.refund_order_cnt_pay_time or 0),
            # 收支指标
            'adCost': round(float(income_row.ad_cost or 0), 2) if income_row else 0,
            'costAmt': round(float(income_row.cost_amt or 0), 2) if income_row else 0,
            # 转化率指标
            'conversionRate': conversion_rate,
            'productClickPayCntRatio': product_click_pay_cnt_ratio,
            'productShowClickCntRatio': product_show_click_cnt_ratio,
            'refundAmtRate': round(float(income_row.refund_amt_rate or 0) * 100, 2) if income_row else 0,
            'adExpenseRatioWithRefund': round(float(income_row.ad_expense_ratio_with_refund or 0) * 100, 2) if income_row else 0,
            # 运营状态新字段（来自 dd_real_overview）
            'unpaid': int(overview_row.unpaid or 0) if overview_row else 0,
            'unsend': int(overview_row.unsend or 0) if overview_row else 0,
            'abnormalPackage': int(overview_row.abnormal_package or 0) if overview_row else 0,
            'unprocess': int(overview_row.unprocess or 0) if overview_row else 0,
            'serviceOrder': int(overview_row.service_order or 0) if overview_row else 0,
            'toBerectifiedRisk': int(overview_row.to_berectified_risk or 0) if overview_row else 0,
            'violationPending': int(overview_row.violation_pending or 0) if overview_row else 0,
        }

    @classmethod
    async def get_hourly_trend(
        cls,
        db: AsyncSession,
        store_id: str = None,
        index_display: str = None,
        dvd_data_scope=None,
    ) -> list[dict[str, Any]]:
        """
        获取小时趋势数据
        
        :param db: orm对象
        :param store_id: 店铺ID筛选（可选）
        :param index_display: 指标显示名称筛选（可选，如：用户支付金额）
        :param dvd_data_scope: 数据权限子查询，None 表示不过滤
        :return: 24小时趋势数据
        """
        latest_date_result = await db.execute(
            select(func.max(DdRealHourlyTrend.collect_date))
        )
        query_date = latest_date_result.scalar()
        
        if query_date is None:
            return []
        
        query = select(
            DdRealHourlyTrend.hour,
            DdRealHourlyTrend.hour_str,
            func.sum(DdRealHourlyTrend.today_value).label('total_value')
        ).where(
            DdRealHourlyTrend.collect_date == query_date
        )
        
        if index_display:
            query = query.where(DdRealHourlyTrend.index_display == index_display)
        if store_id:
            query = query.where(DdRealHourlyTrend.store_id == store_id)
        if dvd_data_scope is not None:
            query = query.where(DdRealHourlyTrend.bind_user_id.in_(dvd_data_scope))
        
        query = query.group_by(
            DdRealHourlyTrend.hour,
            DdRealHourlyTrend.hour_str
        ).order_by(DdRealHourlyTrend.hour)
        
        result = await db.execute(query)
        rows = result.all()
        
        hour_data = {row.hour: round(float(row.total_value or 0), 2) for row in rows}
        
        trend_data = []
        for hour in range(24):
            trend_data.append({
                'hour': hour,
                'hourStr': f'{hour:02d}:00',
                'value': hour_data.get(hour, 0)
            })
        
        return trend_data

    @classmethod
    async def get_available_indices(
        cls,
        db: AsyncSession,
        dvd_data_scope=None,
    ) -> list[dict[str, Any]]:
        """
        获取可用的指标列表（用于调试）
        
        :param db: orm对象
        :param dvd_data_scope: 数据权限子查询，None 表示不过滤
        :return: 指标列表
        """
        latest_date_result = await db.execute(
            select(func.max(DdRealHourlyTrend.collect_date))
        )
        query_date = latest_date_result.scalar()
        
        if query_date is None:
            return []
        
        query = select(
            DdRealHourlyTrend.index_name,
            DdRealHourlyTrend.index_display,
            func.count().label('count')
        ).where(
            DdRealHourlyTrend.collect_date == query_date
        )
        if dvd_data_scope is not None:
            query = query.where(DdRealHourlyTrend.bind_user_id.in_(dvd_data_scope))
        query = query.group_by(
            DdRealHourlyTrend.index_name,
            DdRealHourlyTrend.index_display
        ).order_by(
            DdRealHourlyTrend.index_name
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        return [{
            'indexName': row.index_name,
            'indexDisplay': row.index_display,
            'count': row.count
        } for row in rows]
