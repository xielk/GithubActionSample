import os
import requests
import json
import datetime
from datetime import timedelta

# 从环境变量获取配置信息
cf_api_key = os.environ.get("CF_API_KEY")
zone_id = os.environ.get("ZONE_ID")
appID = os.environ.get("APP_ID")
appSecret = os.environ.get("APP_SECRET")
# 将 openId 修改为一个用户 ID 列表
openIds = os.environ.get("OPEN_IDS").split(',')  # 以逗号分隔的用户 ID 列表
weather_template_id = os.environ.get("TEMPLATE_ID")

def get_cloudflare_stats():
    """使用GraphQL API获取Cloudflare最近30天的统计数据"""
    end_date = datetime.datetime.now()
    start_date = end_date - timedelta(days=30)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    url = 'https://api.cloudflare.com/client/v4/graphql'
    
    headers = {
        'X-Auth-Key': cf_api_key,
        'X-Auth-Email': 'aaron.bzhan@gmail.com',
        'Content-Type': 'application/json'
    }
    
    query = """
    query ($zoneTag: String!, $start: String!, $end: String!) {
        viewer {
            zones(filter: { zoneTag: $zoneTag }) {
                httpRequests1dGroups(
                    limit: 30
                    filter: { date_geq: $start, date_leq: $end }
                ) {
                    sum {
                        bytes
                        requests
                    }
                }
            }
        }
    }
    """
    
    variables = {
        "zoneTag": zone_id,
        "start": start_str,
        "end": end_str
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json={
                "query": query,
                "variables": variables
            }
        )
        
        data = response.json()
        
        if data.get('data') and data['data']['viewer']['zones']:
            zones = data['data']['viewer']['zones']
            stats = zones[0]['httpRequests1dGroups']
            if stats and len(stats) > 0:
                total_bytes = stats[0]['sum']['bytes']
                total_requests = stats[0]['sum']['requests']
                
                # 转换带宽为TB
                bandwidth_tb = total_bytes / (1024 ** 4)
                
                return {
                    'bandwidth': f"{bandwidth_tb:.2f}",
                    'requests': f"{total_requests:,}"
                }
        
        print("获取数据失败，返回数据无效:", data)
        return None
            
    except Exception as e:
        print(f"请求Cloudflare API出错: {str(e)}")
        return None

def send_weather(access_token):
    """发送微信模板消息给多个用户"""
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    
    # 获取Cloudflare数据
    cf_stats = get_cloudflare_stats()
    if not cf_stats:
        cf_stats = {'bandwidth': '0.00', 'requests': '0'}  # 默认值
    
    for openId in openIds:
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
        response = requests.post(url, json=body)
        
        # 检查响应状态
        if response.status_code == 200:
            print(f"消息成功发送给用户 {openId.strip()}:", response.json())
        else:
            print(f"发送失败给用户 {openId.strip()}:", response.status_code, response.text)

def get_access_token():
    """获取微信access token"""
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appID.strip()}&secret={appSecret.strip()}'
    response = requests.get(url).json()
    return response.get('access_token')

if __name__ == '__main__':
    access_token = get_access_token()
    if access_token:
        send_weather(access_token)
    else:
        print("获取 access_token 失败")
