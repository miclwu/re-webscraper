from bs4 import BeautifulSoup
import requests
import json
import re
import hashlib
import time
from requests.exceptions import HTTPError

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9"
}

PHRASES = ["not currently accepting"]

MAX_RETRIES = 5
BACKOFF = 2

with open('database.json', 'r') as infile:
    database = json.load(infile)

for item in database['funds']:
    assert(item["name"])
    assert(item["url"])
    assert(item["status"] == "open" or item["status"] == "closed" or item["status"] == "check required")

    old_checksum = item["checksum"]
    
    skip = False
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(item["url"], headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
        except HTTPError as e:
            if e.response.status_code == 412:
                print(f'Error 412. Skipping "{item["url"]}"...')
                skip = True
                break
            wait_time = BACKOFF ** attempt
            print(f"HTTP error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except Exception as e:
            print(f'Failed to reach URL: {item["url"]}. Error: {e}. Skipping...')
            skip = True
            break
    
    if skip:
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
    
with open('database.json', 'w') as outfile:
        json.dump(database, outfile, indent=4)
