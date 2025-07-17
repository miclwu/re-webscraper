import csv
import json

def csv_to_dict(infile):
    data = []
    with open(infile, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def dict_to_csv(data, outfile, fieldnames):
    with open(outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames)
        
        writer.writeheader()
        writer.writerows([row for row in data])

def json_to_dict(infile):
    with open(infile, 'r') as f:
        dictobj = json.load(f)
    return dictobj

def dict_to_json(dictobj, outfile, indent=4):
    with open(outfile, 'w') as f:
        json.dump(dictobj, f, indent=indent)

