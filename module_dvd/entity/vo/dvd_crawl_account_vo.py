from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


class CrawlAccountModel(BaseModel):
    """
    采集账号信息表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    id: Optional[int] = Field(default=None, description='自增主键')
    platform_id: Optional[str] = Field(default=None, description='平台ID')
    product_id: Optional[str] = Field(default=None, description='产品ID')
    account: Optional[str] = Field(default=None, description='账号（手机号/邮箱/用户名）')
    password: Optional[str] = Field(default=None, description='密码')
    cookies: Optional[str] = Field(default=None, description='Cookies信息（JSON/字符串格式）')
    status: Optional[Literal[1, 2, 3]] = Field(default=1, description='状态：1-正常，2-过期，3-异常')
    bind_user_id: Optional[int] = Field(default=None, description='绑定的用户ID')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    unique_md5: Optional[str] = Field(default=None, description='唯一标识MD5')
    store_names: Optional[list[str]] = Field(default=None, description='关联的店铺名称列表')

    @NotBlank(field_name='platform_id', message='平台不能为空')
    def get_platform_id(self) -> Union[str, None]:
        return self.platform_id

    @NotBlank(field_name='product_id', message='产品不能为空')
    def get_product_id(self) -> Union[str, None]:
        return self.product_id

    @NotBlank(field_name='account', message='账号不能为空')
    @Size(field_name='account', min_length=1, max_length=100, message='账号长度不能超过100个字符')
    def get_account(self) -> Union[str, None]:
        return self.account

    def validate_fields(self) -> None:
        self.get_platform_id()
        self.get_product_id()
        self.get_account()


class CrawlAccountQueryModel(BaseModel):
    """
    采集账号查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    platform_id: Optional[str] = Field(default=None, description='平台ID')
    product_id: Optional[str] = Field(default=None, description='产品ID')
    account: Optional[str] = Field(default=None, description='账号')
    status: Optional[Union[int, str]] = Field(default=None, description='状态')
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    
    @field_validator('status', mode='before')
    @classmethod
    def validate_status(cls, v):
        if v is None:
            return None
        # 如果是字符串，转换为整数
        if isinstance(v, str):
            try:
                v = int(v)
            except ValueError:
                raise ValueError('status must be a valid integer')
        # 验证值是否在允许范围内
        if v not in [1, 2, 3]:
            raise ValueError('status must be 1, 2, or 3')
        return v


class DeleteCrawlAccountModel(BaseModel):
    """
    删除采集账号模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    ids: str = Field(description='需要删除的账号ID')


class QRCodeResponseModel(BaseModel):
    """
    二维码响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    qrcode_base64: str = Field(description='二维码base64编码')
    token: str = Field(description='登录token')


class QRCodeStatusModel(BaseModel):
    """
    二维码状态查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    token: str = Field(description='登录token')
    account_id: Optional[int] = Field(default=None, description='账号ID')


class QRCodeRequestModel(BaseModel):
    """
    获取二维码请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    platform_id: str = Field(description='平台ID')
    product_id: str = Field(description='产品ID')
