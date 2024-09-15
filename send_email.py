import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import os

# 邮件配置
smtp_server = 'smtp.office365.com'
smtp_port = 587
smtp_user = 'grevamhgwbq@hotmail.com'
smtp_password = os.getenv('EMAIL_PASSWORD')

# 邮件内容
subject = 'Cloudflare Traffic Report for the Last 30 Days'
body = f'''
Hi,

Here is the Cloudflare traffic report for the zone ID a768a88b8f71866844da6c81b533ba9c for the last 30 days:

- Total Bandwidth: {os.getenv('BANDWIDTH_TB')} TB
- Total Requests: {os.getenv('REQUESTS')}

Best regards,
Cloudflare Monitoring
'''

# 创建邮件
msg = MIMEMultipart()
msg['From'] = formataddr(('Cloudflare Monitoring', smtp_user))
msg['To'] = 'xielk@yeah.net, 5817253@qq.com'
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

# 发送邮件
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(smtp_user, ['xielk@yeah.net', '5817253@qq.com'], msg.as_string())
