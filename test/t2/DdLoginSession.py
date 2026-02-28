"""
抖店登录会话 - 分步API，适用于集成到Web平台

使用流程：
    session = DdLoginSession(proxy_key="xxx")  # 可选代理

    # 1. 获取二维码
    result = session.start()
    # result = {"qr_base64": "...", "qr_url": "...", "token": "..."}
    # 前端展示 qr_base64 图片

    # 2. 轮询扫码状态（前端定时调用，建议1秒一次）
    result = session.check_status()
    # result = {"status": "waiting"}          等待扫码
    # result = {"status": "scanned"}          已扫码等待确认
    # result = {"status": "expired"}          二维码过期，需重新start()
    # result = {"status": "success", "cookies": {...}}  直接成功
    # result = {"status": "need_verify", "mobile": "151****34", "verify_ways": [...]}  需要验证

    # 3. 如果 need_verify，发送短信
    result = session.send_sms()
    # result = {"success": True, "mobile": "151****34"}

    # 4. 用户输入验证码后提交
    result = session.submit_code("1234")
    # result = {"status": "success", "cookies": {...}}
    # result = {"status": "fail", "message": "验证码错误"}
"""
import time
import uuid
import logging
import requests

try:
    from tools.qrcode.QRCodeLogin import QRCodeLogin
except ModuleNotFoundError:
    try:
        from QRCodeLogin import QRCodeLogin
    except ModuleNotFoundError:
        QRCodeLogin = None


from proxy_manager import QGProxyManager


try:
    from utils.log_util import logger
except ModuleNotFoundError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("DdLoginSession")


