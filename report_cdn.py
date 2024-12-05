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
openId = os.environ.get("OPEN_ID")
weather_template_id = os.environ.get("TEMPLATE_ID")


def get_cloudflare_stats(zone_id, api_key):
    """使用GraphQL API获取Cloudflare最近30天的统计数据"""
    # 计算时间范围
    end_date = datetime.datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 转换为ISO格式的日期字符串 (YYYY-MM-DD)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    url = 'https://api.cloudflare.com/client/v4/graphql'
    
    headers = {
        'X-Auth-Key': api_key,
        'X-Auth-Email': 'aaron.bzhan@gmail.com',
        'Content-Type': 'application/json'
    }
    
    # GraphQL 查询
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
        print("正在请求Cloudflare GraphQL API...")
        print(f"时间范围: {start_str} 到 {end_str}")
        
        response = requests.post(
            url,
            headers=headers,
            json={
                "query": query,
                "variables": variables
            }
        )
        
        print(f"响应状态码: {response.status_code}")
        
        data = response.json()
        
        # 检查 data 是否有效
        if data.get('data') and data['data']['viewer']['zones']:
            zones = data['data']['viewer']['zones']
            stats = zones[0]['httpRequests1dGroups']
            if stats and len(stats) > 0:
                total_bytes = stats[0]['sum']['bytes']
                total_requests = stats[0]['sum']['requests']
                
                # 转换带宽为TB
                bandwidth_tb = total_bytes / (1024 ** 4)
                
                print("\n=== Cloudflare CDN 使用统计（近30天）===")
                print(f"总流量: {bandwidth_tb:.2f} TB")
                print(f"总请求数: {total_requests:,} 次")
                print(f"统计时间: {start_str} 到 {end_str}")
                return {
                'bandwidth': f"{bandwidth_tb:.2f}",
                'requests': f"{total_requests:,}"
            }
            else:
                print("未找到统计数据")
        else:
            print("获取数据失败，返回数据无效:", data)
            
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def send_weather(access_token):
    """发送微信模板消息"""
    today_str = datetime.date.today().strftime("%Y年%m月%d日")
    
    # 获取Cloudflare数据
    cf_stats = get_cloudflare_stats(zone_id,cf_api_key)
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
    response = requests.post(url, json=body)
    
    # 检查响应状态
    if response.status_code == 200:
        print("消息发送成功:", response.json())
    else:
        print("发送失败:", response.status_code, response.text)

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
