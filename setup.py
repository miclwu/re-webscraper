import sqlite3
from utilities import csv_to_records
from constants import DATABASE, EMAIL_ADDRESS
from typing import Any

def init_table_funds(
    conn: sqlite3.Connection
) -> None:
    """Initialize `funds` table in database

    Args:
        conn: An open connection to an sqlite3 database
    """
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS funds")
    cur.execute(
    """CREATE TABLE funds (
        id INTEGER NOT NULL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        url TEXT NOT NULL,
        status TEXT NOT NULL,
        checksum TEXT,
        urls_to_check TEXT,
        access_failures TINYINT DEFAULT 0)
    """
    )
    conn.commit()

def init_table_users(
    conn: sqlite3.Connection
) -> None:
    """Initialize `users` table in database

    Args:
        conn: An open connection to an sqlite3 database
    """
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute(
    """CREATE TABLE users (
        id INTEGER NOT NULL PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        admin BOOL DEFAULT 0)
    """
    )
    conn.commit()

def add_user(
    conn: sqlite3.Connection,
    email: str,
    admin: bool
) -> None:
    """Add user to `users` table in database.

    Args:
        conn: An open connection to an sqlite3 database
        email: The email of the user to add
        admin: The privilege of the user; `True` if admin, `False` otherwise
    """
    cur = conn.cursor()
    cur.execute('INSERT INTO users (email, admin) VALUES (?, ?)', (email, admin))
    cur.commit()

def add_funds(
    conn: sqlite3.Connection,
    records: list[dict[str, Any]]
) -> None:
    """Add funds from `records` object to `funds` table in database.

    Args:
        conn: An open connection to an sqlite3 database
        records: A list of dicts, with each dict representing a row in database
    """
    cur = conn.cursor()
    cur.executemany("INSERT INTO funds (name, url, status, checksum) VALUES (:name, :url, :status, :checksum)", records)
    conn.commit()

if __name__ == '__main__':
    conn = sqlite3.connect(DATABASE)
    init_table_users(conn)
    add_user(conn, EMAIL_ADDRESS, True)
    conn.close()