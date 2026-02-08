from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.entity.do.dd_do import DdRealBusinessOverview, DdRealHourlyTrend, DdRealIncomeExpenditureOverview


class DdOverviewDao:
    """
    抖店数据概览模块数据库操作层
    """

    @classmethod
    async def get_store_list(cls, db: AsyncSession) -> list[dict[str, Any]]:
        """
        获取店铺列表
        
        :param db: orm对象
        :return: 店铺列表
        """
        result = await db.execute(
            select(
                DdRealBusinessOverview.store_name,
                DdRealBusinessOverview.store_id
            )
            .distinct()
            .where(DdRealBusinessOverview.store_name.isnot(None))
            .order_by(DdRealBusinessOverview.store_name)
        )
        
        rows = result.all()
        return [{'storeName': row.store_name, 'storeId': row.store_id} for row in rows]

    @classmethod
    async def get_store_top5(
        cls, 
        db: AsyncSession, 
        store_id: str = None,
        sort_by: str = 'amount', 
        limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        获取店铺销售TOP5
        
        :param db: orm对象
        :param store_id: 店铺ID筛选（可选）
        :param sort_by: 排序方式，'amount'-按成交金额，'orders'-按订单数
        :param limit: 返回数量
        :return: TOP5店铺列表
        """
        # 查询数据库中最新的日期
        latest_date_result = await db.execute(
            select(func.max(DdRealBusinessOverview.collect_date))
        )
        query_date = latest_date_result.scalar()
        
        # 如果数据库中没有数据，返回空列表
        if query_date is None:
            return []
        
        # 选择排序字段
        if sort_by == 'orders':
            sort_field = func.sum(DdRealBusinessOverview.pay_cnt)
            field_name = 'pay_cnt'
        else:  # 默认按成交金额
            sort_field = func.sum(DdRealBusinessOverview.income_amt)
            field_name = 'income_amt'
        
        # 构建数据查询
        query = select(
            DdRealBusinessOverview.store_name,
            DdRealBusinessOverview.store_id,
            sort_field.label('total_value')
        ).where(
            DdRealBusinessOverview.collect_date == query_date,
            DdRealBusinessOverview.store_name.isnot(None)
        )
        
        # 如果指定了店铺ID，添加筛选条件
        if store_id:
            query = query.where(DdRealBusinessOverview.store_id == store_id)
        
        query = (
            query.group_by(
                DdRealBusinessOverview.store_name,
                DdRealBusinessOverview.store_id
            )
            .order_by(desc('total_value'))
            .limit(limit)
        )
        
        result = await db.execute(query)
        rows = result.all()


        # 格式化返回数据
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
        store_id: str = None
    ) -> dict[str, Any]:
        """
        获取抖店概览指标数据
        
        :param db: orm对象
        :param store_id: 店铺ID筛选（可选）
        :return: 概览指标数据
        """
        # 查询数据库中最新的日期
        latest_date_result = await db.execute(
            select(func.max(DdRealBusinessOverview.collect_date))
        )
        query_date = latest_date_result.scalar()
        
        # 如果数据库中没有数据，返回默认值
        if query_date is None:
            return {
                'payAmt': 0,
                'payCnt': 0,
                'productShowUcnt': 0,
                'refundAmtPayTime': 0,
                'incomeAmt': 0,
                'adCost': 0,
                'perUsrPayAmt': 0,
                'conversionRate': 0,
                'productClickPayCntRatio': 0,
                'productShowClickCntRatio': 0,
                'refundAmtRate': 0,
                'adExpenseRatioWithRefund': 0
            }
        
        # 如果选择了单个店铺，直接查询该店铺的数据（包括数据库中已有的转化率）
        if store_id:
            business_query = select(
                func.sum(DdRealBusinessOverview.pay_amt).label('pay_amt'),
                func.sum(DdRealBusinessOverview.pay_cnt).label('pay_cnt'),
                func.sum(DdRealBusinessOverview.product_show_ucnt).label('product_show_ucnt'),
                func.sum(DdRealBusinessOverview.refund_amt_pay_time).label('refund_amt_pay_time'),
                func.sum(DdRealBusinessOverview.income_amt).label('income_amt'),
                func.avg(DdRealBusinessOverview.per_usr_pay_amt).label('per_usr_pay_amt'),
                func.sum(DdRealBusinessOverview.pay_ucnt).label('pay_ucnt'),
                func.avg(DdRealBusinessOverview.product_click_pay_cnt_ratio).label('product_click_pay_cnt_ratio'),
                func.avg(DdRealBusinessOverview.product_show_click_cnt_ratio).label('product_show_click_cnt_ratio')
            ).where(
                DdRealBusinessOverview.collect_date == query_date,
                DdRealBusinessOverview.store_id == store_id
            )
        else:
            # 查询所有店铺时，需要查询原始数据用于计算
            business_query = select(
                func.sum(DdRealBusinessOverview.pay_amt).label('pay_amt'),
                func.sum(DdRealBusinessOverview.pay_cnt).label('pay_cnt'),
                func.sum(DdRealBusinessOverview.product_show_ucnt).label('product_show_ucnt'),
                func.sum(DdRealBusinessOverview.refund_amt_pay_time).label('refund_amt_pay_time'),
                func.sum(DdRealBusinessOverview.income_amt).label('income_amt'),
                func.avg(DdRealBusinessOverview.per_usr_pay_amt).label('per_usr_pay_amt'),
                func.sum(DdRealBusinessOverview.pay_ucnt).label('pay_ucnt'),
                func.sum(DdRealBusinessOverview.product_click_cnt).label('product_click_cnt'),
                func.sum(DdRealBusinessOverview.product_show_cnt).label('product_show_cnt')
            ).where(
                DdRealBusinessOverview.collect_date == query_date
            )
        
        business_result = await db.execute(business_query)
        business_row = business_result.first()
        
        # 构建收支概览查询
        income_query = select(
            func.sum(DdRealIncomeExpenditureOverview.ad_cost).label('ad_cost'),
            func.avg(DdRealIncomeExpenditureOverview.refund_amt_rate).label('refund_amt_rate'),
            func.avg(DdRealIncomeExpenditureOverview.ad_expense_ratio_with_refund).label('ad_expense_ratio_with_refund')
        ).where(
            DdRealIncomeExpenditureOverview.collect_date == query_date
        )
        
        # 如果指定了店铺ID，添加筛选条件
        if store_id:
            income_query = income_query.where(DdRealIncomeExpenditureOverview.store_id == store_id)
        
        income_result = await db.execute(income_query)
        income_row = income_result.first()
        
        # 计算转化率：成交人数 / 商品曝光人数 * 100
        pay_ucnt = float(business_row.pay_ucnt or 0)
        product_show_ucnt = float(business_row.product_show_ucnt or 0)
        conversion_rate = round((pay_ucnt / product_show_ucnt * 100), 2) if product_show_ucnt > 0 else 0
        
        # 判断是单选店铺还是全部店铺
        if store_id:
            # 单选店铺：直接使用数据库中的转化率字段（数据库中存储的已经是百分比形式）
            product_click_pay_cnt_ratio = round(float(business_row.product_click_pay_cnt_ratio or 0), 2)
            product_show_click_cnt_ratio = round(float(business_row.product_show_click_cnt_ratio or 0), 2)
        else:
            # 全部店铺：手动计算转化率
            # 商品点击-成交转化率：成交订单数 / 商品点击次数 * 100
            pay_cnt = float(business_row.pay_cnt or 0)
            product_click_cnt = float(business_row.product_click_cnt or 0)
            product_click_pay_cnt_ratio = round((pay_cnt / product_click_cnt * 100), 2) if product_click_cnt > 0 else 0
            
            # 商品曝光-点击转化率：商品点击次数 / 商品曝光次数 * 100
            product_show_cnt = float(business_row.product_show_cnt or 0)
            product_show_click_cnt_ratio = round((product_click_cnt / product_show_cnt * 100), 2) if product_show_cnt > 0 else 0
        
        # 格式化返回数据
        return {
            'payAmt': round(float(business_row.pay_amt or 0), 2),
            'payCnt': int(business_row.pay_cnt or 0),
            'productShowUcnt': int(business_row.product_show_ucnt or 0),
            'refundAmtPayTime': round(float(business_row.refund_amt_pay_time or 0), 2),
            'incomeAmt': round(float(business_row.income_amt or 0), 2),
            'adCost': round(float(income_row.ad_cost or 0), 2) if income_row else 0,
            'perUsrPayAmt': round(float(business_row.per_usr_pay_amt or 0), 2),
            'conversionRate': conversion_rate,
            'productClickPayCntRatio': product_click_pay_cnt_ratio,
            'productShowClickCntRatio': product_show_click_cnt_ratio,
            'refundAmtRate': round(float(income_row.refund_amt_rate or 0) * 100, 2) if income_row else 0,
            'adExpenseRatioWithRefund': round(float(income_row.ad_expense_ratio_with_refund or 0) * 100, 2) if income_row else 0
        }

    @classmethod
    async def get_hourly_trend(
        cls,
        db: AsyncSession,
        store_id: str = None,
        index_display: str = None
    ) -> list[dict[str, Any]]:
        """
        获取小时趋势数据
        
        :param db: orm对象
        :param store_id: 店铺ID筛选（可选）
        :param index_display: 指标显示名称筛选（可选，如：用户支付金额）
        :return: 24小时趋势数据
        """
        # 查询数据库中最新的日期
        latest_date_result = await db.execute(
            select(func.max(DdRealHourlyTrend.collect_date))
        )
        query_date = latest_date_result.scalar()
        
        # 如果数据库中没有数据，返回空列表
        if query_date is None:
            return []
        
        # 构建查询：按小时分组，累加 today_value
        query = select(
            DdRealHourlyTrend.hour,
            DdRealHourlyTrend.hour_str,
            func.sum(DdRealHourlyTrend.today_value).label('total_value')
        ).where(
            DdRealHourlyTrend.collect_date == query_date
        )
        
        # 如果指定了指标显示名称，添加筛选条件
        if index_display:
            query = query.where(DdRealHourlyTrend.index_display == index_display)
        
        # 如果指定了店铺ID，添加筛选条件
        if store_id:
            query = query.where(DdRealHourlyTrend.store_id == store_id)
        
        query = query.group_by(
            DdRealHourlyTrend.hour,
            DdRealHourlyTrend.hour_str
        ).order_by(DdRealHourlyTrend.hour)
        
        result = await db.execute(query)
        rows = result.all()
        
        # 格式化返回数据，确保0-23小时都有数据
        hour_data = {row.hour: round(float(row.total_value or 0), 2) for row in rows}
        
        # 填充0-23小时的完整数据
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
        db: AsyncSession
    ) -> list[dict[str, Any]]:
        """
        获取可用的指标列表（用于调试）
        
        :param db: orm对象
        :return: 指标列表
        """
        # 查询数据库中最新的日期
        latest_date_result = await db.execute(
            select(func.max(DdRealHourlyTrend.collect_date))
        )
        query_date = latest_date_result.scalar()
        
        if query_date is None:
            return []
        
        # 查询该日期下所有不同的指标
        query = select(
            DdRealHourlyTrend.index_name,
            DdRealHourlyTrend.index_display,
            func.count().label('count')
        ).where(
            DdRealHourlyTrend.collect_date == query_date
        ).group_by(
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
