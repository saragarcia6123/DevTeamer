import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_verification_email(email: str, link: str):
    msg = EmailMessage()
    msg['Subject'] = 'Verify your email address'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    
    # Plain text fallback
    msg.set_content(f"Click this link to verify your email: {link}")
    
    msg.add_alternative(f"""
    <html>
      <body>
        <p>Click the link below to verify your email:</p>
        <p><a href="{link}">{link}</a></p>
      </body>
    </html>
    """, subtype='html')
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
