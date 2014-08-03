#! /usr/bin/python
# -*- coding: utf-8 -*-

import curses
import os
import subprocess
import tempfile
import sys
import datetime, time
import sqlite3
import locale
locale.setlocale(locale.LC_ALL, '')

class mylog:
    def __init__(self):
        self.dbpath = os.environ['HOME']+"/.mylog.db"

        self.connection = sqlite3.connect(self.dbpath,isolation_level=None,detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.text_factory = str

        self.win = curses.initscr()
        self.win.scrollok(True)
        self.win.idlok(True)

        self.max_y, self.max_x = self.win.getmaxyx()
        self.statusline = self.win.subwin(self.max_y-1,0)

        self.win.setscrreg(3,self.max_y-2)

        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()

        #gllobal variables
        self.all_category = None
        self.mode = None
        self.virtual_lines = []
        self.scroll_value = 0

    #retrive database
    def get_entry(self,id,offset):
        if offset == 0:
            entry = self.connection.execute(u"select * from entry where id=%s" % id).fetchone()
        elif offset == 1:
            entry = self.connection.execute(u"select * from entry where id>%s limit 1" % id).fetchone()
        elif offset == -1:
            entry = self.connection.execute(u"select * from entry where id<%s order by id desc limit 1" % id).fetchone()
        if entry is not None:
            category = map(lambda lst: lst[0], self.connection.execute(
                        u"select category from category where id=%s" % entry[0])
                        .fetchall())
        else:
            category = None
        return entry, category

    def update_category(self):
        self.allupdate_category = map(lambda lst: lst[0], self.connection.execute(u"select distinct category from category").fetchall())


    #curses wraper funcrions
    def gety(self,win):
        y,x = win.getyx()
        return min(y+1,self.max_y-2)

    def new_entry(self,id=None):
        self.win.clear()
        self.update_category()
        category = []

        if id:
            entry, org_category = self.get_entry(id,0)
            body = entry[2]

        self.win.addstr(self.gety(self.win)-1,0,'App for my memo.');
        self.win.addstr(self.gety(self.win),0,'===');

        self.win.addstr(self.gety(self.win),0,'Enter memo body');
        self.win.addstr(self.gety(self.win),0,'---');
        self.refresh()
        tmp_file = tempfile.mkstemp(suffix="_edit_entry.md")
        if id:
            f = open(tmp_file[1],'w')
            f.write(body)
            f.close()
        subprocess.call(['vim', tmp_file[1]])

        f = open(tmp_file[1])
        body = f.read().rstrip()
        f.close()
        os.remove(tmp_file[1])

        self.win.addstr(self.gety(self.win),0, body)
        self.refresh()

        def completer(text, state):
            options = [x for x in addr if x.startswith(text)]
            try:
                return options[state]
            except IndexError:
                return None

        self.win.addstr(self.gety(self.win),0, 'Enter category');
        if id:
            self.win.addstr(self.gety(self.win),0,'org category:'+','.join(org_category))
        self.refresh()
        while True:
            #line = raw_input('>>> ')
            curses.echo()
            self.win.addstr(self.gety(self.win),0,'> ')
            self.refresh()
            line = self.win.getstr(self.gety(self.win)-1,2);
            curses.noecho()
            if line == '':
                break
            category.append(line)
            self.win.addstr(self.gety(self.win)-1,0, ",".join(category));
            self.refresh()

        if id:
            cursor = self.connection.cursor()
            cursor.execute(u"""update entry set body=? where id=?""", (body, id))
            cursor.execute(u"delete from category where id=%d" % id)
            sql = u"insert into category values (?, ?)"
            for cat in category:
                cursor.execute(sql, (id, cat))
            self.connection.commit()
            self.display_entry(id)
        else:
            cursor = self.connection.cursor()
            sql = u"insert into entry values (null, ?, ?)"
            cursor.execute(sql, (datetime.datetime.now(), body))
            lastid = cursor.lastrowid
            sql = u"insert into category values (?, ?)"
            for cat in category:
                cursor.execute(sql, (lastid, cat))
            self.connection.commit()
            self.display_entry(lastid)

    def curses_main(self,screen=None):
        cursor = self.connection.cursor()
        lastid = self.connection.execute(u"select max(id) from entry").fetchone()[0]
        id = self.display_entry(lastid)
        while 1:
            if self.mode == "delete":
                c = self.dialog.getkey()
                if c == "y":
                    #delete this entry
                    self.display_statusline("delete this entry.")
                    self.connection.execute(u"delete from entry where id=%d" % id)
                    self.connection.execute(u"delete from category where id=%d" % id)
                    self.mode = None
                    del self.dialog
                    self.win.touchwin()
                elif c == "n":
                    self.display_statusline("cancel delete.")
                    self.mode = None
                    del self.dialog
                    self.win.touchwin()
                self.refresh()
            else:
                c = self.win.getkey()
                if c == "a":
                    #append new entry
                    self.new_entry()
                elif c == "n":
                    id = self.display_entry(id, -1)
                elif c == "p":
                    id = self.display_entry(id, 1)
                elif c == "d":
                    #delete this entry
                    self.display_dialog()
                elif c == "e":
                    #edit this entry
                    self.new_entry(id)
                elif c == "j":
                    #self.win.scroll(1)
                    self.scroll_value -= 1
                    id = self.display_entry(id)
                elif c == "k":
                    #self.win.scroll(-1)
                    self.scroll_value += 1
                    id = self.display_entry(id)
                elif c == "q":
                    break
            self.refresh()
        self.win.clear()
        self.refresh()
        curses.endwin()
        self.connection.close()

    def display_entry(self,id,offset=0):
        entry, category = self.get_entry(id,offset)

        if entry is not None:
            self.win.erase()
            entry_date = entry[1].strftime('%Y/%m/%d(%A) %H:%M:%S')
            category = "category:" + ",".join(category)

            self.win.addstr(0,0,entry_date)
            self.win.addstr(1,0,category)
            self.win.hline(2,0,curses.ACS_HLINE, self.max_x)
            self.win.move(2,0)
            for line in entry[2].split('\n'):
                self.win.addstr(self.gety(self.win),0,line);

            self.display_statusline()
            self.win.scroll(self.scroll_value)
            return entry[0]
        else:
            return id

    def display_dialog(self):
        self.mode = "delete"
        self.dialog = curses.newwin(4,20,int(self.max_y/2)-2,int(self.max_x/2)-10)
        self.dialog.bkgd(curses.A_REVERSE)
        self.dialog.addstr(1,1,"delete this entry?")
        self.dialog.addstr(2,5,"> yes / no")
        self.refresh()
    def display_statusline(self,out_string = "n/p:next/pre a:add e:edit d:delete q:exit"):
        self.statusline.clear()
        #out_string,x = self.win.getparyx()
        self.statusline.addstr(0,0,"[mylog] %s" % out_string)
        self.refresh()
        #self.statusline.refresh(self.max_y-1,0,0,0,1,self.max_x)
    def refresh(self):
        self.win.refresh()
        #self.win.refresh(0,0,0,0,1000,self.max_x)
        #self.win.refresh(0,0,0,0,self.max_y-1,self.max_x)

if __name__ == '__main__':
    a = mylog()
    curses.wrapper(a.curses_main)
