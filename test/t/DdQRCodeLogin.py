import time
import logging

import requests

try:
    from tools.qrcode.QRCodeLogin import QRCodeLogin
except ModuleNotFoundError:
    from QRCodeLogin import QRCodeLogin

try:
    from tools.qrcode.proxy_manager import QGProxyManager
except ModuleNotFoundError:
    try:
        from proxy_manager import QGProxyManager
    except ModuleNotFoundError:
        QGProxyManager = None

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
    抖店二维码登录
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
        """将二维码保存到脚本同目录下的 qrcode.png，方便在Windows资源管理器中打开"""
        import os
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
        """
        返回url\ token \base64
        """
        url = "https://doudian-sso.jinritemai.com/get_qrcode/"
        response = requests.post(url, headers=self.headers)
        assert response.status_code == 200, f"请求异常,{response.status_code}"
        res = response.json()
        qr_url = res.get("data", {}).get("qrcode_index_url")
        return qr_url, res.get("data", {}).get("token"),self.bash64_qrcode(qr_url)

    def listen_qrcode(self, token, blocking=True,verify_ticket=None):
        """
        监听二维码扫码状态
        :param token: 登录token
        :param blocking: 是否阻塞等待，True为阻塞模式（持续轮询），False为单次检查
        :return: (token, cookies) 或 None
        """
        try:
            # 创建 session 对象，自动管理整个请求链的 cookies
            session = requests.Session()
            session.headers.update(self.headers)
            # 删除 Accept-Encoding 避免编码问题
            session.headers.pop('Accept-Encoding', None)
            
            if blocking:
                # 阻塞模式：持续轮询直到扫码成功
                while True:
                    url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
                    data = {
                        "aid": "4272",
                        "language": "zh",
                        "account_sdk_source": "web",
                        "service": "https://fxg.jinritemai.com/login/common",
                        "token": token,
                        "redirect_sso_to_login": "false"
                    }
                    if verify_ticket:
                        data["verify_ticket"] = verify_ticket
                    response = session.post(url, data=data)
                    assert response.status_code == 200, f"请求异常，{response.status_code}"
                    
                    response_data = response.json()

                    if "请完成身份验证" in response.text or response_data.get('data', {}).get('verify_ticket'):
                        # 需要身份验证（短信/邮箱验证码）
                        all_cookies = session.cookies.get_dict()
                        verify_info = {
                            'verify_ticket': response_data.get('data', {}).get('verify_ticket', ''),
                            'verify_ways': response_data.get('data', {}).get('verify_ways', []),
                            'verify_scene_desc': response_data.get('data', {}).get('verify_scene_desc', '为保证账号安全，请完成身份验证'),
                        }
                        logger.info(f"需要身份验证: {verify_info}")
                        return token, all_cookies, verify_info

                    elif response_data['data']['status'] == "3":
                        redirect_url = response_data['data']['redirect_url']
                        logger.info(f"扫码成功，开始处理重定向: {redirect_url}")

                        # 使用 session 访问重定向URL，自动跟随所有重定向并收集 cookies
                        # allow_redirects=True 会自动跟随重定向链，收集所有过程中的 cookies
                        session.get(url=redirect_url, allow_redirects=True)

                        # 从 session 中获取完整的 cookies
                        all_cookies = session.cookies.get_dict()
                        logger.info(f"完整cookies数量: {len(all_cookies)}")
                        logger.info(f"完整cookies内容: {all_cookies}")

                        return token, all_cookies, None
                    time.sleep(0.5)

            else:
                # 非阻塞模式：单次检查
                url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
                data = {
                    "aid": "4272",
                    "language": "zh",
                    "account_sdk_source": "web",
                    "service": "https://fxg.jinritemai.com/login/common",
                    "token": token,
                    "redirect_sso_to_login": "false"
                }
                if verify_ticket:
                    data["verify_ticket"] = verify_ticket
                response = session.post(url, data=data)
                
                if response.status_code == 200:
                    response_data = response.json()

                    if "请完成身份验证" in response.text or response_data.get('data', {}).get('verify_ticket'):
                        # 需要身份验证（短信/邮箱验证码）
                        all_cookies = session.cookies.get_dict()
                        verify_info = {
                            'verify_ticket': response_data.get('data', {}).get('verify_ticket', ''),
                            'verify_ways': response_data.get('data', {}).get('verify_ways', []),
                            'verify_scene_desc': response_data.get('data', {}).get('verify_scene_desc', '为保证账号安全，请完成身份验证'),
                        }
                        logger.info(f"需要身份验证: {verify_info}")
                        return token, all_cookies, verify_info

                    elif response_data.get('data', {}).get('status') == "3":
                        redirect_url = response_data['data']['redirect_url']

                        # 使用 session 访问重定向URL，自动跟随所有重定向并收集 cookies
                        session.get(url=redirect_url, allow_redirects=True)

                        # 从 session 中获取完整的 cookies
                        all_cookies = session.cookies.get_dict()
                        logger.info(f"完整cookies数量: {len(all_cookies)}")
                        logger.info(f"完整cookies内容: {all_cookies}")
                        return token, all_cookies, None

                return None
        except Exception as e:
            print(f"listen_qrcode 发生异常: {str(e)}")
            return None

    def verify_account_login(self, cookies):
        """
        校验登录账号信息
        :param cookies:
        :return:
        """
        url = "https://compass.jinritemai.com/ecomauth/loginv1/get_login_subject"

        params = {
            "bus_type": "1",
            "login_source": "compass",
            "entry_source": "0",
            "bus_child_type": "0",
        }
        response = requests.get(url, headers=self.headers, cookies=cookies, params=params)
        assert response.status_code==200,f"请求异常，{response.status_code}"
        res = response.json()
        assert res.get("msg") == "success", f"请求错误，{response.text}"
        assert res.get("data"), f"账号获取店铺错误"
        return  True

    def verify_store_login(self,cookies,shop_name):
        """
        校验店铺cookies
        :return:
        """
        url = "https://fxg.jinritemai.com/ffa/mshop/homepage/index"
        response = requests.get(url, headers=self.headers, cookies=cookies)
        if shop_name in response.text:
            return True
        return False

    def get_store_list(self,cookies):
        """
        获取店铺列表
        :return:
        """

        url = "https://fxg.jinritemai.com/ecomauth/loginv1/get_login_subject"

        params = {
            'bus_type': "1",
            'login_source': "doudian_pc_web",
            'entry_source': "0",
            'bus_child_type': "0",
        }

        response = requests.get(url, params=params, headers=self.headers,cookies=cookies)
        assert response.status_code == 200, f"请求异常，{response.status_code}"
        res = response.json()
        assert res.get("msg") == "success" , f"请求错误，{response.text}"
        assert res.get("data") , f"账号获取店铺错误"
        store_data = []
        for data in res.get("data", {}).get("login_subject_list",[]):
            store_data.append({
                "account_id":data.get("account_id"),
                "account_name":data.get("account_name"),
                "member_id":data.get("member_id"),
                "encode_shop_id":data.get("encode_shop_id"),
                "encode_member_id":data.get("encode_member_id"),
            })
        return store_data

    def get_stores(self,cookies):
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
            store_data.append(data.get("account_name"))
        return store_data

    def get_store_cookies(self,store_info ,cookies:dict):
        """
        通过账号cookies 获取店铺cookies
        :return:
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
        response = requests.get(url, params=params, headers=self.headers,cookies=cookies)
        assert response.status_code == 200,f"请求异常，{response.status_code}"
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

    def verify_login(self,cookies):

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
            'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            'sec-ch-ua-mobile': "?0",
            'sec-ch-ua-platform': "\"Windows\"",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://fxg.jinritemai.com/login/common?extra=%7B%22target_url%22%3A%22https%3A%2F%2Ffxg.jinritemai.com%2Findex.html%22%7D",
            'accept-language': "zh-CN,zh;q=0.9",
            'priority': "u=1, i",
        }

        response = requests.get(url=url, params=params, headers=headers, cookies=cookies)

        assert response.status_code == 200 , f"请求异常,{response.status_code}"
        res = response.json()
        assert res.get("msg") == "success" , f"请求异常,{response.text}"
        return True

    def get_sms_code(self,verify_ticket,cookie):
        """
        获取短信验证码
        """

        url = "https://doudian-sso.jinritemai.com/passport/web/send_code/"

        params = {
            "aid": "4272",
            "language": "zh",
            "account_sdk_source": "web",
            }
        data = {
            "aid": "4272",
            "language": "zh",
            "account_sdk_source": "web",
            "mix_mode": "1",
            "type": "3737",
            "captcha_key": "",
            "mobile": "undefined",
            "verify_ticket": f"{verify_ticket}"
        }
        response = requests.post(url, headers=self.headers, cookies=cookie, params=params, data=data)
        print(response.text)
        assert response.status_code == 200, f"请求异常,{response.status_code}"
        res = response.json()
        assert res.get("message") == "success", f"请求异常,{response.text}"
        return True

    def submit_code(self,code,verify_ticket,cookies):
        """
        提交验证码
        """
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://fxg.jinritemai.com",
            "priority": "u=1, i",
            "referer": "https://fxg.jinritemai.com/",
            "sec-ch-ua": "\"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 QuarkPC/6.4.0.728",
            "x-requested-with": "XMLHttpRequest",
            "x-tt-passport-csrf-token": "9c88f72f7d63ea3b9769ce5bddd966a3"
        }

        url = "https://doudian-sso.jinritemai.com/passport/web/mobile/check_code/"
        params = {
            "aid": "4272",
            "language": "zh",
            "account_sdk_source": "web",
            # "account_sdk_source_info": "7e276d64776172647760466a6b66707777606b667c273f3735292772606761776c736077273f63646976602927666d776a686061776c736077273f63646976602927766d60696961776c736077273f63646976602927756970626c6b76273f302927756077686c76766c6a6b76273f5e7e276b646860273f276b6a716c636c6664716c6a6b762729277671647160273f2761606b6c606127785829276c6b6b60774d606c626d71273f32333529276c6b6b6077526c61716d273f3431313429276a707160774d606c626d71273f3d303729276a70716077526c61716d273f34313032292776716a64776260567164717076273f7e276c6b61607d60614147273f7e276c6167273f276a676f6066712729276a75606b273f2763706b66716c6a6b2729276c6b61607d60614147273f276a676f6066712729274c41474e607c57646b6260273f2763706b66716c6a6b2729276a75606b4164716467647660273f27706b6160636c6b60612729276c7656646364776c273f636469766029276d6476436071666d273f71777060782927696a66646956716a77646260273f7e276c76567075756a77714956716a77646260273f717770602927766c7f60273f3130343d3337292772776c7160273f7177706078292776716a7764626054706a7164567164717076273f7e277076646260273f3435343d363c33292774706a7164273f3637353d3c363d3533343d3729276c7655776c73647160273f6364697660787829277260676269273f7e2773606b616a77273f27426a6a626960254c6b662b252d4b534c414c442c27292777606b6160776077273f27444b424940252d4b534c414c4429254b534c414c44254260436a7766602557515d253135333525516c252d357d35353535373d35302c25416c77606671364134342573765a305a352575765a305a35292541364134342c277829276b6a716c636c6664716c6a6b556077686c76766c6a6b273f2761606b6c6061272927756077636a7768646b6660273f7e27716c68604a776c626c6b273f34323235333136303d373634332b322927707660614f564d606475566c7f60273f3c3033373132313329276b64736c6264716c6a6b516c686c6b62273f7e276160666a616061476a617c566c7f60273f3030333c2927606b71777c517c7560273f276b64736c6264716c6a6b2729276c6b6c716c64716a77517c7560273f276b64736c6264716c6a6b2729276b646860273f276d717175763f2a2a637d622b6f6c6b776c716068646c2b666a682a696a626c6b2a666a68686a6b3a666d646b6b6069387f6d646a766d646b6227292777606b61607747696a666e6c6b62567164717076273f276b6a6b2867696a666e6c6b62272927766077736077516c686c6b62273f276c6b6b60772966616b286664666d602960616260296a776c626c6b272927627069605671647771273f276b6a6b602729276270696041707764716c6a6b273f276b6a6b602778782927776074706076715a6d6a7671273f27637d622b6f6c6b776c716068646c2b666a68272927776074706076715a7564716d6b646860273f272a696a626c6b2a666a68686a6b27292767776a72766077273f7e7878",
            }
        data = {
            "aid": "4272",
            "language": "zh",
            "account_sdk_source": "web",
            "mix_mode": "1",
            "type": "3737",
            "code": self.xor(code),
            "verify_ticket": f"{verify_ticket}"
        }
        response = requests.post(url, headers=headers, cookies=cookies, params=params, data=data)
        print(response.text)
        assert response.status_code == 200, f"请求异常,{response.status_code}"
        res = response.json()
        assert res.get("message") == "success", f"请求异常,{response.text}"
        return res.get("data", {}).get("ticket")

    @classmethod
    def xor(cls,s):
        """抖店xor算法"""
        chars = '0123456789abcdef'
        arr = [i ^ 5 for i in s.encode()]
        result = ''
        for b in arr:
            result += chars[(b & 255) >> 4]
            result += chars[(b & 255) & 15]
        return result

    def full_login(self) -> dict:
        """
        完整登录流程：展示二维码 → 扫码 → 短信验证（如有）→ 返回 cookies
        使用单一 session 保持整个请求链路的 cookies
        """
        import uuid
        session = requests.Session()
        session.headers.update(self.headers)
        session.headers.pop('Accept-Encoding', None)

        # # 代理管理器初始化
        # proxy_mgr = None
        # if proxy_key and QGProxyManager:
        #     proxy_mgr = QGProxyManager(key=proxy_key, area=proxy_area, isp=proxy_isp)
        #     try:
        #         remaining = proxy_mgr.apply_to_session(session)
        #         logger.info(f"[代理] 已启用青果代理: {proxy_mgr.current_proxy}, 剩余{remaining:.0f}秒")
        #         logger.info(f"[代理] ⚠ 代理有效期约60秒，请在二维码出现后尽快扫码！")
        #     except Exception as e:
        #         logger.error(f"[代理] 获取代理失败: {e}，将使用本地IP继续")
        #         proxy_mgr = None
        # elif proxy_key and not QGProxyManager:
        #     logger.error("[代理] proxy_manager 模块未找到，无法启用代理")

        # 生成设备ID（浏览器抓包发现 ewid/web_did 必须存在且一致）
        web_did = uuid.uuid4().hex  # 32位hex，与浏览器格式一致

        # Step 0: 获取 ttwid（ByteDance设备标识符，浏览器所有SSO请求都带此cookie）
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
            logger.info(f"[ttwid] 状态码: {tw_resp.status_code}, 响应: {tw_resp.text[:200]}")
            logger.info(f"[ttwid] cookies: {session.cookies.get_dict()}")
        except Exception as e:
            logger.warning(f"[ttwid] 获取失败（忽略）: {e}")

        # Step 1: 获取二维码（用 session 捕获初始 cookies，如 ttwid）
        qr_resp = session.post(
            "https://doudian-sso.jinritemai.com/get_qrcode/",
            data={
                "aid": "4272", "language": "zh",
                "account_sdk_source": "web",
                "service": "https://fxg.jinritemai.com/login/common",
            }
        )
        assert qr_resp.status_code == 200, f"获取二维码失败: {qr_resp.text}"
        qr_res = qr_resp.json()
        logger.info(f"[get_qrcode] 完整响应: {qr_res}")
        token = qr_res["data"]["token"]
        qr_url = qr_res["data"]["qrcode_index_url"]
        # 如果服务端返回了 ewid/web_did，优先用服务端的
        web_did = qr_res["data"].get("web_did") or qr_res["data"].get("ewid") or web_did
        logger.info(f"二维码已生成，请扫码，token: {token}, web_did: {web_did}")
        # 保存二维码图片到脚本同目录（方便WSL/无GUI环境使用）
        self._save_qrcode(qr_url)
        try:
            self.show_qrcode(qr_url)
        except Exception:
            pass  # WSL等无GUI环境下忽略显示错误

        # Step 2: 轮询扫码状态
        check_url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
        while True:
            time.sleep(0.5)
            poll_data = {
                "aid": "4272", "language": "zh",
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
            resp = session.post(check_url, data=poll_data)
            assert resp.status_code == 200, f"轮询异常: {resp.status_code}"
            resp_data = resp.json()
            # 记录所有中间状态（排除纯等待的 status=1）
            cur_status = resp_data.get('data', {}).get('status')
            if cur_status not in ('1', None) or dict(resp.cookies):
                logger.info(f"[主轮询] status={cur_status} Set-Cookie={dict(resp.cookies)} text={resp.text[:200]}")
                logger.info(f"[主轮询] session cookies: {session.cookies.get_dict()}")

            # 触发短信二次验证
            if "请完成身份验证" in resp.text or resp_data.get('data', {}).get('verify_ticket'):
                logger.info(f"[check_qrconnect] 完整响应: {resp.text}")
                logger.info(f"[check_qrconnect] Set-Cookie: {dict(resp.cookies)}")
                logger.info(f"[check_qrconnect] session全量cookies: {session.cookies.get_dict()}")
                # verify_ticket 可能在 data 层，也可能在顶层
                verify_ticket = (
                    resp_data.get('data', {}).get('verify_ticket') or
                    resp_data.get('verify_ticket', '')
                )
                logger.info(f"[verify_ticket] 完整值: {verify_ticket}")
                return self._do_sms_verify(session, token, verify_ticket, web_did)

            status = resp_data.get('data', {}).get('status')
            if status == "3":
                # 无需短信，直接跟随重定向
                redirect_url = resp_data['data']['redirect_url']
                session.get(redirect_url, allow_redirects=True)
                all_cookies = session.cookies.get_dict()
                logger.info(f"登录成功（无需短信），获取到 {len(all_cookies)} 个 cookies")
                return all_cookies

    def _do_sms_verify(self, session: requests.Session, token: str, verify_ticket: str, web_did: str = "") -> dict:
        """
        短信验证子流程：发送短信 → 用户输入 → 提交验证码 → 完成登录 → 返回 cookies
        JS分析发现：check_code成功后，用 isResend=1 作为URL参数重新调用 check_qrconnect
        """
        import os
        _code_file = "/tmp/dd_code.txt"
        check_url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
        base_params = {"aid": "4272", "language": "zh", "account_sdk_source": "web"}
        base_data = {
            "aid": "4272", "language": "zh", "account_sdk_source": "web",
            "service": "https://fxg.jinritemai.com/login/common",
            "token": token,
            "ewid": web_did,
            "seraph_did": "",
            "web_did": web_did,
            "pc_did": "",
            "redirect_sso_to_login": "false",
            "fp": "",
        }

        # 将 session 中的 csrf token 设置到 header
        csrf_token = session.cookies.get("passport_csrf_token", "")
        session.headers["x-tt-passport-csrf-token"] = csrf_token
        logger.info(f"[send_code前] CSRF token: {csrf_token}")
        logger.info(f"[send_code前] verify_ticket: {verify_ticket}")

        current_ticket = verify_ticket

        for round_num in range(1, 6):
            logger.info(f"[SMS第{round_num}轮] verify_ticket: {current_ticket}")

            # Step A: 发送短信验证码
            sms_resp = session.post(
                "https://doudian-sso.jinritemai.com/passport/web/send_code/",
                params=base_params,
                data={
                    **base_params,
                    "mix_mode": "1", "type": "3737", "captcha_key": "",
                    "mobile": "undefined", "verify_ticket": current_ticket,
                }
            )
            logger.info(f"[send_code] 响应: {sms_resp.text}")
            assert sms_resp.status_code == 200, f"发送短信失败: {sms_resp.text}"
            assert sms_resp.json().get("message") == "success", f"发送短信失败: {sms_resp.text}"
            logger.info(f"[send_code] 短信验证码已发送（第{round_num}轮）")

            # # Step B: 等待验证码（文件轮询）
            # if os.path.exists(_code_file):
            #     os.remove(_code_file)
            # logger.info(f"[等待验证码] 请将短信验证码写入 {_code_file}")
            #
            # deadline = time.time() + 300
            # code = None
            # while time.time() < deadline:
            #     if os.path.exists(_code_file):
            #         code = open(_code_file).read().strip()
            #         os.remove(_code_file)
            #         logger.info(f"[验证码] 从文件读取: {code}")
            #         break
            #     time.sleep(1)
            code = input("输入验证码：")
            if not code:
                raise TimeoutError(f"第{round_num}轮等待验证码超时（5分钟）")

            # Step C: 提交验证码（xor加密）
            check_resp = session.post(
                "https://doudian-sso.jinritemai.com/passport/web/mobile/check_code/",
                params=base_params,
                data={
                    **base_params,
                    "mix_mode": "1", "type": "3737",
                    "code": self.xor(code),
                    "verify_ticket": current_ticket,
                }
            )
            logger.info(f"[check_code] 响应: {check_resp.text}")
            logger.info(f"[check_code] 响应头: {dict(check_resp.headers)}")
            logger.info(f"[check_code] Set-Cookie直接: {dict(check_resp.cookies)}")
            assert check_resp.status_code == 200, f"验证码提交失败: {check_resp.text}"
            check_res = check_resp.json()
            assert check_res.get("message") == "success", f"验证码校验失败: {check_resp.text}"

            # 提取 X-Ms-Token 并注入 session（ByteDance msToken）
            ms_token = check_resp.headers.get("X-Ms-Token") or check_resp.headers.get("x-ms-token")
            if ms_token:
                logger.info(f"[check_code] 注入 msToken: {ms_token[:20]}...")
                session.cookies.set("msToken", ms_token, domain="doudian-sso.jinritemai.com")

            logger.info(f"[check_code] 验证成功")
            logger.info(f"[session cookies after check_code] {session.cookies.get_dict()}")

            # 获取 check_code 返回的 ticket
            new_ticket = check_res.get("data", {}).get("ticket", current_ticket)
            logger.info(f"[check_code] 返回的ticket: {new_ticket}")

            # Step D: check_code 成功后，带 verify_ticket 轮询 check_qrconnect
            # resume_sms_login 证实：必须带 verify_ticket 才能完成登录
            poll_ticket = new_ticket
            logger.info(f"[轮询] check_code 成功，开始轮询 check_qrconnect（带 verify_ticket）")
            for poll in range(1, 40):
                time.sleep(2)


                poll_resp = session.post(check_url, data={**base_data, "verify_ticket": poll_ticket})

                poll_json = poll_resp.json()
                if dict(poll_resp.cookies):
                    logger.info(f"[轮询第{poll}次] 新Set-Cookie: {dict(poll_resp.cookies)}")
                logger.info(f"[轮询第{poll}次] {poll_resp.text[:200]}")
                if poll % 5 == 1:
                    logger.info(f"[轮询第{poll}次] session cookies: {session.cookies.get_dict()}")

                status = poll_json.get('data', {}).get('status')
                if status == "3":
                    redirect_url = poll_json['data']['redirect_url']
                    try:
                        session.get(redirect_url, allow_redirects=True)
                    except Exception as redir_err:
                        logger.warning(f"[重定向] 代理连接失败: {redir_err}，清除代理使用直连...")
                        session.proxies.clear()
                        session.get(redirect_url, allow_redirects=True)
                    all_cookies = session.cookies.get_dict()
                    logger.info(f"登录成功（SMS验证），获取到 {len(all_cookies)} 个 cookies")
                    return all_cookies

                # 2046 + is_optional_verify: 使用新的 verify_ticket 继续轮询
                if poll_json.get('error_code') == 2046:
                    next_ticket = poll_json.get('verify_ticket')
                    is_optional = poll_json.get('is_optional_verify', False)
                    if next_ticket and is_optional:
                        poll_ticket = next_ticket
                        logger.info(f"[轮询第{poll}次] 可选验证，更新ticket继续")
                    continue

                # 其他错误
                logger.info(f"[轮询] 意外响应，停止: {poll_resp.text}")
                break

            raise AssertionError(f"SMS验证后轮询超时（80秒），服务器未返回 status=3")

        raise AssertionError("超过最大验证轮次")

if __name__ == '__main__':
    dd = DdQRCodeLogin()
    dd.full_login()