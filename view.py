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
        category = map(lambda lst: lst[0], self.connection.execute(
                    u"select category from category where id=%s" % entry[0])
                    .fetchall())
        return entry, category

    def curses_main(self,args):
        win = curses.initscr()
        curses.noecho()
        curses.cbreak()
        entry, category = self.get_entry(1)

        entry_date = entry[1].strftime('%Y/%m/%d')
        category = "category:" + ",".join(category)

        win.addstr(0,0,entry_date)
        win.addstr(1,0,category)
        win.addstr(3,0,entry[2])
        while 1:
            c = win.getkey()
            if c == "c":
                win.erase()
            elif c == "q":
                break
            win.refresh()
        curses.endwin()
        self.connection.close()

if __name__ == '__main__':
    a = mylog()
    curses.wrapper(a.curses_main)
