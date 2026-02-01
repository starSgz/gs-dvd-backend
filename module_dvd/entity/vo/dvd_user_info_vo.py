from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class DvdUserInfoModel(BaseModel):
    """
    DVD用户信息响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    nick_name: Optional[str] = Field(default=None, description='用户昵称')
    access_key: Optional[str] = Field(default=None, description='绑定的卡密')
    expire_time: Optional[datetime] = Field(default=None, description='卡密到期时间')
