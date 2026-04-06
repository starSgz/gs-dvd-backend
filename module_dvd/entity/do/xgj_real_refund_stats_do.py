from sqlalchemy import CHAR, BigInteger, Column, Date, DateTime, DECIMAL, SmallInteger, String, text

from config.database import Base


class XgjRealRefundStats(Base):
    """
    闲鱼实时退款维度快照表
    """

    __tablename__ = 'xgj_real_refund_stats'
    __table_args__ = {'comment': '闲鱼实时退款维度快照表'}

    id = Column(CHAR(32), primary_key=True, nullable=False)
    bind_user_id = Column(BigInteger, nullable=False, comment='绑定用户ID')
    collect_date = Column(Date, nullable=False, comment='采集日期')
    collect_hour = Column(SmallInteger, nullable=False, comment='采集小时')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(64), nullable=True, comment='店铺ID')
    authorize_id = Column(String(64), nullable=True, comment='店铺authorize_id')
    user_nick = Column(String(255), nullable=True, comment='闲鱼昵称')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    about_to_timeout_num = Column(DECIMAL(20, 4), nullable=True, comment='24小时内即将超时')
    seller_pending_num = Column(DECIMAL(20, 4), nullable=True, comment='待商家处理')
    buyer_pending_num = Column(DECIMAL(20, 4), nullable=True, comment='待买家处理')
    update_time = Column(
        DateTime,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
        comment='更新时间',
    )
