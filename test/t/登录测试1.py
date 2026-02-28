import json
import os

from DdQRCodeLogin1 import DdQRCodeLogin

# 初始化登录类
dd = DdQRCodeLogin()

# 执行登录（去掉了 proxy 相关参数）
cookies = dd.full_login()

if cookies:
    # 获取当前脚本所在目录并拼接保存路径
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.json")

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)

    print(f"\n===== 登录成功，cookies 已保存到 {save_path} =====")
    print(json.dumps(cookies, indent=2, ensure_ascii=False))