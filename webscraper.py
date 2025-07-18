from bs4 import BeautifulSoup
import requests
#import json
import re
import hashlib
import time
from requests.exceptions import HTTPError
from utilities import csv_to_dict, dict_to_csv

# TODO:
# - add way to add/remove to PHRASES, FIELDNAMES(?)
# - checksum specific element(s) instead of checking <body>
# - detect random binary data from response
# - proxies
# - research ways to implement into current software or to send a notification of potential fund changes

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9"
}

PHRASES = ["not currently accepting"]
FIELDNAMES = ["name", "url", "status", "checksum"]

OPEN = "Open"
CLOSED = "Closed"
CHECK = "Check Required"

DATAFILE = "database_FULL.csv"

def get_soup(item, retries= 5, backoff= 2):
    for attempt in range(retries):
        try:
            response = requests.get(item["url"], headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            return soup
        
        except HTTPError as e:
            if e.response.status_code == 412:
                print(f'Error 412. Skipping "{item["url"]}"...')
                return None
            wait_time = backoff ** attempt
            print(f"HTTP error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f'Failed to reach URL: {item["url"]}. Error: {e}. Skipping...')
            return None

def main():
    database = csv_to_dict(DATAFILE)

    for item in database:
        assert(item["name"])
        assert(item["url"])
        assert(item["status"] == OPEN or item["status"] == CLOSED or item["status"] == CHECK)

        old_checksum = item["checksum"]
        
        soup = get_soup(item)

        if not soup:
            continue
        
        checksum = hashlib.sha256(soup.body.encode('utf-8')).hexdigest()

        if not old_checksum:
                item["checksum"] = checksum
                print(f'{item["name"]}, {item["status"].upper()} FUND: Adding new checksum.')
                continue

        if item["status"] == OPEN:      # fund open
            if checksum != old_checksum:
                item["checksum"] = checksum
                item["status"] = CHECK
                print(f'{item["name"]}, OPEN FUND: Page change detected. Updating checksum. Check required.')
            else:
                print(f'{item["name"]}, OPEN FUND: Checksums match.')

        elif item["status"] == CLOSED:  # fund closed
            hasChecksumUpdated = False 

            if checksum != old_checksum:
                item["checksum"] = checksum
                hasChecksumUpdated = True
            
            for p in PHRASES:
                tags = soup.body.find_all(string=re.compile(p))
                print(f'{item["name"]}, CLOSED FUND TAGS: {tags}')
                if len(tags) > 0:
                    print(f'{item["name"]}, CLOSED FUND: Phrase found. Still closed.')
                    break
            else:
                if hasChecksumUpdated:
                    item["status"] = CHECK
                    print(f'{item["name"]}, CLOSED FUND: Page change detected. Updating checksum. Check required.')
                else:
                    print(f'{item["name"]}, CLOSED FUND: Phrase not found. Checksums match. Still closed.')
        
        else:                               # check required
            print(f'{item["name"]}, CHECK FUND: Check required.', end='')
            if checksum != old_checksum:
                item["checksum"] = checksum
                print(f' Updating checksum.', end='')
            print('')
        
    dict_to_csv(database, DATAFILE, FIELDNAMES)

if __name__ == "__main__":
    main()
