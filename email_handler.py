import smtplib
import imaplib
import ssl
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from constants import *

def send_email(
    host: str,
    port: int,
    subject: str,
    content: str,
    sender: str,
    password: str,
    recipients: str | list[str],
    attachments: list[tuple[str, str]] =[]
) -> bool:
    """Send email from sender to recipient with optional attachments.

    The list `attachments` is a list of tuples. Each tuple contains two strings,
    in the format: (`file_path`, `file_name`).

    Args:
        host: The name of the host domain
        port: The port number for the connection
        subject: The subject of the email
        content: The body message of the email
        sender: The email address to send from
        password: The password for the account belonging to `sender`
        recipient: The email address(es) to send to
        attachments: A list of files to attach
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    msg.attach(MIMEText(content))

    for file_path, file_name in attachments:
        try:
            f = open(file_path, 'rb')
            msg.attach(MIMEApplication(f.read(), Name=file_name))
            f.close()
        except Exception as e:
            print(f"email_handler.py: Exception: {e}")
    try:
        with smtplib.SMTP_SSL(host, port) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
    except:
        return False
    
    return True
