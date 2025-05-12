# -*- coding: utf-8 -*-
import flet as ft  # Fletライブラリをインポート（FlutterライクなUIツール）
import sqlite3     # SQLiteデータベースを操作するライブラリ

def main(page: ft.Page):
    # ページタイトルを設定
    page.title = "TO-DO 887"

    # データベースに接続
    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()

    # 選択中の編集対象のTODO IDを保存するための変数を定義
    edit_target_id = None

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
    # button_b = ft.ElevatedButton("削除")

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

    '''button_b_container = ft.Container(
        content=button_b,
        left=page.width * 0.3,    # 横幅の30%の位置
        top=page.height * 0.3,    # 高さの30%の位置
    )'''

    # Stackレイアウトに、上で作った要素をまとめる
    stack = ft.Stack(
        [
            text_container,       # タイトル
            button_a_container,   # 追加ボタン
            # button_b_container    # 削除ボタン
        ],
        expand=True  # Stack全体を画面に広げる
    )

    # ==============================
    # TODOリストを表示するためのListViewを定義
    # ==============================
    todo_list_view = ft.ListView(
        expand=True,    # ListViewは全体を広げて表示
        spacing=10,     # 各項目の間隔
        padding=10,     # ListView内のパディング
        auto_scroll=False  # 自動スクロールを無効
    )

    # ==============================
    # DBからTODOアイテムを読み込む関数を定義
    # ==============================
    def load_todo_items():
        # ListViewの中身を一度すべて削除（リセット）
        # → 重複表示を防ぐため、毎回クリアしてから再構築
        todo_list_view.controls.clear()

        # SQLiteデータベースからTODO全件を取得
        # 各カラムは (id, title, detail, category, is_done)
        cursor.execute("SELECT id, title, detail, category, is_done FROM todo")
        rows = cursor.fetchall()  # 結果をすべて取得

        # 各TODOデータを1つずつ処理
        for row in rows:
            # データベースの1レコードを変数に展開
            todo_id, title, detail, category, is_done = row

            # 状態のテキスト化（0 → 未完了、1 → 完了）
            status = "未完了" if is_done == 0 else "完了"

            # 画面に表示する文字列を組み立て（見た目重視）
            todo_text = f"■ {title}｜{detail}｜{category}｜{status}"

            # ★ここが重要：表示用のTextを「タップ可能」にする
            # FletのGestureDetectorでTextをラップすることで「クリック検出」が可能になる
            # on_tapは無名関数（lambda）で、対象のTODO情報を渡す
            todo_item = ft.GestureDetector(
                content=ft.Text(todo_text),  # 表示部分
                on_tap=lambda e, i=todo_id, t=title, d=detail, c=category:
                    open_edit_dialog(i, t, d, c)  # タップ時に編集ダイアログを開く
            )

            # 作成したタップ可能なTODO表示をListViewに追加
            todo_list_view.controls.append(todo_item)

        # ListViewを更新して画面に反映
        page.update()


    # ★★ 編集用テキストフィールドなどを再利用可能にする（入力欄）
    edit_title_input = ft.TextField(label="タイトル")
    edit_detail_input = ft.TextField(label="詳細")
    edit_category_radio = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="遊び", label="遊び"),
            ft.Radio(value="就活", label="就活"),
            ft.Radio(value="学校", label="学校")
        ])
    )

    # ★★ 完了状態を選択するラジオボタンを追加
    edit_is_done_radio = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="0", label="未完了"),
            ft.Radio(value="1", label="完了")
        ])
    )

    # ★★ 編集用ダイアログの定義
    edit_dialog = ft.AlertDialog(
    title=ft.Text("予定を編集"),  # ダイアログのタイトル

    # contentに、入力フォームとボタンを含めたカスタムUIを構築
    content=ft.Column([
        edit_title_input,        # タイトルのテキストフィールド
        edit_detail_input,       # 詳細のテキストフィールド
        edit_category_radio,     # カテゴリ選択用のラジオボタン
        edit_is_done_radio,      # 完了/未完了のラジオボタン

        # ボタンを並べるRow（横並びレイアウト）
        ft.Row(
            [
                # 左側に「削除」ボタンを配置
                ft.TextButton(
                    "削除",
                    on_click=lambda e: delete_todo()  # 削除処理を呼び出す
                ),

                # 真ん中にスペーサー（空のContainerなど）を入れて左右を離す
                ft.Container(expand=True),

                # 右側に「保存」ボタンを配置
                ft.TextButton(
                    "保存",
                    on_click=lambda e: save_edited_todo()  # 保存処理を呼び出す
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN  # 両端に配置
        )
    ]),

    # 通常のactionsは使わない（content内にボタンを組み込んでいるため）
)
    page.add(edit_dialog)  # ページに追加

    # ★★ 編集確定処理：DB更新→表示再描画
    def save_edited_todo():
        global edit_target_id

        # 入力値を取得
        new_title = edit_title_input.value
        new_detail = edit_detail_input.value
        new_category = edit_category_radio.value
        new_is_done = int(edit_is_done_radio.value)  # 完了/未完了状態を取得


        # データベースを更新
        cursor.execute(
            "UPDATE todo SET title=?, detail=?, category=?, is_done=? WHERE id=?",
            (new_title, new_detail, new_category, new_is_done, edit_target_id)
        )
        conn.commit()

        # ダイアログを閉じる＆リストを再読み込み
        edit_dialog.open = False
        page.update()
        load_todo_items()  # リスト更新

    # 削除処理：DB更新→表示再描画
    def delete_todo():
        global edit_target_id

        # 入力値を取得
        new_title = edit_title_input.value
        new_detail = edit_detail_input.value
        new_category = edit_category_radio.value
        new_is_done = int(edit_is_done_radio.value)  # 完了/未完了状態を取得


        # データベースを更新
        cursor.execute(
            "delete from todo WHERE id=?",
            (edit_target_id,)
        )
        conn.commit()

        # ダイアログを閉じる＆リストを再読み込み
        edit_dialog.open = False
        page.update()
        load_todo_items()  # リスト更新


    # ★★ 編集ダイアログを開く関数（指定されたTODO情報で入力欄を埋める）
    def open_edit_dialog(todo_id, title, detail, category):
        global edit_target_id
        edit_target_id = todo_id

        # 入力欄に現在の値をセット
        edit_title_input.value = title
        edit_detail_input.value = detail
        edit_category_radio.value = category
        # 完了状態（is_done）をラジオボタンで設定
        # 0 → 未完了、1 → 完了
        edit_is_done_radio.value = "0" if not edit_target_id else "1"


        # ダイアログを表示
        page.dialog = edit_dialog
        edit_dialog.open = True
        page.update()

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
        # button_b_container.left = page.width * 0.3
        # button_b_container.top = page.height * 0.3
        page.update()

    # リサイズイベントを登録
    page.on_resize = on_resize

# アプリを起動（デスクトップアプリ）
ft.app(target=main, view=ft.WEB_BROWSER)