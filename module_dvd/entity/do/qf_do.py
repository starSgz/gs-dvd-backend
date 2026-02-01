from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, Column, Date, DateTime, BigInteger, String, DECIMAL, text

from config.database import Base


class QfOverview(Base):
    """
    千帆数据概览表
    """

    __tablename__ = 'qf_overview'
    __table_args__ = {'comment': '千帆数据概览表'}

    id = Column(CHAR(32), primary_key=True, nullable=False, comment='主键ID')
    collect_date = Column(Date, nullable=False, comment='采集时间')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(255), nullable=True, comment='店铺id')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    dtm = Column(String(255), nullable=True, comment='时间')
    pay_gmv = Column(DECIMAL(20, 4), nullable=True, comment='支付金额')
    note_pay_gmv = Column(DECIMAL(20, 4), nullable=True, comment='笔记支付金额')
    live_pay_gmv = Column(DECIMAL(20, 4), nullable=True, comment='直播支付金额')
    card_pay_gmv = Column(DECIMAL(20, 4), nullable=True, comment='商卡支付金额')
    pay_pkg_cnt = Column(BigInteger, nullable=True, comment='支付订单数')
    note_pay_pkg_cnt = Column(BigInteger, nullable=True, comment='笔记支付订单数')
    live_pay_pkg_cnt = Column(BigInteger, nullable=True, comment='直播支付订单数')
    card_pay_pkg_cnt = Column(BigInteger, nullable=True, comment='商卡支付订单数')
    pay_user_num = Column(BigInteger, nullable=True, comment='支付买家数')
    note_pay_user_num = Column(BigInteger, nullable=True, comment='笔记支付买家数')
    live_pay_user_num = Column(BigInteger, nullable=True, comment='直播支付买家数')
    card_pay_user_num = Column(BigInteger, nullable=True, comment='商卡支付买家数')
    goods_uv = Column(BigInteger, nullable=True, comment='商品访客数')
    note_goods_uv = Column(BigInteger, nullable=True, comment='笔记商品访客数')
    live_goods_uv = Column(BigInteger, nullable=True, comment='直播商品访客数')
    card_goods_uv = Column(BigInteger, nullable=True, comment='商卡商品访客数')
    refund_pay_gmv = Column(DECIMAL(20, 4), nullable=True, comment='退款金额（退款时间）')
    note_refund_pay_gmv = Column(DECIMAL(20, 4), nullable=True, comment='笔记退款金额（退款时间）')
    live_refund_pay_gmv = Column(DECIMAL(20, 4), nullable=True, comment='直播退款金额（退款时间）')
    card_refund_pay_gmv = Column(DECIMAL(20, 4), nullable=True, comment='商卡退款金额（退款时间）')
    pay_refund_amt = Column(DECIMAL(20, 4), nullable=True, comment='退款金额（支付时间）')
    note_pay_refund_amt = Column(DECIMAL(20, 4), nullable=True, comment='笔记退款金额（支付时间）')
    live_pay_refund_amt = Column(DECIMAL(20, 4), nullable=True, comment='直播退款金额（支付时间）')
    card_pay_refund_amt = Column(DECIMAL(20, 4), nullable=True, comment='商卡退款金额（支付时间）')
    pay_refund_rate = Column(DECIMAL(20, 4), nullable=True, comment='退款率（支付时间）')
    note_pay_refund_rate = Column(DECIMAL(20, 4), nullable=True, comment='笔记退款率（支付时间）')
    live_pay_refund_rate = Column(DECIMAL(20, 4), nullable=True, comment='直播退款率（支付时间）')
    card_pay_refund_rate = Column(DECIMAL(20, 4), nullable=True, comment='商卡退款率（支付时间）')
    pay_refund_pkg_cnt = Column(DECIMAL(20, 4), nullable=True, comment='退款订单数（支付时间）')
    note_pay_refund_pkg_cnt = Column(DECIMAL(20, 4), nullable=True, comment='笔记退款订单数（支付时间）')
    live_pay_refund_pkg_cnt = Column(DECIMAL(20, 4), nullable=True, comment='直播退款订单数（支付时间）')
    card_pay_refund_pkg_cnt = Column(DECIMAL(20, 4), nullable=True, comment='商卡退款订单数（支付时间）')
    pay_refund_rate_before_ship = Column(DECIMAL(20, 4), nullable=True, comment='发货前退款率（支付时间）')
    note_pay_refund_rate_before_ship = Column(DECIMAL(20, 4), nullable=True, comment='笔记发货前退款率（支付时间）')
    live_pay_refund_rate_before_ship = Column(DECIMAL(20, 4), nullable=True, comment='直播发货前退款率（支付时间）')
    card_pay_refund_rate_before_ship = Column(DECIMAL(20, 4), nullable=True, comment='商卡发货前退款率（支付时间）')
    pay_refund_rate_after_ship = Column(DECIMAL(20, 4), nullable=True, comment='发货后退款率（支付时间）')
    note_pay_refund_rate_after_ship = Column(DECIMAL(20, 4), nullable=True, comment='笔记发货后退款率（支付时间）')
    live_pay_refund_rate_after_ship = Column(DECIMAL(20, 4), nullable=True, comment='直播发货后退款率（支付时间）')
    card_pay_refund_rate_after_ship = Column(DECIMAL(20, 4), nullable=True, comment='商卡发货后退款率（支付时间）')
    pay_net_amt = Column(DECIMAL(20, 4), nullable=True, comment='退款后支付金额（支付时间）')
    note_pay_net_amt = Column(DECIMAL(20, 4), nullable=True, comment='笔记退款后支付金额（支付时间）')
    live_pay_net_amt = Column(DECIMAL(20, 4), nullable=True, comment='直播退款后支付金额（支付时间）')
    card_pay_net_amt = Column(DECIMAL(20, 4), nullable=True, comment='商卡退款后支付金额（支付时间）')
    upr = Column(DECIMAL(20, 4), nullable=True, comment='支付转化率')
    note_upr = Column(DECIMAL(20, 4), nullable=True, comment='笔记支付转化率')
    live_upr = Column(DECIMAL(20, 4), nullable=True, comment='直播支付转化率')
    card_upr = Column(DECIMAL(20, 4), nullable=True, comment='商卡支付转化率')
    pay_goods_cnt = Column(DECIMAL(20, 4), nullable=True, comment='支付件数')
    cart_user_num = Column(DECIMAL(20, 4), nullable=True, comment='加购人数')
    cart_goods_cnt = Column(DECIMAL(20, 4), nullable=True, comment='加购件数')
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='更新时间')

