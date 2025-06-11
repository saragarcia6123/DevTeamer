import smtplib
from email.message import EmailMessage

from config import Config

config = Config()


def send_email(msg: EmailMessage):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        smtp.send_message(msg)


def send_verification_email(email: str, link: str):
    msg = EmailMessage()
    msg['Subject'] = 'DevTeamer - Verify your email address'
    msg['From'] = config.EMAIL_ADDRESS
    msg['To'] = email

    msg.set_content(f"""
    Click the link below to verify your email:

    {link}

    If you didn’t request this, you can safely ignore this email.
    """)

    msg.add_alternative(f"""
    <html>
      <body>
        <p>Click the link below to verify your email:</p>
        <p><a href="{link}">{link}</a></p>
        <p>If you didn’t request this, you can safely ignore this email.</p>
      </body>
    </html>
    """, subtype='html')

    send_email(msg)


def send_2fa_email(email: str, link: str):
    msg = EmailMessage()
    msg['Subject'] = 'DevTeamer - Confirm Your Login'
    msg['From'] = config.EMAIL_ADDRESS
    msg['To'] = email

    msg.set_content(f"""
    We received a request to log in to your account.

    To confirm it's you, click the link below:

    {link}

    If you didn’t request this, you can safely ignore this email.
    """)

    msg.add_alternative(f"""
    <html>
      <body>
        <p>We received a request to log in to your account.</p>
        <p>To confirm it's you, click the link below:</p>
        <p><a href="{link}">Confirm Login</a></p>
        <p>If you didn’t request this, you can safely ignore this email.</p>
      </body>
    </html>
    """, subtype='html')

    send_email(msg)
