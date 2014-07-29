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

    def get_entry(self,id=1):
        entry = self.connection.execute(u"select * from entry where id=%s" % id).fetchone()
        if entry is not None:
            category = map(lambda lst: lst[0], self.connection.execute(
                        u"select category from category where id=%s" % entry[0])
                        .fetchall())
        else:
            category = None
        return entry, category

    def curses_main(self,args):
        win = curses.initscr()
        curses.noecho()
        curses.cbreak()
        lastid = self.connection.execute(u"select max(id) from entry").fetchone()[0]
        id = self.display_entry(win, lastid)
        while 1:
            c = win.getkey()
            if c == "n":
                id = self.display_entry(win, id, -1)
            elif c == "p":
                id = self.display_entry(win, id, 1)
            elif c == "q":
                break
            win.refresh()
        curses.endwin()
        self.connection.close()
    def display_entry(self,win,id,offset=0):
        entry, category = self.get_entry(id+offset)

        if entry is not None:
            win.erase()
            entry_date = entry[1].strftime('%Y/%m/%d%A %H:%M:%S')
            category = "category:" + ",".join(category)

            win.addstr(0,0,entry_date)
            win.addstr(1,0,category)
            win.addstr(3,0,entry[2])
            return entry[0]
        else:
            return id

if __name__ == '__main__':
    a = mylog()
    curses.wrapper(a.curses_main)
