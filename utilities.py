import csv
import pandas as pd
import numpy as np
import sqlite3
import os
from typing import *

class InvalidInputError(ValueError):
    """Exception to be raised when database functions are passed invalid input."""
    pass

def db_validate_table(
    conn: sqlite3.Connection,
    table: str
) -> None:
    """Check if `table` is in the database opened via `conn` and raise `InvalidInputError` if not.

    Args:
        conn: An open connection to an sqlite3 database
        table: The name of a table that may be in the database
    Raises:
        InvalidInputError: `table` is not in database opened via `conn` 
    """
    cur = conn.cursor()
    res = cur.execute('SELECT name FROM sqlite_master')
    if (table,) not in res.fetchall():
        raise InvalidInputError('Table not found')

def db_validate_cols(
    conn: sqlite3.Connection,
    table: str,
    cols: list | tuple | set
) -> None:
    """Check if each column in `cols` is present in `table`.

    Args:
        conn: An open connection to an sqlite3 database
        table: The name of a table that is assumed to be in the database
        cols: The list of columns to be validated
    Raises:
        InvalidInputError: Any column in `cols` is not present in `table`
    """
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

def dbtable_to_records(
    conn: sqlite3.Connection,
    table: str
) -> list[dict[str, Any]]:
    """Convert a database table to a records (list of dicts) object.

    Args:
        conn: An open connection to an sqlite3 database
        table: The name of a table in the database
    Returns:
        records: A list of dicts, each dict representing a row in `table`
    """
    cur = conn.cursor()
    db_validate_table(conn, table)
    
    cur.row_factory = db_dict_factory
    cur.execute(f"SELECT * FROM {table}")

    records = []
    for row in cur:
        records.append(row)
    return records

def records_update_dbtable(
    conn: sqlite3.Connection,
    table: str,
    cols: list | tuple | set,
    records: list[dict[str, Any]]
) -> None:
    """Update `table` in the database using `records`.

    Replace each row in `table` with a row in `records`, if row ids match.
    Only updates the columns of each row listed in `cols`.

    Args:
        conn: An open connection to an sqlite3 database
        table: The name of a table in the database
        cols: The list of columns to be updated
        records: The incoming data, where each dict represents a row to be updated
    """
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

def db_get_row(
    conn: sqlite3.Connection,
    table: str,
    cols: list | tuple | set,
    key: str,
    val: Any,
) -> dict[str, Any]:
    """Fetch certain columns of a row from `table` based on an identifier key-value pair.

    Args:
        conn: An open connection to an sqlite3 database
        table: The name of a table in the database
        cols: The list of columns to be fetched from the fetched row
        key: The column that `val` belongs to
        val: The value matched to a row in `table`
    Returns:
        A dict representing the fetched row from `table`.
    """
    cur = conn.cursor()
    cur.row_factory = db_dict_factory
    fieldstr = ', '.join(cols)
    res = cur.execute(f"SELECT {fieldstr} FROM {table} WHERE {key} = ?", (val,))
    return res.fetchone()

def db_insert(
    conn: sqlite3.Connection,
    table: str,
    row: dict[str, Any]
) -> None:
    """Insert `row` into `table`.

    If `table` requires certain columns to not be NULL, then `row` should contain
    those columns. Additionally, `row` need not contain columns that can be NULL.

    Args:
        conn: An open connection to an sqlite3 database
        table: The name of a table in the database
        row: A dict representing a row to be added to `table`
    """
    cur = conn.cursor()
    keystr = ''
    valstr = ''
    for key in row.keys():
        keystr += f"{key}, "
        valstr += f":{key}, "
    keystr = keystr.rstrip(', ')
    valstr = valstr.rstrip(', ')

    cur.execute(f"INSERT INTO {table} ({keystr}) VALUES ({valstr})", row)
    conn.commit()

def db_delete(
    conn: sqlite3.Connection,
    table: str,
    key: str,
    val: Any
) -> None:
    """Delete the row from `table` matched by the identifier key-value pair.

    Args:
        conn: An open connection to an sqlite3 database
        table: The name of a table in the database
        key: The column that `val` belongs to
        val: The value matched to a row in `table`
    """
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE {key} = ?", (val, ))
    conn.commit()

def db_update(
    conn: sqlite3.Connection,
    table: str,
    row: dict[str, Any],
    key: str
) -> None:
    """Update a specific row in `table`.

    Matches `row` to a row in `table` using the key-value pair of
    `key`: `row[key]`. Replace each column
    of the matched row in `table` with the corresponding column
    in `row`.

    Args:
        conn: An open connection to an sqlite3 database
        table: The name of a table in the database
        row: A dict representing the new columns of a row in `table`
        key: The column used to match `row` to a row in `table`
    """
    cur = conn.cursor()
    updatestr = ''
    for key in row.keys():
        updatestr += f"{key} = :{key}, "
    updatestr = updatestr.rstrip(", ")
    cur.execute(f"UPDATE {table} SET {updatestr} WHERE {key} = :{key}", row)
    conn.commit()

def xlsx_to_records(
    infile: str,
    usecols: list | tuple | set | None =None
) -> list[dict[str, Any]]:
    """Convert the contents of a .xlsx file to records (list of dicts).

    Args:
        infile: The name of the .xlsx file to be parsed
        usecols: The list of columns to be included in the output `records`
    Returns:
        records: A list of dicts, each dict representing a row of `infile`
    """
    df = pd.read_excel(infile, usecols=usecols)
    df.replace(np.nan, None, inplace=True)
    return df.to_dict(orient='records')

def records_to_xlsx(
    records: list[dict[str, Any]],
    out: Any,
    usecols: list | tuple | set | None =None,
    sheet_name: str ='Sheet 1'
) -> None:
    """Write records (list of dicts) to an .xlsx file.

    Args:
        records: A list of dicts, each dict representing a row in a table
        out: File path (.xlsx) or existing ExcelWriter to write to
        usecols: The list of columns to be included in `outfile`
    """
    df = pd.DataFrame.from_records(records)
    df.to_excel(out, columns=usecols, sheet_name=sheet_name, index=False)

def prune_records(
    records: list[dict[str, Any]],
    usecols: list | tuple | set | None =None
) -> list[dict[str, Any]]:
    """Remove key-value pairs from each dict in `records` if the key is not in `usecols`.
    
    Args:
        records: A list of dicts, each dict representing a row in a table
        usecols: The columns of the output (pruned) `records` object
    Returns:
        A pruned `records` object, with only the columns in `usecols`
    """
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

def clean_dir(
    path: str
) -> None:
    """Remove all files in directory pointed to by `path`.

    Args:
        path: The path to the directory to be cleaned
    """
    files = [f"{path}/{f}" for f in os.listdir(path) if os.path.isfile(f"{path}/{f}")]
    for fpath in files:
        os.remove(fpath)
