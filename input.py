#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess
import tempfile
import sys
import readline
import datetime, time
import sqlite3

connection = sqlite3.connect("/home/watanab2/diary/data.db",isolation_level=None,detect_types=sqlite3.PARSE_DECLTYPES)
connection.text_factory = str
cursor = connection.cursor()
sql = u"""
create table entry (
id INTEGER PRIMARY KEY,
[timestamp] timestamp,
body text
)
"""
#cursor.execute(sql)
sql = u"""
create table category (
id INTEGER,
category text
)
"""
#cursor.execute(sql)

addr = map(lambda lst: lst[0], cursor.execute(u"select distinct category from category").fetchall())
body = []
category = []

print 'App for my memo.'
print '==='

print 'Enter memo body'
print '---'
tmp_file = tempfile.mkstemp(suffix=".md")
subprocess.call(['vim', tmp_file[1]])

f = open(tmp_file[1])
body = f.read()
f.close()
os.remove(tmp_file[1])
#body = sys.stdin.read()

print body

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')

def completer(text, state):
    options = [x for x in addr if x.startswith(text)]
    try:
        return options[state]
    except IndexError:
        return None

readline.set_completer(completer)

print 'Enter category'
while True:
    line = raw_input('>>> ')
    if line == '':
        break
    category.append(line)
    print category

sql = u"insert into entry values (null, ?, ?)"
cursor.execute(sql, (datetime.datetime.now(), body))
lastid = cursor.lastrowid
sql = u"insert into category values (?, ?)"
for cat in category:
    cursor.execute(sql, (lastid, cat))

connection.commit()
connection.close()
