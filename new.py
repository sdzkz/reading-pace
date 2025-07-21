#!/usr/bin/env python3
"""
new.py – create a new book entry.
Usage: ./new.py
"""

import sqlite3

DB = 'project.db'

conn = sqlite3.connect(DB)
c = conn.cursor()

print()

title = input("(title) ").strip()
if not title:
    print()
    conn.close()
    exit(1)

try:
    pages = int(input("(total pages) "))
except ValueError:
    print("Pages must be an integer.")
    conn.close()
    exit(1)

c.execute("INSERT INTO books (title, number_of_pages) VALUES (?, ?)", (title, pages))
conn.commit()
book_id = c.lastrowid
print(f"Created book #{book_id}: {title} ({pages} pages)")
conn.close()
