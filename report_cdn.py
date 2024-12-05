import os
import requests as req
import json
import datetime
from datetime import timedelta

# 从环境变量获取Cloudflare API密钥和其他信息
cf_api_key = os.environ.get("CF_API_KEY")
zone_id = os.environ.get("ZONE_ID")  # Cloudflare的Zone ID
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
openId = os.environ.get("OPEN_ID")
weather_template_id = os.environ.get("TEMPLATE_ID")

def get_cloudflare_stats():
    """获取Cloudflare最近30天的统计数据"""
    end_date = datetime.datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 转换为ISO格式的字符串
    start_str = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/analytics/dashboard'
    
    headers = {
        'Authorization': f'Bearer {cf_api_key}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'since': start_str,
        'until': end_str,
        'continuous': True
    }
    
    try:
        response = req.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            # 获取带宽数据（bytes）并转换为TB
            bandwidth = data['result']['totals']['bandwidth']['all'] / (1024 ** 4)  # 转换为TB
            requests = data['result']['totals']['requests']['all']
            return {
                'bandwidth': f"{bandwidth:.2f}",  # 保留两位小数
                'requests': f"{requests:,}"  # 添加千位分隔符
            }
        else:
            print(f"获取Cloudflare数据失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求Cloudflare API出错: {str(e)}")
        return None

def send_weather(access_token):
    """发送微信模板消息"""
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    
    # 获取Cloudflare数据
    cf_stats = get_cloudflare_stats()
    if not cf_stats:
        cf_stats = {'bandwidth': '0.00', 'requests': '0'}  # 默认值
    
    body = {
        "touser": openId.strip(),
        "template_id": weather_template_id.strip(),
        "url": "https://weixin.qq.com",
        "data": {
            "date": {
                "value": today_str
            },
            "cdn_bandwidth": {
                "value": f"{cf_stats['bandwidth']} TB"
            },
            "max_requests": {
                "value": f"{cf_stats['requests']} 次"
            },
            "today_note": {
                "value": "Cloudflare过去30天的流量与请求数"
            }
        }
    }
    
    url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
    response = req.post(url, json=body)
    
    # 检查响应状态
    if response.status_code == 200:
        print("消息发送成功:", response.json())
    else:
        print("发送失败:", response.status_code, response.text)

def get_access_token():
    """获取微信access token"""
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}'
    response = req.get(url).json()
    return response.get('access_token')

if __name__ == '__main__':
    access_token = get_access_token()
    if access_token:
        send_weather(access_token)
    else:
        print("获取 access_token 失败")
