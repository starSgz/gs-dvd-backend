from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, VARCHAR

from config.database import Base


class DvdAccessKey(Base):
    """
    卡密表
    """

    __tablename__ = 'dvd_access_key'
    __table_args__ = {'comment': '卡密表'}

    access_key = Column(VARCHAR(255), primary_key=True, nullable=False, comment='卡密')
    bind_store_num = Column(Integer, nullable=True, server_default='5', comment='可绑定店铺数量')
    flag = Column(VARCHAR(5), nullable=True, server_default='0', comment='是否有效 1过期 0有效')
    is_used = Column(VARCHAR(5), nullable=True, server_default='0', comment='是否被使用 1已使用 0未使用')
    used_time = Column(DateTime, nullable=True, comment='被使用时间')
    use_deadline = Column(DateTime, nullable=True, comment='使用截止日期')
    duration_hours = Column(Integer, nullable=True, server_default='0', comment='可激活时长(小时)')
    remark = Column(String(500), nullable=True, comment='备注')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_date = Column(DateTime, nullable=True, onupdate=datetime.now, comment='更新时间')
