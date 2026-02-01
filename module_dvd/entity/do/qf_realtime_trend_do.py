from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, Column, Date, DateTime, String, DECIMAL, text

from config.database import Base


class QfRealtimeTrend(Base):
    """
    千帆实时趋势表
    """

    __tablename__ = 'qf_realtime_trend'
    __table_args__ = {'comment': '千帆实时趋势表'}

    id = Column(CHAR(32), primary_key=True, nullable=False, comment='主键ID')
    collect_date = Column(Date, nullable=False, comment='采集时间')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(255), nullable=True, comment='店铺id')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    dtm = Column(String(255), nullable=True, comment='时间点(00-23)')
    pay_net_amt = Column(DECIMAL(20, 4), nullable=True, comment='净支付金额')
    card_click_cnt = Column(DECIMAL(20, 4), nullable=True, comment='商品卡片点击次数')
    pay_refund_rate_after_ship = Column(DECIMAL(20, 4), nullable=True, comment='发货后退款率')
    note_seller_real_income_amt = Column(DECIMAL(20, 4), nullable=True, comment='笔记实际收入金额')
    pay_refund_pkg_cnt_before_ship_only = Column(DECIMAL(20, 4), nullable=True, comment='仅发货前退款包裹数')
    pay_refund_pkg_cnt_after_ship_only = Column(DECIMAL(20, 4), nullable=True, comment='仅发货后退款包裹数')
    card_click_user_num = Column(DECIMAL(20, 4), nullable=True, comment='商品卡片点击用户数')
    live_seller_real_income_amt = Column(DECIMAL(20, 4), nullable=True, comment='直播实际收入金额')
    add_cart_goods_num = Column(DECIMAL(20, 4), nullable=True, comment='加购商品数')
    pay_refund_amt_after_ship_only = Column(DECIMAL(20, 4), nullable=True, comment='仅发货后退款金额')
    pay_refund_amt_before_ship_only = Column(DECIMAL(20, 4), nullable=True, comment='仅发货前退款金额')
    add_cart_user_num = Column(DECIMAL(20, 4), nullable=True, comment='加购用户数')
    pay_refund_pkg_cnt = Column(DECIMAL(20, 4), nullable=True, comment='退款包裹数')
    upr = Column(DECIMAL(20, 4), nullable=True, comment='支付转化率')
    pay_refund_rate = Column(DECIMAL(20, 4), nullable=True, comment='退款率')
    pay_refund_amt = Column(DECIMAL(20, 4), nullable=True, comment='退款金额')
    upr_pv = Column(DECIMAL(20, 4), nullable=True, comment='PV支付转化率')
    seller_real_income_amt = Column(DECIMAL(20, 4), nullable=True, comment='实际收入金额')
    deal_goods_cnt = Column(DECIMAL(20, 4), nullable=True, comment='成交商品数')
    pay_refund_amt_with_return = Column(DECIMAL(20, 4), nullable=True, comment='含退货退款金额')
    refund_amt = Column(DECIMAL(20, 4), nullable=True, comment='退款金额')
    pay_refund_pkg_cnt_with_return = Column(DECIMAL(20, 4), nullable=True, comment='含退货退款包裹数')
    deal_order_cnt = Column(DECIMAL(20, 4), nullable=True, comment='成交订单数')
    pct = Column(DECIMAL(20, 4), nullable=True, comment='PCT')
    card_seller_real_income_amt = Column(DECIMAL(20, 4), nullable=True, comment='商卡实际收入金额')
    deal_user_num = Column(DECIMAL(20, 4), nullable=True, comment='成交用户数')
    pay_refund_rate_before_ship = Column(DECIMAL(20, 4), nullable=True, comment='发货前退款率')
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间')


