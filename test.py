#!  /usr/bin/python
# -*- coding: utf-8 -*-

import curses

def curses_main(args):
    w    = curses.initscr()
    curses.echo()
    while 1:
        w.addstr(0, 0, ">")
        w.clrtoeol()
        s   = w.getstr()
        if s == "q":    break
        w.insertln()
        w.addstr(1, 0, "[" + s + "]")

def test1(args):
    win = curses.initscr()
    curses.noecho()
    curses.cbreak()

    keys = (
        ("h", "Left"), 
        ("l", "Right"), 
        ("k", "Up"), 
        ("j", "Down"),
        ("c", "Clear"),
        ("q", "Quit"),
    )
    for y, key in enumerate(keys):
        # カーソルを座標(x, y) に移動
        win.move(y, 0)

        # カーソル位置に文字を上書き
        # 改行文字は使えないので、1行ずつ表示する
        win.addstr("%s:%s" % key)

# メインウィンドウを更新
    win.refresh()

# メインウィンドウの高さと幅を取得
    y, x = win.getmaxyx()

# サブウィンドウを作成
    swin = win.subwin(y, x-11, 0, 10)

# サブウィンドウの枠線を描画
# 左、右、上、下、左上、右上、左下、右下
    swin.border("|", "|", "-", "-", "+", "+", "+", "+")

# カーソルが移動できる範囲は
# (0, 0)～(ウィンドウの高さ - 1, ウィンドウの幅 - 1)
# この範囲を超えた座標をmove()に渡すとエラー
    min_x = 0
    min_y = 0
    max_y, max_x = swin.getmaxyx()
    max_x -= 1
    max_y -= 1

# 枠線を上書きしないように調整
    min_x += 1
    min_y += 1
    max_x -= 1
    max_y -= 1

# カーソルをサブウィンドウの座標(x, y)に移動
# サブウィンドウの左上の角が(0, 0)
    x, y = min_x, min_y
    swin.move(y, x)

# カーソル位置のチェックと座標変更用の無名関数
    c_move = {
        "h":(lambda x, y: x > min_x, lambda x, y: (x - 1, y)),
        "l":(lambda x, y: x < max_x, lambda x, y: (x + 1, y)),
        "k":(lambda x, y: y > min_y, lambda x, y: (x, y - 1)),
        "j":(lambda x, y: y < max_y, lambda x, y: (x, y + 1)),
    }

    while 1:
        # 入力されたを文字で取得
        c = swin.getkey()
        
        # 入力されたキーを文字コードで取得
        # c = swin.getch()
        # c = chr(c)

        # 入力されたキーがh,l,k,j
        if c in c_move:
            # カーソル位置が端でなければ、座標を変更
            if c_move[c][0](x, y):
                x, y = c_move[c][1](x, y)

            # 入力された文字を表示した後にカーソルを移動
            # 文字を表示するとカーソルが右端に移動するので
            # 文字表示、カーソル移動の順にしている
            swin.addstr(c)
            swin.move(y, x)
        elif c == "c":
            # サブウィンドウをクリア
            swin.erase()
            # 枠線も消えるので再描画
            swin.border("|", "|", "-", "-", "+", "+", "+", "+")
            swin.move(min_x, min_y) 
        elif c == "q":
            break

        swin.refresh()

# スクリーンを閉じる
    curses.endwin()

curses.wrapper(test1)
