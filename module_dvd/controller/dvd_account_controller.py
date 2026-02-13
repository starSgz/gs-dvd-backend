from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Path, Query, Request, Response
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_dvd.entity.vo.dvd_crawl_account_vo import (
    CrawlAccountModel,
    CrawlAccountQueryModel,
    DeleteCrawlAccountModel,
    QRCodeRequestModel,
    QRCodeStatusModel,
    SendVerifyCodeModel,
    SubmitVerifyCodeModel,
)
from module_dvd.entity.vo.dvd_user_info_vo import DvdUserInfoModel
from exceptions.exception import ServiceException
from module_dvd.dao.dvd_account_dao import CrawlAccountDao
from module_dvd.dao.access_key_dao import AccessKeyDao
from module_dvd.service.dvd_account_service import CrawlAccountService
from utils.log_util import logger
from utils.response_util import ResponseUtil

dvd_account_controller = APIRouterPro(
    prefix='/dvd/account', order_num=21, tags=['DVD配置-账号管理'], dependencies=[PreAuthDependency()]
)


@dvd_account_controller.get(
    '/list',
    summary='获取账号分页列表接口',
    description='用于获取账号分页列表',
    response_model=PageResponseModel[CrawlAccountModel],
)
async def get_account_list(
    request: Request,
    account_query: Annotated[CrawlAccountQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    获取账号分页列表
    """
    account_page_result = await CrawlAccountService.get_account_list_services(query_db, account_query)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=account_page_result)


@dvd_account_controller.get(
    '/dvd_user_info',
    summary='获取当前用户信息接口',
    description='用于获取当前登录用户的昵称、卡密和到期时间',
    response_model=DataResponseModel[DvdUserInfoModel],
)
async def get_dvd_user_info(
    request: Request,
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    获取当前用户信息（昵称、卡密、到期时间）
    """
    user = current_user.user
    nick_name = user.nick_name
    access_key = user.access_key
    expire_time = None

    # 如果用户有卡密，查询卡密信息并计算到期时间
    if access_key:
        key_info = await AccessKeyDao.get_access_key_detail_by_key(query_db, access_key)
        if key_info and key_info.used_time and key_info.duration_hours:
            expire_time = key_info.used_time + timedelta(hours=key_info.duration_hours)

    result = DvdUserInfoModel(
        nick_name=nick_name,
        access_key=access_key,
        expire_time=expire_time
    )
    logger.info(f'获取用户信息成功: {nick_name}')

    return ResponseUtil.success(data=result)


@dvd_account_controller.get(
    '/{account_id}',
    summary='获取账号详情接口',
    description='用于获取指定账号的详细信息',
    response_model=DataResponseModel[dict],
)
async def get_account_detail(
    request: Request,
    account_id: Annotated[int, Path(description='账号ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    获取账号详情
    """
    account_detail_result = await CrawlAccountService.account_detail_services(query_db, account_id)
    logger.info(f'获取account_id为{account_id}的信息成功')

    return ResponseUtil.success(data=account_detail_result)


@dvd_account_controller.post(
    '',
    summary='新增账号接口',
    description='用于新增账号',
    response_model=ResponseBaseModel,
)
@ValidateFields(validate_model='add_crawl_account')
@Log(title='DVD账号管理', business_type=BusinessType.INSERT)
async def add_account(
    request: Request,
    add_account: CrawlAccountModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    新增账号
    """
    # 设置绑定用户ID为当前登录用户
    add_account.bind_user_id = current_user.user.user_id
    # 设置默认状态为过期
    add_account.status = 2
    add_account_result = await CrawlAccountService.add_account_services(query_db, add_account)
    logger.info(add_account_result.message)

    return ResponseUtil.success(msg=add_account_result.message)


@dvd_account_controller.put(
    '',
    summary='编辑账号接口',
    description='用于编辑账号',
    response_model=ResponseBaseModel,
)
@ValidateFields(validate_model='edit_crawl_account')
@Log(title='DVD账号管理', business_type=BusinessType.UPDATE)
async def edit_account(
    request: Request,
    edit_account: CrawlAccountModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    编辑账号
    """
    # 确保bind_user_id不变
    edit_account.bind_user_id = current_user.user.user_id
    edit_account_result = await CrawlAccountService.edit_account_services(query_db, edit_account)
    logger.info(edit_account_result.message)

    return ResponseUtil.success(msg=edit_account_result.message)


@dvd_account_controller.delete(
    '/{account_ids}',
    summary='删除账号接口',
    description='用于删除账号',
    response_model=ResponseBaseModel,
)
@Log(title='DVD账号管理', business_type=BusinessType.DELETE)
async def delete_account(
    request: Request,
    account_ids: Annotated[str, Path(description='需要删除的账号ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    删除账号
    """
    delete_account_obj = DeleteCrawlAccountModel(ids=account_ids)
    delete_account_result = await CrawlAccountService.delete_account_services(query_db, delete_account_obj)
    logger.info(delete_account_result.message)

    return ResponseUtil.success(msg=delete_account_result.message)


@dvd_account_controller.post(
    '/qrcode/get',
    summary='获取登录二维码接口',
    description='用于获取登录二维码（根据平台和产品自动选择登录方式）',
    response_model=DataResponseModel[dict],
)
async def get_qrcode(
    request: Request,
    qrcode_request: QRCodeRequestModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    获取登录二维码
    """
    qrcode_result = await CrawlAccountService.get_qrcode_services(
        query_db, qrcode_request.platform_id, qrcode_request.product_id
    )
    logger.info('获取二维码成功')

    return ResponseUtil.success(data=qrcode_result)


@dvd_account_controller.post(
    '/qrcode/status',
    summary='检查二维码扫码状态接口',
    description='用于检查二维码扫码状态',
    response_model=DataResponseModel[dict],
)
async def check_qrcode_status(
    request: Request,
    status_model: QRCodeStatusModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    检查二维码扫码状态
    """
    # 根据账号ID获取平台和产品ID
    if status_model.account_id:
        account = await CrawlAccountDao.get_account_by_id(query_db, status_model.account_id)
        if not account:
            raise ServiceException(message='账号不存在')
        platform_id = account.platform_id
        product_id = account.product_id
    else:
        raise ServiceException(message='账号ID不能为空')

    status_result = await CrawlAccountService.check_qrcode_status_services(query_db, status_model, platform_id, product_id)
    logger.info('检查二维码状态成功')

    return ResponseUtil.success(data=status_result)


@dvd_account_controller.post(
    '/qrcode/send_code',
    summary='发送身份验证码接口',
    description='用于发送身份验证码（短信/邮箱）',
    response_model=DataResponseModel[dict],
)
async def send_verify_code(
    request: Request,
    send_model: SendVerifyCodeModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    发送身份验证码
    """
    # 根据账号ID获取平台和产品ID
    account = await CrawlAccountDao.get_account_by_id(query_db, send_model.account_id)
    if not account:
        raise ServiceException(message='账号不存在')
    
    platform_id = account.platform_id
    product_id = account.product_id

    send_result = await CrawlAccountService.send_verify_code_services(
        query_db, send_model.verify_ticket, send_model.cookies, platform_id, product_id
    )
    logger.info('发送验证码成功')

    return ResponseUtil.success(data=send_result)


@dvd_account_controller.post(
    '/qrcode/submit_code',
    summary='提交身份验证码接口',
    description='用于提交身份验证码并完成登录',
    response_model=DataResponseModel[dict],
)
async def submit_verify_code(
    request: Request,
    submit_model: SubmitVerifyCodeModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """
    提交身份验证码
    """
    # 根据账号ID获取平台和产品ID
    account = await CrawlAccountDao.get_account_by_id(query_db, submit_model.account_id)
    if not account:
        raise ServiceException(message='账号不存在')
    
    platform_id = account.platform_id
    product_id = account.product_id

    submit_result = await CrawlAccountService.submit_verify_code_services(
        query_db, 
        submit_model.verify_code, 
        submit_model.verify_ticket, 
        submit_model.cookies,
        submit_model.token,
        submit_model.account_id,
        platform_id, 
        product_id
    )
    logger.info('提交验证码成功')

    return ResponseUtil.success(data=submit_result)

