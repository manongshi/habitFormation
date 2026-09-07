import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import settings


def send_verification_email(email: str, code: str) -> None:
    if settings.email_delivery_mode == "console":
        if settings.app_env == "production":
            raise RuntimeError("生产环境禁止使用 console 邮件模式")
        print(f"[DEV EMAIL] {email} 的注册验证码：{code}")
        return

    if settings.email_delivery_mode != "smtp":
        raise RuntimeError("未配置可用的邮件发送方式")
    if not all(
        [
            settings.smtp_host,
            settings.smtp_username,
            settings.smtp_password,
            settings.smtp_from_email,
        ]
    ):
        raise RuntimeError("SMTP 配置不完整")

    message = EmailMessage()
    message["Subject"] = "AI 考证教练注册验证码"
    message["From"] = formataddr((settings.smtp_from_name, settings.smtp_from_email))
    message["To"] = email
    message.set_content(
        f"你的注册验证码是：{code}\n\n验证码 {settings.email_code_expire_seconds // 60} 分钟内有效，请勿转发给他人。"
    )

    if settings.smtp_use_ssl:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)

