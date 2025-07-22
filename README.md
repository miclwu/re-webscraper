# re-webscraper

## Using the webscraper

Arguments (global variables in `webscraper.py`):
- `DATAFILE`: The CSV file where all URLs and other information is stored, input/output
- `FIELDNAMES`: The headers for the fields in the CSV file, currently requires `name`, `url`, `status`, and `checksum`
- `PHRASES`: The phrases used to check for fund `Closed` status
- `DELIM`: The delimiter uised to separate URLs within the `url` field in the CSV file
- `HEADERS`: The request headers sent when scraping

Run `webscraper.py` in the same directory as `DATAFILE`.

## python env

    python3 -m venv ENV_NAME

## pip dependencies

    pip install -r requirements.txt
