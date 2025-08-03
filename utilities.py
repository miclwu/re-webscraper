import csv
import pandas as pd
import numpy as np
import json

class InvalidInputError(ValueError):
    """Errors raised for invalid input"""
    pass

def db_validate_table(conn, table):
    cur = conn.cursor()
    res = cur.execute('SELECT name FROM sqlite_master')
    if (table,) not in res.fetchall():
        raise InvalidInputError('Table not found')

def db_validate_cols(conn, table, cols):
    cur = conn.cursor()
    res = cur.execute(f"PRAGMA table_info({table})")
    db_cols = [colinfo[1] for colinfo in res.fetchall()]
    for c in cols:
        if c not in db_cols:
            raise InvalidInputError(f"Invalid field name: {c}")

# from https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory
def db_dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def dbtable_to_records(conn, table):
    records = []
    cur = conn.cursor()
    res = cur.execute('SELECT name FROM sqlite_master')
    if (table,) not in res.fetchall():
        conn.close()
        raise InvalidInputError(f"Table '{table}' not found")
    
    cur.row_factory = db_dict_factory
    cur.execute(f"SELECT * FROM {table}")

    for row in cur:
        records.append(row)
    return records

def records_update_dbtable(conn, table, cols, records):
    cur = conn.cursor()
    db_validate_table(conn, table)
    db_validate_cols(conn, table, cols)

    updates = ''
    for c in cols:
        updates += f"{c} = :{c}, "
    updates = updates.rstrip(', ')
    for row in records:
        cur.execute(f"UPDATE {table} SET {updates} WHERE id = :id", row)
    conn.commit()

def db_get_row(conn, table, cols, identifier_val, identifier_key='name'):
    cur = conn.cursor()
    cur.row_factory = db_dict_factory
    fieldstr = ', '.join(cols)
    res = cur.execute(f"SELECT {fieldstr} FROM {table} WHERE {identifier_key} = ?", (identifier_val,))
    return res.fetchone()

def db_insert(conn, table, dictobj):
    cur = conn.cursor()
    keystr = ''
    valstr = ''
    for key in dictobj.keys():
        keystr += f"{key}, "
        valstr += f":{key}, "
    keystr = keystr.rstrip(', ')
    valstr = valstr.rstrip(', ')

    cur.execute(f"INSERT INTO {table} ({keystr}) VALUES ({valstr})", dictobj)
    conn.commit()

def db_delete(conn, table, key, val):
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE {key} = ?", (val, ))
    conn.commit()

def db_update(conn, table, dictobj, identifier_index=0):
    cur = conn.cursor()
    updatestr = ''
    for key in dictobj.keys():
        updatestr += f"{key} = :{key}, "
    updatestr = updatestr.rstrip(", ")
    identifier = list(dictobj.keys())[identifier_index]
    cur.execute(f"UPDATE {table} SET {updatestr} WHERE {identifier} = :{identifier}", dictobj)
    conn.commit()

def xlsx_to_records(infile, usecols=None):
    df = pd.read_excel(infile, usecols=usecols)
    df.replace(np.nan, None, inplace=True)
    return df.to_dict(orient='records')

def records_to_xlsx(records, outfile, usecols=None):
    df = pd.DataFrame.from_records(records)
    df.to_excel(outfile, columns=usecols, index=False)

def prune_records(records, usecols):
    rcpy = []
    for row in records:
        dictcpy = dict()
        for key in row:
            if key in usecols:
                dictcpy[key] = row[key]
        rcpy.append(dictcpy)
    return rcpy

def csv_to_records(infile):
    records = []
    with open(infile, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in row:
                if row[key] == '':
                    row[key] = None
            records.append(row)
    return records

def records_to_csv(records, outfile, usecols=None):
    if usecols:
        records = prune_records(records, usecols)
    
    with open(outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, usecols)
        writer.writeheader()
        writer.writerows([row for row in records])

def csv_clear_field(infile, outfile, usecols, field):
    records = csv_to_records(infile)
    for item in records:
        item[field] = None
    records_to_csv(records, outfile, usecols=usecols)

def json_to_dict(infile):
    with open(infile, 'r') as f:
        dictobj = json.load(f)
    return dictobj

def dict_to_json(dictobj, outfile, indent=4):
    with open(outfile, 'w') as f:
        json.dump(dictobj, f, indent=indent)
