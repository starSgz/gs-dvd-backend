import json
import os
import time

import execjs
execjs.runtime_name = 'node'

from tools.qrcode.QRCodeLogin import QRCodeLogin
import requests

class QfQRCodeLogin(QRCodeLogin):
    """
    千帆二维码登录
    """
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json",
        "origin": "https://customer.xiaohongshu.com",
        "priority": "u=1, i",
        "referer": "https://customer.xiaohongshu.com/login?service=https://ark.xiaohongshu.com/ark",
        "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.js_file_path = os.path.join(current_dir, "js", "qf.js")


    def get_qrcode(self):
        data = {
            "service": "https%3A%2F%2Fark.xiaohongshu.com%2Fark"
        }
        data = json.dumps(data, separators=(',', ':'))

        url = "https://customer.xiaohongshu.com/api/cas/customer/web/qr-code"
        # 获取JS文件的绝对路径

        x_s = self.gen_x_s(
            path="/api/cas/customer/web/qr-code",
            data={"service": "https%3A%2F%2Fark.xiaohongshu.com%2Fark"},
            js_path=self.js_file_path
        )
        self.headers["x-s"] = x_s["X-s"]
        self.headers["x-t"] = str(x_s["X-t"])
        response = requests.post(url, headers=self.headers, data=data)
        assert response.status_code == 200, f"请求异常,{response.status_code}"

        res = response.json()
        qr_url = res.get("data", {}).get("url")
        return qr_url, res.get("data", {}).get("id"),self.bash64_qrcode(qr_url)

    @classmethod
    def gen_x_s(cls, path, data, js_path):
        context = execjs.compile(cls.js_from_file(js_path))
        x_s = context.call("lt", path, data)
        return x_s

    @classmethod
    def js_from_file(cls, file_name):
        """
        读取js文件
        :return:
        """
        with open(file_name, 'r', encoding='UTF-8') as file:
            result = file.read()
        return result

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
            
            url = "https://customer.xiaohongshu.com/api/cas/customer/web/qr-code"
            params = {
                "service": "https%3A%2F%2Fark.xiaohongshu.com%2Fapp-note%2Fmanagement",
                "qr_code_id": f"{token}",
                "source": ""
            }
            x_s = self.gen_x_s(
                path="/api/cas/customer/web/qr-code",
                data={
                "service": "https%3A%2F%2Fark.xiaohongshu.com%2Fapp-note%2Fmanagement",
                "qr_code_id": f"{token}",
                "source": "" },
                js_path=self.js_file_path
            )
            session.headers["x-s"] = x_s["X-s"]
            session.headers["x-t"] = str(x_s["X-t"])
            
            if blocking:
                # 阻塞模式：持续轮询直到扫码成功
                while True:
                    response = session.get(url, params=params)
                    assert response.status_code == 200, f"请求异常，{response.status_code}"
                    
                    response_data = response.json()
                    if response_data['data']['status'] == 1:
                        ticket = response_data['data']['ticket']
                        print(f"扫码成功，获取到ticket: {ticket}")

                        payload = {
                            "system": "https://ark.xiaohongshu.com/app-system/home?from=ark-login",
                            "ticket": ticket
                        }
                        sso_url = "https://ark.xiaohongshu.com/api/edith/open/ssologin"
                        sso_response = session.post(url=sso_url, data=json.dumps(payload))
                        assert sso_response.status_code == 200, f"请求异常，{sso_response.status_code}"
                        assert sso_response.json().get("code") == 0, f"请求异常，{sso_response.text}"
                        
                        # 从 session 中获取完整的 cookies
                        all_cookies = session.cookies.get_dict()
                        print(f"完整cookies数量: {len(all_cookies)}")
                        print(f"完整cookies内容: {all_cookies}")
                        
                        return token, all_cookies, None
                    time.sleep(0.5)
            else:
                # 非阻塞模式：单次检查
                response = session.get(url=url, params=params)
                assert response.status_code == 200, f"请求异常，{response.status_code}"
                
                response_data = response.json()
                if response_data.get('data', {}).get('status') == 1:
                    ticket = response_data['data']['ticket']

                    payload = {
                        "system": "https://ark.xiaohongshu.com/app-system/home?from=ark-login",
                        "ticket": ticket
                    }
                    sso_url = "https://ark.xiaohongshu.com/api/edith/open/ssologin"
                    sso_response = session.post(url=sso_url, data=json.dumps(payload))
                    assert sso_response.status_code == 200, f"请求异常，{sso_response.status_code}"
                    assert sso_response.json().get("code") == 0, f"请求异常，{sso_response.text}"
                    
                    # 从 session 中获取完整的 cookies
                    all_cookies = session.cookies.get_dict()
                    return token, all_cookies
                    
                return None
        except Exception as e:
            print(f"listen_qrcode 发生异常: {str(e)}")
            return None

    def verify_login(self, cookies):
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "priority": "u=1, i",
            "referer": "https://ark.xiaohongshu.com/app-note/management?from=ark-login",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }
        url = "https://ark.xiaohongshu.com/api/edith/seller/info/v2"
        response = requests.get(url, headers=headers, cookies=cookies)
        assert response.status_code == 200 , f"请求异常，{response.status_code}"
        res = response.json()
        return res.get("data",{}).get("company_name")

    def get_stores(self,cookies):

        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "priority": "u=1, i",
            "referer": "https://ark.xiaohongshu.com/app-note/management?from=ark-login",
            "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }
        url = "https://ark.xiaohongshu.com/api/edith/seller/info/v2"
        response = requests.get(url, headers=headers, cookies=cookies)
        assert response.status_code == 200, f"请求异常，{response.status_code}"
        res = response.json()
        return [res.get("data", {}).get("company_name")]



if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_file_path = os.path.join(current_dir, "js", "qf.js")
    x = QfQRCodeLogin.gen_x_s(
        path="/api/cas/customer/web/qr-code",
        data={
            "service": "https%3A%2F%2Fark.xiaohongshu.com%2Fapp-note%2Fmanagement",
            "qr_code_id": f"68c517600058301041491974",
            "source": ""},
        js_path=js_file_path
    )
    print(x)