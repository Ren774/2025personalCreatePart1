# -*- coding: utf-8 -*-
"""
0J01013 川上 冠
"""

import flet as ft  # 1. Flet ライブラリをインポート（UIを作成するためのライブラリ）

def main(page: ft.Page):  # 2. アプリのメイン関数。ページオブジェクトを引数に取る
    page.title = "TO-DO 887"

    text = ft.Text("予定を管理", color="blue", size=30)

    # Stack を使って、画面全体に対して相対的に配置する
    page.add(
        ft.Stack(
            [
                ft.Container(
                    content=text,
                    left=page.width * 0.01,   # 画面幅の70%
                    top=page.height * 0.05,   # 画面高さの80%
                )
            ],
            expand=True  # Stackが画面全体に広がる
        )
    )

    # サイズ変更に対応するためのイベント
    def on_resize(e):
        text_container.left = page.width * 0.9
        text_container.top = page.height * 0.8
        page.update()

    # 画面サイズ変更イベントを登録
    page.on_resize = on_resize


ft.app(target=main)  # 8. アプリケーションを起動し、main関数をエントリーポイントに指定

