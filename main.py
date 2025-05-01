# -*- coding: utf-8 -*-
import flet as ft  # Fletライブラリをインポート（FlutterライクなUIツール）
import sqlite3     # SQLiteデータベースを操作するライブラリ

def main(page: ft.Page):
    # ページタイトルを設定
    page.title = "TO-DO 887"

    # データベースに接続
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    # テーブルがなければ作成（新しいカラム構成）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            detail TEXT,
            category TEXT,
            is_done INTEGER DEFAULT 0,
            date TEXT
        )
    ''')
    conn.commit()

    # 画面に表示するテキスト（タイトル）
    text = ft.Text("予定を管理", color="blue", size=30)

    # 「追加」ボタンと「削除」ボタンを作成
    button_a = ft.ElevatedButton("追加")  # 後で押した時の処理を設定する
    button_b = ft.ElevatedButton("削除")

    # 各要素をContainerでラップして、配置位置を設定
    text_container = ft.Container(
        content=text,
        left=page.width * 0.01,   # 横幅の1%の位置
        top=page.height * 0.05,   # 高さの5%の位置
    )

    button_a_container = ft.Container(
        content=button_a,
        left=page.width * 0.1,    # 横幅の10%の位置
        top=page.height * 0.3,    # 高さの30%の位置
    )

    button_b_container = ft.Container(
        content=button_b,
        left=page.width * 0.3,    # 横幅の30%の位置
        top=page.height * 0.3,    # 高さの30%の位置
    )

    # Stackレイアウトに、上で作った要素をまとめる
    stack = ft.Stack(
        [
            text_container,       # タイトル
            button_a_container,   # 追加ボタン
            button_b_container    # 削除ボタン
        ],
        expand=True  # Stack全体を画面に広げる
    )

    # ==============================
    # 【★追加】TODOリストを表示するためのListViewを定義
    # ==============================
    todo_list_view = ft.ListView(
        expand=True,    # ListViewは全体を広げて表示
        spacing=10,     # 各項目の間隔
        padding=10,     # ListView内のパディング
        auto_scroll=False  # 自動スクロールを無効
    )

    # ==============================
    # 【★追加】DBからTODOアイテムを読み込む関数を定義
    # ==============================
    def load_todo_items():
        # リスト表示をクリアしてから再描画
        todo_list_view.controls.clear()  
        cursor.execute("SELECT title, detail, category FROM todo")  # データベースからすべてのTODOを選択
        rows = cursor.fetchall()  # 結果を取得
        for row in rows:
            title, detail, category = row
            # 各TODOアイテムをTextウィジェットとしてListViewに追加
            todo_list_view.controls.append(
                ft.Text(f"■ {title}｜{detail}｜{category}")
            )
        page.update()  # 画面更新

    # ----------- ダイアログの設定 -----------

    # ダイアログを開く関数
    def open_dialog(e):
        page.dialog = dialog    # 表示するダイアログを指定
        dialog.open = True      # ダイアログを開く
        page.update()           # ページ更新（変更を反映）

    # ダイアログを閉じる関数
    def close_dialog(e):
        title = title_input.value
        syousai = detail_input.value
        r = category_radio.value

        # 入力内容を確認（デバッグ用）
        print(f"タイトル: {title}")
        print(f"詳細: {syousai}")
        print(f"カテゴリ: {r}")

        # --- データベースに保存 ---
        cursor.execute(
            "INSERT INTO todo (title, detail, category) VALUES (?, ?, ?)",
            (title, syousai, r)
        )
        conn.commit()  # 変更を保存
        print("データベースに保存しました！")

        dialog.open = False  # ダイアログを閉じる
        title_input.value = ""  # 入力フォームを空にする
        detail_input.value = ""  # 入力フォームを空にする
        category_radio.value = None  # ラジオボタンを未選択にする
        page.update()  # ページ更新

        load_todo_items()   # 保存後にTODO一覧を更新

    # --- 入力フィールドの定義 ---
    title_input = ft.TextField(label="タイトルを入力")    # タイトル入力欄
    detail_input = ft.TextField(label="詳細を入力")        # 詳細入力欄

    # --- ラジオボタンの定義 ---
    category_radio = ft.RadioGroup(
        content=ft.Column([ 
            ft.Radio(value="遊び", label="遊び"),
            ft.Radio(value="就活", label="就活"),
            ft.Radio(value="学校", label="学校")
        ])
    )

    # 「追加」ボタンを押したときに表示するダイアログを作成
    dialog = ft.AlertDialog(
        title=ft.Text("予定を追加"),  # ダイアログタイトル
        content=ft.Column([
            title_input,              # タイトル入力欄
            detail_input,             # 詳細入力欄
            category_radio            # カテゴリ選択ラジオボタン
        ]),
        actions=[
            ft.TextButton("OK", on_click=close_dialog)  # OKボタン
        ]
    )

    # ダイアログを表示可能にする
    page.add(dialog)

    # 「追加」ボタンが押された時に、open_dialog() を呼ぶように設定
    button_a.on_click = open_dialog

    # ==============================
    # TODOリストの表示をページに追加
    # ==============================
    layout = ft.Column(
        controls=[
            stack,            # Stackレイアウト
            todo_list_view    # TODOリスト表示
        ],
        expand=True
    )
    
    # pageにlayoutを追加
    page.add(layout)

    # 初回TODOアイテムのロード
    load_todo_items()

    # ウィンドウサイズが変わった際のレイアウト調整
    def on_resize(e):
        text_container.left = page.width * 0.01
        text_container.top = page.height * 0.05
        button_a_container.left = page.width * 0.1
        button_a_container.top = page.height * 0.3
        button_b_container.left = page.width * 0.3
        button_b_container.top = page.height * 0.3
        page.update()

    # リサイズイベントを登録
    page.on_resize = on_resize

# アプリを起動（デスクトップアプリ）
ft.app(target=main, view=ft.WEB_BROWSER)
