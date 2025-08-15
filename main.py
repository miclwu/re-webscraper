from webscraper import main as webscraper_main
import email_handler as mail
import utilities as util
import sqlite3
import os
from constants import *

def main() -> None:
    """Handle incoming emails, pass inputs to `webscraper` main function, and send outputs via email.

    Use functions from `webscraper.py`, `email_handler.py`, and `utilities.py`. Initialize `conn`
    (type sqlite3.Connection) and `auditlog` (type TextIOWrapper) for use in submodule functions.
    """
    util.clean_dir(INFILE_DIR)
    util.clean_dir(OUTFILE_DIR)

    conn = sqlite3.connect(DATABASE)

    auditlog = open(AUDITLOG_PATH, 'w')
    auditlog.write('BEGIN EMAIL HANDLER\n-----\n\n')
    messages = mail.receive_emails(IMAP_HOST, IMAP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD)
    attachments = mail.parse_emails(conn, USERS_TABLE, messages, attachment_ext=FILE_EXT)
    
    if len(attachments) == 0:
        auditlog.write('EMAIL HANDLER: No inputs received\n\n')

    for i in range(len(attachments)):
        path = f"{INFILE_DIR}/{INFILE_TEMPLATE.replace('X', str(i+1))}"
        try:
            mail.save_attachment(attachments[i], path)
        except Exception as e:
            auditlog.write(f"EMAIL HANDLER ERROR: Unable to save attachment. Exception: {e}\n\n")
        else:
            auditlog.write(f"EMAIL HANDLER: Successfully saved input file at {path}\n\n")

    auditlog.write('-----\nEND EMAIL HANDLER\n\n\nBEGIN WEB SCRAPER\n-----\n\n')

    webscraper_main(conn, auditlog)

    auditlog.write('-----\nEND WEB SCRAPER\n\n\n')
    auditlog.close()

    recipients = util.dbtable_to_records(conn, USERS_TABLE)
    conn.close()

    recipients_admin = set(admin['email'] for admin in recipients if admin['admin'] == True)
    recipients_users = set(user['email'] for user in recipients if user['admin'] == False)

    outfile_admin_exists = os.path.isfile(OUTFILE_ADMIN_PATH)
    outfile_user_exists = os.path.isfile(OUTFILE_USER_PATH)

    # Prepare and send email to admin users

    attachments = [(AUDITLOG_PATH, AUDITLOG_NAME)]
    body_msg = 'No funds to check today.'

    if recipients_admin:
        if outfile_admin_exists:
            attachments.insert(0, (OUTFILE_ADMIN_PATH, OUTFILE_NAME))
            body_msg = 'Funds to check (or table request) attached.'
        elif outfile_user_exists:
            attachments.insert(0, (OUTFILE_USER_PATH, OUTFILE_NAME))
            body_msg = 'Funds to check attached.'
        
        try:
            mail.send_email(
                SMTP_HOST, SMTP_PORT,
                EMAIL_SEND_SUBJECT, body_msg,
                EMAIL_ADDRESS, EMAIL_PASSWORD,
                ', '.join(recipients_admin), attachments
            )
        except Exception as e:
            print(f"Failed to send email to admin users. Exception: {e}")

    # Prepare and send email to normal users

    attachments = []
    body_msg = 'No funds to check today.'

    if recipients_users:
        if outfile_user_exists:
            attachments.append((OUTFILE_USER_PATH, OUTFILE_NAME))
            body_msg = 'Funds to check attached.'
        
        try:
            mail.send_email(
                SMTP_HOST, SMTP_PORT,
                EMAIL_SEND_SUBJECT, body_msg,
                EMAIL_ADDRESS, EMAIL_PASSWORD,
                ', '.join(recipients_users), attachments
            )
        except Exception as e:
            print(f"Failed to send email to regular users. Exception: {e}")

if __name__ == '__main__':
    main()