from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, SmallInteger, VARCHAR

from config.database import Base


class DvdAccountStoreRelation(Base):
    """
    账号-店铺关联表
    """

    __tablename__ = 'dvd_account_store_relation'
    __table_args__ = {'comment': '账号-店铺关联表'}

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    dvd_account_id = Column(BigInteger, nullable=False, comment='账号ID（关联dvd_crawl_account_info.id）')
    store_name = Column(VARCHAR(255), nullable=False, comment='店铺名称')
    platform_id = Column(VARCHAR(50), nullable=False, comment='平台ID')
    product_id = Column(VARCHAR(100), nullable=False, comment='产品ID')
    is_active = Column(SmallInteger, nullable=False, server_default='1', comment='是否激活（1-激活，0-未激活）')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间'
    )
