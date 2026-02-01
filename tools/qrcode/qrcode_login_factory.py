from enum import Enum
from typing import Optional

from tools.qrcode.DdQRCodeLogin import DdQRCodeLogin
from tools.qrcode.QRCodeLogin import QRCodeLogin
from tools.qrcode.QfQRCodeLogin import QfQRCodeLogin


class QRCodeLoginType(str, Enum):
    """
    二维码登录类型枚举
    """
    DOUDIAN = "doudian"  # 抖店
    XIAOHONGSHU = "xiaohongshu"  # 小红书
    QIANFAN = "QIANFAN"  # 小红书


class QRCodeLoginFactory:
    """
    二维码登录工厂类
    根据平台和产品名称返回对应的登录实例
    """

    # 平台名称到登录类型的映射
    PLATFORM_LOGIN_MAP = {
        "抖音": QRCodeLoginType.DOUDIAN,
        "小红书": QRCodeLoginType.XIAOHONGSHU,
    }

    # 产品名称到登录类型的映射（可选，用于更精确的匹配）
    PRODUCT_LOGIN_MAP = {
        # 可以在这里添加特定产品的映射
        "抖店": QRCodeLoginType.DOUDIAN,
        "千帆": QRCodeLoginType.QIANFAN,
    }

    @classmethod
    def get_login_instance(
        cls, platform_name: str, product_name: Optional[str] = None
    ) -> QRCodeLogin:
        """
        根据平台名称和产品名称获取对应的登录实例

        :param platform_name: 平台名称
        :param product_name: 产品名称（可选，用于更精确的匹配）
        :return: QRCodeLogin实例
        :raises ValueError: 如果找不到对应的登录类型
        """
        # 优先检查产品映射
        if product_name and product_name in cls.PRODUCT_LOGIN_MAP:
            login_type = cls.PRODUCT_LOGIN_MAP[product_name]
        # 检查平台映射
        elif platform_name in cls.PLATFORM_LOGIN_MAP:
            login_type = cls.PLATFORM_LOGIN_MAP[platform_name]
        else:
            raise ValueError(f"不支持的平台或产品: 平台={platform_name}, 产品={product_name}")

        # 根据登录类型返回对应的实例
        if login_type == QRCodeLoginType.DOUDIAN:
            return DdQRCodeLogin()
        elif login_type == QRCodeLoginType.QIANFAN:
            return QfQRCodeLogin()
        else:
            raise ValueError(f"未实现的登录类型: {login_type}")

    @classmethod
    async def get_login_instance_by_ids(
        cls, platform_id: str, product_id: str, db_session
    ) -> QRCodeLogin:
        """
        根据平台ID和产品ID获取对应的登录实例
        需要从数据库查询平台和产品的名称

        :param platform_id: 平台ID（dvd_config_menu_id）
        :param product_id: 产品ID（dvd_config_menu_id）
        :param db_session: 数据库会话
        :return: QRCodeLogin实例
        """
        from module_dvd.dao.config_menu_dao import ConfigMenuDao

        # 查询平台名称
        platform_menu = await ConfigMenuDao.get_config_menu_detail_by_id(db_session, int(platform_id))
        if not platform_menu:
            raise ValueError(f"平台ID不存在: {platform_id}")

        # 查询产品名称
        product_menu = await ConfigMenuDao.get_config_menu_detail_by_id(db_session, int(product_id))
        if not product_menu:
            raise ValueError(f"产品ID不存在: {product_id}")

        return cls.get_login_instance(
            platform_name=platform_menu.dvd_config_menu_name,
            product_name=product_menu.dvd_config_menu_name
        )
