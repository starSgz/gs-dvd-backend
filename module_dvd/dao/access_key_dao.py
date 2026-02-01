from datetime import datetime, time
from typing import Any, Union

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_dvd.entity.do.access_key_do import DvdAccessKey
from module_dvd.entity.vo.access_key_vo import AccessKeyModel, AccessKeyPageQueryModel
from utils.page_util import PageUtil


class AccessKeyDao:
    """
    卡密管理模块数据库操作层
    """

    @classmethod
    async def get_access_key_detail_by_key(cls, db: AsyncSession, access_key: str) -> Union[DvdAccessKey, None]:
        """
        根据卡密获取详细信息

        :param db: orm对象
        :param access_key: 卡密
        :return: 卡密信息对象
        """
        access_key_info = (
            (await db.execute(select(DvdAccessKey).where(DvdAccessKey.access_key == access_key))).scalars().first()
        )

        return access_key_info

    @classmethod
    async def get_access_key_list(
        cls, db: AsyncSession, query_object: AccessKeyPageQueryModel, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        根据查询参数获取卡密列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 卡密列表信息对象
        """
        query = (
            select(DvdAccessKey)
            .where(
                DvdAccessKey.access_key.like(f'%{query_object.access_key}%') if query_object.access_key else True,
                DvdAccessKey.flag == query_object.flag if query_object.flag else True,
                DvdAccessKey.is_used == query_object.is_used if query_object.is_used else True,
                DvdAccessKey.create_time.between(
                    datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(00, 00, 00)),
                    datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)),
                )
                if query_object.begin_time and query_object.end_time
                else True,
            )
            .order_by(DvdAccessKey.create_time.desc())
            .distinct()
        )
        access_key_list: Union[PageModel, list[dict[str, Any]]] = await PageUtil.paginate(
            db, query, query_object.page_num, query_object.page_size, is_page
        )

        return access_key_list

    @classmethod
    async def add_access_key_dao(cls, db: AsyncSession, access_key_data: dict) -> DvdAccessKey:
        """
        新增卡密数据库操作

        :param db: orm对象
        :param access_key_data: 卡密数据字典
        :return: 新增的卡密对象
        """
        db_access_key = DvdAccessKey(**access_key_data)
        db.add(db_access_key)
        await db.flush()

        return db_access_key

    @classmethod
    async def edit_access_key_dao(cls, db: AsyncSession, access_key: dict) -> None:
        """
        编辑卡密数据库操作

        :param db: orm对象
        :param access_key: 需要更新的卡密字典
        :return:
        """
        await db.execute(update(DvdAccessKey), [access_key])

    @classmethod
    async def delete_access_key_dao(cls, db: AsyncSession, access_key: str) -> None:
        """
        删除卡密数据库操作

        :param db: orm对象
        :param access_key: 卡密
        :return:
        """
        await db.execute(delete(DvdAccessKey).where(DvdAccessKey.access_key == access_key))
