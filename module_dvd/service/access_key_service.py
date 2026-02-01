import hashlib
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Union

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_dvd.dao.access_key_dao import AccessKeyDao
from module_dvd.entity.vo.access_key_vo import (
    AccessKeyCreateModel,
    AccessKeyModel,
    AccessKeyPageQueryModel,
    ActivateAccessKeyResponseModel,
    DeleteAccessKeyModel,
)
from module_admin.dao.user_dao import UserDao
from module_admin.entity.vo.user_vo import EditUserModel
from utils.common_util import CamelCaseUtil
from utils.log_util import logger


class AccessKeyService:
    """
    卡密管理模块服务层
    """

    @staticmethod
    def generate_access_key(salt: str = 'dvd_shop_secret_2026') -> str:
        """
        生成32位卡密

        :param salt: 加盐字符串
        :return: 32位卡密
        """
        timestamp = str(time.time())
        unique_id = str(uuid.uuid4())
        raw = f'{timestamp}{unique_id}{salt}'
        return hashlib.md5(raw.encode()).hexdigest()

    @classmethod
    async def get_access_key_list_services(
        cls, query_db: AsyncSession, query_object: AccessKeyPageQueryModel, is_page: bool = False
    ) -> Union[PageModel, list[dict[str, Any]]]:
        """
        获取卡密列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 卡密列表信息对象
        """
        access_key_list_result = await AccessKeyDao.get_access_key_list(query_db, query_object, is_page)

        return access_key_list_result

    @classmethod
    async def add_access_key_services(
        cls, query_db: AsyncSession, page_object: AccessKeyCreateModel
    ) -> CrudResponseModel:
        """
        新增卡密信息service

        :param query_db: orm对象
        :param page_object: 新增卡密对象
        :return: 新增卡密校验结果
        """
        # 生成32位卡密
        new_access_key = cls.generate_access_key()

        # 确保卡密唯一
        existing = await AccessKeyDao.get_access_key_detail_by_key(query_db, new_access_key)
        while existing:
            new_access_key = cls.generate_access_key()
            existing = await AccessKeyDao.get_access_key_detail_by_key(query_db, new_access_key)

        # 将年月日时转换为总小时数
        total_hours = page_object.to_total_hours()
        # 获取使用截止日期
        use_deadline = page_object.get_use_deadline()

        # 直接构建数据字典
        access_key_data = {
            'access_key': new_access_key,
            'bind_store_num': page_object.bind_store_num,
            'duration_hours': total_hours,
            'use_deadline': use_deadline,
            'remark': page_object.remark,
            'flag': '0',
            'is_used': '0',
            'create_time': datetime.now(),
        }

        try:
            await AccessKeyDao.add_access_key_dao(query_db, access_key_data)
            await query_db.commit()
            result = {'is_success': True, 'message': '新增成功', 'result': {'accessKey': new_access_key}}
        except Exception as e:
            await query_db.rollback()
            raise e

        return CrudResponseModel(**result)

    @classmethod
    async def edit_access_key_services(
        cls, query_db: AsyncSession, page_object: AccessKeyModel
    ) -> CrudResponseModel:
        """
        编辑卡密信息service

        :param query_db: orm对象
        :param page_object: 编辑卡密对象
        :return: 编辑卡密校验结果
        """
        edit_access_key = page_object.model_dump(exclude_unset=True)
        access_key_info = await cls.access_key_detail_services(query_db, page_object.access_key)

        if access_key_info.access_key:
            try:
                edit_access_key['update_date'] = datetime.now()
                await AccessKeyDao.edit_access_key_dao(query_db, edit_access_key)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='卡密不存在')

    @classmethod
    async def delete_access_key_services(
        cls, query_db: AsyncSession, page_object: DeleteAccessKeyModel
    ) -> CrudResponseModel:
        """
        删除卡密信息service

        :param query_db: orm对象
        :param page_object: 删除卡密对象
        :return: 删除卡密校验结果
        """
        if page_object.access_keys:
            access_key_list = page_object.access_keys.split(',')
            try:
                for access_key in access_key_list:
                    access_key_info = await cls.access_key_detail_services(query_db, access_key)
                    if access_key_info.is_used == '1':
                        raise ServiceException(message=f'卡密 {access_key} 已被使用，无法删除')
                    await AccessKeyDao.delete_access_key_dao(query_db, access_key)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入卡密为空')

    @classmethod
    async def access_key_detail_services(cls, query_db: AsyncSession, access_key: str) -> AccessKeyModel:
        """
        获取卡密详细信息service

        :param query_db: orm对象
        :param access_key: 卡密
        :return: 卡密对应的信息
        """
        access_key_obj = await AccessKeyDao.get_access_key_detail_by_key(query_db, access_key=access_key)
        result = (
            AccessKeyModel(**CamelCaseUtil.transform_result(access_key_obj)) if access_key_obj else AccessKeyModel()
        )

        return result

    @classmethod
    async def activate_access_key_services(
        cls, query_db: AsyncSession, access_key: str, user_id: int
    ) -> ActivateAccessKeyResponseModel:
        """
        激活卡密service

        :param query_db: orm对象
        :param access_key: 卡密
        :param user_id: 用户ID
        :return: 激活结果
        """
        # 获取卡密信息
        access_key_info = await cls.access_key_detail_services(query_db, access_key)

        # 校验卡密是否存在
        if not access_key_info.access_key:
            raise ServiceException(message='卡密不存在')

        # 校验卡密是否已被使用
        if access_key_info.is_used == '1':
            raise ServiceException(message='该卡密已被使用')

        # 校验卡密是否过期
        if access_key_info.flag == '1':
            raise ServiceException(message='该卡密已过期')

        # 校验使用截止日期
        if access_key_info.use_deadline and datetime.now() > access_key_info.use_deadline:
            raise ServiceException(message='该卡密已超过使用截止日期')

        # 计算到期时间
        used_time = datetime.now()
        expire_time = used_time + timedelta(hours=access_key_info.duration_hours)

        try:
            # 更新卡密状态
            update_key_data = {
                'access_key': access_key,
                'is_used': '1',
                'used_time': used_time,
                'update_date': datetime.now(),
            }
            await AccessKeyDao.edit_access_key_dao(query_db, update_key_data)

            # 更新用户的access_key
            from module_admin.service.user_service import UserService
            edit_user = EditUserModel(
                userId=user_id,
                accessKey=access_key,
                expireTime=expire_time,
                updateTime=datetime.now(),
                type='accessKey',  # 标记为卡密激活操作，避免触发角色/岗位相关逻辑
            )
            await UserService.edit_user_services(query_db, edit_user)

            await query_db.commit()

            # 构造响应对象
            logger.info(f'准备返回激活结果：卡密={access_key}, 到期时间={expire_time}')
            result = ActivateAccessKeyResponseModel(
                access_key=access_key,
                expire_time=expire_time,
                message='卡密激活成功'
            )
            logger.info(f'激活响应对象构造成功：{result}')
            return result
        except Exception as e:
            await query_db.rollback()
            raise e
