import os
import requests
import json
import datetime

# 从环境变量获取Cloudflare API密钥和其他信息
cf_api_key = os.environ.get("CF_API_KEY")
zone_id = os.environ.get("ZONE_ID")  # 你需要提供Cloudflare的Zone ID

# 从测试号信息获取
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openId = os.environ.get("OPEN_ID")
weather_template_id = os.environ.get("TEMPLATE_ID")

# 获取Cloudflare过去30天的CDN流量和最大请求数
def get_cloudflare_analytics():
    headers = {
        "Authorization": f"Bearer {cf_api_key}",
        "Content-Type": "application/json"
    }
    
    # 查询过去30天的流量和请求数
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/analytics/dashboard?since=-720h&continuous=true"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        total_bandwidth = data['result']['totals']['bandwidth']['all']
        max_requests = max([day['requests']['all'] for day in data['result']['timeseries']])
        return total_bandwidth, max_requests
    else:
        print(f"Cloudflare API调用失败: {response.status_code}")
        return None, None

# 获取access token
def get_access_token():
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}'
    response = requests.get(url).json()
    access_token = response.get('access_token')
    return access_token

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
                "value": f"{bandwidth / 1024 / 1024:.2f} GB"  # 转换为GB
            },
            "max_requests": {
                "value": f"{requests} 次"
            },
            "today_note": {
                "value": "Cloudflare过去30天的流量与请求数"
            }
        }
    }
    url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
    print(requests.post(url, json.dumps(body)).text)

# 报告CDN流量和请求
def report_cdn_stats():
    # 获取access_token
    access_token = get_access_token()
    # 获取Cloudflare统计信息
    bandwidth, requests = get_cloudflare_analytics()
    if bandwidth and requests:
        # 发送消息
        send_weather(access_token, bandwidth, requests)

if __name__ == '__main__':
    report_cdn_stats()
