#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect('reading.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS books 
             (id INTEGER PRIMARY KEY, title TEXT, number_of_pages INTEGER)''')
c.execute("PRAGMA table_info(books)")
columns = [col[1] for col in c.fetchall()]
if 'amidst' not in columns:
    c.execute("ALTER TABLE books ADD COLUMN amidst INTEGER DEFAULT 0")
conn.commit()
conn.close()
