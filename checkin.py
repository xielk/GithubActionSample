import requests
import json

def checkin():
    # 签到 URL
    url = 'https://www.xmrth.lol/user/checkin'
    
    # Cookie 字符串转换为字典
    cookie_str = '''sl-session=P+/mLY5pLGf90/ARMG8eAA==; uid=250182; email=xielk%40yeah.net; key=3c1999980adb0472ce356a63baa7b27c84d86cf28f4dd; ip=2de2b1c90c8a1a4620304c115140843e; expire_in=1732173488; sl_jwt_session=JTvZW7VmLGfDNbJgyrUXNw==; sl_jwt_sign=; crisp-client%2Fsession%2F5690d3a5-53e4-435e-a52b-12af296b5cd9=session_7c6df5e9-0739-44cc-a216-7cf263ebb383; crisp-client%2Fsession%2F5690d3a5-53e4-435e-a52b-12af296b5cd9%2F00fb53d8-86cf-37a6-b621-721ad94342d1=session_7c6df5e9-0739-44cc-a216-7cf263ebb383'''
    cookies = {}
    for item in cookie_str.split(';'):
        if item.strip():
            key, value = item.strip().split('=', 1)
            cookies[key] = value

    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }

    try:
        # 发送请求
        response = requests.post(url, cookies=cookies, headers=headers)
        result = response.json()
        
        # 判断返回结果
        if '你获得了' in result.get('msg', ''):
            print('签到成功！')
            print('消息:', result['msg'])
        else:
            print('签到失败！')
            print('返回信息:', result)
            
    except Exception as e:
        print('发生错误:', str(e))

# 登录函数（预留）
def login(username, password):
    # 登录 URL（需要时添加）
    login_url = 'https://www.xmrth.lol/auth/login'
    
    # 登录逻辑（需要时实现）
    pass

if __name__ == '__main__':
    # 执行签到
    checkin()
