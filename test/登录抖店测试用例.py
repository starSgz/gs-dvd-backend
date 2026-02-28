import time
import uuid

# import requests
from curl_cffi import requests
from tools.qrcode.DdQRCodeLogin import DdQRCodeLogin
import base64

from utils.log_util import logger

# 获取验证码图片以及监听扫码状态  需要返回结果
dd = DdQRCodeLogin()


# 生成设备ID（浏览器抓包发现 ewid/web_did 必须存在且一致）
web_did = uuid.uuid4().hex  # 32位hex，与浏览器格式一致

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
session = requests.Session()
session.headers.update(headers)
session.headers.pop('Accept-Encoding', None)

# ===== 修复1: 获取 ttwid（ByteDance 设备标识 cookie） =====
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

# 用 session 获取二维码，捕获 ttwid 等 cookies
qr_url = "https://doudian-sso.jinritemai.com/get_qrcode/"
qr_data = {
    "aid": "4272", "language": "zh", "account_sdk_source": "web",
    "service": "https://fxg.jinritemai.com/login/common"
}
qr_resp = session.post(qr_url, data=qr_data)
assert qr_resp.status_code == 200, f"获取二维码失败: {qr_resp.text}"
qr_res = qr_resp.json()
a = qr_res["data"]["qrcode_index_url"]
token = qr_res["data"]["token"]
img = dd.bash64_qrcode(a)
# 如果服务端返回了 ewid/web_did，优先用服务端的
web_did = qr_res["data"].get("web_did") or qr_res["data"].get("ewid") or web_did

logger.info(f"[获取二维码] session cookies: {session.cookies.get_dict()}")
print(a, token, img)
with open("qrcode.png", "wb") as f:
    f.write(base64.b64decode(img))

# 获取ticket、cookies
verify_info = {}
while True:
    time.sleep(1)
    url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
    data = {
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
    response = session.post(url, data=data)
    assert response.status_code == 200, f"请求异常，{response.status_code}"

    response_data = response.json()

    if "请完成身份验证" in response.text or response_data.get('data', {}).get('verify_ticket'):
        # 需要身份验证（短信/邮箱验证码）
        all_cookies = session.cookies.get_dict()
        # ===== 修复2: 从 response_data['data'] 下提取 verify_ticket =====
        verify_info = {
            'verify_ticket': response_data.get('data', {}).get('verify_ticket') or response_data.get('verify_ticket', ''),
            'verify_ways': response_data.get('data', {}).get('verify_ways', []),
            'verify_scene_desc': response_data.get('data', {}).get('verify_scene_desc', '为保证账号安全，请完成身份验证'),
        }
        logger.info(f"需要身份验证: {verify_info}")
        logger.info(f"[需要身份验证] Set-Cookie={dict(response.cookies)} text={response.text[:200]}")

        break
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
        print(token,all_cookies)
        break
    print("=====等待下次循环")

ticket = verify_info.get("verify_ticket")
csrf_token = session.cookies.get("passport_csrf_token", "")
session.headers["x-tt-passport-csrf-token"] = csrf_token
logger.info(f"[CSRF] 设置 x-tt-passport-csrf-token: {csrf_token}")

# 发送短信 - 用 session 保持 cookie 链路
sms_url = "https://doudian-sso.jinritemai.com/passport/web/send_code/"
sms_params = {"aid": "4272", "language": "zh", "account_sdk_source": "web"}
sms_data = {
    "aid": "4272", "language": "zh", "account_sdk_source": "web",
    "mix_mode": "1", "type": "3737", "captcha_key": "",
    "mobile": "undefined", "verify_ticket": ticket
}
logger.info(f"[发送短信] 当前session cookies: {session.cookies.get_dict()}")
sms_resp = session.post(sms_url, data=sms_data, params=sms_params)
assert sms_resp.status_code == 200, f"发送短信失败: {sms_resp.text}"
logger.info(f"[发送短信] 响应: {sms_resp.text}")
logger.info(f"[发送短信] 响应Set-Cookie: {dict(sms_resp.cookies)}")
logger.info(f"[发送短信] session cookies更新后: {session.cookies.get_dict()}")
print("发送短信成功")

code = input("请输入验证码: ")

# 提交验证码 - 用 session 保持 cookie（passport_mfa_token 等关键 cookie 由此响应设置）
check_url = "https://doudian-sso.jinritemai.com/passport/web/mobile/check_code/"
check_params = {"aid": "4272", "language": "zh", "account_sdk_source": "web"}
check_data = {
    "aid": "4272", "language": "zh", "account_sdk_source": "web",
    "mix_mode": "1", "type": "3737",
    "code": DdQRCodeLogin.xor(str(code)),
    "verify_ticket": ticket
}
logger.info(f"[提交验证码] 当前session cookies: {session.cookies.get_dict()}")
check_resp = session.post(check_url, data=check_data, params=check_params)
assert check_resp.status_code == 200, f"验证码提交失败: {check_resp.text}"
logger.info(f"[提交验证码] 响应: {check_resp.text}")
logger.info(f"[提交验证码] 响应Set-Cookie: {dict(check_resp.cookies)}")
logger.info(f"[提交验证码] session cookies更新后: {session.cookies.get_dict()}")
check_res = check_resp.json()
assert check_res.get("message") == "success", f"验证码校验失败: {check_resp.text}"

# 提取 X-Ms-Token 并注入 session（ByteDance msToken）
ms_token = check_resp.headers.get("X-Ms-Token") or check_resp.headers.get("x-ms-token")
if ms_token:
    logger.info(f"[check_code] 注入 msToken: {ms_token[:20]}...")
    session.cookies.set("msToken", ms_token, domain="doudian-sso.jinritemai.com")
logger.info(f"[check_code] 验证成功")
logger.info(f"[session cookies after check_code] {session.cookies.get_dict()}")



new_ticket = check_res.get("data", {}).get("ticket") or ticket
print(f"验证码提交成功, new_ticket: {new_ticket}")

# ===== 修复3: 使用轮询循环替代单次请求，最多等待80秒 =====
url = "https://doudian-sso.jinritemai.com/check_qrconnect/"
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

poll_ticket = new_ticket
logger.info(f"[轮询] check_code 成功，开始轮询 check_qrconnect（带 verify_ticket）")

for poll in range(1, 40):
    time.sleep(2)
    #### 这里需要取消代理，否则获取不到
    poll_resp = session.post(url, data={**base_data, "verify_ticket": poll_ticket})
    assert poll_resp.status_code == 200, f"请求异常，{poll_resp.status_code}"

    poll_json = poll_resp.json()
    if dict(poll_resp.cookies):
        logger.info(f"[轮询第{poll}次] 新Set-Cookie: {dict(poll_resp.cookies)}")
    logger.info(f"[轮询第{poll}次] {poll_resp.text[:200]}")
    if poll % 5 == 1:
        logger.info(f"[轮询第{poll}次] session cookies: {session.cookies.get_dict()}")

    status = poll_json.get('data', {}).get('status')
    if status == "3":
        redirect_url = poll_json['data']['redirect_url']
        logger.info(f"[轮询第{poll}次] 扫码成功，开始处理重定向: {redirect_url}")
        # 使用 session 访问重定向URL，自动跟随所有重定向并收集 cookies
        session.get(url=redirect_url, allow_redirects=True)

        # 从 session 中获取完整的 cookies
        all_cookies = session.cookies.get_dict()
        logger.info(f"登录成功（SMS验证），获取到 {len(all_cookies)} 个 cookies")
        print("===== 登录成功 =====")
        print(all_cookies)
        break