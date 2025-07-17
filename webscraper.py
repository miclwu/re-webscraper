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
# - checksum checking for closed funds instead of only checking for phrase presence?
# - proxies
# - research ways to implement into current software or to send a notification of potential fund changes

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9"
}

PHRASES = ["not currently accepting"]
FIELDNAMES = ["name", "url", "status", "checksum"]

database = csv_to_dict('database.csv')

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
    for item in database:
        assert(item["name"])
        assert(item["url"])
        assert(item["status"] == "open" or item["status"] == "closed" or item["status"] == "check required")

        old_checksum = item["checksum"]
        
        soup = get_soup(item)

        if not soup:
            continue

        if (item["status"] == "open"):      # fund open

            checksum = hashlib.sha256(soup.body.encode('utf-8')).hexdigest()

            if (not old_checksum):
                item["checksum"] = checksum
                print(f'{item["name"]}, OPEN FUND: Adding new checksum.')
                continue

            if checksum != old_checksum:
                item["checksum"] = checksum
                item["status"] = "check required"
                print(f'{item["name"]}, OPEN FUND: Page change detected. Updating checksum. Check required.')
            else:
                print(f'{item["name"]}, OPEN FUND: Checksums match.')

        elif (item["status"] == "closed"):  # fund closed
            for p in PHRASES:
                tags = soup.body.find_all(string=re.compile(p))
                print(f'{item["name"]}, CLOSED FUND TAGS: {tags}')
                if len(tags) > 0:
                    print(f'{item["name"]}, CLOSED FUND: Still closed.')
                    break
            else:
                print(f'{item["name"]}, CLOSED FUND: Check required.')
                item["checksum"] = ""
        
        else:                               # check required
            print(f'{item["name"]}, CHECK FUND')
        
    dict_to_csv(database, 'database.csv', FIELDNAMES)

if __name__ == "__main__":
    main()
