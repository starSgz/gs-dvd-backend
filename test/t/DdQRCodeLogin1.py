import time
import logging
import requests
import uuid
import os

try:
    from tools.qrcode.QRCodeLogin import QRCodeLogin
except ModuleNotFoundError:
    from QRCodeLogin import QRCodeLogin

try:
    from utils.log_util import logger
except ModuleNotFoundError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("DdLogin")


class DdQRCodeLogin(QRCodeLogin):
    """
    抖店二维码登录（纯净版：已移除代理功能）
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

    def _save_qrcode(self, qr_url):
        from qrcode.main import QRCode
        qr = QRCode(version=5, box_size=10, border=4)
        qr.add_data(qr_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black")
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qrcode.png")
        qr_img.save(save_path)
        logger.info(f"[二维码] 已保存到: {save_path}")
        logger.info(f"[二维码] 请在Windows资源管理器中打开此图片扫码")

    def get_qrcode(self):
        url = "https://doudian-sso.jinritemai.com/get_qrcode/"
        response = requests.post(url, headers=self.headers)
        assert response.status_code == 200, f"请求异常,{response.status_code}"
        res = response.json()
        qr_url = res.get("data", {}).get("qrcode_index_url")
        return qr_url, res.get("data", {}).get("token"), self.bash64_qrcode(qr_url)

    def listen_qrcode(self, token, blocking=True, verify_ticket=None):
        try:
            session = requests.Session()
            session.headers.update(self.headers)
            session.headers.pop('Accept-Encoding', None)

            check_url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
            data_template = {
                "aid": "4272",
                "language": "zh",
                "account_sdk_source": "web",
                "service": "https://fxg.jinritemai.com/login/common",
                "token": token,
                "redirect_sso_to_login": "false"
            }

            while True:
                current_data = data_template.copy()
                if verify_ticket:
                    current_data["verify_ticket"] = verify_ticket

                response = session.post(check_url, data=current_data)
                assert response.status_code == 200, f"请求异常，{response.status_code}"
                response_data = response.json()

                if "请完成身份验证" in response.text or response_data.get('data', {}).get('verify_ticket'):
                    all_cookies = session.cookies.get_dict()
                    verify_info = {
                        'verify_ticket': response_data.get('data', {}).get('verify_ticket', ''),
                        'verify_ways': response_data.get('data', {}).get('verify_ways', []),
                        'verify_scene_desc': response_data.get('data', {}).get('verify_scene_desc',
                                                                               '为保证账号安全，请完成身份验证'),
                    }
                    logger.info(f"需要身份验证: {verify_info}")
                    return token, all_cookies, verify_info

                elif response_data['data']['status'] == "3":
                    redirect_url = response_data['data']['redirect_url']
                    logger.info(f"扫码成功，处理重定向...")
                    session.get(url=redirect_url, allow_redirects=True)
                    all_cookies = session.cookies.get_dict()
                    return token, all_cookies, None

                if not blocking:
                    return None
                time.sleep(0.5)

        except Exception as e:
            logger.error(f"listen_qrcode 发生异常: {str(e)}")
            return None

    @classmethod
    def xor(cls, s):
        chars = '0123456789abcdef'
        arr = [i ^ 5 for i in s.encode()]
        result = ''
        for b in arr:
            result += chars[(b & 255) >> 4]
            result += chars[(b & 255) & 15]
        return result

    def full_login(self) -> dict:
        """
        完整登录流程（无代理版）：展示二维码 → 扫码 → 短信验证（如有）→ 返回 cookies
        """
        session = requests.Session()
        session.headers.update(self.headers)
        session.headers.pop('Accept-Encoding', None)

        # Step 0: 获取 ttwid
        try:
            session.post(
                "https://ttwid.bytedance.com/ttwid/union/register/",
                json={"region": "cn", "aid": 4272, "needFid": False, "service": "https://fxg.jinritemai.com",
                      "union": True},
                timeout=10,
            )
        except:
            pass

        # Step 1: 获取二维码
        qr_resp = session.post(
            "https://doudian-sso.jinritemai.com/get_qrcode/",
            data={"aid": "4272", "language": "zh", "account_sdk_source": "web",
                  "service": "https://fxg.jinritemai.com/login/common"}
        )
        qr_res = qr_resp.json()
        token = qr_res["data"]["token"]
        qr_url = qr_res["data"]["qrcode_index_url"]
        web_did = qr_res["data"].get("web_did") or qr_res["data"].get("ewid") or uuid.uuid4().hex

        logger.info(f"二维码已生成，请扫码。token: {token}")
        self._save_qrcode(qr_url)
        try:
            self.show_qrcode(qr_url)
        except:
            pass

        # Step 2: 轮询扫码状态
        check_url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
        while True:
            time.sleep(0.5)
            poll_data = {
                "aid": "4272", "language": "zh", "account_sdk_source": "web",
                "service": "https://fxg.jinritemai.com/login/common",
                "token": token, "ewid": web_did, "web_did": web_did,
                "redirect_sso_to_login": "false",
            }
            resp = session.post(check_url, data=poll_data)
            resp_data = resp.json()

            if "请完成身份验证" in resp.text or resp_data.get('data', {}).get('verify_ticket'):
                verify_ticket = resp_data.get('data', {}).get('verify_ticket') or resp_data.get('verify_ticket', '')
                return self._do_sms_verify(session, token, verify_ticket, web_did)

            status = resp_data.get('data', {}).get('status')
            if status == "3":
                redirect_url = resp_data['data']['redirect_url']
                session.get(redirect_url, allow_redirects=True)
                return session.cookies.get_dict()

    def _do_sms_verify(self, session, token, verify_ticket, web_did) -> dict:
        _code_file = "dd_code.txt"
        check_url = "https://doudian-sso.jinritemai.com/check_qrconnect/"

        # 提取并设置 CSRF
        csrf_token = session.cookies.get("passport_csrf_token", "")
        session.headers["x-tt-passport-csrf-token"] = csrf_token

        # 发送验证码
        sms_resp = session.post(
            "https://doudian-sso.jinritemai.com/passport/web/send_code/",
            data={"aid": "4272", "language": "zh", "account_sdk_source": "web", "mix_mode": "1", "type": "3737",
                  "verify_ticket": verify_ticket}
        )
        logger.info(f"短信验证码已发送，请在 {_code_file} 中写入验证码")

        # 等待文件输入验证码
        # code = None
        # for _ in range(300):
        #     if os.path.exists(_code_file):
        #         with open(_code_file, 'r') as f:
        #             code = f.read().strip()
        #         os.remove(_code_file)
        #         break
        #     time.sleep(1)
        code = input("请输入验证码：")
        if not code:
            raise TimeoutError("验证码输入超时")

        # 提交验证码
        check_resp = session.post(
            "https://doudian-sso.jinritemai.com/passport/web/mobile/check_code/",
            data={"aid": "4272", "language": "zh", "account_sdk_source": "web", "mix_mode": "1", "type": "3737",
                  "code": self.xor(code), "verify_ticket": verify_ticket}
        )
        logger.info(f"最终cookies：{session.cookies.get_dict()}")

        new_ticket = check_resp.json().get("data", {}).get("ticket")

        # 最终确认
        final_resp = session.post(
            check_url,
            data={
                "aid": "4272", "token": token, "ewid": web_did, "web_did": web_did,
                "service": "https://fxg.jinritemai.com/login/common", "verify_ticket": new_ticket
            }
        )
        final_data = final_resp.json()
        if final_data.get('data', {}).get('status') == "3":
            session.get(final_data['data']['redirect_url'], allow_redirects=True)
            logger.info(f"最终cookies：{session.cookies.get_dict()}")
            return session.cookies.get_dict()

        return {}

    # 其余 get_store_list, get_store_cookies 等业务函数保持不变...