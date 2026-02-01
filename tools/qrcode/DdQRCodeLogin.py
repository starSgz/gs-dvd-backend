import time

import requests

from tools.qrcode.QRCodeLogin import QRCodeLogin
from utils.log_util import logger


class DdQRCodeLogin(QRCodeLogin):
    """
    抖店二维码登录
    """
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://compass.jinritemai.com",
        "priority": "u=1, i",
        "referer": "https://compass.jinritemai.com/",
        "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    }

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

    def listen_qrcode(self, token, blocking=True):
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
                    response = session.post(url, data=data)
                    assert response.status_code == 200, f"请求异常，{response.status_code}"
                    
                    response_data = response.json()
                    if response_data['data']['status'] == "3":
                        redirect_url = response_data['data']['redirect_url']
                        logger.info(f"扫码成功，开始处理重定向: {redirect_url}")
                        
                        # 使用 session 访问重定向URL，自动跟随所有重定向并收集 cookies
                        # allow_redirects=True 会自动跟随重定向链，收集所有过程中的 cookies
                        session.get(url=redirect_url, allow_redirects=True)
                        
                        # 从 session 中获取完整的 cookies
                        all_cookies = session.cookies.get_dict()
                        logger.info(f"完整cookies数量: {len(all_cookies)}")
                        logger.info(f"完整cookies内容: {all_cookies}")
                        
                        return token, all_cookies
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
                response = session.post(url, data=data)
                
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('data', {}).get('status') == "3":
                        redirect_url = response_data['data']['redirect_url']
                        
                        # 使用 session 访问重定向URL，自动跟随所有重定向并收集 cookies
                        session.get(url=redirect_url, allow_redirects=True)
                        
                        # 从 session 中获取完整的 cookies
                        all_cookies = session.cookies.get_dict()
                        logger.info(f"完整cookies数量: {len(all_cookies)}")
                        logger.info(f"完整cookies内容: {all_cookies}")
                        return token, all_cookies
                        
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

if __name__ == '__main__':
    dy_login = DdQRCodeLogin()
    # url, token = dy_login.get_qrcode()
    # dy_login.show_qrcode(url)
    # print(dy_login.listen_qrcode(token))
    account_cookies = {'sessionid': '36ca984e66140b906d5ce070f41706a6', 'sessionid_ss': '36ca984e66140b906d5ce070f41706a6',
                       # 'PHPSESSID': 'b67c65bc7f80000317547badfd41f1d4', 'PHPSESSID_SS': 'b67c65bc7f80000317547badfd41f1d4'
                       }
    # print(dy_login.get_store_list(account_cookies))

    store_info = {
        "member_id" :"7573150548351098394",
        "encode_shop_id" :"QhWfhuDN",
        "encode_member_id" :"kpNVwzRnvZRcBZe",
    }
    new_cookies = dy_login.get_store_cookies(store_info,account_cookies)
    print(new_cookies)
    dy_login.test(new_cookies)
    # print(dy_login.verify_store_login(account_cookies, "宇星物语"))