import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(receiver_email:str,token:str):
    sender_email = "usmanghanivhr1453@gmail.com"
    sender_password = "watejilfykndtqrp"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify Your HAAK Account"
    message["From"] = sender_email
    message["To"] = receiver_email

    verify_url = f"http://127.0.0.1:8000/users/verify?token={token}"

    html = f"""
    <html>
      <body>
        <h2>Welcome to HAAK!</h2>
        <p>You are one step away from completing your account registration.</p>
        <p>Please click the link below to verify your email address:</p>
        <a href="{verify_url}" style="padding: 10px 20px; background-color: #000; color: #fff; text-decoration: none;">Verify My Account</a>
      </body>
    </html>
    """
    part = MIMEText(html,"html")
    message.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as server:
        server.login(sender_email,sender_password)
        server.sendmail(sender_email,receiver_email,message.as_string())
