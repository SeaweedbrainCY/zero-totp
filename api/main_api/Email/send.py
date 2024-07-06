import smtplib, ssl
from main_api.environment import conf
from main_api.environment import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_verification_email(email_reciever:str, token:str):# pragma: no cover
    if conf.features.emails.smtp_server == "" or conf.features.emails.smtp_port == None or conf.features.emails.smtp_username == "" or conf.features.emails.sender_password == "" or conf.features.emails.sender_address == "" or not conf.features.emails.require_email_validation :
        logging.error("Email configuration is not set. Please set the email configuration in the environment file.")
        raise Exception("Email configuration is not set. Please set the email configuration in the environment file.")
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify your email address"
    message["From"] = conf.features.emails.sender_address
    message["To"] = email_reciever

    text = f"""\
        Hi, 
        Thank you for signing up for Zero-TOTP. To secure your account, please confirm your email address using the following code:

        VERIFICATION CODE: {token}

        Use this code in the Zero-TOTP application to complete the verification process. The code is valid for 30 minutes.

        If you did not sign up for this account, please ignore this email.

        Have a safe and secure Zero-Trust journey!

        The Zero-TOTP Team
    """
    html = f"""\
<!DOCTYPE html>
<html>
    <body style="font-family: 'Arial', sans-serif; color: #16262E;">

    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #5AA9E6; border-radius: 10px;; color: #16262E;">
        <h2 style="color: #5AA9E6; ">Email Verification - Zero-TOTP</h2>
        <p>Thank you for signing up for Zero-TOTP. To secure your account, please confirm your email address using the following code:</p>

        <div style="border: 1px solid #FE6847; padding: 10px; border-radius: 5px; text-align: center; font-size: 24px; color: #16262E; margin-top: 20px;">
            <strong>VERIFICATION CODE: <span style="color: #FE6847;">{token}</span></strong>
        </div>

        <p>Use this code in the Zero-TOTP application to complete the verification process. The code is valid for 10 minutes.</p>

        <p>If you did not sign up for this account, please ignore this email.</p>

        <p>Have a safe and secure Zero-Trust journey!</p>

        <p>Best regards,<br> The Zero-TOTP Team</p>
    </div>

</body>
</html>
    """
    part1 = MIMEText(text, "plain", "utf-8")
    part2 = MIMEText(html, "html", "utf-8")

    message.attach(part1)
    message.attach(part2)
    with smtplib.SMTP(conf.features.emails.smtp_server, conf.features.emails.smtp_port) as server:
        server.connect(conf.features.emails.smtp_server, conf.features.emails.smtp_port)
        server.starttls()
        server.login(conf.features.emails.smtp_username, conf.features.emails.sender_password)
        server.sendmail(
            conf.features.emails.sender_address, email_reciever, message.as_string()
        )

def send_information_email(email_reciever:str, reason:str, date:str, ip:str): # pragma: no cover
    if conf.features.emails.smtp_server == "" or conf.features.emails.smtp_port == "" or conf.features.emails.smtp_username == "" or conf.features.emails.sender_password == "" or conf.features.emails.sender_address == "":
        logging.error("Email configuration is not set. Please set the email configuration in the environment file.")
        raise Exception("Email configuration is not set. Please set the email configuration in the environment file.")
    message = MIMEMultipart("alternative")
    message["Subject"] = reason
    message["From"] = conf.features.emails.sender_address
    message["To"] = email_reciever

    text = f"""\
        Hi, 
        We wanted to inform you that {reason}.

        Date: {date}
        IP: {ip}

        If you don't recognize this activity, please change your password immediately and contact us. 

        This is a security notification from Zero-TOTP. For safety reasons, you can't unsubscribe from these emails.

        Have a safe and secure Zero-Trust journey!

        The Zero-TOTP Team
    """
    html = f"""\
<!DOCTYPE html>
<html>
    <body style="font-family: 'Arial', sans-serif; color: #16262E;">

    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #5AA9E6; border-radius: 10px;; color: #16262E;">
        <h2 style="color: #5AA9E6; ">Hi,</h2>
        <p>We wanted to inform you that <strong><span style="color: #FE6847;">{reason}</span></strong></p>

        <ul>
            <li>Date: {date}</li>
            <li>IP: {ip}</li>
        </ul>

        <p><strong>If you don't recognize this activity, please change your password immediately and contact us.</strong></p>

        <p>This is a security notification from Zero-TOTP. For safety reasons, you can't unsubscribe from these emails.</p>

        <p>Have a safe and secure Zero-Trust journey!</p>

        <p>Best regards,<br> The Zero-TOTP Team</p>
    </div>

</body>
</html>
    """
    part1 = MIMEText(text, "plain", "utf-8")
    part2 = MIMEText(html, "html", "utf-8")

    message.attach(part1)
    message.attach(part2)
    with smtplib.SMTP(conf.features.emails.smtp_server, conf.features.emails.smtp_port) as server:
        server.connect(conf.features.emails.smtp_server, conf.features.emails.smtp_port)
        server.starttls()
        server.login(conf.features.emails.smtp_username,conf.features.emails.sender_password)
        server.sendmail(
            conf.features.emails.sender_address, email_reciever, message.as_string()
        )
