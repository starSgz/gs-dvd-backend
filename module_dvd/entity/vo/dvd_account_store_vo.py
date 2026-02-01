from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class AccountStoreModel(BaseModel):
    """
    账号-店铺关联信息对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='主键ID')
    dvd_account_id: Optional[int] = Field(default=None, description='账号ID')
    store_name: Optional[str] = Field(default=None, description='店铺名称')
    platform_id: Optional[str] = Field(default=None, description='平台ID')
    product_id: Optional[str] = Field(default=None, description='产品ID')
    is_active: Optional[int] = Field(default=1, description='是否激活（1-激活，0-未激活）')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
