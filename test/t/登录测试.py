import json
import os

try:
    from tools.qrcode.DdQRCodeLogin import DdQRCodeLogin
except ModuleNotFoundError:
    from DdQRCodeLogin import DdQRCodeLogin


# ========== 代理配置 ==========
# 青果代理key（设为 None 则不使用代理，用本地IP）
PROXY_KEY = "PNH6L17T"
# 代理地区代码（空字符串=不筛选，可指定如 "440100" 广州）
PROXY_AREA = ""
# 运营商 0=不筛选 1=电信 2=移动 3=联通
PROXY_ISP = 0
# ==============================

dd = DdQRCodeLogin()

if PROXY_KEY:
    print("=" * 50)
    print("  已启用青果代理IP（每个IP有效期约60秒）")
    print("  二维码出现后请尽快用手机扫码！")
    print("=" * 50)

cookies = dd.full_login(
    proxy_key=PROXY_KEY,
    proxy_area=PROXY_AREA,
    proxy_isp=PROXY_ISP,
)

if cookies:
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)
    print(f"\n===== 登录成功，cookies 已保存到 {save_path} =====")
    print(json.dumps(cookies, indent=2, ensure_ascii=False))
