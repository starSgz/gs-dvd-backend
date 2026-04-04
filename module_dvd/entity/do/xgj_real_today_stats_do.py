from sqlalchemy import CHAR, BigInteger, Column, Date, DateTime, DECIMAL, SmallInteger, String, text

from config.database import Base


class XgjRealTodayStats(Base):
    """
    闲鱼实时今日指标快照表
    """

    __tablename__ = 'xgj_real_today_stats'
    __table_args__ = {'comment': '闲鱼实时今日指标快照表'}

    id = Column(CHAR(32), primary_key=True, nullable=False)
    bind_user_id = Column(BigInteger, nullable=False, comment='绑定用户ID')
    collect_date = Column(Date, nullable=False, comment='采集日期')
    collect_hour = Column(SmallInteger, nullable=False, comment='采集小时')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(64), nullable=True, comment='店铺ID')
    authorize_id = Column(String(64), nullable=True, comment='店铺authorize_id')
    user_nick = Column(String(255), nullable=True, comment='闲鱼昵称')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    pay_amount_today = Column(DECIMAL(20, 4), nullable=True, comment='支付金额今日值')
    pay_amount_yesterday = Column(DECIMAL(20, 4), nullable=True, comment='支付金额昨日值')
    pay_amount_compare = Column(String(64), nullable=True, comment='支付金额对比值')
    pay_order_num_today = Column(DECIMAL(20, 4), nullable=True, comment='支付订单数今日值')
    pay_order_num_yesterday = Column(DECIMAL(20, 4), nullable=True, comment='支付订单数昨日值')
    pay_order_num_compare = Column(String(64), nullable=True, comment='支付订单数对比值')
    unit_price_today = Column(DECIMAL(20, 4), nullable=True, comment='支付客单价今日值')
    unit_price_yesterday = Column(DECIMAL(20, 4), nullable=True, comment='支付客单价昨日值')
    unit_price_compare = Column(String(64), nullable=True, comment='支付客单价对比值')
    new_product_num_today = Column(DECIMAL(20, 4), nullable=True, comment='新发布商品今日值')
    new_product_num_yesterday = Column(DECIMAL(20, 4), nullable=True, comment='新发布商品昨日值')
    new_product_num_compare = Column(String(64), nullable=True, comment='新发布商品对比值')
    pending_payment_num = Column(DECIMAL(20, 4), nullable=True, comment='待付款')
    wait_send_num = Column(DECIMAL(20, 4), nullable=True, comment='待发货')
    shipped_num = Column(DECIMAL(20, 4), nullable=True, comment='已发货')
    pending_after_sale_num = Column(DECIMAL(20, 4), nullable=True, comment='待售后')
    update_time = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
        comment='更新时间',
    )
