# re-webscraper

## Using the Webscraper

The webscraper is interfaced with via emails. All users (registered with the webscraper) will receive output from the webscraper. All privileged/admin users will be able to send commands to the webscraper via input files (.xlsx), and will be able to receive privileged data such as audit logs and full database tables.

### Command Structure

### Valid Commands

Manipulating `FUNDS_TABLE`:
- `ADD`: Add a fund to `FUNDS_TABLE`. Requires: `name`, `url`, and `status`
- `MOD`: Modify an existing fund in `FUNDS_TABLE`. Replaces fund url or status with `url`/`status`. The fund name CANNOT be modified, since it is used to identify which existing fund should be modified. Requires: `name` and `status`
- `DEL`: Delete an existing fund from `FUNDS_TABLE`. Requires: `name`

Manipulating `USERS_TABLE`:
- `ADDU`: Add a user to `USERS_TABLE`. The user email is set by the `name` field, while the user privilege / admin status is set by `status`. Requires: `name` and `status`
- `DELU`: Delete an existing user from `USERS_TABLE`. Requires: `name`

Access command:
- `REQ`: Request all data from a table in `DATABASE`. The requested table is decided by the `name` field. Requires: `name`

### TODO: Add examples

## File Overview

- `main.py`: The main file. Handles audit logging for email input. Handles email input/output using functions from `email_handler.py`. Calls `main()` from `webscraper.py` to handle web scraping and database management.
    - Dependencies: `webscraper.py`, `email_handler.py`, `utilities.py`, `constants.py`
- `webscraper.py`: Web scraping, parsing user input, database management, and audit logging. Takes in user inputs in the form of .xlsx files from `INFILE_DIR` and outputs funds that need to be checked or requested data to `OUTFILE_DIR`.
    - Main Function Args: sqlite3 connection, audit log file
    - Dependencies: `utilities.py`, `constants.py`.
- `email_handler.py`: Contains functions for sending emails, receiving emails, and parsing emails (to authenticate emails and download attachments).
    - Dependencies: `utilities.py`, `constants.py`
- `utilities.py`: Miscellaneous helper functions for database management, converting .xlsx files to records objects (a list of dicts), and file/directory management.
- `constants.py`: Contains constant, global variables for the webscraper.
- `setup.py`: Initializes sqlite3 database and tables `FUNDS_TABLE` and `USERS_TABLE`. Initializes `INFILE_DIR` and `OUTFILE_DIR`.
    - Dependencies: `utilities.py`, `constants.py`

## Constants (`constants.py`)

### General Constants

- `DATABASE`: The sqlite3 .db file used to store data
- `FUNDS_TABLE`: The name of the table in `DATABASE` that stores fund data
- `USERS_TABLE`: The name of the table in `DATABASE` that stores user emails and privilege status
- `FILE_EXT`: The file extension of the type of files to be used in input/output (.xlsx)
- `INFILE_DIR`: The directory to which user input files are saved by the email handler
- `INFILE_TEMPLATE`: The template name used for input files
- `OUTFILE_DIR`: The directory to which webscraper output files and the audit log are saved
- `OUTFILE_NAME`: The name of the webscraper output file (.xlsx file of funds to be checked and/or requested table data) when sending output to users
- `AUDITLOG_PATH`: The path to the audit log file
- `AUDITLOG_NAME`: The name of the audit log file

### Webscraper-specific Constants

- `OUTFILE_ADMIN_PATH`: The path to the webscraper output file for privileged users (may include requested table data)
- `OUTFILE_USER_PATH`: The path to the webscraper output file for non-privileged users (will not include requested table data)
- `DB_FUNDS_COLS`: A list of all the columns in the table `FUNDS_TABLE` in `DATABASE`
- `INPUT_COLS`: The list of required columns for user input files (.xlsx)
- `OUTPUT_COLS`: The list of columns included in the funds to be checked table of the webscraper output file
- `DELIM`: The delimiter used to separate multiple urls in a single field in input/outfile files. Also used in `FUNDS_TABLE` to separate checksums of multiple urls 
- `STATUSES`: The set of valid fund statuses (`OPEN`, `CLOSED`, `CHECK`)
- `OPEN`: The status assigned to open funds
- `CLOSED`: The status assigned to closed funds
- `CHECK`: The status assigned to funds requiring a manual user check
- `HTTP_GET_HEADERS`: The HTTP GET request headers used by the webscraper

### Email Handler Constants

- `EMAIL_ADDRESS`: The email address used to send emails to users
- `EMAIL_PASSWORD`: The password for `EMAIL_ADDRESS`
- `SMTP_HOST`: The host domain for SMTP (sending emails)
- `SMTP_PORT`: The port number for SMTP
- `IMAP_HOST`: The host domain for IMAP (receiving emails)
- `IMAP_PORT`: The port number for IMAP
- `EMAIL_SEND_SUBJECT`: The subject used when sending emails to users

## Database information

`webscraper.py` uses an sqlite3 database, called `DATABASE`.

`DATABASE` has 2 tables, `FUNDS_TABLE` and `USERS_TABLE`.

The table `FUNDS_TABLE` stores information about fund websites that will be scraped for page changes. The table contains the following columns:
- `id`: integer, primary key
- `name`: text, unique, not NULL; The name of the fund
- `url`: text, not NULL; The url(s) associated with a fund
- `status`: text, not NULL; The status of the fund
- `checksum`: text; The checksum(s) of each url associated with a fund
- `urls_to_check`: text; The url(s) that need to be checked
- `access_failures`: integer, default 0; The number of times the scraper has failed to access a url in a fund, resetting each time all urls in the fund are accessed successfully.

The table `USERS_TABLE` stores the emails and privilege of the users it may accept input from and will send output to. The table contains the following columns:
- `id`: integer, primary key
- `email`: text, unique, not NULL; The email address of the user
- `admin`: boolean, default False (0); The privilege of the user. True for privileged/admin status, False for non-privileged status. 

## python env

    python3 -m venv ENV_NAME

## pip dependencies

    pip install -r requirements.txt
