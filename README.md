# re-webscraper

## Using the webscraper

Arguments (global variables in `webscraper.py`):
- `DATABASE`: The .db file used to store data
- `FUNDS_TABLE`: The name of the table in `DATABASE` that stores fund data
- `INFILE`: The name of the input file
- `OUTFILE`: The name of the output file
- `FIELDNAMES`: The headers for the fields in the CSV file, currently requires `name`, `url`, `status`, and `checksum`
- `STATUS`: The accepted values for the field/column, `status`
- `DELIM`: The delimiter used to separate URLs within the `url` field in `DATABASE`, `INFILE`, and `OUTFILE`
- `HEADERS`: The request headers sent when scraping

Run `webscraper.py` in the same directory as `DATABASE`.

## python env

    python3 -m venv ENV_NAME

## pip dependencies

    pip install -r requirements.txt
