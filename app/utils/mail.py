import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendMail(sender, receiver, title, message):
    from app import appCfg

    content = MIMEMultipart()
    content["From"] = sender
    content["To"] = receiver
    content["Subject"] = title
    content.attach(MIMEText(message, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as mailsrv:
        mailsrv.login(sender, appCfg.MAIL_APP_PASSWORD)
        mailsrv.send_message(content)

    print('utils/mail.py.sendMail():', '메일 전송 완료.')
