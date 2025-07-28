#!/usr/bin/env python3
"""
check.py – inspect progress for an existing book.
No longer creates new books; use new.py for that.
"""

import sqlite3
from datetime import datetime, timedelta
import calendar
import sys

DB = 'project.db'

# ---------- helpers ----------------------------------------------------------
def get_month_end(dt, months_ahead=0):
    month = dt.month + months_ahead
    year = dt.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    _, last_day = calendar.monthrange(year, month)
    return datetime(year, month, last_day)

def calculate_pages_needed(current_page, total_pages, deadline):
    remaining = total_pages - current_page
    if remaining <= 0:
        return 0
    days_left = (deadline - datetime.now()).days + 1
    return remaining / max(1, days_left)

def swap_ids(conn, id1, id2):
    c = conn.cursor()
    c.execute("UPDATE books SET id = -1 WHERE id = ?", (id1,))
    c.execute("UPDATE books SET id = ? WHERE id = ?", (id1, id2))
    c.execute("UPDATE books SET id = ? WHERE id = -1", (id2,))
    conn.commit()

# ---------- CLI handling -----------------------------------------------------
print()

if '--swap' in sys.argv:
    try:
        idx = sys.argv.index('--swap')
        id1, id2 = map(int, sys.argv[idx + 1 : idx + 3])
        conn = sqlite3.connect(DB)
        swap_ids(conn, id1, id2)
        conn.close()
        sys.exit(0)
    except (ValueError, IndexError):
        print("Usage: ./check.py --swap ID1 ID2")
        sys.exit(1)

show_all = '--all' in sys.argv
bid_arg = None
for arg in sys.argv[1:]:
    if arg.isdigit():
        bid_arg = int(arg)
        break

conn = sqlite3.connect(DB)
c = conn.cursor()

# ---------- select book ------------------------------------------------------
if bid_arg is not None:
    c.execute("SELECT id, title, number_of_pages FROM books WHERE id=?", (bid_arg,))
    book = c.fetchone()
    if not book:
        print(f"Book ID {bid_arg} not found.")
        print()
        conn.close()
        sys.exit(1)
    bid, title, total_pages = book
    print(f"{title} ({total_pages} pages)")
else:
    if show_all:
        c.execute("SELECT id, title, number_of_pages FROM books")
    else:
        c.execute("SELECT id, title, number_of_pages FROM books WHERE amidst=1")
    books = c.fetchall()
    if not books:
        print("No books found.")
        conn.close()
        sys.exit(0)

    for bid, title, total_pages in books:
        print(f"{bid}: {title} ({total_pages} pages)")

    try:
        bid = int(input("\n: "))
        print()
        c.execute("SELECT id FROM books WHERE id=?", (bid,))
        if c.fetchone() is None:
            raise ValueError
    except ValueError:
        print()
        conn.close()
        sys.exit(1)

# ---------- update “amidst” flag ---------------------------------------------
if bid_arg is not None:
    print()
    amidst_input = input("(amidst) ").strip().lower()
    if amidst_input == 'y':
        c.execute("UPDATE books SET amidst=1 WHERE id=?", (bid,))
    elif amidst_input == 'n':
        c.execute("UPDATE books SET amidst=0 WHERE id=?", (bid,))
    conn.commit()

# ---------- progress input ---------------------------------------------------
c.execute("SELECT number_of_pages FROM books WHERE id=?", (bid,))
total_pages = c.fetchone()[0]

try:
    current_page = int(input("(on page) "))
except ValueError:
    current_page = 0

target_input = input("(target MM-DD) ").strip()
now = datetime.now()

print()

# ---------- deadlines & output -----------------------------------------------
if target_input:
    try:
        month, day = map(int, target_input.split('-'))
        current_year = now.year
        tentative_date = datetime(current_year, month, day)
        if tentative_date.date() < now.date():
            tentative_date = datetime(current_year + 1, month, day)
        deadlines = [tentative_date]
    except ValueError:
        print("Invalid date. Using default targets.")
        deadlines = [get_month_end(now, i) for i in [0, 1, 2]]
else:
    deadlines = [get_month_end(now, i) for i in [0, 1, 2]]

seen_dates = set()
for deadline in deadlines:
    ppd = calculate_pages_needed(current_page, total_pages, deadline)
    if ppd <= 0:
        continue
    if ppd < 1:
        remaining = total_pages - current_page
        days_needed = remaining
        finish_date = datetime.now() + timedelta(days=days_needed - 1)
        date_str = finish_date.strftime('%m-%d')
        if date_str in seen_dates:
            continue
        seen_dates.add(date_str)
        print(f"Read a page per day to finish by {date_str}")
    else:
        date_str = deadline.strftime('%m-%d')
        if date_str in seen_dates:
            continue
        seen_dates.add(date_str)
        print(f"Read {ppd:.1f} pages per day to finish by {date_str}")

conn.close()
print()
