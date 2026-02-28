import time
import uuid

from curl_cffi import requests

from tools.qrcode.QRCodeLogin import QRCodeLogin
from utils.log_util import logger


class DdQRCodeLogin(QRCodeLogin):
    """
    抖店二维码登录
    使用类级别 _sessions 字典维护每个 token 对应的 session，
    保证整个登录流程（get_qrcode -> listen_qrcode -> get_sms_code -> submit_code）
    共享同一个 HTTP session，满足抖店 SSO cookie 链路检测。
    """

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://fxg.jinritemai.com",
        "priority": "u=1, i",
        "referer": "https://fxg.jinritemai.com/",
        "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    }

    # 类级别 session 存储，key = token，value = {"session": Session, "web_did": str}
    _sessions: dict = {}

    # ------------------------------------------------------------------ #
    # 辅助方法
    # ------------------------------------------------------------------ #

    def _get_session(self, token: str) -> dict:
        """通过 token 获取已存储的 session 信息，不存在则抛异常"""
        entry = self._sessions.get(token)
        if not entry:
            raise ValueError(f"未找到 token={token} 对应的 session，请先调用 get_qrcode()")
        return entry

    @classmethod
    def cleanup_session(cls, token: str) -> None:
        """登录完成或超时后清理 session，释放内存"""
        cls._sessions.pop(token, None)
        logger.info(f"[session清理] token={token[:16]}... 已清理")

    # ------------------------------------------------------------------ #
    # 获取二维码（同时初始化并保存 session）
    # ------------------------------------------------------------------ #

    def get_qrcode(self):
        """
        创建 session -> 获取 ttwid -> 获取二维码 -> 存储 session
        :return: (qrcode_url, token, base64_image)
        """
        session = requests.Session()
        session.headers.update(self.headers)
        session.headers.pop('Accept-Encoding', None)

        # Step 0: 获取 ttwid（ByteDance 设备标识 cookie）
        try:
            tw_resp = session.post(
                "https://ttwid.bytedance.com/ttwid/union/register/",
                json={
                    "region": "cn",
                    "aid": 4272,
                    "needFid": False,
                    "service": "https://fxg.jinritemai.com",
                    "union": True,
                    "timezone_name": "Asia/Shanghai",
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            logger.info(f"[ttwid] 状态码: {tw_resp.status_code}, cookies: {session.cookies.get_dict()}")
        except Exception as e:
            logger.warning(f"[ttwid] 获取失败（忽略）: {e}")

        # 生成设备ID
        web_did = uuid.uuid4().hex

        # Step 1: 获取二维码（用 session 捕获初始 cookies）
        qr_resp = session.post(
            "https://doudian-sso.jinritemai.com/get_qrcode/",
            data={
                "aid": "4272",
                "language": "zh",
                "account_sdk_source": "web",
                "service": "https://fxg.jinritemai.com/login/common",
            }
        )
        assert qr_resp.status_code == 200, f"获取二维码失败: {qr_resp.text}"
        qr_res = qr_resp.json()
        token = qr_res["data"]["token"]
        qr_url = qr_res["data"]["qrcode_index_url"]

        # 优先使用服务端返回的 web_did / ewid
        web_did = qr_res["data"].get("web_did") or qr_res["data"].get("ewid") or web_did
        logger.info(f"[get_qrcode] token={token[:16]}... web_did={web_did[:8]}...")
        logger.info(f"[get_qrcode] session cookies: {session.cookies.get_dict()}")

        # 保存 session 供后续步骤使用
        DdQRCodeLogin._sessions[token] = {
            "session": session,
            "web_did": web_did,
        }

        return qr_url, token, self.bash64_qrcode(qr_url)

    # ------------------------------------------------------------------ #
    # 监听二维码扫码状态（非阻塞单次检查）
    # ------------------------------------------------------------------ #

    def listen_qrcode(self, token: str, blocking: bool = False, verify_ticket: str = None):
        """
        检查二维码扫码状态（单次非阻塞模式供 API 轮询）。
        使用与 get_qrcode 同一个 session，保持 cookie 链路。

        :param token: 登录 token
        :param blocking: 保留参数，当前仅支持 False（非阻塞单次检查）
        :param verify_ticket: 身份验证票据（短信验证完成后带入）
        :return: (token, cookies, verify_info) 或 None（未扫码/等待中）
        """
        try:
            entry = self._get_session(token)
            session = entry["session"]
            web_did = entry["web_did"]

            url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
            data = {
                "aid": "4272",
                "language": "zh",
                "account_sdk_source": "web",
                "service": "https://fxg.jinritemai.com/login/common",
                "token": token,
                "ewid": web_did,
                "seraph_did": "",
                "web_did": web_did,
                "pc_did": "",
                "redirect_sso_to_login": "false",
                "fp": "",
            }
            if verify_ticket:
                data["verify_ticket"] = verify_ticket

            response = session.post(url, data=data)
            if response.status_code != 200:
                logger.warning(f"[listen_qrcode] 请求异常: {response.status_code}")
                return None

            response_data = response.json()

            # 需要短信/邮箱身份验证
            if "请完成身份验证" in response.text or response_data.get('data', {}).get('verify_ticket'):
                all_cookies = session.cookies.get_dict()
                verify_info = {
                    'verify_ticket': (
                        response_data.get('data', {}).get('verify_ticket') or
                        response_data.get('verify_ticket', '')
                    ),
                    'verify_ways': response_data.get('data', {}).get('verify_ways', []),
                    'verify_scene_desc': response_data.get('data', {}).get('verify_scene_desc', '为保证账号安全，请完成身份验证'),
                }
                logger.info(f"[listen_qrcode] 需要身份验证: {verify_info}")
                return token, all_cookies, verify_info

            # 扫码成功，处理重定向
            status = response_data.get('data', {}).get('status')
            if status == "3":
                redirect_url = response_data['data']['redirect_url']
                logger.info(f"[listen_qrcode] 扫码成功，处理重定向: {redirect_url}")
                session.get(url=redirect_url, allow_redirects=True)
                all_cookies = session.cookies.get_dict()
                logger.info(f"[listen_qrcode] 完整 cookies 数量: {len(all_cookies)}")
                return token, all_cookies, None

            # 其余状态（等待扫码）
            return None

        except Exception as e:
            logger.error(f"[listen_qrcode] 发生异常: {str(e)}")
            return None

    # ------------------------------------------------------------------ #
    # 发送短信验证码
    # ------------------------------------------------------------------ #

    def get_sms_code(self, verify_ticket: str, token: str) -> bool:
        """
        通过已存储的 session 发送短信验证码，自动携带 csrf_token。

        :param verify_ticket: 验证票据
        :param token: 登录 token，用于检索 session
        :return: True 表示发送成功
        """
        entry = self._get_session(token)
        session = entry["session"]

        # 从 session cookies 中提取 csrf_token 并设置 header
        csrf_token = session.cookies.get("passport_csrf_token", "")
        session.headers["x-tt-passport-csrf-token"] = csrf_token
        logger.info(f"[get_sms_code] csrf_token: {csrf_token}")
        logger.info(f"[get_sms_code] 当前 session cookies: {session.cookies.get_dict()}")

        url = "https://doudian-sso.jinritemai.com/passport/web/send_code/"
        params = {"aid": "4272", "language": "zh", "account_sdk_source": "web"}
        data = {
            "aid": "4272",
            "language": "zh",
            "account_sdk_source": "web",
            "mix_mode": "1",
            "type": "3737",
            "captcha_key": "",
            "mobile": "undefined",
            "verify_ticket": verify_ticket,
        }

        resp = session.post(url, params=params, data=data)
        assert resp.status_code == 200, f"发送短信失败: {resp.text}"
        res = resp.json()
        assert res.get("message") == "success", f"发送短信接口返回异常: {resp.text}"
        logger.info(f"[get_sms_code] 短信验证码已发送，Set-Cookie: {dict(resp.cookies)}")
        logger.info(f"[get_sms_code] 发送后 session cookies: {session.cookies.get_dict()}")
        return True

    # ------------------------------------------------------------------ #
    # 提交验证码 + 完成登录轮询
    # ------------------------------------------------------------------ #

    def submit_code(self, code: str, verify_ticket: str, token: str) -> dict:
        """
        提交短信验证码，然后轮询 check_qrconnect 完成登录，返回最终 cookies。
        全程使用同一个 session，保持 cookie 链路。

        :param code: 用户输入的短信验证码
        :param verify_ticket: 验证票据
        :param token: 登录 token，用于检索 session
        :return: 最终登录 cookies dict
        """
        entry = self._get_session(token)
        session = entry["session"]
        web_did = entry["web_did"]

        # Step C: 提交验证码（xor 加密）
        check_url = "https://doudian-sso.jinritemai.com/passport/web/mobile/check_code/"
        params = {"aid": "4272", "language": "zh", "account_sdk_source": "web"}
        data = {
            "aid": "4272",
            "language": "zh",
            "account_sdk_source": "web",
            "mix_mode": "1",
            "type": "3737",
            "code": self.xor(str(code)),
            "verify_ticket": verify_ticket,
        }

        logger.info(f"[submit_code] 提交验证码前 session cookies: {session.cookies.get_dict()}")
        check_resp = session.post(check_url, params=params, data=data)
        assert check_resp.status_code == 200, f"验证码提交失败: {check_resp.text}"
        check_res = check_resp.json()
        assert check_res.get("message") == "success", f"验证码校验失败: {check_resp.text}"

        # 注入 msToken（如有）
        ms_token = check_resp.headers.get("X-Ms-Token") or check_resp.headers.get("x-ms-token")
        if ms_token:
            logger.info(f"[submit_code] 注入 msToken: {ms_token[:20]}...")
            session.cookies.set("msToken", ms_token, domain="doudian-sso.jinritemai.com")

        logger.info(f"[submit_code] 验证码提交成功，session cookies: {session.cookies.get_dict()}")

        # check_code 返回的新 ticket（用于后续轮询）
        new_ticket = check_res.get("data", {}).get("ticket") or verify_ticket
        logger.info(f"[submit_code] new_ticket: {new_ticket}")

        # Step D: 轮询 check_qrconnect，带 verify_ticket，最多等待 80 秒
        poll_url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
        base_data = {
            "aid": "4272",
            "language": "zh",
            "account_sdk_source": "web",
            "service": "https://fxg.jinritemai.com/login/common",
            "token": token,
            "ewid": web_did,
            "seraph_did": "",
            "web_did": web_did,
            "pc_did": "",
            "redirect_sso_to_login": "false",
            "fp": "",
        }

        for poll in range(1, 10):
            time.sleep(2)
            poll_resp = session.post(poll_url, data={**base_data, "verify_ticket": new_ticket})
            assert poll_resp.status_code == 200, f"轮询请求异常: {poll_resp.status_code}"

            poll_json = poll_resp.json()
            if dict(poll_resp.cookies):
                logger.info(f"[轮询第{poll}次] 新 Set-Cookie: {dict(poll_resp.cookies)}")
            logger.info(f"[轮询第{poll}次] {poll_resp.text[:200]}")

            status = poll_json.get('data', {}).get('status')
            if status == "3":
                redirect_url = poll_json['data']['redirect_url']
                logger.info(f"[轮询第{poll}次] 扫码成功，处理重定向: {redirect_url}")
                session.get(url=redirect_url, allow_redirects=True)
                all_cookies = session.cookies.get_dict()
                logger.info(f"[submit_code] 登录成功，获取到 {len(all_cookies)} 个 cookies")
                return all_cookies

        raise ValueError("提交验证码后轮询超时（40次 x 2秒），未能完成登录")

    # ------------------------------------------------------------------ #
    # 校验登录状态
    # ------------------------------------------------------------------ #

    def verify_login(self, cookies: dict) -> bool:
        """
        校验 cookies 是否有效（能访问抖店后台）
        :param cookies: 登录 cookies dict
        :return: True 表示有效
        """
        url = "https://fxg.jinritemai.com/ecomauth/loginv1/get_login_subject"
        params = {
            'bus_type': "1",
            'login_source': "doudian_pc_web",
            'entry_source': "0",
            'bus_child_type': "0",
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'accept-language': "zh-CN,zh;q=0.9",
        }
        response = requests.get(url=url, params=params, headers=headers, cookies=cookies)
        assert response.status_code == 200, f"请求异常,{response.status_code}"
        res = response.json()
        assert res.get("msg") == "success", f"请求异常,{response.text}"
        return True

    # ------------------------------------------------------------------ #
    # 获取店铺列表
    # ------------------------------------------------------------------ #

    def get_stores(self, cookies: dict) -> list:
        """
        获取账号关联的所有店铺名称列表
        :param cookies: 登录 cookies dict
        :return: 店铺名称列表
        """
        url = "https://fxg.jinritemai.com/ecomauth/loginv1/get_login_subject"
        params = {
            'bus_type': "1",
            'login_source': "doudian_pc_web",
            'entry_source': "0",
            'bus_child_type': "0",
        }
        response = requests.get(url, params=params, headers=self.headers, cookies=cookies)
        assert response.status_code == 200, f"请求异常，{response.status_code}"
        res = response.json()
        assert res.get("msg") == "success", f"请求错误，{response.text}"
        assert res.get("data"), f"账号获取店铺错误"
        return [data.get("account_name") for data in res.get("data", {}).get("login_subject_list", [])]

    def get_store_list(self, cookies: dict) -> list:
        """
        获取店铺详情列表（含 encode_shop_id 等字段）
        :param cookies: 登录 cookies dict
        :return: 店铺详情列表
        """
        url = "https://fxg.jinritemai.com/ecomauth/loginv1/get_login_subject"
        params = {
            'bus_type': "1",
            'login_source': "doudian_pc_web",
            'entry_source': "0",
            'bus_child_type': "0",
        }
        response = requests.get(url, params=params, headers=self.headers, cookies=cookies)
        assert response.status_code == 200, f"请求异常，{response.status_code}"
        res = response.json()
        assert res.get("msg") == "success", f"请求错误，{response.text}"
        assert res.get("data"), f"账号获取店铺错误"
        store_data = []
        for data in res.get("data", {}).get("login_subject_list", []):
            store_data.append({
                "account_id": data.get("account_id"),
                "account_name": data.get("account_name"),
                "member_id": data.get("member_id"),
                "encode_shop_id": data.get("encode_shop_id"),
                "encode_member_id": data.get("encode_member_id"),
            })
        return store_data

    def get_store_cookies(self, store_info: dict, cookies: dict) -> dict:
        """
        通过账号 cookies 获取指定店铺的 cookies
        :param store_info: 店铺信息 dict（含 encode_shop_id / member_id / encode_member_id）
        :param cookies: 账号级 cookies
        :return: 更新后的店铺 cookies
        """
        url = "https://fxg.jinritemai.com/ecomauth/loginv1/callback"
        params = {
            'login_source': "doudian_pc_web",
            'subject_aid': "4966",
            'encode_shop_id': store_info.get("encode_shop_id"),
            'member_id': store_info.get("member_id"),
            'bus_child_type': "0",
            'entry_source': "0",
            'ecom_login_extra': "",
            'use_cache': "false",
            'encode_member_id': store_info.get("encode_member_id"),
            'action_type': "1",
        }
        response = requests.get(url, params=params, headers=self.headers, cookies=cookies)
        assert response.status_code == 200, f"请求异常，{response.status_code}"
        cookies.update(dict(response.cookies))

        dt_params = {
            "login_source": "compass",
            "subject_aid": "4966",
            "bus_child_type": "0",
            "entry_source": "0",
            "ecom_login_extra": "",
            "encode_member_id": store_info.get("encode_member_id"),
            "action_type": "6",
        }
        dt_response = requests.get(url, headers=self.headers, cookies=cookies, params=dt_params)
        assert dt_response.status_code == 200, f"请求异常，{dt_response.status_code}"
        cookies.update(dict(dt_response.cookies))
        return cookies

    # ------------------------------------------------------------------ #
    # 工具方法
    # ------------------------------------------------------------------ #

    @classmethod
    def xor(cls, s: str) -> str:
        """抖店 xor 算法，用于加密验证码"""
        chars = '0123456789abcdef'
        arr = [i ^ 5 for i in s.encode()]
        result = ''
        for b in arr:
            result += chars[(b & 255) >> 4]
            result += chars[(b & 255) & 15]
        return result
