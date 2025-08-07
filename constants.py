import os

# WEBSCRAPER CONSTANTS

DATABASE = 'test.db'
FUNDS_TABLE = 'funds'

INFILE_DIR = 'inputs_TEST'
INFILE_TEMPLATE  = 'input_X.csv'

OUTFILE_PATH = 'outputs/checkfunds.xlsx'
OUTFILE_NAME = 'checkfunds.xlsx'
AUDITLOG_PATH = 'outputs/auditlog.txt'
AUDITLOG_NAME = 'auditlog.txt'

INPUT_COLS = ('command', 'name', 'url', 'status')
OUTPUT_COLS = ('name', 'url', 'status', 'urls_to_check')

DELIM = ';;'

OPEN = 'Open'
CLOSED = 'Closed'
CHECK = 'Check Required'

STATUSES = (OPEN, CLOSED, CHECK)

HTTP_GET_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
}

# EMAIL HANDLER CONSTANTS

EMAIL_ADDRESS = os.environ['EMAIL_USER']
EMAIL_PASSWORD = os.environ['EMAIL_PASS']
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 465
IMAP_HOST = 'imap.gmail.com'
IMAP_PORT = 993
