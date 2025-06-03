import json
import os
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def send_email_alert():
    """发送邮件告警"""
    try:
        # 读取配置文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'alert.json')
        
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)

        # 配置信息
        host_server = config['host_server']
        sender_qq = config['sender_qq']
        pwd = config['pwd']
        receiver = config['receiver']
        mail_title = config['mail_title']
        mail_content = config['mail_content']

        # 创建邮件内容
        msg = MIMEMultipart()
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_qq
        msg['To'] = ";".join(receiver)
        msg.attach(MIMEText(mail_content, 'plain', 'utf-8'))

        # 发送邮件
        with SMTP_SSL(host_server) as smtp:  # 使用上下文管理器自动关闭连接
            smtp.login(sender_qq, pwd)
            smtp.sendmail(sender_qq, receiver, msg.as_string())
            
        return True, "邮件发送成功"
        
    except FileNotFoundError as e:
        return False, f"配置文件未找到: {str(e)}"
    except KeyError as e:
        return False, f"配置文件缺少必要字段: {str(e)}"
    except Exception as e:
        return False, f"邮件发送失败: {str(e)}"

# if __name__ == "__main__":
#     success, message = send_email_alert()
#     print(message)