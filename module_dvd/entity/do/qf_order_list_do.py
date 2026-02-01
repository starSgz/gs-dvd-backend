from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, Column, Date, DateTime, String, DECIMAL, Text, text

from config.database import Base


class QfOrderList(Base):
    """
    千帆订单列表表
    """

    __tablename__ = 'qf_order_list'
    __table_args__ = {'comment': '千帆订单列表表'}

    id = Column(CHAR(32), primary_key=True, nullable=False, comment='主键ID')
    collect_date = Column(Date, nullable=False, comment='采集时间')
    store_name = Column(String(255), nullable=True, comment='店铺名称')
    store_id = Column(String(255), nullable=True, comment='店铺id')
    crawl_account = Column(String(255), nullable=True, comment='采集账号')
    package_id = Column(String(255), nullable=True, comment='订单包裹ID')
    sku_id = Column(String(255), nullable=True, comment='SKU ID')
    nick_name = Column(String(255), nullable=True, comment='买家昵称')
    ordered_at = Column(String(255), nullable=True, comment='下单时间')
    name = Column(String(255), nullable=True, comment='买家姓名')
    sold_price = Column(DECIMAL(20, 4), nullable=True, comment='售价')
    specification = Column(Text, nullable=True, comment='规格')
    sku_name = Column(Text, nullable=True, comment='SKU名称')
    sku_raw_price = Column(DECIMAL(20, 4), nullable=True, comment='SKU原价')
    after_sale_status_desc = Column(String(255), nullable=True, comment='售后状态描述')
    express_company_name = Column(String(255), nullable=True, comment='快递公司名称')
    sku_total_paid_amount = Column(DECIMAL(20, 4), nullable=True, comment='SKU总实付金额')
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='更新时间')

