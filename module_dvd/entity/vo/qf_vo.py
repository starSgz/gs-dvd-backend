from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class QfOverviewModel(BaseModel):
    """
    千帆数据概览对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[str] = Field(default=None, description='主键ID')
    collect_date: Optional[date] = Field(default=None, description='采集时间')
    store_name: Optional[str] = Field(default=None, description='店铺名称')
    store_id: Optional[str] = Field(default=None, description='店铺id')
    crawl_account: Optional[str] = Field(default=None, description='采集账号')
    dtm: Optional[str] = Field(default=None, description='时间')
    pay_gmv: Optional[Decimal] = Field(default=None, description='支付金额')
    note_pay_gmv: Optional[Decimal] = Field(default=None, description='笔记支付金额')
    live_pay_gmv: Optional[Decimal] = Field(default=None, description='直播支付金额')
    card_pay_gmv: Optional[Decimal] = Field(default=None, description='商卡支付金额')
    pay_pkg_cnt: Optional[int] = Field(default=None, description='支付订单数')
    note_pay_pkg_cnt: Optional[int] = Field(default=None, description='笔记支付订单数')
    live_pay_pkg_cnt: Optional[int] = Field(default=None, description='直播支付订单数')
    card_pay_pkg_cnt: Optional[int] = Field(default=None, description='商卡支付订单数')
    pay_user_num: Optional[int] = Field(default=None, description='支付买家数')
    note_pay_user_num: Optional[int] = Field(default=None, description='笔记支付买家数')
    live_pay_user_num: Optional[int] = Field(default=None, description='直播支付买家数')
    card_pay_user_num: Optional[int] = Field(default=None, description='商卡支付买家数')
    goods_uv: Optional[int] = Field(default=None, description='商品访客数')
    note_goods_uv: Optional[int] = Field(default=None, description='笔记商品访客数')
    live_goods_uv: Optional[int] = Field(default=None, description='直播商品访客数')
    card_goods_uv: Optional[int] = Field(default=None, description='商卡商品访客数')
    refund_pay_gmv: Optional[Decimal] = Field(default=None, description='退款金额（退款时间）')
    note_refund_pay_gmv: Optional[Decimal] = Field(default=None, description='笔记退款金额（退款时间）')
    live_refund_pay_gmv: Optional[Decimal] = Field(default=None, description='直播退款金额（退款时间）')
    card_refund_pay_gmv: Optional[Decimal] = Field(default=None, description='商卡退款金额（退款时间）')
    pay_refund_amt: Optional[Decimal] = Field(default=None, description='退款金额（支付时间）')
    note_pay_refund_amt: Optional[Decimal] = Field(default=None, description='笔记退款金额（支付时间）')
    live_pay_refund_amt: Optional[Decimal] = Field(default=None, description='直播退款金额（支付时间）')
    card_pay_refund_amt: Optional[Decimal] = Field(default=None, description='商卡退款金额（支付时间）')
    pay_refund_rate: Optional[Decimal] = Field(default=None, description='退款率（支付时间）')
    note_pay_refund_rate: Optional[Decimal] = Field(default=None, description='笔记退款率（支付时间）')
    live_pay_refund_rate: Optional[Decimal] = Field(default=None, description='直播退款率（支付时间）')
    card_pay_refund_rate: Optional[Decimal] = Field(default=None, description='商卡退款率（支付时间）')
    pay_refund_pkg_cnt: Optional[Decimal] = Field(default=None, description='退款订单数（支付时间）')
    note_pay_refund_pkg_cnt: Optional[Decimal] = Field(default=None, description='笔记退款订单数（支付时间）')
    live_pay_refund_pkg_cnt: Optional[Decimal] = Field(default=None, description='直播退款订单数（支付时间）')
    card_pay_refund_pkg_cnt: Optional[Decimal] = Field(default=None, description='商卡退款订单数（支付时间）')
    pay_refund_rate_before_ship: Optional[Decimal] = Field(default=None, description='发货前退款率（支付时间）')
    note_pay_refund_rate_before_ship: Optional[Decimal] = Field(default=None, description='笔记发货前退款率（支付时间）')
    live_pay_refund_rate_before_ship: Optional[Decimal] = Field(default=None, description='直播发货前退款率（支付时间）')
    card_pay_refund_rate_before_ship: Optional[Decimal] = Field(default=None, description='商卡发货前退款率（支付时间）')
    pay_refund_rate_after_ship: Optional[Decimal] = Field(default=None, description='发货后退款率（支付时间）')
    note_pay_refund_rate_after_ship: Optional[Decimal] = Field(default=None, description='笔记发货后退款率（支付时间）')
    live_pay_refund_rate_after_ship: Optional[Decimal] = Field(default=None, description='直播发货后退款率（支付时间）')
    card_pay_refund_rate_after_ship: Optional[Decimal] = Field(default=None, description='商卡发货后退款率（支付时间）')
    pay_net_amt: Optional[Decimal] = Field(default=None, description='退款后支付金额（支付时间）')
    note_pay_net_amt: Optional[Decimal] = Field(default=None, description='笔记退款后支付金额（支付时间）')
    live_pay_net_amt: Optional[Decimal] = Field(default=None, description='直播退款后支付金额（支付时间）')
    card_pay_net_amt: Optional[Decimal] = Field(default=None, description='商卡退款后支付金额（支付时间）')
    upr: Optional[Decimal] = Field(default=None, description='支付转化率')
    note_upr: Optional[Decimal] = Field(default=None, description='笔记支付转化率')
    live_upr: Optional[Decimal] = Field(default=None, description='直播支付转化率')
    card_upr: Optional[Decimal] = Field(default=None, description='商卡支付转化率')
    pay_goods_cnt: Optional[Decimal] = Field(default=None, description='支付件数')
    cart_user_num: Optional[Decimal] = Field(default=None, description='加购人数')
    cart_goods_cnt: Optional[Decimal] = Field(default=None, description='加购件数')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')


class DashboardMetricsModel(BaseModel):
    """
    大屏核心指标模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    total_orders: int = Field(description='总订单数')
    total_gmv: Decimal = Field(description='总销售额')


class StoreSalesRankModel(BaseModel):
    """
    店铺销售排行模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    rank: int = Field(description='排名')
    store_name: str = Field(description='店铺名称')
    order_count: int = Field(description='订单数')
    sales_amount: Decimal = Field(description='销售额')


class ChannelSalesModel(BaseModel):
    """
    渠道销售数据模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    channel_name: str = Field(description='渠道名称')
    sales_count: int = Field(description='销量')
    sales_amount: Decimal = Field(description='销售额')
    avg_price: Decimal = Field(description='平均价格')


class OrderTimelineModel(BaseModel):
    """
    订单时间线模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    store_name: str = Field(description='店铺名称')
    channel: str = Field(description='渠道')
    order_amount: Decimal = Field(description='订单金额')
    order_time: str = Field(description='订单时间')


class TrendDataModel(BaseModel):
    """
    趋势图数据模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    time_labels: list[str] = Field(description='时间标签')
    gmv_data: list[float] = Field(description='GMV数据')
    order_data: list[int] = Field(description='订单数据')
    note_data: list[float] = Field(description='笔记数据')
    live_data: list[float] = Field(description='直播数据')
    card_data: list[float] = Field(description='商卡数据')

