from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


host_server = 'smtp.qq.com'  #smtp服务器
sender_qq = 'wfshenm@qq.com' #发件人邮箱
pwd = 'tsbfpwnfsuocciha'
receiver = ['wfshenm@qq.com' ]#收件人邮箱
mail_title = '测试邮件' #邮件标题
mail_content = "这是一封测试邮件" #邮件正文内容

msg = MIMEMultipart()
msg["Subject"] = Header(mail_title,'utf-8')
msg["From"] = sender_qq
msg['To'] = ";".join(receiver)
msg.attach(MIMEText(mail_content,'plain','utf-8'))



smtp = SMTP_SSL(host_server) # ssl登录

smtp.login(sender_qq,pwd)

smtp.sendmail(sender_qq,receiver,msg.as_string())

smtp.quit()
