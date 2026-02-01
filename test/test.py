import requests

url = "https://fxg.jinritemai.com/ecomauth/loginv1/get_login_subject"

params = {
  'bus_type': "1",
  'login_source': "doudian_pc_web",
  'entry_source': "0",
  'bus_child_type': "0",
  '_lid': "927145279207"
}

headers = {
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
  'Accept': "application/json, text/plain, */*",
  'Accept-Encoding': "gzip, deflate, br, zstd",
  'sec-ch-ua': "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
  'sec-ch-ua-mobile': "?0",
  'sec-ch-ua-platform': "\"Windows\"",
  'sec-fetch-site': "same-origin",
  'sec-fetch-mode': "cors",
  'sec-fetch-dest': "empty",
  'referer': "https://fxg.jinritemai.com/login/common?channel=zhaoshang",
  'accept-language': "zh-CN,zh;q=0.9",
  'priority': "u=1, i",
  # 'Cookie': "d_ticket=358a680c89495e6f58a731566935939620d15; s_v_web_id=verify_mkfnoa8h_svddxlZZ_gU3d_4OKV_BtMq_WRf89UfUvcXu; passport_csrf_token=b00aafa37296f76ccbb810517c5c4523; passport_csrf_token_default=b00aafa37296f76ccbb810517c5c4523; csrf_session_id=81d69eb12655bbc2ae3935382d3dee63; Hm_lvt_b6520b076191ab4b36812da4c90f7a5e=1768494014; HMACCOUNT=2EB0F5BDEAAE0468; is_staff_user=false; source=doudian_homepage_new_merchant; zsgw_business_data=%7B%22uuid%22%3A%2277e0d866-cbdd-4f6a-837e-ae77769a0fc9%22%2C%22platform%22%3A%22pc%22%2C%22source%22%3A%22doudian_homepage_new_merchant%22%7D; passport_mfa_token=Ci%2FZYyftMY1w9MGX3Dy5cWx6sIml3BnreenZ2qOxKT%2FmzMFKfP90GNC7HDnEod%2FzDBpKCjwAAAAAAAAAAAAAT%2FX2xLESCJyjhCMoYFz3UUTP2nr5NLNWq77SrMX%2BqlmVl98BzwtqKgMVayCSYMK2ZB0QooqHDhj2sdFsIAIiAQM5Nkux; ucas_c0=CkEKBTEuMC4wEIaIg_bApYa9aRjmJiD5hYCpmay-BiiwITCro-D7iqzwBEC2sujLBki25qTOBlCavJbIyonPjGlYbhIUC0AnZovOs_YITz9TtHf_eERZHqU; ucas_c0_ss=CkEKBTEuMC4wEIaIg_bApYa9aRjmJiD5hYCpmay-BiiwITCro-D7iqzwBEC2sujLBki25qTOBlCavJbIyonPjGlYbhIUC0AnZovOs_YITz9TtHf_eERZHqU; ecom_gray_shop_id=254548206; Hm_lpvt_b6520b076191ab4b36812da4c90f7a5e=1769692691; tt_scid=lNHobkCpFfGsBdezPc6OmJRMq5AI4TT0y65kSUryPN6BvC0k5veT5mrDzlKa77Xr4fce; ttwid=1%7CXxZuNBIt62ZNZXIGg0jEGIu2A-UXnQkKnVYziuJAbKE%7C1769692708%7Cadbf039352f2de5c0667e7dbc798e2f5effa794d7b8ec0e9634dc21749e5bc7f; odin_tt=5380a541252f15c96606fd1e19c22a9c457125f0fee45aefb788c309a93c31719adf1bca86fcc2e8aaa176490d4ce9a07f9e82badc430b71ccbc9ebfaa6834e8; passport_auth_status=bc20d2ed9fbd8a61809e1cff652276ba%2C3dd88be6b3370212beee5bc310bee5ec; passport_auth_status_ss=bc20d2ed9fbd8a61809e1cff652276ba%2C3dd88be6b3370212beee5bc310bee5ec; sid_guard=33debbc63a7bdbfc3c33ad3fd7c306a4%7C1769692714%7C5184002%7CMon%2C+30-Mar-2026+13%3A18%3A36+GMT; uid_tt=f790a067660d1201342a75dade033a71; uid_tt_ss=f790a067660d1201342a75dade033a71; sid_tt=33debbc63a7bdbfc3c33ad3fd7c306a4; sessionid=33debbc63a7bdbfc3c33ad3fd7c306a4; sessionid_ss=33debbc63a7bdbfc3c33ad3fd7c306a4; session_tlb_tag=sttt%7C8%7CM967xjp72_w8M60_18MGpP_________1ki3q3i4z16KkKCnczaxhzG9Yiq_S9IThAqI_RNmKHtA%3D; sid_ucp_v1=1.0.0-KDY3Zjg0Yjk5YTU1Njc0ZWYzMWQyZDQyZTRkNjI1ZWM1YzEyNTA5NmEKGQiro-D7iqzwBBCqvO3LBhiwISAMOAZA9AcaAmxmIiAzM2RlYmJjNjNhN2JkYmZjM2MzM2FkM2ZkN2MzMDZhNA; ssid_ucp_v1=1.0.0-KDY3Zjg0Yjk5YTU1Njc0ZWYzMWQyZDQyZTRkNjI1ZWM1YzEyNTA5NmEKGQiro-D7iqzwBBCqvO3LBhiwISAMOAZA9AcaAmxmIiAzM2RlYmJjNjNhN2JkYmZjM2MzM2FkM2ZkN2MzMDZhNA"
}
cookies = {'is_staff_user': 'false', 'passport_auth_status': 'dbb09c6ba41f3d2089114b432a697e0f%2C', 'passport_auth_status_ss': 'dbb09c6ba41f3d2089114b432a697e0f%2C', 'session_tlb_tag': 'sttt%7C20%7CbTSqwwnH7y3gFB1XseLrJP________-zWbB0rW2vK6QdM-dO4HZP63F2lu4SVZnHjUdRN5zZnpY%3D', 'sessionid': '6d34aac309c7ef2de0141d57b1e2eb24', 'sessionid_ss': '6d34aac309c7ef2de0141d57b1e2eb24', 'sid_guard': '6d34aac309c7ef2de0141d57b1e2eb24%7C1769694790%7C5183987%7CMon%2C+30-Mar-2026+13%3A52%3A57+GMT', 'sid_tt': '6d34aac309c7ef2de0141d57b1e2eb24', 'sid_ucp_v1': '1.0.0-KDM3ZTE1YTNjZjhlMDMxYzNhM2FlNzBiMjBhYzk5MjQ4OWU5YmUwM2UKFwiro-D7iqzwBBDGzO3LBhiwITgGQPQHGgJsZiIgNmQzNGFhYzMwOWM3ZWYyZGUwMTQxZDU3YjFlMmViMjQ', 'ssid_ucp_v1': '1.0.0-KDM3ZTE1YTNjZjhlMDMxYzNhM2FlNzBiMjBhYzk5MjQ4OWU5YmUwM2UKFwiro-D7iqzwBBDGzO3LBhiwITgGQPQHGgJsZiIgNmQzNGFhYzMwOWM3ZWYyZGUwMTQxZDU3YjFlMmViMjQ', 'uid_tt': 'a70ad137f4f633202c6036f74f251f09', 'uid_tt_ss': 'a70ad137f4f633202c6036f74f251f09'}

response = requests.get(url, params=params, headers=headers)

print(response.text)



