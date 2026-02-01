from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, Column, Date, DateTime, String, DECIMAL, text

from config.database import Base


class QfRealtimeMetrics(Base):
    """
    千帆实时指标表
    """

    __tablename__ = 'qf_realtime_metrics'
    __table_args__ = {'comment': '千帆实时指标表'}

    id = Column(CHAR(32), primary_key=True, nullable=False)
    collect_date = Column(Date, nullable=False, comment='采集日期')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(255), nullable=True, comment='店铺id')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    # crawl_time = Column(DateTime, nullable=False, comment='入库时间')
    pay_amount = Column(DECIMAL(20, 4), nullable=True, comment='支付金额')
    pay_order_count = Column(DECIMAL(20, 4), nullable=True, comment='支付订单数')
    goods_visit_count = Column(DECIMAL(20, 4), nullable=True, comment='商品访问量')
    refund_amount = Column(DECIMAL(20, 4), nullable=True, comment='退款金额')
    pay_buyer_count = Column(DECIMAL(20, 4), nullable=True, comment='支付买家数')
    account_balance = Column(DECIMAL(20, 4), nullable=True, comment='可提现余额')
    shop_page_visit = Column(DECIMAL(20, 4), nullable=True, comment='店铺访问页面')
    cps_pay_amount = Column(DECIMAL(20, 4), nullable=True, comment='买手支付额')
    ad_pay_amount = Column(DECIMAL(20, 4), nullable=True, comment='广告支付额')
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')

