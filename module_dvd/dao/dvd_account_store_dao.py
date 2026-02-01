from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_dvd.entity.do.dvd_account_store_do import DvdAccountStoreRelation


class AccountStoreDao:
    """
    账号-店铺关联模块数据库操作层
    """

    @classmethod
    async def add_store_batch(
        cls,
        db: AsyncSession,
        dvd_account_id: int,
        store_names: list[str],
        platform_id: str,
        product_id: str,
    ) -> None:
        """
        批量新增店铺关联

        :param db: orm对象
        :param dvd_account_id: 账号ID
        :param store_names: 店铺名称列表
        :param platform_id: 平台ID
        :param product_id: 产品ID
        :return:
        """
        current_time = datetime.now()
        store_relations = [
            DvdAccountStoreRelation(
                dvd_account_id=dvd_account_id,
                store_name=store_name,
                platform_id=platform_id,
                product_id=product_id,
                is_active=1,
                create_time=current_time,
                update_time=current_time,
            )
            for store_name in store_names
        ]
        db.add_all(store_relations)
        await db.flush()

    @classmethod
    async def delete_stores_by_account_id(cls, db: AsyncSession, dvd_account_id: int) -> None:
        """
        删除账号的所有店铺关联

        :param db: orm对象
        :param dvd_account_id: 账号ID
        :return:
        """
        await db.execute(
            delete(DvdAccountStoreRelation).where(DvdAccountStoreRelation.dvd_account_id == dvd_account_id)
        )

    @classmethod
    async def get_stores_by_account_id(
        cls, db: AsyncSession, dvd_account_id: int
    ) -> Sequence[DvdAccountStoreRelation]:
        """
        查询账号关联的店铺列表

        :param db: orm对象
        :param dvd_account_id: 账号ID
        :return: 店铺关联列表
        """
        query = select(DvdAccountStoreRelation).where(
            DvdAccountStoreRelation.dvd_account_id == dvd_account_id,
            DvdAccountStoreRelation.is_active == 1,
        ).order_by(DvdAccountStoreRelation.create_time.asc())

        stores = (await db.execute(query)).scalars().all()
        return stores

    @classmethod
    async def get_stores_by_account_ids(
        cls, db: AsyncSession, dvd_account_ids: list[int]
    ) -> dict[int, list[str]]:
        """
        批量查询多个账号的店铺（用于列表接口）

        :param db: orm对象
        :param dvd_account_ids: 账号ID列表
        :return: 字典，key为账号ID，value为店铺名称列表
        """
        if not dvd_account_ids:
            return {}

        query = select(DvdAccountStoreRelation).where(
            DvdAccountStoreRelation.dvd_account_id.in_(dvd_account_ids),
            DvdAccountStoreRelation.is_active == 1,
        ).order_by(DvdAccountStoreRelation.dvd_account_id, DvdAccountStoreRelation.create_time.asc())

        stores = (await db.execute(query)).scalars().all()

        # 组装结果字典
        result = {}
        for store in stores:
            if store.dvd_account_id not in result:
                result[store.dvd_account_id] = []
            result[store.dvd_account_id].append(store.store_name)

        return result
