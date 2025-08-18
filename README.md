# re-webscraper

## Webscraper Command Cheatsheet

| command 	| name           	| url                                                    	| status             	    |
|---------	|----------------	|--------------------------------------------------------	|--------------------	    |
| ADD     	| Fund name      	| URL 1<br><br>URL 1;;URL 2;; ... ;;URL N                	| Open<br><br>Closed 	    |
| MOD     	| Fund name      	| URL 1<br><br>URL 1;;URL 2;; ... ;;URL N<br><br>_EMPTY_ 	| Open<br><br>Closed 	    |
| DEL     	| Fund name      	| _EMPTY_                                                	| _EMPTY_            	    |
| REQ     	| funds<br>users 	| _EMPTY_                                                	| _EMPTY_            	    |
| REQB      | funds<br>users    | _EMPTY_                                                   | _EMPTY_                   |
| ADDU    	| User email     	| _EMPTY_                                                	| True, 1<br><br>False, 0  	|
| DELU    	| User email     	| _EMPTY_                                                	| _EMPTY_               	|
| BACKUP    | _EMPTY_           | _EMPTY_                                                   | _EMPTY_                   |
| RESTORE   | _EMPTY_           | _EMPTY_                                                   | _EMPTY_                   |

## Using the Webscraper

The webscraper is interfaced with via emails. All users (that are registered with the webscraper) will receive output from the webscraper. All privileged/admin users will be able to send commands to the webscraper via input files (.xlsx), and will be able to receive privileged data such as audit logs and full database tables. Users without admin privilege are **not** able to send commands to the webscraper.

### Command Structure

Commands are written in excel files (.xlsx), with each file containing 4 columns:
1. `command`: The command to execute. See the "Valid Commands" section below. Always required.
2. `name`: The name of the item (ie. a fund, table, or user email) targeted by the command. Always required.
3. `url`: The url(s) of the item (ie. fund url(s)). Required by add fund (`ADD`).
    - Multiple urls may be added in each cell of the `url` column. Separate each url using ";;" as a delimiter.
    - e.g. google.com and mail.google.com --> google.com;;mail.google.com
4. `status`: The status of the item (ie. fund status or user privilege). Required by add fund (`ADD`), modify fund (`MOD`), and add user (`ADDU`) commands.

If a certain command does not require a column to be filled, the cell may be left blank. However, the column **must** still exist in the excel file, **even if the file only contains one command.**

### Valid Commands

Manipulating `FUNDS_TABLE` (ie. "funds"):
- `ADD`: Add a fund to `FUNDS_TABLE`. Requires: `name`, `url`, and `status`
- `MOD`: Modify an existing fund in `FUNDS_TABLE`. Replaces fund url or status with `url`/`status`. The fund name CANNOT be modified, since it is used to identify which existing fund should be modified. Page history is deleted. Requires: `name` and `status`
- `DEL`: Delete an existing fund from `FUNDS_TABLE`. Requires: `name`

Manipulating `USERS_TABLE` (ie. "users"):
- `ADDU`: Add a user to `USERS_TABLE`. The user email is set by the `name` field, while the user privilege / admin status is set by `status`. Requires: `name` and `status`
- `DELU`: Delete an existing user from `USERS_TABLE`. Requires: `name`

Access command:
- `REQ`: Request all data from a table in `DATABASE`. The requested table is decided by the `name` field. Fetches the most up to date version of the requested table (ie. commands after `REQ` in the input file(s) will be executed **before** the requested table is sent). Requires: `name`
- `REQB`: Request all data from a table in the backup database `DATABASE_BACKUP`. Requires: `name`

Backup/restore commands:
- `BACKUP`: Save the current state of `DATABASE` to the backup database `DATABASE_BACKUP`.
- `RESTORE`: Load the backup `DATABASE_BACKUP` into the main `DATABASE`.

### Command Examples

| command 	| name 	| url 	| status 	| Explanation 	|
|---	|---	|---	|---	|---	|
| ADD 	| Google 	| google.com 	| Open 	| Add a fund named "Google" with one URL and status "Open". 	|
| ADD 	| Search Engines 	| google.com;;bing.com 	| Closed 	| Add a fund named "Search Engines" with two URLs and status "Closed". 	|
| MOD 	| Google 	| _EMPTY_ 	| Closed 	| Modify a fund named "Google", setting the "status" field to "Closed" and leaving the "url" field unchanged. 	|
| MOD 	| Search Engines 	| google.com 	| Closed 	| Modify a fund named "Search Engines", modifying "url" field and setting "status" field to "Closed". 	|
| DEL 	| Search Engines 	| _EMPTY_ 	| _EMPTY_ 	| Delete a fund named "Google". 	|
| REQ 	| funds 	| _EMPTY_ 	| _EMPTY_ 	| Request the table named "funds" from the database. 	|
| REQB  | users     | _EMPTY_   | _EMPTY_   | Request the table named "users" from the backup database. |
| ADDU 	| user@example1.test 	| _EMPTY_ 	| True 	| Add a user with admin privileges. 	|
| ADDU 	| user@example2.test 	| _EMPTY_ 	| False 	| Add a user with normal privileges. 	|
| DELU 	| user@example2.test 	| _EMPTY_ 	| _EMPTY_ 	| Delete a user with the matching email. 	|
| BACKUP | _EMPTY_  | _EMPTY_   | _EMPTY_   | Backup the database.  |
| RESTORE | _EMPTY_ | _EMPTY_   | _EMPTY_   | Restore the backup database.  |

