import smtplib, ssl
import environment 
from environment import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_verification_email(email_reciever:str, token:str):# pragma: no cover
    if environment.email_smtp_server == "" or environment.email_smtp_port == "" or environment.email_smtp_username == "" or environment.email_sender_password == "" or environment.email_sender_address == "" or not environment.require_email_validation:
        logging.error("Email configuration is not set. Please set the email configuration in the environment file.")
        raise Exception("Email configuration is not set. Please set the email configuration in the environment file.")
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify your email address"
    message["From"] = environment.email_sender_address
    message["To"] = email_reciever

    text = f"""\
        Hi, 
        Thank you for signing up for Zero-TOTP. To secure your account, please confirm your email address using the following code:

        VERIFICATION CODE: {token}

        Use this code in the Zero-TOTP application to complete the verification process. The code is valid for 10 minutes.

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
    with smtplib.SMTP(environment.email_smtp_server, environment.email_smtp_port) as server:
        server.connect(environment.email_smtp_server, environment.email_smtp_port)
        server.starttls()
        server.login(environment.email_smtp_username, environment.email_sender_password)
        server.sendmail(
            environment.email_sender_address, email_reciever, message.as_string()
        )

