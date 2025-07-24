from celery import Celery

RABBITMQ_URL = "amqp://root:test@127.0.0.1"
CELERY_BACKEND_URL = "db+mysql://rabbitmq:rabbitmq01@127.0.0.1/messaging"

celeryApp = Celery(
    "fastapi-codelab"
    , broker=RABBITMQ_URL
    , backend=CELERY_BACKEND_URL
    , broker_connection_retry_on_startup=True
    # , include=["app.utils.celery.task"] # when referencing tasks which are defined in other modules.
)

# # 셀러리 태스크 정의
# @celeryApp.task
# def add(x, y):
#     return x+y

from celery import Task

# 셀러리 태스크 클래스 정의
class AddTask(Task):
    name = 'celery add task'

    def run(self, x, y):    # run: standard entry point of a celery task class 
        return x+y

celeryApp.register_task(AddTask)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class SendEmailCeleryTask(Task):
    name = "send_email_celery_task" # Celery creates a single shared instance.

    def run(self, sender, receiver, title, message):    # run: standard entry point of a celery task class
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

celeryApp.register_task(SendEmailCeleryTask)
