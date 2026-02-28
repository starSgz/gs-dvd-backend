"""
青果代理IP管理器
API文档: https://share.proxy.qg.net/get
每个IP有效期约60秒，需在有效期内完成登录流程
"""
import time
import logging
import requests
from datetime import datetime, timedelta

try:
    from utils.log_util import logger
except ModuleNotFoundError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("ProxyManager")


class QGProxyManager:
    """青果代理IP管理器"""

    API_URL = "https://share.proxy.qg.net/get"

    def __init__(self, key, area="", isp=0):
        """
        :param key: 青果产品key
        :param area: 地区代码，如 "350500,330700"，空字符串不筛选
        :param isp: 运营商 0=不筛选 1=电信 2=移动 3=联通
        """
        self.key = key
        self.area = area
        self.isp = isp
        self.current_proxy = None  # "ip:port"
        self.proxy_ip = None       # 代理真实出口IP
        self.deadline = None        # datetime 过期时间
        self._proxy_area = None
        self._proxy_isp = None

    def fetch_proxy(self):
        """从青果获取一个新的代理IP"""
        params = {
            "key": self.key,
            "num": 1,
            "isp": self.isp,
            "format": "json",
            "distinct": "true",  # 去重，不会拿到正在使用的IP
        }
        if self.area:
            params["area"] = self.area

        resp = requests.get(self.API_URL, params=params, timeout=10)
        data = resp.json()

        if data.get("code") != "SUCCESS":
            error_msg = f"获取代理IP失败: code={data.get('code')}, request_id={data.get('request_id')}"
            logger.error(error_msg)
            raise Exception(error_msg)

        ip_info = data["data"][0]
        self.current_proxy = ip_info["server"]       # "ip:port" 用于连接
        self.proxy_ip = ip_info.get("proxy_ip", "")  # 真实出口IP
        self._proxy_area = ip_info.get("area", "")
        self._proxy_isp = ip_info.get("isp", "")

        # 解析过期时间
        deadline_str = ip_info.get("deadline", "")
        if deadline_str:
            self.deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
        else:
            # 如果没有返回deadline，默认60秒后过期
            self.deadline = datetime.now() + timedelta(seconds=60)

        remaining = self.remaining_seconds()
        logger.info(
            f"[代理] 获取成功: {self.current_proxy} "
            f"(出口IP: {self.proxy_ip}, 地区: {self._proxy_area}, "
            f"运营商: {self._proxy_isp}, 剩余: {remaining:.0f}秒)"
        )
        return self.current_proxy

    def get_proxies_dict(self, refresh_if_expired=True):
        """
        返回 requests 库可用的 proxies 字典
        :param refresh_if_expired: 过期时是否自动刷新
        """
        if not self.current_proxy or (refresh_if_expired and self.is_expired()):
            self.fetch_proxy()
        return {
            "http": f"http://{self.current_proxy}",
            "https": f"http://{self.current_proxy}",
        }

    def is_expired(self, buffer_seconds=5):
        """检查当前代理是否已过期（含缓冲时间）"""
        if not self.deadline:
            return True
        return datetime.now() >= self.deadline - timedelta(seconds=buffer_seconds)

    def remaining_seconds(self):
        """返回剩余有效秒数"""
        if not self.deadline:
            return 0
        return max(0, (self.deadline - datetime.now()).total_seconds())

    def apply_to_session(self, session: requests.Session, refresh_if_expired=True):
        """
        将代理设置到 requests.Session 上
        :return: 剩余秒数
        """
        proxies = self.get_proxies_dict(refresh_if_expired=refresh_if_expired)
        session.proxies.update(proxies)
        remaining = self.remaining_seconds()
        logger.info(f"[代理] 已应用到session, 剩余: {remaining:.0f}秒")
        return remaining

    def refresh_if_needed(self, session: requests.Session, min_remaining=10):
        """
        如果代理剩余时间不足，自动刷新并更新session
        :param session: requests.Session
        :param min_remaining: 最少需要的剩余秒数
        :return: 剩余秒数
        """
        remaining = self.remaining_seconds()
        if remaining < min_remaining:
            logger.info(f"[代理] 剩余{remaining:.0f}秒 < {min_remaining}秒，自动刷新...")
            self.fetch_proxy()
            self.apply_to_session(session, refresh_if_expired=False)
            remaining = self.remaining_seconds()
        return remaining

    def __str__(self):
        if self.current_proxy:
            return f"QGProxy({self.current_proxy}, 剩余{self.remaining_seconds():.0f}s)"
        return "QGProxy(未初始化)"


if __name__ == "__main__":
    # 测试代理获取
    pm = QGProxyManager(key="PNH6L17T")
    pm.fetch_proxy()
    print(f"代理: {pm.current_proxy}")
    print(f"出口IP: {pm.proxy_ip}")
    print(f"剩余: {pm.remaining_seconds():.0f}秒")
    print(f"proxies字典: {pm.get_proxies_dict(refresh_if_expired=False)}")

    # 测试代理是否可用
    proxies = pm.get_proxies_dict(refresh_if_expired=False)
    try:
        resp = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=10)
        print(f"通过代理访问的IP: {resp.json()}")
    except Exception as e:
        print(f"代理测试失败: {e}")