class DdLoginSession:
    """
    抖店登录会话，分步调用，适合集成到Web平台。
    每个登录流程创建一个实例，实例内维护 session 和状态。
    """

    HEADERS = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://fxg.jinritemai.com",
        "referer": "https://fxg.jinritemai.com/",
        "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    }

    BASE_PARAMS = {"aid": "4272", "language": "zh", "account_sdk_source": "web"}

    def __init__(self, proxy_key=None, proxy_area="", proxy_isp=0):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.session.headers.pop("Accept-Encoding", None)

        self.token = None
        self.web_did = None
        self.verify_ticket = None
        self.verify_ways = None
        self.proxy_mgr = None

        # 代理
        if proxy_key and QGProxyManager:
            self.proxy_mgr = QGProxyManager(key=proxy_key, area=proxy_area, isp=proxy_isp)
            try:
                self.proxy_mgr.apply_to_session(self.session)
                logger.info(f"[代理] 已启用: {self.proxy_mgr.current_proxy}")
            except Exception as e:
                logger.error(f"[代理] 获取失败: {e}")
                self.proxy_mgr = None

    def start(self) -> dict:
        """
        开始登录：获取ttwid + 生成二维码
        返回: {"qr_base64": "...", "qr_url": "...", "token": "..."}
        """
        self.web_did = uuid.uuid4().hex

        # 获取 ttwid
        try:
            self.session.post(
                "https://ttwid.bytedance.com/ttwid/union/register/",
                json={
                    "region": "cn", "aid": 4272, "needFid": False,
                    "service": "https://fxg.jinritemai.com",
                    "union": True, "timezone_name": "Asia/Shanghai",
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
        except Exception as e:
            logger.warning(f"[ttwid] 获取失败（忽略）: {e}")

        # 获取二维码
        qr_resp = self.session.post(
            "https://doudian-sso.jinritemai.com/get_qrcode/",
            data={
                **self.BASE_PARAMS,
                "service": "https://fxg.jinritemai.com/login/common",
            },
        )
        assert qr_resp.status_code == 200, f"获取二维码失败: {qr_resp.text}"
        qr_res = qr_resp.json()
        self.token = qr_res["data"]["token"]
        qr_base64 = qr_res["data"].get("qrcode", "")
        qr_url = qr_res["data"]["qrcode_index_url"]
        self.web_did = qr_res["data"].get("web_did") or qr_res["data"].get("ewid") or self.web_did

        logger.info(f"[start] 二维码已生成, token: {self.token}")

        return {
            "qr_base64": qr_base64,  # PNG图片的base64，前端直接 <img src="data:image/png;base64,{qr_base64}">
            "qr_url": qr_url,        # 二维码内容URL，前端也可自行生成二维码
            "token": self.token,
        }

    def check_status(self) -> dict:
        """
        检查扫码状态（单次，非阻塞）
        返回:
          {"status": "waiting"}
          {"status": "scanned"}
          {"status": "expired"}
          {"status": "success", "cookies": {...}}
          {"status": "need_verify", "mobile": "...", "verify_ways": [...]}
        """
        # 代理过期时自动切直连
        self._safe_proxy_check()

        poll_data = {
            **self.BASE_PARAMS,
            "service": "https://fxg.jinritemai.com/login/common",
            "token": self.token,
            "ewid": self.web_did,
            "seraph_did": "", "web_did": self.web_did,
            "pc_did": "", "redirect_sso_to_login": "false", "fp": "",
        }

        try:
            resp = self.session.post(
                "https://doudian-sso.jinritemai.com/check_qrconnect/",
                data=poll_data,
            )
        except Exception as e:
            self._clear_proxy()
            resp = self.session.post(
                "https://doudian-sso.jinritemai.com/check_qrconnect/",
                data=poll_data,
            )

        assert resp.status_code == 200, f"轮询异常: {resp.status_code}"
        data = resp.json()
        status = data.get("data", {}).get("status")

        # 等待扫码
        if status == "1":
            return {"status": "waiting"}

        # 已扫码，等待确认
        if status == "2":
            return {"status": "scanned"}

        # 二维码过期
        if status == "5":
            return {"status": "expired"}

        # 需要短信验证
        if "请完成身份验证" in resp.text or data.get("data", {}).get("verify_ticket"):
            self.verify_ticket = (
                data.get("data", {}).get("verify_ticket") or
                data.get("verify_ticket", "")
            )
            self.verify_ways = data.get("data", {}).get("verify_ways") or data.get("verify_ways", [])

            # 设置 CSRF token
            csrf = self.session.cookies.get("passport_csrf_token", "")
            self.session.headers["x-tt-passport-csrf-token"] = csrf

            return {
                "status": "need_verify",
                "verify_ways": self.verify_ways,
                "mobile": next((w.get("mobile", "") for w in self.verify_ways if w.get("verify_way") == "mobile_sms_verify"), ""),
            }

        # 登录成功
        if status == "3":
            cookies = self._follow_redirect(data["data"]["redirect_url"])
            return {"status": "success", "cookies": cookies}

        return {"status": "unknown", "raw": data}

    def send_sms(self) -> dict:
        """
        发送短信验证码
        返回: {"success": True, "mobile": "151****34"}
        """
        assert self.verify_ticket, "请先调用 check_status 并确认 need_verify"

        self._safe_proxy_check()

        try:
            resp = self.session.post(
                "https://doudian-sso.jinritemai.com/passport/web/send_code/",
                params=self.BASE_PARAMS,
                data={
                    **self.BASE_PARAMS,
                    "mix_mode": "1", "type": "3737", "captcha_key": "",
                    "mobile": "undefined", "verify_ticket": self.verify_ticket,
                },
            )
        except Exception:
            self._clear_proxy()
            resp = self.session.post(
                "https://doudian-sso.jinritemai.com/passport/web/send_code/",
                params=self.BASE_PARAMS,
                data={
                    **self.BASE_PARAMS,
                    "mix_mode": "1", "type": "3737", "captcha_key": "",
                    "mobile": "undefined", "verify_ticket": self.verify_ticket,
                },
            )

        assert resp.status_code == 200, f"发送短信失败: {resp.text}"
        res = resp.json()
        if res.get("message") != "success":
            return {"success": False, "message": res.get("message", resp.text)}

        mobile = res.get("data", {}).get("mobile", "")
        logger.info(f"[send_sms] 短信已发送到 {mobile}")
        return {"success": True, "mobile": mobile}

    def submit_code(self, code: str) -> dict:
        """
        提交短信验证码
        :param code: 用户输入的验证码
        返回:
          {"status": "success", "cookies": {...}}
          {"status": "fail", "message": "..."}
        """
        assert self.verify_ticket, "请先调用 send_sms"

        self._safe_proxy_check()

        # 提交验证码
        try:
            check_resp = self.session.post(
                "https://doudian-sso.jinritemai.com/passport/web/mobile/check_code/",
                params=self.BASE_PARAMS,
                data={
                    **self.BASE_PARAMS,
                    "mix_mode": "1", "type": "3737",
                    "code": self._xor(code),
                    "verify_ticket": self.verify_ticket,
                },
            )
        except Exception:
            self._clear_proxy()
            check_resp = self.session.post(
                "https://doudian-sso.jinritemai.com/passport/web/mobile/check_code/",
                params=self.BASE_PARAMS,
                data={
                    **self.BASE_PARAMS,
                    "mix_mode": "1", "type": "3737",
                    "code": self._xor(code),
                    "verify_ticket": self.verify_ticket,
                },
            )

        assert check_resp.status_code == 200, f"验证码提交失败: {check_resp.text}"
        check_res = check_resp.json()

        if check_res.get("message") != "success":
            return {"status": "fail", "message": check_res.get("message", check_resp.text)}

        # 注入 msToken
        ms_token = check_resp.headers.get("X-Ms-Token") or check_resp.headers.get("x-ms-token")
        if ms_token:
            self.session.cookies.set("msToken", ms_token, domain="doudian-sso.jinritemai.com")

        new_ticket = check_res.get("data", {}).get("ticket", self.verify_ticket)
        logger.info(f"[submit_code] 验证成功, ticket: {new_ticket}")

        # 轮询 check_qrconnect 直到 status=3
        poll_ticket = new_ticket
        check_url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
        base_data = {
            **self.BASE_PARAMS,
            "service": "https://fxg.jinritemai.com/login/common",
            "token": self.token,
            "ewid": self.web_did, "seraph_did": "", "web_did": self.web_did,
            "pc_did": "", "redirect_sso_to_login": "false", "fp": "",
        }

        for poll in range(1, 40):
            time.sleep(2)
            try:
                poll_resp = self.session.post(check_url, data={**base_data, "verify_ticket": poll_ticket})
            except Exception:
                self._clear_proxy()
                poll_resp = self.session.post(check_url, data={**base_data, "verify_ticket": poll_ticket})

            poll_json = poll_resp.json()
            status = poll_json.get("data", {}).get("status")

            if status == "3":
                cookies = self._follow_redirect(poll_json["data"]["redirect_url"])
                return {"status": "success", "cookies": cookies}

            if poll_json.get("error_code") == 2046:
                next_ticket = poll_json.get("verify_ticket")
                if next_ticket and poll_json.get("is_optional_verify"):
                    poll_ticket = next_ticket
                continue

            logger.warning(f"[submit_code] 轮询意外响应: {poll_resp.text[:200]}")
            break

        return {"status": "fail", "message": "验证后轮询超时，服务器未返回登录成功"}

    # ========== 内部方法 ==========

    def _follow_redirect(self, redirect_url) -> dict:
        """跟随重定向并收集所有cookies"""
        try:
            self.session.get(redirect_url, allow_redirects=True)
        except Exception:
            self._clear_proxy()
            self.session.get(redirect_url, allow_redirects=True)

        cookies = self.session.cookies.get_dict()
        logger.info(f"登录成功，获取到 {len(cookies)} 个 cookies")
        return cookies

    def _safe_proxy_check(self):
        """代理过期时自动切直连"""
        if self.proxy_mgr and self.proxy_mgr.remaining_seconds() <= 0:
            logger.warning("[代理] 已过期，切换到直连")
            self._clear_proxy()

    def _clear_proxy(self):
        """清除代理"""
        self.session.proxies.clear()
        self.proxy_mgr = None

    @staticmethod
    def _xor(s):
        """抖店xor算法"""
        chars = "0123456789abcdef"
        arr = [i ^ 5 for i in s.encode()]
        result = ""
        for b in arr:
            result += chars[(b & 255) >> 4]
            result += chars[(b & 255) & 15]
        return result
