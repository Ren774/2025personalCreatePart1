# -*- coding: utf-8 -*-
"""
0J01013 川上 冠
Fletライブラリを使ったシンプルなUIアプリのサンプル
画面上にタイトルテキストと2つのボタン（追加・削除）を表示
"""

import flet as ft  # Fletライブラリをインポート（Flutter風のUIをPythonで作れる）
import sqlite3     # SQL

def main(page: ft.Page):  # アプリのエントリーポイント（ページオブジェクトを受け取る）
    page.title = "TO-DO 887"  # ウィンドウのタイトルを設定

    # データベースに接続
    conn = sqlite3.connect("TODO.db")
    cursor = conn.cursor()

    # ------------------------------
    # 表示するテキストの作成
    # ------------------------------
    text = ft.Text("予定を管理", color="blue", size=30)  # 青色でサイズ30のテキスト

    # ------------------------------
    # 2つのボタンを作成（ElevatedButton：押しやすい立体ボタン）
    # ------------------------------
    button_a = ft.ElevatedButton("追加")  # 「追加」ボタン
    button_b = ft.ElevatedButton("削除")  # 「削除」ボタン

    # ------------------------------
    # 各要素をContainerで包んで、Stack上で配置位置（left, top）を指定する
    # ※ Containerを使うことで自由な位置に置ける
    # ------------------------------
    text_container = ft.Container(
        content=text,
        left=page.width * 0.01,    # 横幅の1%の位置にテキストを表示
        top=page.height * 0.05,    # 高さの5%の位置にテキストを表示
    )

    button_a_container = ft.Container(
        content=button_a,
        left=page.width * 0.1,     # 横幅の10%に「追加」ボタン
        top=page.height * 0.3,     # 高さの30%に配置
    )

    button_b_container = ft.Container(
        content=button_b,
        left=page.width * 0.3,     # 横幅の30%に「削除」ボタン
        top=page.height * 0.3,     # 高さの30%（横に並べる）
    )

    # ------------------------------
    # Stackレイアウト：複数の要素を重ねて自由に配置できるレイアウト
    # expand=True にすると画面いっぱいに広がる
    # ------------------------------
    stack = ft.Stack(
        [
            text_container,       # テキスト表示コンテナ
            button_a_container,   # 追加ボタンのコンテナ
            button_b_container    # 削除ボタンのコンテナ
        ],
        expand=True  # Stackが画面全体に広がるようにする
    )

    # Stackをページに追加
    page.add(stack)

    # ------------------------------
    # ウィンドウサイズ変更時に要素の位置を自動で再計算するためのイベント
    # ------------------------------
    def on_resize(e):
        # 画面サイズ変更後の位置を再計算（再代入）
        text_container.left = page.width * 0.01
        text_container.top = page.height * 0.05

        button_a_container.left = page.width * 0.1
        button_a_container.top = page.height * 0.3

        button_b_container.left = page.width * 0.3
        button_b_container.top = page.height * 0.3

        page.update()  # 変更内容を画面に反映する

    # resizeイベントを登録（ウィンドウサイズ変更時にon_resizeを呼ぶ）
    page.on_resize = on_resize

# アプリケーションを起動し、main関数をエントリーポイントに指定
ft.app(target=main)