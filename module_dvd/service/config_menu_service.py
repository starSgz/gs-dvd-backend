from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from common.constant import CommonConstant
from common.vo import CrudResponseModel
from exceptions.exception import ServiceException, ServiceWarning
from module_dvd.dao.config_menu_dao import ConfigMenuDao
from module_dvd.entity.do.config_menu_do import DvdConfigMenu
from module_dvd.entity.vo.config_menu_vo import (
    ConfigMenuModel,
    ConfigMenuQueryModel,
    ConfigMenuTreeModel,
    DeleteConfigMenuModel,
)
from utils.common_util import CamelCaseUtil


class ConfigMenuService:
    """
    DVD配置菜单模块服务层
    """

    @classmethod
    async def get_config_menu_tree_services(cls, query_db: AsyncSession) -> list[dict[str, Any]]:
        """
        获取配置菜单树信息service

        :param query_db: orm对象
        :return: 配置菜单树信息对象
        """
        menu_list_result = await ConfigMenuDao.get_config_menu_list(
            query_db, ConfigMenuQueryModel(status='0')
        )
        menu_tree_model_result = cls.list_to_tree(menu_list_result)
        menu_tree_result = [menu.model_dump(exclude_unset=True, by_alias=True) for menu in menu_tree_model_result]

        return menu_tree_result

    @classmethod
    async def get_config_menu_list_services(
        cls, query_db: AsyncSession, page_object: ConfigMenuQueryModel
    ) -> list[dict[str, Any]]:
        """
        获取配置菜单列表信息service

        :param query_db: orm对象
        :param page_object: 分页查询参数对象
        :return: 配置菜单列表信息对象
        """
        menu_list_result = await ConfigMenuDao.get_config_menu_list(query_db, page_object)

        return CamelCaseUtil.transform_result(menu_list_result)

    @classmethod
    async def check_menu_name_unique_services(cls, query_db: AsyncSession, page_object: ConfigMenuModel) -> bool:
        """
        校验菜单名称是否唯一service（同一父菜单下名称不能重复）

        :param query_db: orm对象
        :param page_object: 菜单对象
        :return: 校验结果
        """
        menu_id = -1 if page_object.dvd_config_menu_id is None else page_object.dvd_config_menu_id
        # 检查同一父菜单下是否存在相同名称的菜单
        menu = await ConfigMenuDao.get_config_menu_detail_by_info(
            query_db,
            ConfigMenuModel(
                dvdConfigParentId=page_object.dvd_config_parent_id,
                dvdConfigMenuName=page_object.dvd_config_menu_name,
            ),
        )
        if menu and menu.dvd_config_menu_id != menu_id:
            return CommonConstant.NOT_UNIQUE
        return CommonConstant.UNIQUE

    @classmethod
    async def add_config_menu_services(cls, query_db: AsyncSession, page_object: ConfigMenuModel) -> CrudResponseModel:
        """
        新增配置菜单信息service

        :param query_db: orm对象
        :param page_object: 新增菜单对象
        :return: 新增菜单校验结果
        """
        if not await cls.check_menu_name_unique_services(query_db, page_object):
            raise ServiceException(message=f'新增菜单{page_object.dvd_config_menu_name}失败，同级菜单中已存在相同名称')
        try:
            await ConfigMenuDao.add_config_menu_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_config_menu_services(
        cls, query_db: AsyncSession, page_object: ConfigMenuModel
    ) -> CrudResponseModel:
        """
        编辑配置菜单信息service

        :param query_db: orm对象
        :param page_object: 编辑菜单对象
        :return: 编辑菜单校验结果
        """
        edit_menu = page_object.model_dump(exclude_unset=True)
        menu_info = await cls.config_menu_detail_services(query_db, page_object.dvd_config_menu_id)
        if menu_info.dvd_config_menu_id:
            if not await cls.check_menu_name_unique_services(query_db, page_object):
                raise ServiceException(message=f'修改菜单{page_object.dvd_config_menu_name}失败，同级菜单中已存在相同名称')
            if page_object.dvd_config_menu_id == page_object.dvd_config_parent_id:
                raise ServiceException(message=f'修改菜单{page_object.dvd_config_menu_name}失败，上级菜单不能选择自己')
            try:
                await ConfigMenuDao.edit_config_menu_dao(query_db, edit_menu)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='菜单不存在')

    @classmethod
    async def delete_config_menu_services(
        cls, query_db: AsyncSession, page_object: DeleteConfigMenuModel
    ) -> CrudResponseModel:
        """
        删除配置菜单信息service

        :param query_db: orm对象
        :param page_object: 删除菜单对象
        :return: 删除菜单校验结果
        """
        if page_object.dvd_config_menu_ids:
            menu_id_list = page_object.dvd_config_menu_ids.split(',')
            try:
                for menu_id in menu_id_list:
                    if (await ConfigMenuDao.has_child_by_menu_id_dao(query_db, int(menu_id))) > 0:
                        raise ServiceWarning(message='存在子菜单,不允许删除')
                    await ConfigMenuDao.delete_config_menu_dao(
                        query_db, ConfigMenuModel(dvdConfigMenuId=menu_id)
                    )
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入菜单id为空')

    @classmethod
    async def config_menu_detail_services(cls, query_db: AsyncSession, menu_id: int) -> ConfigMenuModel:
        """
        获取配置菜单详细信息service

        :param query_db: orm对象
        :param menu_id: 菜单id
        :return: 菜单id对应的信息
        """
        menu = await ConfigMenuDao.get_config_menu_detail_by_id(query_db, menu_id=menu_id)
        result = ConfigMenuModel(**CamelCaseUtil.transform_result(menu)) if menu else ConfigMenuModel()

        return result

    @classmethod
    def list_to_tree(cls, menu_list: Sequence[DvdConfigMenu]) -> list[ConfigMenuTreeModel]:
        """
        工具方法：根据菜单列表信息生成树形嵌套数据

        :param menu_list: 菜单列表信息
        :return: 菜单树形嵌套数据
        """
        _menu_list = [
            ConfigMenuTreeModel(
                id=item.dvd_config_menu_id,
                label=item.dvd_config_menu_name,
                parentId=item.dvd_config_parent_id,
            )
            for item in menu_list
        ]
        # 转成id为key的字典
        mapping: dict[int, ConfigMenuTreeModel] = dict(zip([i.id for i in _menu_list], _menu_list))

        # 树容器
        container: list[ConfigMenuTreeModel] = []

        for d in _menu_list:
            # 如果找不到父级项，则是根节点
            parent = mapping.get(d.parent_id)
            if parent is None:
                container.append(d)
            else:
                children: list[ConfigMenuTreeModel] = parent.children
                if not children:
                    children = []
                children.append(d)
                parent.children = children

        return container
