#! /usr/bin/python
# -*- coding: utf-8 -*-

import readline
import sqlite3

con = sqlite3.connect("data.db",isolation_level=None)
sql = u"""
create table entry (
id INTEGER PRIMARY KEY,
body text,
category text,
date DATE)
"""

addr = ['test', 'Mr.Max']
body = ''
category = []

print 'App for my memo.'

print 'Enter memo body'
while True:
    line = raw_input('>>> ')
    if line == '':
        break
    body += line

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

print body
print category
#print 'body:' % body
#print 'category:' % category



