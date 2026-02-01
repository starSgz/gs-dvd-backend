import requests


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    # "Accept-Encoding": "gzip, deflate, br, zstd",
    "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://fxg.jinritemai.com/login/common?channel=zhaoshang",
    "accept-language": "zh-CN,zh;q=0.9",
    "priority": "u=1, i"
}
cookies = {'is_staff_user': 'false', 'passport_auth_status': 'd651ba06f6122f5ad6a7e9ecc2479f5e,', 'passport_auth_status_ss': 'd651ba06f6122f5ad6a7e9ecc2479f5e,', 'session_tlb_tag': 'sttt|9|ptfaqL9WpDYwMW1_Aoe7m__________83Poz4bCQXr39yxDknPl9TD6RDMjVTaO5bsz_rxspA9g=', 'sessionid': 'a6d7daa8bf56a43630316d7f0287bb9b', 'sessionid_ss': 'a6d7daa8bf56a43630316d7f0287bb9b', 'sid_guard': 'a6d7daa8bf56a43630316d7f0287bb9b|1769694113|5183997|Mon, 30-Mar-2026 13:41:50 GMT', 'sid_tt': 'a6d7daa8bf56a43630316d7f0287bb9b', 'sid_ucp_v1': '1.0.0-KGE2Y2RlMDNkMGI4YTJkNWQxNWJkODVhNWNiMjZmNjdhNTkwMzFiMjQKFwiro-D7iqzwBBChx-3LBhiwITgGQPQHGgJsZiIgYTZkN2RhYThiZjU2YTQzNjMwMzE2ZDdmMDI4N2JiOWI', 'ssid_ucp_v1': '1.0.0-KGE2Y2RlMDNkMGI4YTJkNWQxNWJkODVhNWNiMjZmNjdhNTkwMzFiMjQKFwiro-D7iqzwBBChx-3LBhiwITgGQPQHGgJsZiIgYTZkN2RhYThiZjU2YTQzNjMwMzE2ZDdmMDI4N2JiOWI', 'uid_tt': 'ce2a8ca89c468b48a8212b8e9e3cbc3d', 'uid_tt_ss': 'ce2a8ca89c468b48a8212b8e9e3cbc3d'}

url = "https://fxg.jinritemai.com/ecomauth/loginv1/get_login_subject"
params = {
    "bus_type": "1",
    "login_source": "doudian_pc_web",
    "entry_source": "0",
    "bus_child_type": "0",
    "_lid": "927145279207"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

print(response.text)
print(response)