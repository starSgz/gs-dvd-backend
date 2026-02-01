from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String, VARCHAR

from config.database import Base


class DvdConfigMenu(Base):
    """
    DVD配置菜单表
    """

    __tablename__ = 'dvd_config_menu'
    __table_args__ = {'comment': 'DVD配置菜单表'}

    dvd_config_menu_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='菜单ID')
    dvd_config_menu_name = Column(String(50), nullable=False, comment='菜单名称')
    dvd_config_parent_id = Column(BigInteger, nullable=True, server_default='0', comment='父菜单ID')
    order_num = Column(Integer, nullable=True, server_default='0', comment='显示顺序')
    dvd_config_menu_type = Column(CHAR(1), nullable=True, server_default="", comment='菜单类型（P平台 D产品(数据端) F方法）')
    status = Column(CHAR(1), nullable=True, server_default='0', comment='菜单状态（0正常 1停用）')
    logo = Column(VARCHAR(100), nullable=True, comment='产品LOGO')
    screenshot_url = Column(VARCHAR(200), nullable=True, comment='功能截图地址')
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
