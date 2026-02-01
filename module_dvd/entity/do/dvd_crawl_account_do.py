from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String, Text, VARCHAR

from config.database import Base


class DvdCrawlAccountInfo(Base):
    """
    大屏采集账号信息表
    """

    __tablename__ = 'dvd_crawl_account_info'
    __table_args__ = {'comment': '大屏采集账号账号信息表'}

    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='自增主键')
    platform_id = Column(VARCHAR(50), nullable=False, comment='平台名称')
    product_id = Column(VARCHAR(100), nullable=False, comment='产品名称')
    account = Column(VARCHAR(100), nullable=False, comment='账号（手机号/邮箱/用户名）')
    password = Column(VARCHAR(255), nullable=True, comment='密码（建议加密存储）')
    cookies = Column(Text, nullable=True, comment='Cookies信息（JSON/字符串格式）')
    status = Column(Integer, nullable=False, server_default='1', comment='状态：1-正常，2-过期，3-异常')
    bind_user_id = Column(BigInteger, nullable=False, comment='绑定的用户ID')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间'
    )
    unique_md5 = Column(CHAR(32), nullable=False, unique=True, comment='唯一标识MD5(platform,product,account,bind_user_id)')
