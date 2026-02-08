from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, Column, Date, DateTime, BigInteger, String, DECIMAL, Integer, text

from config.database import Base


class DdRealBusinessOverview(Base):
    """
    抖店实时业务概览表
    """

    __tablename__ = 'dd_real_business_overview'
    __table_args__ = {'comment': '抖店实时业务概览表'}

    id = Column(CHAR(32), primary_key=True, nullable=False, comment='主键ID')
    bind_user_id = Column(BigInteger, nullable=False, comment='绑定的数据用户ID')
    collect_date = Column(Date, nullable=False, comment='采集时间')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(255), nullable=True, comment='店铺id')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    real_time = Column(DateTime, nullable=True, comment='实时时间')
    pay_amt = Column(DECIMAL(20, 2), nullable=True, comment='用户支付金额')
    pay_cnt = Column(Integer, nullable=True, comment='成交订单数')
    per_usr_pay_amt = Column(DECIMAL(20, 2), nullable=True, comment='客单价')
    product_show_ucnt = Column(Integer, nullable=True, comment='商品曝光人数')
    product_click_ucnt = Column(Integer, nullable=True, comment='商品点击人数')
    pay_ucnt = Column(Integer, nullable=True, comment='成交人数')
    pay_plat_cost_amt = Column(DECIMAL(20, 2), nullable=True, comment='达人佣金金额')
    income_amt = Column(DECIMAL(20, 2), nullable=True, comment='成交金额')
    refund_amt_rate = Column(DECIMAL(10, 4), nullable=True, comment='退款率(支付时间)')
    rfndsuc_amt = Column(DECIMAL(20, 2), nullable=True, comment='退款金额(退款时间)')
    rfndsuc_amt_pay_time = Column(DECIMAL(20, 2), nullable=True, comment='退款金额(支付时间)')
    refund_order_cnt = Column(Integer, nullable=True, comment='退款订单数(退款时间)')
    refund_amt_pay_time = Column(DECIMAL(20, 2), nullable=True, comment='退款金额(支付时间)')
    refund_order_cnt_pay_time = Column(Integer, nullable=True, comment='退款订单数(支付时间)')
    product_show_click_cnt_ratio = Column(DECIMAL(10, 4), nullable=True, comment='商品曝光-点击转化率(次数)')
    product_show_cnt = Column(Integer, nullable=True, comment='商品曝光次数')
    product_click_pay_cnt_ratio = Column(DECIMAL(10, 4), nullable=True, comment='商品点击-成交转化率(次数)')
    gpm = Column(DECIMAL(20, 2), nullable=True, comment='千次曝光成交金额')
    product_click_cnt = Column(Integer, nullable=True, comment='商品点击次数')
    refund_amt = Column(DECIMAL(20, 2), nullable=True, comment='退款金额')
    refunded_pay_amt_pay_time = Column(DECIMAL(20, 2), nullable=True, comment='退款后用户支付金额(支付时间)')
    refund_pay_qc_plat_coupon_amt_pay_time = Column(DECIMAL(20, 2), nullable=True, comment='退款后智能优惠券(支付时间)')
    deposit_pay_amt = Column(DECIMAL(20, 2), nullable=True, comment='预售定金')
    author_subsidy_amt = Column(DECIMAL(20, 2), nullable=True, comment='达人补贴金额')
    refund_pay_plat_cost_amt_pay_time = Column(DECIMAL(20, 2), nullable=True, comment='退款后达人佣金优惠券金额(支付时间)')
    pay_qc_plat_coupon_amt = Column(DECIMAL(20, 2), nullable=True, comment='智能优惠券')
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class DdRealHourlyTrend(Base):
    """
    抖店实时小时趋势表
    """

    __tablename__ = 'dd_real_hourly_trend'
    __table_args__ = {'comment': '抖店实时小时趋势表'}

    id = Column(CHAR(32), primary_key=True, nullable=False, comment='主键ID')
    bind_user_id = Column(BigInteger, nullable=False, comment='绑定的数据用户ID')
    collect_date = Column(Date, nullable=False, comment='采集时间')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(255), nullable=True, comment='店铺id')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    real_time = Column(DateTime, nullable=True, comment='采集实时时间')
    index_name = Column(String(100), nullable=False, comment='指标名称')
    index_display = Column(String(255), nullable=True, comment='指标显示名称')
    index_unit = Column(Integer, nullable=True, comment='指标单位类型')
    hour = Column(Integer, nullable=False, comment='小时(0-23)')
    hour_str = Column(String(10), nullable=True, comment='小时字符串(如00:00)')
    today_value = Column(DECIMAL(20, 2), nullable=True, comment='今日值')
    yesterday_value = Column(DECIMAL(20, 2), nullable=True, comment='昨日值')
    value_diff = Column(DECIMAL(20, 2), nullable=True, comment='今日-昨日差值')
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


class DdRealIncomeExpenditureOverview(Base):
    """
    抖店实时收支概览表
    """

    __tablename__ = 'dd_real_income_expenditure_overview'
    __table_args__ = {'comment': '抖店实时收支概览表'}

    id = Column(CHAR(32), primary_key=True, nullable=False, comment='主键ID')
    bind_user_id = Column(BigInteger, nullable=False, comment='绑定的数据用户ID')
    collect_date = Column(Date, nullable=False, comment='采集时间')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(255), nullable=True, comment='店铺id')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    real_time = Column(DateTime, nullable=True, comment='实时时间')
    income_amt = Column(DECIMAL(20, 2), nullable=True, comment='成交金额')
    pay_amt = Column(DECIMAL(20, 2), nullable=True, comment='用户支付金额')
    pay_qc_plat_coupon_amt = Column(DECIMAL(20, 2), nullable=True, comment='智能优惠券')
    pay_plat_cost_amt = Column(DECIMAL(20, 2), nullable=True, comment='达人佣金金额')
    homepage_other_pay_amt = Column(DECIMAL(20, 2), nullable=True, comment='其它')
    cost_amt = Column(DECIMAL(20, 2), nullable=True, comment='支出金额')
    ad_cost = Column(DECIMAL(20, 2), nullable=True, comment='投放消耗')
    shop_serv_amt = Column(DECIMAL(20, 2), nullable=True, comment='技术服务费')
    real_commission = Column(DECIMAL(20, 2), nullable=True, comment='实际佣金')
    ad_expense_ratio_with_refund = Column(DECIMAL(10, 4), nullable=True, comment='投放费比')
    refund_amt_rate = Column(DECIMAL(10, 4), nullable=True, comment='退款率')
    refund_amt_pay_time = Column(DECIMAL(20, 2), nullable=True, comment='退款金额(支付时间)')
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')
