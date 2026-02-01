from collections.abc import Sequence
from typing import Union

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.entity.do.dvd_crawl_account_do import DvdCrawlAccountInfo
from module_dvd.entity.vo.dvd_crawl_account_vo import CrawlAccountModel, CrawlAccountQueryModel


class CrawlAccountDao:
    """
    采集账号模块数据库操作层
    """

    @classmethod
    async def get_account_by_id(cls, db: AsyncSession, account_id: int) -> Union[DvdCrawlAccountInfo, None]:
        """
        根据账号id获取账号详细信息

        :param db: orm对象
        :param account_id: 账号id
        :return: 账号信息对象
        """
        account_info = (
            await db.execute(select(DvdCrawlAccountInfo).where(DvdCrawlAccountInfo.id == account_id))
        ).scalars().first()

        return account_info

    @classmethod
    async def get_account_by_unique_md5(cls, db: AsyncSession, unique_md5: str) -> Union[DvdCrawlAccountInfo, None]:
        """
        根据unique_md5获取账号信息

        :param db: orm对象
        :param unique_md5: 唯一标识
        :return: 账号信息对象
        """
        account_info = (
            await db.execute(select(DvdCrawlAccountInfo).where(DvdCrawlAccountInfo.unique_md5 == unique_md5))
        ).scalars().first()

        return account_info

    @classmethod
    async def get_account_list(
        cls, db: AsyncSession, query_object: CrawlAccountQueryModel, is_page: bool = False
    ) -> Sequence[DvdCrawlAccountInfo]:
        """
        根据查询参数获取账号列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否分页
        :return: 账号列表信息对象
        """
        query = select(DvdCrawlAccountInfo).where(
            DvdCrawlAccountInfo.platform_id == query_object.platform_id if query_object.platform_id else True,
            DvdCrawlAccountInfo.product_id == query_object.product_id if query_object.product_id else True,
            DvdCrawlAccountInfo.account.like(f'%{query_object.account}%') if query_object.account else True,
            DvdCrawlAccountInfo.status == query_object.status if query_object.status else True,
        ).order_by(DvdCrawlAccountInfo.create_time.desc())

        if is_page:
            offset = (query_object.page_num - 1) * query_object.page_size
            query = query.offset(offset).limit(query_object.page_size)

        account_list = (await db.execute(query)).scalars().all()

        return account_list

    @classmethod
    async def get_account_count(cls, db: AsyncSession, query_object: CrawlAccountQueryModel) -> int:
        """
        根据查询参数获取账号总数

        :param db: orm对象
        :param query_object: 查询参数对象
        :return: 账号总数
        """
        count = (
            await db.execute(
                select(func.count('*'))
                .select_from(DvdCrawlAccountInfo)
                .where(
                    DvdCrawlAccountInfo.platform_id == query_object.platform_id if query_object.platform_id else True,
                    DvdCrawlAccountInfo.product_id == query_object.product_id if query_object.product_id else True,
                    DvdCrawlAccountInfo.account.like(f'%{query_object.account}%') if query_object.account else True,
                    DvdCrawlAccountInfo.status == query_object.status if query_object.status else True,
                )
            )
        ).scalar()

        return count

    @classmethod
    async def add_account_dao(cls, db: AsyncSession, account: CrawlAccountModel) -> DvdCrawlAccountInfo:
        """
        新增账号数据库操作

        :param db: orm对象
        :param account: 账号对象
        :return: 新增的账号对象
        """
        db_account = DvdCrawlAccountInfo(**account.model_dump(exclude_unset=True))
        db.add(db_account)
        await db.flush()

        return db_account

    @classmethod
    async def edit_account_dao(cls, db: AsyncSession, account: dict) -> None:
        """
        编辑账号数据库操作

        :param db: orm对象
        :param account: 需要更新的账号字典
        :return:
        """
        await db.execute(update(DvdCrawlAccountInfo), [account])

    @classmethod
    async def delete_account_dao(cls, db: AsyncSession, account_ids: list[int]) -> None:
        """
        删除账号数据库操作

        :param db: orm对象
        :param account_ids: 账号ID列表
        :return:
        """
        await db.execute(delete(DvdCrawlAccountInfo).where(DvdCrawlAccountInfo.id.in_(account_ids)))
