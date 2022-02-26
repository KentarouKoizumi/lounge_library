import cv2
import PySimpleGUI as sg

from PIL import Image
import sys
import time

import pyocr
import pyocr.builders

from isbn import search_book

# OCRの準備
tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
tool = tools[0]

# ウィンドウの色設定
sg.theme('Dark Blue 3')

# GUI上のなんかものを定義
frame3 = sg.Image(filename='', key='-IMAGE-')    # カメラの映像を出力するフレーム
frame4 = sg.InputText("", key="ISBN", font=("メイリオ", 15))    # 読み取ったISBNを出力（キーボード入力もできるようにInputTextを使っている。
frame5 = sg.Text("", key="DETAIL", font=("メイリオ", 15))   # ISBNから検索した本の詳細を表示
frame6 = sg.InputText("", key="STUDENT_NUMBER", font=("メイリオ", 15))  # 学籍番号
frame7 = sg.Button("Submit", key="SUBMIT", font=("メイリオ", 15))   # 決定ボタン（後々物理ボタンにする？）

# なんかレイアウトしてる
layout_2 = sg.Frame(layout=[[frame3]],
                          title='',
                          title_color='white',
                          font=('メイリオ', 15),
                          relief=sg.RELIEF_SUNKEN)
layout_3 = sg.Frame(layout=[[frame4]],
                    title="ISBN",
                    font=("メイリオ", 15))
layout_4 = sg.Frame(layout=[[frame5]],
                    title="書籍情報",
                    font=("メイリオ", 15))
layout_5 = sg.Frame(layout=[[frame6]],
                    title="学籍番号",
                    font=("メイリオ", 15))

# レイアウトまとめ
layout = [
            [layout_2],
            [layout_3],
            [layout_4],
            [layout_5],
            [frame7],
         ]

# 画面表示の設定
window = sg.Window('Lounge_Library', layout,
                                     location=(30, 30),
                                     alpha_channel=1.0,
                                     no_titlebar=False,
                                     grab_anywhere=False).Finalize()

### キャプチャ設定 ###
cap = cv2.VideoCapture(0)

cap.set(3, 1920)
cap.set(4, 1080)
cap.set(5, 30)

# OpneCVのQRコードのデコーダを定義（これを使ってQRコードを読み取る。）
qrd = cv2.QRCodeDetector()

# 初期化
fps = ""

while True:
    t1 = time.perf_counter() # fpsを計算するため
    event, values = window.read(timeout=20) # GUIを表示
    if event == sg.WIN_CLOSED: # 画面が閉じられたらwhileから出る
        break
    elif event == "SUBMIT": # Submitボタンが押されたら発動（今はvalues（InputTextにの中身）を出力している）
        print(values)

    _, img = cap.read() # カメラの画像をimgに取得
    img, _ = cv2.decolor(img) # 白黒にしてる
    img_1 = img[int(img.shape[0]/2) - 250 : int(img.shape[0]/2) + 250, int(img.shape[1]/2) - 250 : int(img.shape[1]/2) + 250] # GUIへの出力の関係で画像を小さくしている。
    cv2.putText(img_1, fps, (10,30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2, cv2.LINE_AA) # fpsを表示
    # 画面更新
    imgbytes = cv2.imencode('.png', img_1)[1].tobytes()
    window['-IMAGE-'].update(data=imgbytes)

    # OCRで文字を読み取る
    txt = tool.image_to_string(
        Image.fromarray(img),
        lang="eng",
        builder=pyocr.builders.TextBuilder(tesseract_layout=6)
    )
    lst = txt.split("\n")

    for i in lst: # 読み取った文字からISBNという文字を探す。
        if "ISBN" in i:
            i = i.split(" ")
            for k, j in enumerate(i):
                if "ISBN" in j:
                    isbn_index = k
                    break
            if i[k] == "ISBN": # "ISBN"と数字が離れていたときの処理
                isbn = i[isbn_index+1]
            else: # "ISBN"と数字がスペース無しでくっついていたときの処理
                isbn = i[isbn_index]
            isbn = isbn.replace("ISBN", "").replace("-", "") # 取得したISBNを整形（数字だけにする）
            window["ISBN"].update(isbn) # GUIの"ISBN"の欄を更新
            res = search_book(isbn) # 取得したISBNから本を検索
            if res: # 本が見つかった場合，GUIの書籍情報を更新
                window["DETAIL"].update("タイトル：" + res["title"] + "\n" + "著者：" + ",".join(res["authors"]))

    data, bbox, _ = qrd.detectAndDecode(img) # QRコードを読み取る
    if data: # QRコードが読み取れたらGUIの学籍番号の欄を更新する
        window["STUDENT_NUMBER"].update(data)

    elapsedTime = time.perf_counter() - t1
    fps = f"{1/elapsedTime}FPS"


window.close() # GUIを正式に閉じる。
