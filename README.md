# re-webscraper

## Using the webscraper

Arguments (global variables in `webscraper.py`):
- `DATABASE`: The .db file used to store data
- `FUNDS_TABLE`: The name of the table in `DATABASE` that stores fund data
- `INFILE_DIR`: The name of the directory storing input files
- `INFILE_TEMPLATE`: The template name for input files, with `X`s representing digits (e.g. input_X --> input_31)
- `OUTFILE`: The name of the output file
- `AUDITLOG`: The name of the audit log file
- `INPUT_COLS`: The column names of the input file(s)
- `OUTPUT_COLS`: The column names of the output file
- `OPEN`: The string representing the OPEN status
- `CLOSED`: The string representing the CLOSED status
- `CHECK`: The string representing the CHECK REQUIRED status
- `STATUSES`: The accepted values for the field/column, `status`
- `DELIM`: The delimiter used to separate URLs within the `url` field in `DATABASE`, `INFILE`, and `OUTFILE`
- `HEADERS`: The request headers sent when scraping

Run `webscraper.py` in the same directory as `DATABASE`, `INFILE_DIR`, and `AUDITLOG`.

## Database information

`webscraper.py` uses an sqlite3 database, called `DATABASE`.

The database contains the following columns:
- `id`: integer, primary key
- `name`: text, unique, not NULL; The name of the fund
- `url`: text, not NULL; The url(s) associated with a fund
- `status`: text, not NULL; The status of the fund
- `checksum`: text; The checksum(s) of each url associated with a fund
- `urls_to_check`: text; The url(s) that need to be checked
- `access_failures`: integer, default 0; The number of times the scraper has failed to access a url in a fund, resetting each time all urls in the fund are accessed successfully.

## python env

    python3 -m venv ENV_NAME

## pip dependencies

    pip install -r requirements.txt
