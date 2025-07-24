import sqlite3
import csv
import json

class InvalidInputError(ValueError):
    """Errors raised for invalid input"""
    pass

# from https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory
def db_dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def dbtable_to_dict(database, table):
    data = []
    conn = sqlite3.connect(f"file:{database}?mode=ro", uri=True)
    cur = conn.cursor()
    res = cur.execute("SELECT name FROM sqlite_master")
    if (table,) not in res.fetchall():
        conn.close()
        raise InvalidInputError(f"Table '{table}' not found")
    
    cur.row_factory = db_dict_factory
    cur.execute(f"SELECT * FROM {table}")

    for row in cur:
        data.append(row)

    conn.close()
    return data

def dict_update_dbtable(data, database, table, fieldnames):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    res = cur.execute("SELECT name FROM sqlite_master")
    if (table,) not in res.fetchall():
        conn.close()
        raise InvalidInputError("Table not found")
    res = cur.execute(f"PRAGMA table_info({table})")
    db_fieldnames = [colinfo[1] for colinfo in res.fetchall()]
    for field in fieldnames:
        if field not in db_fieldnames:
            conn.close()
            raise InvalidInputError(f"Invalid field name: {field}")

    updates = ""
    for field in fieldnames:
        updates += f", {field} = ?"
    updates = updates.lstrip(", ")
    for row in data:
        params = tuple([row[field] for field in fieldnames] + [row["id"]])
        cur.execute(f"UPDATE {table} SET {updates} WHERE id = ?", params)
    conn.commit()
    conn.close()

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

def csv_clear_field(infile, outfile, fieldnames, field):
    data = csv_to_dict(infile)
    for item in data:
        item[field] = ""
    dict_to_csv(data, outfile, fieldnames)

def json_to_dict(infile):
    with open(infile, 'r') as f:
        dictobj = json.load(f)
    return dictobj

def dict_to_json(dictobj, outfile, indent=4):
    with open(outfile, 'w') as f:
        json.dump(dictobj, f, indent=indent)
