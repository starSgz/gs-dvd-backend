from sqlalchemy import CHAR, BigInteger, Column, Date, DateTime, DECIMAL, SmallInteger, String, text

from config.database import Base


class XgjRealOrderStats(Base):
    """
    闲鱼实时订单统计表
    """

    __tablename__ = 'xgj_real_order_stats'
    __table_args__ = {'comment': '闲鱼实时订单统计表'}

    id = Column(CHAR(32), primary_key=True, nullable=False)
    bind_user_id = Column(BigInteger, nullable=False, comment='绑定用户ID')
    collect_date = Column(Date, nullable=False, comment='采集日期')
    collect_hour = Column(SmallInteger, nullable=False, comment='采集小时')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(64), nullable=True, comment='店铺ID')
    authorize_id = Column(String(64), nullable=True, comment='店铺authorize_id')
    user_nick = Column(String(255), nullable=True, comment='闲鱼昵称')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    all_order_num = Column(DECIMAL(20, 4), nullable=True, comment='所有订单数量')
    all_order_amount = Column(DECIMAL(20, 4), nullable=True, comment='所有订单金额')
    paid_order_num = Column(DECIMAL(20, 4), nullable=True, comment='付款订单数量')
    paid_order_amount = Column(DECIMAL(20, 4), nullable=True, comment='付款订单金额')
    wait_send_num = Column(DECIMAL(20, 4), nullable=True, comment='等待发货数量')
    wait_send_amount = Column(DECIMAL(20, 4), nullable=True, comment='等待发货金额')
    shipped_order_num = Column(DECIMAL(20, 4), nullable=True, comment='已经发货数量')
    shipped_order_amount = Column(DECIMAL(20, 4), nullable=True, comment='已经发货金额')
    success_order_num = Column(DECIMAL(20, 4), nullable=True, comment='交易成功数量')
    success_order_amount = Column(DECIMAL(20, 4), nullable=True, comment='交易成功金额')
    refund_order_num = Column(DECIMAL(20, 4), nullable=True, comment='已经退款数量')
    refund_order_amount = Column(DECIMAL(20, 4), nullable=True, comment='已经退款金额')
    return_after_send_num = Column(DECIMAL(20, 4), nullable=True, comment='发货后退货数量')
    return_after_send_amount = Column(DECIMAL(20, 4), nullable=True, comment='发货后退货金额')
    closed_order_num = Column(DECIMAL(20, 4), nullable=True, comment='交易关闭数量')
    closed_order_amount = Column(DECIMAL(20, 4), nullable=True, comment='交易关闭金额')
    update_time = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
        comment='更新时间',
    )
