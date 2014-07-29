#! /usr/bin/python
# -*- coding: utf-8 -*-

import curses
import os
import subprocess
import tempfile
import sys
import readline
import datetime, time
import sqlite3
import locale
locale.setlocale(locale.LC_ALL, '')

class mylog(object):
    def __init__(self):
        self.dirpath = os.path.dirname(os.path.abspath(__file__))
        self.dbpath = self.dirpath + "/data.db"

        self.connection = sqlite3.connect(self.dbpath,isolation_level=None,detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.text_factory = str
        self.all_category = None

        self.win = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()

    def update_category(self):
        self.allupdate_category = map(lambda lst: lst[0], self.connection.execute(u"select distinct category from category").fetchall())

    def get_entry(self,id=1):
        entry = self.connection.execute(u"select * from entry where id=%s" % id).fetchone()
        if entry is not None:
            category = map(lambda lst: lst[0], self.connection.execute(
                        u"select category from category where id=%s" % entry[0])
                        .fetchall())
        else:
            category = None
        return entry, category

    def new_entry(self):
        self.win.clear()
        self.update_category()
        category = []
        y = 0

        self.win.addstr(y,0,'App for my memo.');y+=1
        self.win.addstr(y,0,'===');y+=1

        self.win.addstr(y,0,'Enter memo body');y+=1
        self.win.addstr(y,0,'---');y+=1
        tmp_file = tempfile.mkstemp(suffix=".mkd")
        subprocess.call(['vim', tmp_file[1]])

        f = open(tmp_file[1])
        body = f.read()
        f.close()
        os.remove(tmp_file[1])
#body = sys.stdin.read()
        cursor = self.connection.cursor()

        self.win.addstr(y,0, body);y+=1

        readline.parse_and_bind('tab: complete')
        readline.parse_and_bind('set editing-mode vi')

        def completer(text, state):
            options = [x for x in addr if x.startswith(text)]
            try:
                return options[state]
            except IndexError:
                return None

        readline.set_completer(completer)

        self.win.addstr(y,0, 'Enter category');y+=1
        while True:
            #line = raw_input('>>> ')
            curses.echo()
            line = self.win.getstr(y,0);y+=1
            curses.noecho()
            if line == '':
                break
            category.append(line)
            self.win.addstr(y,0, ",".join(category));y+=1

        sql = u"insert into entry values (null, ?, ?)"
        cursor.execute(sql, (datetime.datetime.now(), body))
        lastid = cursor.lastrowid
        sql = u"insert into category values (?, ?)"
        for cat in category:
            cursor.execute(sql, (lastid, cat))

        self.connection.commit()
        #self.connection.close()

    def curses_main(self,screen):
        cursor = self.connection.cursor()
        lastid = self.connection.execute(u"select max(id) from entry").fetchone()[0]
        id = self.display_entry(lastid)
        while 1:
            c = self.win.getkey()
#append new entry
            if c == "a":
                self.new_entry()
                id = id
            elif c == "n":
                id = self.display_entry(id, -1)
            elif c == "p":
                id = self.display_entry(id, 1)
            elif c == "q":
                break
            self.win.refresh()
        curses.endwin()
        self.connection.close()

    def display_entry(self,id,offset=0):
        entry, category = self.get_entry(id+offset)

        if entry is not None:
            self.win.erase()
            entry_date = entry[1].strftime('%Y/%m/%d%A %H:%M:%S')
            category = "category:" + ",".join(category)

            self.win.addstr(0,0,entry_date)
            self.win.addstr(1,0,category)
            self.win.addstr(3,0,entry[2])
            return entry[0]
        else:
            return id

if __name__ == '__main__':
    a = mylog()
    curses.wrapper(a.curses_main)
