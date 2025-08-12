import smtplib
import imaplib
import ssl
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.message import EmailMessage
import sqlite3
from utilities import db_get_row
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
) -> None:
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

    with smtplib.SMTP_SSL(host, port) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

def receive_emails(
    host: str,
    port: str,
    recipient: str,
    password: str,
    mailbox: str ='INBOX',
    flag: str ='UNSEEN',
) -> list[EmailMessage]:
    mail = imaplib.IMAP4_SSL(host, port, ssl_context=ssl.create_default_context())
    mail.login(recipient, password)
    mail.select(mailbox)

    status, data = mail.search(None, flag)
    messages = []

    if status == 'OK':
        for num in data[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1], _class=EmailMessage)
            messages.append(msg)

            print('From:', msg['From'])
            print('Subject:', msg['Subject'])
            print('Date:', msg['Date'])
            print('Body:', msg.get_payload())
            print()

    mail.close()
    mail.logout()

    return messages

def parse_emails(
    conn: sqlite3.Connection,
    table: str,
    messages: list[EmailMessage],
    attachment_ext: str | None =None
) -> list[EmailMessage]:
    attachments = []
    for msg in messages:
        sender_addr = email.utils.parseaddr(msg['From'])[1]
        user = db_get_row(conn, table, ('email', 'admin'), key='email', val=sender_addr)
        if not user or user['admin'] == False:
            print('INPUT ERROR: Non-privileged user.')
            continue

        for att in msg.iter_attachments():
            fname = att.get_filename()
            root, ext = os.path.splitext(fname)
            if not attachment_ext or ext == attachment_ext:
                attachments.append(att)

    return attachments

def save_attachment(att, path):
    if os.path.isfile(path):
        raise FileExistsError(f"File already exists at \"{path}\"")
    
    with open(path, 'wb') as f:
        f.write(att.get_payload(decode=True))

