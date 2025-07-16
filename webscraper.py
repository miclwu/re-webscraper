from bs4 import BeautifulSoup
import requests
import json
import re
import hashlib

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9"
}

PHRASES = ["not currently accepting"]

with open('database.json', 'r') as infile:
    database = json.load(infile)

for item in database['funds']:
    assert(item["name"])
    assert(item["url"])
    assert(item["status"] == "open" or item["status"] == "closed" or item["status"] == "check required")

    old_checksum = item["checksum"]
    
    response = requests.get(item["url"], headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

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
