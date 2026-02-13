import hashlib
import json
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_dvd.dao.dvd_account_dao import CrawlAccountDao
from module_dvd.dao.dvd_account_store_dao import AccountStoreDao
from module_dvd.entity.vo.dvd_crawl_account_vo import (
    CrawlAccountModel,
    CrawlAccountQueryModel,
    DeleteCrawlAccountModel,
    QRCodeResponseModel,
    QRCodeStatusModel,
)
from tools.qrcode.qrcode_login_factory import QRCodeLoginFactory
from utils.common_util import CamelCaseUtil


class CrawlAccountService:
    """
    采集账号模块服务层
    """

    @classmethod
    def generate_unique_md5(
        cls, platform_id: str, product_id: str, account: str, bind_user_id: int
    ) -> str:
        """
        生成唯一MD5标识

        :param platform_id: 平台ID
        :param product_id: 产品ID
        :param account: 账号
        :param bind_user_id: 绑定用户ID
        :return: MD5字符串
        """
        unique_str = f'{platform_id}{product_id}{account}{bind_user_id}'
        md5_hash = hashlib.md5(unique_str.encode('utf-8')).hexdigest()
        return md5_hash

    @classmethod
    async def get_account_list_services(
        cls, query_db: AsyncSession, query_object: CrawlAccountQueryModel
    ) -> PageModel:
        """
        获取账号分页列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :return: 账号分页列表信息
        """
        account_list_result = await CrawlAccountDao.get_account_list(query_db, query_object, is_page=True)
        account_count = await CrawlAccountDao.get_account_count(query_db, query_object)

        account_list = [CamelCaseUtil.transform_result(account) for account in account_list_result]

        # 批量查询店铺信息
        if account_list:
            account_ids = [account['id'] for account in account_list]
            stores_dict = await AccountStoreDao.get_stores_by_account_ids(query_db, account_ids)

            # 将店铺信息附加到每个账号
            for account in account_list:
                account['storeNames'] = stores_dict.get(account['id'], [])

        return PageModel(
            rows=account_list,
            pageNum=query_object.page_num,
            pageSize=query_object.page_size,
            total=account_count,
            hasNext=query_object.page_num * query_object.page_size < account_count,
        )

    @classmethod
    async def account_detail_services(cls, query_db: AsyncSession, account_id: int) -> dict[str, Any]:
        """
        获取账号详细信息service

        :param query_db: orm对象
        :param account_id: 账号id
        :return: 账号详细信息
        """
        account = await CrawlAccountDao.get_account_by_id(query_db, account_id)
        if not account:
            raise ServiceException(message='账号不存在')

        account_dict = CamelCaseUtil.transform_result(account)

        # 获取关联的店铺列表
        stores = await AccountStoreDao.get_stores_by_account_id(query_db, account_id)
        account_dict['storeNames'] = [store.store_name for store in stores]

        return account_dict

    @classmethod
    async def check_unique_md5_services(
        cls, query_db: AsyncSession, account: CrawlAccountModel
    ) -> bool:
        """
        校验unique_md5是否唯一service

        :param query_db: orm对象
        :param account: 账号对象
        :return: 校验结果
        """
        unique_md5 = cls.generate_unique_md5(
            account.platform_id, account.product_id, account.account, account.bind_user_id
        )

        existing_account = await CrawlAccountDao.get_account_by_unique_md5(query_db, unique_md5)

        if existing_account:
            # 如果是编辑操作，检查是否为同一账号
            if account.id and existing_account.id == account.id:
                return True
            return False

        return True

    @classmethod
    async def add_account_services(
        cls, query_db: AsyncSession, account: CrawlAccountModel
    ) -> CrudResponseModel:
        """
        新增账号信息service

        :param query_db: orm对象
        :param account: 新增账号对象
        :return: 新增账号校验结果
        """
        # 生成unique_md5
        account.unique_md5 = cls.generate_unique_md5(
            account.platform_id, account.product_id, account.account, account.bind_user_id
        )

        # 校验唯一性
        if not await cls.check_unique_md5_services(query_db, account):
            raise ServiceException(message=f'该账号已存在')

        try:
            account.create_time = datetime.now()
            account.update_time = datetime.now()
            await CrawlAccountDao.add_account_dao(query_db, account)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_account_services(
        cls, query_db: AsyncSession, account: CrawlAccountModel
    ) -> CrudResponseModel:
        """
        编辑账号信息service

        :param query_db: orm对象
        :param account: 编辑账号对象
        :return: 编辑账号校验结果
        """
        # 校验账号是否存在
        existing_account = await CrawlAccountDao.get_account_by_id(query_db, account.id)
        if not existing_account:
            raise ServiceException(message='账号不存在')

        # 生成unique_md5
        account.unique_md5 = cls.generate_unique_md5(
            account.platform_id, account.product_id, account.account, account.bind_user_id
        )

        # 校验唯一性
        if not await cls.check_unique_md5_services(query_db, account):
            raise ServiceException(message=f'该账号已存在')

        try:
            # 编辑时排除 status 字段，状态只能通过登录功能修改
            edit_account = account.model_dump(exclude_unset=True, exclude={'status'})
            edit_account['update_time'] = datetime.now()
            await CrawlAccountDao.edit_account_dao(query_db, edit_account)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_account_services(
        cls, query_db: AsyncSession, delete_account: DeleteCrawlAccountModel
    ) -> CrudResponseModel:
        """
        删除账号信息service

        :param query_db: orm对象
        :param delete_account: 删除账号对象
        :return: 删除账号校验结果
        """
        if delete_account.ids:
            account_id_list = [int(id_str) for id_str in delete_account.ids.split(',')]
            try:
                await CrawlAccountDao.delete_account_dao(query_db, account_id_list)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入账号ID为空')

    @classmethod
    async def get_qrcode_services(
        cls, query_db: AsyncSession, platform_id: str, product_id: str
    ) -> dict:
        """
        获取二维码service

        :param query_db: 数据库会话
        :param platform_id: 平台ID
        :param product_id: 产品ID
        :return: 二维码base64和token
        """
        try:
            # 根据平台和产品获取对应的登录实例
            login_instance = await QRCodeLoginFactory.get_login_instance_by_ids(
                platform_id=platform_id,
                product_id=product_id,
                db_session=query_db
            )

            # 获取二维码（不同平台的返回格式可能不同）
            qrcode_result = login_instance.get_qrcode()

            # 处理不同平台的返回格式
            if isinstance(qrcode_result, tuple):
                if len(qrcode_result) == 2:
                    # 某些平台返回 (qrcode_url, token)
                    qrcode_url, token = qrcode_result
                    qrcode_base64 = login_instance.bash64_qrcode(qrcode_url)
                    return {
                        'qrcodeBase64': qrcode_base64,
                        'token': token
                    }
                elif len(qrcode_result) == 3:
                    qrcode_url, token, qrcode_base64 = qrcode_result
                    return {
                        'qrcodeBase64': qrcode_base64,
                        'token': token
                    }
            else:
                raise ValueError(f"不支持的二维码返回格式: {type(qrcode_result)}")

        except Exception as e:
            raise ServiceException(message=f'获取二维码失败: {str(e)}')

    @classmethod
    async def check_qrcode_status_services(
        cls, query_db: AsyncSession, status_model: QRCodeStatusModel, platform_id: str, product_id: str
    ) -> dict[str, Any]:
        """
        检查二维码扫码状态service

        :param query_db: orm对象
        :param status_model: 状态查询模型
        :param platform_id: 平台ID
        :param product_id: 产品ID
        :return: 扫码状态和cookies
        """
        try:
            # 根据平台和产品获取对应的登录实例
            login_instance = await QRCodeLoginFactory.get_login_instance_by_ids(
                platform_id=platform_id,
                product_id=product_id,
                db_session=query_db
            )

            # 检查扫码状态（非阻塞式检查）
            result = login_instance.listen_qrcode(status_model.token, blocking=False)
            
            # 处理返回结果（可能是三元组或None）
            if result is None:
                return {
                    'status': 'waiting',
                    'message': '等待扫码',
                }
            
            # 解包返回值
            if len(result) == 3:
                token, cookies, verify_info = result
            else:
                token, cookies = result
                verify_info = None

            if verify_info and isinstance(verify_info, dict):
                # 处理短信/邮箱验证码的问题
                return {
                    'status': 'verify_code',
                    'message': '需要身份验证',
                    'verifyTicket': verify_info.get('verify_ticket'),
                    'verifyWays': verify_info.get('verify_ways', []),
                    'verifySceneDesc': verify_info.get('verify_scene_desc', ''),
                    'cookies': cookies,  # 传递cookies供后续使用
                }

            elif token and cookies:
                status = 0
                # 检测是否真的登录完毕
                login_status = login_instance.verify_login(cookies)
                if login_status:
                    status = 1

                # 获取店铺名称
                stores = login_instance.get_stores(cookies)

                # 如果提供了account_id，更新账号的cookies和店铺关联
                if status_model.account_id:
                    account = await CrawlAccountDao.get_account_by_id(query_db, status_model.account_id)
                    if account:
                        # 更新cookies和状态
                        edit_data = {
                            'id': status_model.account_id,
                            'cookies': json.dumps(cookies),
                            'status': status,  # 设置为正常状态
                            'update_time': datetime.now(),
                        }
                        await CrawlAccountDao.edit_account_dao(query_db, edit_data)

                        # 保存店铺关联：先删除旧关联，再批量插入新关联
                        if stores and isinstance(stores, list) and len(stores) > 0:
                            await AccountStoreDao.delete_stores_by_account_id(query_db, status_model.account_id)
                            await AccountStoreDao.add_store_batch(
                                query_db,
                                dvd_account_id=status_model.account_id,
                                store_names=stores,
                                platform_id=platform_id,
                                product_id=product_id,
                            )

                        await query_db.commit()

                return {
                    'status': 'success',
                    'cookies': cookies,
                    'message': '登录成功',
                }
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'检查二维码状态失败: {str(e)}')

    @classmethod
    async def send_verify_code_services(
        cls, query_db: AsyncSession, verify_ticket: str, cookies: dict, platform_id: str, product_id: str
    ) -> dict[str, Any]:
        """
        发送身份验证码service（支持短信/邮箱）

        :param query_db: orm对象
        :param verify_ticket: 验证票据
        :param cookies: 当前会话cookies
        :param platform_id: 平台ID
        :param product_id: 产品ID
        :return: 发送结果
        """
        try:
            # 根据平台和产品获取对应的登录实例
            login_instance = await QRCodeLoginFactory.get_login_instance_by_ids(
                platform_id=platform_id,
                product_id=product_id,
                db_session=query_db
            )

            # 调用发送验证码方法
            result = login_instance.get_sms_code(verify_ticket, cookies)
            
            if result:
                return {
                    'status': 'success',
                    'message': '验证码已发送',
                }
            else:
                raise ServiceException(message='发送验证码失败')

        except Exception as e:
            raise ServiceException(message=f'发送验证码失败: {str(e)}')

    @classmethod
    async def submit_verify_code_services(
        cls, query_db: AsyncSession, verify_code: str, verify_ticket: str, 
        cookies: dict, token: str, account_id: int, platform_id: str, product_id: str
    ) -> dict[str, Any]:
        """
        提交身份验证码并完成登录service

        :param query_db: orm对象
        :param verify_code: 用户输入的验证码
        :param verify_ticket: 验证票据
        :param cookies: 当前会话cookies
        :param token: 原始登录token
        :param account_id: 账号ID
        :param platform_id: 平台ID
        :param product_id: 产品ID
        :return: 登录结果
        """
        try:
            # 根据平台和产品获取对应的登录实例
            login_instance = await QRCodeLoginFactory.get_login_instance_by_ids(
                platform_id=platform_id,
                product_id=product_id,
                db_session=query_db
            )

            # 提交验证码，获取新的ticket
            new_ticket = login_instance.submit_code(verify_code, verify_ticket, cookies)
            
            if not new_ticket:
                raise ServiceException(message='验证码验证失败')

            # 使用新ticket继续登录流程
            result = login_instance.listen_qrcode(token, blocking=False, verify_ticket=new_ticket)
            
            if result is None:
                raise ServiceException(message='登录验证失败')
            
            # 解包返回值
            if len(result) == 3:
                final_token, final_cookies, verify_info = result
            else:
                final_token, final_cookies = result
                verify_info = None
            
            # 如果还需要验证，说明验证码有问题
            if verify_info:
                raise ServiceException(message='验证失败，请重试')
            
            if not final_cookies:
                raise ServiceException(message='获取登录信息失败')

            # 检测是否真的登录完毕
            status = 0
            login_status = login_instance.verify_login(final_cookies)
            if login_status:
                status = 1

            # 获取店铺名称
            stores = login_instance.get_stores(final_cookies)

            # 更新账号的cookies和店铺关联
            account = await CrawlAccountDao.get_account_by_id(query_db, account_id)
            if account:
                # 更新cookies和状态
                edit_data = {
                    'id': account_id,
                    'cookies': json.dumps(final_cookies),
                    'status': status,  # 设置状态
                    'update_time': datetime.now(),
                }
                await CrawlAccountDao.edit_account_dao(query_db, edit_data)

                # 保存店铺关联：先删除旧关联，再批量插入新关联
                if stores and isinstance(stores, list) and len(stores) > 0:
                    await AccountStoreDao.delete_stores_by_account_id(query_db, account_id)
                    await AccountStoreDao.add_store_batch(
                        query_db,
                        dvd_account_id=account_id,
                        store_names=stores,
                        platform_id=platform_id,
                        product_id=product_id,
                    )

                await query_db.commit()

            return {
                'status': 'success',
                'cookies': final_cookies,
                'message': '登录成功',
            }

        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'提交验证码失败: {str(e)}')