### Understanding the Audit Log

| Message Header 	| Explanation 	|
|---	|---	|
| ADD, MOD, DEL, etc. 	| Successful execution of the corresponding command. 	|
| INPUT FILE ERROR 	| Input file(s) could not be located or parsed. 	|
| INPUT ERROR 	| A command was formatted incorrectly or could not be executed. 	|
| DATABASE ERROR 	| An error occurred while attempting to execute a database operation. 	|
| EMAIL HANDLER 	| Message from the email handler. 	|
| EMAIL HANDLER ERROR 	| An error occurred with the email handler. 	|
| INFO 	| An informational message. 	|
| ERROR 	| A general error message. Check message body to see why the error occurred. 	|
| WARNING 	| Appears right above an ADD, MOD, etc. message in the audit log. Indicates that the command below the warning was valid and was executed but there are potential issues that may result from the execution of the command. 	|

### Audit Log Examples

#### Example 1: Valid command execution

Initial state: empty database
Say the following commands are executed in the following order, and were sent to the webscraper in a single .xlsx file:

    cmd     name        url             status

    ADD     Fund 1      URL 1           Open
    MOD     Fund 1      URL 1;;URL 2    Closed
    ADD     Fund 2      URL 3           Closed
    DEL     Fund 2
    REQ     funds

The audit log would contain the following messages (assuming no page changes were detected):

    INFO: Input files: 1
    ADD: Fund 1
    MOD: Fund 1, URL 1;;URL 2, Closed
    ADD: Fund 2
    DEL: Fund 2
    REQ: Table "funds"
    INFO: Updated funds: 1/1
    INFO: Funds to check: 0/1

#### Example 2: Database Error

Say "Fund 1" already exists in the database, and the following command is executed:

    cmd     name       url       status

    ADD     Fund 1     URL 1     Open        

The following message would be printed in the audit log:

    DATABASE ERROR: ADD Fund 1: UNIQUE constraint failed: funds.name

Most "DATABASE ERROR" messages will occur because of a UNIQUE constraint. If you are getting an error message similar to this, either remove the offending item from the database before adding it, or use the `MOD` command.

#### Example 3: Input Error

Attempting to execute the following commands:

    cmd     name        url         status
    
    ADD     Fund 1                  Open
    ADD     Fund 2      URL 1
    ADD     Fund 3      URL 1       Wrong
    ADD                 URL 1       Open
            Fund 5      URL 1       Open
    DNE     Fund 6      URL 1       Open
    REQ     not_in_db
    
Results in the following messages in the audit log:

    INPUT ERROR: ADD Fund 1: Empty URL
    INPUT ERROR: ADD Fund 2: Invalid status: ""
    INPUT ERROR: ADD Fund 3: Invalid status: "Wrong"
    INPUT ERROR: ADD: Empty name
    INPUT ERROR: Invalid command: " Fund 5"
    INPUT ERROR: Invalid command: "DNE Fund 6"
    INPUT ERROR: REQ not_in_db: Table not found

Note that commands are checked from left to right in the sequence: command, name, url, status
For commands with multiple errors, only the first error is caught:

    cmd     name        url     status

    ADD     Fund 1

Resulting audit log message:

    INPUT ERROR: ADD Fund 1: Empty URL

#### Example 4: MOD Warning

Currently warnings are only issued under specific circumstances with the `MOD` command.

Say that there is an "Open" fund named "Fund 1" in the database. The webscraper detects a page change. A user checks the fund, sees it is now "Closed", and inputs a `MOD` command to edit "Fund 1". Before executing the `MOD` command, the webscraper checks "Fund 1" and detects another page change. It is possible that "Fund 1" is now "Open", but the `MOD` command will change "Fund 1" to "Closed". Thus, the webscraper writes a warning message to the audit log:

    WARNING: Potential change to fund "Fund 1" before MOD command
    MOD: Fund 1, URL 1, Closed

## File Overview

### main.py

The main file. Handles audit logging for email input. Handles email input/output using functions from `email_handler.py`. Calls `main()` from `webscraper.py` to handle web scraping and database management.

Dependencies: `webscraper.py`, `email_handler.py`, `utilities.py`, `constants.py`

### webscraper.py

Web scraping, parsing user input, database management, and audit logging. Takes in user inputs in the form of .xlsx files from `INFILE_DIR` and outputs funds that need to be checked or requested data to `OUTFILE_DIR`.

Main Function Args: sqlite3 connection, audit log file  
Dependencies: `utilities.py`, `constants.py`

### email_handler.py

Contains functions for sending emails, receiving emails, and parsing emails (to authenticate emails and download attachments).

Dependencies: `utilities.py`, `constants.py`

### utilities.py

Miscellaneous helper functions for database management, converting .xlsx files to records objects (a list of dicts), and file/directory management.

### constants.py

Contains constant, global variables for the webscraper.

### setup.py

Initializes sqlite3 database and tables `FUNDS_TABLE` and `USERS_TABLE`. Initializes `INFILE_DIR` and `OUTFILE_DIR`.

Dependencies: `utilities.py`, `constants.py`

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

## Database Information

The webscraper uses an sqlite3 database, called `DATABASE`.

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
