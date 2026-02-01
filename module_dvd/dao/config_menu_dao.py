from collections.abc import Sequence
from typing import Union

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.entity.do.config_menu_do import DvdConfigMenu
from module_dvd.entity.vo.config_menu_vo import ConfigMenuModel, ConfigMenuQueryModel


class ConfigMenuDao:
    """
    DVD配置菜单模块数据库操作层
    """

    @classmethod
    async def get_config_menu_detail_by_id(cls, db: AsyncSession, menu_id: int) -> Union[DvdConfigMenu, None]:
        """
        根据菜单id获取菜单详细信息

        :param db: orm对象
        :param menu_id: 菜单id
        :return: 菜单信息对象
        """
        menu_info = (
            await db.execute(select(DvdConfigMenu).where(DvdConfigMenu.dvd_config_menu_id == menu_id))
        ).scalars().first()

        return menu_info

    @classmethod
    async def get_config_menu_detail_by_info(
        cls, db: AsyncSession, menu: ConfigMenuModel
    ) -> Union[DvdConfigMenu, None]:
        """
        根据菜单参数获取菜单信息

        :param db: orm对象
        :param menu: 菜单参数对象
        :return: 菜单信息对象
        """
        menu_info = (
            (
                await db.execute(
                    select(DvdConfigMenu).where(
                        DvdConfigMenu.dvd_config_parent_id == menu.dvd_config_parent_id
                        if menu.dvd_config_parent_id
                        else True,
                        DvdConfigMenu.dvd_config_menu_name == menu.dvd_config_menu_name
                        if menu.dvd_config_menu_name
                        else True,
                        DvdConfigMenu.dvd_config_menu_type == menu.dvd_config_menu_type
                        if menu.dvd_config_menu_type
                        else True,
                    )
                )
            )
            .scalars()
            .first()
        )

        return menu_info

    @classmethod
    async def get_config_menu_list(
        cls, db: AsyncSession, page_object: ConfigMenuQueryModel
    ) -> Sequence[DvdConfigMenu]:
        """
        根据查询参数获取菜单列表信息

        :param db: orm对象
        :param page_object: 查询参数对象
        :return: 菜单列表信息对象
        """
        menu_query_all = (
            (
                await db.execute(
                    select(DvdConfigMenu)
                    .where(
                        DvdConfigMenu.status == page_object.status if page_object.status else True,
                        DvdConfigMenu.dvd_config_menu_name.like(f'%{page_object.dvd_config_menu_name}%')
                        if page_object.dvd_config_menu_name
                        else True,
                    )
                    .order_by(DvdConfigMenu.order_num)
                    .distinct()
                )
            )
            .scalars()
            .all()
        )

        return menu_query_all

    @classmethod
    async def add_config_menu_dao(cls, db: AsyncSession, menu: ConfigMenuModel) -> DvdConfigMenu:
        """
        新增菜单数据库操作

        :param db: orm对象
        :param menu: 菜单对象
        :return: 新增的菜单对象
        """
        db_menu = DvdConfigMenu(**menu.model_dump())
        db.add(db_menu)
        await db.flush()

        return db_menu

    @classmethod
    async def edit_config_menu_dao(cls, db: AsyncSession, menu: dict) -> None:
        """
        编辑菜单数据库操作

        :param db: orm对象
        :param menu: 需要更新的菜单字典
        :return:
        """
        await db.execute(update(DvdConfigMenu), [menu])

    @classmethod
    async def delete_config_menu_dao(cls, db: AsyncSession, menu: ConfigMenuModel) -> None:
        """
        删除菜单数据库操作

        :param db: orm对象
        :param menu: 菜单对象
        :return:
        """
        await db.execute(
            delete(DvdConfigMenu).where(DvdConfigMenu.dvd_config_menu_id.in_([menu.dvd_config_menu_id]))
        )

    @classmethod
    async def has_child_by_menu_id_dao(cls, db: AsyncSession, menu_id: int) -> Union[int, None]:
        """
        根据菜单id查询菜单关联子菜单的数量

        :param db: orm对象
        :param menu_id: 菜单id
        :return: 菜单关联子菜单的数量
        """
        menu_count = (
            await db.execute(
                select(func.count('*'))
                .select_from(DvdConfigMenu)
                .where(DvdConfigMenu.dvd_config_parent_id == menu_id)
            )
        ).scalar()

        return menu_count
