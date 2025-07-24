import sqlite3
from utilities import csv_to_dict

conn = sqlite3.connect("webscraper.db")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS funds")

cur.execute("""
    CREATE TABLE funds (
        id INTEGER NOT NULL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        url TEXT NOT NULL,
        status TEXT NOT NULL,
        checksum TEXT,
        access_failures INTEGER DEFAULT 0)"""
)

data = csv_to_dict("database_BACKUP.csv")

cur.executemany("INSERT INTO funds (name, url, status, checksum) VALUES (:name, :url, :status, :checksum)", data)
conn.commit()

res = cur.execute("SELECT name FROM funds")
print(res.fetchall())


res = cur.execute("SELECT name FROM sqlite_master")
print(res.fetchall())

conn.close()