from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


class ConfigMenuModel(BaseModel):
    """
    DVD配置菜单表对应pydantic模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    dvd_config_menu_id: Optional[int] = Field(default=None, description='菜单ID')
    dvd_config_menu_name: Optional[str] = Field(default=None, description='菜单名称')
    dvd_config_parent_id: Optional[int] = Field(default=None, description='父菜单ID')
    order_num: Optional[int] = Field(default=None, description='显示顺序')
    dvd_config_menu_type: Optional[Literal['P', 'D', 'C', 'F']] = Field(
        default=None, description='菜单类型（P平台 D产品 C数据口径 F方法）'
    )
    status: Optional[Literal['0', '1']] = Field(default=None, description='菜单状态（0正常 1停用）')
    logo: Optional[str] = Field(default=None, description='产品LOGO')
    screenshot_url: Optional[str] = Field(default=None, description='功能截图地址')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='dvd_config_menu_name', message='菜单名称不能为空')
    @Size(field_name='dvd_config_menu_name', min_length=0, max_length=50, message='菜单名称长度不能超过50个字符')
    def get_menu_name(self) -> Union[str, None]:
        return self.dvd_config_menu_name

    @NotBlank(field_name='order_num', message='显示顺序不能为空')
    def get_order_num(self) -> Union[int, None]:
        return self.order_num

    @NotBlank(field_name='dvd_config_menu_type', message='菜单类型不能为空')
    def get_menu_type(self) -> Union[Literal['P', 'D', 'C', 'F'], None]:
        return self.dvd_config_menu_type

    @Size(field_name='remark', min_length=0, max_length=500, message='备注长度不能超过500个字符')
    def get_remark(self) -> Union[str, None]:
        return self.remark

    def validate_fields(self) -> None:
        self.get_menu_name()
        self.get_order_num()
        self.get_menu_type()
        self.get_remark()


class ConfigMenuQueryModel(ConfigMenuModel):
    """
    DVD配置菜单查询模型
    """

    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class ConfigMenuTreeModel(BaseModel):
    """
    DVD配置菜单树模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    id: int = Field(description='菜单id')
    label: str = Field(description='菜单名称')
    parent_id: int = Field(description='父菜单id')
    children: Optional[list['ConfigMenuTreeModel']] = Field(default=None, description='子菜单树')


class DeleteConfigMenuModel(BaseModel):
    """
    删除DVD配置菜单模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    dvd_config_menu_ids: str = Field(description='需要删除的菜单ID')
