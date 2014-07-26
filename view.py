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

all_entry = connection.execute(u"select * from entry")

for row in all_entry:
    category = map(lambda lst: lst[0], 
            connection.execute(
                u"select category from category where id=%s" % row[0])
            .fetchall())
    #print row
    #print "id",row[0]
    print "category",category
    print "date",row[1]
    print "entry",row[2]
connection.close()
