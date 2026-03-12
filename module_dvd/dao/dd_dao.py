from datetime import date, datetime, timedelta
from typing import Any, Optional, Union

from sqlalchemy import DECIMAL, Integer, cast, func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_dvd.entity.do.dd_do import DdRealOverview, DdRealHourlyTrend, DdRealIncomeExpenditureOverview, DdOverview, DdOrderList
from utils.page_util import PageUtil


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

    @classmethod
    async def get_daily_overview_metrics(
        cls,
        db: AsyncSession,
        start_date: date,
        end_date: date,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        获取每日概览指标数据（来自 dd_overview 表，支持日期范围聚合）

        :param db: orm对象
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param store_id: 店铺ID筛选（可选）
        :param dvd_data_scope: 数据权限子查询，None 表示不过滤
        :return: 日期范围内聚合的概览指标数据
        """
        empty = {
            'startDate': str(start_date),
            'endDate': str(end_date),
            'payAmt': 0,
            'incomeAmt': 0,
            'payCnt': 0,
            'perUsrPayAmt': 0,
            'payUcnt': 0,
            'payQcPlatCouponAmt': 0,
            'payPlatCostAmt': 0,
            'depositPayAmt': 0,
            'authorSubsidyAmt': 0,
            'refundedPayAmtPayTime': 0,
            'refundPayQcPlatCouponAmtPayTime': 0,
            'refundPayPlatCostAmtPayTime': 0,
            'rfndsucAmtPayTime': 0,
            'rfndsucAmt': 0,
            'refundOrderCntPayTime': 0,
            'refundOrderCnt': 0,
            'refundAmtPayTime': 0,
            'refundAmt': 0,
            'productShowUcnt': 0,
            'productShowCnt': 0,
            'productClickUcnt': 0,
            'productClickCnt': 0,
            'gpm': 0,
            'productClickPayCntRatio': 0,
            'productShowClickCntRatio': 0,
        }

        query = select(
            func.sum(cast(DdOverview.pay_amt, DECIMAL(20, 2))).label('pay_amt'),
            func.sum(cast(DdOverview.income_amt, DECIMAL(20, 2))).label('income_amt'),
            func.sum(cast(DdOverview.pay_cnt, Integer)).label('pay_cnt'),
            func.avg(cast(DdOverview.per_usr_pay_amt, DECIMAL(20, 2))).label('per_usr_pay_amt'),
            func.sum(cast(DdOverview.pay_ucnt, Integer)).label('pay_ucnt'),
            func.sum(cast(DdOverview.pay_qc_plat_coupon_amt, DECIMAL(20, 2))).label('pay_qc_plat_coupon_amt'),
            func.sum(cast(DdOverview.pay_plat_cost_amt, DECIMAL(20, 2))).label('pay_plat_cost_amt'),
            func.sum(cast(DdOverview.deposit_pay_amt, DECIMAL(20, 2))).label('deposit_pay_amt'),
            func.sum(cast(DdOverview.author_subsidy_amt, DECIMAL(20, 2))).label('author_subsidy_amt'),
            func.sum(cast(DdOverview.refunded_pay_amt_pay_time, DECIMAL(20, 2))).label('refunded_pay_amt_pay_time'),
            func.sum(cast(DdOverview.refund_pay_qc_plat_coupon_amt_pay_time, DECIMAL(20, 2))).label('refund_pay_qc_plat_coupon_amt_pay_time'),
            func.sum(cast(DdOverview.refund_pay_plat_cost_amt_pay_time, DECIMAL(20, 2))).label('refund_pay_plat_cost_amt_pay_time'),
            func.sum(cast(DdOverview.rfndsuc_amt_pay_time, DECIMAL(20, 2))).label('rfndsuc_amt_pay_time'),
            func.sum(cast(DdOverview.rfndsuc_amt, DECIMAL(20, 2))).label('rfndsuc_amt'),
            func.sum(cast(DdOverview.refund_order_cnt_pay_time, Integer)).label('refund_order_cnt_pay_time'),
            func.sum(cast(DdOverview.refund_order_cnt, Integer)).label('refund_order_cnt'),
            func.sum(cast(DdOverview.refund_amt_pay_time, DECIMAL(20, 2))).label('refund_amt_pay_time'),
            func.sum(cast(DdOverview.refund_amt, DECIMAL(20, 2))).label('refund_amt'),
            func.sum(cast(DdOverview.product_show_ucnt, Integer)).label('product_show_ucnt'),
            func.sum(cast(DdOverview.product_show_cnt, Integer)).label('product_show_cnt'),
            func.sum(cast(DdOverview.product_click_ucnt, Integer)).label('product_click_ucnt'),
            func.sum(cast(DdOverview.product_click_cnt, Integer)).label('product_click_cnt'),
            func.avg(cast(DdOverview.gpm, DECIMAL(20, 2))).label('gpm'),
        ).where(
            DdOverview.collect_date >= start_date,
            DdOverview.collect_date <= end_date,
        )

        if store_id:
            query = query.where(DdOverview.store_id == store_id)
        if dvd_data_scope is not None:
            query = query.where(DdOverview.bind_user_id.in_(dvd_data_scope))

        result = await db.execute(query)
        row = result.first()

        if row is None or row.pay_amt is None:
            return empty

        # 计算转化率（小数形式，如 0.15 表示 15%）
        pay_cnt = float(row.pay_cnt or 0)
        product_click_cnt = float(row.product_click_cnt or 0)
        product_click_pay_cnt_ratio = round(
            pay_cnt / product_click_cnt, 4
        ) if product_click_cnt > 0 else 0

        product_show_cnt = float(row.product_show_cnt or 0)
        product_show_click_cnt_ratio = round(
            product_click_cnt / product_show_cnt, 4
        ) if product_show_cnt > 0 else 0

        return {
            'startDate': str(start_date),
            'endDate': str(end_date),
            # 交易核心指标
            'payAmt': round(float(row.pay_amt or 0), 2),
            'incomeAmt': round(float(row.income_amt or 0), 2),
            'payCnt': int(row.pay_cnt or 0),
            'perUsrPayAmt': round(float(row.per_usr_pay_amt or 0), 2),
            'payUcnt': int(row.pay_ucnt or 0),
            # 补贴/优惠
            'payQcPlatCouponAmt': round(float(row.pay_qc_plat_coupon_amt or 0), 2),
            'payPlatCostAmt': round(float(row.pay_plat_cost_amt or 0), 2),
            'depositPayAmt': round(float(row.deposit_pay_amt or 0), 2),
            'authorSubsidyAmt': round(float(row.author_subsidy_amt or 0), 2),
            # 退款指标
            'refundedPayAmtPayTime': round(float(row.refunded_pay_amt_pay_time or 0), 2),
            'refundPayQcPlatCouponAmtPayTime': round(float(row.refund_pay_qc_plat_coupon_amt_pay_time or 0), 2),
            'refundPayPlatCostAmtPayTime': round(float(row.refund_pay_plat_cost_amt_pay_time or 0), 2),
            'rfndsucAmtPayTime': round(float(row.rfndsuc_amt_pay_time or 0), 2),
            'rfndsucAmt': round(float(row.rfndsuc_amt or 0), 2),
            'refundOrderCntPayTime': int(row.refund_order_cnt_pay_time or 0),
            'refundOrderCnt': int(row.refund_order_cnt or 0),
            'refundAmtPayTime': round(float(row.refund_amt_pay_time or 0), 2),
            'refundAmt': round(float(row.refund_amt or 0), 2),
            # 流量指标
            'productShowUcnt': int(row.product_show_ucnt or 0),
            'productShowCnt': int(row.product_show_cnt or 0),
            'productClickUcnt': int(row.product_click_ucnt or 0),
            'productClickCnt': int(row.product_click_cnt or 0),
            'gpm': round(float(row.gpm or 0), 2),
            # 转化率（计算得出）
            'productClickPayCntRatio': product_click_pay_cnt_ratio,
            'productShowClickCntRatio': product_show_click_cnt_ratio,
        }


    @classmethod
    async def get_traffic_trend(
        cls,
        db: AsyncSession,
        start_date: date,
        end_date: date,
        store_id: str = None,
        dvd_data_scope=None,
    ) -> list[dict[str, Any]]:
        """
        按日期查询商品曝光/点击流量趋势（用于柱线混合图）

        :param db: orm对象
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param store_id: 店铺ID筛选（可选）
        :param dvd_data_scope: 数据权限子查询
        :return: 按日期升序排列的流量趋势列表
        """
        query = (
            select(
                DdOverview.collect_date.label('collect_date'),
                func.sum(cast(DdOverview.product_show_ucnt, Integer)).label('product_show_ucnt'),
                func.sum(cast(DdOverview.product_show_cnt, Integer)).label('product_show_cnt'),
                func.sum(cast(DdOverview.product_click_ucnt, Integer)).label('product_click_ucnt'),
                func.sum(cast(DdOverview.product_click_cnt, Integer)).label('product_click_cnt'),
            )
            .where(
                DdOverview.collect_date >= start_date,
                DdOverview.collect_date <= end_date,
            )
            .group_by(DdOverview.collect_date)
            .order_by(DdOverview.collect_date)
        )

        if store_id:
            query = query.where(DdOverview.store_id == store_id)
        if dvd_data_scope is not None:
            query = query.where(DdOverview.bind_user_id.in_(dvd_data_scope))

        result = await db.execute(query)
        rows = result.all()

        return [
            {
                'date': str(row.collect_date),
                'productShowUcnt': int(row.product_show_ucnt or 0),
                'productShowCnt': int(row.product_show_cnt or 0),
                'productClickUcnt': int(row.product_click_ucnt or 0),
                'productClickCnt': int(row.product_click_cnt or 0),
            }
            for row in rows
        ]


class DdOrderListDao:
    """
    抖店订单列表模块数据库操作层
    """

    @classmethod
    async def get_order_list(
        cls,
        db: AsyncSession,
        start_date: date = None,
        end_date: date = None,
        store_id: str = None,
        order_status_text: str = None,
        page_num: int = 1,
        page_size: int = 20,
        dvd_data_scope=None,
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        查询抖店订单列表（分页）

        :param db: orm对象
        :param start_date: 开始日期（采集日期），为 None 时不过滤
        :param end_date: 结束日期（采集日期），为 None 时不过滤
        :param store_id: 店铺ID筛选
        :param order_status_text: 订单状态筛选
        :param page_num: 当前页码
        :param page_size: 每页记录数
        :param dvd_data_scope: 数据权限子查询
        :return: 分页订单列表
        """
        query = (
            select(
                DdOrderList.id,
                DdOrderList.collect_date,
                DdOrderList.store_name,
                DdOrderList.store_id,
                DdOrderList.crawl_account,
                DdOrderList.shop_order_id,
                DdOrderList.create_time,
                DdOrderList.product_name,
                DdOrderList.order_status_text,
                DdOrderList.order_detail_url,
                DdOrderList.pay_time,
                DdOrderList.user_nickname,
                DdOrderList.post_amount,
                DdOrderList.actual_pay_amount,
                DdOrderList.pay_amount,
                DdOrderList.actual_receive_amount,
                DdOrderList.product_id,
                DdOrderList.sku_spec,
                DdOrderList.total_product_count,
                DdOrderList.update_time,
            )
            .order_by(desc(DdOrderList.create_time))
        )

        if start_date is not None:
            query = query.where(DdOrderList.collect_date >= start_date)
        if end_date is not None:
            query = query.where(DdOrderList.collect_date <= end_date)
        if store_id:
            query = query.where(DdOrderList.store_id == store_id)
        if order_status_text:
            query = query.where(DdOrderList.order_status_text == order_status_text)
        if dvd_data_scope is not None:
            query = query.where(DdOrderList.bind_user_id.in_(dvd_data_scope))

        return await PageUtil.paginate(db, query, page_num, page_size, is_page=True)

    @classmethod
    async def get_geo_order_stats(
        cls,
        db: AsyncSession,
        level: str = 'province',
        parent_province: str = None,
        parent_city: str = None,
        store_id: str = None,
        start_date: date = None,
        end_date: date = None,
        dvd_data_scope=None,
    ) -> list[dict[str, Any]]:
        """
        按地理层级聚合订单支付金额和订单数（用于地图展示）

        :param db: orm对象
        :param level: 聚合层级，'province'按省份、'city'按城市、'town'按区县
        :param parent_province: 父级省份名称（level='city'或'town'时生效）
        :param parent_city: 父级城市名称（level='town'时生效）
        :param store_id: 店铺ID筛选（可选）
        :param start_date: 采集日期开始（可选）
        :param end_date: 采集日期结束（可选）
        :param dvd_data_scope: 数据权限子查询，None 表示不过滤
        :return: 地理聚合数据列表
        """
        # 根据层级选择 GROUP BY 字段
        level_field_map = {
            'province': DdOrderList.province,
            'city': DdOrderList.city,
            'town': DdOrderList.town,
        }
        group_field = level_field_map.get(level, DdOrderList.province)

        query = (
            select(
                group_field.label('name'),
                func.sum(DdOrderList.actual_pay_amount).label('total_pay_amount'),
                func.count(DdOrderList.id).label('order_count'),
            )
            .where(group_field.isnot(None), group_field != '')
        )

        # 父级筛选条件
        if level == 'city' and parent_province:
            query = query.where(DdOrderList.province == parent_province)
        elif level == 'town' and parent_province:
            query = query.where(DdOrderList.province == parent_province)
            if parent_city:
                query = query.where(DdOrderList.city == parent_city)

        # 日期范围筛选
        if start_date is not None:
            query = query.where(DdOrderList.collect_date >= start_date)
        if end_date is not None:
            query = query.where(DdOrderList.collect_date <= end_date)

        if store_id:
            query = query.where(DdOrderList.store_id == store_id)
        if dvd_data_scope is not None:
            query = query.where(DdOrderList.bind_user_id.in_(dvd_data_scope))

        query = (
            query
            .group_by(group_field)
            .order_by(desc('total_pay_amount'))
        )

        result = await db.execute(query)
        rows = result.all()

        return [
            {
                'name': row.name,
                'payAmount': round(float(row.total_pay_amount or 0), 2),
                'orderCount': int(row.order_count or 0),
            }
            for row in rows
        ]

    @classmethod
    async def get_category_stats(
        cls,
        db: AsyncSession,
        start_date: date = None,
        end_date: date = None,
        store_id: str = None,
        top_n: int = 10,
        dvd_data_scope=None,
    ) -> dict[str, Any]:
        """
        按商品名称和商品规格聚合订单数量，用于玫瑰图展示

        :param db: orm对象
        :param start_date: 采集日期开始（可选）
        :param end_date: 采集日期结束（可选）
        :param store_id: 店铺ID筛选（可选）
        :param top_n: 取前N条记录（默认取TOP10）
        :param dvd_data_scope: 数据权限子查询，None 表示不过滤
        :return: 包含 productStats 和 skuStats 的字典
        """

        def _build_base_filters(query):
            if start_date is not None:
                query = query.where(DdOrderList.collect_date >= start_date)
            if end_date is not None:
                query = query.where(DdOrderList.collect_date <= end_date)
            if store_id:
                query = query.where(DdOrderList.store_id == store_id)
            if dvd_data_scope is not None:
                query = query.where(DdOrderList.bind_user_id.in_(dvd_data_scope))
            return query

        # 商品名称聚合
        product_query = (
            select(
                DdOrderList.product_name.label('name'),
                func.count(DdOrderList.id).label('order_count'),
            )
            .where(DdOrderList.product_name.isnot(None), DdOrderList.product_name != '')
            .group_by(DdOrderList.product_name)
            .order_by(desc('order_count'))
            .limit(top_n)
        )
        product_query = _build_base_filters(product_query)
        product_result = await db.execute(product_query)
        product_rows = product_result.all()

        # 商品规格聚合
        sku_query = (
            select(
                DdOrderList.sku_spec.label('name'),
                func.count(DdOrderList.id).label('order_count'),
            )
            .where(DdOrderList.sku_spec.isnot(None), DdOrderList.sku_spec != '')
            .group_by(DdOrderList.sku_spec)
            .order_by(desc('order_count'))
            .limit(top_n)
        )
        sku_query = _build_base_filters(sku_query)
        sku_result = await db.execute(sku_query)
        sku_rows = sku_result.all()

        return {
            'productStats': [
                {'name': row.name, 'value': int(row.order_count or 0)}
                for row in product_rows
            ],
            'skuStats': [
                {'name': row.name, 'value': int(row.order_count or 0)}
                for row in sku_rows
            ],
        }
