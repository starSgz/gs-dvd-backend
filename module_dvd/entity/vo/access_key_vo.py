from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class AccessKeyModel(BaseModel):
    """
    卡密表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    access_key: Optional[str] = Field(default=None, description='卡密')
    bind_store_num: Optional[int] = Field(default=5, description='可绑定店铺数量')
    flag: Optional[Literal['0', '1']] = Field(default='0', description='是否有效（0有效 1过期）')
    is_used: Optional[Literal['0', '1']] = Field(default='0', description='是否被使用（0未使用 1已使用）')
    used_time: Optional[datetime] = Field(default=None, description='被使用时间')
    use_deadline: Optional[datetime] = Field(default=None, description='使用截止日期')
    duration_hours: Optional[int] = Field(default=0, description='可激活时长(小时)')
    remark: Optional[str] = Field(default=None, description='备注')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_date: Optional[datetime] = Field(default=None, description='更新时间')


class AccessKeyQueryModel(AccessKeyModel):
    """
    卡密管理不分页查询模型
    """

    # 覆盖父类默认值，查询时默认不过滤
    flag: Optional[Literal['0', '1']] = Field(default=None, description='是否有效（0有效 1过期）')
    is_used: Optional[Literal['0', '1']] = Field(default=None, description='是否被使用（0未使用 1已使用）')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class AccessKeyPageQueryModel(AccessKeyQueryModel):
    """
    卡密管理分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class AccessKeyCreateModel(BaseModel):
    """
    新增卡密模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    years: int = Field(default=0, ge=0, description='时长-年')
    months: int = Field(default=0, ge=0, description='时长-月')
    days: int = Field(default=0, ge=0, description='时长-天')
    hours: int = Field(default=0, ge=0, description='时长-小时')
    deadline_years: int = Field(default=0, ge=0, description='截止日期-年')
    deadline_months: int = Field(default=0, ge=0, description='截止日期-月')
    deadline_days: int = Field(default=0, ge=0, description='截止日期-天')
    deadline_hours: int = Field(default=0, ge=0, description='截止日期-小时')
    bind_store_num: int = Field(default=5, ge=1, description='可绑定店铺数量')
    remark: Optional[str] = Field(default=None, max_length=500, description='备注')

    def to_total_hours(self) -> int:
        """将年月日时转换为总小时数"""
        return self.years * 365 * 24 + self.months * 30 * 24 + self.days * 24 + self.hours

    def get_use_deadline(self) -> Optional[datetime]:
        """计算使用截止日期，如果没有设置则返回None"""
        total_hours = self.deadline_years * 365 * 24 + self.deadline_months * 30 * 24 + self.deadline_days * 24 + self.deadline_hours
        if total_hours <= 0:
            return None
        from datetime import timedelta
        return datetime.now() + timedelta(hours=total_hours)


class DeleteAccessKeyModel(BaseModel):
    """
    删除卡密模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    access_keys: str = Field(description='需要删除的卡密，多个用逗号分隔')


class ActivateAccessKeyModel(BaseModel):
    """
    激活卡密请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    access_key: str = Field(description='要激活的卡密')


class ActivateAccessKeyResponseModel(BaseModel):
    """
    激活卡密响应模型
    """

    model_config = ConfigDict(
        alias_generator=to_camel, 
        populate_by_name=True,
        from_attributes=True
    )

    access_key: str = Field(description='卡密')
    expire_time: Optional[datetime] = Field(default=None, description='到期时间')
    message: str = Field(description='激活结果消息')