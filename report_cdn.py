import os
import requests
import json
import datetime

# 从环境变量获取Cloudflare API密钥和其他信息
cf_api_key = os.environ.get("CF_API_KEY")
zone_id = os.environ.get("ZONE_ID")  # Cloudflare的Zone ID
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openId = os.environ.get("OPEN_ID")
weather_template_id = os.environ.get("TEMPLATE_ID")

# 发送消息
def send_weather(access_token, bandwidth, requests):
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {
                "value": today_str
            },
            "cdn_bandwidth": {
                "value": "10.00 GB"  # 测试数据
            },
            "max_requests": {
                "value": "100 次"  # 测试数据
            },
            "today_note": {
                "value": "Cloudflare过去30天的流量与请求数"
            }
        }
    }
    url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
    print(requests.post(url, json=body).text)

# 获取access token
def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}'
    response = requests.get(url).json()
    return response.get('access_token')

if __name__ == '__main__':
    access_token = get_access_token()
    send_weather(access_token, "10.00 GB", "100 次")  # 测试调用
